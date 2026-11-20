// Shapes and steam effects (Mason, 2026-11-20): PowerPoint-style shapes drawn at true scale on the drawing, for things a
// product library can't show: flash steam in a pipe, a plume off a vent, condensate, a box round an area, a callout.
//
// Item: { type: "shape", kind, ...style }
//   Box kinds, placed by centre: x, y, w, h (mm), rot (degrees, any angle), flip (mirrors the content)
//     rect, rbox (rounded), ellipse, callout (+ tail: [x, y], the point the tail points at, in drawing coordinates)
//     wisps (flash steam), plume (steam plume), cloud (steam cloud), drops (condensate droplets), water (water level)
//   Path kinds: pts (drawing coordinates), closed, smooth (curve through the points)
//     line (two points), poly (any number)
//   Style: fill ("" = no fill), stroke ("" = no outline), sw (outline width, mm), dash ("", "dash", "dot"),
//     op (opacity of the whole shape, 0.1-1), z ("back": behind everything, "pipes": over pipes but under products,
//     "front": on top of everything), text / ts (text height, mm) / tc (text colour) for rect, rbox, ellipse, callout,
//     n (how many wisps / puffs / drops) for the effects.
// Effects are drawn from w, h and n only (no randomness), so a shape looks the same every time it is drawn.
const SHAPE_BASIC = [["rect", "Rectangle"], ["rbox", "Rounded box"], ["ellipse", "Oval"], ["callout", "Callout"], ["line", "Line"], ["poly", "Polyline"]];
const SHAPE_FX = [["wisps", "Flash steam"], ["plume", "Steam plume"], ["cloud", "Steam cloud"], ["drops", "Droplets"], ["water", "Water level"]];
const SHAPE_NAME = Object.fromEntries([...SHAPE_BASIC, ...SHAPE_FX]);
const shapeIsPath = k => k === "line" || k === "poly";
const shapeHasText = k => k === "rect" || k === "rbox" || k === "ellipse" || k === "callout";
const SHAPE_N = { wisps: [3, 1, 12], plume: [7, 3, 20], cloud: [9, 5, 24], drops: [6, 1, 40] };      // default, min, max
const SHAPE_LAYERS = [["back", "Behind everything"], ["pipes", "Over pipes"], ["front", "In front"]];
const SHAPE_DEF = {
  rect:    { w: 160, h: 100, fill: "", stroke: "#1f3f73", sw: 1.5, dash: "", op: 1, z: "front" },
  rbox:    { w: 160, h: 100, fill: "", stroke: "#1f3f73", sw: 1.5, dash: "", op: 1, z: "front" },
  ellipse: { w: 140, h: 100, fill: "", stroke: "#1f3f73", sw: 1.5, dash: "", op: 1, z: "front" },
  callout: { w: 150, h: 70, fill: "#ffffff", stroke: "#1f3f73", sw: 1.2, dash: "", op: 1, z: "front", text: "Note", ts: 12, tc: "#13233b" },
  line:    { fill: "", stroke: "#1f3f73", sw: 1.5, dash: "", op: 1, z: "front" },
  poly:    { fill: "", stroke: "#1f3f73", sw: 1.5, dash: "", op: 1, z: "front", closed: false, smooth: false },
  wisps:   { w: 70, h: 130, fill: "#ffffff", stroke: "#8d99a8", sw: 0.8, dash: "", op: 0.95, z: "front", n: 3 },
  plume:   { w: 130, h: 220, fill: "#f2f4f7", stroke: "#8d99a8", sw: 0.8, dash: "", op: 0.9, z: "front", n: 7 },
  cloud:   { w: 170, h: 100, fill: "#f2f4f7", stroke: "#8d99a8", sw: 0.8, dash: "", op: 0.9, z: "front", n: 9 },
  drops:   { w: 60, h: 80, fill: "#4a9be0", stroke: "#1f5fae", sw: 0.6, dash: "", op: 1, z: "front", n: 6 },
  water:   { w: 220, h: 18, fill: "#4a9be0", stroke: "#1f5fae", sw: 0.6, dash: "", op: 0.6, z: "pipes" },
};
const SHAPE_STYLE_KEYS = ["fill", "stroke", "sw", "dash", "op", "z", "closed", "smooth", "n", "text", "ts", "tc"];

const _f = v => +(+v).toFixed(2);
const _deg = Math.PI / 180;
// local (unflipped, unrotated, centred) <-> drawing coordinates, for box kinds
function shapeToWorld(it) { const c = Math.cos(it.rot * _deg), s = Math.sin(it.rot * _deg); return p => [it.x + p[0] * c - p[1] * s, it.y + p[0] * s + p[1] * c]; }
function shapeToLocal(it) { const c = Math.cos(it.rot * _deg), s = Math.sin(it.rot * _deg); return p => { const x = p[0] - it.x, y = p[1] - it.y; return [x * c + y * s, -x * s + y * c]; }; }
function shapeCorners(it) { const T = shapeToWorld(it), a = it.w / 2, b = it.h / 2; return [[-a, -b], [a, -b], [a, b], [-a, b]].map(T); }
function shapeBox(it) {
  let P, m;
  if (shapeIsPath(it.kind)) { P = it.pts; m = (it.sw || 1) / 2 + 1; }
  else { P = shapeCorners(it); if (it.kind === "callout" && it.tail) P = [...P, it.tail]; m = (it.sw || 0) + 1; }
  return [Math.min(...P.map(p => p[0])) - m, Math.min(...P.map(p => p[1])) - m, Math.max(...P.map(p => p[0])) + m, Math.max(...P.map(p => p[1])) + m];
}
const shapeCentre = it => { if (!shapeIsPath(it.kind)) return [it.x, it.y]; const b = shapeBox(it); return [(b[0] + b[2]) / 2, (b[1] + b[3]) / 2]; };

// path through points: straight, or a smooth curve (Catmull-Rom as cubic Beziers)
function shapePathD(P, closed, smooth) {
  if (!P.length) return "";
  if (!smooth || P.length < 3) return "M" + P.map(p => `${_f(p[0])},${_f(p[1])}`).join("L") + (closed ? "Z" : "");
  const n = P.length, at = i => closed ? P[(i + n) % n] : P[Math.max(0, Math.min(n - 1, i))];
  let d = `M${_f(P[0][0])},${_f(P[0][1])}`;
  for (let i = 0; i < (closed ? n : n - 1); i++) {
    const p0 = at(i - 1), p1 = at(i), p2 = at(i + 1), p3 = at(i + 2);
    d += `C${_f(p1[0] + (p2[0] - p0[0]) / 6)},${_f(p1[1] + (p2[1] - p0[1]) / 6)} ${_f(p2[0] - (p3[0] - p1[0]) / 6)},${_f(p2[1] - (p3[1] - p1[1]) / 6)} ${_f(p2[0])},${_f(p2[1])}`;
  }
  return d + (closed ? "Z" : "");
}
function shapeDash(it) {
  const w = it.sw || 1;
  return it.dash === "dash" ? ` stroke-dasharray="${_f(w * 4)} ${_f(w * 3)}"` : it.dash === "dot" ? ` stroke-dasharray="${_f(w * 0.05)} ${_f(w * 2.2)}"` : "";
}
const _paint = (it, wide) => `fill="${it.fill || "none"}" stroke="${it.stroke || "none"}" stroke-width="${_f((it.sw || 1) * (wide || 1))}" stroke-linejoin="round" stroke-linecap="round"${shapeDash(it)}`;
const _N = it => { const q = SHAPE_N[it.kind]; return q ? Math.max(q[1], Math.min(q[2], Math.round(it.n || q[0]))) : 0; };

// pieces drawn with the outline under the fill, so overlapping puffs read as one outline (union look)
function _union(it, pieces) {
  const sw = it.stroke ? `<g fill="none" stroke="${it.stroke}" stroke-width="${_f((it.sw || 1) * 2)}" stroke-linejoin="round"${shapeDash(it)}>${pieces.join("")}</g>` : "";
  return sw + `<g fill="${it.fill || "#ffffff"}" stroke="none">${pieces.join("")}</g>`;
}
const _circle = (x, y, r) => `<circle cx="${_f(x)}" cy="${_f(y)}" r="${_f(r)}"/>`;

// the content of a box shape in its local frame (centred on 0,0)
function shapeBody(it) {
  const w = it.w, h = it.h, a = w / 2, b = h / 2;
  switch (it.kind) {
    case "rect": return `<rect x="${_f(-a)}" y="${_f(-b)}" width="${_f(w)}" height="${_f(h)}" ${_paint(it)}/>`;
    case "rbox": { const r = _f(Math.min(w, h) * 0.18); return `<rect x="${_f(-a)}" y="${_f(-b)}" width="${_f(w)}" height="${_f(h)}" rx="${r}" ry="${r}" ${_paint(it)}/>`; }
    case "ellipse": return `<ellipse cx="0" cy="0" rx="${_f(a)}" ry="${_f(b)}" ${_paint(it)}/>`;
    case "wisps": {                                         // tapered ribbons rising from the bottom edge, curling as they go
      const n = _N(it), cell = w / n, out = [];
      for (let i = 0; i < n; i++) {
        const x0 = -a + (i + 0.5) * cell, ph = i * 2.1 + 0.6, top = 0.72 + 0.28 * ((i * 0.618 + 0.3) % 1);
        const A = Math.min(cell * 0.28, h * 0.12), W0 = Math.min(cell * 0.27, h * 0.08), L = [], R = [], S = 30;
        const cx = t => x0 + A * Math.sin(2 * Math.PI * 1.15 * t + ph) * (0.35 + 0.65 * t), cy = t => b - t * h * top;
        for (let k = 0; k <= S; k++) {
          const t = k / S, dx = cx(t + 0.001) - cx(t), dy = cy(t + 0.001) - cy(t), l = Math.hypot(dx, dy) || 1;
          const hw = W0 * Math.pow(1 - t, 0.85) + W0 * 0.06, nx = -dy / l, ny = dx / l;
          L.push([cx(t) + nx * hw, cy(t) + ny * hw]); R.push([cx(t) - nx * hw, cy(t) - ny * hw]);
        }
        out.push(`<path d="${shapePathD([...L, ...R.reverse()], true, false)}" ${_paint(it)}/>`);
      }
      return out.join("");
    }
    case "plume": {                                         // puffs growing from a small one at the bottom to a full head at the top
      const n = _N(it), rb = Math.min(w * 0.14, h * 0.08), rt = Math.min(w * 0.42, h * 0.28), P = [];
      for (let k = 0; k < n; k++) {
        const t = n > 1 ? k / (n - 1) : 1, r = rb + (rt - rb) * t, y = b - rb - t * (h - rb - rt), side = k % 2 ? 1 : -1;
        P.push(_circle(side * (a - r) * 0.3 * t, y, r));
      }
      const rs = rt * 0.72; P.push(_circle(-(a - rs), -b + rt * 1.15, rs), _circle(a - rs, -b + rt * 1.05, rs));
      return _union(it, P);
    }
    case "cloud": {                                         // puffs round an oval, with the oval filled in
      const n = _N(it), R = Math.min(w, h) * 0.24, ea = Math.max(1, a - R), eb = Math.max(1, b - R), P = [`<ellipse cx="0" cy="0" rx="${_f(ea)}" ry="${_f(eb)}"/>`];
      for (let k = 0; k < n; k++) { const t = 2 * Math.PI * k / n - Math.PI / 2, r = R * (0.8 + 0.2 * ((k * 0.618) % 1)); P.push(_circle(ea * Math.cos(t), eb * Math.sin(t), r)); }
      return _union(it, P);
    }
    case "drops": {                                         // teardrops in a staggered grid, each with a highlight
      const n = _N(it), cols = Math.max(1, Math.min(n, Math.round(Math.sqrt(n * w / h)))), rows = Math.ceil(n / cols);
      const cw = w / cols, ch = h / rows, s = Math.min(cw / 1.2, ch / 1.85) * 0.82, out = [];
      for (let k = 0; k < n; k++) {
        const r = Math.floor(k / cols), c = k % cols, inRow = Math.min(cols, n - r * cols), off = (cols - inRow) * cw / 2;
        const x = -a + off + (c + 0.5) * cw + (inRow === cols && cols > 1 ? (r % 2 ? 0.08 : -0.08) * cw : 0);   // rows staggered a little
        const y = -b + (r + 0.5) * ch - s * 0.07;
        out.push(`<g transform="translate(${_f(x)} ${_f(y)})"><path d="M0,${_f(-s)}C${_f(0.35 * s)},${_f(-0.45 * s)} ${_f(0.6 * s)},${_f(-0.05 * s)} ${_f(0.6 * s)},${_f(0.25 * s)}` +
          `A${_f(0.6 * s)},${_f(0.6 * s)} 0 1 1 ${_f(-0.6 * s)},${_f(0.25 * s)}C${_f(-0.6 * s)},${_f(-0.05 * s)} ${_f(-0.35 * s)},${_f(-0.45 * s)} 0,${_f(-s)}Z" ${_paint(it)}/>` +
          `<ellipse cx="${_f(-0.22 * s)}" cy="${_f(0.3 * s)}" rx="${_f(0.11 * s)}" ry="${_f(0.2 * s)}" fill="#ffffff" fill-opacity="0.55"/></g>`);
      }
      return out.join("");
    }
    case "water": {                                         // a box with a wavy top: the liquid surface
      const amp = Math.min(h * 0.15, 3), L = Math.max(12, Math.min(60, h * 2.5)), m = Math.max(1, Math.round(w / L)), hw = w / m / 2, y0 = -b + amp;
      let d = `M${_f(-a)},${_f(y0)}`;
      for (let k = 0; k < 2 * m; k++) { const x = -a + k * hw; d += `Q${_f(x + hw / 2)},${_f(y0 + (k % 2 ? 2 : -2) * amp)} ${_f(x + hw)},${_f(y0)}`; }
      return `<path d="${d}L${_f(a)},${_f(b)}L${_f(-a)},${_f(b)}Z" ${_paint(it)}/>`;
    }
  }
  return "";
}
// callout: rounded box and a tail toward it.tail, drawn as one outline
function shapeCallout(it) {
  const w = it.w, h = it.h, a = w / 2, b = h / 2, r = Math.min(w, h) * 0.15, box = `<rect x="${_f(-a)}" y="${_f(-b)}" width="${_f(w)}" height="${_f(h)}" rx="${_f(r)}" ry="${_f(r)}"/>`;
  const t = it.tail ? shapeToLocal(it)(it.tail) : null, P = [box];
  if (t && (Math.abs(t[0]) > a || Math.abs(t[1]) > b)) {
    const side = Math.abs(t[0]) / a > Math.abs(t[1]) / b, inset = (it.sw || 1) * 2 + 0.5;
    if (side) { const sx = Math.sign(t[0]), bw = Math.min(h * 0.2, w * 0.15), y0 = Math.max(-b + r + bw, Math.min(b - r - bw, t[1] * 0.3)), ex = sx * (a - inset);
      P.push(`<path d="M${_f(ex)},${_f(y0 - bw)}L${_f(t[0])},${_f(t[1])}L${_f(ex)},${_f(y0 + bw)}Z"/>`); }
    else { const sy = Math.sign(t[1]), bw = Math.min(w * 0.12, h * 0.25), x0 = Math.max(-a + r + bw, Math.min(a - r - bw, t[0] * 0.3)), ey = sy * (b - inset);
      P.push(`<path d="M${_f(x0 - bw)},${_f(ey)}L${_f(t[0])},${_f(t[1])}L${_f(x0 + bw)},${_f(ey)}Z"/>`); }
  }
  if (!it.fill) return `<g ${_paint(it)}>${P.join("")}</g>`;      // no fill: plain outlines (the tail's base line shows)
  return _union(it, P);
}
function shapeText(it, wrap) {
  if (!shapeHasText(it.kind) || !it.text) return "";
  const ts = it.ts || 12, lines = wrap(it.text, ts, Math.max(ts, it.w * (it.kind === "ellipse" ? 0.72 : 0.9))), y0 = -(lines.length - 1) * ts * 1.25 / 2 + ts * 0.35;
  return `<text x="0" y="${_f(y0)}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="${_f(ts)}" fill="${it.tc || "#13233b"}">` +
    lines.map((l, i) => `<tspan x="0" dy="${i ? _f(ts * 1.25) : 0}">${String(l).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])) || " "}</tspan>`).join("") + `</text>`;
}
// the whole shape; wrap(text, size, width) -> lines. data-id makes it clickable in the editor.
function shapeSvg(it, wrap) {
  const id = it.id ? ` data-id="${it.id}"` : "", op = it.op < 1 ? ` opacity="${_f(Math.max(0.05, it.op))}"` : "", hitW = _f(Math.max((it.sw || 1) * 4, 6));
  if (shapeIsPath(it.kind)) {
    const closed = it.kind === "poly" && it.closed, d = shapePathD(it.pts, closed, it.kind === "poly" && it.smooth);
    const p = Object.assign({}, it, { fill: closed ? it.fill : "" });
    return `<g${id}${op}><path d="${d}" ${_paint(p)}/><path d="${d}" fill="none" stroke="transparent" stroke-width="${hitW}"/></g>`;
  }
  const body = it.kind === "callout" ? shapeCallout(it) : shapeBody(it);
  // no fill: the inside is still clickable (data-inner: the editor lets anything underneath win; Mason, 2026-11-20)
  const hit = it.fill || ["wisps", "plume", "cloud", "drops", "water"].includes(it.kind) ? "" :
    it.kind === "ellipse" ? `<ellipse data-inner="1" cx="0" cy="0" rx="${_f(it.w / 2)}" ry="${_f(it.h / 2)}" fill="transparent" stroke="none"/>` +
      `<ellipse cx="0" cy="0" rx="${_f(it.w / 2)}" ry="${_f(it.h / 2)}" fill="none" stroke="transparent" stroke-width="${hitW}"/>` :
    `<rect data-inner="1" x="${_f(-it.w / 2)}" y="${_f(-it.h / 2)}" width="${_f(it.w)}" height="${_f(it.h)}" fill="transparent" stroke="none"/>` +
    `<rect x="${_f(-it.w / 2)}" y="${_f(-it.h / 2)}" width="${_f(it.w)}" height="${_f(it.h)}" fill="none" stroke="transparent" stroke-width="${hitW}"/>`;
  return `<g${id}${op} transform="translate(${_f(it.x)} ${_f(it.y)}) rotate(${_f(it.rot || 0)})">` +
    (it.flip && it.kind !== "callout" ? `<g transform="scale(-1 1)">${body}</g>` : body) + hit + shapeText(it, wrap) + `</g>`;
}

// ---- selection handles: 8 to resize, one to turn, one for a callout's tail; a path gets one per point
const SHAPE_SIGNS = [[-1, -1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0]];
const SHAPE_CURSOR = ["nwse-resize", "ns-resize", "nesw-resize", "ew-resize", "nwse-resize", "ns-resize", "nesw-resize", "ew-resize"];
function shapeSelSvg(it, px) {
  const sq = (p, k, cur) => `<rect data-h="${k}" x="${_f(p[0] - 5 * px)}" y="${_f(p[1] - 5 * px)}" width="${_f(10 * px)}" height="${_f(10 * px)}" fill="#fff" stroke="#1f5fae" stroke-width="${_f(1.5 * px)}" style="cursor:${cur}"/>`;
  if (shapeIsPath(it.kind)) {
    const b = shapeBox(it), m = 4 * px;
    return `<rect x="${_f(b[0] - m)}" y="${_f(b[1] - m)}" width="${_f(b[2] - b[0] + 2 * m)}" height="${_f(b[3] - b[1] + 2 * m)}" fill="none" stroke="#1f5fae" stroke-width="${_f(1.5 * px)}" stroke-dasharray="${_f(5 * px)} ${_f(4 * px)}" pointer-events="none"/>` +
      it.pts.map((p, i) => sq(p, i, "move")).join("");
  }
  const T = shapeToWorld(it), a = it.w / 2, b = it.h / 2, C = shapeCorners(it), top = T([0, -b]), rot = T([0, -b - 22 * px]);
  let o = `<polygon points="${C.map(p => `${_f(p[0])},${_f(p[1])}`).join(" ")}" fill="none" stroke="#1f5fae" stroke-width="${_f(1.5 * px)}" stroke-dasharray="${_f(5 * px)} ${_f(4 * px)}" pointer-events="none"/>` +
    `<line x1="${_f(top[0])}" y1="${_f(top[1])}" x2="${_f(rot[0])}" y2="${_f(rot[1])}" stroke="#1f5fae" stroke-width="${_f(1.5 * px)}" pointer-events="none"/>` +
    `<circle data-h="rot" cx="${_f(rot[0])}" cy="${_f(rot[1])}" r="${_f(6 * px)}" fill="#fff" stroke="#1f5fae" stroke-width="${_f(1.5 * px)}" style="cursor:grab"><title>Drag to turn. Shift: 15° steps</title></circle>`;
  SHAPE_SIGNS.forEach((s, k) => { o += sq(T([s[0] * a, s[1] * b]), k, SHAPE_CURSOR[k]); });
  if (it.kind === "callout" && it.tail) { const q = it.tail;
    o += `<path data-h="tail" d="M${_f(q[0])},${_f(q[1] - 7 * px)}L${_f(q[0] + 7 * px)},${_f(q[1])}L${_f(q[0])},${_f(q[1] + 7 * px)}L${_f(q[0] - 7 * px)},${_f(q[1])}Z" fill="#e9c53c" stroke="#1f5fae" stroke-width="${_f(1.5 * px)}" style="cursor:move"><title>Drag to point the callout</title></path>`; }
  return o;
}
// drag handle k of shape it (o = the shape as it was when the drag began) to drawing point p.
// snap(p) rounds a point to the grid; shift keeps proportions (corners), 15° steps (turn, path points); alt: no grid
function shapeDragHandle(it, o, k, p, shift, alt, snap) {
  const q = alt ? [Math.round(p[0] * 10) / 10, Math.round(p[1] * 10) / 10] : snap(p);
  if (shapeIsPath(it.kind)) {
    const i = +k, nb = o.pts[i === 0 ? 1 : i - 1];
    let v = q;
    if (shift && nb) { const L = Math.hypot(p[0] - nb[0], p[1] - nb[1]), t = Math.round(Math.atan2(p[1] - nb[1], p[0] - nb[0]) / (15 * _deg)) * 15 * _deg; v = [_f(nb[0] + L * Math.cos(t)), _f(nb[1] + L * Math.sin(t))]; }
    it.pts = o.pts.map((pt, j) => j === i ? v : pt); return;
  }
  if (k === "tail") { it.tail = alt ? q : [Math.round(p[0]), Math.round(p[1])]; return; }
  if (k === "rot") {
    let ang = Math.atan2(p[1] - o.y, p[0] - o.x) / _deg + 90;
    ang = shift ? Math.round(ang / 15) * 15 : Math.round(ang);
    it.rot = ((ang % 360) + 360) % 360; return;
  }
  const s = SHAPE_SIGNS[+k], L = shapeToLocal(o)(p), MIN = 2;
  const ax = -s[0] * o.w / 2, ay = -s[1] * o.h / 2;           // the opposite side or corner stays put
  let w = s[0] ? Math.max(MIN, s[0] * (L[0] - ax)) : o.w, h = s[1] ? Math.max(MIN, s[1] * (L[1] - ay)) : o.h;
  if (!alt) { w = Math.max(MIN, Math.round(w)); h = Math.max(MIN, Math.round(h)); }
  if (shift && s[0] && s[1]) { const f = Math.max(w / o.w, h / o.h); w = _f(o.w * f); h = _f(o.h * f); }
  const lc = [s[0] ? ax + s[0] * w / 2 : 0, s[1] ? ay + s[1] * h / 2 : 0], c = shapeToWorld(o)(lc);
  it.w = _f(w); it.h = _f(h); it.x = _f(c[0]); it.y = _f(c[1]);
}
// turn by deg about the shape's centre (or about c, for a group turn: then the centre moves too)
function shapeTurn(it, deg, c) {
  const cc = c || shapeCentre(it), co = Math.cos(deg * _deg), si = Math.sin(deg * _deg);
  const R = p => [_f(cc[0] + (p[0] - cc[0]) * co - (p[1] - cc[1]) * si), _f(cc[1] + (p[0] - cc[0]) * si + (p[1] - cc[1]) * co)];
  if (shapeIsPath(it.kind)) { it.pts = it.pts.map(R); return; }
  [it.x, it.y] = R([it.x, it.y]); if (it.tail) it.tail = R(it.tail);
  it.rot = (((it.rot || 0) + deg) % 360 + 360) % 360;
}
function shapeMirror(it) {
  if (shapeIsPath(it.kind)) { const c = shapeCentre(it); it.pts = it.pts.map(p => [_f(2 * c[0] - p[0]), p[1]]); return; }
  if (it.tail) { const L = shapeToLocal(it)(it.tail); it.tail = shapeToWorld(it)([-L[0], L[1]]).map(_f); }
  it.flip = !it.flip;
}
// a new shape of kind k with style st: a box from corner a to corner b (a click: the kind's default size centred on a),
// or a line from a to b
function shapeNew(k, st, a, b, shift) {
  const D = SHAPE_DEF[k], it = Object.assign({ type: "shape", kind: k }, JSON.parse(JSON.stringify(D)), JSON.parse(JSON.stringify(st || {})));
  delete it.w; delete it.h;
  const dx = b[0] - a[0], dy = b[1] - a[1], tiny = Math.abs(dx) < 3 && Math.abs(dy) < 3;
  if (shapeIsPath(k)) {
    let e = tiny ? [a[0] + 150, a[1]] : b;
    if (shift && !tiny) { const L = Math.hypot(dx, dy), t = Math.round(Math.atan2(dy, dx) / (15 * _deg)) * 15 * _deg; e = [_f(a[0] + L * Math.cos(t)), _f(a[1] + L * Math.sin(t))]; }
    it.pts = [a, e]; return it;
  }
  let w = tiny ? D.w : Math.abs(dx), h = tiny ? D.h : Math.abs(dy);
  if (shift && !tiny) w = h = Math.max(w, h);
  const cx = tiny ? a[0] : a[0] + Math.sign(dx || 1) * w / 2, cy = tiny ? a[1] : a[1] + Math.sign(dy || 1) * h / 2;
  Object.assign(it, { x: _f(cx), y: _f(cy), w: _f(w), h: _f(h), rot: 0, flip: false });
  if (k === "callout") it.tail = [Math.round(cx - w * 0.35), Math.round(cy + h / 2 + Math.max(25, h * 0.6))];
  return it;
}
