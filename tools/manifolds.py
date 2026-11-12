"""Forged steam distribution and condensate collection manifolds, MSC and MSD (TI-P115-03-US).

Traced from the front elevations of the full 12-station assemblies (page 7 MSC, page 8 MSD), both the
"without stand" drawing on the left and the "with stand" drawing on the right of each page.

How the station count is set
    The forged header is made of 4-station blocks (two rows of two). On every drawing the 12-station header is
    head + 3 blocks. The linework is cut into bands at fixed heights (cuts sit just below each block joint, where
    only the straight header walls cross):
        head   flange, nozzle and the top of the header
        block  first TI block, two rows and the joint under them; repeated
        tail   last two rows, the end of the header and everything below it (blowdown valve, trap set, stand)
    N stations = head + (N/4 - 1) blocks + tail. 12 stations gives back the TI drawing exactly.

Scale
    The drawings are "reference only". The TI dimension table (page 6) gives the station pitch B: 210 mm on the
    MSC drawing's version, 160 mm on the MSD drawing's version. Each drawing is scaled uniformly so one block is
    2 x B. Checks against the TI (12 stations): MSC body 1257 mm vs table A 50" (1270), overall 1526 mm vs 59-1/2"
    (1511); MSD body 956 mm vs 38.2" (970), overall 1364 mm vs 54-9/16" (1386). 16 stations is not in the table;
    it is one more block.
"""
import cv2
import numpy as np
import ti_trace as T
from sources import MANIFOLD_PDF

STATIONS = ["4", "8", "12", "16"]
VARIANTS = ["no stand", "with stand"]
IN = 25.4

# Landmarks, PDF points. cx header centreline, top flange face, block = header block pitch, head = first cut,
# rows = row centrelines of the first block (TI rows 1, 2) and of the tail (TI rows 5, 6).
SRC = {
    ("MSC", "no stand"): dict(page=7, clip=(92, 195, 234, 560), drop=[(129, 202, 150, 226), (180, 202, 200, 226)],
                              cx=164.7, top=198.9, hdr=(212.8, 503.5), block=97.15, head=218.45, rows=(236.9, 285.1, 431.15, 479.35)),
    ("MSC", "with stand"): dict(page=7, clip=(330, 112, 505, 662), drop=[],
                                cx=417.8, top=120.1, hdr=(136.2, 473.9), block=112.8, head=142.8, rows=(164.25, 220.25, 389.95, 445.95),
                                leg=(640.0, 658.95, 65.0 * 25.4)),
    ("MSD", "no stand"): dict(page=8, clip=(85, 195, 215, 575), drop=[(202, 218, 223, 241), (109, 218, 130, 241),
                                                                       (115, 368, 138, 462)],
                              cx=166.0, top=203.0, hdr=(223.3, 480.6), block=86.1, head=228.8, rows=(244.5, 287.55, 416.7, 459.75),
                              trapset=(85, 500, 150, 540, 516.36)),
    ("MSD", "with stand"): dict(page=8, clip=(340, 112, 492, 603), drop=[],
                                cx=429.4, top=118.5, hdr=(141.9, 438.3), block=99.15, head=148.35, rows=None,
                                trapset=(340, 455, 405, 505, 479.45), leg=(590.0, 600.65, 64.75 * 25.4)),
}
PITCH = {"MSC": 210.0, "MSD": 160.0}           # mm, TI table B for the version each drawing shows
SIDE = {"MSC": 9.625 * IN}                     # header centreline to station end, plan view on page 7 (9-5/8")

_N = ("Traced from the TI front elevation of the 12-station assembly (reference-only drawing). Station count is "
      "set by adding or removing 4-station header blocks; the station pitch is B from the TI table ({b} mm) and the "
      "body length checks against table A within 1.5%. 16 stations is not in the TI table and is one more block. "
      "The flange is drawn as on the TI (2\" ASME 150); 1-1/2\" and Class 300 flanges are not drawn separately. "
      "With stand: the TI's drawn stand leg does not agree with its own overall height, so the leg is set so the "
      "12-station assembly is the TI's overall height ({h}); the leg keeps that length for 4, 8 and 16 stations. ")
DATA = {
    "MSC": {"name": "MSC", "type": "Condensate collection manifold, forged, with trap stations", "ti": "TI-P115-03-US",
            "variants": VARIANTS, "sizes": {n: {} for n in STATIONS},
            "note": _N.format(b=210, h="65\"") + "Connections: first is the station 1 inlet (top left), second the condensate "
            "outlet at the top flange face, third the blowdown valve (drawn at the bottom of the valve, pointing "
            "down), then the other station inlets. Station inlets sit 9-5/8\" either side of the header centreline "
            "(TI plan view), behind the station handwheels."},
    "MSD": {"name": "MSD", "type": "Steam distribution manifold, forged, with drain trap set", "ti": "TI-P115-03-US",
            "variants": VARIANTS, "sizes": {n: {} for n in STATIONS},
            "note": _N.format(b=160, h="64-3/4\"") + "Connections: first is the steam inlet at the top flange face, second the "
            "station 1 outlet (top left), third the condensate drain at the bottom of the drain valve (pointing "
            "down), fourth the trap set condensate outlet, then the other station outlets. The TI front view does "
            "not show where the steam outlets face, so they are placed at the outer edge of each row's valves, on "
            "the row centreline."},
}
_ch = {}


def _chains(model, variant):
    k = (model, variant)
    if k not in _ch:
        s = SRC[k]
        th, _ = T.collect(MANIFOLD_PDF, s["page"], s["clip"], outline_lw=0.1, drop=s["drop"], max_lw=2.0)
        _ch[k] = [segs for _, segs in th]
    return _ch[k]


def _clip_line(a, b, y0, y1):
    """Part of segment a-b with y in [y0, y1), or None."""
    if a[1] > b[1]:
        a, b = b, a
    if b[1] < y0 or a[1] >= y1:
        return None
    def at(y):
        t = (y - a[1]) / (b[1] - a[1]) if b[1] != a[1] else 0
        return (a[0] + (b[0] - a[0]) * t, y)
    p = a if a[1] >= y0 else at(y0)
    q = b if b[1] <= y1 else at(y1)
    return p, q


def _band(chains, y0, y1, dy):
    """Linework with y in [y0, y1), moved down by dy. Straight lines are cut at the band edges; curves go to
    the band holding their middle (none cross a cut)."""
    out = []
    for segs in chains:
        keep = []
        for sg in segs:
            if sg[0] == "l":
                r = _clip_line(sg[1], sg[2], y0, y1)
                if r and (abs(r[0][1] - r[1][1]) > 1e-6 or (y0 <= sg[1][1] < y1)):
                    keep.append(("l",) + tuple((p[0], p[1] + dy) for p in r))
            else:
                ym = sum(p[1] for p in sg[1:]) / 4
                if y0 <= ym < y1:
                    keep.append((sg[0],) + tuple((p[0], p[1] + dy) for p in sg[1:]))
        if keep:
            out.append(keep)
    return out


def simplify(strokes, eps):
    """Flatten each stroke chain to a polyline and drop points within eps (mm) of the line (Douglas-Peucker).
    The TI linework has thousands of near-zero segments; this keeps the pack small with no visible change."""
    out = []
    for lw, segs in strokes:
        pts = [np.array(segs[0][1], float)]
        for sg in segs:
            f = T.flat(sg) if sg[0] == "c" else np.array([sg[1], sg[2]], float)
            if np.hypot(*(f[0] - pts[-1])) > 1e-3:               # a gap inside the chain: start a new piece
                if len(pts) > 1:
                    out.append((lw, pts))
                pts = [f[0]]
            pts.extend(f[1:])
        if len(pts) > 1:
            out.append((lw, pts))
    res = []
    for lw, pts in out:
        Q = cv2.approxPolyDP(np.array(pts, np.float32).reshape(-1, 1, 2), eps, False)[:, 0, :].astype(float)
        if len(Q) < 2 or np.ptp(Q, axis=0).max() < eps:
            continue
        res.append((lw, [["l", tuple(Q[i]), tuple(Q[i + 1])] for i in range(len(Q) - 1)]))
    return res


class Manifold:
    def __init__(self, model, size, variant=None):
        d = DATA[model]
        self.model, self.size, self.variant = model, size, variant or d["variants"][0]
        self.d = {}
        s = SRC[(model, self.variant)]
        ch = _chains(model, self.variant)
        n = int(size) // 4                                   # header blocks
        B, h0 = s["block"], s["head"]
        lines = _band(ch, -1e9, h0, 0)
        for i in range(n - 1):
            lines += _band(ch, h0, h0 + B, i * B)
        dt = (n - 3) * B
        k = 2 * PITCH[model] / B                             # mm per point
        if "leg" in s:
            # Stand leg: the drawn leg does not agree with the TI's overall height, so the leg is cut at ys and the
            # base plate moved so the 12-station assembly is the TI's overall height (65" MSC, 64-3/4" MSD).
            ys, ybot, tgt = s["leg"]
            dl = tgt / k - (ybot - s["top"])                 # points; negative shortens the leg
            lines += _band(ch, h0 + 2 * B, ys + min(dl, 0), dt)
            lines += _band(ch, ys, 1e9, dt + dl)
            if dl > 0:                                        # stretch the leg walls across the gap
                for segs in ch:
                    for sg in segs:
                        if sg[0] == "l" and min(sg[1][1], sg[2][1]) < ys <= max(sg[1][1], sg[2][1]):
                            x = sg[1][0] + (sg[2][0] - sg[1][0]) * (ys - sg[1][1]) / (sg[2][1] - sg[1][1])
                            lines.append([("l", (x, ys + dt), (x, ys + dt + dl))])
        else:
            lines += _band(ch, h0 + 2 * B, 1e9, dt)

        lw = 0.45 * k
        cx, top = s["cx"], s["top"]
        fx = lambda p: ((p[0] - cx) * k, (p[1] - top) * k)
        thick = [(lw, [(sg[0],) + tuple(fx(p) for p in sg[1:]) for sg in segs]) for segs in lines]
        P = np.array([p for _, segs in thick for sg in segs for p in sg[1:]])
        mg = 20
        c2 = (P[:, 0].min() - mg, P[:, 1].min() - mg, P[:, 0].max() + mg, P[:, 1].max() + mg)
        g = T.assemble(thick, [], c2, px=min(4.0, 4000 / max(c2[2] - c2[0], c2[3] - c2[1])), close=2)
        self.fill = [[tuple(p) for p in poly] for poly in g["fill"]]
        self.strokes = simplify([(w, [[sg[0]] + [tuple(p) for p in sg[1:]] for sg in segs]) for w, segs in g["outline"]], 0.25)
        m = lw / 2
        self.x0, self.y0 = P[:, 0].min() - m, P[:, 1].min() - m
        self.x1, self.y1 = P[:, 0].max() + m, P[:, 1].max() + m
        self.w, self.h = self.x1 - self.x0, self.y1 - self.y0

        # rows of stations, mm from the flange face
        rows = s["rows"]
        if rows is None:                                     # MSD with stand: same layout as the MSD drawing
            r = SRC[("MSD", "no stand")]
            rows = tuple(s["hdr"][0] + (y - r["hdr"][0]) * (B / r["block"]) for y in r["rows"])
        ys = []
        for i in range(n - 1):
            ys += [rows[0] + i * B, rows[1] + i * B]
        ys += [rows[2] + dt, rows[3] + dt]
        ys = [(y - top) * k for y in ys]

        def ext(yc, half):                                  # outer x of the linework in a row band, mm
            sel = P[(P[:, 1] > yc - half) & (P[:, 1] < yc + half)]
            return sel[:, 0].min() - m, sel[:, 0].max() + m
        half = 0.45 * PITCH[model]
        stations = []
        for y in ys:
            xl, xr = (-SIDE[model], SIDE[model]) if model in SIDE else ext(y, half)
            stations += [(round(xl, 2), round(y, 2)), (round(xr, 2), round(y, 2))]

        # blowdown / drain valve: bottom of the linework under the header on the centreline (ignores the stand)
        hb = ys[-1] + half
        if self.variant == "with stand":                     # the stand leg runs past the valve: use the
            yb = Manifold(model, size, "no stand").ports["drain"][1]   # no-stand drawing's valve, same place
        else:
            near = P[(np.abs(P[:, 0]) < 0.6 * PITCH[model]) & (P[:, 1] > hb)]
            yb = near[:, 1].max() + m
        self.ports = {}
        if model == "MSC":
            self.ports["in"] = stations[0]
            self.ports["out"] = (0.0, 0.0)
        else:
            self.ports["in"] = (0.0, 0.0)
            self.ports["out"] = stations[0]
        self.ports["drain"] = (0.0, round(yb, 2))
        self.drain_angle = 90
        if model == "MSD":
            tx0, ty0, tx1, ty1, tyc = s["trapset"]
            yt = (tyc + dt - top) * k
            sel = P[(P[:, 1] > yt - 25) & (P[:, 1] < yt + 25) & (P[:, 0] < 0)]
            self.ports["trapset"] = (round(sel[:, 0].min() - m, 2), round(yt, 2))
        for i, p in enumerate(stations[1:], 2):
            self.ports[f"st{i}"] = p
        self.arrow = None
        self.k = k
        self.n = n
        body = (s["hdr"][1] - s["hdr"][0] + dt) * k
        self.d = {"Station pitch B": PITCH[model], "Header body length": round(body, 1),
                  "Overall height": round(self.h, 1), "Overall width": round(self.w, 1)}
