import sys, pymupdf, numpy as np, cv2
def refgrid(pdf, page, clip, out, zoom=4, grid=10):
    pg = pymupdf.open(pdf)[page-1]
    pm = pg.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), clip=pymupdf.Rect(*clip))
    im = np.frombuffer(pm.samples, np.uint8).reshape(pm.h, pm.w, pm.n)[:, :, :3].copy()
    im = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
    x0, y0 = clip[0], clip[1]
    import math
    gx = math.ceil(x0/grid)*grid
    while gx < clip[2]:
        x = int((gx-x0)*zoom); cv2.line(im, (x, 0), (x, pm.h), (190, 190, 255), 1)
        cv2.putText(im, str(gx), (x+2, 11), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (0, 0, 220), 1); gx += grid
    gy = math.ceil(y0/grid)*grid
    while gy < clip[3]:
        y = int((gy-y0)*zoom); cv2.line(im, (0, y), (pm.w, y), (190, 190, 255), 1)
        cv2.putText(im, str(gy), (2, y-2), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (0, 0, 220), 1); gy += grid
    cv2.imwrite(out, im)
if __name__ == "__main__":
    a = sys.argv
    refgrid(a[1], int(a[2]), tuple(float(v) for v in a[3].split(",")), a[4], float(a[5]) if len(a) > 5 else 4)
