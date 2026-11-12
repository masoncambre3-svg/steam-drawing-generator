// Steam Drawing Generator: the editor. Product drawings live in /products, one pack file per product.
// Product library: assembled from the pack files under /products (see app/loader.js)
const LIB = { families: [...SDG.families], products: [], symbols: {} };
for (const pack of SDG.packs) {
  if (!LIB.families.includes(pack.product.family)) LIB.families.push(pack.product.family);
  LIB.products.push(pack.product); Object.assign(LIB.symbols, pack.symbols);
}
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
// ASME B36.10 pipe: outside diameter and wall for schedule 40 and 80, mm
const PIPE = { '1/4"': [13.7, 2.24, 3.02], '3/8"': [17.1, 2.31, 3.20], '1/2"': [21.3, 2.77, 3.73], '3/4"': [26.7, 2.87, 3.91],
  '1"': [33.4, 3.38, 4.55], '1-1/4"': [42.2, 3.56, 4.85], '1-1/2"': [48.3, 3.68, 5.08], '2"': [60.3, 3.91, 5.54],
  '2-1/2"': [73.0, 5.16, 7.01], '3"': [88.9, 5.49, 7.62], '4"': [114.3, 6.02, 8.56], '5"': [141.3, 6.55, 9.53],
  '6"': [168.3, 7.11, 10.97], '8"': [219.1, 8.18, 12.70], '10"': [273.0, 9.27, 15.09], '12"': [323.8, 10.31, 17.48] };
// ASME B16.9 butt-weld fittings, mm: long-radius 90 elbow centre to end, tee centre to end, reducer length (by large end)
const ELBOW = { '1/2"': 38, '3/4"': 38, '1"': 38, '1-1/4"': 48, '1-1/2"': 57, '2"': 76, '2-1/2"': 95, '3"': 114, '4"': 152, '5"': 190, '6"': 229, '8"': 305, '10"': 381, '12"': 457 };
const TEE = { '1/2"': 25, '3/4"': 29, '1"': 38, '1-1/4"': 48, '1-1/2"': 57, '2"': 64, '2-1/2"': 76, '3"': 86, '4"': 105, '5"': 124, '6"': 143, '8"': 178, '10"': 216, '12"': 254 };
const REDH = { '3/4"': 38, '1"': 51, '1-1/4"': 51, '1-1/2"': 64, '2"': 76, '2-1/2"': 89, '3"': 89, '4"': 102, '5"': 127, '6"': 140, '8"': 152, '10"': 178, '12"': 203 };
const FSIZES = Object.keys(ELBOW);
const smaller = (size, n) => FSIZES.slice(Math.max(0, FSIZES.indexOf(size) - n), FSIZES.indexOf(size));
LIB.families.push("Fittings");
LIB.products.push(
  { id: "ELBOW90", name: "90° elbow", type: "Long radius, butt weld", ti: "ASME B16.9", family: "Fittings", sizes: FSIZES, variantsFor: () => ["-"], fit: true },
  { id: "TEE", name: "Tee", type: "Straight or reducing, butt weld", ti: "ASME B16.9", family: "Fittings", sizes: FSIZES, variantsFor: s => [s, ...smaller(s, 4).reverse()], variantLabel: "Branch size", fit: true },
  { id: "REDC", name: "Concentric reducer", type: "Butt weld", ti: "ASME B16.9", family: "Fittings", sizes: FSIZES.slice(1), variantsFor: s => smaller(s, 4).reverse(), variantLabel: "Small end", fit: true },
  { id: "REDE", name: "Eccentric reducer", type: "Butt weld, flat on bottom as placed", ti: "ASME B16.9", family: "Fittings", sizes: FSIZES.slice(1), variantsFor: s => smaller(s, 4).reverse(), variantLabel: "Small end", fit: true });
const variantsOf = (p, size) => p.variantsFor ? p.variantsFor(size) : p.variants;
const FITS = {};
function fitGeom(product, size, variant) {
  const od = PIPE[size][0], r = od / 2, lw = 0.5 + od * 0.008, f = v => v.toFixed(2);
  let d, ports, box, dims;
  if (product === "ELBOW90") {
    const R = ELBOW[size];
    d = `M${f(-R)},${f(-r)}A${f(R + r)},${f(R + r)} 0 0 1 ${f(r)},${f(R)}L${f(-r)},${f(R)}` + (R - r > 0.5 ? `A${f(R - r)},${f(R - r)} 0 0 0 ${f(-R)},${f(r)}` : `L${f(-R)},${f(r)}`) + "Z";
    ports = [[-R, 0], [0, R]]; box = [-R, -r, R + r, R + r]; dims = { "Centre to end": R, "Pipe OD": od };
  } else if (product === "TEE") {
    const C = TEE[size], M = TEE[size], rb = PIPE[variant][0] / 2;
    d = `M${f(-C)},${f(-r)}L${f(C)},${f(-r)}L${f(C)},${f(r)}L${f(rb)},${f(r)}L${f(rb)},${f(M)}L${f(-rb)},${f(M)}L${f(-rb)},${f(r)}L${f(-C)},${f(r)}Z`;
    ports = [[-C, 0], [C, 0], [0, M]]; box = [-C, -r, 2 * C, r + M]; dims = { "Run, centre to end": C, "Branch, centre to end": M, "Run OD": od, "Branch OD": rb * 2 };
  } else {
    const H = REDH[size], r2 = PIPE[variant][0] / 2, t = 0.12 * H, ecc = product === "REDE", top2 = ecc ? r - 2 * r2 : -r2, bot2 = ecc ? r : r2;
    d = `M0,${f(-r)}L${f(t)},${f(-r)}L${f(H - t)},${f(top2)}L${f(H)},${f(top2)}L${f(H)},${f(bot2)}` + (ecc ? "" : `L${f(H - t)},${f(bot2)}L${f(t)},${f(r)}`) + `L0,${f(r)}Z`;
    ports = [[0, 0], [H, ecc ? r - r2 : 0]]; box = [0, -r, H, 2 * r]; dims = { "Length": H, "Large end OD": od, "Small end OD": r2 * 2 };
  }
  return { box: [box[0] - lw / 2, box[1] - lw / 2, box[2] + lw, box[3] + lw], fill: d, strokes: [[lw, d]], arrow: null, ports, dims, flat: true };
}
function lookup(key) {
  if (LIB.symbols[key]) return LIB.symbols[key];
  if (FITS[key]) return FITS[key];
  const [product, size, variant] = key.split("|"), p = LIB.products.find(q => q.id === product);
  if (!p || !p.fit || !PIPE[size] || !p.sizes.includes(size) || !variantsOf(p, size).includes(variant)) return null;
  return (FITS[key] = fitGeom(product, size, variant));
}
const NOM = s => s.replace('"', "").split("-").reduce((a, p) => a + (p.includes("/") ? p.split("/")[0] / p.split("/")[1] : +p), 0) * 25.4;
const PRESETS = [["Blue", "#3f86dc"], ["Navy", "#1f3f73"], ["Steel grey", "#8d99a8"], ["Black", "#2a2f36"], ["Red", "#d0473c"],
                 ["Orange", "#e58a2b"], ["Yellow", "#e9c53c"], ["Green", "#3f9a5f"], ["White", "#f2f4f7"]];
const VARIANT_LABEL = { NPT: "NPT", screwed: "Screwed", flanged: "Flanged" };
const GRID = 5;
const BUILD = "5";

let doc = { v: 1, style: { shade: true, blackLines: false }, items: [] };
const ui = { tool: "select", sel: null, draft: null, cursor: null, view: { cx: 0, cy: 0, s: 1.6 },
  pick: { family: "Steam traps", product: "TD52", size: '3/4"', variant: "NPT", color: "#3f86dc", arrow: true },
  pipe: { nps: '3/4"', sch: 80, color: "#8d99a8", label: true, cut: false },
  text: { text: "", size: 14, color: "#13233b" }, arrow: { color: "#13233b" } };
let hist = [], hi = -1, nextId = 1;

// ---------------------------------------------------------------- colour
function hexToHsl(hex) {
  const n = parseInt(hex.slice(1), 16), r = (n >> 16) / 255, g = ((n >> 8) & 255) / 255, b = (n & 255) / 255;
  const mx = Math.max(r, g, b), mn = Math.min(r, g, b), l = (mx + mn) / 2;
  let h = 0, s = 0;
  if (mx !== mn) { const d = mx - mn; s = l > 0.5 ? d / (2 - mx - mn) : d / (mx + mn);
    h = (mx === r ? (g - b) / d + (g < b ? 6 : 0) : mx === g ? (b - r) / d + 2 : (r - g) / d + 4) * 60; }
  return [h, s, l];
}
function hsl(h, s, l) {
  const c = v => Math.max(0, Math.min(1, v)); s = c(s); l = c(l);
  const k = n => (n + h / 30) % 12, a = s * Math.min(l, 1 - l);
  const f = n => Math.round(255 * (l - a * Math.max(-1, Math.min(k(n) - 3, 9 - k(n), 1))));
  return "#" + [f(0), f(8), f(4)].map(v => v.toString(16).padStart(2, "0")).join("");
}
function pal(color) {
  const [h, s, l] = hexToHsl(color), dark = l < 0.3, sh = doc.style.shade;
  return { top: sh ? hsl(h, s, l + 0.12) : color, bot: sh ? hsl(h, s, l - 0.07) : color, mid: color,
    line: doc.style.blackLines ? "#111111" : dark ? hsl(h, Math.min(s, 0.35), 0.82) : hsl(h, Math.min(s + 0.1, 0.7), Math.max(0.12, l * 0.3)),
    arrow: dark ? hsl(h, 0.2, 0.9) : "#f3f8ff", bore: hsl(h, s * 0.5, Math.min(0.95, l + 0.32)) };
}

// ---------------------------------------------------------------- geometry
const symOf = it => lookup(`${it.product}|${it.size}|${it.variant}`);
function symXform(it) {
  const s = symOf(it), cx = s.box[0] + s.box[2] / 2, cy = s.box[1] + s.box[3] / 2;
  const a = it.rot * Math.PI / 180, co = Math.cos(a), si = Math.sin(a), f = it.flip ? -1 : 1;
  return p => { const x = (p[0] - cx) * f, y = p[1] - cy; return [it.x + x * co - y * si, it.y + x * si + y * co]; };
}
const portsOf = it => { const T = symXform(it); return symOf(it).ports.map(T); };
function bboxOf(it) {
  if (it.type === "sym") {
    const s = symOf(it), T = symXform(it), [x, y, w, h] = s.box;
    const c = [[x, y], [x + w, y], [x, y + h], [x + w, y + h]].map(T);
    return [Math.min(...c.map(p => p[0])), Math.min(...c.map(p => p[1])), Math.max(...c.map(p => p[0])), Math.max(...c.map(p => p[1]))];
  }
  if (it.type === "pipe") {
    const r = PIPE[it.nps][0] / 2 + 1;
    return [Math.min(...it.pts.map(p => p[0])) - r, Math.min(...it.pts.map(p => p[1])) - r, Math.max(...it.pts.map(p => p[0])) + r, Math.max(...it.pts.map(p => p[1])) + r];
  }
  if (it.type === "text") {
    const lines = (it.text || " ").split("\n"), w = Math.max(...lines.map(l => l.length), 1) * it.size * 0.56;
    return [it.x, it.y - it.size, it.x + w, it.y + (lines.length - 1) * it.size * 1.25 + it.size * 0.3];
  }
  const m = 3;
  return [Math.min(it.a[0], it.b[0]) - m, Math.min(it.a[1], it.b[1]) - m, Math.max(it.a[0], it.b[0]) + m, Math.max(it.a[1], it.b[1]) + m];
}
function docBox(margin) {
  const live = doc.items.filter(valid);
  if (!live.length) return null;
  const b = live.map(bboxOf);
  return [Math.min(...b.map(v => v[0])) - margin, Math.min(...b.map(v => v[1])) - margin, Math.max(...b.map(v => v[2])) + margin, Math.max(...b.map(v => v[3])) + margin];
}
const valid = it => it.type !== "sym" || !!symOf(it);
function pipePath(pts, nps) {
  if (pts.length < 2) return "";
  const R = ELBOW[nps] || 1.5 * NOM(nps);         // long-radius elbow, centreline
  let d = `M${pts[0][0].toFixed(2)},${pts[0][1].toFixed(2)}`;
  for (let i = 1; i < pts.length; i++) {
    const p = pts[i], q = pts[i + 1];
    if (!q) { d += `L${p[0].toFixed(2)},${p[1].toFixed(2)}`; break; }
    const a = pts[i - 1], l1 = Math.hypot(p[0] - a[0], p[1] - a[1]), l2 = Math.hypot(q[0] - p[0], q[1] - p[1]);
    if (!l1 || !l2) continue;
    const u1 = [(p[0] - a[0]) / l1, (p[1] - a[1]) / l1], u2 = [(q[0] - p[0]) / l2, (q[1] - p[1]) / l2];
    const cross = u1[0] * u2[1] - u1[1] * u2[0], phi = Math.atan2(Math.abs(cross), u1[0] * u2[0] + u1[1] * u2[1]);
    if (phi < 0.02 || phi > 3.1) { d += `L${p[0].toFixed(2)},${p[1].toFixed(2)}`; continue; }
    const tn = Math.tan(phi / 2), t = Math.min(R * tn, l1 / 2, l2 / 2), re = t / tn;
    const e1 = [p[0] - u1[0] * t, p[1] - u1[1] * t], e2 = [p[0] + u2[0] * t, p[1] + u2[1] * t];
    d += `L${e1[0].toFixed(2)},${e1[1].toFixed(2)}A${re.toFixed(2)},${re.toFixed(2)} 0 0 ${cross > 0 ? 1 : 0} ${e2[0].toFixed(2)},${e2[1].toFixed(2)}`;
  }
  return d;
}

// ---------------------------------------------------------------- drawing each item
let gradN = 0;
function symInner(key, color, arrow, rot, flip) {
  const s = lookup(key), p = pal(color), gid = "g" + (++gradN);
  let o = `<defs><linearGradient id="${gid}" x1="0" y1="0" x2="0" y2="1" gradientTransform="rotate(${-rot * (flip ? -1 : 1)} .5 .5)">` +
    `<stop offset="0" stop-color="${p.top}"/><stop offset="1" stop-color="${p.bot}"/></linearGradient></defs><path d="${s.fill}" fill="${s.flat ? p.mid : `url(#${gid})`}"/>`;
  for (const [lw, d] of s.strokes) o += `<path d="${d}" fill="none" stroke="${p.line}" stroke-width="${lw}" stroke-linecap="round" stroke-linejoin="round"/>`;
  if (s.arrow && arrow) o += `<polygon points="${s.arrow[0]}" fill="${p.arrow}" stroke="${p.line}" stroke-width="${s.arrow[1]}" stroke-linejoin="round"/>`;
  return o;
}
function itemSvg(it) {
  const id = `data-id="${it.id}"`;
  if (it.type === "sym") {
    const s = symOf(it), cx = s.box[0] + s.box[2] / 2, cy = s.box[1] + s.box[3] / 2;
    return `<g ${id} transform="translate(${it.x} ${it.y}) rotate(${it.rot}) scale(${it.flip ? -1 : 1} 1) translate(${-cx} ${-cy})">` +
      symInner(`${it.product}|${it.size}|${it.variant}`, it.color, it.arrow, it.rot, it.flip) + `</g>`;
  }
  if (it.type === "pipe") return pipeOutline(it) + pipeBody(it) + pipeLabel(it);
  if (it.type === "text") {
    const lines = (it.text || "Text").split("\n");
    return `<text ${id} x="${it.x}" y="${it.y}" font-family="Arial, Helvetica, sans-serif" font-size="${it.size}" fill="${it.color}">` +
      lines.map((l, i) => `<tspan x="${it.x}" dy="${i ? it.size * 1.25 : 0}">${esc(l) || " "}</tspan>`).join("") + `</text>`;
  }
  const dx = it.b[0] - it.a[0], dy = it.b[1] - it.a[1], L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L, w = it.w || 1.6, h = Math.min(w * 6, L * 0.6);
  const bx = it.b[0] - ux * h, by = it.b[1] - uy * h;
  return `<g ${id}><line x1="${it.a[0]}" y1="${it.a[1]}" x2="${bx}" y2="${by}" stroke="${it.color}" stroke-width="${w}" stroke-linecap="round"/>` +
    `<polygon points="${it.b[0]},${it.b[1]} ${bx - uy * h * 0.36},${by + ux * h * 0.36} ${bx + uy * h * 0.36},${by - ux * h * 0.36}" fill="${it.color}"/>` +
    `<line x1="${it.a[0]}" y1="${it.a[1]}" x2="${it.b[0]}" y2="${it.b[1]}" stroke="transparent" stroke-width="${Math.max(w * 5, 8)}"/></g>`;
}
function pipeOutline(it) {
  const od = PIPE[it.nps][0], p = pal(it.color);
  return `<path data-id="${it.id}" d="${pipePath(it.pts, it.nps)}" fill="none" stroke="${p.line}" stroke-width="${od}" stroke-linejoin="round"/>`;
}
function pipeBody(it) {
  const [od, w40, w80] = PIPE[it.nps], p = pal(it.color), lw = 0.5 + od * 0.008, d = pipePath(it.pts, it.nps);
  let o = `<path data-id="${it.id}" d="${d}" fill="none" stroke="${p.mid}" stroke-width="${od - 2 * lw}" stroke-linejoin="round"/>`;
  if (it.cut) o += `<path data-id="${it.id}" d="${d}" fill="none" stroke="${p.bore}" stroke-width="${od - 2 * (it.sch === 80 ? w80 : w40)}" stroke-linejoin="round"/>`;
  return o;
}
function pipeLabel(it) {
  if (!it.label) return "";
  const od = PIPE[it.nps][0];
  let bi = 0, bl = -1;
  for (let i = 0; i < it.pts.length - 1; i++) { const l = Math.hypot(it.pts[i + 1][0] - it.pts[i][0], it.pts[i + 1][1] - it.pts[i][1]); if (l > bl) { bl = l; bi = i; } }
  const a = it.pts[bi], b = it.pts[bi + 1], mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, fs = Math.max(9, od * 0.42);
  let ang = Math.atan2(b[1] - a[1], b[0] - a[0]) * 180 / Math.PI;          // text follows the run, never upside down
  if (ang > 90) ang -= 180; if (ang <= -90) ang += 180;
  const r = ang * Math.PI / 180, off = od / 2 + fs * 0.45, tx = mx + Math.sin(r) * off, ty = my - Math.cos(r) * off;
  return `<text data-id="${it.id}" x="${tx.toFixed(2)}" y="${ty.toFixed(2)}" font-family="Arial, Helvetica, sans-serif" font-size="${fs.toFixed(1)}" fill="#13233b" text-anchor="middle"` +
    (Math.abs(ang) > 0.5 ? ` transform="rotate(${ang.toFixed(1)} ${tx.toFixed(2)} ${ty.toFixed(2)})"` : "") + `>${esc(it.nps)} SCH ${it.sch}</text>`;
}
function renderAll() {
  const live = doc.items.filter(valid), pipes = live.filter(i => i.type === "pipe"), rest = live.filter(i => i.type !== "pipe");
  return pipes.map(pipeOutline).join("") + pipes.map(pipeBody).join("") + rest.map(itemSvg).join("") + pipes.map(pipeLabel).join("");
}
const ordered = () => [...doc.items.filter(i => i.type === "pipe"), ...doc.items.filter(i => i.type !== "pipe")].filter(valid);

// ---------------------------------------------------------------- view
function viewSize() { const r = $("cv").getBoundingClientRect(); return [Math.max(r.width, 50), Math.max(r.height, 50)]; }
function toWorld(e) {
  const r = $("cv").getBoundingClientRect(), [W, H] = [r.width, r.height], v = ui.view;
  return [v.cx + (e.clientX - r.left - W / 2) / v.s, v.cy + (e.clientY - r.top - H / 2) / v.s];
}
function fit() {
  const b = docBox(20), [W, H] = viewSize();
  if (!b) { ui.view = { cx: 0, cy: 0, s: 1.6 }; return; }
  ui.view = { cx: (b[0] + b[2]) / 2, cy: (b[1] + b[3]) / 2, s: Math.min(6, W / (b[2] - b[0]), H / (b[3] - b[1])) };
}
function zoom(f, at) {
  const v = ui.view, ns = Math.max(0.05, Math.min(20, v.s * f));
  if (at) { v.cx = at[0] - (at[0] - v.cx) * v.s / ns; v.cy = at[1] - (at[1] - v.cy) * v.s / ns; }
  v.s = ns; draw();
}

// ---------------------------------------------------------------- snapping
function snapTargets(skipId) {
  const t = [];
  for (const it of doc.items) {
    if (it.id === skipId || !valid(it)) continue;
    if (it.type === "sym") {
      const T = symXform(it);
      for (const p of symOf(it).ports) { const w = T(p); if (p.length > 2) w.push(it.rot + (it.flip ? 180 - p[2] : p[2])); t.push(w); }
    }
    if (it.type === "pipe") t.push(it.pts[0], it.pts[it.pts.length - 1]);
  }
  return t;
}
const gridSnap = v => Math.round(v / GRID) * GRID;
// Returns [x, y, snappedToAConnection, directionOfThatConnection].
// Runs lock to 45 degree steps from the last point; extraDir adds one more allowed direction (a strainer leg).
function snapPoint(p, prev, skipId, free, extraDir) {
  const tol = 11 / ui.view.s;
  let best = null, bd = tol;
  for (const t of snapTargets(skipId)) { const d = Math.hypot(t[0] - p[0], t[1] - p[1]); if (d < bd) { bd = d; best = t; } }
  if (best) return [best[0], best[1], true, best[2]];
  let c = [gridSnap(p[0]), gridSnap(p[1])], u = null;
  if (prev && !free) {
    const dx = p[0] - prev[0], dy = p[1] - prev[1], ang = Math.atan2(dy, dx) * 180 / Math.PI;
    let a = Math.round(ang / 45) * 45;
    if (extraDir != null && Math.abs(((ang - extraDir + 540) % 360) - 180) < 14) a = extraDir;
    const r = a * Math.PI / 180;
    u = [Math.abs(Math.cos(r)) < 1e-9 ? 0 : Math.cos(r), Math.abs(Math.sin(r)) < 1e-9 ? 0 : Math.sin(r)];
    const len = Math.max(0, gridSnap(dx * u[0] + dy * u[1]));
    c = [Math.round((prev[0] + u[0] * len) * 100) / 100, Math.round((prev[1] + u[1] * len) * 100) / 100];
  }
  // land on the centreline of another pipe to make a tee
  for (const it of doc.items) {
    if (it.type !== "pipe" || it.id === skipId) continue;
    for (let i = 0; i < it.pts.length - 1; i++) {
      const a = it.pts[i], b = it.pts[i + 1], vx = b[0] - a[0], vy = b[1] - a[1], L2 = vx * vx + vy * vy;
      if (!L2) continue;
      if (!u) {
        const k = Math.max(0, Math.min(1, ((c[0] - a[0]) * vx + (c[1] - a[1]) * vy) / L2)), q = [a[0] + vx * k, a[1] + vy * k];
        if (Math.hypot(q[0] - c[0], q[1] - c[1]) <= tol) return [q[0], q[1], true];
        continue;
      }
      const den = u[0] * vy - u[1] * vx;                      // where this run would cross that pipe
      if (Math.abs(den) < 1e-9) continue;
      const ex = a[0] - prev[0], ey = a[1] - prev[1], tt = (ex * vy - ey * vx) / den, k = (ex * u[1] - ey * u[0]) / den;
      if (tt <= 0 || k < 0 || k > 1) continue;
      const q = [prev[0] + u[0] * tt, prev[1] + u[1] * tt];
      if (Math.hypot(q[0] - c[0], q[1] - c[1]) <= tol) return [Math.round(q[0] * 100) / 100, Math.round(q[1] * 100) / 100, true];
    }
  }
  return c;
}
function snapSym(it) {                                    // pull a product onto a nearby pipe end or port, else onto the grid
  const tol = 11 / ui.view.s, ps = portsOf(it), targets = snapTargets(it.id);
  let best = null, bd = tol;
  for (const p of ps) for (const t of targets) { const d = Math.hypot(t[0] - p[0], t[1] - p[1]); if (d < bd) { bd = d; best = [t[0] - p[0], t[1] - p[1]]; } }
  if (!best) best = [gridSnap(ps[0][0]) - ps[0][0], gridSnap(ps[0][1]) - ps[0][1]];
  it.x += best[0]; it.y += best[1];
}

// ---------------------------------------------------------------- canvas
function draw() {
  const cv = $("cv"), [W, H] = viewSize(), v = ui.view, vw = W / v.s, vh = H / v.s, x0 = v.cx - vw / 2, y0 = v.cy - vh / 2, px = 1 / v.s;
  cv.setAttribute("viewBox", `${x0} ${y0} ${vw} ${vh}`);
  gradN = 0;
  const minor = v.s * 10 >= 7 ? 10 : 50, major = minor * 10 >= 100 ? (minor === 10 ? 100 : 500) : 100;
  let o = `<defs><pattern id="gm" width="${minor}" height="${minor}" patternUnits="userSpaceOnUse"><path d="M${minor} 0H0V${minor}" fill="none" stroke="#e6ebf1" stroke-width="${px}"/></pattern>` +
    `<pattern id="gM" width="${major}" height="${major}" patternUnits="userSpaceOnUse"><path d="M${major} 0H0V${major}" fill="none" stroke="#cdd6e0" stroke-width="${px}"/></pattern></defs>` +
    `<rect x="${x0}" y="${y0}" width="${vw}" height="${vh}" fill="#ffffff"/><rect x="${x0}" y="${y0}" width="${vw}" height="${vh}" fill="url(#gm)"/><rect x="${x0}" y="${y0}" width="${vw}" height="${vh}" fill="url(#gM)"/>`;
  o += renderAll();
  // connection points while routing pipe or moving things
  if (ui.tool === "pipe" || ui.drag) for (const t of snapTargets(ui.drag && ui.drag.id)) o += `<circle cx="${t[0]}" cy="${t[1]}" r="${4 * px}" fill="#fff" stroke="#1f5fae" stroke-width="${1.5 * px}" pointer-events="none"/>`;
  const sel = selected();
  if (sel && valid(sel)) {
    const b = bboxOf(sel), m = 4 * px;
    o += `<rect x="${b[0] - m}" y="${b[1] - m}" width="${b[2] - b[0] + 2 * m}" height="${b[3] - b[1] + 2 * m}" fill="none" stroke="#1f5fae" stroke-width="${1.5 * px}" stroke-dasharray="${5 * px} ${4 * px}" pointer-events="none"/>`;
    const hs = sel.type === "pipe" ? sel.pts : sel.type === "arrow" ? [sel.a, sel.b] : [];
    hs.forEach((p, i) => { o += `<rect data-h="${i}" x="${p[0] - 5 * px}" y="${p[1] - 5 * px}" width="${10 * px}" height="${10 * px}" fill="#fff" stroke="#1f5fae" stroke-width="${1.5 * px}" style="cursor:move"/>`; });
  }
  if (ui.draft) {
    const pts = ui.cursor ? [...ui.draft.pts, ui.cursor] : ui.draft.pts;
    if (ui.tool === "pipe" && pts.length > 1) {
      const od = PIPE[ui.pipe.nps][0];
      o += `<path d="${pipePath(pts, ui.pipe.nps)}" fill="none" stroke="${ui.pipe.color}" stroke-opacity="0.55" stroke-width="${od}" stroke-linejoin="round" pointer-events="none"/>`;
    }
    if (ui.tool === "arrow" && pts.length > 1) o += `<line x1="${pts[0][0]}" y1="${pts[0][1]}" x2="${pts[1][0]}" y2="${pts[1][1]}" stroke="#1f5fae" stroke-width="${1.5 * px}" pointer-events="none"/>`;
    pts.forEach(p => { o += `<circle cx="${p[0]}" cy="${p[1]}" r="${3 * px}" fill="#1f5fae" pointer-events="none"/>`; });
  }
  cv.innerHTML = o;
  const choices = [0.5, 1, 2, 4, 6, 12, 24, 48, 96], inches = choices.find(c => c * 25.4 * v.s >= 60) || 96, bar = $("scalebar");
  bar.querySelector("i").style.width = (inches * 25.4 * v.s).toFixed(1) + "px";
  bar.querySelector("span").textContent = inches >= 12 ? `${inches / 12} ft` : `${inches} in`;
  $("board").className = "board t-" + ui.tool;
  $("tip").textContent = { select: sel ? "Drag to move. Delete removes it." : "Click an item to select it. Drag the sheet to pan, scroll to zoom.",
    pipe: ui.draft ? "Runs lock to 45° steps (hold Alt for any angle). Double-click or Enter to finish, Esc to cancel." : "Click to start a pipe. It snaps to product connections (blue dots).",
    text: "Click where the label goes.", arrow: ui.draft ? "Click where the arrow points." : "Click where the arrow starts." }[ui.tool];
}
const selected = () => doc.items.find(i => i.id === ui.sel) || null;

// ---------------------------------------------------------------- history and storage
function commit() {
  const j = JSON.stringify(doc);
  if (j !== hist[hi]) { hist = hist.slice(0, hi + 1); hist.push(j); hi++; if (hist.length > 80) { hist.shift(); hi--; } }
  try { localStorage.setItem("sdg-doc", j); } catch (e) {}
  refresh();
}
function loadDoc(d) {
  if (!d || !Array.isArray(d.items)) throw new Error("bad file");
  doc = { v: 1, style: Object.assign({ shade: true, blackLines: false }, d.style || {}), items: d.items.filter(i => i && ["sym", "pipe", "text", "arrow"].includes(i.type) && (i.type !== "pipe" || PIPE[i.nps])) };
  doc.items.forEach(i => { i.id = nextId++; });
  ui.sel = null; ui.draft = null;
}
function step(n) { if (hist[hi + n] === undefined) return; hi += n; const keep = ui.view; loadDoc(JSON.parse(hist[hi])); ui.view = keep; try { localStorage.setItem("sdg-doc", hist[hi]); } catch (e) {} refresh(); }
function refresh() { draw(); panel(); }

// ---------------------------------------------------------------- side panel
function chipRow(el, items, current, onPick, label) {
  el.innerHTML = "";
  items.forEach(it => { const b = document.createElement("button"); b.type = "button"; b.className = "chip"; b.textContent = label ? label(it) : it;
    b.setAttribute("aria-pressed", it === current); b.addEventListener("click", () => onPick(it)); el.appendChild(b); });
}
function swatches(el, current, onPick) {
  el.innerHTML = "";
  PRESETS.forEach(([name, hex]) => { const b = document.createElement("button"); b.type = "button"; b.className = "sw"; b.style.background = hex; b.title = name;
    b.setAttribute("aria-label", name); b.setAttribute("aria-pressed", hex.toLowerCase() === String(current).toLowerCase()); b.addEventListener("click", () => onPick(hex)); el.appendChild(b); });
  const c = document.createElement("input"); c.type = "color"; c.value = /^#[0-9a-f]{6}$/i.test(current) ? current : "#3f86dc"; c.setAttribute("aria-label", "Custom color");
  c.addEventListener("change", e => onPick(e.target.value)); el.appendChild(c);
}
function panel() {
  const sel = selected(), kind = sel ? sel.type : null;
  $("gProduct").hidden = !(kind === "sym" || (!sel && ui.tool === "select"));
  $("gPipe").hidden = !(kind === "pipe" || (!sel && ui.tool === "pipe"));
  $("gText").hidden = !(kind === "text" || (!sel && ui.tool === "text"));
  $("gArrow").hidden = !(kind === "arrow" || (!sel && ui.tool === "arrow"));
  ["Select", "Pipe", "Text", "Arrow"].forEach(t => $("t" + t).setAttribute("aria-pressed", ui.tool === t.toLowerCase()));
  $("bRot").disabled = !(kind === "sym" || kind === "pipe"); $("bFlip").disabled = kind !== "sym";
  $("bRot").textContent = kind === "pipe" ? "Rotate 45°" : "Rotate"; $("bDup").disabled = $("bDel").disabled = !sel;
  $("bUndo").disabled = hi <= 0; $("bRedo").disabled = hi >= hist.length - 1;
  $("shade").checked = doc.style.shade; $("blackLines").checked = doc.style.blackLines;

  // product picker: edits the selected product, or sets up the next one to add
  const tgt = kind === "sym" ? sel : ui.pick, editing = kind === "sym";
  const set = (k, v) => { tgt[k] = v; if (editing) commit(); else panel(); };
  let p = LIB.products.find(q => q.id === tgt.product);
  if (!editing) {
    if (!p || p.family !== ui.pick.family) { ui.pick.product = LIB.products.find(q => q.family === ui.pick.family).id; p = LIB.products.find(q => q.id === ui.pick.product); }
    if (!p.sizes.includes(ui.pick.size)) ui.pick.size = p.sizes[Math.min(1, p.sizes.length - 1)];
    if (!variantsOf(p, ui.pick.size).includes(ui.pick.variant)) ui.pick.variant = variantsOf(p, ui.pick.size)[0];
  } else if (p && !variantsOf(p, sel.size).includes(sel.variant)) sel.variant = variantsOf(p, sel.size)[0];
  if (p) {
    $("prodTitle").textContent = editing ? "Selected product" : "Add a product";
    $("families").hidden = $("products").hidden = $("addBtn").hidden = editing;
    if (!editing) {
      chipRow($("families"), LIB.families, ui.pick.family, v => {
        if (v === "Fittings" && ui.pick.family !== "Fittings") { ui.pick.prevColor = ui.pick.color; ui.pick.color = ui.pipe.color; }
        if (v !== "Fittings" && ui.pick.family === "Fittings" && ui.pick.prevColor) ui.pick.color = ui.pick.prevColor;
        ui.pick.family = v; panel(); });
      const box = $("products"); box.innerHTML = ""; gradN = 1000;
      LIB.products.filter(q => q.family === ui.pick.family).forEach(q => {
        const b = document.createElement("button"); b.type = "button"; b.className = "prod"; b.setAttribute("aria-pressed", q.id === ui.pick.product);
        const ts = q.sizes[Math.min(q.fit ? 5 : 1, q.sizes.length - 1)], k = `${q.id}|${ts}|${variantsOf(q, ts)[q.fit && variantsOf(q, ts).length > 2 ? 2 : 0]}`, s = lookup(k);
        b.innerHTML = `<svg viewBox="${s.box[0] - 1} ${s.box[1] - 1} ${s.box[2] + 2} ${s.box[3] + 2}" preserveAspectRatio="xMidYMid meet" aria-hidden="true">${symInner(k, ui.pick.color, false, 0, false)}</svg><span></span>`;
        b.querySelector("span").textContent = q.name.split(" /")[0];
        b.addEventListener("click", () => { ui.pick.product = q.id; panel(); }); box.appendChild(b);
      });
    }
    $("prodmeta").innerHTML = `<b>${esc(p.name)}</b> · ${esc(p.type)} · ${esc(p.ti)}`;
    chipRow($("sizes"), p.sizes, tgt.size, v => { tgt.size = v; if (!variantsOf(p, v).includes(tgt.variant)) tgt.variant = variantsOf(p, v)[0]; if (editing) commit(); else panel(); });
    const vs = variantsOf(p, tgt.size);
    $("variantRow").hidden = $("variants").hidden = vs.length < 2 && vs[0] === "-";
    $("variantLabel").textContent = p.variantLabel || "Connection";
    chipRow($("variants"), vs, tgt.variant, v => set("variant", v), v => VARIANT_LABEL[v] || (v[0].toUpperCase() + v.slice(1)));
    swatches($("symColors"), tgt.color, v => set("color", v));
    const s = lookup(`${tgt.product}|${tgt.size}|${tgt.variant}`);
    $("symArrow").checked = !!tgt.arrow; $("symArrowWrap").hidden = !(s && s.arrow);
    $("symArrow").onchange = e => set("arrow", e.target.checked);
    const inch = mm => (mm / 25.4).toFixed(mm / 25.4 >= 10 ? 1 : 2) + '"';
    $("dims").innerHTML = s ? `<tr><th>${p.fit ? "Dimension" : "TI dim"}</th><th>in</th><th>mm</th></tr>` + Object.keys(s.dims).map(k => `<tr><td>${k}</td><td>${inch(s.dims[k])}</td><td>${s.dims[k]}</td></tr>`).join("") : "";
  }

  // pipe
  const pt = kind === "pipe" ? sel : ui.pipe, pe = kind === "pipe", pset = (k, v) => { pt[k] = v; if (pe) commit(); else refresh(); };
  $("pipeTitle").textContent = pe ? "Selected pipe" : "Pipe"; $("pipeHint").hidden = pe;
  if (!$("nps").options.length) Object.keys(PIPE).forEach(k => { const o = document.createElement("option"); o.value = k; o.textContent = k; $("nps").appendChild(o); });
  $("nps").value = pt.nps; $("sch").value = String(pt.sch); $("pipeLabel").checked = !!pt.label; $("pipeCut").checked = !!pt.cut;
  $("nps").onchange = e => pset("nps", e.target.value); $("sch").onchange = e => pset("sch", +e.target.value);
  $("pipeLabel").onchange = e => pset("label", e.target.checked); $("pipeCut").onchange = e => pset("cut", e.target.checked);
  swatches($("pipeColors"), pt.color, v => pset("color", v));
  const [od, w40, w80] = PIPE[pt.nps], wall = pt.sch === 80 ? w80 : w40;
  $("pipeMeta").textContent = `OD ${(od / 25.4).toFixed(3)}", wall ${(wall / 25.4).toFixed(3)}", ID ${((od - 2 * wall) / 25.4).toFixed(3)}"`;

  // text
  const tt = kind === "text" ? sel : ui.text, te = kind === "text";
  $("textTitle").textContent = te ? "Selected text" : "Text"; $("textHint").hidden = te;
  if (document.activeElement !== $("textVal")) $("textVal").value = tt.text;
  if (document.activeElement !== $("textSize")) $("textSize").value = tt.size;
  $("textVal").oninput = e => { tt.text = e.target.value; if (te) { draw(); clearTimeout(panel.t); panel.t = setTimeout(commit, 500); } };
  $("textSize").oninput = e => { const v = Math.max(3, Math.min(400, +e.target.value || 14)); tt.size = v; if (te) { draw(); clearTimeout(panel.t); panel.t = setTimeout(commit, 500); } };
  swatches($("textColors"), tt.color, v => { tt.color = v; if (te) commit(); else panel(); });
  const at = kind === "arrow" ? sel : ui.arrow;
  $("arrowHint").hidden = kind === "arrow";
  swatches($("arrowColors"), at.color, v => { at.color = v; if (kind === "arrow") commit(); else panel(); });
}

// ---------------------------------------------------------------- actions
function setTool(t) { ui.tool = t; ui.draft = null; ui.cursor = null; if (t !== "select") ui.sel = null; refresh(); }
function addProduct() {
  const k = ui.pick, it = { id: nextId++, type: "sym", product: k.product, size: k.size, variant: k.variant, color: k.color, arrow: k.arrow, rot: 0, flip: false, x: ui.view.cx, y: ui.view.cy };
  doc.items.push(it); snapSym(it); ui.sel = it.id; ui.tool = "select"; commit();
}
function finishPipe() {
  const d = ui.draft; ui.draft = null; ui.cursor = null;
  if (d && d.pts.length > 1) { const it = Object.assign({ id: nextId++, type: "pipe", pts: d.pts }, ui.pipe); doc.items.push(it); commit(); } else refresh();
}
function del() { if (!ui.sel) return; doc.items = doc.items.filter(i => i.id !== ui.sel); ui.sel = null; commit(); }
function dup() {
  const s = selected(); if (!s) return;
  const c = JSON.parse(JSON.stringify(s)); c.id = nextId++;
  if (c.type === "pipe") c.pts = c.pts.map(p => [p[0] + 20, p[1] + 20]); else if (c.type === "arrow") { c.a = [c.a[0] + 20, c.a[1] + 20]; c.b = [c.b[0] + 20, c.b[1] + 20]; } else { c.x += 20; c.y += 20; }
  doc.items.push(c); ui.sel = c.id; commit();
}
function rotate() {
  const s = selected(); if (!s) return;
  if (s.type === "sym") { s.rot = (s.rot + 90) % 360; commit(); }
  else if (s.type === "pipe") {                           // 45 degrees about the first point
    const o = s.pts[0], c = Math.SQRT1_2;
    s.pts = s.pts.map(p => { const x = p[0] - o[0], y = p[1] - o[1]; return [Math.round((o[0] + x * c - y * c) * 100) / 100, Math.round((o[1] + x * c + y * c) * 100) / 100]; });
    commit();
  }
}
function mirror() { const s = selected(); if (s && s.type === "sym") { s.flip = !s.flip; commit(); } }

// ---------------------------------------------------------------- pointer input
const cv = $("cv");
let lastDown = null;
cv.addEventListener("pointerdown", e => {
  if (e.button !== 0 && e.pointerType === "mouse") return;
  const w = toWorld(e);
  const dbl = lastDown && e.timeStamp - lastDown.t < 400 && Math.hypot(e.clientX - lastDown.x, e.clientY - lastDown.y) < 6;
  lastDown = { t: e.timeStamp, x: e.clientX, y: e.clientY };
  if (ui.tool === "pipe") {
    if (dbl && ui.draft) { finishPipe(); return; }          // double-click ends the run
    const prev = ui.draft && ui.draft.pts[ui.draft.pts.length - 1];
    const sp = snapPoint(w, prev, null, e.altKey, ui.draft && ui.draft.pts.length === 1 ? ui.draft.dir : null), p = sp.slice(0, 2);
    if (!ui.draft) ui.draft = { pts: [p], dir: sp[3] };
    else if (Math.hypot(p[0] - prev[0], p[1] - prev[1]) > 0.5) ui.draft.pts.push(p);
    draw();
    return;
  }
  if (ui.tool === "arrow") {
    const p = [Math.round(w[0]), Math.round(w[1])];
    if (!ui.draft) { ui.draft = { pts: [p] }; draw(); }
    else { const it = { id: nextId++, type: "arrow", a: ui.draft.pts[0], b: p, color: ui.arrow.color, w: 1.6 }; ui.draft = null; doc.items.push(it); ui.sel = it.id; ui.tool = "select"; commit(); }
    return;
  }
  if (ui.tool === "text") {
    const it = { id: nextId++, type: "text", x: gridSnap(w[0]), y: gridSnap(w[1]), text: ui.text.text || "Label", size: ui.text.size, color: ui.text.color };
    doc.items.push(it); ui.sel = it.id; ui.tool = "select"; commit(); $("textVal").focus(); $("textVal").select();
    return;
  }
  const h = e.target.closest("[data-h]"), g = e.target.closest("[data-id]");
  cv.setPointerCapture(e.pointerId);
  if (h && selected()) { ui.drag = { kind: "handle", id: ui.sel, i: +h.dataset.h, moved: false }; return; }
  if (g) {
    const id = +g.dataset.id, it = doc.items.find(i => i.id === id);
    ui.sel = id; ui.drag = { kind: "move", id, start: w, orig: JSON.stringify(it), moved: false }; refresh();
    return;
  }
  ui.sel = null; ui.drag = { kind: "pan", sx: e.clientX, sy: e.clientY, cx: ui.view.cx, cy: ui.view.cy, moved: false }; refresh();
});
cv.addEventListener("pointermove", e => {
  const w = toWorld(e), d = ui.drag;
  if (!d) {
    if (ui.draft) { const prev = ui.draft.pts[ui.draft.pts.length - 1]; ui.cursor = ui.tool === "pipe" ? snapPoint(w, prev, null, e.altKey, ui.draft.pts.length === 1 ? ui.draft.dir : null).slice(0, 2) : w; draw(); }
    return;
  }
  if (d.kind === "pan") { ui.view.cx = d.cx - (e.clientX - d.sx) / ui.view.s; ui.view.cy = d.cy - (e.clientY - d.sy) / ui.view.s; d.moved = true; draw(); return; }
  const it = doc.items.find(i => i.id === d.id); if (!it) return;
  d.moved = true;
  if (d.kind === "handle") {
    if (it.type === "pipe") it.pts[d.i] = snapPoint(w, null, it.id, true).slice(0, 2); else it[d.i ? "b" : "a"] = [Math.round(w[0]), Math.round(w[1])];
  } else {
    const o = JSON.parse(d.orig), dx = w[0] - d.start[0], dy = w[1] - d.start[1];
    if (it.type === "pipe") { const sx = gridSnap(dx), sy = gridSnap(dy); it.pts = o.pts.map(p => [p[0] + sx, p[1] + sy]); }
    else if (it.type === "arrow") { it.a = [o.a[0] + dx, o.a[1] + dy]; it.b = [o.b[0] + dx, o.b[1] + dy]; }
    else { it.x = o.x + dx; it.y = o.y + dy; if (it.type === "sym") snapSym(it); else { it.x = gridSnap(it.x); it.y = gridSnap(it.y); } }
  }
  draw();
});
function endDrag() { const d = ui.drag; ui.drag = null; if (d && d.moved && d.kind !== "pan") commit(); else draw(); }
cv.addEventListener("pointerup", endDrag); cv.addEventListener("pointercancel", endDrag);
cv.addEventListener("dblclick", e => {
  const g = e.target.closest("[data-id]"); if (ui.tool === "select" && g && selected() && selected().type === "text") { $("textVal").focus(); $("textVal").select(); } });
cv.addEventListener("wheel", e => { e.preventDefault(); zoom(e.deltaY < 0 ? 1.15 : 1 / 1.15, toWorld(e)); }, { passive: false });
window.addEventListener("keydown", e => {
  if (/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) return;
  const k = e.key.toLowerCase(), mod = e.ctrlKey || e.metaKey;
  if (k === "escape") { if (ui.draft) { ui.draft = null; ui.cursor = null; draw(); } else setTool("select"); }
  else if (k === "enter" && ui.tool === "pipe") finishPipe();
  else if ((k === "delete" || k === "backspace") && ui.sel) { e.preventDefault(); del(); }
  else if (mod && k === "z") { e.preventDefault(); step(e.shiftKey ? 1 : -1); }
  else if (mod && k === "y") { e.preventDefault(); step(1); }
  else if (mod && k === "d") { e.preventDefault(); dup(); }
  else if (k === "r" && !mod) rotate(); else if (k === "m" && !mod) mirror();
  else if (k === "v" && !mod) setTool("select"); else if (k === "p" && !mod) setTool("pipe"); else if (k === "t" && !mod) setTool("text");
});

// ---------------------------------------------------------------- export
function say(msg, cls) { const s = $("status"); s.textContent = msg; s.className = "status" + (cls ? " " + cls : ""); }
function exportSvg(maxPx) {
  const b = docBox(8); if (!b) return null;
  const w = b[2] - b[0], h = b[3] - b[1], k = Math.min(8, maxPx / Math.max(w, h));
  gradN = 5000;
  const bg = $("whiteBg").checked ? `<rect x="${b[0]}" y="${b[1]}" width="${w}" height="${h}" fill="#ffffff"/>` : "";
  return { text: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${b[0]} ${b[1]} ${w} ${h}" width="${Math.round(w * k)}" height="${Math.round(h * k)}">${bg}${renderAll()}</svg>`,
    W: Math.round(w * k), H: Math.round(h * k) };
}
function pngBlob() {
  return new Promise((resolve, reject) => {
    const f = exportSvg(3200); if (!f) return reject(new Error("empty"));
    const url = URL.createObjectURL(new Blob([f.text], { type: "image/svg+xml" })), img = new Image();
    img.onload = () => { const c = document.createElement("canvas"); c.width = f.W; c.height = f.H; c.getContext("2d").drawImage(img, 0, 0, f.W, f.H); URL.revokeObjectURL(url);
      c.toBlob(bl => bl ? resolve(bl) : reject(new Error("render failed")), "image/png"); };
    img.onerror = () => { URL.revokeObjectURL(url); reject(new Error("render failed")); };
    img.src = url;
  });
}
async function save(name, getData) {
  if (!doc.items.length) { say("The drawing is empty.", "warn"); return; }
  try {
    const data = await getData(), blob = data instanceof Blob ? data : new Blob([data], { type: name.endsWith(".svg") ? "image/svg+xml" : "application/json" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 4000);
    say(`Saved ${name} to your downloads folder`, "ok");
  } catch (e) { say("Couldn't save the file.", "warn"); }
}
$("pngBtn").addEventListener("click", () => save("steam-drawing.png", pngBlob));
$("svgBtn").addEventListener("click", () => save("steam-drawing.svg", async () => exportSvg(3200).text));
$("saveBtn").addEventListener("click", () => save("steam-drawing.json", async () => JSON.stringify(doc)));
$("copyBtn").addEventListener("click", async () => {
  if (!doc.items.length) { say("The drawing is empty.", "warn"); return; }
  try { if (!navigator.clipboard || !window.ClipboardItem) throw new Error("no clipboard");
    await navigator.clipboard.write([new ClipboardItem({ "image/png": pngBlob() })]); say("Copied. Paste it into PowerPoint or Word.", "ok"); }
  catch (e) { say("Copying images is blocked in this view. Use Download PNG.", "warn"); }
});
$("openBtn").addEventListener("click", () => $("openFile").click());
$("openFile").addEventListener("change", e => {
  const f = e.target.files[0]; if (!f) return;
  const r = new FileReader();
  r.onload = () => { try { loadDoc(JSON.parse(r.result)); fit(); commit(); say(`Opened ${f.name}`, "ok"); } catch (err) { say("That file isn't a drawing saved from this page.", "warn"); } };
  r.readAsText(f); e.target.value = "";
});
let clearArmed = 0;
$("clearBtn").addEventListener("click", () => {
  if (Date.now() - clearArmed < 4000) { doc.items = []; ui.sel = null; clearArmed = 0; $("clearBtn").textContent = "Clear"; commit(); say("Cleared. Undo brings it back."); }
  else { clearArmed = Date.now(); $("clearBtn").textContent = "Click again to clear"; setTimeout(() => { $("clearBtn").textContent = "Clear"; }, 4000); }
});

// ---------------------------------------------------------------- wiring
[["tSelect", "select"], ["tPipe", "pipe"], ["tText", "text"], ["tArrow", "arrow"]].forEach(([id, t]) => $(id).addEventListener("click", () => setTool(t)));
$("addBtn").addEventListener("click", addProduct);
$("bRot").addEventListener("click", rotate); $("bFlip").addEventListener("click", mirror); $("bDup").addEventListener("click", dup); $("bDel").addEventListener("click", del);
$("bUndo").addEventListener("click", () => step(-1)); $("bRedo").addEventListener("click", () => step(1));
$("bIn").addEventListener("click", () => zoom(1.25)); $("bOut").addEventListener("click", () => zoom(0.8)); $("bFit").addEventListener("click", () => { fit(); draw(); });
$("shade").addEventListener("change", e => { doc.style.shade = e.target.checked; commit(); });
$("blackLines").addEventListener("change", e => { doc.style.blackLines = e.target.checked; commit(); });
window.addEventListener("resize", draw);

function exampleDoc() {
  // a small drip-leg style run so the sheet does not open empty
  const mk = (product, size, variant, inlet) => {
    const it = { id: nextId++, type: "sym", product, size, variant, color: "#3f86dc", arrow: true, rot: 0, flip: false, x: 0, y: 0 };
    const p = portsOf(it)[0]; it.x += inlet[0] - p[0]; it.y += inlet[1] - p[1]; return it;
  };
  const pipe = (pts) => ({ id: nextId++, type: "pipe", pts, nps: '3/4"', sch: 80, color: "#8d99a8", label: false, cut: false });
  const st = mk("FIG16HP", '3/4"', "screwed", [0, 0]), so = portsOf(st)[1];
  const tr = mk("TD52", '3/4"', "NPT", [so[0] + 110, 0]), to = portsOf(tr)[1];
  const first = pipe([[-230, -150], [-230, 0], [0, 0]]); first.label = true;
  doc.items = [first, pipe([so, [so[0] + 110, 0]]), pipe([to, [to[0] + 160, 0]]), st, tr,
    { id: nextId++, type: "text", x: -230, y: 130, text: "Example layout. Press Clear to start your own.", size: 12, color: "#5b6878" }];
}
let restored = false;
try { const j = localStorage.getItem("sdg-doc"); if (j) { loadDoc(JSON.parse(j)); restored = doc.items.length > 0; } } catch (e) {}
if (!restored) exampleDoc();
fit(); commit();
requestAnimationFrame(() => { fit(); draw(); });
$("ver").textContent = `Version ${BUILD}. ${LIB.products.filter(p => !p.fit).length} products loaded.` + (SDG.failed && SDG.failed.length ? ` ${SDG.failed.length} pack(s) failed to load.` : "");
