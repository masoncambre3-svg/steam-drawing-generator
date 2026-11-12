"""Baffle separators: S5 (TI-P023-11), S6 (TI-P023-12), S4A (TI-P139-02-US, TI-P139-03-US).

S5 / S6
    Traced from the TI outline drawing (front elevation, flanged, drain down). Both sheets carry the same
    drawing at different scales, so the S6 linework is moved into the S5 frame and the same landmarks serve
    both. The drawing is the 1/2" size. For each size:
      - caps, vent and drain plugs keep their drawn size (dimension D is 68 mm for every size)
      - the body is widened to H and stretched up and down so the plugs land on B and C
      - each nozzle is scaled with the pipe OD and stretched along the pipe to make up length A
      - flanges get their outside diameter from ASME B16.5 / EN 1092 (the TI does not list it)
      - screwed / SW / BW cut the nozzle off at the hub end, where the TI measures "A Scrd/SW/BW"

S4A
    Not traceable. On TI-P139-02-US (1/2" to 6") the drawings are raster pictures, and on TI-P139-03-US
    (8" to 18") the outline is drawn as filled shapes, not strokes, which collect() does not read.
    So S4A is redrawn by hand from the 8"-18" drawing's proportions with the helpers in ti_trace,
    with every size set from the TI table.
"""
import math
import numpy as np
import ti_trace as T
from sources import S5_PDF, S6_PDF

# pipe OD, mm (ASME B36.10)
POD = {'1/2"': 21.3, '3/4"': 26.7, '1"': 33.4, '1-1/4"': 42.2, '1-1/2"': 48.3, '2"': 60.3, '2-1/2"': 73.0,
       '3"': 88.9, '4"': 114.3, '6"': 168.3, '8"': 219.1, '10"': 273.1, '12"': 323.9, '14"': 355.6,
       '16"': 406.4, '18"': 457.0}
# flange outside diameter, mm: ASME B16.5 and EN 1092-1 PN40
FOD = {
    "ASME 150": {'1/2"': 89, '3/4"': 98, '1"': 108, '1-1/4"': 117, '1-1/2"': 127, '2"': 152, '2-1/2"': 178, '3"': 191,
                 '4"': 229, '6"': 279, '8"': 343, '10"': 406, '12"': 483, '14"': 533, '16"': 597, '18"': 635},
    "ASME 300": {'1/2"': 95, '3/4"': 117, '1"': 124, '1-1/4"': 133, '1-1/2"': 156, '2"': 165, '2-1/2"': 191, '3"': 210,
                 '4"': 254, '6"': 318, '8"': 381, '10"': 444, '12"': 521, '14"': 584, '16"': 648, '18"': 711},
    "ASME 600": {'2-1/2"': 191, '3"': 210, '4"': 273, '6"': 356, '8"': 419, '10"': 508, '12"': 559, '14"': 603,
                 '16"': 686, '18"': 743},
    "PN40": {'1/2"': 95, '3/4"': 105, '1"': 115, '1-1/4"': 140, '1-1/2"': 150, '2"': 165},
}
# flange thickness incl. raised face, mm (ASME B16.5, approximate) - S4A only
FTH = {
    "ASME 150": {'2-1/2"': 24, '3"': 26, '4"': 26, '6"': 27, '8"': 30, '10"': 32, '12"': 33, '14"': 37, '16"': 38, '18"': 41},
    "ASME 300": {'2-1/2"': 27, '3"': 30, '4"': 33, '6"': 38, '8"': 43, '10"': 49, '12"': 52, '14"': 56, '16"': 59, '18"': 62},
    "ASME 600": {'2-1/2"': 35, '3"': 38, '4"': 45, '6"': 54, '8"': 62, '10"': 70, '12"': 73, '14"': 76, '16"': 83, '18"': 89},
}

SZ6 = ['1/2"', '3/4"', '1"', '1-1/4"', '1-1/2"', '2"']
# TI-P023-11 / -12 (identical tables): A screwed/SW/BW, A flanged (PN40, ASME 150/300, JIS), B, C, H.  D = 68 all sizes.
_s56 = dict(zip(SZ6, [dict(As=130, Af=204, B=150, C=294, H=83), dict(As=130, Af=212, B=146, C=347, H=83),
                      dict(As=178, Af=260, B=170.5, C=386, H=130), dict(As=190, Af=277, B=195, C=440, H=144),
                      dict(As=220, Af=314, B=208, C=508, H=168), dict(As=214, Af=314, B=208, C=558, H=168)]))
V56 = ["screwed", "socket weld", "butt weld", "ASME 150", "ASME 300", "PN40"]
_N56 = ("Traced from the TI outline drawing. The TI has one drawing for every size: the body is set to width H, "
        "the plugs to B and C, and the nozzles to length A from the TI table. Flange diameter is ASME B16.5 / EN 1092 "
        "PN40, since the TI does not list it. Screwed, socket weld and butt weld are drawn the same, cut off at the hub "
        "end where the TI measures A Scrd/SW/BW. Third connection is the drain, fourth is the air vent. "
        "JIS/KS flanges and the PN16 column (blank on the TI) are not included.")

# S4A, TI-P139-02-US and -03-US. A, B, C, H in mm; G/F = inlet centreline to underside of the shoulder ring;
# E drain and F vent connection sizes.
_s4a_scr = {
    '1/2"': dict(A=229, B=132, C=269, H=63.5, E='3/4"', V='3/4"'),
    '3/4"': dict(A=236, B=150, C=307, H=63.5, E='3/4"', V='3/4"'),
    '1"': dict(A=300, B=152, C=358, H=101.6, E='3/4"', V='3/4"'),
    '1-1/4"': dict(A=338, B=180, C=414, H=127, E='3/4"', V='3/4"'),
    '1-1/2"': dict(A=391, B=193, C=483, H=152.4, E='1"', V='3/4"'),
    '2"': dict(A=404, B=206, C=523, H=152.4, E='1"', V='3/4"'),
}
_c = ("ASME 150", "ASME 300", "ASME 600")
def _fl(A, H, G, E, V, B, C):
    return {"A": A, "H": H, "G": G, "E": E, "V": V, "BC": {c: (b, cc) for c, b, cc in zip(_c, B, C)}}
_s4a_fl = {
    '2-1/2"': _fl(572, 221, 180, '1"', '3/4"', (239, 239, 251), (622, 622, 650)),
    '3"': _fl(643, 274, 201, '2"', '3/4"', (305, 305, 323), (726, 732, 759)),
    '4"': _fl(737, 325, 224, '2"', '1-1/2"', (320, 320, 335), (792, 792, 815)),
    '6"': _fl(909, 406, 290, '2"', '1-1/2"', (312, 315, 330), (932, 937, 960)),
    '8"': _fl(1064, None, 381, '2"', '2"', (389, 394, 399), (1222, 1227, 1240)),
    '10"': _fl(1237, None, 417, '2"', '2"', (686, 688, 696), (1605, 1613, 1628)),
    '12"': _fl(1257, None, 483, '2"', '2"', (757, 759, 770), (1727, 1735, 1750)),
    '14"': _fl(1392, None, 511, '2"', '2"', (782, 782, 790), (1831, 1834, 1849)),
    '16"': _fl(1499, None, 511, '2"', '2"', (833, 836, 851), (1971, 1979, 2007)),
    '18"': _fl(1707, None, 511, '2"', '2"', (894, 894, 922), (2131, 2134, 2189)),
}
# 8"-18": the TI gives no body diameter. Take it from the TI drawing's proportion of body width to overall
# height (79 pt / 191 pt on TI-P139-03-US p3). The 2-1/2"-6" table bodies sit at 0.36-0.44 of C, so this fits.
BODY_RATIO = 79.0 / 191.0
for _s, _r in _s4a_fl.items():
    if _r["H"] is None:
        _r["H"] = round(BODY_RATIO * _r["BC"]["ASME 150"][1])

DATA = {
    "S5": {"name": "S5", "type": "Baffle separator, carbon steel", "ti": "TI-P023-11", "variants": V56,
           "sizes": _s56, "src": "S5", "note": _N56},
    "S6": {"name": "S6", "type": "Baffle separator, stainless steel", "ti": "TI-P023-12", "variants": V56,
           "sizes": _s56, "src": "S6", "note": _N56},
    "S4A": {"name": 'S4A (1/2" to 2")', "type": "Baffle separator, fabricated steel, screwed / SW", "ti": "TI-P139-02-US",
            "variants": ["NPT", "socket weld"], "sizes": _s4a_scr,
            "note": "Redrawn by hand: the TI drawing is a raster picture. Overall size follows the TI table (A, B, C, "
                    "body diameter H). Head shape, end connection bosses, couplings and internals are drawn from the "
                    "TI picture's proportions. NPT and socket weld are drawn the same. Third connection is the drain, "
                    "fourth is the vent. For 2-1/2\" and up use S4A flanged."},
    "S4A-FL": {"name": 'S4A flanged (2-1/2" to 18")', "type": "Baffle separator, fabricated steel, flanged",
               "ti": "TI-P139-02-US / TI-P139-03-US", "variants": list(_c), "sizes": _s4a_fl,
               "note": "Redrawn by hand: the 2-1/2\" to 6\" TI drawing is a raster picture and the 8\" to 18\" one is "
                       "drawn as filled shapes the kit cannot trace. A, B, C and the shoulder ring height (G / F) "
                       "follow the TI table. Body diameter H is from the TI for 2-1/2\" to 6\". For 8\" to 18\" the TI "
                       "gives no body diameter, so it is assumed from the TI drawing's proportions (0.41 x C): "
                       "8\" 505, 10\" 664, 12\" 714, 14\" 757, 16\" 815, 18\" 881 mm. Flange diameter and "
                       "thickness are ASME B16.5 (approximate thickness). The TI prints the 6\" ANSI 600 B as "
                       "3.0 in; the 330 mm value is used. Third connection is the drain, fourth is the vent."},
}

# ---------------------------------------------------------------- S5 / S6: traced
# landmarks on TI-P023-11 page 3, PDF points
XF0, XF1, XC, CL = 203.1, 390.6, 296.85, 222.55        # flange faces, body centre, inlet centreline
WL, WR = 258.8, 334.9                                   # body walls
HL, HR = 238.6, 355.1                                   # hub ends (A screwed/SW/BW)
YN = [87.8, 110.5, 124.0, 200.8, CL, 244.2, 328.0, 340.0, 362.8]   # vent top, cap/shoulder, shoulder/straight,
                                                                   # bulge top, CL, bulge bottom, ..., drain bottom
S0 = 204.0 / (XF1 - XF0)                                # mm per point, the 1/2" flanged size
DROP5 = [(258.2, 89, 259.2, 121), (237.9, 211, 239.0, 362), (355.5, 211, 356.1, 234), (202.6, 266.5, 203.4, 362),
         (265.2, 348.8, 266.0, 362), (247.0, 98.0, 276.0, 99.6), (255.0, 353.0, 276.0, 354.6)]
# S6 (TI-P023-12 page 4) is the same drawing: faces 81.6 / 240.8, centreline 209.15, centre 161.2
K6, O6 = (XF1 - XF0) / (240.8 - 81.6), (161.2, 209.15)
DROP6 = [(117.0, 101.0, 144.5, 102.3), (124.0, 319.0, 145.0, 320.3)]   # cap leaders "5" and "3", S6 page points
_ch = {}


def _chains(src):
    if src not in _ch:
        if src == "S5":
            th, _ = T.collect(S5_PDF, 3, (200, 85, 395, 372), outline_lw=0.45, drop=DROP5)
            _ch[src] = [segs for _, segs in th]
        else:
            to6 = lambda p: ((p[0] - XC) / K6 + O6[0], (p[1] - CL) / K6 + O6[1])
            clip = to6((200, 85)) + to6((395, 372))
            drop = [to6(b[:2]) + to6(b[2:]) for b in DROP5] + DROP6
            th, _ = T.collect(S6_PDF, 4, clip, outline_lw=0.45, drop=drop)
            to5 = lambda p: ((p[0] - O6[0]) * K6 + XC, (p[1] - O6[1]) * K6 + CL)
            _ch[src] = [[(sg[0],) + tuple(to5(p) for p in sg[1:]) for sg in segs] for _, segs in th]
    return _ch[src]


class S56:
    def __init__(self, model, size, variant):
        d = DATA[model]["sizes"][size]
        fl = variant.startswith(("ASME", "PN"))
        A = d["Af"] if fl else d["As"]
        B, C, H = d["B"], d["C"], d["H"]
        kn = POD[size] / POD['1/2"']                       # nozzle scale
        fs = FOD[variant][size] / ((266.8 - 178.2) * S0) if fl else 1
        xf = XF0 if fl else HL
        kxn = (A / 2 - H / 2) / (WL - xf)                  # mm per point along the nozzle
        top = -(C - B)
        t = [top, top + (YN[1] - YN[0]) * S0, top + (YN[2] - YN[0]) * S0,
             (YN[3] - CL) * S0 * kn, 0.0, (YN[5] - CL) * S0 * kn,
             B - (YN[8] - YN[6]) * S0, B - (YN[8] - YN[7]) * S0, B]

        def ymap(y):
            return float(np.interp(y, YN, t, left=t[0] + (y - YN[0]) * S0, right=t[-1] + (y - YN[-1]) * S0))

        def fx(p):
            x, y = p
            if y <= YN[1] or y >= YN[7]:                   # caps and plugs: drawn size, slid to B and C
                return (A / 2 + (x - XC) * S0, ymap(y))
            nozzle = (x < WL - 0.05 or x > WR + 0.05) or (YN[3] - 0.5 <= y <= YN[5] + 0.5 and (x < 265.5 or x > 328.2))
            if nozzle and (190 < y < 255 or x < 218.0 or x > 375.7):     # flange corners reach past the band
                left = x < XC
                dx = (x - xf) if left else (2 * XC - xf) - x   # distance from this end's face
                X = dx * kxn if left else A - dx * kxn
                flange = (x < 218.0 or x > 375.7) and abs(y - CL) > 30
                return (X, (y - CL) * S0 * (fs if flange else kn))
            return (A / 2 + (x - XC) / ((WR - WL) / 2) * H / 2, ymap(y))

        segs_all = []
        for segs in _chains(DATA[model]["src"]):
            P = np.array([p for sg in segs for p in sg[1:]])
            if not fl and (P[:, 0].min() < HL - 0.3 or P[:, 0].max() > HR + 0.3):
                continue
            segs_all.append([(sg[0],) + tuple(fx(p) for p in sg[1:]) for sg in segs])
        if not fl:                                         # close the hub ends
            for x in (HL, HR):
                segs_all.append(T.polyline([fx((x, 212.4)), fx((x, 232.7))]))
        lw = max(0.6, 0.0035 * C)
        self._finish(segs_all, lw, A, B, C)
        self.arrow = (A / 2, 0.0, 0.42 * H, "r", lw * 0.55)
        self.d = dict(A=A, B=B, C=C, D=68, H=H)
        self.k = S0

    def _finish(self, segs_all, lw, A, B, C):
        thick = [(lw, s) for s in segs_all]
        P = np.array([p for _, segs in thick for sg in segs for p in sg[1:]])
        mg = 6 + 0.03 * C
        clip = (P[:, 0].min() - mg, P[:, 1].min() - mg, P[:, 0].max() + mg, P[:, 1].max() + mg)
        px = min(10.0, 3600 / max(clip[2] - clip[0], clip[3] - clip[1]))
        g = T.assemble(thick, [], clip, px=px, close=max(2, int(round(0.004 * C * px))))
        self.fill = [[tuple(p) for p in poly] for poly in g["fill"]]
        self.strokes = [(w, [[sg[0]] + [tuple(p) for p in sg[1:]] for sg in segs]) for w, segs in g["outline"]]
        m = lw / 2
        F = np.array([p for poly in self.fill for p in poly])
        self.x0, self.y0 = min(F[:, 0].min(), P[:, 0].min()) - m, min(F[:, 1].min(), P[:, 1].min()) - m
        self.x1, self.y1 = max(F[:, 0].max(), P[:, 0].max()) + m, max(F[:, 1].max(), P[:, 1].max()) + m
        self.w, self.h = self.x1 - self.x0, self.y1 - self.y0
        self.ports = {"in": (0.0, 0.0), "out": (A, 0.0), "drain": (A / 2, B), "vent": (A / 2, -(C - B))}
        self.drain_angle = 90.0


# ---------------------------------------------------------------- S4A: drawn by hand
def _rect(x0, y0, x1, y1):
    return T.polyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], closed=True)


def _qell(cx, cy, rx, ry, a0, a1):
    """Quarter ellipse from angle a0 to a1 (degrees, y down) as one cubic."""
    k = 0.5522847498
    p = lambda a: (cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a)))
    d = lambda a: (-rx * math.sin(math.radians(a)), ry * math.cos(math.radians(a)))
    s = 1 if a1 > a0 else -1
    P0, P3, D0, D3 = p(a0), p(a1), d(a0), d(a1)
    return ("c", P0, (P0[0] + s * k * D0[0], P0[1] + s * k * D0[1]), (P3[0] - s * k * D3[0], P3[1] - s * k * D3[1]), P3)


class S4A(S56):
    def __init__(self, model, size, variant):
        d = DATA[model]["sizes"][size]
        flg = model == "S4A-FL"
        A, H = d["A"], d["H"]
        B, C = d["BC"][variant] if flg else (d["B"], d["C"])
        cx, R, od = A / 2, H / 2, POD[size]
        tw = max(1.5, 0.035 * H)                           # wall
        hh = 0.3 * H                                       # head depth
        wcd, wcv = 1.25 * POD[d["E"]] + 6, 1.25 * POD[d["V"]] + 6
        hcd, hcv = 0.7 * wcd, 0.7 * wcv                    # couplings
        top = -(C - B)
        yt = top + hcv * 0.8 + hh                          # top seam
        yb = B - hcd * 0.8 - hh                            # bottom seam
        S = []
        # shell
        S.append([("l", (cx - R, yt), (cx - R, yb)), _qell(cx, yb, R, hh, 180, 90), _qell(cx, yb, R, hh, 90, 0),
                  ("l", (cx + R, yb), (cx + R, yt)), _qell(cx, yt, R, hh, 0, -90), _qell(cx, yt, R, hh, -90, -180)])
        S.append(T.polyline([(cx - R, yt), (cx + R, yt)]))
        S.append(T.polyline([(cx - R, yb), (cx + R, yb)]))
        # couplings, with the socket line
        S.append(_rect(cx - wcv / 2, top, cx + wcv / 2, top + hcv))
        S.append(T.polyline([(cx - wcv / 2, top + 0.45 * hcv), (cx + wcv / 2, top + 0.45 * hcv)]))
        S.append(_rect(cx - wcd / 2, B - hcd, cx + wcd / 2, B))
        S.append(T.polyline([(cx - wcd / 2, B - 0.45 * hcd), (cx + wcd / 2, B - 0.45 * hcd)]))
        # end connections
        r = od / 2
        if flg:
            Df = FOD[variant][size]; tf = FTH[variant][size]
            rf = 1.6 if variant != "ASME 600" else 6.4
            rrf = 0.5 * (od + 0.45 * (Df - od))            # raised face radius
            rh = r + 0.12 * (Df - od) / 2 + 3              # hub root radius
            lh = 0.35 * od + 25                            # hub length
            for sg in (1, -1):
                x0 = 0 if sg == 1 else A
                X = lambda v: x0 + sg * v
                S.append(_rect(X(0), -rrf, X(rf), rrf))
                S.append(_rect(X(rf), -Df / 2, X(tf), Df / 2))
                S.append(T.polyline([(X(tf), -rh), (X(tf + lh), -r), (cx - sg * R, -r)]))
                S.append(T.polyline([(X(tf), rh), (X(tf + lh), r), (cx - sg * R, r)]))
                S.append(T.polyline([(X(tf + lh), -r), (X(tf + lh), r)]))
        else:
            rs = r + 0.3 * od + 4                          # socket boss
            ls = 0.7 * od + 18
            for sg in (1, -1):
                x0 = 0 if sg == 1 else A
                X = lambda v: x0 + sg * v
                S.append(_rect(X(0), -rs, X(ls), rs))
                S.append(T.polyline([(X(ls), -r), (cx - sg * R, -r)]))
                S.append(T.polyline([(X(ls), r), (cx - sg * R, r)]))
        # inner wall lines, broken at the nozzles
        for sg in (1, -1):
            xi = cx + sg * (R - tw)
            S.append(T.polyline([(xi, yt), (xi, -r)]))
            S.append(T.polyline([(xi, r), (xi, yb)]))
        # shoulder ring (flanged sizes)
        if flg:
            G = d["G"]; lh_, wl = 0.24 * H, 0.15 * H
            for sg in (1, -1):
                xw = cx + sg * R
                S.append(T.polyline([(xw, -G - lh_), (xw + sg * wl, -G - 0.06 * H), (xw + sg * wl, -G), (xw, -G)]))
        # internals: inlet pipe, outlet funnel, baffle plate with tabs
        xi0 = cx - R + tw
        S.append(T.polyline([(xi0, -r), (cx - 0.4 * R, -r), (cx - 0.4 * R, r), (xi0, r)]))
        xo0 = cx + R - tw
        S.append(T.polyline([(xo0, -r), (cx + 0.45 * R, -r), (cx + 0.84 * R, r), (xo0, r)]))
        pt, pb = max(yt + 0.1 * R, -1.55 * R), yb + 0.25 * R
        S.append(_rect(cx + 0.19 * R, pt, cx + 0.28 * R, pb))
        for a, b in ((-1.55, -1.3), (-1.18, -0.97), (-0.85, -0.62)):
            if a * R > pt:
                S.append(_rect(cx - 0.05 * R, a * R, cx + 0.19 * R, b * R))
        S.append(_rect(cx + 0.13 * R, -0.47 * R, cx + 0.19 * R, 0.47 * R))

        lw = max(0.6, 0.0035 * C)
        self._finish(S, lw, A, B, C)
        ay = min(0.8 * R, (r + yb) / 2)
        self.arrow = (cx - 0.38 * R, ay, 0.5 * R, "r", lw * 0.55)
        self.d = dict(A=A, B=B, C=C, H=H) if not (flg and size in ('8"', '10"', '12"', '14"', '16"', '18"')) else dict(A=A, B=B, C=C)
        if flg:
            self.d["G" if size in ('2-1/2"', '3"', '4"', '6"') else "F"] = d["G"]
        self.k = 1.0


def Separator(model, size, variant=None):
    variant = variant or DATA[model]["variants"][0]
    return (S4A if model.startswith("S4A") else S56)(model, size, variant)
