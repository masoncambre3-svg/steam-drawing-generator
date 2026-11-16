"""PTF4, PPEC and APT automatic pump traps (TI-P207-10-US, TI-P208-02-US, TI-P612-02, TI-P612-28).

Every drawing is a front elevation with the liquid inlet on the left, origin at the inlet connection on the pipe
centreline, x with the flow, y down. Extra ports (motive, exhaust) have no direction.
"""
import numpy as np
import ti_trace as T
from manifolds import simplify
import sources as S
from traps2 import _cut_x

DATA = {
    "PTF4": {
        "name": "PTF4 (high capacity)", "type": "Pivotrol pressure powered pump, high capacity, with check valves",
        "ti": "TI-P207-10-US", "variants": ["ASME 150 flanged"],
        "sizes": {'4" x 4"': dict(A=1002, B=851, C=813, D=368, E=406, F=503, G=508, H=267, I=15, J=699, K=800,
                                 L=1427, M=102, N=224, P=330)},
        "note": "Front elevation from TI-P207-10-US p5, with the wafer check valves and companion flanges fitted. "
                "The ports are the outer ends of the companion flange hubs. Length L (1427) is set across the hubs "
                "and the height from N (inlet / outlet centreline 224 above the base). Overall height then comes "
                "out about 1015 against A 1002 (the TI gives A as reference only). Ports: in, out, then motive "
                "(left cover, right cover) and exhaust (left cover, right cover); motive points are the TI's leader "
                "dots, exhaust points are where the P (330) extension lines meet the covers. The drawing also has "
                "the vent assist outlets and gauges, which have no port."},
    "APT14": {
        "name": "APT14", "type": "Automatic pump trap, SG iron, DN40 x DN25", "ti": "TI-P612-02",
        "variants": ["screwed", "PN16", "ASME 150", "JIS / KS 10"],
        "sizes": {'1-1/2" x 1"': dict(A_scr=350, A_PN16=389, A_JIS=385, A_ASME=386.5, B=198, C=246, D=385, E=304,
                                      F=258, G=57, H=250, J=198)},
        "flange": ('1-1/2"', '1"'),
        "note": "Front view from TI-P612-02 p9 (right-hand view: inlet flange left, outlet flange right, motive and "
                "exhaust facing you). Face to face A for the connection picked, inlet / outlet centreline B (= J) above "
                "the base, motive and exhaust centreline C and overall height E are from the TI table. Height is set in "
                "bands (base to centreline, centreline to motive, motive to top); bolts, nuts and the motive / exhaust "
                "bosses keep their shape. Flange thickness is kept as drawn; flange diameter is EN 1092-1 PN16, ASME "
                "B16.5 Class 150 or JIS B 2220 10K (KS the same), since the TI does not list it. Screwed: the TI draws "
                "the flanged unit only, so the flanges are cut off at their backs and the body is scaled to A 350. "
                "Ports: in, out, motive (S), exhaust (E); motive and exhaust face you, so they are points with no "
                "direction. Withdrawal distance H and the side view (D, F) are not drawn."},
    "APT14HC": {
        "name": "APT14HC", "type": "Automatic pump trap, high capacity, SG iron, DN50 x DN40", "ti": "TI-P612-02",
        "variants": ["PN16", "ASME 150", "JIS / KS 10"],
        "sizes": {'2" x 1-1/2"': dict(A_PN16=512, A_JIS=506, A_ASME=524, B=198, C=270, D=400, E=335, F=261, G=57,
                                      H=275, I_PN16=31.5, I_JIS=31.5, I_ASME=45, J=198)},
        "flange": ('2"', '1-1/2"'),
        "note": "Drawn from the one outline on TI-P612-02 p9 (the TI has no separate HC drawing), set to the HC row: "
                "A for the flange picked, B (= J) 198, C 270, E 335. So the body is stretched against the APT14: about "
                "1.35 times along the pipe and more above the inlet centreline than below; bolts and bosses keep their "
                "shape. The inlet check valve end that sticks out I (31.5 / 45) past the inlet flange face is left "
                "off: it sits inside the mating flange, and the inlet port is the flange face as A is measured. Flange "
                "diameter from EN 1092-1 PN16, ASME B16.5 Class 150 or JIS B 2220 10K, since the TI does not list it."},
    "APT14SHC": {
        "name": "APT14SHC", "type": "Automatic pump trap, high capacity, carbon steel, DN50 x DN40", "ti": "TI-P612-02",
        "variants": ["PN16", "ASME 150", "JIS / KS 10"],
        "sizes": {'2" x 1-1/2"': dict(A_PN16=552, A_JIS=546, A_ASME=544, B=206, C=278, D=407, E=351, F=261, G=57,
                                      H=275, I_PN16=31.5, I_JIS=31.5, I_ASME=45, J=206)},
        "flange": ('2"', '1-1/2"'),
        "note": "Same as APT14HC (one outline on TI-P612-02 p9, set to the SHC row: A for the flange picked, B (= J) "
                "206, C 278, E 351). The inlet check valve end (I) is left off. Flange diameter from EN 1092-1 PN16, "
                "ASME B16.5 Class 150 or JIS B 2220 10K, since the TI does not list it."},
    "APT10": {
        "name": "APT10 / APT10SS", "type": "Automatic pump trap, screwed, DN20 x DN20", "ti": "TI-P612-28",
        "variants": ["screwed"],
        "sizes": {'3/4" x 3/4"': dict(A=187, B=23, C=223, D=398, E=273, F=209, G=57, H=135, I=171)},
        "note": "Side view from TI-P612-28 p5 (left-hand view), mirrored so the inlet faces left. The APT10 has its "
                "inlet and outlet on the end face, one above the other, so there is no straight-through front view: "
                "both ports face left, inlet I (171) and outlet B (23) above the base. Length D (398, gauge plug to the "
                "motive strainer end) and height E (273) are from the TI table; F (209) and C (223) check within 1 mm. "
                "Ports: in, out, motive (end of the motive strainer, C above the base), exhaust. The exhaust is "
                "behind the motive strainer in this view: its point is put on the strainer housing face at height C "
                "(an estimate, the TI does not show it from the side). Width A, G and withdrawal H are not drawn."},
    "PPEC": {
        "name": "PPEC", "type": "Low-profile pressure powered pump, with check valves", "ti": "TI-P208-02-US",
        "variants": ["iron, bronze checks", "iron, SS checks", "steel", "316 SS"], "variantLabel": "Body",
        "sizes": {'1"': {}, '1-1/2"': {}},
        "note": "Front elevation from TI-P208-02-US p5 (iron) and p6 (steel and 316 SS). Both drawings are only "
                "pictures, so they were vectorised (tools/raster.py), not traced: lines follow the picture. Height B "
                "(base to top of the body), inlet / outlet centreline E above the base, body length A, check valve "
                "lengths M and N and overall P are from the TI table for the body and size picked. The pictures do "
                "not hold B and E at one scale, so the body is scaled in two bands (base to centreline, centreline "
                "to top). The check valves are scaled as a unit to M and N; their own proportions are the TI's. "
                "Iron: the TI draws the 1\" inlet swing check and the 1-1/2\" inlet lift check; the lift check is drawn "
                "below the pump on the TI and is moved up onto the inlet centreline here. The outlet check is the one "
                "drawn (same shape for both sizes) and the SS check valve rows use the same pictures. Iron P is "
                "longer than M + A + N: the difference is drawn as a nipple each side (the TI shows them dashed). "
                "Steel / 316 SS: wafer checks between the body flange and a companion flange; M and N run from the "
                "body flange face to the stud ends (M + A + N = P within 1 mm); the ports are the companion flange hub "
                "ends. Motive (1/2\" NPT) is the top of the boss on the cover; exhaust (3/4\" NPT) is put at the end "
                "of the fitting on the cover end, an estimate: the TI shows the exhaust only in the plan view."},
}

_IRON = dict(A=279, B=480, C=371, D=333, F=356, G=229, H=28, J=15, K=292, L=15)
_STEEL = dict(A=297, B=498, C=371, D=333, E=71, F=356, G=229, H=28, J=15, K=294, L=15)
PPEC_TAB = {   # TI-P208-02-US p5 and p6, mm
    ("iron, bronze checks", '1"'): dict(_IRON, E=53, M=91, N=86, P=516),
    ("iron, bronze checks", '1-1/2"'): dict(_IRON, E=53, M=109, N=109, P=587),
    ("iron, SS checks", '1"'): dict(_IRON, E=71, M=84, N=84, P=493),
    ("iron, SS checks", '1-1/2"'): dict(_IRON, E=71, M=122, N=122, P=605),
    ("steel", '1"'): dict(_STEEL, M=53, N=53, P=404),
    ("steel", '1-1/2"'): dict(_STEEL, M=69, N=69, P=434),
    ("316 SS", '1"'): dict(_STEEL, K=295, M=53, N=53, P=404),
    ("316 SS", '1-1/2"'): dict(_STEEL, K=295, M=69, N=69, P=434),
}
# Picture landmarks, image px (line centres). Iron: TI-P208-02-US p5 picture xref 18; steel: p6 xref 24.
# Both are 1-bit image masks (alpha only); the mask is read straight from the PDF, so no vector dimensions on it,
# but the picture itself carries its dimension and centre lines: they are painted out (white) or cleared as
# horizontal dashes (clear rows) before vectorising.
PPEC_PIC = {
    "iron": dict(page=5, xref=18, yc=498.5, top=104.5, base=552.5, cl=(497, 501),
                 body=((150, 86, 541, 556), [(150, 86, 168, 258), (480, 86, 487, 91), (519, 86, 528, 158),
                                             (517, 98, 541, 108), (150, 440, 185, 556), (455, 452, 541, 556),
                                             (183, 535, 191, 556), (448, 535, 456, 556)]),
                 inlet={'1"': ((80, 445, 174, 531), [(80, 455, 87, 482)], 0.0),
                        '1-1/2"': ((82, 556, 174, 630), [(82, 556, 92, 571), (164, 556, 174, 575), (82, 618, 87, 630)],
                                   100.0)},     # lift check: drawn 100 px lower on the TI, centre line rows 597-601
                 outlet=((468, 450, 561, 531), []),
                 x=dict(face_in=89, end_in=170, body0=187, body1=452, end_out=473, face_out=554),
                 x_in={'1"': (89, 170), '1-1/2"': (87.5, 168)},
                 motive=(481, 93.5), exhaust=(530, 187.5),
                 nipples=[((170, 483), (187, 483)), ((170, 517), (187, 517)), ((452, 483), (473, 483)),
                          ((452, 517), (473, 517))]),
    "steel": dict(page=6, xref=24, yc=488.5, top=94, base=543, cl=(487, 491),
                  body=((45, 70, 420, 545), [(45, 70, 52, 250), (367, 70, 373, 81), (408, 70, 414, 149),
                                             (402, 91, 420, 99), (45, 440, 65, 545), (342, 440, 420, 545),
                                             (334, 529, 342, 545)]),
                  inlet=((5, 444, 66, 530), [(5, 519, 15, 530)]), outlet=((341, 444, 400, 530), []),
                  x=dict(tip_in=12, hub_in=28.5, body0=66.5, body1=340, hub_out=377.5, tip_out=394.5),
                  motive=(369, 83.5), exhaust=(417, 180)),
}


FLANGE_OD = {   # mm: EN 1092-1 PN16, ASME B16.5 Class 150, JIS B 2220 10K (KS B 1511 10K the same)
    "PN16": {'1"': 115, '1-1/2"': 150, '2"': 165},
    "ASME 150": {'1"': 108.0, '1-1/2"': 127.0, '2"': 152.4},
    "JIS / KS 10": {'1"': 125, '1-1/2"': 140, '2"': 155},
}
AKEY = {"screwed": "A_scr", "PN16": "A_PN16", "ASME 150": "A_ASME", "JIS / KS 10": "A_JIS"}


def _bb(segs):
    P = np.vstack([T.flat(sg) for sg in segs])
    return P.min(0), P.max(0)


_pic_cache = {}


def _ppec_image(pic):
    """The picture as grey (0 ink, 255 paper). It is a 1-bit image mask: the alpha channel is the ink."""
    key = pic["xref"]
    if key not in _pic_cache:
        import pymupdf
        pix = pymupdf.Pixmap(pymupdf.open(S.PPEC_PDF), pic["xref"])
        _pic_cache[key] = 255 - np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width).copy()
    return _pic_cache[key]


def _ppec_lines(g0, crop, white, cl):
    """Vectorise one region of a PPEC picture: paint out the white boxes, clear the horizontal centre-line dashes
    (ink in rows cl[0]..cl[1] with paper just above and below), then raster.polylines. Image px."""
    import raster as R
    g = g0.copy()
    r0, r1 = cl
    col = (g[r0 - 2] > 128) & (g[r1 + 2] > 128)               # paper above and below: part of a horizontal dash
    for r in range(r0, r1 + 1):
        g[r, col] = 255
    gc, o = R.crop(g, crop, white)
    pl = R.polylines(gc, o, thresh=128, min_w=1.0, eps=0.7)
    ends = np.array([Q[i] for _, Q in pl for i in (0, -1)])
    out = []
    for w, Q in pl:
        if np.hypot(*np.diff(Q, axis=0).T).sum() >= 4:
            out.append((w, Q))
            continue
        # a short piece is kept when it joins two others (pixel steps on a long line), dropped when it is a spur
        n = [(np.hypot(*(ends - Q[i]).T) < 1.6).sum() - 1 for i in (0, -1)]
        if min(n) >= 1:
            out.append((w, Q))
    return out


def _rigid_map(chains, f, k, size, xr):
    """Map chains through f, except small parts: chains whose bboxes touch are grouped, and a group no bigger than
    size (pt) lying between xr[0] and xr[1] moves as one piece (centre through f, scaled by k), so nuts and bosses
    keep their shape where the body is stretched."""
    bbs = [_bb(segs) for _, segs in chains]
    n = len(bbs)
    par = list(range(n))

    def root(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i
    small = [i for i in range(n) if (bbs[i][1] - bbs[i][0]).max() <= size]
    for ii, i in enumerate(small):
        for j in small[ii + 1:]:
            (a0, a1), (b0, b1) = bbs[i], bbs[j]
            if (a0 <= b1 + 0.2).all() and (b0 <= a1 + 0.2).all():
                par[root(i)] = root(j)
    groups = {}
    for i in small:
        groups.setdefault(root(i), []).append(i)
    rigid = {}
    for g in groups.values():
        a = np.min([bbs[i][0] for i in g], axis=0)
        b = np.max([bbs[i][1] for i in g], axis=0)
        if (b - a).max() <= size and xr[0] < a[0] and b[0] < xr[1]:
            # a group touching a big chain is part of a longer line: leave it to f
            if not any((bbs[j][0] <= b + 0.2).all() and (a <= bbs[j][1] + 0.2).all() and j not in g and
                       (bbs[j][1] - bbs[j][0]).max() > size and _touches(chains[j][1], a, b) for j in range(n)):
                c = (a + b) / 2
                for i in g:
                    rigid[i] = c
    out = []
    for i, (lw, segs) in enumerate(chains):
        if i in rigid:
            cx, cy = rigid[i]
            X, Y = f((cx, cy))
            out.append((lw, [(sg[0],) + tuple((X + (p[0] - cx) * k, Y + (p[1] - cy) * k) for p in sg[1:]) for sg in segs]))
        else:
            out.append((lw, [(sg[0],) + tuple(f(p) for p in sg[1:]) for sg in segs]))
    return out


def _touches(segs, a, b):
    """True if an end point of a segment in segs lies within 0.2 pt of the box a-b."""
    for sg in segs:
        for p in (sg[1], sg[-1]):
            if a[0] - 0.2 <= p[0] <= b[0] + 0.2 and a[1] - 0.2 <= p[1] <= b[1] + 0.2:
                return True
    return False


def _mapped(chains, f):
    return [(lw, [(sg[0],) + tuple(f(p) for p in sg[1:]) for sg in segs]) for lw, segs in chains]


class Pump:
    def __init__(self, model, size, variant=None):
        d = DATA[model]
        self.model, self.size, self.variant = model, size, variant or d["variants"][0]
        self.d = dict(d["sizes"][size])
        getattr(self, "_" + model.replace("-", "_"))()

    # ------------------------------------------------------------------ shared finish
    def _finish(self, chains, ports, lw, eps=0.25, close=3):
        """chains in mm (lw ignored, lw given), ports dict in mm."""
        thick = [(lw, segs) for _, segs in chains]
        P = np.array([p for _, segs in thick for sg in segs for p in sg[1:]])
        mg = 12 + 0.02 * np.ptp(P, axis=0).max()
        clip = (P[:, 0].min() - mg, P[:, 1].min() - mg, P[:, 0].max() + mg, P[:, 1].max() + mg)
        r = T.assemble(thick, [], clip, px=min(10.0, 3600 / max(clip[2] - clip[0], clip[3] - clip[1])), close=close)
        self.fill = [[tuple(p) for p in poly] for poly in r["fill"]]
        strokes = [(w, [[sg[0]] + [tuple(p) for p in sg[1:]] for sg in segs]) for w, segs in r["outline"]]
        self.strokes = simplify(strokes, eps) if eps else strokes
        m = lw / 2
        self.x0, self.y0, self.x1, self.y1 = P[:, 0].min() - m, P[:, 1].min() - m, P[:, 0].max() + m, P[:, 1].max() + m
        self.w, self.h = self.x1 - self.x0, self.y1 - self.y0
        self.ports = {k: (round(float(v[0]), 2), round(float(v[1]), 2)) for k, v in ports.items()}
        self.arrow = None
        self.P = P

    # ------------------------------------------------------------------ PTF4
    def _PTF4(self):
        # TI-P207-10-US p5, lower right view. The whole outline is one 0.36 pt path that carries a centre-line dash
        # pattern but prints solid (ignore_dash). Leaders and dimension lines are 0.5 pt (max_lw drops them); the
        # grey 0.13 pt lines are centre lines and seams (outline_lw drops them).
        ch, _ = T.collect(S.PTF4_PDF, 5, (248, 312, 532, 514), outline_lw=0.3, max_lw=0.4, ignore_dash=True)
        flatpts = lambda segs: np.vstack([T.flat(sg) for sg in segs])
        ch = [c for c in ch if c[0] > 0.3 and np.ptp(flatpts(c[1])[:, 1]) + abs(flatpts(c[1])[:, 1].mean() - 468.2) > 0.2]   # drop the pipe centre line
        xin, xout, cin, base = 253.58, 522.62, 468.2, 510.07          # hub ends, in / out centreline, base
        sx = self.d["L"] / (xout - xin)
        sy = self.d["N"] / (base - cin)
        f = lambda p: ((p[0] - xin) * sx, (p[1] - cin) * sy)
        named = {"in": (xin, cin), "out": (xout, cin),
                 "motive": (361.0, 344.5), "motive 2": (414.0, 344.0),
                 "exhaust": (357.0, 347.5), "exhaust 2": (420.0, 347.5)}
        self._finish(_mapped(ch, f), {k: f(v) for k, v in named.items()}, 0.34 * sx, close=6)
        self.k = sx

    # ------------------------------------------------------------------ APT14 / APT14HC / APT14SHC
    def _APT14(self):
        d, v = self.d, self.variant
        # TI-P612-02 p9 right-hand view. Outline 0.71 pt; leaders are 0.5 pt (outline_lw drops them).
        ch, _ = T.collect(S.APT14_PDF, 9, (336, 95, 525, 233), outline_lw=0.6, max_lw=0.8)
        xfl, xbl, xbr, xfr = 353.3, 360.4, 515.96, 523.48      # inlet face, inlet flange back, outlet back, outlet face
        yc, ym, top, base = 143.6, 122.51, 96.7, 231.42         # in / out centreline, motive / exhaust, top, base
        nl, nr = 12.6, 16.1                                     # neck half heights at the flange backs (pt)
        Rl, Rr = (169.52 - 117.66) / 2, (177.06 - 110.12) / 2   # drawn flange half heights (pt)
        ch = _cut_x(ch, xfl - 0.05, 1e9)                        # inlet check valve end past the inlet face: left off
        k0 = d["B"] / (base - yc)                               # mm per pt, base to centreline
        s2 = (d["C"] - d["B"]) / (yc - ym)
        s3 = (d["E"] - d["C"]) / (ym - top)

        def fy(y):                                              # body height, mm from the centreline (down +)
            if y >= yc:
                return (y - yc) * k0
            if y >= ym:
                return (y - yc) * s2
            return (ym - yc) * s2 + (y - ym) * s3
        A = d[AKEY[v]]
        scr = v == "screwed"
        if scr:                                                 # cut just inside the flange backs
            xbl, xbr = xbl + 0.2, xbr - 0.2
        tl, tr = (0.0, 0.0) if scr else ((xbl - xfl) * k0, (xfr - xbr) * k0)   # flange thickness as drawn
        sxb = (A - tl - tr) / (xbr - xbl)
        if not scr:
            rl, rr = (FLANGE_OD[v][s] / 2 for s in DATA[self.model]["flange"])

        def flange_y(y, n, R, r):
            dy = y - yc
            if abs(dy) <= n:
                return fy(y)
            e = abs(fy(yc + np.sign(dy) * n))
            return np.sign(dy) * (e + (abs(dy) - n) * (r - e) / (R - n))

        def f(p):
            x, y = p
            if x < xbl + 0.15 and not scr:
                return ((x - xfl) * k0, flange_y(y, nl, Rl, rl))
            if x > xbr - 0.15 and not scr:
                return (tl + (xbr - xbl) * sxb + (x - xbr) * k0, flange_y(y, nr, Rr, rr))
            return (tl + (x - xbl) * sxb, fy(y))
        if scr:                                                 # flanges cut off at their backs, ends closed
            ch = _cut_x(ch, xbl, xbr)
            ch += [(0.71, T.polyline([(xbl, 130.99), (xbl, 156.16)])), (0.71, T.polyline([(xbr, 128.08), (xbr, 160.33)]))]
        out = []
        out = _rigid_map(ch, f, k0, 11, (xbl + 1, xbr - 1))   # nuts and bosses keep their shape
        xin = xbl if scr else xfl
        xo = xbr if scr else xfr
        named = {"in": f((xin, yc)), "out": f((xo, yc)), "motive": f((426.26, ym)), "exhaust": f((451.39, ym))}
        named["out"] = (named["out"][0], 0.0)
        self._finish(out, named, 0.6 * k0, eps=0.1)
        self.k = k0

    _APT14HC = _APT14SHC = _APT14

    # ------------------------------------------------------------------ PPEC (raster pictures)
    def _PPEC(self):
        v, size = self.variant, self.size
        d = self.d = dict(PPEC_TAB[(v, size)])
        pic = PPEC_PIC["iron" if v.startswith("iron") else "steel"]
        g0 = _ppec_image(pic)
        yc, top, base = pic["yc"], pic["top"], pic["base"]
        ky_lo = d["E"] / (base - yc)                              # body, centreline to base
        ky_hi = (d["B"] - d["E"]) / (yc - top)                    # body, top to centreline
        fyb = lambda y: (y - yc) * (ky_lo if y > yc else ky_hi)
        X = pic["x"]
        parts = []                                                # (crop, white, transform)
        if "face_in" in X:                                        # iron: check, nipple, body, nipple, check
            xi0, xi1 = pic["x_in"][size]
            kM = d["M"] / (xi1 - xi0)
            kN = d["N"] / (X["face_out"] - X["end_out"])
            sA = d["A"] / (X["body1"] - X["body0"])
            gl, gr = X["body0"] - X["end_in"], X["end_out"] - X["body1"]
            gap = d["P"] - d["M"] - d["A"] - d["N"]
            g1, g2 = gap * gl / (gl + gr), gap * gr / (gl + gr)
            xb0 = d["M"] + g1                                     # body0 in mm from the inlet face
            crop, white, dy = pic["inlet"][size]
            parts.append((crop, white, lambda p, dy=dy: ((p[0] - xi0) * kM, (p[1] - dy - yc) * kM)))
            parts.append((pic["body"][0], pic["body"][1], lambda p: (xb0 + (p[0] - X["body0"]) * sA, fyb(p[1]))))
            xo0 = xb0 + d["A"] + g2
            parts.append((pic["outlet"][0], pic["outlet"][1], lambda p: (xo0 + (p[0] - X["end_out"]) * kN, (p[1] - yc) * kN)))

            def fnip(p):                                          # nipples between the checks and the body
                x, y = p
                if x < X["body0"] + 1:
                    return (d["M"] + (x - X["end_in"]) * g1 / gl, (y - yc) * kM)
                return (xb0 + d["A"] + (x - X["body1"]) * g2 / gr, (y - yc) * kN)
            extra = [[fnip(a), fnip(b)] for a, b in pic["nipples"]]
            ports = {"in": (0.0, 0.0), "out": (d["P"], 0.0)}
        else:                                                     # steel: wafer check sets bolted to the body flanges
            kM = d["M"] / (X["body0"] - X["tip_in"])
            kN = d["N"] / (X["tip_out"] - X["body1"])
            sA = d["A"] / (X["body1"] - X["body0"])
            parts.append((pic["inlet"][0], pic["inlet"][1], lambda p: (d["M"] + (p[0] - X["body0"]) * kM, (p[1] - yc) * kM)))
            parts.append((pic["body"][0], pic["body"][1], lambda p: (d["M"] + (p[0] - X["body0"]) * sA, fyb(p[1]))))
            parts.append((pic["outlet"][0], pic["outlet"][1],
                          lambda p: (d["M"] + d["A"] + (p[0] - X["body1"]) * kN, (p[1] - yc) * kN)))
            extra = []
            ports = {"in": (d["M"] + (X["hub_in"] - X["body0"]) * kM, 0.0),
                     "out": (d["M"] + d["A"] + (X["hub_out"] - X["body1"]) * kN, 0.0)}
        body_f = parts[1][2]
        ports["motive"] = body_f(pic["motive"])
        ports["exhaust"] = body_f(pic["exhaust"])
        chains = []
        for crop, white, f in parts:
            cl = pic["cl"] if crop[1] < pic["cl"][0] < crop[3] else (597, 601)
            for w, Q in _ppec_lines(g0, crop, white, cl):
                pts = [f(p) for p in Q]
                chains.append((1, [("l", pts[i], pts[i + 1]) for i in range(len(pts) - 1)]))
        chains += [(1, [("l", a, b)]) for a, b in extra]
        ox = ports["in"][0]                                       # origin at the inlet port
        sh = lambda p: (p[0] - ox, p[1])
        chains = _mapped(chains, sh)
        ports = {k: sh(p) for k, p in ports.items()}
        self._finish(chains, ports, 1.2, eps=0, close=14)
        self.k = sA

    # ------------------------------------------------------------------ APT10
    def _APT10(self):
        d = self.d
        # TI-P612-28 p5 left-hand view. Every line is its own 0.75 pt path; dimension lines run outside the clip.
        ch, _ = T.collect(S.APT10_PDF, 5, (66, 100, 346, 306), outline_lw=0.5, max_lw=0.8)
        xl, xf, xs, xh, top, base = 68.82, 264.71, 343.39, 257.65, 108.65, 301.19   # plug, port faces, strainer end
        sx = d["D"] / (xs - xl)
        sy = d["E"] / (base - top)
        yin = base - d["I"] / sy
        f = lambda p: (-(p[0] - xf) * sx, (p[1] - yin) * sy)                      # mirrored: ports face left
        ym = 143.84
        named = {"in": (0.0, 0.0), "out": (0.0, d["I"] - d["B"]), "motive": f((xs, ym)), "exhaust": f((xh, ym))}
        self._finish(_mapped(ch, f), named, 0.75 * sy, eps=0.05)
        self.k = sy
