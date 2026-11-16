"""Steam traps, batch 2 (2026-11-16): TDC46M, TD62M / TD62LM flanged, TD120M, HM34.

TDC46M   TI-P187-04 p8. Two drawings: screwed / socket weld (left) and flanged (right).
TD62M-FL TI-P068-20 p4. Flanged TD62M / TD62LM (ASTM body). The screwed / SW version is the older TD62M pack.
TD120M   TI-P150-11 p5. One drawing (flanged); butt weld and socket weld cut the flanges off at the end of the neck,
         where the TI's B / B1 extension lines sit.
HM34     TI-2-404-US p2. Section drawing, raster picture only: vectorised with raster.py.

Every drawing is one outline for all sizes. x and y are set separately (none of these TI drawings is to scale both
ways), and the parts with their own dimension are set on their own (cap diameter, flange OD).
Origin at the inlet connection on the pipe centreline, x with the flow, y down, mm.
"""
import numpy as np
import ti_trace as T
from universal import _chains, _bb, _pw
from sources import TDC46M_PDF, TD62FL_PDF, TD120M_PDF, HM34_PDF

IN = 25.4
# flange outside diameters, mm. ASME B16.5, EN 1092-1, JIS B 2220 (the TIs give face to face only)
OD = {
    "ASME 150": {'1/2"': 88.9, '3/4"': 98.6, '1"': 108.0},
    "ASME 300": {'1/2"': 95.3, '3/4"': 117.5, '1"': 124.0},
    "ASME 600": {'1/2"': 95.3, '3/4"': 117.5, '1"': 124.0},
    "ASME 900 / 1500": {'1/2"': 120.7, '3/4"': 130.2, '1"': 149.4},
    "PN40": {'1/2"': 95, '3/4"': 105, '1"': 115},
    "PN100": {'1/2"': 105, '3/4"': 130, '1"': 140},
    "PN160": {'1/2"': 105, '1"': 140},
    "PN250": {'1/2"': 130, '1"': 150},
    "JIS/KS 40K": {'1/2"': 115, '3/4"': 120, '1"': 130},
}
OD["ANSI 600"], OD["ANSI 300"] = OD["ASME 600"], OD["ASME 300"]
S3 = ['1/2"', '3/4"', '1"']


def _tab(sizes, **cols):
    return {s: {k: v[i] for k, v in cols.items()} for i, s in enumerate(sizes)}


DATA = {
    "TDC46M": {
        "name": "TDC46M", "type": "Thermodynamic with strainer, carbon steel, maintainable seat", "ti": "TI-P187-04",
        "variants": ["screwed", "socket weld", "ASME 150", "ASME 300", "ASME 600", "PN40", "PN100"],
        "sizes": _tab(S3, A=[58, 61, 65], B_scr=[78, 95, 95], B_sw=[92, 92, 92], B_fl=[150, 150, 160],
                      B_pn100=[210, 210, 230], C=[61, 61, 61], D=[59, 63, 67]),
        "note": "Length B for the connection picked, cap diameter C, A (pipe centreline to the top of the cap) and D (pipe "
                "centreline to the bottom of the strainer cap) are from the TI table. Screwed and socket weld use the "
                "TI's screwed drawing, flanged the flanged drawing. The TI drawings are not to scale along the pipe, so the "
                "cap is set to C and the body ends (or the necks to the flanges) take up the rest of B. Flange diameter is "
                "ASME B16.5 / EN 1092-1, since the TI does not list it; flange thickness is kept in proportion to the drawn "
                "flange, not taken from the standard. Withdrawal distances E (40 below) and F (30 above) are not drawn.",
    },
    "TD62M-FL": {
        "name": "TD62M flanged / TD62LM flanged", "type": "Thermodynamic, high pressure, ASTM body, flanged",
        "ti": "TI-P068-20", "variants": ["ANSI 600", "ANSI 300", "JIS/KS 40K"],
        "sizes": _tab(S3, A=[87, 87, 87], B_600=[147, 151, 160], B_300=[135, 138, 147], B_jis=[146, 146, 156],
                      C=[92, 92, 92], D=[72, 72, 72]),
        "note": "Face to face B for the flange picked, cap diameter C, A (pipe centreline to the top of the cap) and D "
                "(pipe centreline to the bottom of the cover nuts) are from the TI table. The TD62LM has the same "
                "outline. The body keeps its drawn width (scaled with C) and the flanges take up the rest of B, so flange "
                "thickness differs by class as the TI lengths do. Flange diameter is ASME B16.5 or JIS B 2220 40K, since "
                "the TI does not list it. Withdrawal distances E (40 below) and F (30 above) are not drawn. The screwed and "
                "socket weld TD62M / TD62LM (TI-P068-08) is the separate TD62M pack.",
    },
    "TD120M": {
        "name": "TD120M", "type": "Thermodynamic, high pressure, replaceable seat", "ti": "TI-P150-11",
        "variants": ["butt weld", "socket weld", "ASME 600", "ASME 900 / 1500", "PN100"],
        "sizes": _tab(S3, A_w=[78, 80, 80], E_w=[78, 78, 78], B=[157, 157, 157], B1=[156, 156, 170],
                      A_fl=[80, 80, 80], E_fl=[80, 80, 80], B2_600=[210, 240, 260], B2_900=[240, 240, 260],
                      B2_pn100=[210, 240, 260], F=[117, 117, 117]),
        "note": "Length (B butt weld, B1 socket weld, B2 flanged), A (top of the cap nuts to the pipe centreline), E (pipe "
                "centreline to the bottom of the cap nuts) and body width F are from the TI tables. The TI draws the "
                "flanged trap; butt and socket weld ends are the same body cut at the end of the neck, where the TI's B "
                "extension lines sit. Flange diameter is ASME B16.5 / EN 1092-1 (the TI does not list it); flange "
                "thickness is kept in proportion to the drawn flange. The TI drawing does not mark the flow direction; "
                "in is on the left. Withdrawal distances C and D (56 above and below) are not drawn. PN160 and PN250 "
                "(1/2\" and 1\" only) are the TD120M PN160 / PN250 pack.",
    },
    "TD120M-PN": {
        "name": "TD120M PN160 / PN250", "type": "Thermodynamic, high pressure, replaceable seat", "ti": "TI-P150-11",
        "variants": ["PN160", "PN250"],
        "sizes": _tab(['1/2"', '1"'], A_fl=[80, 80], E_fl=[80, 80], B2_pn160=[210, 260], B2_pn250=[240, 240],
                      F=[117, 117]),
        "note": "DN15 and DN25 only (the TI lists no DN20 for PN160 and PN250). Face to face B2, A, E and F are from the TI "
                "tables; the TI's PN250 B2 of 240 covers both sizes. Flange diameter is EN 1092-1 (the TI does not list "
                "it); flange thickness is kept in proportion to the drawn flange. The TI drawing does not mark the flow "
                "direction; in is on the left. Withdrawal distances C and D (56 above and below) are not drawn.",
    },
    "HM34": {
        "name": "HM34", "type": "Inverted bucket, steel, integral strainer", "ti": "TI-2-404-US",
        "variants": ["screwed NPT", "socket weld"],
        "sizes": _tab(S3, A=[119.4, 119.4, 180.3], B=[104.1, 104.1, 160.0], F=[66.0, 88.9, 144.8], G=[88.9, 106.7, 119.4]),
        "source": "Vectorised from the TI picture (the sheet has no vector drawing)",
        "note": "Section view, as the TI draws it: in on the left, out on the right, both on the same centreline. The TI "
                "drawing is only a picture, so it was vectorised (tools/raster.py), not traced: lines follow the picture "
                "to about 0.5 mm, joints are not as clean as a traced drawing, and the thread lines in the connections are "
                "wavy as on the TI. Face to face A, centreline to the top of the cover F and centreline to the bottom of "
                "the strainer housing G are from the TI table (x and y are set separately; the picture is not to scale). "
                "The TI has one drawing for all three sizes, so the 1\" (much taller above the centreline, F 5.7\") is the "
                "same picture stretched, not its own shape. Cover width B is not set; it comes out within 1% (1/2\", 3/4\") and 2% (1\") of the table. "
                "Withdrawal distances C (above the cover) and H (strainer screen) are not drawn. Screwed and socket weld "
                "have the same outline.",
    },
}
_cache = {}


def _ch(key, pdf, page, clip, drop=(), min_lw=0.0):
    """Stroked chains (pdf line width, segs); white strokes and lines thinner than min_lw (dimensions) left out."""
    if key not in _cache:
        _cache[key] = [(w, segs) for w, segs, grey, _ in _chains(pdf, page, clip, drop=drop) if grey < 0.9 and w >= min_lw]
    return _cache[key]


def _rigid(chains, box, f, k):
    """Chains inside box move as one piece: their centre goes where f puts it, scaled by k (flow arrows)."""
    out, rest = [], []
    for w, segs in chains:
        bb = _bb(segs)
        (out if bb[0] >= box[0] and bb[2] <= box[2] and bb[1] >= box[1] and bb[3] <= box[3] else rest).append((w, segs))
    if not out:
        return [], rest
    P = np.vstack([T.flat(sg) for _, segs in out for sg in segs])
    cx, cy = (P[:, 0].min() + P[:, 0].max()) / 2, (P[:, 1].min() + P[:, 1].max()) / 2
    X, Y = f((cx, cy), (cx, cy, cx, cy))
    g = lambda p, bb: (X + (p[0] - cx) * k, Y + (p[1] - cy) * k)
    return _map(out, g), rest


def _cut_x(chains, xa, xb):
    """Keep only what lies between xa and xb; straight segments crossing them are cut there."""
    out = []
    for w, segs in chains:
        keep = []
        for sg in segs:
            P = np.array(sg[1:], float)
            if P[:, 0].min() >= xa - 1e-6 and P[:, 0].max() <= xb + 1e-6:
                keep.append(sg)
            elif sg[0] == "l" and P[:, 0].max() > xa and P[:, 0].min() < xb:
                (x0, y0), (x1, y1) = P
                ts = sorted([0.0, 1.0] + [(xc - x0) / (x1 - x0) for xc in (xa, xb) if 0 < (xc - x0) / (x1 - x0) < 1])
                for t0, t1 in zip(ts, ts[1:]):
                    xm = x0 + (x1 - x0) * (t0 + t1) / 2
                    if xa <= xm <= xb:
                        keep.append(("l", (x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0), (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)))
        if keep:
            out.append((w, keep))
    return out


def _fy_flange(dy, n, k, R, r):
    """Flange y: inside the neck joint (|dy| <= n) the body scale k, so the neck meets the flange; out to the drawn
    flange radius R it runs on to the real flange radius r."""
    a = abs(dy)
    if a <= n:
        return dy * k
    return np.sign(dy) * (n * k + (a - n) * (r - n * k) / (R - n))


def _map(chains, f):
    return [(w, [(sg[0],) + tuple(f(p, _bb(segs)) for p in sg[1:]) for sg in segs]) for w, segs in chains]


# ---------------------------------------------------------------- TDC46M
def _tdc46m(d, v, size):
    A, C, D = d["A"], d["C"], d["D"]
    if v in ("screwed", "socket weld"):
        B = d["B_scr"] if v == "screwed" else d["B_sw"]
        ch = _ch("tdc_s", TDC46M_PDF, 8, (75, 105, 200, 280))
        xl, xr, yc, top, bot = 76.17, 189.31, 191.3, 113.06, 270.35
        cx, m0, m1 = (91.82 + 176.31) / 2, 90.42, 177.88          # cap centre, the middle part kept at the cap scale
        kc = C / (176.31 - 91.82)
        X = lambda x: B / 2 + (x - (xl + xr) / 2) * kc            # middle part (body centre under the cap centre)
        def f(p, bb):
            x, y = p
            if y > 214.0 or m0 <= x <= m1:                        # strainer and the middle of the body
                xx = X(x)
            elif x < m0:
                xx = (x - xl) / (m0 - xl) * X(m0)
            else:
                xx = X(m1) + (x - m1) / (xr - m1) * (B - X(m1))
            return xx, (y - yc) * (A / (yc - top) if y < yc else D / (bot - yc))
        arrow, rest = _rigid(ch, (166, 182, 184, 202), f, kc)
        return _map(rest, f) + arrow, B, None
    fl = OD[v][size]
    B = d["B_pn100"] if v == "PN100" else d["B_fl"]
    ch = _ch("tdc_f", TDC46M_PDF, 8, (260, 105, 555, 285), drop=[(296, 274.5, 413, 275.6)])
    xl, xr, yc, top, bot, R = 266.40, 545.61, 191.405, 113.08, 274.57, (276.44 - 106.37) / 2
    rf_d, fb_l, fb_r = 268.77, 295.53, 516.42                     # raised face / flange face, back of the flanges
    m0, m1, cx = 361.28, 451.11, 406.0
    kc = C / (443.64 - 368.37)
    kf = fl / 2 / R
    rf, t = (rf_d - xl) * kf, (fb_l - rf_d) * kf                  # flange kept in proportion to its drawn shape
    X = lambda x: B / 2 + (x - cx) * kc
    def f(p, bb):
        x, y = p
        if bb[2] <= fb_l + 0.1 or bb[0] >= fb_r - 0.1:            # flange and raised face
            xx = (x - xl) * kf if x < cx else B - (xr - x) * kf
            return xx, _fy_flange(y - yc, 41.0, A / (yc - top) if y < yc else D / (bot - yc), R, fl / 2)
        if m0 <= x <= m1:
            xx = X(x)
        elif x < m0:
            xx = _pw(x, [fb_l, m0], [rf + t, X(m0)])
        else:
            xx = _pw(x, [m1, fb_r], [X(m1), B - rf - t])
        return xx, (y - yc) * (A / (yc - top) if y < yc else D / (bot - yc))
    arrow, rest = _rigid(ch, (456, 182, 474.5, 202), f, kc)
    return _map(rest, f) + arrow, B, fl


# ---------------------------------------------------------------- TD62M / TD62LM flanged
def _td62fl(d, v, size):
    A, C, D = d["A"], d["C"], d["D"]
    B = d[{"ANSI 600": "B_600", "ANSI 300": "B_300", "JIS/KS 40K": "B_jis"}[v]]
    fl = OD[v][size]
    ch = _ch("td62fl", TD62FL_PDF, 4, (195, 100, 392, 310))
    xl, xr, yc, top, bot, R = 203.72, 387.93, 215.33, 109.70, 303.47, (280.23 - 150.43) / 2
    ff_l, fb_l, fb_r, ff_r = 206.15, 232.84, 358.81, 385.50       # flange faces and backs
    m0, m1, cx = 241.81, 349.84, (240.14 + 351.51) / 2
    kc = C / (351.51 - 240.14)
    kf = fl / 2 / R
    X = lambda x: B / 2 + (x - cx) * kc
    neck = (m0 - fb_l) * kc                                       # drawn neck length, kept
    rf = (ff_l - xl) * kf
    back = X(m0) - neck                                           # back of the flange: the rest of B is flange
    def f(p, bb):
        x, y = p
        if bb[2] <= fb_l + 0.4 or bb[0] >= fb_r - 0.4:          # flange (its back edge is drawn a little skew)
            if x < cx:
                xx = _pw(x, [xl, ff_l, fb_l], [0, rf, back])
            else:
                xx = _pw(x, [fb_r, ff_r, xr], [B - back, B - rf, B])
            return xx, _fy_flange(y - yc, (y < yc) * 46.41 + (y >= yc) * 46.41, A / (yc - top) if y < yc else D / (bot - yc), R, fl / 2)
        if m0 <= x <= m1:
            xx = X(x)
        elif x < m0:
            xx = _pw(x, [fb_l, m0], [back, X(m0)])
        else:
            xx = _pw(x, [m1, fb_r], [X(m1), B - back])
        return xx, (y - yc) * (A / (yc - top) if y < yc else D / (bot - yc))
    out = _map(ch, f)
    d["Flange thickness (from B)"] = round(back - rf, 1)
    return out, B, fl


# ---------------------------------------------------------------- TD120M
def _td120m(d, v, size):
    flanged = v not in ("butt weld", "socket weld")
    F = d["F"]
    A, E = (d["A_fl"], d["E_fl"]) if flanged else (d["A_w"], d["E_w"])
    ch = _ch("td120", TD120M_PDF, 5, (60, 130, 280, 315), min_lw=0.8)
    yc, top, bot = 221.44, 137.93, 304.94
    bl, br = 105.33, 226.80                                        # body sides (F)
    cx = (bl + br) / 2
    kx = F / (br - bl)
    X = lambda x: F / 2 + (x - cx) * kx                            # body, centred on 0..F
    ky = lambda y: (y - yc) * (A / (yc - top) if y < yc else E / (bot - yc))
    if not flanged:
        L = d["B"] if v == "butt weld" else d["B1"]
        xe_l, xe_r = 84.30, 247.85                                 # neck ends (the TI's B extension lines)
        sh = (L - F) / 2
        def f(p, bb):
            x, y = p
            if x < bl:
                xx = _pw(x, [xe_l, bl], [0, sh])
            elif x > br:
                xx = _pw(x, [br, xe_r], [sh + F, L])
            else:
                xx = sh + X(x)
            return xx, ky(y)
        out = _map(_cut_x(ch, xe_l, xe_r), f)
        # close the neck ends with a short line, as the kit does for screwed / welded ends
        for xx in (0.0, L):
            yy = [p[1] for _, segs in out for sg in segs for p in sg[1:] if abs(p[0] - xx) < 0.05]
            if yy:
                out.append((0.82, [("l", (xx, min(yy)), (xx, max(yy)))]))
        return out, L, None
    key = {"ASME 600": "B2_600", "ASME 900 / 1500": "B2_900", "PN100": "B2_pn100", "PN160": "B2_pn160", "PN250": "B2_pn250"}[v]
    L = d[key]
    fl = OD[v][size]
    xl, xr, R = 67.19, 264.94, (273.61 - 169.26) / 2
    ff_l, ff_r = 80.37, 251.76
    kf = fl / 2 / R
    t = (ff_l - xl) * kf
    sh = (L - F) / 2
    def f(p, bb):
        x, y = p
        if bb[2] <= ff_l + 0.1 or bb[0] >= ff_r - 0.1:
            xx = (x - xl) * kf if x < cx else L - (xr - x) * kf
            return xx, _fy_flange(y - yc, 18.35, A / (yc - top) if y < yc else E / (bot - yc), R, fl / 2)
        if x < bl:
            xx = _pw(x, [ff_l, bl], [t, sh])
        elif x > br:
            xx = _pw(x, [br, ff_r], [sh + F, L - t])
        else:
            xx = sh + X(x)
        return xx, ky(y)
    return _map(ch, f), L, fl


# ---------------------------------------------------------------- HM34 (raster)
HM34_IMG = dict(page=2, rect=(69.324, 103.597, 252.924, 304.717), px=765)
HM34_WHITE = [(0, 0, 766, 100), (150, 95, 160, 328), (178, 95, 190, 188), (525, 95, 535, 122), (550, 95, 566, 128),
              (150, 117, 299, 127), (325, 95, 365, 113), (145, 397, 157, 404),
              (60, 753, 398, 766), (395, 750, 410, 766), (497, 736, 509, 752), (420, 748, 766, 839), (555, 680, 766, 839),
              (0, 0, 160, 328), (0, 328, 157, 839), (0, 766, 766, 839)]
HM34_FIX = [((200, 546), (200, 578))]                                     # a break in the outer wall on the picture
HM34_MARK = dict(xin=159.5, xout=559.0, yc=400.0, top=119.0, bot=755.0)    # picture px: faces, centreline, extents


def _hm34(self):
    import raster as R
    d = self.d
    A, Fu, G = d["A"], d["F"], d["G"]
    if "hm34" not in _cache:
        import cv2
        g0 = R.render(HM34_PDF, HM34_IMG["page"], HM34_IMG["rect"], HM34_IMG["px"])
        for a, b in HM34_FIX:
            cv2.line(g0, a, b, 0, 2)
        g, o = R.crop(g0, (110, 60, 640, 839), HM34_WHITE)
        pl = [(w, Q) for w, Q in R.polylines(g, o, thresh=200, min_w=1.5)
              if np.hypot(*np.diff(Q, axis=0).T).sum() >= 6]
        _cache["hm34"] = (pl, R.silhouette(g, o, thresh=200, close=27))
    pl, sil = _cache["hm34"]
    M = HM34_MARK
    kx = A / (M["xout"] - M["xin"])
    fx = lambda x: (x - M["xin"]) * kx
    fy = lambda y: (y - M["yc"]) * (Fu / (M["yc"] - M["top"]) if y < M["yc"] else G / (M["bot"] - M["yc"]))
    lw = 0.6
    strokes = []
    for w, Q in pl:
        pts = [(fx(x), fy(y)) for x, y in Q]
        strokes.append([["l", pts[i], pts[i + 1]] for i in range(len(pts) - 1)])
    self.fill = [[(fx(x), fy(y)) for x, y in poly] for poly in sil]
    self.strokes = [(lw, segs) for segs in strokes]
    P = np.array([p for poly in self.fill for p in poly])
    self.x0, self.y0 = min(P[:, 0].min(), 0.0), min(P[:, 1].min(), -Fu)
    self.x1, self.y1 = max(P[:, 0].max(), A), max(P[:, 1].max(), G)
    self.w, self.h = self.x1 - self.x0, self.y1 - self.y0
    self.ports = {"in": (0.0, 0.0), "out": (round(A, 2), 0.0)}
    self.arrow = None
    d["Cover width B as drawn"] = round((530 - 183) * kx, 1)


class Trap:
    def __init__(self, model, size, variant=None):
        dd = DATA[model]
        self.model, self.size, self.variant = model, size, variant or dd["variants"][0]
        self.d = dict(dd["sizes"][size])
        v = self.variant
        if model == "HM34":
            _hm34(self)
            return
        if model == "TDC46M":
            chains, L, fl = _tdc46m(self.d, v, size)
            dd_ = self.d
            self.d = {"A": dd_["A"], "B": L, "C": dd_["C"], "D": dd_["D"]}
        elif model == "TD62M-FL":
            chains, L, fl = _td62fl(self.d, v, size)
            dd_ = self.d
            self.d = {"A": dd_["A"], "B": L, "C": dd_["C"], "D": dd_["D"],
                      "Flange thickness (from B)": dd_["Flange thickness (from B)"]}
        else:                                                          # TD120M, TD120M-PN
            chains, L, fl = _td120m(self.d, v, size)
            dd_ = self.d
            fln = v not in ("butt weld", "socket weld")
            self.d = {"A": dd_["A_fl"] if fln else dd_["A_w"], "E": dd_["E_fl"] if fln else dd_["E_w"],
                      ("B2" if fln else "B1" if v == "socket weld" else "B"): L, "F": dd_["F"]}
        if fl:
            self.d["Flange OD"] = fl
        P = np.array([p for _, segs in chains for sg in segs for p in sg[1:]])
        span = max(P[:, 0].max() - P[:, 0].min(), P[:, 1].max() - P[:, 1].min())
        lw = max(0.5, 0.0075 * span)
        wmax = max(w for w, _ in chains)
        thick = [(lw if w > 0.75 * wmax else lw * 0.6, segs) for w, segs in chains]
        mg = 6 + 0.03 * span
        c2 = (P[:, 0].min() - mg, P[:, 1].min() - mg, P[:, 0].max() + mg, P[:, 1].max() + mg)
        g = T.assemble(thick, [], c2, px=min(10.0, 3600 / max(c2[2] - c2[0], c2[3] - c2[1])))
        self.fill = [[tuple(p) for p in poly] for poly in g["fill"]]
        self.strokes = [(w, [[sg[0]] + [tuple(p) for p in sg[1:]] for sg in segs]) for w, segs in g["outline"]]
        m = lw / 2
        F_ = np.array([p for poly in self.fill for p in poly])
        self.x0, self.y0 = min(F_[:, 0].min(), P[:, 0].min()) - m, min(F_[:, 1].min(), P[:, 1].min()) - m
        self.x1, self.y1 = max(F_[:, 0].max(), P[:, 0].max()) + m, max(F_[:, 1].max(), P[:, 1].max()) + m
        self.w, self.h = self.x1 - self.x0, self.y1 - self.y0
        self.ports = {"in": (0.0, 0.0), "out": (round(L, 2), 0.0)}
        self.arrow = None
        self.lw = lw
