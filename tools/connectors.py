"""Pipeline connectors and trapping stations: the body a universal (two bolt) trap unit bolts onto.

STS17.2 (TI-P128-22), front elevations on pages 7 to 10, pipe left to right, isolation valve levers up.
    One pack per type: SB (single isolation), DB US (double isolation upstream), DBB USH (double block and bleed
    upstream horizontal), DBB USH DSH (the same downstream as well). Sizes 1/2", 3/4", 1"; connections BSPT / NPT
    and SW, whose lengths differ in the table.
    The TI tables give overall sizes, which the drawings' own arrows do not always point at:
      A  end face to end face
      B  pipe centreline to the lowest point (strainer cap on SB / DB, bleed valve on DBB)
      C  pipe centreline to the top of the levers (93 for every size)
      D  lever length (90), not used for scaling
    The drawings are to scale (C, B and A agree to about 1%). Scale k is set from C. The screwed end pieces at the
    two pipe ends stretch to make A exactly, and on DBB the bleed valve's bottom end stretches to make B. Levers,
    nuts and everything else move with the body unchanged.
    Not done: ASME 150 / 300 and PN40 flanged versions (the TI draws screwed ends only), and the two vertical types
    DBB USV and DBB USV DSH (pages 11 and 12), whose A in the table is the overall length over the levers of the
    vertical valves, not the end faces the drawing points at, and whose inlet is on a vertical end.
    The trap unit bolts to the connector face, which faces out of the page in this view, so there is no
    connection point for it.

PC4000 / PC4001 / PC40 (TI-P128-33), the "horizontal application" side view on page 7 (pipe end on), PC4001 drawn;
    PC4000 drops the bypass valve, PC40 both valves. See PC_NOTE.
"""
import numpy as np
import ti_trace as T
from universal import _chains, _bb, _mapped, _pw, _finish
from sources import STS17_PDF, PC4000_PDF, PC90_PDF, UPC_PDF

_SZ = ('1/2"', '3/4"', '1"')
_VAR = ["BSPT / NPT", "SW"]


def _tab(a, b):
    """a, b: {size: (screwed, SW)} -> {size: {variant: value}}"""
    return {s: dict(zip(_VAR, a[s])) for s in _SZ}, {s: dict(zip(_VAR, b[s])) for s in _SZ}


STS_NOTE = ("Front elevation as the TI draws it: pipe left to right, isolation valve levers up, strainer below. "
            "A (end face to end face) and B (pipe centreline to the lowest point) are from the TI table for the size "
            "and connection; the screwed end pieces stretch to make A{bleed}. C 93 and lever length D 90 are the "
            "same for every size. The TI draws screwed ends only, so SW looks the same. The trap unit bolts to the "
            "connector face, which faces out of the page in this view, so there is no connection point for it. "
            "Flanged versions (ASME 150 / 300, PN40) are not drawn yet.")

# landmarks (pt): page, clip, drops, end faces xL / xR, inner ends of the screwed end pieces xLi / xRi,
# centreline yc, top of the levers ytop, half height of the end pieces hb; DBB: bleed valves (x from, x to),
# bleed end piece top yBi and bleed bottom yB.
STSV = {
    "SB": dict(page=7, clip=(215, 118, 384, 239), drop=[(222.5, 197.5, 223.0, 236.5)],
               xL=222.73, xLi=230.46, xRi=364.79, xR=372.49, yc=185.55, ytop=122.25, hb=12),
    "DBUS": dict(page=8, clip=(172, 118, 420, 240), drop=[],
                 xL=176.82, xLi=185.97, xRi=409.51, xR=418.66, yc=186.09, ytop=123.23, hb=14.5),
    "DBBUSH": dict(page=9, clip=(170, 118, 418, 267), drop=[(262.0, 236.0, 324.3, 236.6)],
                   xL=174.90, xLi=184.06, xRi=407.59, xR=416.74, yc=185.19, ytop=122.33, hb=14.5,
                   bleed=[(222.0, 265.0)], yBi=249.51, yB=265.06),
    "DBBUSHDSH": dict(page=10, clip=(130, 120, 464, 272), drop=[(220.5, 239.9, 282.6, 240.2)],
                      xL=133.19, xLi=142.34, xRi=452.44, xR=461.60, yc=188.94, ytop=126.08, hb=14.5,
                      bleed=[(180.0, 223.5), (371.0, 414.5)], yBi=253.26, yB=268.81),
}

DATA = {}
for _id, _name, _ti, _a, _b, _typ in (
        ("SB", "STS17.2 SB", 7, {'1/2"': (222, 222), '3/4"': (222, 213), '1"': (229, 269)},
         {s: (76, 76) for s in _SZ}, "Trapping station, single isolation"),
        ("DBUS", "STS17.2 DB US", 8, {'1/2"': (350, 350), '3/4"': (350, 341), '1"': (357, 397)},
         {s: (76, 76) for s in _SZ}, "Trapping station, double isolation upstream"),
        ("DBBUSH", "STS17.2 DBB USH", 9, {'1/2"': (351, 351), '3/4"': (351, 342), '1"': (358, 398)},
         {'1/2"': (118, 118), '3/4"': (118, 118), '1"': (118, 138)}, "Trapping station, double block and bleed upstream"),
        ("DBBUSHDSH", "STS17.2 DBB USH DSH", 10, {'1/2"': (479, 479), '3/4"': (479, 470), '1"': (486, 526)},
         {'1/2"': (118, 118), '3/4"': (118, 118), '1"': (118, 138)},
         "Trapping station, double block and bleed up and downstream")):
    A, B = _tab(_a, _b)
    DATA["STS17-" + _id] = {
        "name": _name, "type": _typ, "ti": "TI-P128-22", "view": _id,
        "sizes": {s: {v: dict(A=A[s][v], B=B[s][v], C=93, D=90) for v in _VAR} for s in _SZ},
        "variants": list(_VAR), "variantLabel": "Connection",
        "note": STS_NOTE.format(bleed=" and the bleed valve's bottom end stretches to make B" if "DBB" in _id else ""),
    }


def _sts(self):
    V = STSV[self.dd["view"]]
    A, B, C = self.d["A"], self.d["B"], self.d["C"]
    lw = 0.5
    ch = _chains(STS17_PDF, V["page"], V["clip"], drop=V["drop"], max_lw=1.0)
    xL, xLi, xRi, xR, yc = V["xL"], V["xLi"], V["xRi"], V["xR"], V["yc"]
    k = (C - lw / 2) / (yc - V["ytop"])
    core = (xRi - xLi) * k
    e = (A - core) / 2                                   # each screwed end piece
    assert e > 3, (self.model, self.size, self.variant, e)
    xsrc, xdst = [xL, xLi, xRi, xR], [lw / 2, e, e + core, A - lw / 2]
    body = lambda x: e + (x - xLi) * k
    yflat = lambda y: (y - yc) * k
    if "bleed" not in V:                                 # SB / DB: below the centreline, scale to B (strainer cap)
        ylow = max(_bb(segs)[3] for _, segs, _, _ in ch)
        yflat = lambda y: (y - yc) * (k if y <= yc else (B - lw / 2) / (ylow - yc))
    ysrc = ydst = None
    if "bleed" in V:
        yBi, yB = V["yBi"], V["yB"]
        ysrc, ydst = [yc, yBi, yB], [0.0, (yBi - yc) * k, B - lw / 2]
        assert ydst[2] > ydst[1]
    parts = []
    for _, segs, _, _ in ch:
        x0, y0, x1, y1 = _bb(segs)
        in_band = y0 >= yc - V["hb"] and y1 <= yc + V["hb"]
        fx = (lambda x: _pw(x, xsrc, xdst)) if in_band else body
        fy = yflat
        if ysrc and y1 > V["yBi"] + 0.3 and any(a <= x0 and x1 <= b for a, b in V["bleed"]):
            fy = lambda y: _pw(y, ysrc, ydst)
        parts.append(_mapped(segs, lambda p, fx=fx, fy=fy: (fx(p[0]), fy(p[1]))))
    _finish(self, parts, lw, {"in": (0.0, 0.0), "out": (float(A), 0.0)}, k, px=10)


PC_NOTE = ("Side view (the TI's 'horizontal application' drawing): the pipe runs into the page, so in and out are the "
           "same point, at the centre of the inlet. The trap unit bolts to the connector face on the left; that is the "
           "third connection point, on the pipe centreline. Body height A 72 with the pipe centreline at B 36 from "
           "the bottom, bypass valve 45 above the body and depressurisation valve 34 below it (both closed), as the "
           "TI gives them; the valves are stretched slightly to hit those. Handwheel closed. The TI draws the PC4001; "
           "PC4000 is the same without the bypass valve, and PC40 is drawn here as the same body without either "
           "valve (its own TI drawing is a part view). Both sizes have the same dimensions.")
DATA["PC4000"] = {
    "name": "PC4000 / PC4001 / PC40", "type": "Pipeline connector, two piston isolation valves", "ti": "TI-P128-33",
    "tracer": "pc", "sizes": {'1/2"': {}, '3/4"': {}}, "variants": ["PC4000", "PC4001", "PC40"], "variantLabel": "Model",
    "note": PC_NOTE,
}


def _pc(self):
    """TI-P128-33 p7, horizontal application view of the PC4001."""
    A, B, BY, DP = 72, 36, 45, 34
    self.d = dict(A=A, B=B)
    if self.variant == "PC4001":
        self.d["Bypass valve above body (closed)"] = BY
    if self.variant != "PC40":
        self.d["Depressurisation valve below body (closed)"] = DP
    lw = 0.5
    ch = _chains(PC4000_PDF, 7, (99, 120, 221, 266), drop=[(99.5, 197.3, 101.0, 197.8)], max_lw=1.0)
    xc, yc, top, bot, bytop, dpbot, face = 122.07, 197.55, 162.82, 231.30, 122.55, 265.37, 99.88
    k = (A - lw) / (bot - top)
    ysrc = [bytop, top, yc, bot, dpbot]
    ydst = [-(A - B) - BY + lw / 2, -(A - B) + lw / 2, 0.0, B - lw / 2, B + DP - lw / 2]
    f = lambda p: ((p[0] - xc) * k, _pw(p[1], ysrc, ydst))
    parts = []
    for _, segs, grey, _ in ch:
        x0, y0, x1, y1 = _bb(segs)
        if grey < 0.05 and x0 > 104 and x1 < 140 and y0 > 164 and y1 < 192:
            continue                                     # black strokes the TI hides under the white body (a copy of the bypass valve)
        if y1 < 162.0 and x1 < 152 and self.variant != "PC4001":
            continue                                     # bypass valve
        if y0 >= 231.0 and x1 < 132 and self.variant == "PC40":
            continue                                     # depressurisation valve
        parts.append(_mapped(segs, f))
    xf = (face - xc) * k - lw / 2
    _finish(self, parts, lw, {"in": (0.0, 0.0), "out": (0.0, 0.0), "trap": (xf, 0.0)}, k)


# ---------------------------------------------------------------- PC90 4-bolt connector (TI-P806-01), added 2026-11-16
# Front view (p5, left): the trap face looks out of the page, flow right to left as the TI arrow shows, so the inlet is
# the right end and the outlet is A to the left (out at x = -A). The app turns it round when it is dropped on a pipe.
# The drawing is to scale (A and B agree to 0.5%). Blank cap and blowdown (BD) adaptor are the same drawing; the BD
# adaptor version is 2 mm shorter (B), made by the vertical scale below the centreline.
# Flanged (Class 600 / 900) ends are not drawn on the TI: weld neck flanges are added to the SW body from ASME B16.5
# (OD, thickness, hub, raised face), with a short pipe stub to make face to face A. B in the TI table is exactly the
# flange radius plus 77 for every size, which confirms the B16.5 diameters.
# Side view (p5, right): pipe end on, in and out the same point; the trap face is the third connection, on the right,
# where USM90 and UTDS90 (drawn face on the left) bolt on. Flanges show as a circle behind the body.
PIPE_OD = {'1/2"': 21.3, '3/4"': 26.7, '1"': 33.4}
WN = {  # ASME B16.5 weld neck: OD, thickness, hub diameter X, length through hub Y, raised face diameter
    "Class 600": {'1/2"': (95.3, 14.3, 38.1, 52.4, 34.9), '3/4"': (117.5, 15.9, 47.6, 57.2, 42.9), '1"': (124.0, 17.5, 54.0, 61.9, 50.8)},
    "Class 900": {'1/2"': (120.7, 22.3, 38.1, 60.3, 34.9), '3/4"': (130.2, 25.4, 44.5, 69.9, 42.9), '1"': (149.4, 28.6, 52.4, 73.0, 50.8)},
}
RF_H = 6.4
R_BOSS = (132.97 - 100.72) * 108 / (306.16 - 186.07)       # end boss radius on the front view, mm (29.0)
PC90_A = {'1/2"': {"SW": 108, "Class 600": 260, "Class 900": 260}, '3/4"': {"SW": 108, "BW": 107, "Class 600": 238, "Class 900": 264},
          '1"': {"SW": 108, "BW": 107, "Class 600": 248, "Class 900": 270}}
PC90_B = {"blank cap": {'1/2"': {"SW": 106, "Class 600": 124.5, "Class 900": 137.5}, '3/4"': {"SW": 106, "BW": 106, "Class 600": 135.5, "Class 900": 142},
                        '1"': {"SW": 106, "BW": 106, "Class 600": 139, "Class 900": 151.5}},
          "BD adaptor": {'1/2"': {"SW": 104, "Class 600": 122.5, "Class 900": 135.5}, '3/4"': {"SW": 104, "BW": 104, "Class 600": 133.5, "Class 900": 140},
                         '1"': {"SW": 104, "BW": 104, "Class 600": 137, "Class 900": 149.5}}}
_PCV = ["SW, blank cap", "SW, BD adaptor", "Class 600, blank cap", "Class 600, BD adaptor", "Class 900, blank cap",
        "Class 900, BD adaptor"]
_PC90N = ("Front view, the trap bolts to the face looking out of the page. The TI draws the flow right to left; it is "
          "mirrored here to match the STS17.2 and universal connectors, inlet on the left and flow left to right (the cast "
          "arrow points right). Dropped on a pipe it turns to suit. The third connection point is the centre of the four connector bolts (54 from the "
          "inlet, about 5.5 below the pipe centreline), where USM90 (front view) snaps on. Face to face A and B "
          "(top of the end boss, or of the flange, to the bottom of the cap) are from the TI table. The BD adaptor is "
          "drawn as the blank cap, 2 mm shorter as the table gives it. The four connector bolts the TI draws below the "
          "cap (withdrawal distance D 85) are not drawn. ")


PC90_BOLTS = (246.13, 139.08)    # p5 front view: centre of the four connector bolt holes (holes 49.55 pt apart = 44.6 mm)


def _pc90_body(B, cap_k=None):
    """Front view body (SW), mm, inlet face (right end) at x 0; returns parts, k, boss radius."""
    ch = _chains(PC90_PDF, 5, (180, 95, 310, 222), drop=[(180, 216.5, 310, 222.5)], max_lw=1.0)
    xl, xr, yc, top, bot = 186.07, 306.16, 132.97, 100.72, 218.21
    k = 108 / (xr - xl)                                   # SW face to face sets the scale
    r = (yc - top) * k
    kd = (B - r) / (bot - yc)
    f = lambda p: ((p[0] - xr) * k, (p[1] - yc) * (k if p[1] < yc else kd))
    _pc90_body.trap = f(PC90_BOLTS)                       # centre of the four connector bolts, for the trap's port
    return [_mapped(segs, f) for _, segs, grey, _ in ch if grey < 0.9], k, r


def _wn(x_end, x_face, d, nps, side):
    """Weld neck flange from the body end x_end out to the raised face x_face (side +1 right, -1 left), mm."""
    od, t, X, Y, rfd = d
    po = PIPE_OD[nps] / 2
    xf = x_face
    xr_ = xf - side * RF_H                                # flange front (behind the raised face)
    xb = xr_ - side * t                                    # flange back
    hub = max(0.0, min(Y - t, abs(xb - x_end)))
    xh = xb - side * hub
    out = [T.polyline([(xf, -rfd / 2), (xr_, -rfd / 2), (xr_, rfd / 2), (xf, rfd / 2)], closed=True),
           T.polyline([(xr_, -od / 2), (xb, -od / 2), (xb, od / 2), (xr_, od / 2)], closed=True),
           T.polyline([(xb, -X / 2), (xh, -po), (xh, po), (xb, X / 2)])]
    if abs(xh - x_end) > 0.05:
        out.append(T.polyline([(xh, -po), (x_end, -po)]))
        out.append(T.polyline([(xh, po), (x_end, po)]))
    return out


def _pc90(self):
    conn, cap = self.variant.split(", ")
    nps = self.size
    A, B = PC90_A[nps][conn], PC90_B[cap][nps][conn]
    if conn in ("SW", "BW"):
        parts, k, r = _pc90_body(B)
        trap = _pc90_body.trap
        if conn == "BW":                                   # BW is 1 mm shorter than SW
            parts = [_mapped(p, lambda q: (q[0] * A / 108, q[1])) for p in parts]
            trap = (trap[0] * A / 108, trap[1])
        self.d = {"A": A, "B": B}
    else:
        d = WN[conn][nps]
        parts, k, r = _pc90_body(B - (d[0] / 2 - R_BOSS))     # B is over the flange: body B is over the boss
        e = (A - 108) / 2
        parts = [_mapped(p, lambda q: (q[0] - e, q[1])) for p in parts]
        trap = (_pc90_body.trap[0] - e, _pc90_body.trap[1])
        parts += _wn(-e, 0.0, d, nps, +1) + _wn(-e - 108, -A, d, nps, -1)
        self.d = {"A": A, "B": B, "Flange OD (ASME B16.5)": d[0]}
    lw = 0.6
    # turned to match STS17.2 and the universal connectors: inlet on the left, flow left to right (mirror of the TI view)
    parts = [_mapped(p, lambda q: (-q[0], q[1])) for p in parts]
    # third connection point: the centre of the four connector bolts, where USM90's front view snaps on
    _finish(self, parts, lw, {"in": (0.0, 0.0), "out": (float(A), 0.0), "trap": (round(-trap[0], 2), round(trap[1], 2))}, k)


def _pc90side(self):
    conn, cap = self.variant.split(", ")
    nps = self.size
    key = "SW" if conn == "SW / BW" else conn
    B = PC90_B[cap][nps][key]
    ch = _chains(PC90_PDF, 5, (365, 95, 440, 222), max_lw=1.0)
    xc, yc, top, bot = 403.48, 132.97, 100.72, 218.27
    k = 108 / (306.16 - 186.07)
    r = (yc - top) * k
    od = WN[key][nps][0] if key in WN else 0.0
    Bsw = B - (od / 2 - r) if od else B                  # body bottom below the boss top, as for SW
    kd = (Bsw - r) / (bot - yc)
    f = lambda p: ((p[0] - xc) * k, (p[1] - yc) * (k if p[1] < yc else kd))
    parts = [_mapped(segs, f) for _, segs, grey, _ in ch if grey < 0.9]
    hidden = []
    hw, yb, cw = (431.84 - 375.12) / 2 * k, (202.71 - yc) * kd, (421.83 - 385.13) / 2 * k
    if od:
        R = od / 2
        th = np.linspace(0, 2 * np.pi, 721)
        P = np.c_[R * np.cos(th), R * np.sin(th)]
        behind = (P[:, 1] > -r) & (((np.abs(P[:, 0]) < hw) & (P[:, 1] < yb)) | ((np.abs(P[:, 0]) < cw) & (P[:, 1] < Bsw - r)))
        behind |= np.hypot(P[:, 0], P[:, 1]) < r                       # (never: the flange is bigger than the boss)
        vis = ~behind
        run = []
        for p, v in zip(P, vis):
            if v:
                run.append(tuple(p))
            elif len(run) > 1:
                parts.append(T.polyline(run)); run = []
            else:
                run = []
        if len(run) > 1:
            parts.append(T.polyline(run))
        hidden.append(T.circle(0, 0, R))
        self.d = {"B": B, "C": 51, "Flange OD (ASME B16.5)": od}
    else:
        self.d = {"B": B, "C": 51}
    xf = (435.72 - xc) * k
    lw = 0.6
    _finish(self, parts, lw, {"in": (0.0, 0.0), "out": (0.0, 0.0), "trap": (round(xf, 2), 0.0)}, k, hidden=hidden)


DATA["PC90"] = {
    "name": "PC90", "type": "4-bolt pipeline connector, front view", "ti": "TI-P806-01", "tracer": "pc90",
    "sizes": {s: {} for s in _SZ}, "variants": _PCV, "variantLabel": "Connection",
    "note": _PC90N + "Class 600 and 900 flanges are not drawn on the TI: they are weld neck flanges from ASME B16.5 "
            "(diameter, thickness, hub, 1/4\" raised face) on a short pipe stub, to make the table's A. Butt weld "
            "(3/4\" and 1\" only) is the PC90 BW pack.",
}
DATA["PC90-BW"] = {
    "name": "PC90 BW", "type": "4-bolt pipeline connector, butt weld, front view", "ti": "TI-P806-01", "tracer": "pc90",
    "sizes": {s: {} for s in ('3/4"', '1"')}, "variants": ["BW, blank cap", "BW, BD adaptor"], "variantLabel": "Connection",
    "note": _PC90N + "Butt weld ends are drawn as the SW body (the TI draws SW), A 107 instead of 108. There is no 1/2\" BW.",
}
# PC90-SIDE (side view, pipe end on, trap face as a third port) was removed 2026-11-16 at Mason's request; _pc90side
# above still builds it if it is wanted again (add the DATA entry back and put the ID in catalog.json).


# ---------------------------------------------------------------- Universal pipeline connectors, US (TI-P127-03-US)
# Page 3 front views. Strainer connector: right hand (flow left to right) and left hand (right to left), with the 3/8"
# NPT plug or the blowdown valve on the strainer. Straight connector: front view with the trap mounting ears.
# The drawings are to scale for 1/2" (A, B and C agree to 1%). Each size: the scale k is set from B; the end blocks
# (the body between the end face and the start of the middle) stretch to make A; the strainer leg, the lug and the
# ears keep their shape. Under the end blocks the stretch fades out over a few mm, so the lug and the strainer leg
# stay joined to the body.
UPC_V = {
    "Right hand, plug": dict(clip=(255, 80, 306.5, 141.5), drop=[], leader=(294, 127, 304, 136), flow=1, m=(271.55, 289.13), band=(86.07, 104.41)),
    "Right hand, blowdown valve": dict(clip=(353, 76, 404, 158.5), drop=[], flow=1, m=(369.37, 387.05), band=(84.71, 103.15)),
    "Left hand, plug": dict(clip=(252, 196, 306, 259), drop=[], leader=(270.5, 252, 307, 258.5), flow=-1, m=(269.5, 287.22), band=(203.98, 222.46)),
    "Left hand, blowdown valve": dict(clip=(350, 194, 405, 276), drop=[], flow=-1, m=(368.07, 385.9), band=(202.71, 221.2)),
}
UPC_STR = dict(clip=(322, 496, 365, 543), drop=[(321, 495, 325, 500.5), (361, 495, 366, 500.5)], m=(328.5, 359.0))
IN = 25.4


def _upc_map(ch, A, Bv, V, straight=False):
    """Map one view: returns parts (mm, origin at the inlet face, x with the flow), k, extents."""
    small = lambda c: max(_bb(c[1])[2] - _bb(c[1])[0], _bb(c[1])[3] - _bb(c[1])[1]) <= 0.25
    big = [c for c in ch if not small(c)]
    ends = np.array([p for c in big for p in (c[1][0][1], c[1][-1][-1])])
    near = lambda c: (np.hypot(*(ends - c[1][0][1]).T) < 0.6).any()
    ch = big + [c for c in ch if small(c) and near(c)]           # specks on their own (stray dots) out
    P = np.vstack([T.flat(sg) for _, segs, _, _ in big for sg in segs])
    if straight:
        top, bot = P[:, 1].min(), P[:, 1].max()
        yc = (top + bot) / 2
        band = (yc - 9, yc + 9)
        k = Bv / (bot - top)
    else:
        band = V["band"]
        yc = sum(band) / 2
        bot = P[:, 1].max()
        k = Bv / (bot - yc)
    if straight:                                        # each end face is one segment (y 510.19 to 527.94): only its two
        inb = P[(P[:, 1] >= band[0]) & (P[:, 1] <= band[1])]            # end points exist, so keep the band's edges
    else:
        inb = P[(P[:, 1] > band[0] + 0.5) & (P[:, 1] < band[1] - 1.5)]  # end faces only, not the lugs below them
    xl, xr = inb[:, 0].min(), inb[:, 0].max()
    m0, m1 = V["m"]
    cm = (m0 + m1) / 2
    Xm = lambda x: A / 2 + (x - (xl + xr) / 2) * k     # middle, centred
    def Xpw(x):
        if x < m0:
            return _pw(x, [xl, m0], [0.0, Xm(m0)])
        if x > m1:
            return _pw(x, [m1, xr], [Xm(m1), A])
        return Xm(x)
    fade = 4.0                                          # pt below / above the end blocks over which the stretch fades
    def f(p):
        x, y = p
        X = Xpw(x)
        dy = max(band[0] - y, y - band[1], 0.0)
        if dy > 0 and (x < m0 or x > m1):
            w = max(0.0, 1 - dy / fade)
            X = w * X + (1 - w) * Xm(x)
        return X, (y - yc) * k
    parts = [_mapped(segs, f) for _, segs, grey, _ in ch if grey < 0.9]
    return parts, k, (xl, xr, yc)


def _upc(self):
    V = UPC_V[self.variant]
    A = self.d["A"]
    bdv = "blowdown" in self.variant
    Bv, Cv = (self.d["B_bdv"], self.d["C_bdv"]) if bdv else (self.d["B_plug"], self.d["C_plug"])
    ch = _chains(UPC_PDF, 3, V["clip"], drop=V["drop"], max_lw=1.0)
    if "leader" in V:                                  # the "Plug" leader: one long straight line; the plug's own short
        L = V["leader"]                                # edges inside the same box stay
        inside = lambda bb: bb[0] >= L[0] and bb[2] <= L[2] and bb[1] >= L[1] and bb[3] <= L[3]
        ch = [c for c in ch if not (inside(_bb(c[1])) and _bb(c[1])[2] - _bb(c[1])[0] > 4.5)]
    parts, k, _ = _upc_map(ch, A, Bv, V)
    if V["flow"] < 0:                                  # left hand: inlet is the right end, outlet A to the left
        parts = [_mapped(p, lambda q: (q[0] - A, q[1])) for p in parts]
        ports = {"in": (0.0, 0.0), "out": (-float(A), 0.0)}
    else:
        ports = {"in": (0.0, 0.0), "out": (float(A), 0.0)}
    Q = np.vstack([T.flat(sg) for p in parts for sg in p])
    c_drawn = (Q[:, 0].max() if V["flow"] > 0 else -Q[:, 0].min())
    self.d = {"A": A, "B": Bv, "C": Cv, "E": 20}
    lw = 0.5
    _finish(self, parts, lw, ports, k, close=10)
    # C on the TI runs from the inlet face to the far side of the plug / valve end; report what the drawing gives
    F_ = np.array([p for poly in self.fill for p in poly])
    lo = F_[F_[:, 1] > F_[:, 1].max() - 6.0][:, 0]                # the bottom 6 mm: plug end or valve end
    self.d["C as drawn"] = round(float(lo.max() if V["flow"] > 0 else -lo.min()), 1)


def _upcs(self):
    A, Bv = self.d["A"], self.d["B"]
    ch = _chains(UPC_PDF, 3, UPC_STR["clip"], drop=UPC_STR["drop"], max_lw=1.0)
    parts, k, _ = _upc_map(ch, A, Bv, UPC_STR, straight=True)
    _finish(self, parts, 0.5, {"in": (0.0, 0.0), "out": (float(A), 0.0)}, k, close=10)


_UPCN = ("Front view as the TI draws it, the trap face looking out of the page. NPT and SW connectors have the same "
         "outline. The drawings are to scale for 1/2\"; for the other sizes the scale is set from B and the end blocks "
         "stretch to make A, so the strainer, lug and mounting ears keep their shape. ")
DATA["UPC-STR"] = {
    "name": "Universal strainer connector", "type": "Universal pipeline connector with strainer (US)", "ti": "TI-P127-03-US",
    "tracer": "upc",
    "sizes": {s: dict(A=a, B_plug=bp, C_plug=cp, B_bdv=bb, C_bdv=cb) for s, a, bp, cp, bb, cb in zip(
        _SZ, [81, 89, 99], [79, 81, 86], [66, 71, 76], [112, 114, 117], [79, 84, 89])},
    "variants": list(UPC_V), "variantLabel": "Model",
    "note": _UPCN + "Right hand: flow left to right; left hand: flow right to left, so the inlet is the right end (the "
            "app turns it round when it is dropped on a pipe). A, B (pipe centreline to the bottom of the plug or "
            "blowdown valve) are set from the TI table; C (inlet face to the far side of the strainer end) is checked, "
            "not set. Screen withdrawal E (20) and the trap dimensions D, F, G are not drawn. The trap is not drawn: "
            "it bolts to the face that looks out of the page.",
}
DATA["UPC-ST"] = {
    "name": "Universal straight connector", "type": "Universal pipeline connector, straight (US)", "ti": "TI-P127-03-US",
    "tracer": "upcs", "sizes": {s: dict(A=a, B=69) for s, a in zip(_SZ, [61, 71, 89])},
    "variants": ["NPT", "SW"], "variantLabel": "Connection",
    "note": _UPCN + "Face to face A and the height over the mounting ears B (69, every size) are from the TI table. The "
            "TI does not mark a flow direction; in is on the left. The trap is not drawn: it bolts to the face that "
            "looks out of the page.",
}


class Connector:
    def __init__(self, model, size, variant=None):
        d = DATA[model]
        self.model, self.size, self.variant = model, size, variant or d["variants"][0]
        self.dd = d
        sz = d["sizes"][size]
        self.d = dict(sz[self.variant] if self.variant in sz else sz)
        TRACERS[d.get("tracer", "sts")](self)


TRACERS = {"sts": _sts, "pc": _pc, "pc90": _pc90, "pc90side": _pc90side, "upc": _upc, "upcs": _upcs}
