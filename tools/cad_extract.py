"""Pull one 2D view out of a manufacturer CAD drawing (DXF) into tools/cad/<name>.json for a tracer to use.

Spirax CAD downloads come as DWG, one file per view (front, back, left, ...), already flattened to 2D lines with the
visible edges on layer MAIN-1 and the hidden ones on MAIN-2. Convert DWG to DXF first with LibreDWG (not installed by
default; build it from the GitHub release, see tools/README.md), then:

    python3 tools/cad_extract.py front.dxf tools/cad/PC4000-front.json --origin -202.94 48.07 --layer MAIN-1

Output units are mm (the CAD is 1:1), x to the right and y DOWN like the TI tracers, origin at --origin (CAD
coordinates), so the pack's inlet can sit at (0, 0). Lines that meet end to end are joined and simplified (0.03 mm).
"""
import argparse
import json
import math

import ezdxf
import numpy as np
from ezdxf import path as dxfpath


def rdp(P, eps):
    if len(P) < 3:
        return P
    a, b = P[0], P[-1]
    ab = b - a
    n = math.hypot(*ab)
    D = P - a
    d = np.abs(ab[0] * D[:, 1] - ab[1] * D[:, 0]) / n if n > 1e-9 else np.hypot(D[:, 0], D[:, 1])
    i = int(np.argmax(d))
    if d[i] > eps:
        return np.vstack([rdp(P[:i + 1], eps)[:-1], rdp(P[i:], eps)])
    return np.array([a, b])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dxf")
    ap.add_argument("out")
    ap.add_argument("--origin", nargs=2, type=float, required=True)
    ap.add_argument("--layer", default="MAIN-1")
    ap.add_argument("--eps", type=float, default=0.03)
    a = ap.parse_args()
    ox, oy = a.origin
    doc = ezdxf.readfile(a.dxf)
    pieces = []
    for e in doc.modelspace():
        if e.dxf.layer != a.layer:
            continue
        t = e.dxftype()
        if t == "LINE":
            P = [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
        elif t in ("ARC", "ELLIPSE", "CIRCLE", "LWPOLYLINE", "POLYLINE", "SPLINE"):
            P = [(v.x, v.y) for v in dxfpath.make_path(e).flattening(0.01)]
        else:
            continue
        P = [(round(x - ox, 3), round(-(y - oy), 3)) for x, y in P]
        if len(P) > 1 and P[0] != P[-1] or len(P) > 2:
            pieces.append(P)
    # join pieces end to end
    key = lambda p: (round(p[0], 2), round(p[1], 2))
    ends = {}
    for i, P in enumerate(pieces):
        for j in (0, -1):
            ends.setdefault(key(P[j]), []).append(i)
    used = [False] * len(pieces)
    chains = []
    for i in range(len(pieces)):
        if used[i]:
            continue
        used[i] = True
        C = list(pieces[i])
        for side in (1, 0):                     # grow from the end, then from the start
            while True:
                k = key(C[-1] if side else C[0])
                nxt = [j for j in ends.get(k, []) if not used[j]]
                if not nxt:
                    break
                j = nxt[0]
                used[j] = True
                P = pieces[j]
                if key(P[0]) != k:
                    P = P[::-1]
                C = C + P[1:] if side else P[::-1][:-1] + C
        chains.append(C)
    out = [np.round(rdp(np.array(C, float), a.eps), 2).tolist() for C in chains]
    json.dump({"source": a.dxf.split("/")[-1], "layer": a.layer, "origin_cad": [ox, oy], "units": "mm, y down",
               "polylines": out}, open(a.out, "w"), separators=(",", ":"))
    print(len(pieces), "pieces ->", len(out), "polylines,", sum(len(c) for c in out), "points")


if __name__ == "__main__":
    main()
