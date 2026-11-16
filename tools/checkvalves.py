"""Check valves and the sight check, traced from their TI sheets.

Every model has one outline on its TI sheet for all sizes. Each size is set from the TI table:
the length along the pipe, the overall height and any part with its own dimension.
Wafer and sanitary valves are drawn on their TI sheets with the flow running up the page;
they are turned so the flow runs along x like every other pack.
"""
import numpy as np
import ti_trace as T

from sources import SIGHT_PDF, SDCV44_PDF, LCV_PDF, DCV41_PDF, DCV10_PDF, CVS10_PDF

IN = 25.4
B165_150 = {'1/2"': 3.5, '3/4"': 3.88, '1"': 4.25, '1-1/2"': 5.0, '2"': 6.0, '2-1/2"': 7.0, '3"': 7.5, '4"': 9.0}
B165_300 = {'1/2"': 3.75, '3/4"': 4.62, '1"': 4.88, '1-1/2"': 6.12, '2"': 6.5, '2-1/2"': 7.5, '3"': 8.25, '4"': 10.0}
EN1092 = {'1/2"': 95, '3/4"': 105, '1"': 115, '1-1/4"': 140, '1-1/2"': 150, '2"': 165, '2-1/2"': 185, '3"': 200}


def _tab(sizes, **cols):
    return {s: {k: v[i] for k, v in cols.items()} for i, s in enumerate(sizes)}


LCV_TYPE = "Lift check valve: LCV3 cast iron, LCV4 carbon steel, LCV6 stainless, LCV7 SG iron"
FLS = ['1/2"', '3/4"', '1"', '1-1/2"', '2"', '2-1/2"', '3"', '4"']
PNS = ['1/2"', '3/4"', '1"', '1-1/4"', '1-1/2"', '2"', '2-1/2"', '3"', '4"']
SCS = ['1/2"', '3/4"', '1"', '1-1/4"', '1-1/2"', '2"']

DATA = {
    "SIGHTCHECK": {
        "name": "Sight Check", "type": "Combined sight glass and check valve, bronze", "ti": "TI-P022-01",
        "variants": ["NPT", "BSP"],
        "sizes": _tab(['1/2"', '3/4"', '1"'], A=[76, 76, 89], B=[95, 95, 108], C=[44, 44, 54], D=[38, 38, 38], E=[64, 64, 64]),
        "note": "A, B and D are set from the TI table. The TI drawing is not to scale: with the cap at the TI width C the "
                "sight tube would run down into the body, so the tube and cap are scaled as one piece to fit B, and the cap "
                "comes out narrower than C (about 36 mm against 44 mm at 1/2\", 41 mm against 54 mm at 1\"). "
                "E (64 mm) is the clearance needed to pull the sight tube out, along the tube; it is not drawn."},
    "DCV41": {
        "name": "DCV41", "type": "Disc check valve, austenitic stainless steel", "ti": "TI-P601-18",
        "variants": ["screwed", "socket weld"],
        "sizes": _tab(['1/2"', '3/4"', '1"', '1-1/4"', '1-1/2"', '2"'],
                      A_screwed=[51, 57, 68, 100, 100, 100], A_sw=[50, 55, 67, 100, 100, 100], B=[34, 41, 50, 80, 80, 80]),
        "note": "Length A (screwed or socket weld) and the hex across flats B are set from the TI table. 1-1/4\" to 2\" share "
                "one body on the TI. The TI dimension drawing does not mark the flow direction; the arrow assumes left to "
                "right. Mirror (M) turns it round."},
    "CVS10": {
        "name": "CVS10", "type": "Sanitary check valve, metal seat, clamp ends", "ti": "TI-P029-21",
        "variants": ["ASME clamp", "DIN clamp"],
        "sizes": _tab(['1/2"', '3/4"', '1"', '1-1/2"', '2"'], A=[40, 40, 25, 30, 35],
                      B_ASME=[25.0, 25.0, 50.39, 50.39, 63.91], B_DIN=[34.0, 34.0, 50.5, 50.5, 64.0]),
        "note": "The TI drawing shows the valve with the flow running up the page; it is turned to run along the pipe here. "
                "Length A and clamp diameter B are from the TI table (A is the same for ASME and DIN clamps; the TI only "
                "lists it once). The TI gives 1\" as shorter than 1/2\" (25 mm against 40 mm); that is drawn as listed. "
                "The clamp lips keep their drawn shape and the body between them stretches to A. "
                "The TI does not mark the flow direction; the arrow assumes left to right."},
    "DCV10": {
        "name": "DCV10", "type": "Wafer disc check valve, stainless, close coupled to a pump", "ti": "TI-P601-32-US",
        "variants": ["ASME 150 / 300"],
        "sizes": {'1-1/2"': dict(A=3.7*IN, B=3.4*IN, C=1.8*IN, D_open=1.9*IN, D_closed=1.8*IN, E=1.6*IN, F=1.9*IN)},
        "note": "Side elevation from the TI, turned so the flow runs along the pipe (the TI draws it flowing up). Face to face "
                "is C and the body diameter is B. The raised boss on the outlet face stands about 0.1\" proud (D open). "
                "Fits between ASME 150 or 300 flanges; the flanges are not part of the valve. The PN25 version has no "
                "dimensions on this US sheet and is not drawn."},
    "SDCV44": {
        "name": "SDCV44", "type": "Split disc check valve, wafer, austenitic stainless steel", "ti": "TI-P154-10-US",
        "variants": ["ASME 150 / 300"],
        "sizes": {'2"': dict(A=104.1, B=55.9, C=43.2, D=69), '3"': dict(A=134.6, B=73.7, C=66, D=94),
                  '4"': dict(A=180, B=76, C=89, D=121)},
        "note": "Half section from the TI, turned so the flow runs along the pipe (the TI draws it flowing up). Face to face "
                "B, body OD A, bore C on the inlet side and recess D on the outlet side are all from the TI table. Hinge pin "
                "and retainer plug are kept round. Fits between ASME 150 or 300 flanges; the flanges are not part of the valve."},
    "LCV": {
        "name": "LCV screwed / SW", "type": LCV_TYPE, "ti": "TI-P029-16",
        "variants": ["NPT", "socket weld", "BSP"],
        "sizes": {s: {"A_NPT_SW": a, "B_NPT_SW": b, "A_BSP": a2, "B_BSP": b2} for s, a, b, a2, b2 in zip(
            SCS, [165, 165, 197, 216, 235, 267], [102, 102, 102, 132, 132, 132],
            [130, 155, 160, 185, 205, 230], [88, 88, 88, 117, 117, 117])},
        "note": "Length A and the height B (pipe centreline to the top of the cover bolts) are from the TI table for the "
                "connection picked. The body depth below the pipe is not on the TI; it scales with A. Not every body "
                "material comes with every connection: check the TI sizes table."},
    "LCV-FL": {
        "name": "LCV ASME flanged", "type": LCV_TYPE, "ti": "TI-P029-16",
        "variants": ["ASME 125", "ASME 150", "ASME 250", "ASME 300"],
        "sizes": {s: {"A_125": a1, "A_150": a2, "A_250_300": a3, "B": b} for s, a1, a2, a3, b in zip(
            FLS, [184, 184, 184, 222, 254, 267, 298, 349], [184, 184, 184, 222, 254, 276, 298, 352],
            [191, 191, 197, 235, 267, 292, 318, 368], [102, 102, 102, 132, 132, 200, 200, 216])},
        "note": "Face to face A and height B (pipe centreline to the top of the cover bolts) are from the TI table. Flange "
                "diameter is ASME B16.5 (Class 150 / 300; B16.1 Class 125 / 250 cast iron flanges have the same "
                "diameters), since the TI does not list it. 1-1/4\" is not offered with ASME flanges. The body depth below "
                "the pipe is not on the TI; it scales with A."},
    "LCV-PN": {
        "name": "LCV PN flanged", "type": LCV_TYPE, "ti": "TI-P029-16",
        "variants": ["PN16", "PN25", "PN40"],
        "sizes": {s: {"A": a, "B": b} for s, a, b in zip(
            PNS, [130, 150, 160, 180, 200, 230, 290, 310, 350], [88, 88, 88, 117, 117, 117, 166, 166, 180])},
        "note": "Face to face A and height B are from the TI table (sizes are DN15 to DN100). Flange diameter is EN 1092-1, "
                "since the TI does not list it. JIS / KS flanges share these lengths but are not drawn. The body depth "
                "below the pipe is not on the TI; it scales with A."},
}

_cache = {}


def _chains(key, pdf, page, clip, lw, drop=()):
    if key not in _cache:
        _cache[key], _ = T.collect(pdf, page, clip, outline_lw=lw, drop=drop)
    return _cache[key]


def _bb(segs):
    P = np.vstack([T.flat(sg) for sg in segs])
    return P[:, 0].min(), P[:, 1].min(), P[:, 0].max(), P[:, 1].max()


def _map(chains, f):
    """f(point, chain bbox) -> new point"""
    out = []
    for _, segs in chains:
        bb = _bb(segs)
        out.append([(sg[0],) + tuple(f(p, bb) for p in sg[1:]) for sg in segs])
    return out


# ---------------------------------------------------------------- one mapper per model: returns (chains in mm, ports, arrow)
def _sight(d):
    A, B, D = d["A"], d["B"], d["D"]
    ch = _chains("sight", SIGHT_PDF, 4, (238, 113, 406, 285), 0.9)
    xl, xr, cl, top, right, btop = 241.66, 348.18, 259.56, 116.54, 400.86, 239.53
    neck = btop - 223.46                                   # drawn gap from the body top up to the tube's lower flange
    s = A / (xr - xl)
    kc = (B - (cl - btop + neck) * s) / (223.46 - top)     # tube and cap as one piece, sized to fit B
    d["C as drawn"] = round(55.65 * kc, 1)

    def f(p, bb):
        x, y = p
        if y >= 236.0:
            return ((x - xl) * s, (y - cl) * s)
        return (A + D + (x - right) * kc, -B + (y - top) * kc)
    arrow = (A * 0.6, 0.0, A * 0.3, "r")
    return _map(ch, f), {"in": (0, 0), "out": (A, 0)}, arrow


def _dcv41(d, v):
    A, B = d["A_screwed" if v == "screwed" else "A_sw"], d["B"]
    ch = _chains("dcv41", DCV41_PDF, 4, (159, 89, 311, 189), 0.3, drop=((150, 85, 215, 90.2), (150, 187, 215, 191)))
    xl, xr, yt, yb = 161.89, 308.14, 90.37, 186.51
    cl = (yt + yb) / 2
    sx, sy = A / (xr - xl), B / (yb - yt)
    f = lambda p, bb: ((p[0] - xl) * sx, (p[1] - cl) * sy)
    return _map(ch, f), {"in": (0, 0), "out": (A, 0)}, ((228.5 - xl) * sx, 0.0, A * 0.22, "r")


def _cvs10(d, v):
    A, B = d["A"], d["B_ASME" if v.startswith("ASME") else "B_DIN"]
    ch = _chains("cvs", CVS10_PDF, 3, (229, 417, 369, 503), 0.3)
    y0, y1, xc = 416.58, 495.53, (231.93 + 365.44) / 2
    kB = B / (365.44 - 231.93)
    lip = 16.0                                             # clamp lip, kept to its drawn shape
    km = (A - 2 * lip * kB) / (y1 - y0 - 2 * lip)

    def f(p, bb):
        x, y = p
        t = y - y0
        if t <= lip:
            X = t * kB
        elif y1 - y <= lip:
            X = A - (y1 - y) * kB
        else:
            X = lip * kB + (t - lip) * km
        return (X, -(x - xc) * kB)
    return _map(ch, f), {"in": (0, 0), "out": (A, 0)}, (A / 2, 0.0, min(A * 0.45, B * 0.5), "r")


def _dcv10(d):
    C, B = d["C"], d["B"]
    ch = _chains("dcv10", DCV10_PDF, 2, (361, 125, 503, 183.5), 0.3)
    yin, yout, xl, xr = 181.06, 129.34, 364.28, 501.52
    xc, ky, kx = (xl + xr) / 2, C / (yin - yout), B / (xr - xl)
    f = lambda p, bb: ((yin - p[1]) * ky, (p[0] - xc) * kx)
    return _map(ch, f), {"in": (0, 0), "out": (C, 0)}, None     # the TI drawing carries its own flow arrow


def _sdcv44(d):
    A, B, C, D = d["A"], d["B"], d["C"], d["D"]
    ch = _chains("sdcv", SDCV44_PDF, 2, (332, 623, 533, 706), 0.3)
    yin, yout, xl, xr = 704.13, 624.72, 334.09, 530.24
    xc, kB = (xl + xr) / 2, B / (yin - yout)
    R = [0, 98.04 / 2, (495.53 - 368.75) / 2, (xr - xl) / 2]     # drawn radii: 0, bore C, recess D, body A
    M = [0, C / 2, D / 2, A / 2]
    rad = lambda r: np.sign(r) * np.interp(abs(r), R, M)
    kc = M[1] / R[1]
    k = min(kB, kc)

    def f(p, bb):
        x, y = p
        if bb[0] > 414 and bb[2] < 451 and bb[1] > 636 and bb[3] < 684 and abs((bb[2]-bb[0]) - (bb[3]-bb[1])) < 2:
            cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2   # hinge pin, retainer plug: stay round
            return ((yin - cy) * kB - (y - cy) * k, rad(cx - xc) + (x - cx) * k)
        return ((yin - y) * kB, rad(x - xc))
    return _map(ch, f), {"in": (0, 0), "out": (B, 0)}, (B * 0.7, M[2] * 0.55, B * 0.34, "r")


def _lcv_screwed(A, B):
    ch = _chains("lcvs", LCV_PDF, 10, (66, 100, 270, 273), 0.3)
    xl, xr, cl, top, yn = 68.88, 267.81, 209.05, 102.53, 178.37      # yn: top of the port block
    s = A / (xr - xl)
    su = (B - (cl - yn) * s) / (yn - top)

    def f(p, bb):
        x, y = p
        Y = (y - cl) * s if y >= yn else -(cl - yn) * s - (yn - y) * su
        return ((x - xl) * s, Y)
    return _map(ch, f), {"in": (0, 0), "out": (A, 0)}, (A * 0.5, (254 - cl) * s, A * 0.16, "r")


def _lcv_flanged(A, B, OD):
    ch = _chains("lcvf", LCV_PDF, 10, (326, 100, 535, 273), 0.3)
    xl, xr, cl, top, yn, R = 327.25, 526.29, 198.67, 103.01, 165.0, (270.0 - 127.33) / 2
    s = A / (xr - xl)
    su = (B - (cl - yn) * s) / (yn - top)
    kf = OD / 2 / R

    def f(p, bb):
        x, y = p
        if bb[2] <= 347.2 or bb[0] >= 506.5:                        # flange and raised face
            Y = (y - cl) * kf
        else:
            Y = (y - cl) * s if y >= yn else -(cl - yn) * s - (yn - y) * su
        return ((x - xl) * s, Y)
    return _map(ch, f), {"in": (0, 0), "out": (A, 0)}, (A * 0.5, (251 - cl) * s, A * 0.13, "r")


class Valve:
    def __init__(self, model, size, variant=None):
        dd = DATA[model]
        self.model, self.size, self.variant = model, size, variant or dd["variants"][0]
        self.d = dict(dd["sizes"][size])
        v = self.variant
        if model == "SIGHTCHECK":
            chains, ports, arrow = _sight(self.d)
        elif model == "DCV41":
            chains, ports, arrow = _dcv41(self.d, v)
        elif model == "CVS10":
            chains, ports, arrow = _cvs10(self.d, v)
        elif model == "DCV10":
            chains, ports, arrow = _dcv10(self.d)
        elif model == "SDCV44":
            chains, ports, arrow = _sdcv44(self.d)
        elif model == "LCV":
            k = "NPT_SW" if v in ("NPT", "socket weld") else "BSP"
            chains, ports, arrow = _lcv_screwed(self.d["A_" + k], self.d["B_" + k])
        elif model == "LCV-FL":
            A = self.d["A_125"] if v == "ASME 125" else self.d["A_150"] if v == "ASME 150" else self.d["A_250_300"]
            OD = (B165_150 if v in ("ASME 125", "ASME 150") else B165_300)[size] * IN
            chains, ports, arrow = _lcv_flanged(A, self.d["B"], OD)
            self.d["Flange OD"] = round(OD, 1)
        elif model == "LCV-PN":
            OD = 220 if (size == '4"' and v == "PN16") else 235 if size == '4"' else EN1092[size]
            chains, ports, arrow = _lcv_flanged(self.d["A"], self.d["B"], OD)
            self.d["Flange OD"] = OD
        dd_ = self.d
        if model == "DCV41":
            self.d = {"A": dd_["A_screwed" if v == "screwed" else "A_sw"], "B": dd_["B"]}
        elif model == "CVS10":
            self.d = {"A": dd_["A"], "B": dd_["B_ASME" if v.startswith("ASME") else "B_DIN"]}
        elif model == "LCV":
            self.d = {"A": dd_["A_" + k], "B": dd_["B_" + k]}
        elif model == "LCV-FL":
            self.d = {"A": A, "B": dd_["B"], "Flange OD": dd_["Flange OD"]}
        P = np.array([p for segs in chains for sg in segs for p in sg[1:]])
        span = max(P[:, 0].max() - P[:, 0].min(), P[:, 1].max() - P[:, 1].min())
        lw = max(0.5, 0.0075 * span)
        thick = [(lw, segs) for segs in chains]
        mg = 6 + 0.03 * span
        c2 = (P[:, 0].min() - mg, P[:, 1].min() - mg, P[:, 0].max() + mg, P[:, 1].max() + mg)
        g = T.assemble(thick, [], c2, px=min(10.0, 3600 / max(c2[2] - c2[0], c2[3] - c2[1])))
        self.fill = [[tuple(p) for p in poly] for poly in g["fill"]]
        self.strokes = [(w, [[sg[0]] + [tuple(p) for p in sg[1:]] for sg in segs]) for w, segs in g["outline"]]
        m = lw / 2
        F = np.array([p for poly in self.fill for p in poly])
        self.x0, self.y0 = min(F[:, 0].min(), P[:, 0].min()) - m, min(F[:, 1].min(), P[:, 1].min()) - m
        self.x1, self.y1 = max(F[:, 0].max(), P[:, 0].max()) + m, max(F[:, 1].max(), P[:, 1].max()) + m
        self.w, self.h = self.x1 - self.x0, self.y1 - self.y0
        self.ports = ports
        self.lw = lw
        self.arrow = arrow + (lw * 0.55,) if arrow else None
