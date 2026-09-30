/* The twelve simulations. Each one runs the proven maths from bo.js and names its theorem.
   Nothing here is an illustration of a result; each is the result, running. */

import { law, boundary, disk, coupling, cones, fitCanvas, css, onScreen, slider } from './bo.js';

const TAU = Math.PI * 2;
const C = disk.C;

/* ---------------------------------------------------------------- shared drawing */

const ink = () => css('--ink');
const ink2 = () => css('--ink-2');
const ink3 = () => css('--ink-3');
const rule = () => css('--rule');
const accent = () => css('--accent');
const cool = () => css('--cool');
const good = () => css('--good');
const bad = () => css('--bad');

function frame(cv) {
  const { g, w, h } = fitCanvas(cv);
  return { g, w, h, cx: w / 2, cy: h / 2, R: Math.min(w, h) / 2 - 18 };
}

function readout(host, html) { host.querySelector('.readout').innerHTML = html; }

function disc(g, cx, cy, R) {
  g.strokeStyle = rule(); g.lineWidth = 1;
  g.beginPath(); g.arc(cx, cy, R, 0, TAU); g.stroke();
}

/** A hyperbolic circle of hyperbolic radius rho about disk point p, as a Euclidean circle. */
function hypCircle(p, rho) {
  const d = Math.hypot(p.x, p.y);
  const t = Math.tanh(rho / 2);
  if (d < 1e-12) return { x: 0, y: 0, r: t };
  // map the two ends of the diameter through p, then take their Euclidean midpoint
  const u = { x: p.x / d, y: p.y / d };
  const a = disk.add(p, { x: u.x * t, y: u.y * t });
  const b = disk.add(p, { x: -u.x * t, y: -u.y * t });
  return { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2, r: Math.hypot(a.x - b.x, a.y - b.y) / 2 };
}

function geodesicPath(g, a, b, cx, cy, R, n = 40) {
  const pts = disk.geodesic(a, b, n);
  g.beginPath();
  pts.forEach((p, i) => (i ? g.lineTo(cx + p.x * R, cy + p.y * R) : g.moveTo(cx + p.x * R, cy + p.y * R)));
  g.stroke();
}

/** Pointer drag on a canvas, in disk coordinates. */
function drag(cv, getGeom, onMove) {
  let down = false;
  const to = (e) => {
    const r = cv.getBoundingClientRect();
    const { cx, cy, R } = getGeom();
    return { x: (e.clientX - r.left - cx) / R, y: (e.clientY - r.top - cy) / R };
  };
  const clamp = (p) => {
    const d = Math.hypot(p.x, p.y);
    return d > 0.97 ? { x: (p.x / d) * 0.97, y: (p.y / d) * 0.97 } : p;
  };
  cv.addEventListener('pointerdown', (e) => { down = true; cv.setPointerCapture(e.pointerId); onMove(clamp(to(e))); });
  cv.addEventListener('pointermove', (e) => { if (down) { e.preventDefault(); onMove(clamp(to(e))); } });
  cv.addEventListener('pointerup', () => { down = false; });
  cv.addEventListener('pointercancel', () => { down = false; });
}

/* ================================================================ 1 · You are the centre */
export function simCentre(host) {
  const cv = host.querySelector('canvas');
  let obs = C(0, 0);

  // a lattice at hyperbolic radii, with as many points per ring as the ring has room
  const stars = [];
  for (let k = 1; k <= 9; k++) {
    const rho = k * 0.62;
    const n = Math.max(6, Math.round(disk.circumference(rho) * 1.05));
    for (let i = 0; i < n; i++) stars.push(disk.fromPolar(rho, (TAU * i) / n + k * 0.31));
  }

  const geom = () => { const f = frame(cv); return f; };
  drag(cv, geom, (p) => { obs = p; draw(); });

  function draw() {
    const { g, cx, cy, R } = frame(cv);
    disc(g, cx, cy, R);
    // rings of constant distance from the observer
    g.strokeStyle = rule();
    for (let rho = 1; rho <= 4; rho++) {
      const c = hypCircle(disk.neg(obs), rho);  // seen from the observer: centre at -obs
      g.beginPath(); g.arc(cx + c.x * R, cy + c.y * R, c.r * R, 0, TAU); g.stroke();
    }
    // the world as the observer sees it
    let near = 0;
    for (const s of stars) {
      const v = disk.recentre(obs, s);
      const d = Math.hypot(v.x, v.y);
      if (d > 0.995) continue;
      const scale = 1 - d * d;                 // the disk's own conformal factor
      const rr = Math.max(0.6, 3.4 * scale);
      g.fillStyle = ink3();
      g.globalAlpha = Math.min(1, 0.25 + scale * 1.6);
      g.beginPath(); g.arc(cx + v.x * R, cy + v.y * R, rr, 0, TAU); g.fill();
      g.globalAlpha = 1;
      if (disk.distance(obs, s) < 1.0) near++;
    }
    g.fillStyle = accent();
    g.beginPath(); g.arc(cx, cy, 5, 0, TAU); g.fill();
    readout(host, `you <b>0.00</b> from yourself<br>edge <b>&#8734;</b> away<br>${near} points within <b>1.0</b>`);
  }
  draw();
  window.addEventListener('resize', draw);
}

/* ================================================================ 2 · Two histories, one reading */
export function simHistories(host) {
  const cv = host.querySelector('canvas');
  let show = 0;   // 0 = one reading, 1 = the extra measurement
  let t = 0;

  host.querySelectorAll('.seg button').forEach((b, i) =>
    b.addEventListener('click', () => {
      show = i;
      host.querySelectorAll('.seg button').forEach((x, j) => x.setAttribute('aria-pressed', j === i));
    }));

  // two histories that meet at the same reading and then part
  const A = (x) => 0.5 + 0.42 * Math.sin(x * 2.1) * Math.exp(-x * 0.9);
  const B = (x) => 0.5 - 0.42 * Math.sin(x * 2.1) * Math.exp(-x * 0.9);
  const futureA = (x) => 0.5 + 0.40 * (1 - Math.exp(-(x - 3) * 1.4));
  const futureB = (x) => 0.5 - 0.44 * (1 - Math.exp(-(x - 3) * 1.1));
  // the hidden variable: reserve left. Identical reading, different reserve.
  const resA = (x) => 0.80 - 0.02 * x;
  const resB = (x) => 0.80 - 0.22 * x;

  const curve = (g, f, x0, x1, X, Y, col, dash) => {
    g.strokeStyle = col; g.lineWidth = 2; g.setLineDash(dash || []);
    g.beginPath();
    for (let x = x0; x <= x1; x += 0.02) {
      const px = X(x), py = Y(f(x));
      x === x0 ? g.moveTo(px, py) : g.lineTo(px, py);
    }
    g.stroke(); g.setLineDash([]);
  };

  function draw(now) {
    t = ((now || 0) / 2600) % 1;
    const { g, w, h } = fitCanvas(cv);
    const L = 44, Rp = 14, T = 16, Bm = 26;
    const X = (x) => L + (x / 6) * (w - L - Rp);
    const Y = (v) => T + (1 - v) * (h - T - Bm);
    g.strokeStyle = rule(); g.lineWidth = 1;
    g.beginPath(); g.moveTo(L, Y(0)); g.lineTo(w - Rp, Y(0)); g.stroke();
    g.font = '11px ui-sans-serif, system-ui'; g.fillStyle = ink3();
    g.fillText('reading', 2, Y(0.5) + 4);
    g.fillText('past', L, h - 8); g.fillText('future', X(4.4), h - 8);

    curve(g, A, 0, 3, X, Y, cool());
    curve(g, B, 0, 3, X, Y, bad());
    const nowX = 3 + t * 3;
    curve(g, futureA, 3, nowX, X, Y, cool());
    curve(g, futureB, 3, nowX, X, Y, bad());

    if (show === 1) {
      curve(g, resA, 0, 3, X, Y, cool(), [4, 3]);
      curve(g, resB, 0, 3, X, Y, bad(), [4, 3]);
      g.fillStyle = ink3(); g.fillText('reserve (the second measurement)', L + 6, Y(0.88));
    }

    // the moment they read the same
    g.strokeStyle = accent(); g.setLineDash([3, 3]);
    g.beginPath(); g.moveTo(X(3), T); g.lineTo(X(3), h - Bm); g.stroke(); g.setLineDash([]);
    g.fillStyle = accent(); g.beginPath(); g.arc(X(3), Y(0.5), 4.5, 0, TAU); g.fill();

    const gapNow = Math.abs(futureA(nowX) - futureB(nowX));
    readout(host,
      show === 0
        ? `both read <b>0.50</b><br>futures differ by <b>${gapNow.toFixed(2)}</b><br>no way to tell them apart`
        : `both read <b>0.50</b><br>reserve <b>${resA(3).toFixed(2)}</b> vs <b>${resB(3).toFixed(2)}</b><br>now they are different states`);
  }
  onScreen(cv, draw);
  draw(0);
}

/* ================================================================ 3 · The horizon */
export function simHorizon(host) {
  const cv = host.querySelector('canvas');
  let step = 0.5, n = 0, acc = 0;

  slider(host.querySelector('.ctls'), { min: .05, max: .95, step: .01, value: .5, label: 'each step' },
    (v) => { step = v; n = 0; });

  function draw(now) {
    acc = acc || now;
    if (now - acc > 620) { acc = now; n = n >= 14 ? 0 : n + 1; }
    const { g, w, h } = fitCanvas(cv);
    const L = 20, Rp = 20, yv = h * 0.33, yr = h * 0.74;
    const X = (u) => L + u * (w - L - Rp);

    const vals = [0]; let x = 0;
    for (let i = 0; i < n; i++) { x = law.einstein(x, step); vals.push(x); }

    const drawAxis = (y, label) => {
      g.strokeStyle = rule(); g.lineWidth = 1;
      g.beginPath(); g.moveTo(L, y); g.lineTo(w - Rp, y); g.stroke();
      g.font = '11px ui-sans-serif, system-ui'; g.fillStyle = ink3(); g.fillText(label, L, y - 26);
    };
    drawAxis(yv, 'what you measure');
    // the ceiling
    g.strokeStyle = accent(); g.lineWidth = 2;
    g.beginPath(); g.moveTo(X(1), yv - 18); g.lineTo(X(1), yv + 18); g.stroke();
    g.fillStyle = accent(); g.font = '11px ui-sans-serif, system-ui';
    g.fillText('ceiling', X(1) - 42, yv - 24);

    drawAxis(yr, 'rapidity: the same steps, evenly');
    const maxPsi = Math.max(1e-6, law.rapidity(Math.min(vals[vals.length - 1], 1 - 1e-12)));
    const psiScale = 14 * law.rapidity(step) > 0 ? 1 / Math.max(maxPsi, law.rapidity(step) * 14) : 1;

    vals.forEach((v, i) => {
      const a = i / Math.max(1, vals.length - 1);
      g.globalAlpha = 0.25 + 0.75 * a;
      g.fillStyle = i === vals.length - 1 ? accent() : ink3();
      g.beginPath(); g.arc(X(v), yv, i === vals.length - 1 ? 5 : 3, 0, TAU); g.fill();
      const p = law.rapidity(Math.min(v, 1 - 1e-12)) * psiScale;
      g.beginPath(); g.arc(X(p), yr, i === vals.length - 1 ? 5 : 3, 0, TAU); g.fill();
      g.globalAlpha = 1;
    });

    const last = vals[vals.length - 1];
    readout(host, `steps <b>${n}</b><br>value <b>${last.toFixed(6)}</b><br>left to go <b>${(1 - last).toExponential(1)}</b>`);
  }
  onScreen(cv, draw);
  draw(0);
}

/* ================================================================ 4 · Three laws */
export function simTrichotomy(host) {
  const cv = host.querySelector('canvas');
  let k = 1;
  slider(host.querySelector('.ctls'),
    { min: -1.4, max: 1.4, step: .01, value: 1, label: 'ceiling κ', fmt: (v) => v.toFixed(2) },
    (v) => { k = v; draw(); });

  function draw() {
    const { g, w, h } = fitCanvas(cv);
    const L = 30, Rp = 30, T = 20, B = 34;
    const X = (u) => L + ((u + 2) / 4) * (w - L - Rp);
    const Y = (v) => T + (1 - (v + 1.6) / 3.2) * (h - T - B);

    g.strokeStyle = rule(); g.lineWidth = 1;
    g.beginPath(); g.moveTo(L, Y(0)); g.lineTo(w - Rp, Y(0)); g.stroke();
    g.font = '11px ui-sans-serif, system-ui'; g.fillStyle = ink3();
    g.fillText('X(u) = 1 − κ u²   —  where this crosses zero, the flow stops', L, h - 10);

    g.strokeStyle = cool(); g.lineWidth = 2; g.beginPath();
    for (let u = -2; u <= 2; u += 0.01) {
      const v = 1 - k * u * u;
      u === -2 ? g.moveTo(X(u), Y(v)) : g.lineTo(X(u), Y(v));
    }
    g.stroke();

    let type, note;
    if (k > 1e-6) {
      const f = 1 / Math.sqrt(k);
      type = 'two horizons'; note = 'bounded';
      g.fillStyle = accent();
      [-f, f].forEach((u) => { g.beginPath(); g.arc(X(u), Y(0), 5, 0, TAU); g.fill(); });
      g.globalAlpha = .1; g.fillRect(X(-f), T, X(f) - X(-f), h - T - B); g.globalAlpha = 1;
    } else if (k < -1e-6) {
      type = 'no fixed point'; note = 'wraps through infinity';
    } else {
      type = 'one double point at ∞'; note = 'flat addition';
    }

    // repeated composition from rest, as a ladder
    let x = 0; const pts = [0];
    for (let i = 0; i < 26; i++) { x = law.trichotomy(x, 0.35, k); if (!Number.isFinite(x) || Math.abs(x) > 12) break; pts.push(x); }
    g.fillStyle = ink3();
    pts.forEach((p, i) => {
      if (Math.abs(p) > 2) return;
      g.globalAlpha = .2 + .8 * (i / pts.length);
      g.beginPath(); g.arc(X(p), Y(0) + 16, 2.6, 0, TAU); g.fill(); g.globalAlpha = 1;
    });

    readout(host, `κ = <b>${k.toFixed(2)}</b><br>${type}<br><b>${note}</b>`);
  }
  draw();
  window.addEventListener('resize', draw);
}

/* ================================================================ 5 · Arrival or horizon */
export function simExponent(host) {
  const cv = host.querySelector('canvas');
  let gam = 1, t0 = 0;
  slider(host.querySelector('.ctls'), { min: 0, max: 2.4, step: .01, value: 1, label: 'boundary exponent γ' },
    (v) => { gam = v; t0 = 0; });

  function draw(now) {
    if (!t0) t0 = now;
    const T = Math.min(((now - t0) / 1000) % 9, 9);
    const { g, w, h } = fitCanvas(cv);
    const L = 40, Rp = 26, Tp = 18, B = 30;
    const X = (u) => L + (u / 9) * (w - L - Rp);
    const Y = (v) => Tp + (1 - v) * (h - Tp - B);

    g.strokeStyle = accent(); g.lineWidth = 2;
    g.beginPath(); g.moveTo(L, Y(0)); g.lineTo(w - Rp, Y(0)); g.stroke();
    g.font = '11px ui-sans-serif, system-ui'; g.fillStyle = accent();
    g.fillText('the ceiling', L + 4, Y(0) - 6);
    g.fillStyle = ink3(); g.fillText('time', w - Rp - 24, h - 8);
    g.save(); g.translate(12, Y(0.5) + 26); g.rotate(-Math.PI / 2);
    g.fillText('room left', 0, 0); g.restore();

    for (const [gg, col, lw] of [[0.5, ink3(), 1], [1, ink3(), 1], [2, ink3(), 1], [gam, cool(), 2.4]]) {
      g.strokeStyle = col; g.lineWidth = lw; g.globalAlpha = lw > 1 ? 1 : .35;
      g.beginPath();
      for (let u = 0; u <= 9; u += 0.03) {
        const d = boundary.roomLeft(gg, 1, u);
        u === 0 ? g.moveTo(X(u), Y(d)) : g.lineTo(X(u), Y(d));
      }
      g.stroke(); g.globalAlpha = 1;
    }

    const d = boundary.roomLeft(gam, 1, T);
    g.fillStyle = d <= 0 ? bad() : accent();
    g.beginPath(); g.arc(X(T), Y(Math.max(d, 0)), 5.5, 0, TAU); g.fill();

    const ta = boundary.arrivalTime(gam, 1);
    readout(host, `γ = <b>${gam.toFixed(2)}</b><br>room left <b>${d <= 0 ? '0' : d.toExponential(1)}</b><br>` +
      (Number.isFinite(ta) ? `<b style="color:${bad()}">arrives at t = ${ta.toFixed(2)}</b>` : `<b>never arrives</b>`));
  }
  onScreen(cv, draw);
  draw(0);
}

/* ================================================================ 6 · The room inside */
export function simRoom(host) {
  const cv = host.querySelector('canvas');
  let depth = 5;
  slider(host.querySelector('.ctls'), { min: 1, max: 7, step: 1, value: 5, label: 'tree depth', fmt: (v) => v.toFixed(0) },
    (v) => { depth = v; draw(); });

  function draw() {
    const { g, cx, cy, R } = frame(cv);
    disc(g, cx, cy, R);
    g.strokeStyle = rule(); g.lineWidth = 1;
    for (let rho = 1; rho <= 5; rho++) {
      const r = Math.tanh(rho / 2) * R;
      g.beginPath(); g.arc(cx, cy, r, 0, TAU); g.stroke();
    }
    // a binary tree with equal hyperbolic edge lengths
    const edge = 1.25;
    let nodes = 0;
    const walk = (p, dir, spread, k) => {
      nodes++;
      if (k >= depth) return;
      for (const s of [-1, 1]) {
        const th = dir + s * spread;
        const q = disk.add(p, disk.fromPolar(edge, th));
        g.strokeStyle = cool(); g.lineWidth = Math.max(0.6, 2.2 - k * 0.3); g.globalAlpha = 0.85;
        geodesicPath(g, p, q, cx, cy, R, 24);
        g.globalAlpha = 1;
        walk(q, th, spread * 0.62, k + 1);
      }
    };
    for (let i = 0; i < 3; i++) {
      const th = (TAU * i) / 3;
      const q = disk.add(C(0, 0), disk.fromPolar(edge, th));
      g.strokeStyle = cool(); g.lineWidth = 2.2;
      geodesicPath(g, C(0, 0), q, cx, cy, R, 24);
      walk(q, th, 0.85, 1);
    }
    g.fillStyle = accent(); g.beginPath(); g.arc(cx, cy, 4.5, 0, TAU); g.fill();

    const r = 5;
    readout(host, `at radius ${r}: <b>${disk.circumference(r).toFixed(0)}</b> around<br>` +
      `flat would be <b>${(TAU * r).toFixed(0)}</b><br>${nodes * 3} nodes, none crowded`);
  }
  draw();
  window.addEventListener('resize', draw);
}

/* ================================================================ 7 · Round and back, turned */
export function simHolonomy(host) {
  const cv = host.querySelector('canvas');
  let a = C(0.58, 0.10), b = C(-0.18, 0.62);
  const geom = () => frame(cv);
  let which = 0;
  cv.addEventListener('pointerdown', (e) => {
    const r = cv.getBoundingClientRect(); const { cx, cy, R } = geom();
    const p = C((e.clientX - r.left - cx) / R, (e.clientY - r.top - cy) / R);
    which = Math.hypot(p.x - a.x, p.y - a.y) < Math.hypot(p.x - b.x, p.y - b.y) ? 0 : 1;
  });
  drag(cv, geom, (p) => { if (which === 0) a = p; else b = p; draw(); });

  function draw() {
    const { g, cx, cy, R } = frame(cv);
    disc(g, cx, cy, R);
    const ab = disk.add(a, b);
    const P = (p) => [cx + p.x * R, cy + p.y * R];

    g.strokeStyle = cool(); g.lineWidth = 2;
    geodesicPath(g, C(0, 0), a, cx, cy, R);
    geodesicPath(g, a, ab, cx, cy, R);
    g.strokeStyle = accent();
    geodesicPath(g, C(0, 0), ab, cx, cy, R);

    // shade the triangle through its geodesic edges
    g.beginPath();
    const tri = [...disk.geodesic(C(0, 0), a, 26), ...disk.geodesic(a, ab, 26), ...disk.geodesic(ab, C(0, 0), 26)];
    tri.forEach((p, i) => (i ? g.lineTo(...P(p)) : g.moveTo(...P(p))));
    g.closePath(); g.fillStyle = accent(); g.globalAlpha = .1; g.fill(); g.globalAlpha = 1;

    const ang = disk.gyrationAngle(a, b);
    // the carried arrow, before and after
    const drawArrow = (at, th, col) => {
      const [x, y] = P(at); const len = 26;
      g.strokeStyle = col; g.lineWidth = 2;
      g.beginPath(); g.moveTo(x, y); g.lineTo(x + len * Math.cos(th), y + len * Math.sin(th)); g.stroke();
      g.beginPath(); g.arc(x + len * Math.cos(th), y + len * Math.sin(th), 3, 0, TAU); g.fillStyle = col; g.fill();
    };
    drawArrow(C(0, 0), 0, ink3());
    drawArrow(C(0, 0), -ang, accent());

    [[C(0, 0), 'you'], [a, 'a'], [ab, 'a ⊕ b']].forEach(([p, t]) => {
      const [x, y] = P(p);
      g.fillStyle = ink(); g.beginPath(); g.arc(x, y, 4, 0, TAU); g.fill();
      g.font = '11px ui-sans-serif, system-ui'; g.fillStyle = ink2(); g.fillText(t, x + 7, y - 7);
    });

    readout(host, `turn <b>${Math.abs(ang).toFixed(3)}</b> rad<br>triangle area <b>${Math.abs(ang).toFixed(3)}</b><br>they are the same number`);
  }
  draw();
  window.addEventListener('resize', draw);
}

/* ================================================================ 8 · Beyond the horizon */
export function simFarSide(host) {
  const cv = host.querySelector('canvas');
  let v = 0.6;
  slider(host.querySelector('.ctls'), { min: -3.4, max: 3.4, step: .01, value: .6, label: 'value' },
    (x) => { v = Math.abs(x) < 0.02 ? 0.02 : x; draw(); });

  function draw() {
    const { g, w, h } = fitCanvas(cv);
    const cx = w * 0.29, cy = h * 0.52, R = Math.min(w * 0.24, h * 0.36);
    // the projective line closed into a circle: x = tan(theta/2)
    g.strokeStyle = rule(); g.lineWidth = 1;
    g.beginPath(); g.arc(cx, cy, R, 0, TAU); g.stroke();
    const ang = (x) => 2 * Math.atan(x) - Math.PI / 2;
    // inside arc
    g.strokeStyle = cool(); g.lineWidth = 3.5;
    g.beginPath(); g.arc(cx, cy, R, ang(-1), ang(1)); g.stroke();
    g.strokeStyle = bad(); g.lineWidth = 3.5;
    g.beginPath(); g.arc(cx, cy, R, ang(1), ang(-1)); g.stroke();
    // the two horizons
    g.fillStyle = accent();
    [-1, 1].forEach((x) => {
      g.beginPath(); g.arc(cx + R * Math.cos(ang(x)), cy + R * Math.sin(ang(x)), 4.5, 0, TAU); g.fill();
    });
    const put = (x, col, r = 5) => {
      g.fillStyle = col;
      g.beginPath(); g.arc(cx + R * Math.cos(ang(x)), cy + R * Math.sin(ang(x)), r, 0, TAU); g.fill();
    };
    put(v, ink());
    const out = Math.abs(v) > 1;
    put(1 / v, out ? accent() : ink3(), 3.5);
    g.font = '11px ui-sans-serif, system-ui'; g.fillStyle = ink3();
    g.fillText('inside', cx - 16, cy + R + 16); g.fillText('far side', cx - 20, cy - R - 8);

    // Minkowski panel: the physical instance
    const mx = w * 0.70, my = h * 0.52, M = Math.min(w * 0.2, h * 0.36);
    g.strokeStyle = rule(); g.lineWidth = 1;
    g.beginPath(); g.moveTo(mx - M, my); g.lineTo(mx + M, my); g.moveTo(mx, my - M); g.lineTo(mx, my + M); g.stroke();
    g.strokeStyle = rule(); g.setLineDash([3, 3]);
    g.beginPath(); g.moveTo(mx - M, my + M); g.lineTo(mx + M, my - M); g.moveTo(mx - M, my - M); g.lineTo(mx + M, my + M); g.stroke();
    g.setLineDash([]);
    const vel = Math.max(-0.95, Math.min(0.95, out ? 1 / v : v));
    g.strokeStyle = cool(); g.lineWidth = 2.4;
    g.beginPath(); g.moveTo(mx - M * vel, my + M); g.lineTo(mx + M * vel, my - M); g.stroke();
    g.strokeStyle = accent(); g.lineWidth = 2.4;
    g.beginPath(); g.moveTo(mx - M, my + M * vel); g.lineTo(mx + M, my - M * vel); g.stroke();
    g.fillStyle = ink3(); g.font = '11px ui-sans-serif, system-ui';
    g.fillText('time axis: v', mx - M, my - M - 6);
    g.fillText('simultaneity: 1/v', mx - M, my + M + 16);

    const z = law.farSide(v);
    readout(host, out
      ? `value <b>${v.toFixed(2)}</b> is past the horizon<br>its inside partner <b>${(1 / v).toFixed(3)}</b><br>rapidity <b>${z.re.toFixed(3)} + iπ/2</b>`
      : `value <b>${v.toFixed(2)}</b><br>rapidity <b>${z.re.toFixed(3)}</b><br>simultaneity slope <b>${(1 / v).toFixed(2)}</b>`);
  }
  draw();
  window.addEventListener('resize', draw);
}

/* ================================================================ 9 · Channels that forget */
export function simChannels(host) {
  const cv = host.querySelector('canvas');
  let mode = 0, step = 0, t0 = 0;
  const REV = [[1.6, 0, 0], [0, 0.7, 0], [0, 0, 1.15]];              // positive diagonal: an automorphism
  const FWD = [[0.6, 0.3, 0.2], [0.25, 0.5, 0.3], [0.15, 0.2, 0.5]]; // sends the cone into itself

  host.querySelectorAll('.seg button').forEach((b, i) =>
    b.addEventListener('click', () => {
      mode = i; step = 0; t0 = 0;
      host.querySelectorAll('.seg button').forEach((x, j) => x.setAttribute('aria-pressed', j === i));
    }));

  let cloud = [];
  const reset = () => {
    cloud = [];
    for (let i = 0; i < 160; i++) {
      const a = Math.random(), b = Math.random() * (1 - a);
      cloud.push([a + 0.02, b + 0.02, 1 - a - b + 0.02]);
    }
  };
  reset();

  function draw(now) {
    if (!t0) t0 = now;
    if (now - t0 > 900) {
      t0 = now;
      if (step < 6) { cloud = cloud.map((p) => cones.apply(mode === 0 ? REV : FWD, p)); step++; }
      else { reset(); step = 0; }
    }
    const { g, w, h } = fitCanvas(cv);
    const S = Math.min(w * 0.42, h * 0.8), cx = w / 2, cy = h / 2 + S * 0.16;
    const V = [[cx, cy - S * 0.62], [cx - S * 0.56, cy + S * 0.34], [cx + S * 0.56, cy + S * 0.34]];
    g.strokeStyle = rule(); g.lineWidth = 1.2;
    g.beginPath(); V.forEach((p, i) => (i ? g.lineTo(...p) : g.moveTo(...p))); g.closePath(); g.stroke();
    g.font = '11px ui-sans-serif, system-ui'; g.fillStyle = ink3();
    g.fillText('A', V[0][0] - 4, V[0][1] - 8);
    g.fillText('B', V[1][0] - 12, V[1][1] + 14);
    g.fillText('C', V[2][0] + 6, V[2][1] + 14);

    const P = (p) => {
      const s = p[0] + p[1] + p[2];
      const [a, b, c] = [p[0] / s, p[1] / s, p[2] / s];
      return [a * V[0][0] + b * V[1][0] + c * V[2][0], a * V[0][1] + b * V[1][1] + c * V[2][1]];
    };
    g.fillStyle = mode === 0 ? cool() : accent();
    cloud.forEach((p) => { const [x, y] = P(p); g.globalAlpha = .55; g.beginPath(); g.arc(x, y, 2.4, 0, TAU); g.fill(); });
    g.globalAlpha = 1;

    let dmax = 0;
    for (let i = 0; i < 40; i++) dmax = Math.max(dmax, cones.hilbert(cloud[i], cloud[(i + 17) % 40]));
    const k = cones.birkhoff(mode === 0 ? REV : FWD);
    readout(host, mode === 0
      ? `reversible update<br>spread <b>${dmax.toFixed(3)}</b><br><b>distances kept</b>`
      : `forward-only update<br>spread <b>${dmax.toFixed(3)}</b><br>shrinks by ≤ <b>tanh(Δ/4) = ${k.toFixed(2)}</b>`);
  }
  onScreen(cv, draw);
  draw(0);
}

/* ================================================================ 10 · Two minds lock */
export function simLocking(host) {
  const cv = host.querySelector('canvas');
  let phi = 1.2, beta = 1, kind = 'tanh';
  let d = 0.1, hist = [];

  const ctls = host.querySelector('.ctls');
  slider(ctls, { min: 0, max: 4, step: .01, value: 1.2, label: 'drive Φ' }, (v) => { phi = v; hist = []; });
  slider(ctls, { min: .1, max: 2, step: .01, value: 1, label: 'coupling β' }, (v) => { beta = v; hist = []; });
  host.querySelectorAll('.seg button').forEach((b, i) =>
    b.addEventListener('click', () => {
      kind = ['tanh', 'sin', 'sinh'][i]; d = 0.1; hist = [];
      host.querySelectorAll('.seg button').forEach((x, j) => x.setAttribute('aria-pressed', j === i));
    }));

  function draw() {
    for (let i = 0; i < 12; i++) d = coupling.step(d, phi, beta, kind, 0.01);
    if (!Number.isFinite(d) || Math.abs(d) > 40) d = 0.1;
    hist.push(d); if (hist.length > 420) hist.shift();

    const { g, w, h } = fitCanvas(cv);
    const L = 40, Rp = 16, T = 16, B = 26;
    const span = 6;
    const X = (i) => L + (i / 420) * (w - L - Rp);
    const Y = (v) => T + (1 - (v + span) / (2 * span)) * (h - T - B);
    g.strokeStyle = rule(); g.lineWidth = 1;
    g.beginPath(); g.moveTo(L, Y(0)); g.lineTo(w - Rp, Y(0)); g.stroke();
    g.font = '11px ui-sans-serif, system-ui'; g.fillStyle = ink3();
    g.fillText('gap between the two', L, T + 2);

    const lock = coupling.lockGap(phi, beta, kind);
    if (lock !== null && Math.abs(lock) < span) {
      g.strokeStyle = good(); g.setLineDash([4, 4]); g.lineWidth = 1.4;
      g.beginPath(); g.moveTo(L, Y(lock)); g.lineTo(w - Rp, Y(lock)); g.stroke(); g.setLineDash([]);
    }
    g.strokeStyle = accent(); g.lineWidth = 2; g.beginPath();
    hist.forEach((v, i) => {
      const y = Y(Math.max(-span, Math.min(span, v)));
      i ? g.lineTo(X(i), y) : g.moveTo(X(i), y);
    });
    g.stroke();

    const state = lock !== null ? 'locked' : (kind === 'sin' ? 'slipping' : 'split apart');
    readout(host, `${kind} coupling<br>gap <b>${d.toFixed(2)}</b><br><b style="color:${lock !== null ? good() : bad()}">${state}</b>`);
  }
  onScreen(cv, draw);
  draw(0);
}

/* ================================================================ 11 · The dial */
export function simDial(host) {
  const cv = host.querySelector('canvas');
  let al = 0;
  slider(host.querySelector('.ctls'), { min: -5, max: 1, step: .01, value: 0, label: 'dial α' },
    (v) => { al = v; draw(); });

  function draw() {
    const { g, w, h } = fitCanvas(cv);
    const S = Math.min(w * 0.42, h - 52), ox = w / 2 - S - 18, oy = 22;
    // combination surface as a heat grid
    const N = 34;
    for (let i = 0; i < N; i++) {
      for (let j = 0; j < N; j++) {
        const a = (i + 0.5) / N * 0.92, b = (j + 0.5) / N * 0.92;
        const e = Math.max(0, Math.min(1, law.dial(a, b, al)));
        const l = 1 - e;
        g.fillStyle = `rgb(${Math.round(255 - 150 * (1 - l))}, ${Math.round(150 + 90 * l)}, ${Math.round(110 + 120 * l)})`;
        g.fillRect(ox + (i / N) * S, oy + (1 - (j + 1) / N) * S, S / N + 1, S / N + 1);
      }
    }
    g.strokeStyle = rule(); g.strokeRect(ox, oy, S, S);
    g.font = '11px ui-sans-serif, system-ui'; g.fillStyle = ink3();
    g.fillText('drug A →', ox, oy + S + 16);
    g.save(); g.translate(ox - 8, oy + S); g.rotate(-Math.PI / 2); g.fillText('drug B →', 0, 0); g.restore();

    // the dial itself: combined effect of two equal effects
    const px = w / 2 + 10, pw = Math.min(w / 2 - 26, S + 20), ph = S;
    const X = (a) => px + ((a + 5) / 6) * pw;
    const Y = (v) => oy + (1 - v) * ph;
    g.strokeStyle = rule(); g.lineWidth = 1;
    g.beginPath(); g.moveTo(px, Y(0)); g.lineTo(px + pw, Y(0)); g.stroke();
    g.strokeStyle = cool(); g.lineWidth = 2; g.beginPath();
    for (let a = -5; a <= 1; a += 0.02) {
      const v = law.dial(0.4, 0.4, a);
      a === -5 ? g.moveTo(X(a), Y(v)) : g.lineTo(X(a), Y(v));
    }
    g.stroke();
    [[0, 'Bliss'], [1, 'Loewe'], [-1, 'Einstein']].forEach(([a, t]) => {
      g.fillStyle = ink3();
      g.beginPath(); g.arc(X(a), Y(law.dial(0.4, 0.4, a)), 3.5, 0, TAU); g.fill();
      g.fillText(t, X(a) - 14, Y(law.dial(0.4, 0.4, a)) - 9);
    });
    g.fillStyle = accent();
    g.beginPath(); g.arc(X(al), Y(law.dial(0.4, 0.4, al)), 5.5, 0, TAU); g.fill();
    g.fillStyle = ink3(); g.fillText('α →', px, oy + ph + 16);

    const e = law.dial(0.4, 0.4, al);
    readout(host, `α = <b>${al.toFixed(2)}</b><br>0.40 with 0.40 gives <b>${e.toFixed(3)}</b><br>` +
      (Math.abs(al) < .02 ? 'independent action' : al > .9 ? 'the odds add' : Math.abs(al + 1) < .02 ? 'Einstein' : ''));
  }
  draw();
  window.addEventListener('resize', draw);
}

/* ================================================================ 12 · Your mind on the disk */
export function simIda(host) {
  const cv = host.querySelector('canvas');
  const FEATS = [
    { name: 'alpha', th: 0.0, z: 0.6 },
    { name: 'theta', th: TAU / 4, z: -0.3 },
    { name: 'beta', th: TAU / 2, z: 0.2 },
    { name: '1/f', th: (3 * TAU) / 4, z: -0.5 },
  ];
  const ctls = host.querySelector('.ctls');
  FEATS.forEach((f) => slider(ctls, { min: -2.5, max: 2.5, step: .01, value: f.z, label: f.name },
    (v) => { f.z = v; draw(); }));

  function draw() {
    const { g, cx, cy, R } = frame(cv);
    disc(g, cx, cy, R);
    g.strokeStyle = rule();
    for (let rho = 1; rho <= 3; rho++) {
      const r = Math.tanh(rho / 2) * R;
      g.beginPath(); g.arc(cx, cy, r, 0, TAU); g.stroke();
    }
    const kappa = 0.6;
    // hyperbolic: compose the feature rapidities by Mobius addition, in the declared order
    let p = C(0, 0);
    FEATS.forEach((f) => { p = disk.add(p, disk.fromPolar(f.z * kappa, f.th)); });
    // reverse order, to show the composition defect
    let q = C(0, 0);
    [...FEATS].reverse().forEach((f) => { q = disk.add(q, disk.fromPolar(f.z * kappa, f.th)); });
    // flat comparator: add the vectors, then map once
    let vx = 0, vy = 0;
    FEATS.forEach((f) => { vx += f.z * kappa * Math.cos(f.th); vy += f.z * kappa * Math.sin(f.th); });
    const vm = Math.hypot(vx, vy);
    const flat = vm < 1e-9 ? C(0, 0) : disk.fromPolar(vm, Math.atan2(vy, vx));

    g.font = '11px ui-sans-serif, system-ui';
    FEATS.forEach((f) => {
      const e = disk.fromPolar(2.6, f.th);
      g.fillStyle = ink3();
      g.fillText(f.name, cx + e.x * R * 0.97 - 12, cy + e.y * R * 0.97 + 4);
    });

    const dot = (pt, col, r, label) => {
      g.fillStyle = col; g.beginPath(); g.arc(cx + pt.x * R, cy + pt.y * R, r, 0, TAU); g.fill();
      if (label) { g.fillStyle = ink2(); g.fillText(label, cx + pt.x * R + 8, cy + pt.y * R - 7); }
    };
    dot(flat, ink3(), 4, 'flat');
    dot(q, cool(), 3.5, '');
    dot(p, accent(), 6, 'you');
    g.fillStyle = accent(); g.beginPath(); g.arc(cx, cy, 3, 0, TAU); g.fill();
    g.strokeStyle = ink3(); g.lineWidth = 1; g.setLineDash([2, 3]);
    g.beginPath(); g.moveTo(cx, cy); g.lineTo(cx + p.x * R, cy + p.y * R); g.stroke(); g.setLineDash([]);

    readout(host, `displacement <b>${disk.distance(C(0, 0), p).toFixed(2)}</b><br>` +
      `order defect <b>${disk.distance(p, q).toFixed(2)}</b><br>` +
      `flat says <b>${disk.distance(C(0, 0), flat).toFixed(2)}</b>`);
  }
  draw();
  window.addEventListener('resize', draw);
}

/* ---------------------------------------------------------------- hero backdrop */
export function heroField(cv) {
  const pts = [];
  for (let k = 1; k <= 8; k++) {
    const rho = k * 0.7;
    const n = Math.max(5, Math.round(disk.circumference(rho) * 0.55));
    for (let i = 0; i < n; i++) pts.push({ rho, th: (TAU * i) / n + k * 0.4 });
  }
  function draw(now) {
    const { g, w, h } = fitCanvas(cv);
    const cx = w / 2, cy = h / 2, R = Math.max(w, h) * 0.62;
    const drift = (now || 0) / 26000;
    g.fillStyle = css('--ink-3');
    for (const s of pts) {
      const p = disk.fromPolar(s.rho, s.th + drift * (1 + s.rho * 0.1));
      const d = Math.hypot(p.x, p.y);
      const scale = 1 - d * d;
      g.globalAlpha = Math.min(0.5, 0.06 + scale * 0.75);
      g.beginPath(); g.arc(cx + p.x * R, cy + p.y * R, Math.max(0.5, 2.6 * scale), 0, TAU); g.fill();
    }
    g.globalAlpha = 1;
  }
  onScreen(cv, draw);
  draw(0);
}
