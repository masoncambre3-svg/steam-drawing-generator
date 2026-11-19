"""Ball float steam traps (2026-11-19): FT14, FTC62, FTC80. Front elevation, pipe left to right.

FT14   TI-S02-03 p5 (screwed, left drawing) and TI-S02-26 p5 (flanged, left drawing). SG iron.
FTC62  TI-P179-13 p8: flanged (top left drawing) and screwed / socket weld (bottom left drawing).
FTC80  TI-P179-02 p5, left drawing. Socket weld body; the ASME 600 flanges and necks are drawn dashed on the TI and
       are drawn solid here for the flanged variant. BDV2 air vent on the cover as drawn; "plug" replaces it.

The FTC62 page carries hidden copies of the linework (offset 10 mm and 6 mm, covered by white fills or clipped),
so every drawing here is read through `_visible`: a stroke is kept only where the rendered page has ink under it.
Fully visible strokes keep their own segments (curves stay curves); partly hidden ones are cut into the visible
pieces (polylines, pieces under 3 pt dropped). Dimension lines that lie on the outline are dropped with boxes.

Every TI here draws the trap with flow right to left (FTC62 has the arrow on the cover; R-L is the standard
build for FT14 and FTC80). The drawings are mirrored so the inlet is on the left at x = 0 and flow runs +x,
like every other pack. Mirror (M) in the app gives R-L.

x: the body keeps one scale (from its height in the TI table, so round things stay round) and the hubs / necks
take up the rest of the face to face. Flanges: OD from the standard, thickness kept in proportion to the drawn
flange (scaled with the OD), so flange thickness is not from the standard either.
"""
import numpy as np
import pymupdf
import ti_trace as T
from universal import _chains, _pw
from traps2 import _fy_flange
from sources import FT14S_PDF, FT14F_PDF, FTC62_PDF, FTC80_PDF

# flange outside diameters, mm (the TIs give face to face only): EN 1092-1, ASME B16.5, JIS B 2220
OD = {
    "PN16": {'1/2"': 95, '3/4"': 105, '1"': 115},
    "ASME 150": {'1/2"': 88.9, '3/4"': 98.6, '1"': 108.0},
    "JIS/KS 20K": {'1/2"': 95, '3/4"': 100, '1"': 125},
    "PN100": {'1/2"': 105, '3/4"': 130, '1"': 140},
    "ASME 600": {'1/2"': 95.3, '3/4"': 117.5, '1"': 124.0, '1-1/2"': 155.4, '2"': 165.1},
}
PIPE_OD = {'1/2"': 21.3, '3/4"': 26.7, '1"': 33.4, '1-1/2"': 48.3, '2"': 60.3}
S3 = ['1/2"', '3/4"', '1"']


def _tab(sizes, **cols):
    return {s: {k: v[i] for k, v in cols.items()} for i, s in enumerate(sizes)}


DATA = {
    "FT14": {
        "name": "FT14", "type": "Ball float (F&T), SG iron, horizontal", "ti": "TI-S02-03 / TI-S02-26",
        "variants": ["screwed", "PN16", "ASME 150", "JIS/KS 20K"],
        "sizes": _tab(S3, A_scr=[121, 121, 145], B_scr=[107, 107, 107],
                      A_fl=[150, 150, 160], A_jis=[150, 150, 170], B_fl=[107, 107, 117]),
        "note": "Front elevation (the TI's left drawing): face to face A and height B from the TI tables, screwed from "
                "TI-S02-03, flanged from TI-S02-26. One outline per TI for every size: the cover keeps its drawn shape at "
                "the scale set by B, and the hubs (screwed) or necks (flanged) take up the rest of A. The pipe "
                "centreline is where the TI draws it (not tabled). Screwed 1\": the drawn hub (31 mm tall at B) is "
                "smaller than 1\" pipe, so its hub is drawn 42 mm tall (1.25 x pipe OD, assumed). Flange OD is EN 1092-1 "
                "PN16, ASME B16.5 Class 150 or JIS B 2220 20K (not in the TI); flange thickness scales with the drawn "
                "flange. Drawn R-L on the TIs, mirrored so in is on the left. BSP and NPT share the screwed outline. "
                "FT14V, FT14-C (needle valve, F) and the side view (C, D, E) are not drawn.",
    },
    "FTC62": {
        "name": "FTC62", "type": "Ball float (F&T), carbon steel, high pressure", "ti": "TI-P179-13",
        "variants": ["screwed", "socket weld", "PN100", "ASME 600"],
        "sizes": _tab(S3, A_scr=[190, 190, 190], A_pn=[300, 300, 300], A_600=[261, 271, 291],
                      F=[239, 239, 239]),
        "note": "Front elevation (the TI's left drawings): face to face A for the connection picked and height F from "
                "the TI table; screwed and socket weld use the TI's screwed / SW drawing, flanged the flanged drawing. "
                "The body keeps its drawn shape at the scale set by F; hubs or necks take up the rest of A (the screwed "
                "hubs come out shorter than drawn: the TI drawing is not to scale along the pipe). The pipe centreline "
                "is where the TI draws it (not tabled). Flange OD is EN 1092-1 PN100 or ASME B16.5 Class 600 (not in "
                "the TI); flange thickness scales with the drawn flange. The TI page holds hidden offset copies of the "
                "linework; only what prints is traced. Drawn R-L (arrow on the cover), mirrored so in is on the left "
                "and the arrow points with the flow. Side view (B, C, D, E) not drawn.",
    },
    "FTC80": {
        "name": "FTC80", "type": "Ball float (F&T), cast steel, high pressure", "ti": "TI-P179-02",
        "variants": ["socket weld, BDV2", "socket weld, plug", "ASME 600, BDV2", "ASME 600, plug"],
        "sizes": _tab(['1-1/2"', '2"'], A_sw=[555, 555], A_600=[755, 785], B_bdv2=[430, 430], B_plug=[390, 390],
                      C=[324, 324], D=[110.5, 110.5]),
        "note": "Front elevation (the TI's left drawing), drawn to scale on the TI (3.13 mm/pt both ways). A for the "
                "connection, B (base to top of the BDV2 air vent, or of the plug) and D (pipe centreline to base) from "
                "the TI table. To hit B and D exactly the feet are 2.5 mm shorter than drawn and the cover dome 8.7 mm "
                "taller (the drawn body comes out at B 424, D 113). The TI draws the ASME 600 flanges and necks dashed "
                "(1-1/2\" drawn); they are drawn solid for the flanged variants, the 2\" with longer necks to its A and "
                "B16.5 Class 600 OD (thickness scales with the drawn flange). Plug variant: the BDV2 is left off and a "
                "hex plug is drawn on the cover boss, 19 mm across (assumed, the TI has no picture) and as tall as B "
                "allows (about 6 mm). Socket weld 1-1/2\" and 2\" share one body (same A). Drawn R-L, mirrored so the "
                "strainer (inlet) end is on the left. End view (C, F) not drawn.",
    },
}

_cache = {}


def _visible(key, pdf, page, clip, drop=(), min_lw=0.0, Z=6, step=0.3, minlen=2.0):
    """Stroked chains inside clip, cut to what actually prints (ink under the line on a render of the page)."""
    if key in _cache:
        return _cache[key]
    pg = pymupdf.open(pdf)[page - 1]
    pm = pg.get_pixmap(matrix=pymupdf.Matrix(Z, Z), colorspace=pymupdf.csGRAY)
    im = np.frombuffer(pm.samples, np.uint8).reshape(pm.h, pm.w)
    ins = lambda bb, b: bb[0] >= b[0] and bb[2] <= b[2] and bb[1] >= b[1] and bb[3] <= b[3]
    out = []
    for w, segs, grey, _ in _chains(pdf, page, clip, drop=drop):
        if grey > 0.9 or w < min_lw:
            continue
        pts = []
        for s in segs:
            f = T.flat(s) if s[0] == "c" else np.array([s[1], s[2]], float)
            for a, b in zip(f[:-1], f[1:]):
                n = max(2, int(np.hypot(*(b - a)) / step) + 1)
                q = np.linspace(a, b, n)
                pts.append(q if not pts else q[1:])
        P = np.vstack(pts)
        ink = np.array([im[max(0, int(y * Z) - 1):int(y * Z) + 2, max(0, int(x * Z) - 1):int(x * Z) + 2].min() < 140
                        for x, y in P])
        if ink.all():
            out.append((w, [(sg[0],) + tuple(tuple(map(float, p)) for p in sg[1:]) for sg in segs]))
            continue
        i = 0
        while i < len(P):
            if not ink[i]:
                i += 1
                continue
            j = i
            while j + 1 < len(P) and ink[j + 1]:
                j += 1
            Q = P[i:j + 1]
            # a hidden copy only shows ink where it happens to lie on a printed line: a chain mostly without ink keeps
            # only long pieces
            if np.hypot(*np.diff(Q, axis=0).T).sum() >= (minlen if ink.mean() >= 0.5 else 8.0):
                import cv2
                Q = cv2.approxPolyDP(Q.astype(np.float32).reshape(-1, 1, 2), 0.04, False)[:, 0, :].astype(float)
                bb = (Q[:, 0].min(), Q[:, 1].min(), Q[:, 0].max(), Q[:, 1].max())
                if not any(ins(bb, b) for b in drop):
                    out.append((w, [("l", tuple(Q[k]), tuple(Q[k + 1])) for k in range(len(Q) - 1)]))
            i = j + 1
    _cache[key] = out
    return out


def _map(chains, f):
    return [(w, [(sg[0],) + tuple(f(p) for p in sg[1:]) for sg in segs]) for w, segs in chains]


def _snap(x, xs, tol=0.9):
    """Flange faces and backs are drawn a little skew on these TIs; a skew back in the neck zone gets stretched with
    the neck. Points within tol of a listed x are put on it."""
    for v in xs:
        if abs(x - v) < tol:
            return v
    return x


def _axial(L, k, m0, m1, face_l, face_r, fl=None):
    """x map for a body between m0 and m1 (one scale k, centred on L/2) with hubs / necks out to the faces.
    fl = (kf, fb_l, fb_r): flanges keep their drawn shape scaled by kf, from the face to the flange back."""
    xm = (m0 + m1) / 2
    X = lambda x: L / 2 + (x - xm) * k
    if fl is None:
        return lambda x: X(x) if m0 <= x <= m1 else (_pw(x, [face_l, m0], [0, X(m0)]) if x < m0
                                                      else _pw(x, [m1, face_r], [X(m1), L]))
    kf, fb_l, fb_r = fl
    tl, tr = (fb_l - face_l) * kf, (face_r - fb_r) * kf

    def fx(x):
        if m0 <= x <= m1:
            return X(x)
        if x <= fb_l:
            return (x - face_l) * kf
        if x >= fb_r:
            return L - (face_r - x) * kf
        return _pw(x, [fb_l, m0], [tl, X(m0)]) if x < m0 else _pw(x, [m1, fb_r], [X(m1), L - tr])
    return fx


# ---------------------------------------------------------------- FT14
def _ft14(d, v, size):
    if v == "screwed":
        ch = _visible("ft14s", FT14S_PDF, 5, (147, 95, 233.5, 170.5), min_lw=0.7)
        face_l, face_r, m0, m1, yc, top, bot = 149.33, 231.32, 154.53, 226.12, 133.09, 97.64, 168.54
        A, B = d["A_scr"], d["B_scr"]
        k = B / (bot - top)
        fx = _axial(A, k, m0, m1, face_l, face_r)
        hub = 143.48 - 122.70                                  # drawn hub height, pt
        out = _map(ch, lambda p: (fx(p[0]), (p[1] - yc) * k))
        hh = max(hub * k, 1.25 * PIPE_OD[size]) if hub * k < 1.1 * PIPE_OD[size] else hub * k
        if hh > hub * k + 0.01:
            out = _ft14_hub(ch, out, fx, k, yc, hh, face_l, face_r)
        return out, A, None
    A = d["A_jis"] if v == "JIS/KS 20K" else d["A_fl"]
    B = d["B_fl"]
    ch = _visible("ft14f", FT14F_PDF, 5, (62, 72, 143, 131), min_lw=0.6)
    face_l, face_r, fb_l, fb_r, m0, m1 = 63.64, 141.44, 70.25, 134.83, 74.39, 130.77
    yc, top, bot, R = (75.35 + 127.71) / 2, 73.32, 129.75, (127.71 - 75.35) / 2
    k = B / (bot - top)
    fl = OD[v][size]
    kf = fl / 2 / R
    fx = _axial(A, k, m0, m1, face_l, face_r, (kf, fb_l, fb_r))
    f = lambda p: (fx(p[0]), _fy_flange(p[1] - yc, 8.3, k, R, fl / 2) if (p[0] <= fb_l + 0.4 or p[0] >= fb_r - 0.4)
                   else (p[1] - yc) * k)
    return _map(ch, f), A, fl


def _ft14_hub(ch, out, fx, k, yc, hh, face_l, face_r):
    """Screwed 1": hub drawn taller than the TI. Hub top / bottom lines move out to hh / 2 and run in to the cover edge;
    the end faces are redrawn at the new height. Everything else as traced."""
    h0 = 10.39                                              # drawn hub half height, pt
    yn = hh / 2 / k                                         # new half height, pt
    keep = []
    for w, segs in ch:
        P = np.array([p for sg in segs for p in sg[1:]])
        hubline = (len(segs) == 1 and segs[0][0] == "l" and np.ptp(P[:, 1]) < 0.02 and abs(abs(P[0, 1] - yc) - h0) < 0.05
                   and (P[:, 0].max() < 157.6 or P[:, 0].min() > 223.1))
        face = (len(segs) == 1 and segs[0][0] == "l" and np.ptp(P[:, 0]) < 0.02
                and (abs(P[0, 0] - face_l) < 0.05 or abs(P[0, 0] - face_r) < 0.05))
        if not (hubline or face):
            keep.append((w, segs))
    # cover edge x at the new hub height: the body outline near the hubs (left and right)
    edge = np.vstack([T.flat(sg) for w, segs in keep for sg in segs])
    lw = ch[0][0]
    new = []
    for side, xf in (("l", face_l), ("r", face_r)):
        for sgn in (-1, 1):
            y = yc + sgn * yn
            band = edge[np.abs(edge[:, 1] - y) < 0.35]
            band = band[(band[:, 0] > 154) & (band[:, 0] < 163)] if side == "l" else band[(band[:, 0] < 226.5) & (band[:, 0] > 217.5)]
            xe = band[:, 0].min() if side == "l" else band[:, 0].max()
            new.append((lw, [("l", (xf, y), (xe, y))]))
        new.append((lw, [("l", (xf, yc - yn), (xf, yc + yn))]))
    return _map(keep + new, lambda p: (fx(p[0]), (p[1] - yc) * k))


# ---------------------------------------------------------------- FTC62
def _ftc62(d, v, size):
    F = d["F"]
    if v in ("screwed", "socket weld"):
        ch = _visible("ftc62s", FTC62_PDF, 8, (212, 312, 345, 455),
                      drop=[(289, 317.5, 352, 318.5), (279.5, 449.3, 352, 450), (216, 402.6, 218.5, 456), (333.5, 402.6, 335, 456)])
        face_l, face_r, m0, m1, yc, top, bot = 217.22, 334.01, 231.10, 319.85, 391.70, 318.03, 449.65
        A = d["A_scr"]
        k = F / (bot - top)
        fx = _axial(A, k, m0, m1, face_l, face_r)
        return _map(ch, lambda p: (fx(p[0]), (p[1] - yc) * k)), A, None
    A = d["A_pn"] if v == "PN100" else d["A_600"]
    ch = _visible("ftc62f", FTC62_PDF, 8, (205, 105, 355, 250),
                  drop=[(284.5, 242.9, 351, 243.4), (209.5, 196.5, 211, 251), (349.6, 196.5, 351, 251)])
    face_l, face_r, fb_l, fb_r, m0, m1 = 210.48, 350.42, 222.15, 338.94, 236.02, 325.05
    yc, top, bot, R = 185.45, 111.92, 243.54, (211.80 - 159.10) / 2
    k = F / (bot - top)
    fl = OD[v][size]
    kf = fl / 2 / R
    fx = _axial(A, k, m0, m1, face_l, face_r, (kf, fb_l, fb_r))
    sx = lambda x: _snap(x, (212.35, fb_l, fb_r, 348.65), 0.7)
    f = lambda p: (fx(sx(p[0])), _fy_flange(p[1] - yc, 10.2, k, R, fl / 2) if (sx(p[0]) <= fb_l or sx(p[0]) >= fb_r)
                   else (p[1] - yc) * k)
    return _map(ch, f), A, fl


# ---------------------------------------------------------------- FTC80
def _ftc80(d, v, size):
    flanged, plug = v.startswith("ASME"), v.endswith("plug")
    clip = (110, 82, 359, 224)
    ch = _visible("ftc80", FTC80_PDF, 5, clip)
    face_l, face_r, yc = 147.57, 324.73, 182.35
    k = d["A_sw"] / (face_r - face_l)                          # 3.133 mm/pt; the TI is to scale
    boss, bdv_top, cover, foot0, base = 97.74, 83.14, 143.5, 208.0, 218.41
    up = (d["B_bdv2"] - d["D"]) - (yc - bdv_top) * k           # extra height above the centreline (8.7)
    yb0 = (foot0 - yc) * k

    def fy(y):
        if y >= foot0:                                          # feet: base lands on D
            return _pw(y, [foot0, base], [yb0, d["D"]])
        if y >= cover:
            return (y - yc) * k
        if y >= boss:                                           # cover dome takes the extra height
            return _pw(y, [boss, cover], [(boss - yc) * k - up, (cover - yc) * k])
        return (y - yc) * k - up
    if plug:                                                    # BDV2 left off: everything above the boss top
        ch = [(w, segs) for w, segs in ch if min(p[1] for sg in segs for p in sg[1:]) > boss - 0.05]
    if not flanged:
        A = d["A_sw"]
        fx = lambda x: (x - face_l) * k
        out = _map(ch, lambda p: (fx(p[0]), fy(p[1])))
        fl = None
    else:
        A = d["A_600"]
        fl = OD["ASME 600"][size]
        dash = [(w, segs) for w, segs, grey, ds in _chains(FTC80_PDF, 5, clip, dashed=True) if ds]
        rf_l, rf_r, fb_l, fb_r = 115.42, 356.91, 124.61, 347.73   # raised faces (ports) and flange backs
        R = (207.07 - 157.31) / 2
        kf = fl / 2 / R
        ycf = (157.31 + 207.36) / 2
        neck = (A - (face_r - face_l) * k) / 2                  # face of the flange to the body end
        tl = (fb_l - rf_l) * kf
        fx = lambda x: (_pw(x, [rf_l, fb_l, face_l], [0, tl, neck]) if x < face_l else
                        _pw(x, [face_r, fb_r, rf_r], [A - neck, A - tl, A]) if x > face_r else neck + (x - face_l) * k)
        fyd = lambda x, y: _fy_flange(y - ycf, 12.0, k, R, fl / 2) if (x <= fb_l + 0.05 or x >= fb_r - 0.05) else (y - ycf) * k
        out = _map(ch, lambda p: (fx(p[0]), fy(p[1]))) + _map(dash, lambda p: (fx(p[0]), fyd(*p)))
    if plug:
        Bp = d["B_plug"] - d["D"]                               # plug top above the centreline
        y0, y1 = (boss - yc) * k - up, -Bp
        xc = A / 2 + (((237.27 + 253.23) / 2) - (face_l + face_r) / 2) * k
        hw = 19 / 2
        lw = ch[0][0]
        out.append((lw, T.polyline([(xc - hw, y0), (xc - hw, y1), (xc + hw, y1), (xc + hw, y0)])))
        out.append((lw * 0.6, T.polyline([(xc - hw / 2, y0), (xc - hw / 2, y1)])))
        out.append((lw * 0.6, T.polyline([(xc + hw / 2, y0), (xc + hw / 2, y1)])))
    return out, A, fl


class Trap:
    def __init__(self, model, size, variant=None):
        dd = DATA[model]
        self.model, self.size, self.variant = model, size, variant or dd["variants"][0]
        t = dict(dd["sizes"][size])
        v = self.variant
        if model == "FT14":
            chains, L, fl = _ft14(t, v, size)
            self.d = {"A": L, "B": t["B_scr"] if v == "screwed" else t["B_fl"]}
        elif model == "FTC62":
            chains, L, fl = _ftc62(t, v, size)
            self.d = {"A": L, "F": t["F"]}
        else:
            chains, L, fl = _ftc80(t, v, size)
            self.d = {"A": L, "B": t["B_plug"] if v.endswith("plug") else t["B_bdv2"], "D": t["D"]}
        if fl:
            self.d["Flange OD"] = fl
        # mirror: the TIs draw flow right to left
        chains = [(w, [(sg[0],) + tuple((L - p[0], p[1]) for p in sg[1:]) for sg in segs]) for w, segs in chains]
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
