"""Steam trap symbols, batch 1, draft 2.

Geometry comes off the TI outline drawings (ti_trace.py). Each symbol is then
stretched onto the real dimensions from the TI table for the chosen size, so
length, height and face-to-face are true for every size. Output is in mm.
"""
import json, math, os, subprocess, sys
import numpy as np
import ti_trace as T

from sources import V1

# colours: blue traps, navy linework
FILL_TOP, FILL_BOT, LINE, ARROW = "#6aaef2", "#2f76cc", "#0b2447", "#eaf3ff"

# ---------------------------------------------------------------- TI tables (mm)
DATA = {
    "TD52": {
        "name": "TD52", "type": "Thermodynamic", "ti": "TI-P014-23-US",
        "sizes": {
            '3/8"': dict(A=50.8, B=26.2, C=55.9, D=43.2, E=25.4),
            '1/2"': dict(A=68.6, B=31.5, C=63.5, D=45.7, E=30.4),
            '3/4"': dict(A=71.1, B=39.6, C=73.7, D=53.3, E=38.1),
            '1"':   dict(A=83.8, B=46.0, C=86.4, D=63.5, E=45.7),
        }, "variants": ["NPT"]},
    "TD62M": {
        "name": "TD62M / TD62LM", "type": "Thermodynamic, high pressure", "ti": "TI-P068-08",
        "sizes": {
            '1/2"': dict(A=80, B=92, C=92, D=52),
            '3/4"': dict(A=80, B=92, C=92, D=52),
            '1"':   dict(A=85, B=100, C=92, D=47),
        }, "variants": ["screwed"]},
    "FT450": {
        "name": "FT450", "type": "Float and thermostatic", "ti": "TI-P026-02-US",
        "sizes": {
            '3/4"':   dict(A=155, A1=254, B=66, C=66),
            '1"':     dict(A=165, A1=264, B=114, C=84),
            '1-1/2"': dict(A=249, A1=356, B=130, C=79),
            '2"':     dict(A=300, A1=406, B=140, C=91),
        }, "variants": ["screwed", "flanged"]},
    "IBV-C": {
        "name": "IBV Series C", "type": "Inverted bucket, vertical", "ti": "TI-P067-10",
        "sizes": {
            '1/2"':   dict(A=260, B=488, C=420, D=25, E=165),
            '3/4"':   dict(A=260, B=488, C=420, D=25, E=165),
            '1"':     dict(A=345, B=616, C=530, D=40, E=210),
            '1-1/2"': dict(A=411, B=774, C=650, D=39, E=265),
            '2"':     dict(A=411, B=782, C=650, D=39, E=265),
            '3"':     dict(A=532, B=1026, C=850, D=36, E=305),
        }, "variants": ["screwed", "flanged"]},
    "BPC32Y": {
        "name": "BPC32Y", "type": "Balanced pressure thermostatic", "ti": "TI-P005-01",
        "sizes": {s: dict(A=95, A1=150, B=94, C=64, F=54) for s in ('1/2"', '3/4"', '1"')},
        "variants": ["screwed", "flanged"]},
    "SMC32Y": {
        "name": "SMC32Y", "type": "Bimetallic", "ti": "TI-P076-10",
        "sizes": {s: dict(A=95, A1=150, B=94, C=92, F=54) for s in ('1/2"', '3/4"', '1"')},
        "variants": ["screwed", "flanged"]},
}


# ---------------------------------------------------------------- geometry sources
FLANGE_OD_300 = {'3/4"': 117.0, '1"': 124.0, '1-1/2"': 156.0, '2"': 165.0}


def ft450_geom(d, flanged):
    """FT450 front view, built directly in mm for each size.

    The handbook only carries this drawing as a small picture, so it cannot be
    traced like the others. It is rebuilt here from that picture and the table.
    """
    A, A1, B, C = d["A"], d["A1"], d["B"], d["C"]
    e = (A1 - A) / 2
    cx = A / 2
    H = B + C
    r = 0.082 * H                                                # bolt lug radius
    plug = 0.07 * H                                              # air vent plug standing above the cover
    yt, yb = -(B - plug - r), C - r                              # top and bottom lug centres
    R, cy = (yb - yt) / 2, (yb + yt) / 2
    hw = min(0.866 * R, 0.5 * A - r - 0.02 * A)                  # regular hexagon unless the body is short
    V = [(cx, yt), (cx + hw, cy - R/2), (cx + hw, cy + R/2), (cx, yb), (cx - hw, cy + R/2), (cx - hw, cy - R/2)]
    hub = min(0.265 * A, 0.34 * H)
    shapes = [T.polyline(V, closed=True)] + [T.circle(x, y, r) for x, y in V]
    shapes.append(T.polyline([(0, -hub/2), (A, -hub/2), (A, hub/2), (0, hub/2)], closed=True))
    pw = 0.75 * r
    shapes.append(T.polyline([(cx-pw, -B), (cx+pw, -B), (cx+pw, yt), (cx-pw, yt)], closed=True))
    fh = FLANGE_OD_300.get(d.get("size"), hub * 2.6)               # ASME class 300 flange OD
    clip = (-e - 8, -max(B, fh/2) - 8, A + e + 8, max(C, fh/2) + 8)
    wo, wd = 0.0105 * H, 0.0064 * H
    thick = [(wo, sh) for sh in T.union_outline(shapes, clip, smooth=1.0, S=min(20, 3200 / (A1 + 16)))]
    thin = []
    for x, y in V:                                               # cover bolts
        thin.append((wd * 1.15, T.circle(x, y, r * 0.60)))
        thin.append((wd, T.polyline([(x + r*0.40*math.cos(math.radians(a)), y + r*0.40*math.sin(math.radians(a)))
                                     for a in range(0, 360, 60)], closed=True)))
    f = 0.78
    thin.append((wd, T.polyline([(cx + (x-cx)*f, cy + (y-cy)*f) for x, y in V], closed=True)))   # raised cover face
    rb = 0.26 * R
    for rr, w in ((rb, wd*1.15), (rb*0.63, wd), (rb*0.3, wd)):   # mechanism boss
        thin.append((w, T.circle(cx, 0, rr)))
    for sx in (-1, 1):                                           # cast ribs either side of the boss
        for dy in (-0.24, 0.24):
            thin.append((wd, T.polyline([(cx + sx*rb*0.97, dy*rb), (cx + sx*hw*0.74, dy*rb)])))
    thin.append((wd, T.polyline([(cx-pw, -B + plug*0.45), (cx+pw, -B + plug*0.45)])))   # plug hex
    for x in (0.03*A, 0.97*A):                                   # connection ends
        thin.append((wd, T.polyline([(x, -hub/2), (x, hub/2)])))
    if flanged:
        ft, neck = e * 0.42, hub * 0.72
        for sx, xo in ((-1, 0), (1, A)):
            xf = xo + sx * e
            thick.append((wo, T.polyline([(xf, -fh/2), (xf - sx*ft, -fh/2), (xf - sx*ft, fh/2), (xf, fh/2)], closed=True)))
            for sy in (-1, 1):
                thick.append((wo, T.polyline([(xo, sy*hub/2), (xo + sx*(e-ft)*0.25, sy*neck/2), (xf - sx*ft, sy*neck/2)])))
    return T.assemble(thick, thin, clip)


def get_geom(model, variant, cache={}):
    key = (model, variant)
    if key in cache:
        return cache[key]
    if model == "TD52":
        g = T.trace(V1, 157, (132, 88, 263.5, 209.6), outline_lw=0.45, min_thin_lw=0.3)
    elif model == "TD62M":
        g = T.trace(V1, 194, (345, 30, 580, 290), outline_lw=0.7)
    elif model == "BPC32Y":
        clip = (314, 62, 436, 160.5) if variant == "flanged" else (338.6, 62, 411.4, 160.5)
        g = T.trace(V1, 356, clip, outline_lw=0.6)
    elif model == "SMC32Y":
        clip = (166, 104, 266, 201) if variant == "flanged" else (186.8, 104, 246.8, 201)
        g = T.trace(V1, 460, clip, outline_lw=0.6)
    elif model == "IBV-C":
        clip, lugs, drop = {
            "socketweld": ((46, 364, 175, 510), [(46, 405, 92, 440), (130, 405, 175, 440)], []),
            "screwed": ((228, 313, 356.5, 571), [(228, 405, 273, 440), (312, 405, 356.5, 440)], []),
            "flanged": ((409, 330, 538, 552), [(409, 405, 455, 440), (493, 405, 538, 440)], [(515.5, 347, 516.5, 378)]),
        }[variant]
        g = T.trace(V1, 394, clip, outline_lw=0.52, max_lw=0.9, min_thin_lw=0.3, extra_outline=lugs, drop=drop)
    cache[key] = g
    return g


def maps(model, variant, d, g):
    """Breakpoints (drawing pt -> mm). x runs with flow from the inlet face, y is 0 on the pipe centreline."""
    bx0, by0, bx1, by1 = g["bbox"]
    if model == "TD52":
        return ([(bx0, 0), (bx1, d["A"])],
                [(by0, -(d["C"] - d["E"]/2)), (155.0, -d["E"]/2), (by1, d["E"]/2)])
    if model == "TD62M":
        return ([(bx0, 0), (bx1, d["B"])],
                [(by0, -d["A"]), (185.3, 0), (by1, d["D"])])
    if model in ("BPC32Y", "SMC32Y"):
        xa, xb, xf0, xf1, cl = (340.0, 410.4, 316.0, 434.4, 115.4) if model == "BPC32Y" else (188.0, 245.6, 168.6, 264.6, 165.0)
        e = (d["A1"] - d["A"]) / 2
        return ([(xf0, -e), (xa, 0), (xb, d["A"]), (xf1, d["A"] + e)],
                [(by0, -d["C"]), (cl, 0), (by1, d["F"])])
    if model == "IBV-C":
        # flow is bottom to top. Width is the cover flange E; height is A / B / C by connection type.
        fl = {"socketweld": (67.9, 153.5, 373.5, 507.7, "A"), "screwed": (249.7, 335.4, 315.8, 568.5, "B"),
              "flanged": (430.7, 517.8, 332.7, 549.2, "C")}[variant]
        return ([(fl[0], -d["E"]/2), (fl[1], d["E"]/2)], [(fl[2], 0), (fl[3], d[fl[4]])])
    if model == "FT450":
        e = (d["A1"] - d["A"]) / 2
        return ([(52, -e), (72, 0), (157, d["A"]), (177, d["A"] + e)],
                [(116.0, -d["B"]), (168.0, 0), (211.0, d["C"])])


def ports(model, variant, d):
    if model == "IBV-C":
        h = d[{"socketweld": "A", "screwed": "B", "flanged": "C"}[variant]]
        return {"in": (0, h), "out": (0, 0)}
    L = d["B"] if model == "TD62M" else d["A"]
    e = (d["A1"] - d["A"]) / 2 if variant == "flanged" else 0
    return {"in": (-e, 0), "out": (L + e, 0)}


# small flow arrow: (centre x as fraction of length, centre y in mm from centreline as fraction of a dim, direction)
ARROWS = {"TD52": lambda d: (d["A"]*0.5, d["E"]*0.12, d["A"]*0.15, "r"),
          "BPC32Y": lambda d: (d["A"]*0.13, d["A"]*0.02, d["A"]*0.13, "r"),
          "SMC32Y": lambda d: (d["A"]*0.13, d["A"]*0.02, d["A"]*0.13, "r"),
          "FT450": lambda d: (d["A"]*0.5, d["C"]*0.36, (d["B"]+d["C"])*0.085, "r")}


def pmap(v, pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    if v <= xs[0]:
        i = 0
    elif v >= xs[-1]:
        i = len(xs) - 2
    else:
        i = max(j for j in range(len(xs)-1) if xs[j] <= v)
    return ys[i] + (v - xs[i]) * (ys[i+1] - ys[i]) / (xs[i+1] - xs[i])


_uid = 0


class Symbol:
    def __init__(self, model, size, variant=None):
        self.model, self.size = model, size
        self.variant = variant or DATA[model]["variants"][0]
        self.d = DATA[model]["sizes"][size]
        if model == "FT450":
            g = ft450_geom(dict(self.d, size=size), self.variant == "flanged")
            fx = lambda p: (p[0], p[1])
            self.k = 1.0
        else:
            g = get_geom(model, self.variant)
            xm, ym = maps(model, self.variant, self.d, g)
            fx = lambda p: (pmap(p[0], xm), pmap(p[1], ym))
            sx = abs((xm[-1][1]-xm[0][1]) / (xm[-1][0]-xm[0][0])); sy = abs((ym[-1][1]-ym[0][1]) / (ym[-1][0]-ym[0][0]))
            self.k = math.sqrt(sx*sy)                               # mm per drawing point, for line weights
        self.fill = [[fx(p) for p in poly] for poly in g["fill"]]
        self.strokes = []
        for key in ("outline", "detail"):
            for lw, segs in g[key]:
                self.strokes.append((lw * self.k * (1.0 if key == "outline" else 0.8),
                                     [[s[0]] + [fx(p) for p in s[1:]] for s in segs]))
        P = np.array([p for poly in self.fill for p in poly])
        m = max(lw for lw, _ in self.strokes) / 2
        self.x0, self.y0 = P[:, 0].min() - m, P[:, 1].min() - m
        self.x1, self.y1 = P[:, 0].max() + m, P[:, 1].max() + m
        self.ports = ports(model, self.variant, self.d)
        self.w, self.h = self.x1 - self.x0, self.y1 - self.y0

    def body(self):
        global _uid
        _uid += 1
        gid = f"g{_uid}"
        o = [f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="{FILL_TOP}"/><stop offset="1" stop-color="{FILL_BOT}"/></linearGradient></defs>']
        dfill = " ".join("M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in poly) + " Z" for poly in self.fill)
        o.append(f'<path d="{dfill}" fill="url(#{gid})" stroke="none"/>')
        by = {}
        for lw, segs in self.strokes:
            by.setdefault(round(lw, 3), []).append(segs)
        for lw, groups in sorted(by.items()):
            ds = []
            for segs in groups:
                last = None
                for s in segs:
                    a = s[1]
                    if last is None or abs(a[0]-last[0]) > 1e-3 or abs(a[1]-last[1]) > 1e-3:
                        ds.append(f"M{a[0]:.2f},{a[1]:.2f}")
                    if s[0] == "l":
                        ds.append(f"L{s[2][0]:.2f},{s[2][1]:.2f}")
                    else:
                        ds.append("C" + " ".join(f"{p[0]:.2f},{p[1]:.2f}" for p in s[2:]))
                    last = s[-1]
            o.append(f'<path d="{" ".join(ds)}" fill="none" stroke="{LINE}" stroke-width="{lw:.3f}" '
                     f'stroke-linecap="round" stroke-linejoin="round"/>')
        if self.model in ARROWS or self.model == "IBV-C":
            if self.model == "IBV-C":
                cx, cy, L, dr = 0, self.h * 0.62 + self.y0, self.d["E"] * 0.13, "u"
            else:
                cx, cy, L, dr = ARROWS[self.model](self.d)
            h = L * 0.2
            p = [(-L/2, -h/2), (L*0.12, -h/2), (L*0.12, -h*1.25), (L/2, 0), (L*0.12, h*1.25), (L*0.12, h/2), (-L/2, h/2)]
            if dr == "u":
                p = [(y, -x) for x, y in p]
            o.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.3f" stroke-linejoin="round"/>' %
                     (" ".join(f"{cx+x:.2f},{cy+y:.2f}" for x, y in p), ARROW, LINE, 0.4 * self.k))
        return "".join(o)

    def svg(self, px_per_mm=None, pad=1.0, extra=""):
        vb = f"{self.x0-pad:.2f} {self.y0-pad:.2f} {self.w+2*pad:.2f} {self.h+2*pad:.2f}"
        size = ""
        if px_per_mm:
            size = f' width="{(self.w+2*pad)*px_per_mm:.0f}" height="{(self.h+2*pad)*px_per_mm:.0f}"'
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"{size}{extra}>{self.body()}</svg>'


def slug(model, size, variant):
    s = size.replace('"', "in").replace("/", "-")
    return f"{model}_{s}_{variant}"


PX_PER_MM = 6

if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out + "/svg", exist_ok=True); os.makedirs(out + "/png", exist_ok=True)
    n = 0
    index = []
    for model, d in DATA.items():
        for size in d["sizes"]:
            for v in d["variants"]:
                s = Symbol(model, size, v)
                name = slug(model, size, v)
                p = f"{out}/svg/{name}.svg"
                open(p, "w").write(s.svg(px_per_mm=PX_PER_MM))
                subprocess.run(["rsvg-convert", p, "-o", f"{out}/png/{name}.png"], check=True)
                index.append(dict(file=name, model=model, size=size, connection=v, width_mm=round(s.w, 1),
                                  height_mm=round(s.h, 1), inlet=s.ports["in"], outlet=s.ports["out"], dims_mm=s.d))
                n += 1
    json.dump(index, open(out + "/index.json", "w"), indent=1)
    print("symbols written:", n)
