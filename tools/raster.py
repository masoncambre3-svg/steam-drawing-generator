"""Vectorise a raster TI picture, for sheets whose dimension drawing is only an image (UTD52L, TI-P614-04-US).

The vector tracer in ti_trace.py needs strokes from get_drawings(). When the sheet only has a picture this gives a
close second: the dark lines are thinned to one pixel (skimage skeletonize), the pixel chains are walked into
polylines and simplified, and the silhouette comes from the filled outer contour of the picture itself.
Coordinates come back in image pixels; the caller maps them to mm from the TI dimensions.
thresh sets how light a line may be and still be drawn; the UTD52L picture draws some edges in grey, so 170.
Needs scikit-image (pip install scikit-image).
"""
import numpy as np, cv2, pymupdf


def image(pdf, page, xref):
    """The picture with this xref on that page, as an 8-bit grey array."""
    doc = pymupdf.open(pdf)
    pix = pymupdf.Pixmap(doc, xref)
    if pix.n - pix.alpha != 3 or pix.alpha:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    im = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
    return cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)


def crop(gray, box, white=()):
    """box (x0, y0, x1, y1) in image px; white: boxes (image px) painted white first (dimensions, lettering)."""
    g = gray.copy()
    for x0, y0, x1, y1 in white:
        g[y0:y1, x0:x1] = 255
    x0, y0, x1, y1 = box
    return g[y0:y1, x0:x1], (x0, y0)


def polylines(g, origin, thresh=170, min_w=3.0, eps=0.9):
    """Centre lines of the dark lines: [(line width px, Nx2 array of image px)]. Lines thinner than min_w (dimension
    and hatching strays) are left out."""
    from skimage.morphology import skeletonize
    b = (g < thresh).astype(np.uint8)
    sk = skeletonize(b > 0)
    dist = cv2.distanceTransform(b, cv2.DIST_L2, 3)
    pts = set(zip(*np.nonzero(sk)))
    nb = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh = lambda p: [(p[0] + a, p[1] + c) for a, c in nb if (p[0] + a, p[1] + c) in pts]
    nodes = {p for p in pts if len(neigh(p)) != 2}
    used, chains = set(), []

    def walk(a, b):
        path, prev, cur = [a, b], a, b
        while cur not in nodes:
            nx = [q for q in neigh(cur) if q != prev and frozenset((cur, q)) not in used]
            if not nx:
                break
            used.add(frozenset((cur, nx[0])))
            prev, cur = cur, nx[0]
            path.append(cur)
        return path
    for start in list(nodes) + list(pts):                 # open chains from their ends first, then closed loops
        for q in neigh(start):
            e = frozenset((start, q))
            if e not in used:
                used.add(e)
                chains.append(walk(start, q))
    out = []
    for P in chains:
        if len(P) < 3:
            continue
        w = float(np.median([dist[r, c] for r, c in P])) * 2
        if w < min_w:
            continue
        A = np.array([(c, r) for r, c in P], np.float32)
        Q = cv2.approxPolyDP(A.reshape(-1, 1, 2), eps, False)[:, 0, :] + origin
        out.append((w, Q.astype(float)))
    return out


def silhouette(g, origin, thresh=200, close=15, shrink=2, eps=1.0):
    """Filled outer outline of everything darker than thresh: list of Nx2 arrays in image px. close bridges gaps in
    the outline; shrink pulls the edge in from the outer edge of the drawn lines towards their centre."""
    b = (g < thresh).astype(np.uint8) * 255
    b = cv2.morphologyEx(b, cv2.MORPH_CLOSE, np.ones((close, close), np.uint8))
    cs, _ = cv2.findContours(b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    b = cv2.drawContours(np.zeros_like(b), cs, -1, 255, -1)
    if shrink:
        b = cv2.erode(b, np.ones((2 * shrink + 1, 2 * shrink + 1), np.uint8))
    cs, _ = cv2.findContours(b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cs:
        if cv2.contourArea(c) < 400:
            continue
        out.append(cv2.approxPolyDP(c, eps, True)[:, 0, :].astype(float) + origin)
    return out


def extent(g, origin, thresh=90):
    """Outer edges of the dark lines (x0, y0, x1, y1) in image px."""
    ys, xs = np.nonzero(g < thresh)
    return xs.min() + origin[0], ys.min() + origin[1], xs.max() + 1 + origin[0], ys.max() + 1 + origin[1]


def render(pdf, page, rect, px_wide):
    """The page area rect (x0, y0, x1, y1, pt) rendered grey, px_wide pixels across. For pictures that get_images()
    cannot hand back as grey (HM34, TI-2-404-US: a 1-bit image mask), render at about the picture's own resolution."""
    pg = pymupdf.open(pdf)[page - 1]
    z = px_wide / (rect[2] - rect[0])
    pm = pg.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(*rect), colorspace=pymupdf.csGRAY)
    return np.frombuffer(pm.samples, np.uint8).reshape(pm.h, pm.w).copy()
