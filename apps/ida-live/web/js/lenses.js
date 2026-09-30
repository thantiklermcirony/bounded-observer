// Lenses: different ways of looking at the same live signals.
// Every lens draws real samples at real positions; nothing is decorative data.
//
// Stream  - you stand at the centre of a hyperbolic plane. Each band is a wave riding a
//           hypercycle (a line at fixed distance from the flow axis). New samples appear at
//           the front horizon and are carried past you toward the back horizon by a
//           hyperbolic translation, an isometry, so every sample is a true point of the plane.
// Tunnel  - the same waves in first person: they fly out of the distance and past you.
// Map     - the IDA state map: your point against your frozen reference.
// Aurora  - the whole spectrum, 1-45 Hz around the circle, flowing outward in time.
// Web     - the four electrodes and how strongly each pair moves together, per band.

import { BANDS, FS, N, PAIRS, SPEC_BINS, SPEC_HZ } from "./dsp.js";
import { hsl, hex } from "./gl.js";

export const BAND_COLORS = {
  delta: hex("#7C6CFF"), theta: hex("#3FA7FF"), alpha: hex("#2EF2C4"), beta: hex("#EAF2FF"), gamma: hex("#FF5FD0"),
};
// Display-only height scale per band. Fast bands pack many cycles into little space, so
// they are drawn lower to stay readable. It is constant, so changes over time are real.
export const BAND_HEIGHT = { delta: 1.0, theta: 0.8, alpha: 0.62, beta: 0.45, gamma: 0.34 };
export const BAND_GLYPH = { delta: "δ", theta: "θ", alpha: "α", beta: "β", gamma: "γ" };
const AMBER = hex("#FFB45C"), TEAL = hex("#5FE3D6"), GREY = [0.55, 0.58, 0.64];

const SHEET_STEP = 8; // rainbow sheets are built from every 8th sample (32 per second)
const clamp = (x, a, b) => (x < a ? a : x > b ? b : x);
const smooth = (x) => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
function mix(a, b, t) { return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]; }

// ------------------------------------------------------------------ hyperbolic helpers
// Fermi coordinates (s along the flow axis, u across it) to the Poincaré disk,
// returned in screen orientation: x to the right, y downward, front = y < 0.
function fermi(s, u) {
  const a = Math.exp(Math.min(s, 30)), X = a * Math.tanh(u), Y = a / Math.cosh(u);
  const D = X * X + (Y + 1) * (Y + 1);
  return [(2 * X) / D, (X * X + Y * Y - 1) / D];
}
// Möbius map sending p to the origin: you are always at the centre
function mobius(x, y, px, py) {
  const nr = x - px, ni = y - py;
  const dr = 1 - (px * x + py * y), di = -(px * y - py * x);
  const d = dr * dr + di * di;
  return [(nr * dr + ni * di) / d, (ni * dr - nr * di) / d];
}
function mobiusInv(x, y, px, py) { return mobius(x, y, -px, -py); }

// plane tilted away from you, seen in perspective
class Plane {
  constructor(W, H, R, tiltDeg, cyFrac = 0.5) {
    this.W = W; this.H = H; this.R = R;
    const t = (tiltDeg * Math.PI) / 180;
    this.sin = Math.sin(t); this.cos = Math.cos(t); this.D = 2.3;
    this.cx = W / 2; this.cy = H * cyFrac;
  }
  // disk point -> [px, py, pixels per hyperbolic unit]
  p(x, y) {
    const Z = this.D - y * this.sin, k = this.D / Z;
    const r2 = x * x + y * y;
    return [this.cx + x * k * this.R, this.cy + y * this.cos * k * this.R, Math.max(0, (1 - r2) / 2) * k * this.R];
  }
}

function statePoint(ctx) {
  const st = ctx.state || {};
  if (!ctx.disp.ida || !st.calibrated || st.x === undefined) return [0, 0];
  const k = ctx.disp.ida_coupling ?? 1;
  let x = st.x, y = -st.y; // map y is up; screen y is down
  const r = Math.hypot(x, y);
  if (r > 1e-9 && k !== 1) { const rr = Math.tanh(k * Math.atanh(Math.min(r, 0.999999))); x *= rr / r; y *= rr / r; }
  return [x, y];
}

function refAmps(ctx) { return BANDS.map((_, b) => ctx.hub.refAmp(b, ctx.status && ctx.status.reference)); }

// strands to draw: [{band, b, source, lane}]
function strands(ctx, laneGap) {
  const bands = BANDS.filter((b) => ctx.disp.bands.includes(b));
  const out = [];
  const n = bands.length;
  bands.forEach((band, j) => {
    const b = BANDS.indexOf(band);
    const lane = (j - (n - 1) / 2) * laneGap;
    if (ctx.disp.hemispheres) {
      out.push({ band, b, source: "L", lane: lane - laneGap * 0.2, side: -1 });
      out.push({ band, b, source: "R", lane: lane + laneGap * 0.2, side: 1 });
    } else out.push({ band, b, source: "all", lane, side: 0 });
  });
  return out;
}

function rainbowAlpha(c, thr) { return smooth((c - thr) / Math.max(0.02, 1 - thr)); }

// ================================================================== STREAM
export function drawStream(ctx) {
  const { batch: B, W, H, hub, disp } = ctx;
  const R = Math.min(W, H) * 0.56 * (disp.zoom || 1);
  const P = new Plane(W, H, R, disp.tilt, 0.53);
  const v = disp.speed, s0 = 2.1, sMax = 5.6;
  const [px, py] = statePoint(ctx);
  const amps = refAmps(ctx);
  const tNow = ctx.tDisp; // display position in samples (fractional)
  const labels = [];
  const glow = disp.glow;
  const proj = (s, u) => { const [x, y] = fermi(s, u); const [mx, my] = mobius(x, y, px, py); return P.p(mx, my); };

  // --- grid: geodesics across the flow (they travel with it) and the lane rails
  if (disp.grid) {
    const step = 0.5, off = ((tNow / FS) * v) % step;
    for (let s = -s0 - 2 + off; s < sMax + 1; s += step) {
      const pts = [];
      for (let u = -3.2; u <= 3.2; u += 0.08) {
        const [X, Y, sc] = proj(s, u);
        pts.push(X, Y, Math.max(0.4, sc * 0.004), 0.45, 0.6, 0.9, 0.07 * glow);
      }
      B.ribbon(pts, 0);
    }
    for (const u of [-2.4, -1.6, -0.8, 0, 0.8, 1.6, 2.4]) {
      const pts = [];
      for (let s = -6; s <= 6; s += 0.08) { const [X, Y, sc] = proj(s, u); pts.push(X, Y, Math.max(0.4, sc * 0.003), 0.45, 0.6, 0.9, 0.045 * glow); }
      B.ribbon(pts, 0);
    }
  }
  // horizon (the disk's boundary)
  {
    const pts = [];
    for (let k = 0; k <= 180; k++) {
      const a = (k / 180) * Math.PI * 2;
      const [X, Y] = P.p(Math.cos(a) * 0.998, Math.sin(a) * 0.998);
      pts.push(X, Y, 1.1, 0.4, 0.62, 0.95, 0.35);
    }
    B.ribbon(pts, 6);
  }
  // "now" line at the front
  {
    const pts = [];
    for (let u = -3; u <= 3; u += 0.05) { const [X, Y, sc] = proj(-s0, u); pts.push(X, Y, Math.max(0.5, sc * 0.006), 0.8, 0.9, 1, 0.16); }
    B.ribbon(pts, 3);
    const [X, Y] = proj(-s0, 2.9);
    labels.push({ text: "now", x: X + 8, y: Y, cls: "tag" });
  }

  const S = strands(ctx, disp.hemispheres ? 0.8 : 0.72);
  const thr = disp.rainbow_threshold;
  const gain = disp.gain;
  const lines = new Map(); // strand key -> sampled centre points for sheets
  const nAvail = Math.min(hub.n, N - FS);
  const newest = Math.min(Math.floor(tNow), hub.n - 1);

  for (const st of S) {
    const val = hub.val[`${st.source}|${st.band}`], env = hub.env[`${st.source}|${st.band}`];
    const A = amps[st.b];
    const col = BAND_COLORS[st.band];
    const corrLR = hub.corrLR[st.b];
    const pts = [], sheetPts = [];
    let lx = -1e9, ly = -1e9;
    for (let i = newest; i > newest - nAvail && i >= 0; i--) {
      const age = (tNow - i) / FS;
      const s = -s0 + age * v;
      if (s > sMax) break;
      const k = hub.idx(i);
      const x = val[k] / A, e = env[k] / A;
      const u = st.lane + gain * 0.13 * BAND_HEIGHT[st.band] * clamp(x, -4, 4);
      const [X, Y, sc] = proj(s, u);
      if (i % SHEET_STEP === 0) sheetPts.push(X, Y, k);
      const d = Math.hypot(X - lx, Y - ly);
      if (d < 1.6) continue;
      lx = X; ly = Y;
      const clean = hub.clean[k];
      const wHyp = disp.amplitude ? 0.003 + 0.0105 * clamp(e, 0, 4) : 0.006;
      let c = col;
      if (!disp.hemispheres && disp.rainbows) {
        const r = rainbowAlpha(corrLR[k], thr);
        if (r > 0) c = mix(col, hsl(age * 0.09 + ctx.time * 0.03, 0.9, 0.62), r * 0.75);
      }
      if (!clean) c = mix(c, GREY, 0.8);
      const fadeIn = smooth((age * v) / 0.35);
      const a = (clean ? 0.85 : 0.28) * fadeIn * (disp.amplitude ? 0.5 + 0.5 * clamp(e, 0, 1.5) / 1.5 : 0.8);
      pts.push(X, Y, Math.max(0.55, wHyp * sc), c[0], c[1], c[2], a * glow);
    }
    B.ribbon(pts, 2.6);
    lines.set(st, sheetPts);
    // label at the front of each lane
    const [LX, LY] = proj(-s0 + 0.25, st.lane);
    if (st.side <= 0) labels.push({ text: BAND_GLYPH[st.band], x: LX, y: LY - 16, cls: `glyph ${st.band}` });
  }

  // --- rainbow sheets where neighbouring signals move together
  if (disp.rainbows) {
    const pairs = [];
    if (disp.hemispheres) {
      for (let j = 0; j + 1 < S.length; j += 2) pairs.push([S[j], S[j + 1], hub.corrLR[S[j].b]]);
    } else {
      for (let j = 0; j + 1 < S.length; j++) {
        const a = S[j], b = S[j + 1];
        if (b.b === a.b + 1) pairs.push([a, b, hub.corrBand[a.b]]);
      }
    }
    for (const [sa, sb, corr] of pairs) {
      const A = lines.get(sa), Bp = lines.get(sb);
      if (!A || !Bp) continue;
      // both lines hold the same samples (every SHEET_STEP-th), so point j is the same moment
      const n = Math.min(A.length, Bp.length) / 3;
      const LA = [], LB = [];
      for (let j = 0; j < n; j++) {
        const k = A[j * 3 + 2];
        const r = rainbowAlpha(corr[k], thr) * (hub.clean[k] ? 1 : 0.2);
        const h = (j / n) * 1.3 - ctx.time * 0.05;
        const ca = hsl(h, 0.95, 0.6), cb = hsl(h + 0.18, 0.95, 0.6);
        const al = r * 0.22 * glow;
        LA.push(A[j * 3], A[j * 3 + 1], ca[0], ca[1], ca[2], al);
        LB.push(Bp[j * 3], Bp[j * 3 + 1], cb[0], cb[1], cb[2], al);
      }
      B.sheet(LA, LB);
    }
  }

  // --- you, and your reference
  {
    const [X, Y, sc] = P.p(0, 0);
    B.ring(X, Y, 9, 0.9, [1, 1, 1, 0.55], 40, 3);
    B.glowDisc(X, Y, 5, [1, 1, 1, 0.5]);
    if (ctx.state && ctx.state.calibrated && disp.ida) {
      const [rx, ry] = P.p(-px, -py);
      B.ribbon([rx - 7, ry, 0.8, ...TEAL, 0.7, rx + 7, ry, 0.8, ...TEAL, 0.7], 2);
      B.ribbon([rx, ry - 7, 0.8, ...TEAL, 0.7, rx, ry + 7, 0.8, ...TEAL, 0.7], 2);
      labels.push({ text: "reference", x: rx + 10, y: ry + 12, cls: "tag teal" });
    }
    void sc;
  }
  return { labels, bg: { cx: P.cx, cy: P.cy, r: R, disk: 0 } };
}

// ================================================================== TUNNEL
export function drawTunnel(ctx) {
  const { batch: B, W, H, hub, disp } = ctx;
  const f = Math.min(W, H) * 0.36;
  const cx = W / 2, cy = H / 2;
  const zFar = 10, zNear = 0.32, V = disp.speed * 2.4;
  const [px, py] = statePoint(ctx);
  const ox = -px * 0.9, oy = -py * 0.9;
  const amps = refAmps(ctx);
  const tNow = ctx.tDisp, newest = Math.min(Math.floor(tNow), hub.n - 1);
  const nAvail = Math.min(hub.n, N - FS);
  const glow = disp.glow, gain = disp.gain, thr = disp.rainbow_threshold;
  const labels = [];
  const pr = (X, Y, z) => [cx + ((X + ox) / z) * f, cy + ((Y + oy) / z) * f];

  // rings of the tunnel, travelling toward you once per second
  if (disp.grid) {
    const off = (tNow / FS) % 1;
    for (let a = off; a < zFar / V + 1; a += 1) {
      const z = zFar - (a - off + off) * V;
      const zz = zFar - a * V;
      if (zz < zNear) continue;
      const pts = [];
      for (let k = 0; k <= 96; k++) {
        const t = (k / 96) * Math.PI * 2;
        const [X, Y] = pr(Math.cos(t) * 1.25, Math.sin(t) * 1.25, zz);
        pts.push(X, Y, Math.max(0.4, 1.4 / zz), 0.45, 0.6, 0.9, 0.08 * glow * smooth((zFar - zz) / 2) * smooth((zz - zNear) / 0.5));
      }
      B.ribbon(pts, 0);
      void z;
    }
  }
  // strands around the wall
  const bands = BANDS.filter((b) => disp.bands.includes(b));
  const S = [];
  bands.forEach((band, j) => {
    const b = BANDS.indexOf(band);
    if (disp.hemispheres) {
      const spread = Math.PI * 0.7, t = bands.length > 1 ? j / (bands.length - 1) : 0.5;
      const thL = Math.PI - spread / 2 + t * spread; // left wall
      S.push({ band, b, source: "L", th: thL });
      S.push({ band, b, source: "R", th: Math.PI - thL }); // mirrored on the right
    } else {
      S.push({ band, b, source: "all", th: Math.PI / 2 + (j / bands.length) * Math.PI * 2 });
    }
  });
  const lines = new Map();
  for (const st of S) {
    const val = hub.val[`${st.source}|${st.band}`], env = hub.env[`${st.source}|${st.band}`];
    const A = amps[st.b], col = BAND_COLORS[st.band];
    const c0 = Math.cos(st.th), s0 = Math.sin(st.th);
    const pts = [], keep = [];
    let lx = -1e9, ly = -1e9;
    for (let i = newest; i > newest - nAvail && i >= 0; i--) {
      const age = (tNow - i) / FS;
      const z = zFar - age * V;
      if (z < zNear) break;
      const k = hub.idx(i);
      const x = val[k] / A, e = env[k] / A;
      const th = st.th + gain * 0.08 * BAND_HEIGHT[st.band] * clamp(x, -4, 4);
      const [X, Y] = pr(Math.cos(th), Math.sin(th), z);
      const fade0 = smooth((zFar - z) / 2.5) * smooth((z - zNear) / 0.6);
      if (i % SHEET_STEP === 0) keep.push(X, Y, k, fade0);
      if (Math.hypot(X - lx, Y - ly) < 1.8) continue;
      lx = X; ly = Y;
      const clean = hub.clean[k];
      const wW = disp.amplitude ? 0.0025 + 0.0065 * clamp(e, 0, 4) : 0.004;
      let c = col;
      if (!disp.hemispheres && disp.rainbows) {
        const rr = rainbowAlpha(hub.corrLR[st.b][k], thr);
        if (rr > 0) c = mix(col, hsl(age * 0.2 + ctx.time * 0.03, 0.9, 0.62), rr * 0.75);
      }
      if (!clean) c = mix(c, GREY, 0.8);
      const fade = smooth((zFar - z) / 2.5) * smooth((z - zNear) / 0.6);
      pts.push(X, Y, Math.max(0.55, (wW / z) * f), c[0], c[1], c[2], (clean ? 0.85 : 0.28) * fade * glow);
    }
    B.ribbon(pts, 3);
    lines.set(st, keep);
  }
  if (disp.rainbows && S.length > 1) {
    const pairs = [];
    if (disp.hemispheres) for (let j = 0; j + 1 < S.length; j += 2) pairs.push([S[j], S[j + 1], hub.corrLR[S[j].b]]);
    else for (let j = 0; j < S.length; j++) { const a = S[j], b = S[(j + 1) % S.length]; if (b.b === a.b + 1) pairs.push([a, b, hub.corrBand[a.b]]); }
    for (const [sa, sb, corr] of pairs) {
      const A = lines.get(sa), Bb = lines.get(sb);
      const n = Math.min(A.length, Bb.length) / 4;
      const LA = [], LB = [];
      for (let j = 0; j < n; j++) {
        const k = A[j * 4 + 2];
        const r = rainbowAlpha(corr[k], thr) * A[j * 4 + 3];
        const h = j / n + ctx.time * 0.04;
        const ca = hsl(h, 0.95, 0.6), cb = hsl(h + 0.2, 0.95, 0.6);
        LA.push(A[j * 4], A[j * 4 + 1], ca[0], ca[1], ca[2], r * 0.2 * glow);
        LB.push(Bb[j * 4], Bb[j * 4 + 1], cb[0], cb[1], cb[2], r * 0.2 * glow);
      }
      B.sheet(LA, LB);
    }
  }
  // vanishing point and you
  B.glowDisc(cx + (ox / zFar) * f, cy + (oy / zFar) * f, 30, [0.5, 0.7, 1, 0.12]);
  labels.push({ text: "now", x: cx + (ox / zFar) * f + 14, y: cy + (oy / zFar) * f - 14, cls: "tag" });
  B.ring(cx, cy, 10, 0.8, [1, 1, 1, 0.35], 40, 2);
  for (const st of S) {
    if (st.source === "R") continue;
    const [X, Y] = pr(Math.cos(st.th) * 1.35, Math.sin(st.th) * 1.35, 2.2);
    labels.push({ text: BAND_GLYPH[st.band], x: X, y: Y, cls: `glyph ${st.band}` });
  }
  return { labels, bg: { cx, cy, r: Math.max(W, H), disk: 0 } };
}

// ================================================================== MAP
export function drawMap(ctx) {
  const { batch: B, W, H, disp } = ctx;
  const R = Math.min(W, H) * 0.4;
  const cx = W / 2, cy = H * 0.5;
  const P = (x, y) => [cx + x * R, cy - y * R]; // map y is up
  const labels = [];
  const st = ctx.state || {};
  const glow = disp.glow;
  // rings at hyperbolic distance 1, 2, 3 and spokes
  if (disp.grid) {
    for (const d of [1, 2, 3]) {
      B.ring(cx, cy, Math.tanh(d / 2) * R, 0.7, [0.5, 0.65, 0.95, 0.12 * glow], 120, 0);
      labels.push({ text: String(d), x: cx + Math.tanh(d / 2) * R * 0.707 + 4, y: cy - Math.tanh(d / 2) * R * 0.707 - 4, cls: "tag dim" });
    }
    for (let k = 0; k < 12; k++) {
      const a = (k / 12) * Math.PI * 2;
      B.ribbon([cx, cy, 0.5, 0.5, 0.65, 0.95, 0.06 * glow, cx + Math.cos(a) * R, cy + Math.sin(a) * R, 0.5, 0.5, 0.65, 0.95, 0.02 * glow], 0);
    }
  }
  B.ring(cx, cy, R, 1.2, [0.4, 0.62, 0.95, 0.4], 180, 6);
  // dead band around the reference
  const db = ctx.deadBand ?? 0.6;
  B.ring(cx, cy, Math.tanh(db / 2) * R, 0.8, [...TEAL, 0.25], 90, 3);
  // axes: which feature pulls which way
  const map = ctx.status && ctx.status.map;
  if (map) {
    for (const ax of map.axes) {
      const a = (ax.angle_deg * Math.PI) / 180;
      const z = st.z ? st.z[ax.feature] || 0 : 0;
      const len = Math.tanh((Math.abs(z) * map.kappa * ax.weight) / 2) * R * Math.sign(z);
      const col = [0.75, 0.82, 1];
      B.ribbon([cx, cy, 1.2, ...col, 0.25, cx + Math.cos(a) * len, cy - Math.sin(a) * len, 1.2, ...col, 0.5], 2);
      const lr = Math.abs(Math.sin(a)) > 0.7 ? R - 18 : R + 30;
      labels.push({ text: ax.label || ax.feature, x: cx + Math.cos(a) * lr, y: cy - Math.sin(a) * lr, cls: "tag axis" });
    }
  }
  // trail
  const tr = ctx.trail;
  if (tr.length > 1) {
    const pts = [];
    const tEnd = tr[tr.length - 1].t;
    for (const q of tr) {
      const [X, Y] = P(q.x, q.y);
      const age = tEnd - q.t;
      const a = Math.pow(1 - age / 90, 1.6);
      const c = q.clean ? AMBER : GREY;
      pts.push(X, Y, 1 + 3 * clamp(q.residue || 0, 0, 1.5), c[0], c[1], c[2], 0.7 * a * glow);
    }
    B.ribbon(pts, 3);
  }
  // markers
  for (const m of ctx.markers) {
    const [X, Y] = P(m.x, m.y);
    const c = m.kind === "probe" ? (m.answer === "aware" ? hex("#62F28B") : hex("#FF6FA8")) : m.kind === "trigger" ? AMBER : TEAL;
    B.glowDisc(X, Y, 9, [...c, 0.5]);
    B.disc(X, Y, 3, [...c, 0.9]);
  }
  // drift
  if (st.drift_x !== undefined) {
    const [X, Y] = P(st.drift_x, st.drift_y);
    B.ring(X, Y, 7, 1, [...TEAL, 0.8], 32, 2);
    labels.push({ text: "baseline drift", x: X + 10, y: Y + 12, cls: "tag teal" });
  }
  // reference and you
  B.ribbon([cx - 9, cy, 1, 1, 1, 1, 0.6, cx + 9, cy, 1, 1, 1, 1, 0.6], 2);
  B.ribbon([cx, cy - 9, 1, 1, 1, 1, 0.6, cx, cy + 9, 1, 1, 1, 1, 0.6], 2);
  if (st.x !== undefined) {
    const [X, Y] = P(st.x, st.y);
    const res = clamp(st.residue || 0, 0, 2);
    B.glowDisc(X, Y, 24 + 60 * res, [...AMBER, 0.18 + 0.25 * res]);
    if (st.clean) { B.glowDisc(X, Y, 14, [...AMBER, 0.9]); B.disc(X, Y, 5, [1, 0.95, 0.85, 1]); }
    else B.ring(X, Y, 7, 1.2, [...GREY, 0.9], 32, 1);
  } else {
    labels.push({ text: "Calibrate to place yourself on the map", x: cx, y: cy + R * 0.25, cls: "hint center" });
  }
  return { labels, bg: { cx, cy, r: R, disk: 1 } };
}

// ================================================================== AURORA
export function drawAurora(ctx) {
  const { batch: B, W, H, hub, disp } = ctx;
  const R = Math.min(W, H) * 0.47;
  const cx = W / 2, cy = H / 2;
  const labels = [];
  const rows = Math.min(hub.specN, 40 * SPEC_HZ - 1);
  if (rows < 2) return { labels, bg: { cx, cy, r: R, disk: 1 } };
  // per-frequency mean and spread over what we have, so every frequency is visible
  const mean = new Float32Array(SPEC_BINS), sd = new Float32Array(SPEC_BINS);
  const nUse = Math.min(rows, 30 * SPEC_HZ);
  for (let f = 0; f < SPEC_BINS; f++) {
    let s = 0, s2 = 0;
    for (let r = 0; r < nUse; r++) { const v = hub.spec[(((hub.specN - 1 - r) % (40 * SPEC_HZ)) + 40 * SPEC_HZ) % (40 * SPEC_HZ) * SPEC_BINS + f]; s += v; s2 += v * v; }
    mean[f] = s / nUse; sd[f] = Math.sqrt(Math.max(1e-6, s2 / nUse - mean[f] * mean[f]));
  }
  const bandOf = (hz) => BANDS.find((b) => hz >= hub.bandsHz[b][0] && hz < hub.bandsHz[b][1]) || "gamma";
  const v = disp.speed * 0.9;
  const frac = (ctx.tDisp / FS) * SPEC_HZ - Math.floor((ctx.tDisp / FS) * SPEC_HZ);
  const angle = (hz) => -Math.PI / 2 + ((hz - 0.5) / SPEC_BINS) * Math.PI * 2;
  const rad = (age) => Math.tanh((0.25 + age * v) / 2) * R;
  const maxAge = 3.2 / v;
  for (let r = 0; r < rows - 1; r++) {
    const age0 = (r + frac) / SPEC_HZ, age1 = (r + 1 + frac) / SPEC_HZ;
    if (age0 > maxAge) break;
    const row = (((hub.specN - 1 - r) % (40 * SPEC_HZ)) + 40 * SPEC_HZ) % (40 * SPEC_HZ);
    const r0 = rad(age0), r1 = rad(age1);
    for (let f = 0; f < SPEC_BINS; f++) {
      const hz = f + 1;
      const band = bandOf(hz);
      if (!disp.bands.includes(band)) continue;
      const z = (hub.spec[row * SPEC_BINS + f] - mean[f]) / sd[f];
      const a = clamp(0.18 + 0.28 * z, 0, 1) * 0.75 * disp.glow * (1 - age0 / maxAge);
      if (a < 0.02) continue;
      const col = BAND_COLORS[band];
      const a0 = angle(hz - 0.5), a1 = angle(hz + 0.5);
      const c = [col[0], col[1], col[2], a];
      B.quad(cx + Math.cos(a0) * r0, cy + Math.sin(a0) * r0, c, cx + Math.cos(a1) * r0, cy + Math.sin(a1) * r0, c,
             cx + Math.cos(a1) * r1, cy + Math.sin(a1) * r1, c, cx + Math.cos(a0) * r1, cy + Math.sin(a0) * r1, c);
    }
  }
  B.ring(cx, cy, R, 1.2, [0.4, 0.62, 0.95, 0.35], 180, 6);
  for (const b of BANDS) {
    const [lo, hi] = hub.bandsHz[b];
    const a = angle((lo + Math.min(hi, 45)) / 2 + 0.5);
    const lr = Math.abs(Math.sin(a)) > 0.8 ? R - 20 : R + 34;
    labels.push({ text: `${BAND_GLYPH[b]} ${lo}–${hi} Hz`, x: cx + Math.cos(a) * lr, y: cy + Math.sin(a) * lr, cls: `tag center ${b}` });
    const ab = angle(lo + 0.5);
    B.ribbon([cx + Math.cos(ab) * R * 0.1, cy + Math.sin(ab) * R * 0.1, 0.5, 0.6, 0.7, 0.9, 0.12, cx + Math.cos(ab) * R, cy + Math.sin(ab) * R, 0.5, 0.6, 0.7, 0.9, 0.12], 0);
  }
  labels.push({ text: "now", x: cx, y: cy, cls: "tag center" });
  return { labels, bg: { cx, cy, r: R, disk: 1 } };
}

// ================================================================== WEB
const NODE_POS = [[-0.62, 0.3], [-0.42, -0.42], [0.42, -0.42], [0.62, 0.3]]; // TP9, AF7, AF8, TP10 (front = up)
const NODE_NAME = ["TP9 · left ear", "AF7 · left forehead", "AF8 · right forehead", "TP10 · right ear"];
export function drawWeb(ctx) {
  const { batch: B, W, H, hub, disp } = ctx;
  const R = Math.min(W, H) * 0.45;
  const cx = W / 2, cy = H / 2;
  const P = (x, y) => [cx + x * R, cy + y * R];
  const labels = [];
  const glow = disp.glow, thr = disp.rainbow_threshold;
  const amps = refAmps(ctx);
  const now = Math.max(0, Math.min(Math.floor(ctx.tDisp), hub.n - 1));
  const k = hub.idx(now);
  B.ring(cx, cy, R, 1.2, [0.4, 0.62, 0.95, 0.35], 180, 6);
  // nose: front of the head
  B.ribbon([...P(-0.07, -0.93), 1, 0.6, 0.7, 0.9, 0.35, ...P(0, -1.02), 1, 0.6, 0.7, 0.9, 0.35, ...P(0.07, -0.93), 1, 0.6, 0.7, 0.9, 0.35], 1);
  const bands = BANDS.filter((b) => disp.bands.includes(b));
  // ripples: each electrode sends out a ring twice a second, as strong as it was then
  const period = FS / 2;
  for (let c = 0; c < 4; c++) {
    const [nx, ny] = NODE_POS[c];
    for (let j = 0; j < 7; j++) {
      const iEmit = Math.floor(now / period) * period - j * period;
      if (iEmit < 0) break;
      const age = (ctx.tDisp - iEmit) / FS;
      const rho = age * disp.speed * 0.8;
      if (rho > 3.5) break;
      const ke = hub.idx(iEmit);
      // strongest visible band at emission
      let best = bands[0], bv = -1;
      for (const b of bands) { const vv = hub.env[`${["TP9", "AF7", "AF8", "TP10"][c]}|${b}`][ke] / amps[BANDS.indexOf(b)]; if (vv > bv) { bv = vv; best = b; } }
      if (!best) break;
      const col = BAND_COLORS[best];
      const rr = Math.tanh(rho / 2);
      const pts = [];
      for (let q = 0; q <= 72; q++) {
        const t = (q / 72) * Math.PI * 2;
        const [x, y] = mobiusInv(Math.cos(t) * rr, Math.sin(t) * rr, nx, ny);
        const [X, Y] = P(x, y);
        pts.push(X, Y, 0.5 + 1.2 * clamp(bv, 0, 2), col[0], col[1], col[2], 0.22 * (1 - rho / 3.5) * glow * clamp(bv, 0.2, 1.5));
      }
      B.ribbon(pts, 2);
    }
  }
  // links between electrodes: geodesics, one per band, bowed apart so they don't overlap
  bands.forEach((band, j) => {
    const b = BANDS.indexOf(band);
    const col = BAND_COLORS[band];
    PAIRS.forEach(([a, c], p) => {
      const corr = hub.corrPair[b][p][k];
      const strength = clamp((Math.abs(corr) - 0.1) / 0.9, 0, 1);
      if (strength <= 0.01) return;
      const [ax, ay] = NODE_POS[a], [bx, by] = NODE_POS[c];
      const [tx, ty] = mobius(bx, by, ax, ay);
      const bow = (j - (bands.length - 1) / 2) * 0.05;
      const pts = [];
      const rb = disp.rainbows ? rainbowAlpha(corr, thr) : 0;
      for (let q = 0; q <= 40; q++) {
        const t = q / 40;
        let [x, y] = mobiusInv(tx * t, ty * t, ax, ay);
        const nxp = -(by - ay), nyp = bx - ax, nl = Math.hypot(nxp, nyp);
        x += (nxp / nl) * bow * Math.sin(Math.PI * t); y += (nyp / nl) * bow * Math.sin(Math.PI * t);
        const [X, Y] = P(x, y);
        const cc = rb > 0 ? mix(col, hsl(t * 0.8 + ctx.time * 0.08, 0.95, 0.62), rb) : corr < 0 ? mix(col, GREY, 0.6) : col;
        pts.push(X, Y, 0.6 + 3.2 * strength, cc[0], cc[1], cc[2], (0.2 + 0.7 * strength) * glow);
      }
      B.ribbon(pts, 2.5);
    });
  });
  // electrodes
  for (let c = 0; c < 4; c++) {
    const [X, Y] = P(...NODE_POS[c]);
    let tot = 0;
    for (const band of bands) tot += hub.env[`${["TP9", "AF7", "AF8", "TP10"][c]}|${band}`][k] / amps[BANDS.indexOf(band)];
    tot /= Math.max(1, bands.length);
    const q = ctx.quality ? ctx.quality[c] : "good";
    const ok = q === "good" || q === "ok" || q === "interference";
    const col = ok ? [0.85, 0.92, 1] : hex("#FF7A6B");
    B.glowDisc(X, Y, 18 + 26 * clamp(tot, 0, 2.5), [...col, 0.35]);
    B.disc(X, Y, 5, [...col, 1]);
    labels.push({ text: NODE_NAME[c] + (ok ? "" : ` · ${q}`), x: X, y: Y + (NODE_POS[c][1] < 0 ? -30 : 34), cls: `tag center${ok ? "" : " warn"}` });
  }
  return { labels, bg: { cx, cy, r: R, disk: 1 } };
}

export const LENSES = { stream: drawStream, tunnel: drawTunnel, map: drawMap, aurora: drawAurora, web: drawWeb };
