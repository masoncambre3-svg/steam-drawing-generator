"""Build product packs for the Steam Drawing Generator.

    python3 tools/make_packs.py                 # rebuild every pack that has a tracer here
    python3 tools/make_packs.py valves/A3S      # rebuild one product
    python3 tools/make_packs.py --index         # only rewrite products/index.js from catalog.json

Each product gets its own folder:  products/<family>/<ID>/<ID>.js  (+ preview.png)
The pack is plain data: SDG.register({product: {...}, symbols: {"ID|size|variant": {...}}}).
A symbol is in millimetres, origin at the inlet connection on the pipe centreline, x with the flow, y down:
    box     [x, y, width, height] of the drawing
    fill    SVG path of the silhouette
    strokes [[line width, SVG path], ...]
    arrow   [polygon points, line width] or null
    dims    the TI table row for that size
    ports   connection points [[x, y], ...]; a third value is a direction in degrees (strainer drain)
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
CATALOG = os.path.join(HERE, "catalog.json")


def parts(s, arrow_spec=None, dec=2):
    """Turn a traced symbol object (fill, strokes, ports, d, box) into pack data.
    dec: decimals written for coordinates (1 is plenty for very large drawings like the manifolds)."""
    fill = " ".join("M" + " L".join(f"{x:.{dec}f},{y:.{dec}f}" for x, y in poly) + "Z" for poly in s.fill)
    by = {}
    for lw, segs in s.strokes:
        by.setdefault(round(lw, 3), []).append(segs)
    strokes = []
    for lw, groups in sorted(by.items()):
        ds = []
        for segs in groups:
            last = None
            for sg in segs:
                a = sg[1]
                if last is None or abs(a[0]-last[0]) > 1e-3 or abs(a[1]-last[1]) > 1e-3:
                    ds.append(f"M{a[0]:.{dec}f},{a[1]:.{dec}f}")
                ds.append(f"L{sg[2][0]:.{dec}f},{sg[2][1]:.{dec}f}" if sg[0] == "l" else "C" + " ".join(f"{p[0]:.{dec}f},{p[1]:.{dec}f}" for p in sg[2:]))
                last = sg[-1]
        strokes.append([lw, "".join(ds)])
    arrow = None
    if arrow_spec:
        cx, cy, L, dr, aw = arrow_spec
        h = L * 0.2
        p = [(-L/2, -h/2), (L*0.12, -h/2), (L*0.12, -h*1.25), (L/2, 0), (L*0.12, h*1.25), (L*0.12, h/2), (-L/2, h/2)]
        if dr == "u":
            p = [(y, -x) for x, y in p]
        arrow = [" ".join(f"{cx+x:.2f},{cy+y:.2f}" for x, y in p), round(aw, 3)]
    ports = [[round(float(v), 2) for v in s.ports[k]] for k in ("in", "out") if k in s.ports]
    if "drain" in s.ports:
        ports.append([round(float(v), 2) for v in s.ports["drain"]] + [round(float(s.drain_angle), 1)])
    for k in s.ports:                                   # any other connections (motive, exhaust, ...)
        if k not in ("in", "out", "drain"):
            ports.append([round(float(v), 2) for v in s.ports[k]])
    return dict(box=[round(float(v), 2) for v in (s.x0, s.y0, s.w, s.h)], fill=fill, strokes=strokes, arrow=arrow,
                dims={k: v for k, v in s.d.items() if k != "size"}, ports=ports)


def preview(sym, path):
    x, y, w, h = sym["box"]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x-2} {y-2} {w+4} {h+4}" width="{int(480*min(1, w/h))}" height="{int(480*min(1, h/w))}">',
         '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6aaef2"/><stop offset="1" stop-color="#2f76cc"/></linearGradient></defs>',
         f'<path d="{sym["fill"]}" fill="url(#g)"/>']
    for lw, d in sym["strokes"]:
        o.append(f'<path d="{d}" fill="none" stroke="#0b2447" stroke-width="{lw}" stroke-linecap="round" stroke-linejoin="round"/>')
    if sym["arrow"]:
        o.append(f'<polygon points="{sym["arrow"][0]}" fill="#f3f8ff" stroke="#0b2447" stroke-width="{sym["arrow"][1]}"/>')
    o.append("</svg>")
    tmp = path + ".svg"
    open(tmp, "w").write("".join(o))
    subprocess.run(["rsvg-convert", tmp, "-o", path], check=True)
    os.remove(tmp)


def write_pack(family_slug, family_name, pid, product, symbols):
    folder = os.path.join(ROOT, "products", family_slug, pid)
    os.makedirs(folder, exist_ok=True)
    product = dict(product, id=pid, family=family_name)
    body = json.dumps({"product": product, "symbols": symbols}, separators=(",", ":"))
    open(os.path.join(folder, pid + ".js"), "w").write(f"// {product['name']} ({product['ti']}). Built by tools/make_packs.py.\nSDG.register({body});\n")
    sizes = product["sizes"]
    key = f"{pid}|{sizes[min(1, len(sizes)-1)]}|{product['variants'][0]}"
    preview(symbols[key], os.path.join(folder, "preview.png"))
    cat = json.load(open(CATALOG)) if os.path.exists(CATALOG) else {"families": []}
    fam = next((f for f in cat["families"] if f["slug"] == family_slug), None)
    if not fam:
        fam = {"slug": family_slug, "name": family_name, "products": []}
        cat["families"].append(fam)
    if pid not in fam["products"]:
        fam["products"].append(pid)
    json.dump(cat, open(CATALOG, "w"), indent=1)
    print(f"  {family_slug}/{pid}: {len(symbols)} drawings, {len(body)//1024} KB")


def write_index():
    cat = json.load(open(CATALOG))
    packs = []
    for f in cat["families"]:
        for pid in f["products"]:
            rel = f"{f['slug']}/{pid}/{pid}.js"
            if os.path.exists(os.path.join(ROOT, "products", rel)):
                packs.append(rel)
            else:
                print("  missing pack, left out of the index:", rel)
    idx = {"families": [f["name"] for f in cat["families"]], "packs": packs}
    open(os.path.join(ROOT, "products", "index.js"), "w").write(
        "// List of product packs, in display order. Built by tools/make_packs.py from tools/catalog.json.\nSDG.index(" + json.dumps(idx, indent=1) + ");\n")
    print(f"index: {len(packs)} packs in {len(cat['families'])} families")


# ---------------------------------------------------------------- tracers for each product line
def build_traps(only=None):
    import symbols as SY
    FT_NOTE = "The handbook has only a low-resolution picture of this trap, so its cover detail is redrawn by hand. Overall size follows the TI table."
    for model, d in SY.DATA.items():
        if only and only != model:
            continue
        syms = {}
        for size in d["sizes"]:
            for v in d["variants"]:
                s = SY.Symbol(model, size, v)
                spec = None
                if model == "IBV-C":
                    spec = (0, s.h * 0.62 + s.y0, s.d["E"] * 0.13, "u", 0.4 * s.k)
                elif model in SY.ARROWS:
                    spec = SY.ARROWS[model](s.d) + (0.4 * s.k,)
                syms[f"{model}|{size}|{v}"] = parts(s, spec)
        write_pack("steam-traps", "Steam traps", model,
                   dict(name=d["name"], type=d["type"], ti=d["ti"], sizes=list(d["sizes"]), variants=d["variants"],
                        source="Redrawn by hand from the TI picture" if model == "FT450" else "Traced from the TI outline drawing",
                        note=FT_NOTE if model == "FT450" else ""), syms)
    import universal as UN
    for model, d in UN.DATA.items():
        if only and only != model:
            continue
        syms = {f"{model}|{size}|{v}": parts(UN.Universal(model, size, v)) for size in d["sizes"] for v in d["variants"]}
        write_pack("steam-traps", "Steam traps", model,
                   dict(name=d["name"], type=d["type"], ti=d["ti"], sizes=list(d["sizes"]), variants=d["variants"],
                        sizeLabel=d.get("sizeLabel", "Size"), source="Traced from the TI outline drawing", note=d["note"]), syms)


def build_strainers(only=None):
    import strainers as ST
    N = "The TI sheet has one outline for every size. Length A and depth B are set from the TI table for the size you pick."
    FL = " Flange diameter is ASME B16.5 for the class shown, since the TI sheet does not list it."
    for model, d in ST.DATA.items():
        if only and only != model:
            continue
        syms = {}
        for size in d["sizes"]:
            for v in d["variants"]:
                s = ST.Strainer(model, size, v)
                syms[f"{model}|{size}|{v}"] = parts(s, s.arrow)
        fl = d["variants"][0].startswith("ASME")
        write_pack("strainers", "Strainers", model,
                   dict(name=d["name"], type=d["type"], ti=d["ti"], sizes=list(d["sizes"]), variants=d["variants"],
                        source="Traced from the TI outline drawing", note=N + (FL if fl else "") + (" " + d["note"] if d.get("note") else "")), syms)


def build_valves(only=None):
    import valves as VL
    for model, d in VL.DATA.items():
        if only and only != model:
            continue
        syms = {}
        for size in d["sizes"]:
            for v in d["variants"]:
                s = VL.Valve(model, size, v)
                syms[f"{model}|{size}|{v}"] = parts(s, s.arrow)
        write_pack("valves", "Valves", model,
                   dict(name=d["name"], type=d["type"], ti=d["ti"], sizes=list(d["sizes"]), variants=d["variants"],
                        source="Traced from the TI outline drawing", note=""), syms)


def build_pumps(only=None):
    import pumps as PU
    for model, d in PU.DATA.items():
        if only and only != model:
            continue
        syms = {}
        for size in d["sizes"]:
            for v in d["variants"]:
                s = PU.Pump(model, size, v)
                syms[f"{model}|{size}|{v}"] = parts(s, s.arrow)
        write_pack("pumps", "Pumps", model,
                   dict(name=d["name"], type=d["type"], ti=d["ti"], sizes=list(d["sizes"]), variants=d["variants"],
                        source="Traced from the TI outline drawing", note=d.get("note", "")), syms)


def build_separators(only=None):
    import separators as SE
    for model, d in SE.DATA.items():
        if only and only != model:
            continue
        syms = {}
        for size in d["sizes"]:
            for v in d["variants"]:
                s = SE.Separator(model, size, v)
                syms[f"{model}|{size}|{v}"] = parts(s, s.arrow)
        hand = model.startswith("S4A")
        write_pack("separators", "Separators", model,
                   dict(name=d["name"], type=d["type"], ti=d["ti"], sizes=list(d["sizes"]), variants=d["variants"],
                        source="Redrawn by hand from the TI picture and table" if hand else "Traced from the TI outline drawing",
                        note=d["note"]), syms)


def build_manifolds(only=None):
    import manifolds as MF
    for model, d in MF.DATA.items():
        if only and only != model:
            continue
        syms = {f"{model}|{n}|{v}": parts(MF.Manifold(model, n, v), dec=1) for n in d["sizes"] for v in d["variants"]}
        write_pack("manifolds", "Manifolds", model,
                   dict(name=d["name"], type=d["type"], ti=d["ti"], sizes=list(d["sizes"]), variants=d["variants"],
                        sizeLabel="Stations", variantLabel="Stand", source="Traced from the TI outline drawing",
                        note=d["note"]), syms)


BUILDERS = {"steam-traps": build_traps, "strainers": build_strainers, "valves": build_valves, "pumps": build_pumps,
            "separators": build_separators, "manifolds": build_manifolds}

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--index" not in sys.argv:
        if args:
            for a in args:
                fam, _, pid = a.partition("/")
                BUILDERS[fam](pid or None)
        else:
            for b in BUILDERS.values():
                b()
    write_index()
