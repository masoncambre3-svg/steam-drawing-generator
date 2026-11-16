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
from sources import STS17_PDF, PC4000_PDF

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


class Connector:
    def __init__(self, model, size, variant=None):
        d = DATA[model]
        self.model, self.size, self.variant = model, size, variant or d["variants"][0]
        self.dd = d
        sz = d["sizes"][size]
        self.d = dict(sz[self.variant] if self.variant in sz else sz)
        TRACERS[d.get("tracer", "sts")](self)


TRACERS = {"sts": _sts, "pc": _pc}
