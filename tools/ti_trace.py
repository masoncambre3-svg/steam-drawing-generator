"""Pull the outline drawing off a TI sheet as clean vector geometry.

The handbook PDFs carry the TI outline drawings as vector linework. This reads
the strokes inside a region of a page, keeps the product outline and its
internal detail, drops dimension lines and lettering, and works out the filled
silhouette. Result is plain geometry in PDF points that symbols.py then maps to
real dimensions.
"""
import json, math, sys
import numpy as np, cv2, pymupdf

PX = 10            # raster px per pdf point, used only to find the silhouette


def bez(p0, p1, p2, p3, n=14):
    t = np.linspace(0, 1, n)[:, None]
    return ((1-t)**3)*p0 + 3*((1-t)**2)*t*p1 + 3*(1-t)*t*t*p2 + (t**3)*p3


def to_segs(d):
    """A pymupdf drawing -> list of segments ('l', a, b) / ('c', a, b, c, d) as float tuples."""
    out = []
    for it in d["items"]:
        k = it[0]
        if k == "l":
            out.append(("l", tuple(it[1]), tuple(it[2])))
        elif k == "c":
            out.append(("c", tuple(it[1]), tuple(it[2]), tuple(it[3]), tuple(it[4])))
        elif k == "re":
            r = it[1]
            c = [(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)]
            out += [("l", c[i], c[(i+1) % 4]) for i in range(4)]
        elif k == "qu":
            q = it[1]
            c = [tuple(q.ul), tuple(q.ur), tuple(q.lr), tuple(q.ll)]
            out += [("l", c[i], c[(i+1) % 4]) for i in range(4)]
    return out


def flat(seg):
    if seg[0] == "l":
        return np.array([seg[1], seg[2]], float)
    return bez(*[np.array(p, float) for p in seg[1:]])


def _dash_first(d):
    """First dash length and phase of a stroke's dash pattern, or None for a solid stroke."""
    ds = d.get("dashes")
    if not ds or ds in ("[] 0", ""):
        return None
    try:
        arr, phase = ds.rsplit("]", 1)
        return float(arr.strip("[ ").split()[0]), float(phase)
    except Exception:
        return (0.0, 0.0)


def collect(pdf, page_no, clip, outline_lw, drop=(), keep_thin=True, inside_frac=0.92,
          keep_fills=False, close=3, min_thin_lw=0.0, extra_outline=(), max_lw=9.0, short_dash_solid=False, ignore_dash=False):
    """clip/drop boxes are (x0, y0, x1, y1) in pdf points on the page.
    ignore_dash: keep every stroke whatever its dash pattern (sheets that leave a centre-line dash set on the
    whole outline and still print it solid, e.g. TI-P207-10-US); drop real centre lines with drop boxes."""
    page = pymupdf.open(pdf)[page_no - 1]
    x0, y0, x1, y1 = clip
    W, H = int((x1-x0)*PX), int((y1-y0)*PX)
    thick, thin, fills = [], [], []
    def inside(bb, b):
        return bb[0] >= b[0] and bb[2] <= b[2] and bb[1] >= b[1] and bb[3] <= b[3]

    for d in page.get_drawings():
        lw = d.get("width") or 0
        if lw > max_lw:
            continue                                   # heavy dimension lines
        dash = None if ignore_dash else _dash_first(d)
        if dash and not short_dash_solid:
            continue                                   # centre lines, hidden lines
        stroked = d["type"] in ("s", "fs") and d.get("color") is not None
        if not stroked:
            continue
        # one PDF path can hold several separate pieces, even from different views: split them
        chains, cur = [], []
        for sg in to_segs(d):
            if cur and (abs(sg[1][0]-cur[-1][-1][0]) > 0.02 or abs(sg[1][1]-cur[-1][-1][1]) > 0.02):
                chains.append(cur); cur = []
            cur.append(sg)
        if cur:
            chains.append(cur)
        for segs in chains:
            P = np.vstack([np.array(sg[1:], float) for sg in segs])
            bb = (P[:, 0].min(), P[:, 1].min(), P[:, 0].max(), P[:, 1].max())
            if not inside(bb, (x0-0.5, y0-0.5, x1+0.5, y1+0.5)):
                continue
            if any(inside(bb, b) for b in drop):
                continue
            if dash:
                # Some sheets leave a dash pattern set on ordinary outline strokes. A piece shorter than the
                # first dash, starting at phase 0, prints solid: keep it. Anything else is a real dashed line.
                L = sum(float(np.hypot(*np.diff(flat(sg), axis=0).T).sum()) for sg in segs)
                if dash[1] != 0 or L > dash[0]:
                    continue
            if lw >= outline_lw or any(inside(bb, b) for b in extra_outline):
                thick.append((lw, segs))
            elif lw >= min_thin_lw:
                thin.append((lw, segs))
    return thick, thin




def trace(pdf, page_no, clip, outline_lw, drop=(), keep_thin=True, inside_frac=0.92,
          keep_fills=False, close=3, min_thin_lw=0.0, extra_outline=(), max_lw=9.0):
    thick, thin = collect(pdf, page_no, clip, outline_lw, drop, keep_thin, inside_frac, keep_fills, close,
                          min_thin_lw, extra_outline, max_lw)
    return assemble(thick, thin, clip, keep_thin, inside_frac, close)


def assemble(thick, thin, clip, keep_thin=True, inside_frac=0.92, close=3, px=None):
    PX = px or globals()['PX']
    x0, y0, x1, y1 = clip
    W, H = int((x1-x0)*PX), int((y1-y0)*PX)

    def pts_px(seg):
        return ((flat(seg) - (x0, y0)) * PX)

    img = np.zeros((H, W), np.uint8)
    for lw, segs in thick:
        for s in segs:
            cv2.polylines(img, [np.round(pts_px(s)).astype(np.int32)], False, 255, max(1, int(round(lw*PX))))
    k = np.ones((close*2+1, close*2+1), np.uint8)
    wall = cv2.dilate(img, k)
    ff = wall.copy()
    cv2.floodFill(ff, np.zeros((H+2, W+2), np.uint8), (0, 0), 128)
    sil = np.where(ff == 128, 0, 255).astype(np.uint8)
    sil = cv2.erode(sil, k)                              # undo the dilation
    sil = cv2.bitwise_or(sil, img)
    inner = cv2.erode(sil, np.ones((3, 3), np.uint8))

    kept = []
    if keep_thin:
        for lw, segs in thin:
            P = np.vstack([pts_px(s) for s in segs])
            # sample along each segment
            samp = []
            for s in segs:
                f = flat(s) if s[0] == "c" else np.linspace(np.array(s[1]), np.array(s[2]), 12)
                samp.append((f - (x0, y0)) * PX)
            S = np.round(np.vstack(samp)).astype(int)
            S[:, 0] = np.clip(S[:, 0], 0, W-1); S[:, 1] = np.clip(S[:, 1], 0, H-1)
            if inner[S[:, 1], S[:, 0]].mean() / 255 >= inside_frac:
                kept.append((lw, segs))

    cs, _ = cv2.findContours(sil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    polys = []
    for c in cs:
        if cv2.contourArea(c) < (PX*2)**2:
            continue
        c = cv2.approxPolyDP(c, 0.6, True)[:, 0, :].astype(float)
        polys.append((c / PX + (x0, y0)).round(3).tolist())
    ys, xs = np.nonzero(sil)
    bbox = [x0 + xs.min()/PX, y0 + ys.min()/PX, x0 + (xs.max()+1)/PX, y0 + (ys.max()+1)/PX]

    def ser(items):
        return [[round(lw, 3), [[s[0]] + [[round(a, 3), round(b, 3)] for a, b in s[1:]] for s in segs]]
                for lw, segs in items]
    return {"fill": polys, "outline": ser(thick), "detail": ser(kept), "bbox": [round(v, 2) for v in bbox]}


def preview(g, path, scale=6, grid=10):
    """Quick PNG of traced geometry with a labelled grid in pdf points."""
    bx0, by0, bx1, by1 = g["bbox"]
    m = 14
    ox, oy = bx0 - m, by0 - m
    W, H = int((bx1-bx0+2*m)*scale), int((by1-by0+2*m)*scale)
    im = np.full((H, W, 3), 255, np.uint8)
    T = lambda p: ((np.array(p, float) - (ox, oy)) * scale)
    for poly in g["fill"]:
        cv2.fillPoly(im, [np.round(T(poly)).astype(np.int32)], (235, 170, 90))
    for key, col in (("outline", (60, 30, 10)), ("detail", (60, 30, 10))):
        for lw, segs in g[key]:
            for s in segs:
                f = flat((s[0],) + tuple(tuple(p) for p in s[1:]))
                cv2.polylines(im, [np.round(T(f)).astype(np.int32)], False, col, max(1, int(lw*scale*0.9)), cv2.LINE_AA)
    gx = math.ceil(ox/grid)*grid
    while gx < ox + W/scale:
        x = int((gx-ox)*scale); cv2.line(im, (x, 0), (x, H), (200, 200, 255), 1)
        cv2.putText(im, str(gx), (x+2, 11), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (0, 0, 200), 1); gx += grid
    gy = math.ceil(oy/grid)*grid
    while gy < oy + H/scale:
        y = int((gy-oy)*scale); cv2.line(im, (0, y), (W, y), (200, 200, 255), 1)
        cv2.putText(im, str(gy), (2, y-2), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (0, 0, 200), 1); gy += grid
    cv2.imwrite(path, im)


# ---------------------------------------------------------------- helpers for hand-built geometry
def circle(cx, cy, r):
    k = 0.5522847498 * r
    return [("c", (cx+r, cy), (cx+r, cy+k), (cx+k, cy+r), (cx, cy+r)),
            ("c", (cx, cy+r), (cx-k, cy+r), (cx-r, cy+k), (cx-r, cy)),
            ("c", (cx-r, cy), (cx-r, cy-k), (cx-k, cy-r), (cx, cy-r)),
            ("c", (cx, cy-r), (cx+k, cy-r), (cx+r, cy-k), (cx+r, cy))]


def polyline(pts, closed=False):
    pts = [tuple(map(float, p)) for p in pts]
    segs = [("l", pts[i], pts[i+1]) for i in range(len(pts)-1)]
    if closed:
        segs.append(("l", pts[-1], pts[0]))
    return segs


def union_outline(shapes, clip, smooth=0.5, S=20):
    """shapes: list of closed seg lists. Returns the outline of their union as seg lists."""
    x0, y0, x1, y1 = clip
    W, H = int((x1-x0)*S), int((y1-y0)*S)
    m = np.zeros((H, W), np.uint8)
    for segs in shapes:
        P = np.vstack([flat(s) for s in segs])
        cv2.fillPoly(m, [np.round((P - (x0, y0)) * S).astype(np.int32)], 255)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cs:
        c = cv2.approxPolyDP(c, smooth, True)[:, 0, :].astype(float) / S + (x0, y0)
        out.append(polyline(c.tolist(), closed=True))
    return out
