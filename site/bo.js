/* The Bounded Observer — the maths, in the browser.
   Every function here mirrors one in toolkit/bounded/ and names the theorem it implements.
   toolkit/tests/test_theorems.py checks the same identities numerically. */

export const law = {
  // Theorems 1 and 7: two horizons, Einstein composition on (-c, c)
  einstein: (a, b, c = 1) => (a + b) / (1 + (a * b) / (c * c)),
  rapidity: (x, c = 1) => c * Math.atanh(x / c),
  fromRapidity: (p, c = 1) => c * Math.tanh(p / c),

  // Theorem 4: the trichotomy. kappa > 0 bounded, = 0 flat, < 0 wraps
  trichotomy: (u, v, k) => {
    const d = 1 + k * u * v;
    return d === 0 ? Infinity : (u + v) / d;
  },

  // Theorem 8: the one-horizon dial. alpha = 0 Bliss, -> 1 Loewe, = -1 Einstein on [0,1)
  dial: (a, b, al) => (a + b - (1 + al) * a * b) / (1 - al * a * b),
  dialRapidity: (e, al) =>
    Math.abs(1 - al) < 1e-12 ? e / (1 - e) : Math.log((1 - al * e) / (1 - e)) / (1 - al),
  bliss: (a, b) => 1 - (1 - a) * (1 - b),
  loewe: (a, b) => { const o = a / (1 - a) + b / (1 - b); return o / (1 + o); },

  // Theorem 19: the far side. artanh x = artanh(1/x) + i pi/2 for |x| > 1
  farSide: (x) => Math.abs(x) <= 1
    ? { re: Math.atanh(x), im: 0 }
    : { re: Math.atanh(1 / x), im: Math.sign(x) * Math.PI / 2 },
};

/* Proposition 9: the boundary exponent. delta' = -k delta^gamma.
   Osgood: the ceiling is reached in finite time iff gamma < 1. */
export const boundary = {
  arrivalTime: (g, d0, k = 1) => (g >= 1 ? Infinity : Math.pow(d0, 1 - g) / (k * (1 - g))),
  roomLeft: (g, d0, t, k = 1) => {
    if (g === 1) return d0 * Math.exp(-k * t);
    const base = Math.pow(d0, 1 - g) - (1 - g) * k * t;
    if (g < 1) return base <= 0 ? 0 : Math.pow(base, 1 / (1 - g));
    return Math.pow(base, 1 / (1 - g));
  },
};

/* The Poincare disk. Complex numbers as {x, y}. Curvature -1. */
const C = (x, y) => ({ x, y });
export const disk = {
  C,
  add: (a, b) => {
    // (a + b) / (1 + conj(a) b)
    const nr = a.x + b.x, ni = a.y + b.y;
    const dr = 1 + (a.x * b.x + a.y * b.y), di = a.x * b.y - a.y * b.x;
    const q = dr * dr + di * di;
    return C((nr * dr + ni * di) / q, (ni * dr - nr * di) / q);
  },
  neg: (a) => C(-a.x, -a.y),
  abs: (a) => Math.hypot(a.x, a.y),
  mul: (a, s) => C(a.x * s, a.y * s),
  recentre(o, x) { return this.add(this.neg(o), x); },          // Theorem 29 item 2
  distance(a, b) { return 2 * Math.atanh(Math.min(this.abs(this.recentre(a, b)), 1 - 1e-12)); },
  gyration: (a, b) => {                                          // Theorem 26
    const nr = 1 + (a.x * b.x + a.y * b.y), ni = a.y * b.x - a.x * b.y;
    const dr = 1 + (a.x * b.x + a.y * b.y), di = a.x * b.y - a.y * b.x;
    const q = dr * dr + di * di;
    return C((nr * dr + ni * di) / q, (ni * dr - nr * di) / q);
  },
  gyrationAngle(a, b) { const g = this.gyration(a, b); return Math.atan2(g.y, g.x); },
  circumference: (r) => 2 * Math.PI * Math.sinh(r),              // section 8.4
  fromPolar: (rho, th) => C(Math.tanh(rho / 2) * Math.cos(th), Math.tanh(rho / 2) * Math.sin(th)),
  geodesic(a, b, n = 48) {
    const w = this.recentre(a, b), m = this.abs(w);
    if (m < 1e-12) return [a];
    const rho = Math.atanh(Math.min(m, 1 - 1e-12)), u = this.mul(w, 1 / m), out = [];
    for (let i = 0; i < n; i++) out.push(this.add(a, this.mul(u, Math.tanh((rho * i) / (n - 1)))));
    return out;
  },
};

/* Theorem 16: two coupled rapidities. dD/dt = Phi - 2 beta u(D). */
export const coupling = {
  u: { sinh: Math.sinh, tanh: Math.tanh, sin: Math.sin, linear: (d) => d },
  lockGap(phi, beta, kind) {
    const s = phi / (2 * beta);
    if (kind === 'sinh') return Math.asinh(s);
    if (kind === 'linear') return s;
    if (Math.abs(s) >= 1) return null;
    return kind === 'tanh' ? Math.atanh(s) : Math.asin(s);
  },
  step(d, phi, beta, kind, dt) { return d + dt * (phi - 2 * beta * this.u[kind](d)); },
};

/* Theorem 25 item 4: forward-only maps contract the Hilbert projective distance
   by at least tanh(Delta/4) (Birkhoff 1957). */
export const cones = {
  hilbert: (x, y) => {
    let lo = Infinity, hi = -Infinity;
    for (let i = 0; i < x.length; i++) { const r = x[i] / y[i]; if (r < lo) lo = r; if (r > hi) hi = r; }
    return Math.log(hi / lo);
  },
  apply: (M, v) => M.map((row) => row.reduce((s, m, j) => s + m * v[j], 0)),
  diameter(M) {
    const n = M.length, cols = [];
    for (let j = 0; j < n; j++) cols.push(M.map((r) => r[j]));
    let d = 0;
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) d = Math.max(d, this.hilbert(cols[i], cols[j]));
    return d;
  },
  birkhoff(M) { const d = this.diameter(M); return Number.isFinite(d) ? Math.tanh(d / 4) : 1; },
};

/* ------------------------------------------------------------------ canvas helpers */

export function fitCanvas(cv) {
  const r = Math.min(window.devicePixelRatio || 1, 2);
  const w = cv.clientWidth, h = cv.clientHeight;
  if (cv.width !== Math.round(w * r) || cv.height !== Math.round(h * r)) {
    cv.width = Math.round(w * r); cv.height = Math.round(h * r);
  }
  const g = cv.getContext('2d');
  g.setTransform(r, 0, 0, r, 0, 0);
  g.clearRect(0, 0, w, h);
  return { g, w, h };
}

export function css(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

/** Animate only while visible, and show a still frame when reduced motion is requested. */
export function onScreen(el, draw) {
  let live = false, raf = null;
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const loop = (t) => {
    raf = null;
    if (!live) return;
    draw(t);
    if (!motion.matches) raf = requestAnimationFrame(loop);
  };
  const sync = () => {
    if (raf !== null) cancelAnimationFrame(raf);
    raf = null;
    if (!live) return;
    if (motion.matches) draw(0);
    else raf = requestAnimationFrame(loop);
  };
  new IntersectionObserver((es) => {
    es.forEach((e) => {
      live = e.isIntersecting;
      sync();
    });
  }, { rootMargin: '120px' }).observe(el);
  motion.addEventListener('change', sync);
  return () => draw(motion.matches ? 0 : performance.now());
}

/** A labelled slider that calls back on input. Returns the <input>. */
export function slider(host, { min, max, step, value, label, fmt = (v) => v.toFixed(2) }, onInput) {
  const wrap = document.createElement('label');
  wrap.className = 'ctl';
  const name = document.createElement('span');
  name.className = 'ctl-name';
  name.textContent = label;
  const out = document.createElement('output');
  out.textContent = fmt(value);
  const input = document.createElement('input');
  Object.assign(input, { type: 'range', min, max, step, value });
  input.addEventListener('input', () => { out.textContent = fmt(+input.value); onInput(+input.value); });
  wrap.append(name, input, out);
  host.append(wrap);
  return input;
}
