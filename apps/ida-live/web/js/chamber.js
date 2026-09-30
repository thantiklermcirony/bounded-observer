// The TAO Chamber (Murray, "Thresholded Adaptive Orchestration", SSRN 6779487, section
// "The TAO Chamber Demonstration"), driven by EEG and built from footage and sound.
// Pure logic: no drawing, no audio. Everything here follows a declared state contract
// (levels/levels.json -> "contract"), logged with every run before any outcome is seen.
//
// Player state x = (a, c, l, f)                      World state w = (q, h, n, p)
//   a arousal offset   log-odds target corridor        q clarity     saturating growth, suppressive input
//   c coherence        saturating growth               h rhythm      multiplicative gate
//   l load (effort)    inhibitory suppression          n novelty     independent threat
//   f flow membership  logistic-distance law           p perturbation independent threat
//
// Each world variable moves in its own chart (rapidity r = phi(w)) by the paper's sampled law
//   r[k+1] = r[k] + dt [ G tanh(alpha d / G) * c^p  - gamma (r - r*) + b(r) ]
// with a bounded drive, a confidence gate c^p (p = 2), a smooth barrier b(r) from
// B(e) = -log(e - eps) - log(1 - eps - e), and hard clipping only as a logged emergency stop.
// Tiers are hysteretic modes: thresholds in the log-odds chart of corridor occupancy with a
// dwell time, and tier changes are blended over tau_s so the world never jumps.

const clamp = (x, a, b) => (x < a ? a : x > b ? b : x);
const sig = (r) => 1 / (1 + Math.exp(-r));
const logit = (e) => Math.log(e / (1 - e));
const sech2 = (u) => { const c = Math.cosh(clamp(u, -30, 30)); return 1 / (c * c); };

// ------------------------------------------------------------------ the five TAO base primitives (charts)
export const CHARTS = {
  saturating: { phi: (e) => e / (1 - e), inv: (r) => r / (1 + r), de: (r) => 1 / ((1 + r) * (1 + r)) },
  suppression: { phi: (e) => (1 - e) / e, inv: (r) => 1 / (1 + r), de: (r) => -1 / ((1 + r) * (1 + r)) },
  logodds: { phi: logit, inv: sig, de: (r) => { const e = sig(r); return e * (1 - e); } },
  threat: { phi: (e) => -Math.log(1 - e), inv: (r) => 1 - Math.exp(-r), de: (r) => Math.exp(-r) },
  gate: { phi: (e) => -Math.log(e), inv: (r) => Math.exp(-r), de: (r) => -Math.exp(-r) },
};

// the declared contract (defaults; levels.json can override per level). Ranges follow the
// paper's reporting anchors: gamma in [0.1, 1.0], hysteresis width >= 0.5, eps in [0.05, 0.15].
export const CONTRACT = {
  version: "tao-chamber-1",
  eps: 0.05, kappa: 0.001, p: 2, c_min: 0.6, inadmissible_after_s: 3.0, tau_s: 2.0, dwell_s: 12.0,
  // measurement, not law: the order parameter is averaged over this many seconds of clean signal
  // before the flow law reads it (a 2 s EEG index decorrelates within 2 s; the state it stands for
  // does not), and while the signal is unclean the world holds instead of counting it as failure
  z_smooth_s: 5.0, hold_s: 10.0,
  h_plus: logit(0.7), h_minus: logit(0.2), occupancy_window_s: 12.0,
  world: {
    q: { chart: "saturating", eps: 0.05, start: 0.12, target: 0.12, alpha: 0.5, G: 1.0, gamma: 0.1, actuator: "fog, defocus, colour; audio low-pass and noise bed" },
    h: { chart: "gate", eps: 0.05, start: 0.25, gamma: 0.3, actuator: "0.1 Hz visual swell; audio breath pacer loudness; bone-conduction pulse" },
    n: { chart: "threat", eps: 0.02, start: 0.45, alpha: 0.5, G: 0.8, gamma: 0.1, actuator: "warp and shards; audio grain density" },
    p: { chart: "threat", eps: 0.05, barrier: "upper", start: 0.01, target: 0.01, gamma: 0.9, actuator: "knock events (visual and sound), bounded and ramped" },
  },
  player: {
    a: { chart: "logodds", target: 0.5, estimate: "breath rate and head motion vs your settle baseline", actuator: "perturbation pressure gain" },
    c: { chart: "saturating", estimate: "steadiness of the target signal and of breathing" },
    l: { chart: "suppression", estimate: "muscle effort (forehead and temporal EMG) and lost signal", actuator: "density and noise reduction" },
    f: { law: "logistic distance", F: "sech^2((z - z*)/tau)", estimate: "distance of the level index from the tier's target" },
  },
  anticipation: { window_s: 10, kappa_V: 1.5, kappa_A: 1.5, lambda_A: 1.0, actuator: "widen the flow band, lower sensory intensity, hold the next knock" },
};

export class Chamber {
  constructor(level, contract = null) {
    this.lv = level;
    this.K = deepMerge(deepMerge(CONTRACT, level.contract || {}), contract || {});
    this.tiers = level.tiers;
    this.near = level.corridor === "near";
    this.base = { V0: 0.25, A0: 0.5, sV: 0.1, sA: 0.1 };
    this.reset(true);
  }

  reset(full = false) {
    const K = this.K;
    this.t = 0;
    this.tier = 1; this.tierStart = 0; this.maxTier = 1; this.lastGood = 0;
    this.blend = { depth: this.tiers[0].depth, tau: this.tiers[0].tau, novelty: this.tiers[0].novelty, beta: 1 };
    this.conf = 0.5; this.lowConfSince = null; this.admissible = true;
    this.hist = []; this.occ = [];
    this.r = {};
    for (const [k, v] of Object.entries(K.world)) { const eps = v.eps ?? K.eps; this.r[k] = CHARTS[v.chart].phi(clamp(v.start, eps * 1.2, 1 - eps * 1.2)); }
    this.rp = { a: 0, c: CHARTS.saturating.phi(0.5), l: CHARTS.suppression.phi(0.2) };
    this.nextEvent = null; this.events = []; this.pending = null;
    this.work = 0; this._zPrev = null;
    this.zs = null; this.unclean_s = 0; this.lastFe = 0;
    this.log = []; this.eventNow = "";
    this.bast = { emergency: 0, pinned_s: 0, barrier_s: 0 };
    if (full) this.base = { V0: 0.25, A0: 0.5, sV: 0.1, sA: 0.1 };
  }

  get tierSpec() { return this.tiers[this.tier - 1]; }

  // baselines for critical slowing, from the settle (the paper's calibration window)
  setBaseline(zs) {
    if (zs.length < 60) return;
    const W = Math.max(20, Math.round(zs.length / 6));
    const Vs = [], As = [];
    for (let i = W; i <= zs.length; i += Math.max(1, Math.round(W / 4))) {
      const [V, A] = varAc(zs.slice(i - W, i)); Vs.push(V); As.push(A);
    }
    const m = (x) => x.reduce((a, b) => a + b, 0) / x.length;
    const s = (x) => Math.sqrt(m(x.map((v) => (v - m(x)) ** 2))) || 0.05;
    this.base = { V0: Math.max(0.02, m(Vs)), A0: m(As), sV: Math.max(0.02, s(Vs)), sA: Math.max(0.02, s(As)) };
  }

  // one world variable, one sampled step of the paper's law in its own chart
  // smooth barrier b(r) = -kappa d/dr B(phi^-1(r)), B(e) = -log(e - eps) - log(1 - eps - e)
  barrier(k, r) {
    const K = this.K, v = K.world[k], C = CHARTS[v.chart], eps = v.eps ?? K.eps;
    const e = C.inv(r), side = v.barrier || "both";                     // declared unsafe margins
    const Bp = (side === "upper" ? 0 : -1 / Math.max(1e-6, e - eps)) + (side === "lower" ? 0 : 1 / Math.max(1e-6, 1 - eps - e));
    return clamp(-K.kappa * Bp * C.de(r), -5, 5);
  }

  move(k, drive, gate, rStar, dt) {
    const K = this.K, v = K.world[k], C = CHARTS[v.chart], eps = v.eps ?? K.eps;
    const G = v.G ?? 1, alpha = v.alpha ?? 0;
    const g = alpha ? G * Math.tanh((alpha * drive) / G) * gate : 0;       // bounded drive, confidence-gated
    // the declared target is the observable rest point, so the barrier's pull there is pre-compensated
    const rRest = rStar - this.barrier(k, rStar) / v.gamma;
    let r = this.r[k];
    const b = this.barrier(k, r);
    if (Math.abs(b - this.barrier(k, rStar)) > 0.05) this.bast.barrier_s += dt;
    // the same law integrated in eight sub-steps, so the barrier can act before a single 0.25 s
    // step jumps over the margin (a strong drive toward an edge used to trip the emergency stop)
    const sub = 8, h = dt / sub;
    for (let i = 0; i < sub; i++) {
      const bi = this.barrier(k, r);
      r += h * (g - v.gamma * (r - rRest) + bi);
      if (!Number.isFinite(r)) break;
    }
    let e2 = C.inv(r);
    const lo = v.barrier === "upper" ? 1e-4 : eps / 2, hi = v.barrier === "lower" ? 1 - 1e-4 : 1 - eps / 2;
    if (!(e2 > lo && e2 < hi) || !Number.isFinite(r)) {                     // emergency stop only
      e2 = clamp(Number.isFinite(e2) ? e2 : v.start, lo + 1e-4, hi - 1e-4);
      r = C.phi(e2); this.bast.emergency += 1; (this.bast.by ||= {})[k] = (this.bast.by[k] || 0) + 1;
    }
    if ((v.barrier !== "upper" && e2 < eps * 1.5) || (v.barrier !== "lower" && e2 > 1 - eps * 1.5)) this.bast.pinned_s += dt;
    this.r[k] = r;
    return e2;
  }

  // inp: {dt, z, ze, clean, motion, live, gate, effort (settle SD), breath: {sync, conf, rate_z}}
  step(inp) {
    const K = this.K;
    const dt = clamp(inp.dt, 0, 0.1);
    this.t += dt;
    const t = this.t, spec = this.tierSpec;

    // tier changes blend over tau_s (actuator-facing variables never jump)
    const bl = this.blend;
    bl.beta = Math.min(1, bl.beta + dt / K.tau_s);
    const depth = bl.depth + (spec.depth - bl.depth) * bl.beta;
    let tau = bl.tau + (spec.tau - bl.tau) * bl.beta;
    const novelty = bl.novelty + (spec.novelty - bl.novelty) * bl.beta;

    // confidence: staleness decay while not clean; admissibility against c_min
    this.conf = inp.clean ? this.conf + (1 - this.conf) * Math.min(1, dt * 4) : this.conf * Math.exp(-2 * dt);
    if (this.conf < K.c_min) this.lowConfSince ??= t; else this.lowConfSince = null;
    this.admissible = this.lowConfSince === null || t - this.lowConfSince < K.inadmissible_after_s;
    const gate = this.admissible ? Math.pow(this.conf, K.p) : 0;         // alpha -> 0 when inadmissible

    // player state
    const breath = inp.breath || {};
    this.hist.push({ t, z: inp.z, clean: inp.clean });
    while (this.hist.length && t - this.hist[0].t > 12) this.hist.shift();
    const zc = this.hist.filter((h) => t - h.t <= 3 && h.clean).map((h) => h.z);
    const zm = zc.reduce((a, b) => a + b, 0) / Math.max(1, zc.length);
    const sd3 = Math.sqrt(zc.reduce((a, b) => a + (b - zm) ** 2, 0) / Math.max(1, zc.length));
    // c: saturating growth toward steadiness of the signal and, when known, of breathing
    const cRaw = sig(3 * (0.7 - sd3)) * (breath.conf > 0.3 ? 0.6 + 0.4 * breath.conf : 1);
    this.rp.c += (1 - Math.exp(-dt / 1.5)) * (CHARTS.saturating.phi(clamp(cRaw, 0.02, 0.98)) - this.rp.c);
    const c = CHARTS.saturating.inv(this.rp.c);
    // l: inhibitory suppression chart; effort (muscle) and lost signal load the player
    const lost = this.hist.filter((h) => t - h.t <= 3 && !h.clean).length / Math.max(1, this.hist.filter((h) => t - h.t <= 3).length);
    const lRaw = clamp(1 - (1 - sig(1.2 * ((inp.effort ?? 0) - 1))) * (1 - lost), 0.02, 0.98);
    this.rp.l += (1 - Math.exp(-dt / 1.0)) * (CHARTS.suppression.phi(lRaw) - this.rp.l);
    const l = CHARTS.suppression.inv(this.rp.l);
    // a: arousal offset in a log-odds target corridor (breath rate and motion vs settle)
    const aDrive = 0.8 * (breath.rate_z ?? 0) + 0.5 * clamp(((inp.motion || 0) - 2) / 4, -1, 3) + 0.3 * (inp.ze ?? 0);
    this.rp.a += (1 - Math.exp(-dt / 2)) * (clamp(aDrive, -4, 4) - this.rp.a);
    const a = sig(this.rp.a), aOff = this.rp.a - logit(K.player.a.target);

    // f: logistic-distance law around the tier's target (two-sided, as declared). A "near"
    // level measures distance from baseline, so its target manifold is distance zero.
    const W = this.warning(t);
    tau *= 1 + 0.5 * Math.min(1, W.score);                                  // anticipation widens the band
    // the order parameter, averaged over clean signal only
    if (inp.clean && Number.isFinite(inp.z)) {
      const Ts = Math.max(0.01, K.z_smooth_s ?? 0);
      this.zs = this.zs === null ? inp.z : this.zs + (1 - Math.exp(-dt / Ts)) * (inp.z - this.zs);
      this.unclean_s = 0;
    } else this.unclean_s += dt;
    const holding = !inp.clean && this.unclean_s < (K.hold_s ?? 10);
    const zu = this.zs ?? inp.z ?? 0;
    const F = this.near ? sech2(Math.max(0, -zu) / Math.abs(depth)) * (inp.gate ?? 1)
      : sech2((zu - depth) / tau) * (inp.gate ?? 1);
    let Fe = inp.clean ? F * gate : (holding ? this.lastFe : 0);
    if (this.lv.stability_gate) Fe *= 0.35 + 0.65 * clamp(c / 0.6, 0, 1);
    if (inp.clean) this.lastFe = Fe;
    if (inp.clean) this.occ.push({ t, Fe });                                 // missing signal is not failure
    while (this.occ.length && t - this.occ[0].t > K.occupancy_window_s) this.occ.shift();
    const TF = this.occ.length ? this.occ.reduce((s, o) => s + o.Fe, 0) / this.occ.length : 0;

    // world update, each variable in its own chart (drives are dimensionless, declared)
    // while the signal is briefly unclean the scene holds where it was (no drive, no relaxation)
    const q = holding ? CHARTS.saturating.inv(this.r.q)
      : this.move("q", 2.5 * (Fe - 0.5) + 0.8 * (c - 0.5) - 1.5 * (l - 0.2), gate, CHARTS.saturating.phi(K.world.q.target), dt);
    // h: multiplicative gate. Its target rapidity is the sum of -log of each gate that must hold:
    // breath locked to the pacer, a steady signal, a confident estimate.
    const gates = [clamp(breath.conf > 0.2 ? breath.sync ?? 0.25 : 0.25, 0.05, 0.99), clamp(c, 0.05, 0.99), clamp(this.conf, 0.05, 0.99)];
    // (the target rapidity is kept inside the declared safe margins: a product of three small gates
    // could otherwise ask for a rest point the barrier forbids, which is what tripped the emergency stops)
    const hEps = K.world.h.eps ?? K.eps;
    const hStar = clamp(gates.reduce((s, g) => s - Math.log(g), 0), CHARTS.gate.phi(1 - 1.5 * hEps), CHARTS.gate.phi(1.5 * hEps));
    const h = this.move("h", 0, 1, hStar, dt);
    const soothe = 1 - 0.5 * Math.min(1, W.score) - 0.4 * l;               // anticipation and load lower density
    const n = holding ? CHARTS.threat.inv(this.r.n)
      : this.move("n", 1.2 * novelty * soothe - 1.4 * Fe * (0.4 + 0.6 * c), 1, CHARTS.threat.phi(clamp(novelty, 0.05, 0.9)), dt);
    const pressure = 1 - 0.6 * Math.tanh(Math.max(0, aOff));               // a's actuator: pressure gain

    // perturbation events: independent hazards compose additively in the threat chart
    this.eventNow = "";
    if (inp.live && spec.perturb > 0) {
      if (this.nextEvent === null) this.nextEvent = t + spec.perturb_every_s * (0.6 + 0.8 * Math.random());
      if (W.score > 0.5 || l > 0.6) this.nextEvent += dt;                  // hold the knock while you steady
      if (t >= this.nextEvent) {
        const mag = clamp(spec.perturb * pressure * (0.8 + 0.4 * Math.random()), 0, 0.95);
        this.r.p += -Math.log(1 - mag);
        const last3 = this.occ.filter((o) => t - o.t <= 3);
        const before = last3.reduce((s, o) => s + o.Fe, 0) / Math.max(1, last3.length);
        this.pending = { t, mag, before: Math.max(0.3, before * 0.9), recovered: null };
        this.events.push(this.pending);
        this.eventNow = `${this.lv.perturbation} ${mag.toFixed(2)}`;
        this.nextEvent = t + spec.perturb_every_s * (0.6 + 0.8 * Math.random());
      }
    }
    const p = this.move("p", 0, 1, CHARTS.threat.phi(K.world.p.target), dt);
    if (this.pending && this.pending.recovered === null) {                 // the IDA return
      const since = t - this.pending.t;
      const last1 = this.occ.filter((o) => t - o.t <= 1);
      const f1 = last1.reduce((s, o) => s + o.Fe, 0) / Math.max(1, last1.length);
      if (since > 0.5 && f1 >= this.pending.before) this.pending.recovered = +since.toFixed(2);
      else if (since > 15) this.pending.recovered = 15;
    }

    // hysteretic modes (tiers): thresholds in the log-odds chart of occupancy, with dwell
    if (Fe > 0.5) this.lastGood = t;
    const rTF = logit(clamp(TF, 0.01, 0.99));
    if (inp.live && t - this.tierStart >= K.dwell_s) {
      if (rTF > K.h_plus && this.tier < this.tiers.length) this.changeTier(+1, t, depth, tau, novelty);
      else if (this.tier > 1 && rTF < K.h_minus && t - this.lastGood > K.dwell_s) this.changeTier(-1, t, depth, tau, novelty);
    }

    // semantic work: path length in the target's own coordinate (effortless = little work)
    if (this._zPrev !== null && inp.clean) this.work += Math.abs(zu - this._zPrev);
    if (inp.clean) this._zPrev = zu;

    const within = clamp(TF / 0.7, 0, 1) * clamp((t - this.tierStart) / K.dwell_s, 0.25, 1);
    return {
      tier: this.tier, name: this.tierSpec.name, F, Fe, TF, conf: this.conf, admissible: this.admissible,
      a, c, l, W: W.score, warning: W.flag, q, h, n, p, pressure, zs: zu, holding,
      pos: ((this.tier - 1) + within) / this.tiers.length, event: this.eventNow, target: depth, tau,
    };
  }

  changeTier(dir, t, depth, tau, novelty) {
    this.blend = { depth, tau, novelty, beta: 0 };
    this.tier += dir; this.tierStart = t; this.occ = []; this.nextEvent = null;
    this.maxTier = Math.max(this.maxTier, this.tier);
    this.log.push({ t: +t.toFixed(2), tier: this.tier, dir: dir > 0 ? "up" : "down" });
  }

  // critical slowing on the order parameter (the level's own coordinate): both variance and
  // lag-one autocorrelation must exceed the settle baseline by the declared margins
  warning(t) {
    const A = this.K.anticipation;
    const zw = this.hist.filter((h) => t - h.t <= A.window_s && h.clean).map((h) => h.z);
    if (zw.length < 40) return { score: 0, flag: false };
    const [V, Ac] = varAc(zw), B = this.base;
    const flag = V > B.V0 + A.kappa_V * B.sV && Ac > B.A0 + A.kappa_A * B.sA;
    const score = flag ? Math.max(0, V - B.V0) / B.V0 + A.lambda_A * Math.max(0, Ac - B.A0) : 0;
    return { score, flag };
  }

  summary() {
    const rec = this.events.filter((e) => e.recovered !== null).map((e) => e.recovered);
    const R = rec.length ? rec.reduce((a, b) => a + b, 0) / rec.length : null;
    return {
      max_tier: this.maxTier, max_tier_name: this.tiers[this.maxTier - 1].name, final_tier: this.tier,
      perturbations: this.events.length, recoveries_s: rec, mean_recovery_s: R === null ? null : +R.toFixed(2),
      semantic_work: +this.work.toFixed(2),
      efficiency: R === null ? null : +(1 / (Math.max(0.5, R) * (this.work / Math.max(1, this.t) + 0.1))).toFixed(3),
      bast: { emergency_stops: this.bast.emergency, by: this.bast.by, boundary_pinning_s: +this.bast.pinned_s.toFixed(1), barrier_active_s: +this.bast.barrier_s.toFixed(1) },
      contract: this.K.version, tier_log: this.log,
    };
  }
}

function varAc(z) {
  const m = z.reduce((a, b) => a + b, 0) / z.length;
  const V = z.reduce((a, b) => a + (b - m) ** 2, 0) / z.length;
  let num = 0, den = 0;
  for (let i = 1; i < z.length; i++) { num += (z[i] - m) * (z[i - 1] - m); den += (z[i] - m) ** 2; }
  return [V, den > 0 ? num / den : 0];
}

function deepMerge(a, b) {
  const out = Array.isArray(a) ? [...a] : { ...a };
  for (const [k, v] of Object.entries(b || {})) out[k] = v && typeof v === "object" && !Array.isArray(v) && typeof a[k] === "object" ? deepMerge(a[k], v) : v;
  return out;
}
