"""Pivotrol PTF pressure powered pumps (TI-P207-06-US, handbook volume 1, section 5)."""
import numpy as np
import ti_trace as T
from sources import V1

DATA = {
    "PTF": {
        "name": "PTF / PTF-SS", "type": "Pivotrol pressure powered pump, with check valves", "ti": "TI-P207-06-US",
        "variants": ["flanged"],
        "sizes": {'2" x 2"': dict(A=742, B=366, C=356, D=815, E=130, F=279, G=264, H=800, I=160, J=947, K=15),
                  '3" x 2"': dict(A=767, B=366, C=356, D=815, E=130, F=279, G=264, H=800, I=160, J=947, K=15)},
        "note": "Front elevation with the inlet and outlet check valves fitted. Overall length A, the centre to "
                "outlet face B and overall height J are set from the TI table. The inlet check valve is scaled as a "
                "unit to make up length A, so on the 3\" x 2\" it is drawn larger than the outlet."},
    "PTF-TOP": {
        "name": "PTF Top Inlet", "type": "Pivotrol pressure powered pump, top inlet and outlet", "ti": "TI-P207-06-US",
        "variants": ["flanged"],
        "sizes": {'3" x 3"': dict(A=488, B=244, D=815, F=1039, H=800, J=1135, K=15, L=305, M=406, N=147, O=76)},
        "note": "Front elevation. Overall height J and the width across the check valve faces A are set from the "
                "TI table. The TI does not mark which side is the inlet; it is drawn with the inlet on the left."},
}
_chains = {}


def _collect(key, page, clip, drop):
    if key not in _chains:
        _chains[key], _ = T.collect(V1, page, clip, outline_lw=0.3, drop=drop, max_lw=1.5, short_dash_solid=True)
    return _chains[key]


class Pump:
    def __init__(self, model, size, variant=None):
        d = DATA[model]
        self.model, self.size, self.variant = model, size, variant or d["variants"][0]
        self.d = dict(d["sizes"][size])
        A, B, J = self.d["A"], self.d["B"], self.d["J"]
        if model == "PTF":
            # drawing landmarks, PDF points on page 883
            xc, wl, wr, fl, fr = 298.3, 238.7, 358.0, 192.6, 404.1      # centre, tank walls, check valve faces
            top, base, cin, cout = 70.0, 348.5, 266.6, 271.3            # top, floor, inlet and outlet centrelines
            ch = _collect(model, 883, (186, 66, 409, 350.5), [(297.9, 60, 298.7, 351), (303.5, 154.8, 331.2, 260.5)])
            s = J / (base - top)                                        # mm per point, whole pump
            rt = (wr - xc) * s                                          # tank radius, mm
            kin = (A - B - rt) / ((wl - fl) * s)                        # inlet nozzle + check valve, scaled as a unit
            kout = (B - rt) / ((fr - wr) * s)

            def fx(p):
                x, y = p
                if x < wl:
                    return (-rt + (x - wl) * s * kin, (cin - base) * s + (y - cin) * s * kin)
                if x > wr:
                    return (rt + (x - wr) * s * kout, (cout - base) * s + (y - cout) * s * kout)
                return ((x - xc) * s, (y - base) * s)
            named = {"in": (fl, cin), "out": (fr, cout), "motive": (293.5, 113.5), "exhaust": (283.3, 107.2)}
        else:
            xc, fl, fr = 298.7, 233.7, 363.8                            # centre, check valve faces
            top, base, cman, zone = 96.9, 427.4, 124.7, 153.0           # top, floor, manifold centreline, manifold zone
            ch = _collect(model, 884, (226, 95, 372, 428.6), [])
            s = J / (base - top)
            ka = (A / 2) / ((xc - fl) * s)                              # manifold stretched to the face-to-face width

            def fx(p):
                x, y = p
                return ((x - xc) * s * (ka if y < zone else 1.0), (y - base) * s)
            named = {"in": (fl, cman), "out": (fr, cman), "motive": (256.0, 194.5), "exhaust": (262.0, 189.6)}

        o = fx(named["in"])                                            # origin at the liquid inlet
        g = lambda p: (fx(p)[0] - o[0], fx(p)[1] - o[1])
        lw = 0.5 * s
        thick = [(lw, [(sg[0],) + tuple(g(p) for p in sg[1:]) for sg in segs]) for _, segs in ch]
        P = np.array([p for _, segs in thick for sg in segs for p in sg[1:]])
        mg = 12 + 0.03 * J
        clip = (P[:, 0].min() - mg, P[:, 1].min() - mg, P[:, 0].max() + mg, P[:, 1].max() + mg)
        r = T.assemble(thick, [], clip, px=min(10.0, 3600 / max(clip[2] - clip[0], clip[3] - clip[1])))
        self.fill = [[tuple(p) for p in poly] for poly in r["fill"]]
        self.strokes = [(w, [[sg[0]] + [tuple(p) for p in sg[1:]] for sg in segs]) for w, segs in r["outline"]]
        m = lw / 2
        self.x0, self.y0, self.x1, self.y1 = P[:, 0].min() - m, P[:, 1].min() - m, P[:, 0].max() + m, P[:, 1].max() + m
        self.w, self.h = self.x1 - self.x0, self.y1 - self.y0
        self.ports = {k: g(v) for k, v in named.items()}
        self.arrow = None
        self.k = s
