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
const BUILD = "8";
const LOGO = window.SDG_LOGO || null;                       // vector Spirax Sarco logo, app/logo.js
const STYLE0 = { shade: true, blackLines: false, units: "ftin", prec: 1 };
const UNITS = [["ftin", "ft-in"], ["in", "in"], ["mm", "mm"]];
const PRECS = [[1, '1"'], [0.5, '1/2"'], [0.0625, '1/16"']];     // what ft-in and in lengths round to
const LOGO_POS = [["center", "On body"], ["above", "Above"], ["below", "Below"]];
const LOGO_SIZE = { S: 0.3, M: 0.45, L: 0.65 };             // logo width as a share of the product's width

let doc = { v: 1, style: Object.assign({}, STYLE0), items: [] };
const ui = { tool: "select", sel: null, set: [], draft: null, cursor: null, view: { cx: 0, cy: 0, s: 1.6 },
  pick: { family: "Steam traps", product: "TD52", size: '3/4"', variant: "NPT", color: "#3f86dc", arrow: true, logo: false, logoPos: "center", logoSize: "M" },
  pipe: { nps: '3/4"', sch: 80, color: "#8d99a8", label: true, cut: false, len: false },
  text: { text: "", size: 14, color: "#13233b" }, arrow: { color: "#13233b" }, dim: { mode: "aligned", color: "#13233b", size: 0 } };

// ---------------------------------------------------------------- lengths and dimensions
// Lengths read to the drawing's rounding (1", 1/2" or 1/16"), or to 1 mm.
function fmtLen(mm, units, prec) {
  units = units || doc.style.units;
  if (units === "mm") return `${Math.round(mm)} mm`;
  const per = Math.max(1, Math.round(1 / (prec || doc.style.prec || 1)));            // steps per inch
  const n = Math.round(Math.abs(mm) / 25.4 * per), ft = units === "ftin" ? Math.floor(n / (12 * per)) : 0, r = n - ft * 12 * per;
  const whole = Math.floor(r / per); let num = r % per, den = per;
  while (num && num % 2 === 0) { num /= 2; den /= 2; }
  const lead = whole || !num || ft;                        // 4'-0 5/8", but 5/8" on its own
  const inch = (lead ? String(whole) : "") + (num ? `${lead ? " " : ""}${num}/${den}` : "");
  return ft ? `${ft}'-${inch}"` : `${inch}"`;
}
// Typed lengths: 24, 24", 2'-6", 2' 6 1/2, 30 1/2, 30.5, 2ft, 600mm, 1.2m. Bare numbers are inches (mm when the drawing is in mm).
function parseLen(str) {
  let t = String(str || "").trim().toLowerCase().replace(/inches|inch|in\b/g, '"').replace(/feet|foot|ft\b/g, "'").replace(/\s+/g, " ");
  if (!t) return null;
  const num = v => { v = v.trim().replace(/"$/, "").trim(); if (!v) return 0;
    const m = v.match(/^(\d+(?:\.\d+)?)?(?:[ -]?(\d+)\/(\d+))?$/); if (!m || (!m[1] && !m[2])) return NaN;
    return (m[1] ? +m[1] : 0) + (m[2] ? m[2] / m[3] : 0); };
  let mm;
  if (/mm$/.test(t)) mm = +t.slice(0, -2);
  else if (/[0-9.]m$/.test(t)) mm = +t.slice(0, -1) * 1000;
  else if (t.includes("'")) { const [f, r] = t.split("'"); mm = (+f * 12 + num(r.replace(/^[ -]+/, ""))) * 25.4; }
  else if (t.includes('"') || doc.style.units !== "mm") mm = num(t) * 25.4;
  else mm = num(t);
  return isFinite(mm) && mm > 0 ? Math.round(mm * 100) / 100 : null;
}
// A dimension: points a and b, the measuring mode (aligned, h, v) and the signed offset of the dimension line.
function dimGeom(it) {
  const a = it.a, b = it.b, dx = b[0] - a[0], dy = b[1] - a[1];
  let u = it.mode === "h" ? [dx < 0 ? -1 : 1, 0] : it.mode === "v" ? [0, dy < 0 ? -1 : 1] : [dx, dy];
  const ul = Math.hypot(u[0], u[1]) || 1; u = [u[0] / ul, u[1] / ul];
  const n = [-u[1], u[0]], dn = dx * n[0] + dy * n[1], L = Math.abs(dx * u[0] + dy * u[1]);
  const p1 = [a[0] + n[0] * it.off, a[1] + n[1] * it.off], p2 = [b[0] + n[0] * (it.off - dn), b[1] + n[1] * (it.off - dn)];
  return { u, n, L, p1, p2 };
}
function dimSvg(it) {
  const g = dimGeom(it), s = it.size, lw = Math.max(0.25, s * 0.07), ah = Math.min(s * 0.85, g.L * 0.3), aw = ah * 0.28;
  const f = v => v.toFixed(2), side = it.off < 0 ? -1 : 1;
  const ext = (p, q) => {                                 // extension line from the measured point past the dimension line
    const vx = q[0] - p[0], vy = q[1] - p[1], l = Math.hypot(vx, vy);
    if (l < s * 0.4) return "";
    const ux = vx / l, uy = vy / l, gap = s * 0.3, over = s * 0.45;
    return `M${f(p[0] + ux * gap)},${f(p[1] + uy * gap)}L${f(q[0] + ux * over)},${f(q[1] + uy * over)}`;
  };
  const head = (p, d) => `${f(p[0])},${f(p[1])} ${f(p[0] + d[0] * ah - g.n[0] * aw)},${f(p[1] + d[1] * ah - g.n[1] * aw)} ${f(p[0] + d[0] * ah + g.n[0] * aw)},${f(p[1] + d[1] * ah + g.n[1] * aw)}`;
  const um = [-g.u[0], -g.u[1]];
  let ang = Math.atan2(g.u[1], g.u[0]) * 180 / Math.PI;
  if (ang > 90.5) ang -= 180; if (ang <= -89.5) ang += 180;
  const r = ang * Math.PI / 180, up = [Math.sin(r), -Math.cos(r)];           // screen "up" for the text
  const mx = (g.p1[0] + g.p2[0]) / 2, my = (g.p1[1] + g.p2[1]) / 2, tx = mx + up[0] * s * 0.45, ty = my + up[1] * s * 0.45;
  const id = `data-id="${it.id}"`;
  return `<g ${id}><path d="${ext(it.a, g.p1)}${ext(it.b, g.p2)}M${f(g.p1[0])},${f(g.p1[1])}L${f(g.p2[0])},${f(g.p2[1])}" fill="none" stroke="${it.color}" stroke-width="${f(lw)}" stroke-linecap="round"/>` +
    `<polygon points="${head(g.p1, g.u)}" fill="${it.color}"/><polygon points="${head(g.p2, um)}" fill="${it.color}"/>` +
    `<text x="${f(tx)}" y="${f(ty)}" font-family="Arial, Helvetica, sans-serif" font-size="${f(s)}" fill="${it.color}" text-anchor="middle"` +
    (Math.abs(ang) > 0.5 ? ` transform="rotate(${ang.toFixed(1)} ${f(tx)} ${f(ty)})"` : "") + `>${esc(fmtLen(g.L))}</text>` +
    `<path d="M${f(g.p1[0])},${f(g.p1[1])}L${f(g.p2[0])},${f(g.p2[1])}" stroke="transparent" stroke-width="${f(Math.max(s * 1.6, 10 / ui.view.s))}"/></g>`;
}
function dimBox(it) {
  const g = dimGeom(it), s = it.size, P = [it.a, it.b, g.p1, g.p2].map(p => [p[0], p[1]]);
  const mx = (g.p1[0] + g.p2[0]) / 2, my = (g.p1[1] + g.p2[1]) / 2, half = fmtLen(g.L).length * s * 0.3;
  P.push([mx - half, my - s * 1.4], [mx + half, my + s * 1.4]);
  return [Math.min(...P.map(p => p[0])), Math.min(...P.map(p => p[1])), Math.max(...P.map(p => p[0])), Math.max(...P.map(p => p[1]))];
}
const autoDimSize = L => Math.round(Math.max(8, Math.min(50, L * 0.035)));
// Spirax Sarco logo on a product: always upright and never mirrored, placed from the product's outline box.
function logoPlace(it, b) {
  if (!LOGO || !it.logo) return null;
  const bw = b[2] - b[0], bh = b[3] - b[1], pos = it.logoPos || "center";
  let w = bw * (LOGO_SIZE[it.logoSize] || LOGO_SIZE.M);
  if (pos === "center") w = Math.min(w, bh * 0.3 * LOGO.w / LOGO.h);
  const h = w * LOGO.h / LOGO.w, cx = (b[0] + b[2]) / 2, gap = h * 0.35;
  const cy = pos === "above" ? b[1] - gap - h / 2 : pos === "below" ? b[3] + gap + h / 2 : (b[1] + b[3]) / 2;
  return { x: cx - w / 2, y: cy - h / 2, w, h, plate: pos === "center" };
}
function logoSvg(it) {
  const L = logoPlace(it, symBox(it)); if (!L) return "";
  const k = L.w / LOGO.w, pad = L.h * 0.16, f = v => v.toFixed(2);
  return (L.plate ? `<rect data-id="${it.id}" x="${f(L.x - pad)}" y="${f(L.y - pad)}" width="${f(L.w + 2 * pad)}" height="${f(L.h + 2 * pad)}" rx="${f(pad)}" fill="#ffffff" fill-opacity="0.94"/>` : "") +
    `<path data-id="${it.id}" d="${LOGO.d}" fill="${LOGO.color}" transform="translate(${f(L.x)} ${f(L.y)}) scale(${k.toFixed(5)})"/>`;
}
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
function symBox(it) {
  const s = symOf(it), T = symXform(it), [x, y, w, h] = s.box;
  const c = [[x, y], [x + w, y], [x, y + h], [x + w, y + h]].map(T);
  return [Math.min(...c.map(p => p[0])), Math.min(...c.map(p => p[1])), Math.max(...c.map(p => p[0])), Math.max(...c.map(p => p[1]))];
}
function bboxOf(it) {
  if (it.type === "sym") {
    const b = symBox(it), L = logoPlace(it, b);
    return L ? [Math.min(b[0], L.x), Math.min(b[1], L.y), Math.max(b[2], L.x + L.w), Math.max(b[3], L.y + L.h)] : b;
  }
  if (it.type === "dim") return dimBox(it);
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
      symInner(`${it.product}|${it.size}|${it.variant}`, it.color, it.arrow, it.rot, it.flip) + `</g>` + logoSvg(it);
  }
  if (it.type === "dim") return dimSvg(it);
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
  if (!it.label && !it.len) return "";
  const od = PIPE[it.nps][0], fs = Math.max(9, od * 0.42);
  // text along segment i, never upside down; side +1 sits above the run (size label), -1 below (run length)
  const along = (i, txt, side) => {
    const a = it.pts[i], b = it.pts[i + 1], mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2;
    let ang = Math.atan2(b[1] - a[1], b[0] - a[0]) * 180 / Math.PI;
    if (ang > 90) ang -= 180; if (ang <= -90) ang += 180;
    const r = ang * Math.PI / 180, off = side > 0 ? od / 2 + fs * 0.45 : -(od / 2 + fs * 1.05), tx = mx + Math.sin(r) * off, ty = my - Math.cos(r) * off;
    return `<text data-id="${it.id}" x="${tx.toFixed(2)}" y="${ty.toFixed(2)}" font-family="Arial, Helvetica, sans-serif" font-size="${fs.toFixed(1)}" fill="#13233b" text-anchor="middle"` +
      (Math.abs(ang) > 0.5 ? ` transform="rotate(${ang.toFixed(1)} ${tx.toFixed(2)} ${ty.toFixed(2)})"` : "") + `>${esc(txt)}</text>`;
  };
  const lens = it.pts.slice(1).map((p, i) => Math.hypot(p[0] - it.pts[i][0], p[1] - it.pts[i][1]));
  let o = "";
  if (it.label) { const bi = lens.indexOf(Math.max(...lens)); o += along(bi, `${it.nps} SCH ${it.sch}`, 1); }
  // run lengths are centreline lengths, point to point (to where the turns' centrelines meet)
  if (it.len) lens.forEach((l, i) => { if (l >= fs * 2) o += along(i, fmtLen(l), -1); });
  return o;
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
function snapTargets(skip) {
  const t = [], skipped = id => skip instanceof Set ? skip.has(id) : id === skip;
  for (const it of doc.items) {
    if (skipped(it.id) || !valid(it)) continue;
    if (it.type === "sym") {
      const T = symXform(it);
      for (const p of symOf(it).ports) { const w = T(p); if (p.length > 2) w.push(it.rot + (it.flip ? 180 - p[2] : p[2])); t.push(w); }
    }
    if (it.type === "pipe") t.push(it.pts[0], it.pts[it.pts.length - 1]);
  }
  return t;
}
const gridSnap = v => Math.round(v / GRID) * GRID;
// Pipe runs drawn with the mouse step in whole inches (or half inches) so they read cleanly; 5 mm in mm or at 1/16".
const lenStep = () => doc.style.units === "mm" || doc.style.prec < 0.2 ? GRID : doc.style.prec * 25.4;
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
    const st = lenStep(), len = Math.max(0, Math.round((dx * u[0] + dy * u[1]) / st) * st);
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
// Dimension points snap to product connections, every pipe point (ends and turns), then pipe centrelines and the grid.
function dimSnap(p) {
  const tol = 11 / ui.view.s, t = snapTargets(null);
  for (const it of doc.items) if (it.type === "pipe") t.push(...it.pts);
  let best = null, bd = tol;
  for (const q of t) { const d = Math.hypot(q[0] - p[0], q[1] - p[1]); if (d < bd) { bd = d; best = q; } }
  return best ? [best[0], best[1]] : snapPoint(p, null, null, true).slice(0, 2);
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
  if (ui.tool === "pipe" || ui.tool === "dim" || ui.drag) for (const t of snapTargets(ui.drag && ui.drag.ids ? new Set(ui.drag.ids) : ui.drag && ui.drag.id)) o += `<circle cx="${t[0]}" cy="${t[1]}" r="${4 * px}" fill="#fff" stroke="#1f5fae" stroke-width="${1.5 * px}" pointer-events="none"/>`;
  const sel = selected(), many = selItems();
  if (many.length > 1) {
    const B = many.map(bboxOf), b = [Math.min(...B.map(q => q[0])), Math.min(...B.map(q => q[1])), Math.max(...B.map(q => q[2])), Math.max(...B.map(q => q[3]))], m = 6 * px;
    for (const q of B) o += `<rect x="${q[0]}" y="${q[1]}" width="${q[2] - q[0]}" height="${q[3] - q[1]}" fill="none" stroke="#1f5fae" stroke-opacity="0.35" stroke-width="${px}" pointer-events="none"/>`;
    o += `<rect x="${b[0] - m}" y="${b[1] - m}" width="${b[2] - b[0] + 2 * m}" height="${b[3] - b[1] + 2 * m}" fill="none" stroke="#1f5fae" stroke-width="${1.5 * px}" stroke-dasharray="${5 * px} ${4 * px}" pointer-events="none"/>`;
  }
  if (ui.drag && ui.drag.kind === "box" && ui.drag.cur) {
    const a = ui.drag.start, c = ui.drag.cur;
    o += `<rect x="${Math.min(a[0], c[0])}" y="${Math.min(a[1], c[1])}" width="${Math.abs(c[0] - a[0])}" height="${Math.abs(c[1] - a[1])}" fill="#1f5fae" fill-opacity="0.06" stroke="#1f5fae" stroke-width="${px}" stroke-dasharray="${4 * px} ${3 * px}" pointer-events="none"/>`;
  }
  if (sel && valid(sel)) {
    const b = bboxOf(sel), m = 4 * px;
    o += `<rect x="${b[0] - m}" y="${b[1] - m}" width="${b[2] - b[0] + 2 * m}" height="${b[3] - b[1] + 2 * m}" fill="none" stroke="#1f5fae" stroke-width="${1.5 * px}" stroke-dasharray="${5 * px} ${4 * px}" pointer-events="none"/>`;
    const dg = sel.type === "dim" ? dimGeom(sel) : null;
    const hs = sel.type === "pipe" ? sel.pts : sel.type === "arrow" ? [sel.a, sel.b] :
      dg ? [sel.a, sel.b, [(dg.p1[0] + dg.p2[0]) / 2, (dg.p1[1] + dg.p2[1]) / 2]] : [];
    hs.forEach((p, i) => { o += `<rect data-h="${i}" x="${p[0] - 5 * px}" y="${p[1] - 5 * px}" width="${10 * px}" height="${10 * px}" fill="#fff" stroke="#1f5fae" stroke-width="${1.5 * px}" style="cursor:move"/>`; });
  }
  if (ui.draft) {
    const pts = ui.cursor ? [...ui.draft.pts, ui.cursor] : ui.draft.pts;
    if (ui.tool === "pipe" && pts.length > 1) {
      const od = PIPE[ui.pipe.nps][0];
      o += `<path d="${pipePath(pts, ui.pipe.nps)}" fill="none" stroke="${ui.pipe.color}" stroke-opacity="0.55" stroke-width="${od}" stroke-linejoin="round" pointer-events="none"/>`;
    }
    if (ui.tool === "arrow" && pts.length > 1) o += `<line x1="${pts[0][0]}" y1="${pts[0][1]}" x2="${pts[1][0]}" y2="${pts[1][1]}" stroke="#1f5fae" stroke-width="${1.5 * px}" pointer-events="none"/>`;
    if (ui.tool === "dim") {
      const d = ui.draft;
      if (d.pts.length === 1 && ui.cursor) o += `<line x1="${d.pts[0][0]}" y1="${d.pts[0][1]}" x2="${ui.cursor[0]}" y2="${ui.cursor[1]}" stroke="#1f5fae" stroke-width="${1.5 * px}" stroke-dasharray="${5 * px} ${4 * px}" pointer-events="none"/>`;
      if (d.pts.length === 2) o += `<g pointer-events="none" opacity="0.75">${dimSvg(dimDraft(ui.cursor))}</g>`;
    }
    pts.forEach(p => { o += `<circle cx="${p[0]}" cy="${p[1]}" r="${3 * px}" fill="#1f5fae" pointer-events="none"/>`; });
  }
  cv.innerHTML = o;
  const choices = [0.5, 1, 2, 4, 6, 12, 24, 48, 96], inches = choices.find(c => c * 25.4 * v.s >= 60) || 96, bar = $("scalebar");
  bar.querySelector("i").style.width = (inches * 25.4 * v.s).toFixed(1) + "px";
  bar.querySelector("span").textContent = inches >= 12 ? `${inches / 12} ft` : `${inches} in`;
  $("board").className = "board t-" + ui.tool;
  $("tip").textContent = { select: many.length > 1 ? `${many.length} items. Drag to move them together. Ctrl+G groups, Ctrl+Shift+G ungroups.` :
      sel ? "Drag to move. Delete removes it. Shift+click adds to the selection." : "Click an item to select it. Shift+drag a box to select several. Drag the sheet to pan, scroll to zoom.",
    pipe: ui.draft ? "Aim with the mouse and type a length, then Enter. Or click. Double-click or Enter on an empty box finishes, Esc cancels." : "Click to start a pipe. It snaps to product connections (blue dots).",
    text: "Click where the label goes.", arrow: ui.draft ? "Click where the arrow points." : "Click where the arrow starts.",
    dim: !ui.draft ? "Click the first point. It snaps to connections and pipe ends and turns." : ui.draft.pts.length === 1 ? "Click the second point." :
      "Move to place the dimension line, then click. Esc cancels." }[ui.tool];
}
// The dimension being placed: its two points are set, the cursor sets the offset of the dimension line.
function dimDraft(cur) {
  const [a, b] = ui.draft.pts, it = { id: 0, type: "dim", a, b, mode: ui.dim.mode, off: 0, color: ui.dim.color, size: 1 };
  const g = dimGeom(it);
  it.size = ui.dim.size || autoDimSize(g.L);
  if (cur) it.off = Math.round(((cur[0] - a[0]) * g.n[0] + (cur[1] - a[1]) * g.n[1]) * 100) / 100;
  return it;
}
const selected = () => doc.items.find(i => i.id === ui.sel) || null;
// Selection: ui.set holds every selected id; ui.sel is that id when exactly one item is selected (the panel edits it).
function selectIds(ids) { ui.set = [...new Set(ids)]; ui.sel = ui.set.length === 1 ? ui.set[0] : null; }
const selItems = () => ui.set.map(id => doc.items.find(i => i.id === id)).filter(Boolean);
const groupOf = it => it.grp ? doc.items.filter(i => i.grp === it.grp) : [it];
const nextGrp = () => 1 + Math.max(0, ...doc.items.map(i => i.grp || 0));

// ---------------------------------------------------------------- history and storage
function commit() {
  const j = JSON.stringify(doc);
  if (j !== hist[hi]) { hist = hist.slice(0, hi + 1); hist.push(j); hi++; if (hist.length > 80) { hist.shift(); hi--; } }
  try { localStorage.setItem("sdg-doc", j); } catch (e) {}
  projAutosave(j);
  refresh();
}
function loadDoc(d) {
  if (!d || !Array.isArray(d.items)) throw new Error("bad file");
  doc = { v: 1, style: Object.assign({}, STYLE0, d.style || {}), items: d.items.filter(i => i && ["sym", "pipe", "text", "arrow", "dim"].includes(i.type) && (i.type !== "pipe" || PIPE[i.nps])) };
  doc.items.forEach(i => { i.id = nextId++; });
  selectIds([]); ui.draft = null;
}
function step(n) { if (hist[hi + n] === undefined) return; hi += n; const keep = ui.view; loadDoc(JSON.parse(hist[hi])); ui.view = keep; try { localStorage.setItem("sdg-doc", hist[hi]); } catch (e) {} refresh(); }
function refresh() { draw(); panel(); projLabel(); }

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
  $("gDim").hidden = !(kind === "dim" || (!sel && ui.tool === "dim"));
  const many = selItems(), grouped = many.length > 1 && many.every(i => i.grp && i.grp === many[0].grp);
  $("gSel").hidden = many.length < 2;
  if (many.length > 1) {
    $("gProduct").hidden = true;
    $("selTitle").textContent = grouped ? `Group of ${many.length}` : `${many.length} items selected`;
    $("selHint").textContent = grouped ? "Moves, copies, rotates and deletes as one. Alt+click an item in the group to edit just that item." :
      "Drag any of them to move them together. Group them to keep them together.";
  }
  $("bGroup").disabled = many.length < 2 || grouped; $("bUngroup").disabled = !many.some(i => i.grp);
  ["Select", "Pipe", "Text", "Arrow", "Dim"].forEach(t => $("t" + t).setAttribute("aria-pressed", ui.tool === t.toLowerCase()));
  $("bRot").disabled = !(kind === "sym" || kind === "pipe" || many.length > 1); $("bFlip").disabled = kind !== "sym";
  $("bRot").textContent = kind === "pipe" ? "Rotate 45°" : "Rotate"; $("bDup").disabled = $("bDel").disabled = !many.length;
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
    $("sizeLabel").textContent = p.sizeLabel || "Size";
    // Spirax Sarco logo: on/off, where it sits and how big
    $("logoWrap").hidden = !LOGO;
    $("symLogo").checked = !!tgt.logo; $("symLogo").onchange = e => set("logo", e.target.checked);
    $("logoOpts").hidden = !tgt.logo;
    chipRow($("logoPos"), LOGO_POS.map(v => v[0]), tgt.logoPos || "center", v => set("logoPos", v), v => LOGO_POS.find(q => q[0] === v)[1]);
    chipRow($("logoSize"), Object.keys(LOGO_SIZE), tgt.logoSize || "M", v => set("logoSize", v), v => ({ S: "Small", M: "Medium", L: "Large" })[v]);
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
    $("prodNote").hidden = !p.note; $("prodNote").textContent = p.note || "";
  }

  // pipe
  const pt = kind === "pipe" ? sel : ui.pipe, pe = kind === "pipe", pset = (k, v) => { pt[k] = v; if (pe) commit(); else refresh(); };
  $("pipeTitle").textContent = pe ? "Selected pipe" : "Pipe"; $("pipeHint").hidden = pe;
  if (!$("nps").options.length) Object.keys(PIPE).forEach(k => { const o = document.createElement("option"); o.value = k; o.textContent = k; $("nps").appendChild(o); });
  $("nps").value = pt.nps; $("sch").value = String(pt.sch); $("pipeLabel").checked = !!pt.label; $("pipeCut").checked = !!pt.cut;
  $("nps").onchange = e => pset("nps", e.target.value); $("sch").onchange = e => pset("sch", +e.target.value);
  $("pipeLabel").onchange = e => pset("label", e.target.checked); $("pipeCut").onchange = e => pset("cut", e.target.checked);
  $("pipeLen").checked = !!pt.len; $("pipeLen").onchange = e => pset("len", e.target.checked);
  swatches($("pipeColors"), pt.color, v => pset("color", v));
  // lengths: type the next run while drawing, or edit any run of the selected pipe
  $("runNext").hidden = pe || ui.tool !== "pipe";
  const runs = $("runs"); runs.hidden = !pe;
  if (pe && !runs.contains(document.activeElement)) {
    runs.innerHTML = `<div class="row"><label>Run lengths (centreline, point to point)</label></div>`;
    const ARR = ["→", "↘", "↓", "↙", "←", "↖", "↑", "↗"];
    sel.pts.slice(1).forEach((q, i) => {
      const a = sel.pts[i], L = Math.hypot(q[0] - a[0], q[1] - a[1]), ang = Math.atan2(q[1] - a[1], q[0] - a[0]) * 180 / Math.PI;
      const r = document.createElement("div"); r.className = "row run";
      r.innerHTML = `<label for="run${i}">${i + 1}. ${ARR[(Math.round(ang / 45) + 8) % 8]}</label><input id="run${i}" type="text" inputmode="decimal" autocomplete="off">` +
        `<span class="meta">${esc(fmtLen(L, doc.style.units === "mm" ? "ftin" : "mm"))}</span>`;
      const inp = r.querySelector("input"); inp.value = fmtLen(L);
      inp.addEventListener("change", () => { const v = parseLen(inp.value); if (v) setRunLength(sel, i, v); else { say(`"${inp.value}" isn't a length I can read. Try 24, 2'-6" or 600mm.`, "warn"); panel(); } });
      inp.addEventListener("keydown", e => { if (e.key === "Enter") inp.blur(); });
      runs.appendChild(r);
    });
  }
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

  // dimensions, and the units used for every length on the drawing
  const dt = kind === "dim" ? sel : ui.dim, de = kind === "dim", dset = (k, v) => { dt[k] = v; if (de) commit(); else panel(); };
  $("dimTitle").textContent = de ? "Selected dimension" : "Dimension"; $("dimHint").hidden = de;
  chipRow($("dimMode"), ["aligned", "h", "v"], dt.mode, v => dset("mode", v), v => ({ aligned: "Aligned", h: "Horizontal", v: "Vertical" })[v]);
  if (document.activeElement !== $("dimSize")) $("dimSize").value = dt.size || "";
  $("dimSize").placeholder = "Auto";
  $("dimSize").oninput = e => { const v = +e.target.value; dt.size = v ? Math.max(3, Math.min(400, v)) : (de ? autoDimSize(dimGeom(dt).L) : 0);
    if (de) { draw(); clearTimeout(panel.t); panel.t = setTimeout(commit, 500); } };
  swatches($("dimColors"), dt.color, v => dset("color", v));
  $("dimMeta").textContent = de ? `Measures ${fmtLen(dimGeom(sel).L, "ftin")} · ${fmtLen(dimGeom(sel).L, "mm")}` : "";
  chipRow($("units"), UNITS.map(u => u[0]), doc.style.units, v => { doc.style.units = v; commit(); }, v => UNITS.find(u => u[0] === v)[1]);
  $("precRow").hidden = doc.style.units === "mm";
  chipRow($("prec"), PRECS.map(p => p[0]), doc.style.prec, v => { doc.style.prec = v; commit(); }, v => PRECS.find(p => p[0] === v)[1]);
}

// ---------------------------------------------------------------- actions
function setTool(t) { ui.tool = t; ui.draft = null; ui.cursor = null; if (t !== "select") selectIds([]); refresh(); }
function addProduct() {
  const k = ui.pick, it = { id: nextId++, type: "sym", product: k.product, size: k.size, variant: k.variant, color: k.color, arrow: k.arrow, rot: 0, flip: false, x: ui.view.cx, y: ui.view.cy,
    logo: !!k.logo, logoPos: k.logoPos, logoSize: k.logoSize };
  doc.items.push(it); snapSym(it); selectIds([it.id]); ui.tool = "select"; commit();
}
function finishPipe() {
  const d = ui.draft; ui.draft = null; ui.cursor = null;
  if (d && d.pts.length > 1) { const it = Object.assign({ id: nextId++, type: "pipe", pts: d.pts }, ui.pipe); doc.items.push(it); commit(); } else refresh();
}
function del() { if (!ui.set.length) return; const k = new Set(ui.set); doc.items = doc.items.filter(i => !k.has(i.id)); selectIds([]); commit(); }
// move an item by (dx, dy) from its saved copy o
function shiftItem(it, o, dx, dy) {
  if (it.type === "pipe") it.pts = o.pts.map(p => [p[0] + dx, p[1] + dy]);
  else if (it.type === "arrow" || it.type === "dim") { it.a = [o.a[0] + dx, o.a[1] + dy]; it.b = [o.b[0] + dx, o.b[1] + dy]; }
  else { it.x = o.x + dx; it.y = o.y + dy; }
}
function dup() {
  const src = selItems(); if (!src.length) return;
  const g = new Map(), out = [];
  for (const s of src) {
    const c = JSON.parse(JSON.stringify(s)); c.id = nextId++;
    if (c.grp) { if (!g.has(c.grp)) g.set(c.grp, nextGrp() + g.size); c.grp = g.get(c.grp); }
    shiftItem(c, s, 20, 20); doc.items.push(c); out.push(c.id);
  }
  selectIds(out); commit();
}
function group() { const m = selItems(); if (m.length < 2) return; const g = nextGrp(); m.forEach(i => { i.grp = g; }); commit(); say(`Grouped ${m.length} items.`, "ok"); }
function ungroup() { const m = selItems(); if (!m.some(i => i.grp)) return; m.forEach(i => { delete i.grp; }); commit(); say("Ungrouped.", "ok"); }
// several items: turn 90 degrees clockwise about the middle of the selection
function rotateSet(m) {
  const B = m.map(bboxOf), cx = gridSnap((Math.min(...B.map(q => q[0])) + Math.max(...B.map(q => q[2]))) / 2), cy = gridSnap((Math.min(...B.map(q => q[1])) + Math.max(...B.map(q => q[3]))) / 2);
  const R = p => [Math.round((cx - (p[1] - cy)) * 100) / 100, Math.round((cy + (p[0] - cx)) * 100) / 100];
  for (const it of m) {
    if (it.type === "pipe") it.pts = it.pts.map(R);
    else if (it.type === "arrow" || it.type === "dim") { it.a = R(it.a); it.b = R(it.b); if (it.type === "dim" && it.mode !== "aligned") it.mode = it.mode === "h" ? "v" : "h"; }
    else { [it.x, it.y] = R([it.x, it.y]); if (it.type === "sym") it.rot = (it.rot + 90) % 360; }
  }
  commit();
}
// change one run of a pipe to length L; the points after it move along with it
function setRunLength(it, i, L) {
  const a = it.pts[i], b = it.pts[i + 1], l = Math.hypot(b[0] - a[0], b[1] - a[1]); if (!l) return;
  const dx = (b[0] - a[0]) / l * (L - l), dy = (b[1] - a[1]) / l * (L - l);
  it.pts = it.pts.map((p, j) => j > i ? [Math.round((p[0] + dx) * 100) / 100, Math.round((p[1] + dy) * 100) / 100] : p);
  commit();
}
// while drawing a pipe: add a run of length L toward the mouse (or straight on)
function typedRun(L) {
  const d = ui.draft; if (!d) { say("Click where the pipe starts first, then type the length.", "warn"); return; }
  const a = d.pts[d.pts.length - 1];
  let u = ui.cursor && Math.hypot(ui.cursor[0] - a[0], ui.cursor[1] - a[1]) > 0.5 ? [ui.cursor[0] - a[0], ui.cursor[1] - a[1]] :
    d.pts.length > 1 ? [a[0] - d.pts[d.pts.length - 2][0], a[1] - d.pts[d.pts.length - 2][1]] : [1, 0];
  const l = Math.hypot(u[0], u[1]); u = [u[0] / l, u[1] / l];
  const p = [Math.round((a[0] + u[0] * L) * 100) / 100, Math.round((a[1] + u[1] * L) * 100) / 100];
  d.pts.push(p); ui.cursor = [p[0] + u[0] * 0.001, p[1] + u[1] * 0.001]; draw();
}
function rotate() {
  const m = selItems(); if (m.length > 1) { rotateSet(m); return; }
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
    else { const it = { id: nextId++, type: "arrow", a: ui.draft.pts[0], b: p, color: ui.arrow.color, w: 1.6 }; ui.draft = null; doc.items.push(it); selectIds([it.id]); ui.tool = "select"; commit(); }
    return;
  }
  if (ui.tool === "dim") {
    if (!ui.draft || ui.draft.pts.length < 2) {
      const p = dimSnap(w);
      if (!ui.draft) ui.draft = { pts: [p] };
      else if (Math.hypot(p[0] - ui.draft.pts[0][0], p[1] - ui.draft.pts[0][1]) > 0.5) { ui.draft.pts.push(p); ui.cursor = w; }
      draw();
    } else {
      const it = dimDraft(w); it.id = nextId++; ui.draft = null; ui.cursor = null;
      doc.items.push(it); selectIds([it.id]); commit();
    }
    return;
  }
  if (ui.tool === "text") {
    const it = { id: nextId++, type: "text", x: gridSnap(w[0]), y: gridSnap(w[1]), text: ui.text.text || "Label", size: ui.text.size, color: ui.text.color };
    doc.items.push(it); selectIds([it.id]); ui.tool = "select"; commit(); $("textVal").focus(); $("textVal").select();
    return;
  }
  const h = e.target.closest("[data-h]"), g = e.target.closest("[data-id]");
  cv.setPointerCapture(e.pointerId);
  if (h && selected()) { ui.drag = { kind: "handle", id: ui.sel, i: +h.dataset.h, moved: false }; return; }
  if (g) {
    const id = +g.dataset.id, it = doc.items.find(i => i.id === id), ids = (e.altKey ? [it] : groupOf(it)).map(i => i.id);
    if (e.shiftKey) {                                     // add to the selection, or take back out
      const on = ids.every(i => ui.set.includes(i));
      selectIds(on ? ui.set.filter(i => !ids.includes(i)) : [...ui.set, ...ids]);
    } else if (!(ui.set.length > 1 && ui.set.includes(id))) selectIds(ids);
    const move = selItems();
    if (move.length) ui.drag = { kind: "move", id: move.length === 1 ? move[0].id : null, ids: move.map(i => i.id), start: w,
      orig: Object.fromEntries(move.map(i => [i.id, JSON.stringify(i)])), moved: false };
    refresh();
    return;
  }
  if (e.shiftKey) { ui.drag = { kind: "box", start: w, cur: null, base: [...ui.set], moved: false }; return; }
  selectIds([]); ui.drag = { kind: "pan", sx: e.clientX, sy: e.clientY, cx: ui.view.cx, cy: ui.view.cy, moved: false }; refresh();
});
cv.addEventListener("pointermove", e => {
  const w = toWorld(e), d = ui.drag;
  if (!d) {
    if (ui.draft) { const prev = ui.draft.pts[ui.draft.pts.length - 1];
      ui.cursor = ui.tool === "pipe" ? snapPoint(w, prev, null, e.altKey, ui.draft.pts.length === 1 ? ui.draft.dir : null).slice(0, 2) :
        ui.tool === "dim" && ui.draft.pts.length === 1 ? dimSnap(w) : w; draw(); }
    return;
  }
  if (d.kind === "pan") { ui.view.cx = d.cx - (e.clientX - d.sx) / ui.view.s; ui.view.cy = d.cy - (e.clientY - d.sy) / ui.view.s; d.moved = true; draw(); return; }
  if (d.kind === "box") { d.cur = w; d.moved = true; draw(); return; }
  if (d.kind === "move" && d.ids.length > 1) {              // several items move together, on the grid or onto a connection
    const dx = w[0] - d.start[0], dy = w[1] - d.start[1], items = d.ids.map(i => doc.items.find(q => q.id === i)).filter(Boolean);
    items.forEach(it => shiftItem(it, JSON.parse(d.orig[it.id]), dx, dy));
    const tol = 11 / ui.view.s, targets = snapTargets(new Set(d.ids)), mine = [];
    for (const it of items) { if (it.type === "sym") mine.push(...portsOf(it)); if (it.type === "pipe") mine.push(it.pts[0], it.pts[it.pts.length - 1]); }
    let best = null, bd = tol;
    for (const p of mine) for (const t of targets) { const q = Math.hypot(t[0] - p[0], t[1] - p[1]); if (q < bd) { bd = q; best = [t[0] - p[0], t[1] - p[1]]; } }
    const sx = best ? dx + best[0] : gridSnap(dx), sy = best ? dy + best[1] : gridSnap(dy);
    items.forEach(it => shiftItem(it, JSON.parse(d.orig[it.id]), sx, sy));
    d.moved = true; draw(); return;
  }
  const it = doc.items.find(i => i.id === d.id); if (!it) return;
  d.moved = true;
  if (d.kind === "handle") {
    if (it.type === "pipe") it.pts[d.i] = snapPoint(w, null, it.id, true).slice(0, 2);
    else if (it.type === "dim") {
      if (d.i < 2) it[d.i ? "b" : "a"] = dimSnap(w);
      else { const g = dimGeom(it); it.off = Math.round(((w[0] - it.a[0]) * g.n[0] + (w[1] - it.a[1]) * g.n[1]) * 100) / 100; }
    } else it[d.i ? "b" : "a"] = [Math.round(w[0]), Math.round(w[1])];
  } else {
    const o = JSON.parse(d.orig[it.id]), dx = w[0] - d.start[0], dy = w[1] - d.start[1];
    if (it.type === "pipe") { const sx = gridSnap(dx), sy = gridSnap(dy); it.pts = o.pts.map(p => [p[0] + sx, p[1] + sy]); }
    else if (it.type === "arrow") { it.a = [o.a[0] + dx, o.a[1] + dy]; it.b = [o.b[0] + dx, o.b[1] + dy]; }
    else if (it.type === "dim") { const sx = gridSnap(dx), sy = gridSnap(dy); it.a = [o.a[0] + sx, o.a[1] + sy]; it.b = [o.b[0] + sx, o.b[1] + sy]; }
    else { it.x = o.x + dx; it.y = o.y + dy; if (it.type === "sym") snapSym(it); else { it.x = gridSnap(it.x); it.y = gridSnap(it.y); } }
  }
  draw();
});
function endDrag() {
  const d = ui.drag; ui.drag = null;
  if (d && d.kind === "box") {
    if (d.cur) {
      const x0 = Math.min(d.start[0], d.cur[0]), x1 = Math.max(d.start[0], d.cur[0]), y0 = Math.min(d.start[1], d.cur[1]), y1 = Math.max(d.start[1], d.cur[1]);
      const hit = doc.items.filter(valid).filter(i => { const b = bboxOf(i); return b[0] >= x0 && b[2] <= x1 && b[1] >= y0 && b[3] <= y1; });
      selectIds([...d.base, ...hit.flatMap(i => groupOf(i).map(q => q.id))]);
    }
    refresh(); return;
  }
  if (d && d.moved && d.kind !== "pan") commit(); else draw();
}
cv.addEventListener("pointerup", endDrag); cv.addEventListener("pointercancel", endDrag);
cv.addEventListener("dblclick", e => {
  const g = e.target.closest("[data-id]"); if (ui.tool === "select" && g && selected() && selected().type === "text") { $("textVal").focus(); $("textVal").select(); } });
cv.addEventListener("wheel", e => { e.preventDefault(); zoom(e.deltaY < 0 ? 1.15 : 1 / 1.15, toWorld(e)); }, { passive: false });
window.addEventListener("keydown", e => {
  if (/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) return;
  const k = e.key.toLowerCase(), mod = e.ctrlKey || e.metaKey;
  if (k === "escape") { if (ui.draft) { ui.draft = null; ui.cursor = null; draw(); } else setTool("select"); }
  else if (k === "enter" && ui.tool === "pipe") finishPipe();
  else if ((k === "delete" || k === "backspace") && ui.set.length) { e.preventDefault(); del(); }
  else if (mod && k === "g") { e.preventDefault(); if (e.shiftKey) ungroup(); else group(); }
  else if (mod && k === "a") { e.preventDefault(); setTool("select"); selectIds(doc.items.filter(valid).map(i => i.id)); refresh(); }
  else if (ui.tool === "pipe" && ui.draft && !mod && /^[0-9.]$/.test(e.key)) { e.preventDefault(); const r = $("runLen"); r.focus(); r.value += e.key; }
  else if (mod && k === "z") { e.preventDefault(); step(e.shiftKey ? 1 : -1); }
  else if (mod && k === "y") { e.preventDefault(); step(1); }
  else if (mod && k === "d") { e.preventDefault(); dup(); }
  else if (k === "r" && !mod) rotate(); else if (k === "m" && !mod) mirror();
  else if (k === "v" && !mod) setTool("select"); else if (k === "p" && !mod) setTool("pipe"); else if (k === "t" && !mod) setTool("text");
  else if (k === "d" && !mod) setTool("dim");
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
  r.onload = () => { try { const d = JSON.parse(r.result); if (d && d.sdgProject) { importProject(d, f.name); return; } loadDoc(d); proj.cur = {}; projSave(); fit(); commit(); say(`Opened ${f.name}`, "ok"); } catch (err) { say("That file isn't a drawing saved from this page.", "warn"); } };
  r.readAsText(f); e.target.value = "";
});
let clearArmed = 0;
$("clearBtn").addEventListener("click", () => {
  if (Date.now() - clearArmed < 4000) { doc.items = []; selectIds([]); clearArmed = 0; $("clearBtn").textContent = "Clear"; commit(); say("Cleared. Undo brings it back."); }
  else { clearArmed = Date.now(); $("clearBtn").textContent = "Click again to clear"; setTimeout(() => { $("clearBtn").textContent = "Clear"; }, 4000); }
});

// ---------------------------------------------------------------- projects
// Drawings saved by name into projects, kept in this browser's storage. The open drawing saves itself as you work.
// Export writes a project to one .json file (a backup, or a way to move it to another computer); Open or Import reads it back.
const PKEY = "sdg-projects";
const proj = (() => { try { const p = JSON.parse(localStorage.getItem(PKEY)); if (p && Array.isArray(p.projects)) return Object.assign({ cur: {} }, p); } catch (e) {} return { v: 1, projects: [], cur: {} }; })();
const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
const projOf = id => proj.projects.find(p => p.id === id);
function curDrawing() { const p = projOf(proj.cur.p), d = p && p.drawings.find(q => q.id === proj.cur.d); return d ? { p, d } : null; }
function projSave() {
  try { localStorage.setItem(PKEY, JSON.stringify(proj)); return true; }
  catch (e) { say("Browser storage is full. Export a project and delete it here to make room.", "warn"); return false; }
}
function projAutosave(j) {
  const c = curDrawing(); if (!c) return;
  c.d.doc = JSON.parse(j); c.d.updated = Date.now();
  clearTimeout(projAutosave.t); projAutosave.t = setTimeout(projSave, 300);
}
function projLabel() {
  const c = curDrawing(), el = $("curName");
  if (el) el.innerHTML = c ? `<b>${esc(c.p.name)}</b> › ${esc(c.d.name)}` : "Not saved to a project";
}
const when = t => new Date(t).toLocaleString([], { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
function freeName(list, base) { let n = base, k = 2; while (list.some(x => x.name === n)) n = `${base} (${k++})`; return n; }
function openDrawing(p, d) {
  loadDoc(d.doc || { items: [] }); proj.cur = { p: p.id, d: d.id }; projSave();
  hist = []; hi = -1; fit(); commit(); requestAnimationFrame(() => { fit(); draw(); });
  say(`Opened ${d.name}`, "ok");
}
function importProject(data, fname) {
  const name = freeName(proj.projects, data.name || fname.replace(/\.json$/i, "").replace(/\.sdgproj$/i, "") || "Imported project");
  const p = { id: uid(), name, drawings: (data.drawings || []).filter(d => d && d.doc && Array.isArray(d.doc.items))
    .map(d => ({ id: uid(), name: d.name || "Drawing", updated: d.updated || Date.now(), doc: d.doc })) };
  proj.projects.push(p); ui.projSel = p.id; projSave(); projDialog();
  say(`Imported project ${name} (${p.drawings.length} drawings).`, "ok");
}
function projDialog() {
  const dlg = $("projDlg");
  if (!projOf(ui.projSel)) ui.projSel = (projOf(proj.cur.p) || proj.projects[0] || {}).id;
  const P = projOf(ui.projSel), pl = $("projList"), dl = $("drwList");
  pl.innerHTML = proj.projects.length ? "" : `<li class="empty">No projects yet. Name one below.</li>`;
  proj.projects.forEach(p => {
    const li = document.createElement("li"), b = document.createElement("button");
    b.type = "button"; b.className = "item"; b.setAttribute("aria-pressed", p.id === ui.projSel);
    b.innerHTML = `<span>${esc(p.name)}</span><small>${p.drawings.length} drawing${p.drawings.length === 1 ? "" : "s"}</small>`;
    b.addEventListener("click", () => { ui.projSel = p.id; projDialog(); });
    li.appendChild(b); pl.appendChild(li);
  });
  $("drwHead").textContent = P ? `Drawings in ${P.name}` : "Drawings";
  $("drwPane").hidden = !P;
  dl.innerHTML = P && P.drawings.length ? "" : `<li class="empty">No drawings in this project yet.</li>`;
  if (P) [...P.drawings].sort((a, b) => b.updated - a.updated).forEach(d => {
    const li = document.createElement("li"), open = proj.cur.p === P.id && proj.cur.d === d.id;
    li.className = "drw" + (open ? " open" : "");
    li.innerHTML = `<div class="dn"><span></span><small>${open ? "Open now · " : ""}saved ${esc(when(d.updated))} · ${((d.doc && d.doc.items) || []).length} item${((d.doc && d.doc.items) || []).length === 1 ? "" : "s"}</small></div>` +
      `<button type="button" class="btn sm" data-a="open">Open</button><button type="button" class="btn sm" data-a="ren">Rename</button><button type="button" class="btn sm" data-a="del">Delete</button>`;
    li.querySelector(".dn span").textContent = d.name;
    li.querySelector('[data-a="open"]').addEventListener("click", () => { openDrawing(P, d); dlg.close(); });
    li.querySelector('[data-a="ren"]').addEventListener("click", () => { const n = prompt("Drawing name", d.name); if (n && n.trim()) { d.name = n.trim(); projSave(); projDialog(); projLabel(); } });
    li.querySelector('[data-a="del"]').addEventListener("click", () => {
      if (!confirm(`Delete the drawing "${d.name}"? This can't be undone.`)) return;
      P.drawings = P.drawings.filter(q => q !== d); if (open) proj.cur = {}; projSave(); projDialog(); projLabel(); });
    dl.appendChild(li);
  });
  $("drwName").placeholder = P ? freeName(P.drawings, `Drawing ${P.drawings.length + 1}`) : "Drawing name";
}
$("projBtn").addEventListener("click", () => { ui.projSel = proj.cur.p || ui.projSel; projDialog(); $("projDlg").showModal(); });
$("projClose").addEventListener("click", () => $("projDlg").close());
$("projNew").addEventListener("click", () => {
  const n = $("projName").value.trim() || freeName(proj.projects, "Project " + (proj.projects.length + 1));
  const p = { id: uid(), name: freeName(proj.projects, n), drawings: [] }; proj.projects.push(p); ui.projSel = p.id;
  $("projName").value = ""; projSave(); projDialog();
});
$("projName").addEventListener("keydown", e => { if (e.key === "Enter") $("projNew").click(); });
$("drwSave").addEventListener("click", () => {
  const P = projOf(ui.projSel); if (!P) return;
  const d = { id: uid(), name: freeName(P.drawings, $("drwName").value.trim() || $("drwName").placeholder), updated: Date.now(), doc: JSON.parse(JSON.stringify(doc)) };
  P.drawings.push(d); proj.cur = { p: P.id, d: d.id }; $("drwName").value = "";
  if (projSave()) say(`Saved as ${d.name} in ${P.name}. Changes now save to it as you work.`, "ok");
  projDialog(); projLabel();
});
$("drwName").addEventListener("keydown", e => { if (e.key === "Enter") $("drwSave").click(); });
$("drwNew").addEventListener("click", () => {
  const P = projOf(ui.projSel); if (!P) return;
  if (!curDrawing() && doc.items.length && !confirm("The drawing on screen isn't saved to a project. Start a new blank drawing anyway?")) return;
  const d = { id: uid(), name: freeName(P.drawings, $("drwName").value.trim() || $("drwName").placeholder), updated: Date.now(), doc: { v: 1, style: Object.assign({}, doc.style), items: [] } };
  P.drawings.push(d); $("drwName").value = ""; openDrawing(P, d); $("projDlg").close();
});
$("projRename").addEventListener("click", () => { const P = projOf(ui.projSel); if (!P) return; const n = prompt("Project name", P.name);
  if (n && n.trim()) { P.name = n.trim(); projSave(); projDialog(); projLabel(); } });
$("projDelete").addEventListener("click", () => {
  const P = projOf(ui.projSel); if (!P) return;
  if (!confirm(`Delete the project "${P.name}" and its ${P.drawings.length} drawings? Export it first if you want a copy. This can't be undone.`)) return;
  proj.projects = proj.projects.filter(q => q !== P); if (proj.cur.p === P.id) proj.cur = {}; ui.projSel = null; projSave(); projDialog(); projLabel();
});
$("projExport").addEventListener("click", () => {
  const P = projOf(ui.projSel); if (!P) return;
  const data = { sdgProject: 1, name: P.name, exported: new Date().toISOString(), drawings: P.drawings.map(d => ({ name: d.name, updated: d.updated, doc: d.doc })) };
  const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([JSON.stringify(data)], { type: "application/json" }));
  a.download = `${P.name.replace(/[^\w .-]+/g, "_")}.sdgproj.json`; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 4000);
  say(`Exported ${P.name} to your downloads folder.`, "ok");
});
$("projImport").addEventListener("click", () => $("projFile").click());
$("projFile").addEventListener("change", e => {
  const f = e.target.files[0]; if (!f) return; const r = new FileReader();
  r.onload = () => {
    try {
      const d = JSON.parse(r.result);
      if (d && d.sdgProject) importProject(d, f.name);
      else if (d && Array.isArray(d.items)) {                 // a single drawing file goes into the selected project
        let P = projOf(ui.projSel);
        if (!P) { P = { id: uid(), name: freeName(proj.projects, "Imported"), drawings: [] }; proj.projects.push(P); ui.projSel = P.id; }
        P.drawings.push({ id: uid(), name: freeName(P.drawings, f.name.replace(/\.json$/i, "")), updated: Date.now(), doc: d });
        projSave(); projDialog(); say(`Added ${f.name} to ${P.name}.`, "ok");
      } else throw new Error("bad");
    } catch (err) { say("That file isn't a project or drawing saved from this page.", "warn"); }
  };
  r.readAsText(f); e.target.value = "";
});

// ---------------------------------------------------------------- wiring
[["tSelect", "select"], ["tPipe", "pipe"], ["tText", "text"], ["tArrow", "arrow"], ["tDim", "dim"]].forEach(([id, t]) => $(id).addEventListener("click", () => setTool(t)));
$("addBtn").addEventListener("click", addProduct);
$("bGroup").addEventListener("click", group); $("bUngroup").addEventListener("click", ungroup);
$("runLen").addEventListener("keydown", e => {
  if (e.key === "Enter") { e.preventDefault(); const t = e.target.value.trim(); if (!t) { finishPipe(); e.target.blur(); return; }
    const L = parseLen(t); if (L) { typedRun(L); e.target.value = ""; } else say(`"${t}" isn't a length I can read. Try 24, 2'-6" or 600mm.`, "warn"); }
  else if (e.key === "Escape") { e.target.value = ""; e.target.blur(); }
});
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
