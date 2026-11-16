"""Every size and variant of some products on one sheet at ONE shared scale, wrapped into rows (the preview image
Mason asks for; sheet.py gives each row its own scale instead).

    python3 tools/gridsheet.py pumps /tmp/pumps PTF4,PPEC,APT10       # writes /tmp/pumps.svg and .png
    python3 tools/gridsheet.py pumps /tmp/pumps PTF4 --scale=0.4       # px per mm (default 0.52)
"""
import json, html, subprocess, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = [a for a in sys.argv[1:] if not a.startswith("--")]
fam, name, ids = args[0], args[1], args[2].split(",")
k = float(next((a[8:] for a in sys.argv if a.startswith("--scale=")), 0.52))
R = os.path.join(ROOT, "products", fam) + "/"


def load(p):
    t = open(R + p + "/" + p + ".js").read()
    return json.loads(t[t.index("SDG.register(") + 13:t.rindex(");")])


items = []
for pid in ids:
    pk = load(pid); P = pk["product"]
    for sz in P["sizes"]:
        for v in P["variants"]:
            items.append((P["name"].split(" /")[0], sz, v, pk["symbols"][f"{pid}|{sz}|{v}"]))
W, pad = 2000, 26
x, y, rowh, out = pad, pad, 0, []
for nm, sz, v, s in items:
    bx, by, bw, bh = s["box"]; w, h = bw * k, bh * k
    cw = max(w, 150)
    if x + cw > W - pad:
        x = pad; y += rowh + pad; rowh = 0
    out.append(f'<g transform="translate({x - bx * k:.1f},{y - by * k:.1f}) scale({k})"><path d="{s["fill"]}" fill="#5aa0ea"/>')
    for lw, d in s["strokes"]:
        out.append(f'<path d="{d}" fill="none" stroke="#0b2447" stroke-width="{lw}" stroke-linejoin="round"/>')
    for p in s["ports"]:
        out.append(f'<circle cx="{p[0]}" cy="{p[1]}" r="{3 / k}" fill="#e33"/>')
    out.append("</g>")
    out.append(f'<text x="{x}" y="{y + h + 16}" font-size="14" font-weight="bold" font-family="sans-serif">{html.escape(nm)} {html.escape(sz)}</text>')
    out.append(f'<text x="{x}" y="{y + h + 32}" font-size="12" fill="#444" font-family="sans-serif">{html.escape(v)}</text>')
    x += cw + pad; rowh = max(rowh, h + 40)
H = y + rowh + pad + 24
out.append(f'<text x="{pad}" y="{H - 12}" font-size="12" fill="#555" font-family="sans-serif">All at one scale ({k} px per mm). Red dots are the connection points.</text>')
open(name + ".svg", "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}"><rect width="100%" height="100%" fill="white"/>' + "".join(out) + "</svg>")
subprocess.run(["rsvg-convert", name + ".svg", "-o", name + ".png"], check=True)
print(name, W, int(H))
