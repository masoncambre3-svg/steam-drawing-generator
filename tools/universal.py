"""Universal (swivel connector) steam traps, sealed trap units that bolt onto a pipeline connector.

UFT32 (TI-P146-05)
    Traced from the side elevation on page 4. The TI dimensions only the trap unit, not the connector:
      A 168.5  dome end to connector face
      B 94     body diameter
      C 47     connector centreline to underside of the body
    x is scaled to A, y to B (the drawing's flange ring is used for B), which puts the connector
    centreline at C from the bottom. The one connection is the connector face, on its centreline.
    Every pressure rating (UFT32-4.5 to -32) has the same outline.
"""
import numpy as np
import ti_trace as T
from sources import UFT32_PDF

UFT_RATINGS = ["4.5", "10", "14", "21", "32"]
DATA = {
    "UFT32": {
        "name": "UFT32", "type": "Ball float, sealed stainless, for pipeline connectors", "ti": "TI-P146-05",
        "sizes": {f"UFT32-{r}": dict(A=168.5, B=94, C=47) for r in UFT_RATINGS},
        "variants": ["-"], "sizeLabel": "Model",
        "note": "Trap unit only, as dimensioned on the TI. The pipeline connector (PC10HP, PC20, PC3_, PC4_) is not "
                "drawn: its dimensions are on TI-P128. The connection point is the connector face. Every rating "
                "has the same outline; pick the rating for the label only. Install with the TOP label up (as drawn).",
    },
}
_ch = {}


class Universal:
    def __init__(self, model, size, variant=None):
        d = DATA[model]
        self.model, self.size, self.variant = model, size, variant or d["variants"][0]
        self.d = dict(d["sizes"][size])
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
