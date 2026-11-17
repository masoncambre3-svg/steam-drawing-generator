"""Universal (swivel connector) steam traps, sealed trap units that bolt onto a pipeline connector.

UFT32 (TI-P146-05): the pack is now the front view from Spirax CAD (_uft32cad, 2026-11-17). The side view below is Universal._side.
    Traced from the side elevation on page 4. The TI dimensions only the trap unit, not the connector:
      A 168.5  dome end to connector face
      B 94     body diameter
      C 47     connector centreline to underside of the body
    x is scaled to A, y to B (the drawing's flange ring is used for B), which puts the connector
    centreline at C from the bottom. The one connection is the connector face, on its centreline.
    Every pressure rating (UFT32-4.5 to -32) has the same outline.
"""
import json
from pathlib import Path

import numpy as np, pymupdf
import ti_trace as T
from sources import UFT32_PDF, UFT14HC_PDF, UBP32_PDF, UTDS46M_PDF, UIB45_PDF, UIB30_PDF, UTD52L_PDF, USM90_PDF, UTDS90_PDF

UFT_RATINGS = ["4.5", "10", "14", "21", "32"]
DATA = {
    "UFT32": {
        "name": "UFT32", "type": "Ball float, sealed stainless, for pipeline connectors, front view", "ti": "TI-P146-05",
        "sizes": {f"UFT32-{r}": dict(A=168.5, B=94, C=47) for r in UFT_RATINGS},
        "variants": ["-"], "sizeLabel": "Model",
        "note": "Front view from Spirax's 2D CAD of the UFT32-4.5 (front DWG, visible edges only), 1:1: the trap seen "
                "face on, body B 94 round, the two connector bolts above and below the spigot. The one connection "
                "point is the centre of the two bolts (= spigot centre), so it snaps onto a connector's trap point "
                "(PC4000: drawn behind the connector). Bolts 50.8 apart on the CAD (PC4000 CAD 50.5). Every rating "
                "has the same outline, so all use the 4.5 CAD; pick the rating for the label only. The side view "
                "(TI-P146-05 p4, connection at the connector face) is no longer in the pack; Universal._side still "
                "builds it.",
    },
}
_ch = {}


class Universal:
    def __init__(self, model, size, variant=None):
        d = DATA[model]
        self.model, self.size, self.variant = model, size, variant or d["variants"][0]
        self.d = dict(d["sizes"][size])
        if model in TRACERS:
            TRACERS[model](self)
            return
        self._side()

    def _side(self):
        """UFT32 side view from TI-P146-05 p4 (the pack's view until 2026-11-17; kept for reference)."""
        model = self.model
        A, B = self.d["A"], self.d["B"]
        if model not in _ch:
            th, _ = T.collect(UFT32_PDF, 4, (272, 80, 404, 160), outline_lw=0.9)
            _ch[model] = th
        th = _ch[model]
        lw = 0.9                                          # mm, close to the TI's 1 pt line at this size
        xa, xb, ya, yb = 275.85, 399.70, 85.08, 155.93    # stroke centrelines of the outer extents, pt
        sx, sy = (A - lw) / (xb - xa), (B - lw) / (yb - ya)
        C = self.d["C"]
        fx = lambda p: ((p[0] - xb) * sx - lw / 2, (p[1] - yb) * sy + C - lw / 2)
        thick = [(lw, [(sg[0],) + tuple(fx(p) for p in sg[1:]) for sg in segs]) for _, segs in th]
        P = np.array([p for _, segs in thick for sg in segs for p in sg[1:]])
        mg = 6
        c2 = (P[:, 0].min() - mg, P[:, 1].min() - mg, P[:, 0].max() + mg, P[:, 1].max() + mg)
        g = T.assemble(thick, [], c2, px=20)
        self.fill = [[tuple(p) for p in poly] for poly in g["fill"]]
        self.strokes = [(w, [[sg[0]] + [tuple(p) for p in sg[1:]] for sg in segs]) for w, segs in g["outline"]]
        m = lw / 2
        self.x0, self.y0 = P[:, 0].min() - m, P[:, 1].min() - m
        self.x1, self.y1 = P[:, 0].max() + m, P[:, 1].max() + m
        self.w, self.h = self.x1 - self.x0, self.y1 - self.y0
        self.ports = {"in": (0.0, 0.0)}
        self.arrow = None
        self.k = sx


# ---------------------------------------------------------------- trap units added 2026-11-16
# UFT14HC, UBP32, UTDS46M: trap unit only, like UFT32. The connection point is the connector face (where the TI
# dimensions start), on the connector centreline, and the trap runs +x from it as the TI draws it.
# UIB45, UIB30, UIB30H: the TI dimension drawing is the trap on a PC10HP connector, so the front view (pipe left to
# right, bucket hanging down) is traced with the connector: in and out are the connector ends, A apart.
N_UNIT = ("Trap unit only, as dimensioned on the TI. The pipeline connector (PC10, PC10HP, PC20, PC3_, PC4_) is not "
          "drawn. The connection point is the connector face, on the connector centreline. ")
DATA["UFT14HC"] = {
    "name": "UFT14HC", "type": "Ball float, sealed stainless, for pipeline connectors, front view", "ti": "TI-P712-01",
    "sizes": {f"UFT14HC-{r}": dict(A=205, B=110, C=153, D=67, E=50.8) for r in ("4.5", "10", "14")},
    "variants": ["-"], "sizeLabel": "Model", "source": "Spirax 2D CAD (UFT14HC-4.5 front DWG), 1:1",
    "note": "Front view from Spirax's 2D CAD of the UFT14HC-4.5 (front DWG, visible edges only), 1:1: the trap seen "
            "from the connector side, flange D 67 round about the spigot, body collar 111 round and set 24.85 above "
            "the spigot (the body axis is above the connector centreline), the two connector bolts above and below "
            "the spigot, 50.8 apart (E). The one connection point is the bolt centre (= spigot centre), so it snaps "
            "onto a connector's trap point. Every rating has the same outline, so all use the 4.5 CAD; pick the "
            "rating for the label only. The TI side view (_uft14hc, connection at the spigot face) is no longer in "
            "the pack.",
}
DATA["UBP32"] = {
    "name": "UBP32", "type": "Balanced pressure, sealed stainless, for pipeline connectors", "ti": "TI-P127-01",
    "sizes": {"UBP32": dict(A=35, B=33, C=68, D=42.5)}, "variants": ["-"], "sizeLabel": "Model",
    "note": "Front view: the trap as seen from the front of its connector, the TI's round view. The plate (C 68) is "
            "behind, the capsule housing (D 42.5, drawn 42.6) in front, and the two connector screws level with the "
            "plate centre, 50.7 apart. The connection point is the centre of the two screws, which matches the trap "
            "point on the universal straight and strainer connectors: drag it onto the connector and it snaps there. "
            "On the straight connector the screws run up and down, so turn the trap 90 degrees; on the strainer "
            "connector they run at about 55 degrees, which the app's 90 degree turns cannot match. The side view "
            "(A, B) is not drawn.",
}
DATA["UTDS46M"] = {
    "name": "UTDS46M", "type": "Thermodynamic with strainer, for pipeline connectors, front view", "ti": "TI-P187-03",
    "sizes": {"UTDS46M": {}}, "variants": ["-"], "sizeLabel": "Model",
    "source": "Spirax 2D CAD (UTDS46M connector 1200 front DWG), 1:1",
    "note": "Front view from Spirax's 2D CAD of the UTDS46M (front DWG, visible edges only), 1:1: the trap seen from "
            "the connector side, flange D 67 round about the spigot, the two connector bolts above and below it, 50.8 "
            "apart, and the cap (63 round, top 55.8 above the spigot centreline) standing up behind. The one "
            "connection point is the bolt centre (= spigot centre), so it snaps onto a connector's trap point. The "
            "TI side view (_utds46m, connection at the spigot face) is no longer in the pack.",
}
DATA["UTDS46M-BDV2"] = {
    "name": "UTDS46M BDV2", "type": "Thermodynamic with strainer and blowdown valve, for pipeline connectors, front view",
    "ti": "TI-P187-03", "sizes": {"UTDS46M BDV2": {}}, "variants": ["-"], "sizeLabel": "Model",
    "source": "Spirax 2D CAD (UTDS46M with BDV2, connector 1251 front DWG), 1:1",
    "note": "Front view from Spirax's 2D CAD of the UTDS46M with BDV2 blowdown valve (front DWG, visible edges only), "
            "1:1. Same trap, flange and bolts as the UTDS46M; the BDV2 on the strainer cap shows below the flange, its "
            "outlet end 44.45 below the spigot centreline. One connection point at the bolt centre (= spigot centre), "
            "so it snaps onto a connector's trap point. The blowdown outlet is not a connection point.",
}
_UIBN = ("Front view on a PC10HP connector, as the TI draws it: pipe left to right, connections at the connector "
         "ends, A apart. The TI views are not to scale, so the connector (A, and D from the top of the connector "
         "to the pipe centreline) and the trap (bucket diameter E, overall height C) are set separately; the "
         "bucket keeps its drawn shape and only its straight side stretches to hit C.")
DATA["UIB45"] = {
    "name": "UIB45", "type": "Inverted bucket, sealed, on PC10HP connector", "ti": "TI-P113-03",
    "sizes": {'1/2"': dict(A=61.5, B=89, C=170, D=33.5, E=90), '3/4"': dict(A=73.5, B=87, C=170, D=33.5, E=90),
              '1"': dict(A=90, B=90, C=170, D=33.5, E=90)},
    "variants": ["PC10HP"], "variantLabel": "Connector",
    "note": _UIBN + " The PC10HP is drawn because the TI dimensions include it; A is the PC10HP face to face.",
}
for _m, _c, _cp in (("UIB30", 124.5, 158), ("UIB30H", 159, 192)):
    DATA[_m] = {
        "name": _m, "type": "Inverted bucket, sealed, on PC10HP connector", "ti": "TI-P113-01",
        "sizes": {'1/2"': dict(A=61.5, B=88, C=_c, Cp=_cp, D=33.5, E=83), '3/4"': dict(A=73.5, B=86, C=_c, Cp=_cp, D=33.5, E=83),
                  '1"': dict(A=90, B=89, C=_c, Cp=_cp, D=33.5, E=83)},
        "variants": ["Plain cover", "Drain plug"], "variantLabel": "Cover",
        "note": _UIBN + " The PC10HP is drawn dashed on the TI; here it is solid. Drain plug: C to the bottom of the "
                "plug and plug width F 32 from the TI; the 20 mm plug withdrawal distance is not drawn.",
    }


def _pw(v, src, dst):
    """Piecewise linear map, carried on straight past both ends."""
    if v <= src[0]:
        return dst[0] + (v - src[0]) * (dst[1] - dst[0]) / (src[1] - src[0])
    if v >= src[-1]:
        return dst[-1] + (v - src[-1]) * (dst[-1] - dst[-2]) / (src[-1] - src[-2])
    return float(np.interp(v, src, dst))


def _chains(pdf, page, clip, drop=(), max_lw=3.0, dashed=False):
    """Stroked chains inside clip: (pdf line width, segs, grey level of the stroke, dashed)."""
    pg = pymupdf.open(pdf)[page - 1]
    ins = lambda bb, b: bb[0] >= b[0] and bb[2] <= b[2] and bb[1] >= b[1] and bb[3] <= b[3]
    box = (clip[0] - 0.5, clip[1] - 0.5, clip[2] + 0.5, clip[3] + 0.5)
    out = []
    for d in pg.get_drawings():
        if d["type"] not in ("s", "fs") or d.get("color") is None or (d.get("width") or 0) > max_lw:
            continue
        ds = d.get("dashes")
        dash = bool(ds) and ds not in ("[] 0", "")
        if dash and not dashed:
            continue
        chains, cur = [], []
        for sg in T.to_segs(d):
            if cur and (abs(sg[1][0] - cur[-1][-1][0]) > 0.02 or abs(sg[1][1] - cur[-1][-1][1]) > 0.02):
                chains.append(cur); cur = []
            cur.append(sg)
        if cur:
            chains.append(cur)
        for segs in chains:
            P = np.vstack([T.flat(sg) for sg in segs])
            bb = (P[:, 0].min(), P[:, 1].min(), P[:, 0].max(), P[:, 1].max())
            if ins(bb, box) and not any(ins(bb, b) for b in drop):
                out.append((d.get("width") or 0, segs, d["color"][0], dash))
    return out


def _bb(segs):
    P = np.vstack([T.flat(sg) for sg in segs])
    return P[:, 0].min(), P[:, 1].min(), P[:, 0].max(), P[:, 1].max()


def _on_circle(segs, xc, yc, r, tol=1.5):
    P = np.vstack([T.flat(sg) for sg in segs])
    return bool((np.abs(np.hypot(P[:, 0] - xc, P[:, 1] - yc) - r) < tol).all())


def _mapped(segs, f):
    return [(sg[0],) + tuple(f(p) for p in sg[1:]) for sg in segs]


def _finish(self, parts, lw, ports, k, hidden=(), px=20, close=3):
    """parts: seg lists already in mm. Silhouette, strokes, box and ports, as for UFT32.
    hidden: extra seg lists that close the silhouette where the TI leaves a gap (behind another part); not drawn.
    close: gap (px at px per mm) the silhouette bridges between line ends; raise it for drawings made of many short
    pieces that do not quite meet (TI-P127-03-US)."""
    thick = [(lw, segs) for segs in parts] + [(lw, segs) for segs in hidden]
    P = np.vstack([T.flat(sg) for _, segs in thick for sg in segs])
    mg = 6
    c2 = (P[:, 0].min() - mg, P[:, 1].min() - mg, P[:, 0].max() + mg, P[:, 1].max() + mg)
    g = T.assemble(thick, [], c2, px=px, close=close)
    self.fill = [[tuple(p) for p in poly] for poly in g["fill"]]
    self.strokes = [(w, [[sg[0]] + [tuple(p) for p in sg[1:]] for sg in segs]) for w, segs in g["outline"][:len(parts)]]
    m = lw / 2
    self.x0, self.y0 = P[:, 0].min() - m, P[:, 1].min() - m
    self.x1, self.y1 = P[:, 0].max() + m, P[:, 1].max() + m
    self.w, self.h = self.x1 - self.x0, self.y1 - self.y0
    self.ports = ports
    self.arrow = None
    self.k = k


def _uft14hc(self):
    """TI-P712-01 p3 side view. x to A (spigot face to dome end); y piecewise: flange to D, body to B."""
    A, B, D = self.d["A"], self.d["B"], self.d["D"]
    lw = 0.7
    ch = _chains(UFT14HC_PDF, 3, (200, 528, 383, 631), max_lw=1.0)
    xa, xb = 202.50, 381.15                          # spigot face, dome end (stroke centrelines, pt)
    yc, ft, fb, bt, bb = 599.91, 570.72, 629.10, 529.91, 626.61   # centreline, flange top/bottom, body top/bottom
    sx = (A - lw) / (xb - xa)
    kd = (D - lw) / (fb - ft)
    ybb = (bb - yc) * kd
    src, dst = [bt, ft, yc, bb, fb], [ybb - (B - lw), -(D - lw) / 2, 0, ybb, (D - lw) / 2]
    f = lambda p: ((p[0] - xa) * sx + lw / 2, _pw(p[1], src, dst))
    _finish(self, [_mapped(segs, f) for _, segs, _, _ in ch], lw, {"in": (0.0, 0.0)}, sx)


def _ubp32(self):
    """TI-P127-01 p4 end view: the trap as seen from the front of its connector (Mason, 2026-11-16). Plate C 68 round,
    capsule housing D in front of it, two connector screw ears level with the plate centre. Origin at the centre of the
    two screws (= plate centre = spigot), which is the trap point on the connectors."""
    C = self.d["C"]
    lw = 0.6
    ch = [c for c in _chains(UBP32_PDF, 4, (290, 50, 412, 178), max_lw=2.0) if c[2] < 0.9]
    x0, x1, xc, yc = 296.57, 404.59, 350.58, 124.51      # plate circle, screw centre
    k = (C - lw) / (x1 - x0)
    _finish(self, [_mapped(segs, lambda p: ((p[0] - xc) * k, (p[1] - yc) * k)) for _, segs, _, _ in ch], lw,
            {"trap": (0.0, 0.0)}, k)
    self.d = dict(self.d, **{"Screw spacing (drawn)": round((390.88 - 310.28 + 0) * k, 1)})


def _utds46m(self):
    """TI-P187-03 p4 side view. x to the 113 length, y to the 67 flange (about the connector centreline)."""
    L, F = self.d["Length"], self.d["Flange"]
    lw = 0.6
    ch = _chains(UTDS46M_PDF, 4, (214, 388, 372, 519), drop=[(216.0, 495.5, 217.3, 515.5)], max_lw=1.0)
    xa, xb = 216.82, 369.35                          # spigot face, strainer cap end
    yc, ft, fb = 469.29, 422.44, 516.14
    sx = (L - lw) / (xb - xa)
    ky = (F - lw) / (fb - ft)
    f = lambda p: ((p[0] - xa) * sx + lw / 2, (p[1] - yc) * ky)
    _finish(self, [_mapped(segs, f) for _, segs, _, _ in ch], lw, {"in": (0.0, 0.0)}, sx)


# Landmarks of the three UIB front views (pt): connector circle centre and top, connector end blocks (x: outer face,
# inner face, inner face, outer face; y band), bucket sides, top of the cover lip (y, x from, x to), bottom of the
# lip, start of the bottom curve, bottom of the cover; for the drain plug view also the plug sides and plug bottom.
UIBV = {
    "UIB45": dict(pdf=UIB45_PDF, page=5, clip=(50, 100, 175, 366), drop=(), conn="grey",
                  xc=111.47, yc=146.46, top=105.06, rect=(67.63, 97.51, 125.54, 155.03), band=(122.00, 170.84),
                  bucket=(58.80, 164.60), lipt=(174.39, 55.65, 167.76), lipb=188.26, ys=309.05, bot=364.43),
    "UIB30": dict(pdf=UIB30_PDF, page=4, clip=(376, 85, 447, 216), drop=(), conn="dashed",
                  xc=411.5, yc=117.40, top=90.78, rect=(382.33, 401.60, 421.36, 440.70), band=(102.70, 132.10),
                  bucket=(381.47, 441.56), lipt=(129.17, 378.54, 444.49), lipb=136.87, ys=203.39, bot=214.94),
    "UIB30-plug": dict(pdf=UIB30_PDF, page=4, clip=(376, 430, 448, 588), drop=[(427.0, 580.0, 447.0, 581.5)],
                       conn="dashed", xc=412.8, yc=464.485, top=437.83, rect=(383.57, 402.86, 422.65, 442.02),
                       band=(449.76, 479.21), bucket=(382.71, 442.88), lipt=(476.27, 379.77, 445.82), lipb=483.99, ys=550.59, bot=562.16,
                       plug=(400.16, 425.43, 587.11)),
}


def _uib(self):
    plug = self.variant == "Drain plug"
    V = UIBV[self.model.rstrip("H") + ("-plug" if plug else "")]
    A, D, E = self.d["A"], self.d["D"], self.d["E"]
    C = self.d.pop("Cp", None)
    if plug:
        self.d.update(C=C, F=32, G=20)
    else:
        C = self.d["C"]
    lw = 0.7
    ch = _chains(V["pdf"], V["page"], V["clip"], drop=V["drop"], max_lw=1.0, dashed=True)
    xc, yc, (r0, r1, r2, r3), (b0, b1) = V["xc"], V["yc"], V["rect"], V["band"]
    kc = (D - lw / 2) / (yc - V["top"])                          # connector: D sets its size
    xsrc = [r0, r1, r2, r3]
    xdst = [lw / 2, A / 2 - (xc - r1) * kc, A / 2 + (r2 - xc) * kc, A - lw / 2]
    q0, q1 = V["bucket"]
    kt = (E - lw) / (q1 - q0)                                   # trap: E sets its size, C its height
    qc = (q0 + q1) / 2
    ybot = C - D - lw / 2
    if plug:
        p0, p1, pb = V["plug"]
        kp = (self.d["F"] - lw) / (p1 - p0)
        ybot -= (pb - V["bot"]) * kp
    ylip = (V["lipb"] - yc) * kt
    ycurve = ybot - (V["bot"] - V["ys"]) * kt
    assert ycurve > ylip, (self.model, self.size, self.variant)
    ysrc, ydst = [yc, V["lipb"], V["ys"], V["bot"]], [0.0, ylip, ycurve, ybot]
    circ = lambda p: (A / 2 + (p[0] - xc) * kc, (p[1] - yc) * kc)
    ends = lambda p: (_pw(p[0], xsrc, xdst), (p[1] - yc) * kc)
    trap = lambda p: (A / 2 + (p[0] - qc) * kt, _pw(p[1], ysrc, ydst))
    parts = []
    for _, segs, grey, dash in ch:
        x0, y0, x1, y1 = _bb(segs)
        conn = (dash if V["conn"] == "dashed" else grey > 0.4) or (x0 > r1 - 1 and x1 < r2 + 1 and y1 < V["lipb"])
        if plug and y1 > V["bot"] + 0.5:
            f = lambda p: (A / 2 + (p[0] - (p0 + p1) / 2) * kp, ybot + (p[1] - V["bot"]) * kp)
        elif not conn:
            f = trap
        elif _on_circle(segs, xc, yc, yc - V["top"]) or (y1 - y0 > 1 and (y1 < b0 + 0.3 or y0 > b1 - 0.3)):
            f = circ                                               # the round body and what hangs off it keep their shape
        else:
            f = ends                                               # end blocks stretch to A
        parts.append(_mapped(segs, f))
    lt, l0, l1 = V["lipt"]                                 # tops of the cover and its lip, hidden behind the connector
    close = [T.polyline([trap((q0, V["lipb"])), trap((q1, V["lipb"]))]), T.polyline([trap((l0, lt)), trap((l1, lt))])]
    _finish(self, parts, lw, {"in": (0.0, 0.0), "out": (A, 0.0)}, kt, hidden=close)


DATA["UTD52L"] = {
    "name": "UTD52L", "type": "Thermodynamic, bar stock, on strainer connector", "ti": "TI-P614-04-US",
    "sizes": {'1/2"': {"Cap top to centreline": 38.1, "Centreline to strainer bottom": 76.2}},
    "variants": ["Strainer connector"], "variantLabel": "Connector",
    "source": "Vectorised from the TI picture (the sheet has no vector drawing)",
    "note": "Front view on a 1/2\" strainer connector, as the TI draws it (third view on page 3): pipe left to right, "
            "strainer leg down on the inlet side. The TI drawing is only a picture, so it was vectorised "
            "(tools/raster.py), not traced: lines follow the picture to within about 0.3 mm, but joints are not as clean as a traced drawing. "
            "Heights are from the TI: 1.5\" cap top to centreline, 3.0\" centreline to the bottom of the strainer. "
            "The TI gives no face to face for the connector; it is measured from the picture at the same scale "
            "(about 80 mm) and the connections are there. The connector is sold separately (TI-2-519-US, not "
            "attached), so 3/4\" and 1\" connectors are not drawn.",
}


def _utd52l(self):
    """TI-P614-04-US p3, third view, picture xref 30 (2219 x 643 px). y above and below the centreline each set from
    its TI dimension; x at the mean of the two scales."""
    import raster as R
    up, dn = self.d["Cap top to centreline"], self.d["Centreline to strainer bottom"]
    lw = 0.6
    white = [(1466, 70, 1545, 93), (1185, 226, 1199, 237), (1497, 226, 1545, 237), (1185, 509, 1398, 520),
             (1212, 228, 1286, 235), (1424, 228, 1489, 235),           # dimension lines and the centre line
             (1297, 262, 1365, 300), (1437, 212, 1486, 250)]           # lettering on the body
    g, o = R.crop(R.image(UTD52L_PDF, 3, 30), (1185, 70, 1545, 530), white)
    x0, top, x1, bot = R.extent(g, o)
    yc, xin, xout = 231.5, 1194, 1500                                  # centreline, connector end faces (px)
    ku, kd = up / (yc - top), dn / (bot - yc)
    kx = (ku + kd) / 2
    fx = lambda x: (x - xin) * kx
    fy = lambda y: (y - yc) * (ku if y < yc else kd)
    m = lw / 2 / kx                                                     # px from the outer edge to the stroke centre
    fy_in = lambda y: fy(min(max(y, top + m), bot - m))
    fx_in = lambda x: fx(min(max(x, xin + m), x1 - m))
    strokes = []
    for w, Q in R.polylines(g, o):
        pts = [(fx_in(x), fy_in(y)) for x, y in Q]
        strokes.append([["l", pts[i], pts[i + 1]] for i in range(len(pts) - 1)])
    self.fill = [[(fx(x), fy(y)) for x, y in poly] for poly in R.silhouette(g, o)]
    self.strokes = [(lw, segs) for segs in strokes]
    P = np.array([p for poly in self.fill for p in poly])
    self.x0, self.y0 = min(P[:, 0].min(), 0.0), -up
    self.x1, self.y1 = P[:, 0].max(), dn
    self.w, self.h = self.x1 - self.x0, self.y1 - self.y0
    A = round(fx(xout), 1)
    self.d["Face to face (from the picture)"] = A
    self.ports = {"in": (0.0, 0.0), "out": (A, 0.0)}
    self.arrow = None
    self.k = kx


# ---------------------------------------------------------------- 4-bolt (PC90) trap units, added 2026-11-16
# USM90 (TI-P805-01) and UTDS90 (TI-P804-01): side view of the trap unit, face on the left as the TI draws it.
# The connection point is the connector face, at the height of the PC90 pipe centreline. That height is read from the
# TI's third view (trap bolted to the PC90, pipe end on): both views share the same y on the sheet. The trap's own
# spigot sits about 5 mm below the pipe centreline.
N_90 = ("Trap unit only, side view as the TI draws it. The PC90 4-bolt connector is not drawn here (the PC90 pack is a front "
        "view; a side view to bolt this trap onto is not in the library for now). The connection point is the connector face at the height of the PC90 pipe "
        "centreline, read from the TI's view of the trap on its connector. ")
# Sizes are the PC90 sizes it bolts to (Mason, 2026-11-17); one trap unit fits all three, so every size is the same drawing.
PC90_SIZES = ['1/2"', '3/4"', '1"']
DATA["USM90"] = {
    "name": "USM90", "type": "Bimetallic, sealed stainless, for PC90 4-bolt connector", "ti": "TI-P805-01",
    "sizes": {sz: dict(A=115, B=79, C=64, D=67) for sz in PC90_SIZES}, "variants": ["-"],
    "note": "Front view from Spirax's 2D CAD of the USM90 (front DWG, visible edges only), 1:1: the trap seen from its "
            "connector side, four connector bolts on a 44.5 square round the spigot, body C 64 round above it. The one "
            "connection point is the centre of the four bolts (= spigot centre), the same point as the PC90 front view's "
            "trap point (54 from the inlet, 5.5 below the pipe centreline), so it snaps on. Sizes 1/2\", 3/4\" and 1\" are the PC90 sizes; the trap unit is the same for all three. CAD: flange 66.5 (D 67), "
            "top of the body to the bottom of the flange 79.7 (B 79), spigot face to body end 114.3 (A 115). Replaces the "
            "TI-built front view and the side view (2026-11-17); _usm90 / _usm90_front still build those from TI-P805-01.",
}
DATA["UTDS90"] = {
    "name": "UTDS90", "type": "Thermodynamic with strainer, stainless, for PC90 4-bolt connector", "ti": "TI-P804-01",
    "sizes": {sz: dict(A=94, B=64, C=67, D=119) for sz in PC90_SIZES}, "variants": ["-"],
    "note": "Front view from Spirax's 2D CAD of the UTDS90 (front DWG, visible edges only), 1:1: the trap seen from its "
            "connector side, four connector bolts on a 44.5 square round the spigot, cap plate and cap screws above. "
            "The one connection point is the centre of the four bolts (= spigot centre), the same point as the PC90 "
            "front view's trap point, so it snaps on. Sizes 1/2\", 3/4\" and 1\" are the PC90 sizes; the trap unit is the same for all three. CAD: flange 66.5 (C 67), cap plate 94 across (A 94), spigot face "
            "to body end 118.8 (D 119); top of the cap screws is 67 above the spigot centre where the TI table gives B "
            "64 (the CAD is taken as right). Replaces the built (guessed) front view and the side view (2026-11-17); "
            "_utds90 / _utds90_front still build those from TI-P804-01.",
}


# USM90 and UTDS90 front views from Spirax's 2D CAD (Mason, 2026-11-17: zips "USM90" and "UTDS90", usm90 / utds90 front,
# top, left DWG). Both downloads share one CAD frame with the spigot at CAD (0, 0); tools/cad/USM90-front.json and
# UTDS90-front.json are the front DWGs' MAIN-1 layer, origin CAD (0, 0). Measured:
#   USM90  front: bolt hexes (r 11 lobes) centred (+-22.27, +-22.27), 44.54 square (PC90 holes 44.6); spigot circles about
#                 (0, 0) -> trap point = bolt centre = origin; body circle r 32 about (0, 14), top y 46.39; flange +-33.27
#          left:  flange x -20..0, spigot face x 3.8; dome arc (-58.18, 14) r 52.3 -> end x -110.48; spigot face to dome
#                 end 114.3 (A 115); body y -18..46 (C 64), body axis 14 above the spigot
#   UTDS90 front: same bolts, spigot and flange; cap plate x +-47, y 31.45..50.45; cap screw tops y 67.0
#          left:  flange x -20..0, spigot face x 3.8; cap plate x -115..-21 (A 94); spigot face to body end 118.8 (D 119)
#          top:   cap circle r 47 (94), six cap screws r 5 on a 37 radius
CAD90 = {"USM90": Path(__file__).with_name("cad") / "USM90-front.json",
         "UTDS90": Path(__file__).with_name("cad") / "UTDS90-front.json"}


def _cad90(self):
    lw = 0.35
    pl = json.load(open(CAD90[self.model]))["polylines"]
    _finish(self, [T.polyline(p) for p in pl if len(p) > 1], lw, {"trap": (0.0, 0.0)}, 1.0, close=6)
    if self.model == "USM90":
        self.d = {"A (spigot face to body end)": 114.3, "B (body top to flange bottom)": 79.7, "C (body)": 64,
                  "D (flange)": 66.5, "Bolt square": 44.54}
    else:
        self.d = {"A (cap plate)": 94, "Cap screw top above centreline": 67.0, "C (flange)": 66.5,
                  "D (spigot face to body end)": 118.8, "Bolt square": 44.54}


def _usm90_front(self):
    """TI-P805-01 p4 end view D (flange face), turned into the view from the front of the PC90: body circle in front,
    flange outline and holes only where outside it. Origin at the centre of the four bolt holes."""
    lw = 0.6
    ch = [c for c in _chains(USM90_PDF, 4, (212, 395, 290, 478), max_lw=1.0) if c[2] < 0.9]
    xl, xr, hc = 218.42, 283.02, (250.74, 445.77)          # flange sides, bolt hole centre
    k = (self.d["D"] - lw) / (xr - xl)
    r = self.d["C"] / 2 - lw / 2
    cy = (432.33 - hc[1]) * k                              # body centre, above the bolt centre (TI: body top 401.27)
    f = lambda p: ((p[0] - hc[0]) * k, (p[1] - hc[1]) * k)

    def outside(segs):                                     # parts of a traced chain not hidden by the body
        out = []
        for sg in segs:
            P = np.array([f(p) for p in T.flat(sg)])
            vis = np.hypot(P[:, 0], P[:, 1] - cy) > r + lw / 2
            run = []
            for p, v in zip(P, vis):
                if v:
                    run.append(tuple(p))
                else:
                    if len(run) > 1:
                        out.extend(T.polyline(run))
                    run = []
            if len(run) > 1:
                out.extend(T.polyline(run))
        return out
    parts, hidden = [T.circle(0.0, cy, r)], []
    for _, segs, _, _ in ch:
        b = _bb(segs)
        w, h = b[2] - b[0], b[3] - b[1]
        flange = (abs(w - 15.47) < 0.2 and abs(h - 15.47) < 0.2) or (abs(w - 33.66) < 0.2 and abs(h - 3.96) < 0.2) \
            or (abs(w - 3.96) < 0.2 and abs(h - 33.66) < 0.2)
        hole = abs(w - 7.66) < 0.1 and abs(h - 7.7) < 0.1
        if flange or hole:
            o = outside(segs)
            if o:
                parts.append(o)
            if flange:
                hidden.append(_mapped(segs, f))             # whole flange outline closes the silhouette
    _finish(self, parts, lw, {"trap": (0.0, 0.0)}, k, hidden=hidden)


def _usm90(self):
    """TI-P805-01 p4 side view. x to A (face to the dome end), y to B (top of the body to the bottom of the flange)."""
    if self.variant.startswith("Front"):
        return _usm90_front(self)
    A, B = self.d["A"], self.d["B"]
    lw = 0.6
    ch = _chains(USM90_PDF, 4, (72, 398, 184, 481), max_lw=1.0)
    ch = [c for c in ch if c[2] < 0.9]
    xa, xb, yt, yb, yc = 74.38, 180.79, 401.19, 478.08, 440.55     # face, dome end, body top, flange bottom, pipe CL
    sx, sy = (A - lw) / (xb - xa), (B - lw) / (yb - yt)
    f = lambda p: ((p[0] - xa) * sx + lw / 2, (p[1] - yc) * sy)
    _finish(self, [_mapped(segs, f) for _, segs, _, _ in ch], lw, {"in": (0.0, 0.0)}, sx)


def _rrect(x0, y0, x1, y1, r):
    """Rounded rectangle as one closed seg list (corner arcs as Beziers)."""
    c = 0.5522847498 * r
    return [("l", (x0 + r, y0), (x1 - r, y0)), ("c", (x1 - r, y0), (x1 - r + c, y0), (x1, y0 + r - c), (x1, y0 + r)),
            ("l", (x1, y0 + r), (x1, y1 - r)), ("c", (x1, y1 - r), (x1, y1 - r + c), (x1 - r + c, y1), (x1 - r, y1)),
            ("l", (x1 - r, y1), (x0 + r, y1)), ("c", (x0 + r, y1), (x0 + r - c, y1), (x0, y1 - r + c), (x0, y1 - r)),
            ("l", (x0, y1 - r), (x0, y0 + r)), ("c", (x0, y0 + r), (x0, y0 + r - c), (x0 + r - c, y0), (x0 + r, y0))]


def _hexnut(cx, yb, w, h):
    """Hex nut seen across the corners from the side: outline and the two visible edges between flats."""
    return [T.polyline([(cx - w / 2, yb), (cx - w / 2, yb - h), (cx + w / 2, yb - h), (cx + w / 2, yb)], closed=True),
            T.polyline([(cx - w / 4, yb), (cx - w / 4, yb - h)]), T.polyline([(cx + w / 4, yb), (cx + w / 4, yb - h)])]


def _utds90_front(self):
    """Front view, as for USM90: the trap seen from the front of the PC90, sitting over it. TI-P804-01 draws no such
    view, so it is built (Mason asked for a best guess, 2026-11-16). Heights are the side view's, mapped as _utds90
    maps them, measured from the spigot (= the 4-bolt centre, the trap point). The flange is USM90's 4-bolt flange
    (TI-P805-01 view D, 67 square; UTDS90's flange C is 67 and bolts to the same PC90). Widths across are not on the
    TI and are assumed: cap plate 64, body 54, strainer housing 40, two rows of cap screws 40 apart."""
    lw = 0.6
    # heights from the side view (mm, + down, origin at the spigot centre)
    nut_top, cap_top, cap_bot, body_top, body_bot, str_bot = -63.1, -49.1, -28.4, -23.3, -2.6, 14.6
    front = [(-32.0, cap_top, 32.0, cap_bot, 4.0), (-27.0, body_top, 27.0, body_bot, 2.0), (-20.0, body_bot, 20.0, str_bot, 6.0)]
    parts = [_rrect(*r) for r in front]
    for sx in (-20.0, 20.0):
        parts.append(T.polyline([(sx - 3.5, cap_bot), (sx - 3.5, body_top)]) + T.polyline([(sx + 3.5, cap_bot), (sx + 3.5, body_top)]))
        parts += _hexnut(sx, cap_top, 19.0, 10.0)
        parts.append(T.polyline([(sx - 5, cap_top - 10.0), (sx - 5, nut_top), (sx + 5, nut_top), (sx + 5, cap_top - 10.0)]))
    # flange behind: USM90's view D outline and holes, only where no front part covers it
    ch = [c for c in _chains(USM90_PDF, 4, (212, 395, 290, 478), max_lw=1.0) if c[2] < 0.9]
    xl, xr, hc = 218.42, 283.02, (250.74, 445.77)
    k = (self.d["C"] - lw) / (xr - xl)
    f = lambda p: ((p[0] - hc[0]) * k, (p[1] - hc[1]) * k)
    cover = [(x0 - lw, y0 - lw, x1 + lw, y1 + lw) for x0, y0, x1, y1, _ in front] + \
            [(sx - 3.5 - lw, cap_bot, sx + 3.5 + lw, body_top) for sx in (-20.0, 20.0)]
    hid = lambda q: any(a <= q[0] <= c and b <= q[1] <= d for a, b, c, d in cover)
    hidden = []
    for _, segs, _, _ in ch:
        b = _bb(segs)
        w, h = b[2] - b[0], b[3] - b[1]
        flange = (abs(w - 15.47) < 0.2 and abs(h - 15.47) < 0.2) or (abs(w - 33.66) < 0.2 and abs(h - 3.96) < 0.2) \
            or (abs(w - 3.96) < 0.2 and abs(h - 33.66) < 0.2)
        hole = abs(w - 7.66) < 0.1 and abs(h - 7.7) < 0.1
        if not (flange or hole):
            continue
        out = []
        for sg in segs:
            P = np.array([f(p) for p in T.flat(sg)])
            if len(P) == 2:                                   # straight line: split finely so it can be cut
                P = np.linspace(P[0], P[1], 60)
            run = []
            for p in P:
                if not hid(p):
                    run.append(tuple(p))
                else:
                    if len(run) > 1:
                        out.extend(T.polyline(run))
                    run = []
            if len(run) > 1:
                out.extend(T.polyline(run))
        if out:
            parts.append(out)
        if flange:
            hidden.append(_mapped(segs, f))
    _finish(self, parts, lw, {"trap": (0.0, 0.0)}, k, hidden=hidden)


def _utds90(self):
    """TI-P804-01 p4 side view. x to D (face to the end of the body); y piecewise: flange to C, top to B."""
    if self.variant.startswith("Front"):
        return _utds90_front(self)
    B, C, D = self.d["B"], self.d["C"], self.d["D"]
    lw = 0.6
    ch = _chains(UTDS90_PDF, 4, (118, 428, 252, 537), max_lw=1.0)
    ch = [c for c in ch if c[2] < 0.9]
    xa, xb = 120.09, 248.43                                         # spigot face, end of the body
    yt, ft, fb, ysp, yc = 431.27, 461.74, 533.93, 497.83, 491.9     # top, flange top / bottom, spigot centre, pipe CL
    sx = (D - lw) / (xb - xa)
    kc = (C - lw) / (fb - ft)
    Ysp = (ysp - yc) * kc
    Ytop = Ysp - (B - lw / 2)
    src, dst = [yt, ft, fb], [Ytop, Ysp - (ysp - ft) * kc, Ysp + (fb - ysp) * kc]
    f = lambda p: ((p[0] - xa) * sx + lw / 2, _pw(p[1], src, dst))
    _finish(self, [_mapped(segs, f) for _, segs, _, _ in ch], lw, {"in": (0.0, 0.0)}, sx)


# UFT32 front view from Spirax's 2D CAD (Mason, 2026-11-17: zip "UFT32", uft32-4_5_connector_5300 front / top / left
# DWG). tools/cad/UFT32-front.json is the front DWG's MAIN-1 layer, 1:1 mm, origin at CAD x -89.32, y 121.03. Measured:
#   front view: body circle r 47 (B 94) about (-89.32, 121.03); bolt hex centres (-89.32, 146.43) and (-89.32, 95.63),
#               50.8 apart vertical; spigot circles about the same centre -> trap point = bolt centre = origin
#   left view:  spigot / body axis y 121.03, bolts y 95.63 / 146.43; dome end x -144.49 to connector face x 24.01
#               = 168.5 (A on the TI)
#   top view:   body x -136.32 to -42.32 = 94 (B)
UFT32_CAD = Path(__file__).with_name("cad") / "UFT32-front.json"


def _uft32cad(self):
    lw = 0.35
    pl = json.load(open(UFT32_CAD))["polylines"]
    _finish(self, [T.polyline(p) for p in pl if len(p) > 1], lw, {"trap": (0.0, 0.0)}, 1.0, close=6)
    self.d = {"A (dome end to connector face)": 168.5, "B (body)": 94, "Bolt spacing": 50.8}


# UFT14HC front view from Spirax's 2D CAD (Mason, 2026-11-17: zip "UFT14", uft14hc-4_5_connector_5011 front / top /
# left DWG). tools/cad/UFT14HC-front.json is the front DWG's MAIN-1 layer, origin at CAD x -89.32, y 121.03 (same as UFT32).
#   front view: flange circle r 33.5 (D 67) and spigot circles about (-89.32, 121.03); bolt hex centres (-89.32, 95.63)
#               and (-89.32, 146.43), 50.8 apart vertical (E); body collar circle r 55.5 about (-89.32, 145.88)
#   left view:  dome end (r 80 arc) x -179.84 to spigot end face x 25.16 = 205 (A); dome end to collar face x -27.14 =
#               152.7 (C 153); flange x 4.01-17.01, y 87.53-154.53 = 67 (D); body axis y 145.88, spigot axis y 121.03
#   top view:   body x -144.32 to -34.32 = 110 (B); collar 111
UFT14HC_CAD = Path(__file__).with_name("cad") / "UFT14HC-front.json"


def _uft14hccad(self):
    lw = 0.35
    pl = json.load(open(UFT14HC_CAD))["polylines"]
    _finish(self, [T.polyline(p) for p in pl if len(p) > 1], lw, {"trap": (0.0, 0.0)}, 1.0, close=6)
    self.d = {"A (dome end to spigot face)": 205, "B (body)": 110, "D (flange)": 67, "E (bolt spacing)": 50.8}


# UTDS46M and UTDS46M with BDV2 front views from Spirax's 2D CAD (Mason, 2026-11-17: zips "UTDS46M" and
# "UTDS46M_WITH_BDV2", utds46m_connector_1200 / _1251 front / top / left DWG). Both downloads share one CAD frame;
# tools/cad/UTDS46M-front.json and UTDS46M-BDV2-front.json are the front DWGs' MAIN-1 layer, origin CAD x 37.79, y 11.25.
#   front view: flange circle r 33.5 (D 67) and spigot circles about (37.79, 11.25); bolt hexes centred (37.79, 36.65)
#               and (37.79, -14.15), 50.8 apart vertical -> trap point = bolt centre = origin. BDV2 outlet end y -33.20
#               (44.45 below the spigot centreline), hex x 29.71-45.87
#   left view:  spigot axis y 11.25; flange x 83.35-96.35, y -22.25..44.75 (67); spigot face x 100.05; strainer cap end
#               x -9.60 -> spigot face to strainer cap end 109.65 (the old TI tracer used 113 for this length); cap top
#               y 67.05 (55.8 above the spigot centreline, TI 56); BDV2 end x -61.05 (51.45 past the strainer cap)
#   top view:   cap circle r 31.5 (63, TI 63) about (37.79, -43.45)
UTDS46M_CAD = {"UTDS46M": Path(__file__).with_name("cad") / "UTDS46M-front.json",
               "UTDS46M-BDV2": Path(__file__).with_name("cad") / "UTDS46M-BDV2-front.json"}


def _utds46mcad(self):
    lw = 0.35
    pl = json.load(open(UTDS46M_CAD[self.model]))["polylines"]
    _finish(self, [T.polyline(p) for p in pl if len(p) > 1], lw, {"trap": (0.0, 0.0)}, 1.0, close=6)
    self.d = {"D (flange)": 67, "Cap dia": 63, "Cap top to centreline": 55.8, "Bolt spacing": 50.8}
    if self.model == "UTDS46M-BDV2":
        self.d["BDV2 outlet below centreline"] = 44.45


TRACERS = {"UFT32": _uft32cad, "USM90": _cad90, "UTDS90": _cad90, "UTD52L": _utd52l, "UFT14HC": _uft14hccad, "UBP32": _ubp32, "UTDS46M": _utds46mcad, "UTDS46M-BDV2": _utds46mcad, "UIB45": _uib, "UIB30": _uib, "UIB30H": _uib}
