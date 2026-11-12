"""Valves traced from TI sheets supplied outside the product handbook."""
import numpy as np
import ti_trace as T

from sources import A3S_PDF

DATA = {
    "A3S": {
        "name": "A3S / A3SS", "type": "Bellows sealed stop valve, Class 800", "ti": "TI-P132-09",
        "variants": ["screwed", "socket weld"],
        "sizes": {'1/2"': dict(A=80, B=136, C=70), '3/4"': dict(A=90, B=144, C=90), '1"': dict(A=110, B=167, C=110),
                  '1-1/4"': dict(A=127, B=194, C=110), '1-1/2"': dict(A=155, B=220, C=130), '2"': dict(A=170, B=230, C=180)}},
}
_chains = {}


class Valve:
    """A3S: length A is the body end to end, B is centreline to the top of the stem with the valve open,
    C is the handwheel diameter. The TI has one outline for all sizes, so each of those is set from the table."""
    def __init__(self, model, size, variant=None):
        d = DATA[model]
        self.model, self.size, self.variant = model, size, variant or d["variants"][0]
        self.d = dict(d["sizes"][size])
        A, B, C = self.d["A"], self.d["B"], self.d["C"]
        clip = (430, 62, 549, 242.5)
        if model not in _chains:
            _chains[model], _ = T.collect(A3S_PDF, 4, clip, outline_lw=0.3)
        ch = _chains[model]
        xl, xr, top, cl, wheel_y, ax = 433.4, 546.0, 65.3, 208.3, 92.0, 489.7
        wl, wr = 442.3, 534.3                                   # handwheel extent in the sketch
        s = A / (xr - xl)                                       # mm per drawing point along the pipe
        sw = C / (wr - wl)                                      # handwheel scale, same both ways so it stays round
        sy = (B - (wheel_y - top) * sw) / (cl - wheel_y)        # yoke and bonnet take up the rest of B

        def fx(p):
            if p[1] < wheel_y:
                return ((ax - xl) * s + (p[0] - ax) * sw, -B + (p[1] - top) * sw)
            if p[1] < cl:
                return ((p[0] - xl) * s, -B + (wheel_y - top) * sw + (p[1] - wheel_y) * sy)
            return ((p[0] - xl) * s, (p[1] - cl) * s)
        lw = max(0.5, 0.0075 * A)
        thick = [(lw, [(sg[0],) + tuple(fx(p) for p in sg[1:]) for sg in segs]) for _, segs in ch]
        P = np.array([p for _, segs in thick for sg in segs for p in sg[1:]])
        mg = 6 + 0.03 * A
        c2 = (P[:, 0].min() - mg, P[:, 1].min() - mg, P[:, 0].max() + mg, P[:, 1].max() + mg)
        g = T.assemble(thick, [], c2, px=min(10.0, 3600 / max(c2[2] - c2[0], c2[3] - c2[1])))
        self.fill = [[tuple(p) for p in poly] for poly in g["fill"]]
        self.strokes = [(w, [[sg[0]] + [tuple(p) for p in sg[1:]] for sg in segs]) for w, segs in g["outline"]]
        m = thick[0][0] / 2
        F = np.array([p for poly in self.fill for p in poly])
        self.x0, self.y0 = min(F[:, 0].min(), P[:, 0].min()) - m, min(F[:, 1].min(), P[:, 1].min()) - m
        self.x1, self.y1 = max(F[:, 0].max(), P[:, 0].max()) + m, max(F[:, 1].max(), P[:, 1].max()) + m
        self.w, self.h = self.x1 - self.x0, self.y1 - self.y0
        self.ports = {"in": (0, 0), "out": (A, 0)}
        self.A = A
        self.arrow = (A * 0.5, A * 0.1, A * 0.12, "r", thick[0][0] * 0.55)
        self.k = s
