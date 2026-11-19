// Equipment drawn from dimensions you type, not traced from a TI sheet: customer equipment comes in every size.
// Each builder returns the same shape of data as a product pack symbol (box, fill, strokes, ports, dims), plus
// grips: points you can drag to stretch it. All in millimetres, y down. Hidden parts (U-tube bundle, coil in a tank,
// vessel wall inside a jacket) are dashed. Nozzles are ASME B16.5 Class 150 flanged stubs and are the connection points.
// Loaded before app.js; uses PIPE from app.js only when a drawing is built.
(function () {
  const F150 = { '1/4"': [89, 11], '3/8"': [89, 11], '1/2"': [89, 11], '3/4"': [98, 13], '1"': [108, 14], '1-1/4"': [117, 16],
    '1-1/2"': [127, 18], '2"': [152, 19], '2-1/2"': [178, 22], '3"': [191, 24], '4"': [229, 24], '5"': [254, 24], '6"': [279, 25],
    '8"': [343, 29], '10"': [406, 30], '12"': [483, 32] };
  const od = n => (PIPE[n] || PIPE['1"'])[0];
  const r2 = v => Math.round(v * 100) / 100;
  const PI = Math.PI;
  const area = P => { let a = 0; for (let i = 0; i < P.length; i++) { const p = P[i], q = P[(i + 1) % P.length]; a += p[0] * q[1] - q[0] * p[1]; } return a / 2; };
  const cw = P => area(P) < 0 ? P.slice().reverse() : P;          // same winding everywhere so overlapping fills don't cancel
  const dp = (P, close = true) => "M" + P.map(p => `${r2(p[0])},${r2(p[1])}`).join("L") + (close ? "Z" : "");
  const rect = (x, y, w, h) => [[x, y], [x + w, y], [x + w, y + h], [x, y + h]];
  const arc = (cx, cy, rx, ry, a0, a1, n) => {
    n = n || Math.max(8, Math.ceil(Math.abs(a1 - a0) / (PI / 24)));
    const o = []; for (let i = 0; i <= n; i++) { const t = a0 + (a1 - a0) * i / n; o.push([cx + rx * Math.cos(t), cy + ry * Math.sin(t)]); } return o;
  };

  // collects outlined shapes, fill-only shapes, solid lines, thin lines and hidden (dashed) lines
  function Builder() { return { shapes: [], fills: [], lines: [], thin: [], hidden: [] }; }
  // flanged nozzle stub from (x, y) along unit vector u; returns the connection point [x, y, direction]
  function noz(b, x, y, u, nps, len) {
    const o = od(nps), F = F150[nps] || [o * 2, 15], n = [-u[1], u[0]];
    len = len || Math.max(100, 2.5 * o);
    const P = (a, w) => [x + u[0] * a + n[0] * w, y + u[1] * a + n[1] * w];
    b.shapes.push([P(-2, -o / 2), P(len, -o / 2), P(len, o / 2), P(-2, o / 2)]);
    b.shapes.push([P(len, -F[0] / 2), P(len + F[1], -F[0] / 2), P(len + F[1], F[0] / 2), P(len, F[0] / 2)]);
    const e = P(len + F[1], 0);
    return [r2(e[0]), r2(e[1]), Math.round(Math.atan2(u[1], u[0]) * 180 / PI)];
  }
  function finish(b, dims, ports, grips) {
    const all = [...b.shapes, ...b.fills, ...b.lines, ...b.thin, ...b.hidden].flat();
    const xs = all.map(p => p[0]), ys = all.map(p => p[1]);
    const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
    const lw = Math.max(0.8, Math.max(x1 - x0, y1 - y0) * 0.0012);
    const strokes = [];
    if (b.thin.length) strokes.push([r2(lw * 0.4), b.thin.map(P => dp(P, false)).join("")]);
    strokes.push([r2(lw), b.shapes.map(P => dp(P)).join("") + b.lines.map(P => dp(P, false)).join("")]);
    if (b.hidden.length) strokes.push([r2(lw * 0.75), b.hidden.map(P => dp(P, false)).join(""), `${r2(lw * 5)} ${r2(lw * 3.5)}`]);
    return { box: [r2(x0 - lw / 2), r2(y0 - lw / 2), r2(x1 - x0 + lw), r2(y1 - y0 + lw)], fill: [...b.shapes, ...b.fills].map(cw).map(P => dp(P)).join(""),
      strokes, arrow: null, ports, dims, grips: grips || [] };
  }
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

  // ------------------------------------------------------------ U-tube exchanger, horizontal, channel on the left
  // Origin: channel bonnet tangent line, on the centreline. Steam in the shell, process in the tubes.
  function utube(p, variant) {
    const b = Builder(), D = p.D, R = D / 2, h = D / 4, L = p.L, C = p.C;
    const f = Math.max(60, 0.12 * D), Rf = R + Math.max(50, 0.11 * D), x0 = C + f, x1 = x0 + L;
    b.shapes.push([...arc(0, 0, h, R, PI / 2, 1.5 * PI), [C, -R], [C, R]]);                 // bonnet head + channel
    b.shapes.push(rect(C, -Rf, f, 2 * Rf));                                                    // girth flanges + tubesheet
    b.lines.push([[C + f * 0.4, -Rf], [C + f * 0.4, Rf]], [[C + f * 0.6, -Rf], [C + f * 0.6, Rf]]);
    b.shapes.push([[x0, -R], [x1, -R], ...arc(x1, 0, h, R, -PI / 2, PI / 2), [x0, R]]);        // shell + far head
    b.lines.push([[0, -R], [0, R]], [[x1, -R], [x1, R]]);                                      // head tangent lines
    b.hidden.push([[0, 0], [C, 0]]);                                                           // pass partition
    const ro = 0.36 * D, ri = 0.1 * D, xb = x1 - 0.03 * L - ro, xt = C + f * 0.5;              // U-tube bundle envelope
    b.hidden.push([[xt, -ro], [xb, -ro], ...arc(xb, 0, ro, ro, -PI / 2, PI / 2), [xt, ro]]);
    b.hidden.push([[xt, -ri], [xb, -ri], ...arc(xb, 0, ri, ri, -PI / 2, PI / 2), [xt, ri]]);
    const nb = Math.max(1, Math.floor((xb - x0) / Math.max(D, 300)));                          // segmental baffles
    for (let i = 1; i <= nb; i++) { const x = x0 + (xb - x0) * i / (nb + 1), up = i % 2; b.hidden.push([[x, up ? -R * 0.92 : -R * 0.45], [x, up ? R * 0.45 : R * 0.92]]); }
    const steam = noz(b, x0 + Math.max(1.5 * od(p.ns), 0.12 * L), -R, [0, -1], p.ns);
    const cond = noz(b, x1 - Math.max(1.5 * od(p.nc), 0.08 * L), R, [0, 1], p.nc);
    const tin = noz(b, C / 2, -R, [0, -1], p.nt), tout = noz(b, C / 2, R, [0, 1], p.nt);
    if (variant === "on saddles") {
      const S = Math.max(p.S, (F150[p.nc] || [0, 15])[1] + Math.max(100, 2.5 * od(p.nc)) + 40), w = Math.max(150, 0.18 * D), sp = 0.06 * D;
      for (const x of [x0 + 0.2 * L, x0 + 0.72 * L]) {
        b.shapes.push([[x - w / 2, R - 1], [x + w / 2, R - 1], [x + w / 2 + sp, R + S - 15], [x - w / 2 - sp, R + S - 15]]);
        b.shapes.push(rect(x - w / 2 - sp - 20, R + S - 15, w + 2 * sp + 40, 15));
      }
    }
    return finish(b, { "Shell OD": D, "Shell length": L, "Channel length": C, "Overall length": r2(x1 + 2 * h) },
      [steam, cond, tin, tout], [{ k: "L", p: [x1 + h, 0], u: [1, 0], f: 1 }, { k: "D", p: [x0 + L / 2, -R], u: [0, -1], f: 2 }]);
  }

  // ------------------------------------------------------------ open tank with a helical steam coil (coil dashed)
  // Origin: tank bottom, on the centreline. Coil inlet comes up and over the rim; outlet goes out through the side wall.
  function tankcoil(p, variant) {
    const b = Builder(), D = p.D, R = D / 2, H = p.H, o = od(p.nps);
    const lip = Math.max(15, 0.02 * D), rimH = Math.max(20, 0.025 * D);
    b.shapes.push(rect(-R, -H, D, H));
    b.shapes.push(rect(-R - lip, -H, D + 2 * lip, rimH));
    if (variant === "on legs") {
      const lg = p.Lg, wl = Math.max(50, 0.05 * D);
      for (const x of [-R * 0.8, R * 0.8]) { b.shapes.push(rect(x - wl / 2, -2, wl, lg - 10)); b.shapes.push(rect(x - wl, lg - 12, 2 * wl, 12)); }
    }
    const rc = clamp(p.Dc, 4 * o, D - 2 * o - 100) / 2, gap = clamp(p.gap, o, H / 2);
    const Hc = clamp(p.Hc, 2 * o, H - gap - 2 * o - 100), N = clamp(Math.round(p.N), 1, 60);
    const yb = -(gap + o / 2), yt = yb - Hc, T = 2 * PI * (N + 0.5), n = Math.ceil(36 * (N + 0.5));
    const helix = dy => { const P = []; for (let i = 0; i <= n; i++) { const t = PI + T * i / n; P.push([rc * Math.cos(t), yb - Hc * i / n + dy]); } return P; };
    b.hidden.push(helix(-o / 2), helix(o / 2));
    const rise = Math.max(150, 2 * o), yr = -H - rise, out = R + Math.max(200, 0.15 * D);
    b.hidden.push([[rc - o / 2, yt], [rc - o / 2, -H]], [[rc + o / 2, yt], [rc + o / 2, -H]]);       // riser inside the tank
    b.shapes.push([[rc - o / 2, -H + 1], [rc - o / 2, yr - o / 2], [out, yr - o / 2], [out, yr + o / 2], [rc + o / 2, yr + o / 2], [rc + o / 2, -H + 1]]);
    const inlet = noz(b, out, yr, [1, 0], p.nps, 1);
    b.hidden.push([[-rc, yb - o / 2], [-R, yb - o / 2]], [[-rc, yb + o / 2], [-R, yb + o / 2]]);       // run to the side wall
    const outlet = noz(b, -R, yb, [-1, 0], p.nps);
    return finish(b, { "Tank OD": D, "Tank height": H, "Coil diameter": r2(2 * rc), "Coil height": r2(Hc), "Coil turns": N },
      [inlet, outlet], [{ k: "H", p: [0, -H], u: [0, -1], f: 1 }, { k: "D", p: [R, -H / 2], u: [1, 0], f: 2 }]);
  }

  // ------------------------------------------------------------ finned air heater coil, face view
  // Origin: bottom left of the casing. Supply header on the left: steam in near the top, condensate out at the bottom.
  function aircoil(p) {
    const b = Builder(), W = p.W, Hf = p.Hf, cf = Math.max(40, 0.05 * Hf), H = Hf + 2 * cf;
    const hw = Math.max(100, 2.2 * od(p.ni)), rb = Math.max(60, 0.6 * hw), xf = hw + cf;
    b.shapes.push(rect(0, -H - 20, hw, H + 40));                                   // supply / return header
    b.shapes.push(rect(hw, -H, W + 2 * cf, H));                                    // casing
    b.shapes.push(rect(xf, -H + cf, W, Hf));                                       // finned face
    b.shapes.push(rect(hw + W + 2 * cf, -H - 10, rb, H + 20));                     // return bends
    const s = Math.max(12, W / 70);
    for (let x = xf + s; x < xf + W - s / 2; x += s) b.thin.push([[x, -H + cf], [x, -cf]]);
    const rows = Math.max(2, Math.round(Hf / 90));
    for (let i = 1; i <= rows; i++) { const y = -cf - Hf * (i - 0.5) / rows; b.hidden.push([[xf, y], [xf + W, y]]); }
    const inlet = noz(b, 0, -H + Math.max(od(p.ni), 60), [-1, 0], p.ni);
    const outlet = noz(b, 0, -Math.max(od(p.no), 50), [-1, 0], p.no);
    return finish(b, { "Finned length": W, "Finned height": Hf, "Overall height": r2(H + 40), "Overall length": r2(hw + W + 2 * cf + rb) },
      [inlet, outlet], [{ k: "W", p: [hw + W + 2 * cf + rb, -H / 2], u: [1, 0], f: 1 }, { k: "Hf", p: [xf + W / 2, -H], u: [0, -1], f: 1 }]);
  }

  // ------------------------------------------------------------ steam jacketed kettle, hemispherical bottom
  // Origin: top of the rim, on the centreline. Jacket steam in high on the side, condensate out low, product drain at the bottom.
  function kettle(p, variant) {
    const b = Builder(), D = p.D, R = D / 2, Hs = p.Hs, g = Math.max(40, 0.05 * D), Rj = R + g;
    const J = clamp(p.J, 100, Hs), jt = Hs - J, lip = Math.max(25, 0.04 * D), rimH = Math.max(25, 0.03 * D);
    if (variant === "on legs") {
      const wl = Math.max(50, 0.06 * D), xl = 0.75 * Rj, yl = Hs + Math.sqrt(Rj * Rj - xl * xl) - 10, yf = Hs + Rj + p.Lg;
      for (const x of [-xl, xl]) { b.shapes.push(rect(x - wl / 2, yl, wl, yf - yl - 12)); b.shapes.push(rect(x - wl, yf - 12, 2 * wl, 12)); }
    }
    b.fills.push([[-R, 0], [R, 0], ...arc(0, Hs, R, R, 0, PI)]);                    // vessel: outline drawn below
    b.lines.push([[-R, 0], [-R, jt]], [[R, 0], [R, jt]]);
    b.hidden.push([[R, jt], ...arc(0, Hs, R, R, 0, PI), [-R, jt]]);                  // vessel wall inside the jacket
    b.shapes.push([[-Rj, jt], [Rj, jt], ...arc(0, Hs, Rj, Rj, 0, PI)]);             // jacket
    b.shapes.push(rect(-R - lip, -rimH, D + 2 * lip, rimH));                          // rim
    const steam = noz(b, Rj, jt + Math.max(60, 1.5 * od(p.ns)), [1, 0], p.ns);
    const xc = -0.35 * Rj, cond = noz(b, xc, Hs + Math.sqrt(Rj * Rj - xc * xc) - 3, [0, 1], p.nc);
    const drain = noz(b, 0, Hs + Rj - 3, [0, 1], p.nd);
    return finish(b, { "Vessel ID": D, "Straight side": Hs, "Jacket height": r2(J), "Jacket diameter": r2(2 * Rj) },
      [steam, cond, drain], [{ k: "D", p: [Rj, Hs], u: [1, 0], f: 2 }, { k: "Hs", p: [0, Hs + Rj], u: [0, 1], f: 1 }]);
  }

  // ------------------------------------------------------------ reservoir (receiver) for a pressure powered pump package
  // Pipe-body vessel with 2:1 elliptical heads. Origin: left (or bottom) tangent line, on the centreline. Nozzles on top and
  // bottom are spaced evenly along the shell (horizontal) or across the head (vertical); the vent can leave the top or the
  // bottom. A bottom vent has a dashed internal riser up into the vapour space. Nozzles are flanged stubs or threaded
  // half couplings (ASME B16.11 Class 3000 band OD, from app.js THD).
  function thdNoz(b, x, y, u, nps, len) {
    const o = od(nps), T = (typeof THD !== "undefined" && THD[nps]) || [1.0 * o, 0, 1.45 * o], H = T[2], n = [-u[1], u[0]];
    len = len || Math.max(30, 0.85 * T[0]);
    const P = (a, w) => [x + u[0] * a + n[0] * w, y + u[1] * a + n[1] * w];
    b.shapes.push([P(-2, -H / 2), P(len, -H / 2), P(len, H / 2), P(-2, H / 2)]);
    b.thin.push([P(len * 0.62, -H / 2), P(len * 0.62, H / 2)]);                       // thread run-out line
    const e = P(len, 0);
    return [r2(e[0]), r2(e[1]), Math.round(Math.atan2(u[1], u[0]) * 180 / PI)];
  }
  function reservoir(p, variant) {
    const b = Builder(), D = p.D, R = D / 2, L = p.L, h = D / 4, vert = variant === "vertical";
    const thd = p.ends === "Threaded", N = (k, max) => clamp(Math.round(p[k] || 0), 0, max);
    // extra: added stub length, so nozzles on a head all end in one plane
    const T_ = nps => (typeof THD !== "undefined" && THD[nps]) || [od(nps), 0, 1.45 * od(nps)];
    const base = nps => thd ? Math.max(30, 0.85 * T_(nps)[0]) : Math.max(60, 1.5 * od(nps));
    const face = nps => thd ? 0 : (F150[nps] || [0, 15])[1];
    const nozzle = (x, y, u, nps, extra = 0) => thd ? thdNoz(b, x, y, u, nps, base(nps) + extra) : noz(b, x, y, u, nps, base(nps) + extra);
    // drawn horizontal, x along the shell; a vertical vessel is the same drawing turned (top = -x side up)
    const V = vert ? q => [q[1], -q[0]] : q => q, Vu = vert ? u => [u[1], -u[0]] : u => u;
    const pts = P => P.map(V);
    b.shapes.push(pts([[0, -R], [L, -R], ...arc(L, 0, h, R, -PI / 2, PI / 2), [0, R], ...arc(0, 0, h, R, PI / 2, 1.5 * PI)]));
    b.lines.push(pts([[0, -R], [0, R]]), pts([[L, -R], [L, R]]));                      // tangent lines
    const top = [], bot = [];
    for (let i = 1; i <= N("nTop", 6); i++) top.push(p["t" + i]);
    for (let i = 1; i <= N("nBot", 6); i++) bot.push(p["b" + i]);
    const vBot = p.vpos !== "Top";
    (vBot ? bot : top).push("vent");
    // positions: along the shell (horizontal) or across the head (vertical: top = right-hand head, which is up)
    const place = n => vert ? Array.from({ length: n }, (_, i) => -R * 0.7 + (n > 1 ? 1.4 * R * i / (n - 1) : 0.7 * R))
      : Array.from({ length: n }, (_, i) => L * (i + 0.5) / n);
    const ports = [], dims = { "Diameter": r2(D), "Shell length": r2(L), "Overall length": r2(L + 2 * h) };
    const side = (list, sgn) => {
      const xs = place(list.length), sz = list.map(n => n === "vent" ? p.vent : n);
      const reach = Math.max(...sz.map(n => base(n) + face(n)));      // vertical: every face on this head in one plane
      list.forEach((nps, i) => {
        const vent = nps === "vent", size = vent ? p.vent : nps;
        let q, u, extra = 0;
        if (vert) {                                                // on a head: y across, out along the axis
          const yy = xs[i], hx = h * Math.sqrt(Math.max(0, 1 - (yy / R) ** 2));
          q = sgn < 0 ? [L + hx - 2, yy] : [-hx + 2, yy]; u = sgn < 0 ? [1, 0] : [-1, 0]; extra = h - hx + reach - base(size) - face(size);
        } else { q = [xs[i], sgn * R]; u = [0, sgn]; }
        const pt = nozzle(...V(q), Vu(u), size, extra);
        ports.push(pt);
        if (vent && vBot) {                                        // internal riser into the vapour space, dashed
          const o = od(size), top_ = vert ? L + h * 0.5 : -R * 0.7;
          const a = vert ? [[q[0], q[1] - o / 2], [top_, q[1] - o / 2]] : [[q[0] - o / 2, R], [q[0] - o / 2, top_]];
          const c = vert ? [[q[0], q[1] + o / 2], [top_, q[1] + o / 2]] : [[q[0] + o / 2, R], [q[0] + o / 2, top_]];
          b.hidden.push(pts(a), pts(c));
        }
      });
    };
    side(top, -1); side(bot, 1);
    const grips = vert ? [{ k: "L", p: V([L + h, 0]), u: [0, -1], f: 1 }, { k: "D", p: V([L / 2, R]), u: [1, 0], f: 2 }]
      : [{ k: "L", p: [L + h, 0], u: [1, 0], f: 1 }, { k: "D", p: [L / 2, -R], u: [0, -1], f: 2 }];
    return finish(b, dims, ports, grips);
  }

  const IN = 25.4;
  const nps = ['1/2"', '3/4"', '1"', '1-1/4"', '1-1/2"', '2"', '2-1/2"', '3"', '4"', '6"', '8"', '10"', '12"'];
  const NOZ = ['1/2"', '3/4"', '1"', '1-1/4"', '1-1/2"', '2"', '2-1/2"', '3"', '4"', '6"'];
  const nozFields = (pre, cnt, label) => Array.from({ length: 6 }, (_, i) => ({ k: pre + (i + 1), label: `${label} ${i + 1}`, t: "nps", opts: NOZ,
    show: p => Math.round(p[cnt] || 0) > i }));
  window.EQUIP = {
    UTUBE: { name: "U-tube exchanger", type: "Shell and tube, U-tube bundle, horizontal", build: utube,
      variants: ["on saddles", "no saddles"], variantLabel: "Supports",
      defaults: { D: 18 * IN, L: 96 * IN, C: 18 * IN, S: 16 * IN, ns: '4"', nc: '1-1/2"', nt: '3"' },
      fields: [{ k: "D", label: "Shell OD", t: "len", min: 150, max: 3000 }, { k: "L", label: "Shell length", t: "len", min: 300, max: 15000 },
        { k: "C", label: "Channel length", t: "len", min: 100, max: 3000 }, { k: "S", label: "Saddle height", t: "len", min: 100, max: 3000 },
        { k: "ns", label: "Steam inlet", t: "nps", opts: nps }, { k: "nc", label: "Condensate outlet", t: "nps", opts: nps }, { k: "nt", label: "Tube side nozzles", t: "nps", opts: nps }],
      note: "Drawn from the sizes you enter. Steam in the shell (inlet top, near the tubesheet; condensate out bottom, far end), process through the tubes (both nozzles on the channel). The U-tube bundle and baffles are dashed. Connections: steam in, condensate out, tube side in, tube side out. Drag the end or top handle to stretch it." },
    TANKCOIL: { name: "Open tank, helical coil", type: "Open top tank with a steam coil (coil shown dashed)", build: tankcoil,
      variants: ["on floor", "on legs"], variantLabel: "Supports",
      defaults: { D: 48 * IN, H: 60 * IN, Dc: 36 * IN, Hc: 24 * IN, N: 6, gap: 6 * IN, Lg: 12 * IN, nps: '1-1/2"' },
      fields: [{ k: "D", label: "Tank OD", t: "len", min: 300, max: 10000 }, { k: "H", label: "Tank height", t: "len", min: 300, max: 10000 },
        { k: "Dc", label: "Coil diameter", t: "len", min: 100, max: 10000 }, { k: "Hc", label: "Coil height", t: "len", min: 50, max: 10000 },
        { k: "N", label: "Coil turns", t: "num", min: 1, max: 60 }, { k: "gap", label: "Coil above floor", t: "len", min: 0, max: 3000 },
        { k: "Lg", label: "Leg height", t: "len", min: 50, max: 3000 }, { k: "nps", label: "Coil pipe size", t: "nps", opts: nps }],
      note: "Drawn from the sizes you enter. The coil is dashed (inside the tank). Steam inlet comes up and over the rim; the condensate outlet leaves through the side wall at the bottom of the coil. Connections: coil inlet, coil outlet. The coil is held inside the tank if the sizes would push it through the wall. Drag the top or side handle to stretch it." },
    AIRCOIL: { name: "Air heater coil", type: "Finned steam coil, face view", build: aircoil, variants: ["-"],
      defaults: { W: 48 * IN, Hf: 24 * IN, ni: '2"', no: '1"' },
      fields: [{ k: "W", label: "Finned length", t: "len", min: 200, max: 10000 }, { k: "Hf", label: "Finned height", t: "len", min: 100, max: 5000 },
        { k: "ni", label: "Steam inlet", t: "nps", opts: nps }, { k: "no", label: "Condensate outlet", t: "nps", opts: nps }],
      note: "Drawn from the sizes you enter. Supply header on the left with steam in near the top and condensate out at the bottom; return bends on the right; tube rows dashed. Mirror it for a right-hand header. Connections: steam in, condensate out. Drag the end or top handle to stretch it." },
    KETTLE: { name: "Jacketed kettle", type: "Steam jacketed kettle, hemispherical bottom", build: kettle,
      variants: ["on legs", "no legs"], variantLabel: "Supports",
      defaults: { D: 36 * IN, Hs: 24 * IN, J: 14 * IN, Lg: 18 * IN, ns: '1"', nc: '3/4"', nd: '2"' },
      fields: [{ k: "D", label: "Vessel ID", t: "len", min: 200, max: 5000 }, { k: "Hs", label: "Straight side", t: "len", min: 50, max: 5000 },
        { k: "J", label: "Jacket up the side", t: "len", min: 100, max: 5000 }, { k: "Lg", label: "Leg clearance", t: "len", min: 50, max: 3000 },
        { k: "ns", label: "Jacket steam inlet", t: "nps", opts: nps }, { k: "nc", label: "Jacket condensate", t: "nps", opts: nps }, { k: "nd", label: "Product drain", t: "nps", opts: nps }],
      note: "Drawn from the sizes you enter. Jacket steam inlet high on the side, condensate outlet at the low point of the jacket, product drain at the bottom centre. The vessel wall inside the jacket is dashed. Jacket height is measured up the straight side from the bottom tangent line. Connections: steam in, condensate out, product drain. Drag the side or bottom handle to stretch it." },
    RESERVOIR: { name: "Reservoir", type: "Reservoir (receiver) for a pressure powered pump package", build: reservoir,
      variants: ["horizontal", "vertical"], variantLabel: "Orientation",
      defaults: { D: 12.75 * IN, L: 36 * IN, nTop: 2, t1: '2"', t2: '1-1/2"', t3: '1"', t4: '1"', t5: '1"', t6: '1"',
        nBot: 1, b1: '2"', b2: '1"', b3: '1"', b4: '1"', b5: '1"', b6: '1"', vent: '1-1/2"', vpos: "Bottom", ends: "Threaded" },
      fields: [{ k: "D", label: "Diameter", t: "len", min: 100, max: 3000 }, { k: "L", label: "Shell length", t: "len", min: 150, max: 10000 },
        { k: "ends", label: "Nozzle ends", t: "nps", opts: ["Threaded", "Flanged"] },
        { k: "nTop", label: "Top outlets", t: "num", min: 0, max: 6 }, ...nozFields("t", "nTop", "Top"),
        { k: "nBot", label: "Bottom outlets", t: "num", min: 0, max: 6 }, ...nozFields("b", "nBot", "Bottom"),
        { k: "vent", label: "Vent size", t: "nps", opts: NOZ }, { k: "vpos", label: "Vent leaves", t: "nps", opts: ["Bottom", "Top"] }],
      note: "Drawn from the sizes you enter. Pipe-body vessel with 2:1 elliptical heads. Top and bottom outlets are spaced evenly; the vent is one more connection on the side you pick. A vent leaving the bottom has a dashed riser inside up into the vapour space. Threaded nozzles are Class 3000 half couplings; flanged are Class 150 stubs. Connections: top outlets, then bottom outlets, vent on its side. Vertical: top outlets on the upper head. Drag the end or side handle to stretch it." },
  };
})();
