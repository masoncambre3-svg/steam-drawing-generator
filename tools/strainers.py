"""Y strainers, traced from the TI outline drawings (US Product Handbook Vol. 1, Section 9).

The TI sheets carry one outline sketch per strainer, not one per size, and the
sketch is not in proportion for the bigger sizes. So each symbol is built like this:
  1. scale the traced outline so the face-to-face length A is true
  2. slide the cap (and its bolts or plug) along the leg until the bottom sits at B,
     which lengthens the leg without skewing the cap
  3. for flanged strainers, set the flange diameter from ASME B16.5
"""
import math
import numpy as np
import ti_trace as T

from sources import V1

# ASME B16.5 flange outside diameters, mm
OD = {
    150: {'1/2"': 89, '3/4"': 98, '1"': 108, '1-1/4"': 117, '1-1/2"': 127, '2"': 152, '2-1/2"': 178, '3"': 191,
          '4"': 229, '5"': 254, '6"': 279, '8"': 343},
    300: {'1/2"': 95, '3/4"': 117, '1"': 124, '1-1/4"': 133, '1-1/2"': 156, '2"': 165, '2-1/2"': 191, '3"': 210,
          '4"': 254, '5"': 279, '6"': 318, '8"': 381},
    600: {'1/2"': 95, '3/4"': 117, '1"': 124, '1-1/4"': 133, '1-1/2"': 156, '2"': 165, '2-1/2"': 191, '3"': 210,
          '4"': 273, '5"': 330, '6"': 356, '8"': 419},
}
SZ = ['1/2"', '3/4"', '1"', '1-1/4"', '1-1/2"', '2"', '2-1/2"', '3"', '4"', '5"', '6"', '8"']

def rows(sizes, *cols):
    return {s: dict(zip(("A", "B"), v)) for s, v in zip(sizes, zip(*cols))}

_f34 = dict(zip(SZ, zip([120, 144, 154, 180, 200, 230, 290, 310, 351, 401, 473, 593],      # A, ASME 150
                        [127, 150, 160, 180, 208, 240, 289, 311, 351, 401, 478, 600],      # A, ASME 300
                        [70, 80, 95, 130, 146, 180, 200, 205, 255, 315, 345, 440])))       # B
_f36 = dict(zip(SZ, zip([124, 142, 156, 180, 200, 230, 290, 310, 351, 400, 475, 594],
                        [130, 149, 163, 180, 208, 241, 290, 310, 351, 400, 480, 600],
                        [70, 80, 95, 130, 146, 180, 200, 205, 255, 315, 345, 440])))
_hp_sizes = ['1/2"', '3/4"', '1"', '1-1/2"', '2"', '2-1/2"', '3"', '4"', '6"', '8"']
_hp = dict(zip(_hp_sizes, zip([165, 190, 216, 241, 292, 330, 356, 432, 559, 660],
                              [117, 117, 117, 195, 195, 222, 222, 280, 360, 455])))

DATA = {
    "FIG16HP": {
        "name": "Fig 16HP", "type": "Y strainer, stainless steel", "ti": "TI-P169-08", "variants": ["screwed"],
        "sizes": {'1/4"': dict(A=70, B=51, C=80, D=32), '3/8"': dict(A=70, B=51, C=80, D=32),
                  '1/2"': dict(A=73, B=52, C=81, D=32), '3/4"': dict(A=90, B=64, C=100, D=36),
                  '1"': dict(A=105, B=74, C=120, D=46), '1-1/4"': dict(A=140, B=102, C=164, D=60),
                  '1-1/2"': dict(A=152, B=115, C=184, D=70), '2"': dict(A=178, B=138, C=224, D=80)}},
    "FIG16L": {
        "name": "Fig 16L", "type": "Y strainer, stainless steel", "ti": "TI-P160-01", "variants": ["screwed"],
        "sizes": {'3/8"': dict(A=69, B=55, C=87, D=26), '1/2"': dict(A=76, B=55, C=87, D=32),
                  '3/4"': dict(A=88, B=65, C=110, D=38), '1"': dict(A=106, B=78, C=125, D=46),
                  '1-1/4"': dict(A=133, B=103, C=155, D=56), '1-1/2"': dict(A=146, B=115, C=190, D=62),
                  '2"': dict(A=172, B=140, C=230, D=76)}},
    "FIG34": {
        "name": "Fig 34", "type": "Y strainer, carbon steel, flanged", "ti": "TI-P064-02", "variants": ["ASME 150", "ASME 300"],
        "sizes": {s: dict(A150=v[0], A300=v[1], B=v[2]) for s, v in _f34.items()},
        "note": 'Sizes 1-1/4" and up use the bolted-cover outline from the Fig 36 sheet. The Fig 34 sheet only draws the 1/2" to 1" body, and the two strainers share the same dimensions.'},
    "FIG34HP": {
        "name": "Fig 34HP", "type": "Y strainer, carbon steel, high pressure", "ti": "TI-P168-01", "variants": ["ASME 600"],
        "sizes": {s: dict(A600=v[0], B=v[1]) for s, v in _hp.items()}},
    "FIG36": {
        "name": "Fig 36", "type": "Y strainer, stainless steel, flanged", "ti": "TI-P160-02", "variants": ["ASME 150", "ASME 300"],
        "sizes": {s: dict(A150=v[0], A300=v[1], B=v[2]) for s, v in _f36.items()}},
    "FIG36HP": {
        "name": "Fig 36HP", "type": "Y strainer, stainless steel, high pressure", "ti": "TI-P160-11", "variants": ["ASME 600"],
        "sizes": {s: dict(A600=v[0], B=v[1]) for s, v in _hp.items()}},
}

# where each outline lives, and the cap geometry in drawing points:
#   face = two ends of the cap's inner face; slack = how far before that face still counts as cap
SRC = {
    "16HP": dict(page=1572, clip=(247.5, 438, 420, 558), face=((401.1, 504.5), (365.5, 552.9)), slack=1.0, margin=8,
                 ybody=492.5, flanged=False),
    "16L": dict(page=1578, clip=(218.5, 82.5, 378, 214.5), face=((336.5, 144.5), (304.7, 187.8)), slack=1.0, margin=10,
                ybody=135.7, flanged=False),
    "34": dict(page=1593, clip=(197, 88, 397, 242), face=((328.1, 201.4), (292.5, 235.5)), slack=1.0, margin=7, flanged=True),
    "34HP": dict(page=1601, clip=(199, 86, 389, 266), face=((326.7, 189.3), (256.8, 229.6)), slack=6.0, margin=8, flanged=True),
    "36": dict(page=1606, clip=(219, 79, 373, 237.5), face=((337.5, 171.8), (274.1, 218.1)), slack=1.0, margin=8, flanged=True),
    "36HP": dict(page=1612, clip=(201, 263, 390, 443), face=((328.0, 366.2), (258.1, 406.6)), slack=6.0, margin=8, flanged=True),
}


def source_for(model, size):
    if model == "FIG34":
        return "34" if size in ('1/2"', '3/4"', '1"') else "36"
    return {"FIG16HP": "16HP", "FIG16L": "16L", "FIG34HP": "34HP", "FIG36": "36", "FIG36HP": "36HP"}[model]


_cache = {}

def chains(src):
    """Linework for one source drawing, with anything that is not part of the body removed
    (centre-line ticks, leader stubs, the withdrawal outline)."""
    if src not in _cache:
        import cv2
        sp = SRC[src]
        thick, _ = T.collect(V1, sp["page"], sp["clip"], outline_lw=0.3)
        x0, y0, x1, y1 = sp["clip"]; PX = 10
        g = T.assemble(thick, [], sp["clip"], px=PX)
        main = max(g["fill"], key=lambda p: cv2.contourArea(np.array(p, np.float32)))
        m = np.zeros((int((y1-y0)*PX) + 2, int((x1-x0)*PX) + 2), np.uint8)
        cv2.fillPoly(m, [np.round((np.array(main) - (x0, y0)) * PX).astype(np.int32)], 255)
        m = cv2.dilate(m, np.ones((15, 15), np.uint8))               # 0.7 pt of slack
        out = []
        for lw, segs in thick:
            S = np.vstack([T.flat(sg) if sg[0] == "c" else np.linspace(np.array(sg[1]), np.array(sg[2]), 12) for sg in segs])
            I = np.round((S - (x0, y0)) * PX).astype(int)
            I[:, 0] = np.clip(I[:, 0], 0, m.shape[1]-1); I[:, 1] = np.clip(I[:, 1], 0, m.shape[0]-1)
            if m[I[:, 1], I[:, 0]].mean() / 255 < 0.85:
                continue
            P = np.vstack([np.array(sg[1:], float) for sg in segs])
            out.append((segs, (P[:, 0].min(), P[:, 1].min(), P[:, 0].max(), P[:, 1].max())))
        _cache[src] = out
    return _cache[src]


class Strainer:
    def __init__(self, model, size, variant=None):
        d = DATA[model]
        self.model, self.size = model, size
        self.variant = variant or d["variants"][0]
        self.d = dict(d["sizes"][size])
        cls = int(self.variant.split()[-1]) if self.variant.startswith("ASME") else None
        A = self.d.get(f"A{cls}") if cls else self.d["A"]
        B = self.d["B"]
        src = source_for(model, size); sp = SRC[src]
        ch = chains(src)

        (fx1, fy1), (fx2, fy2) = sp["face"]
        cx, cy = (fx1 + fx2) / 2, (fy1 + fy2) / 2
        hw = math.hypot(fx2 - fx1, fy2 - fy1) / 2
        v = ((fx2 - fx1) / (2 * hw), (fy2 - fy1) / (2 * hw))          # along the cap face
        u = (-v[1], v[0]) if -v[1] > 0 else (v[1], -v[0])              # along the leg, pointing away from the body
        if u[1] < 0: u = (-u[0], -u[1])

        allx0 = min(b[0] for _, b in ch); allx1 = max(b[2] for _, b in ch)
        if sp["flanged"]:
            # flanges are the tall narrow pieces at each end
            fl = [b for _, b in ch if (b[2] - b[0]) < 0.14 * (allx1 - allx0) and (b[3] - b[1]) > 0.35 * (allx1 - allx0)
                  and (b[0] < allx0 + 1.5 or b[2] > allx1 - 1.5 or True)]
            xl_in = max(b[2] for b in fl if b[2] < (allx0 + allx1) / 2)
            xr_in = min(b[0] for b in fl if b[0] > (allx0 + allx1) / 2)
            ftop = min(b[1] for b in fl); fbot = max(b[3] for b in fl)
            cl = (ftop + fbot) / 2
            xleft, xright = allx0, allx1
        else:
            cl = (min(b[1] for _, b in ch) + sp["ybody"]) / 2
            xleft = allx0

        def is_cap(p):
            a = (p[0] - cx) * u[0] + (p[1] - cy) * u[1]
            c = (p[0] - cx) * v[0] + (p[1] - cy) * v[1]
            ok = a >= -sp["slack"] and abs(c) <= hw + sp["margin"]
            if sp["flanged"]:
                return ok and p[1] > cl and xl_in < p[0] < xr_in
            return ok and p[1] > sp["ybody"] + 3

        pts = [p for segs, _ in ch for sg in segs for p in sg[1:]]
        if not sp["flanged"]:
            xright = max(p[0] for p in pts if not is_cap(p))
        s = A / (xright - xleft)                                       # mm per drawing point
        cap_low = max(p[1] for p in pts if is_cap(p))
        delta = (B - (cap_low - cl) * s) / u[1]                        # slide along the leg, mm
        ysc = 1.0
        if delta < 0:
            # a shorter leg than the sketch: squeeze everything below the centreline instead,
            # so the cap can never run into the body or a flange
            ysc, delta = B / ((cap_low - cl) * s), 0.0
        fscale = 1.0
        if sp["flanged"]:
            fscale = (OD[cls][size] / 2) / ((fbot - ftop) / 2 * s)

        def fx(p, flange):
            x, y = (p[0] - xleft) * s, (p[1] - cl) * s
            if flange:
                return (x, y * fscale)
            if delta and is_cap(p):
                return (x + delta * u[0], y + delta * u[1])
            return (x, y * ysc if y > 0 else y)

        lw = max(0.6, 0.0085 * A)
        thick = []
        for segs, b in ch:
            flange = sp["flanged"] and (b[2] <= xl_in + 0.4 or b[0] >= xr_in - 0.4)
            thick.append((lw, [(sg[0],) + tuple(fx(p, flange) for p in sg[1:]) for sg in segs]))
        P = np.array([p for _, segs in thick for sg in segs for p in sg[1:]])
        mg = 6 + 0.03 * A
        clip = (P[:, 0].min() - mg, P[:, 1].min() - mg, P[:, 0].max() + mg, P[:, 1].max() + mg)
        px = min(10.0, 3600 / max(clip[2] - clip[0], clip[3] - clip[1]))
        g = T.assemble(thick, [], clip, px=px, close=max(3, int(round(0.012 * A * px))))
        self.fill = [[tuple(p) for p in poly] for poly in g["fill"]]
        self.strokes = [(w, [[sg[0]] + [tuple(p) for p in sg[1:]] for sg in segs]) for w, segs in g["outline"]]
        self.k = s
        m = lw / 2
        F = np.array([p for poly in self.fill for p in poly])
        self.x0, self.y0 = min(F[:, 0].min(), P[:, 0].min()) - m, min(F[:, 1].min(), P[:, 1].min()) - m
        self.x1, self.y1 = max(F[:, 0].max(), P[:, 0].max()) + m, max(F[:, 1].max(), P[:, 1].max()) + m
        self.w, self.h = self.x1 - self.x0, self.y1 - self.y0
        self.ports = {"in": (0, 0), "out": (A, 0)}
        # drain / blowdown connection: centre of the cap, at its outer end, pointing along the leg
        amax = max((p[0] - cx) * u[0] + (p[1] - cy) * u[1] for p in pts if is_cap(p))
        d0, d1 = fx((cx, cy), False), fx((cx + u[0] * amax, cy + u[1] * amax), False)
        self.ports["drain"] = d1
        self.drain_angle = math.degrees(math.atan2(d1[1] - d0[1], d1[0] - d0[0]))
        self.A = A
        self.arrow = (A * (0.2 if sp["flanged"] else 0.27), 0.0, A * (0.085 if sp["flanged"] else 0.12), "r", lw * 0.55)
        self.d = {("A" if k.startswith("A") else k): v for k, v in self.d.items() if not k.startswith("A") or k in ("A", f"A{cls}")}
