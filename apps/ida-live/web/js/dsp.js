// Live signal processing in the display: turns the raw 256 Hz headband stream into
// band-limited waves, their amplitude envelopes, correlations and spectra.
// Everything is causal (it only uses the past), sample by sample, so what you see is
// exactly what the brain produced, delayed only by the filters' own group delay.

export const FS = 256;
export const BANDS = ["delta", "theta", "alpha", "beta", "gamma"];
export const ELECTRODES = ["TP9", "AF7", "AF8", "TP10"];
// strand sources: whole head, the two hemispheres, and each electrode
export const SOURCES = ["all", "L", "R", "TP9", "AF7", "AF8", "TP10"];
let SRC_W = {
  all: [0.25, 0.25, 0.25, 0.25], L: [0.5, 0.5, 0, 0], R: [0, 0, 0.5, 0.5],
  TP9: [1, 0, 0, 0], AF7: [0, 1, 0, 0], AF8: [0, 0, 1, 0], TP10: [0, 0, 0, 1],
};
export const PAIRS = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]];
const SECONDS = 40;
export const N = FS * SECONDS; // ring length in samples
export const SPEC_HZ = 16;     // spectrum frames per second
export const SPEC_BINS = 45;   // 1..45 Hz
const SPEC_N = SPEC_HZ * SECONDS;

// ---------------------------------------------------------------- biquads (RBJ)
function biquad(type, f0, q) {
  const w = (2 * Math.PI * f0) / FS, c = Math.cos(w), s = Math.sin(w), a = s / (2 * q);
  let b0, b1, b2;
  if (type === "lp") { b0 = (1 - c) / 2; b1 = 1 - c; b2 = (1 - c) / 2; }
  else if (type === "hp") { b0 = (1 + c) / 2; b1 = -(1 + c); b2 = (1 + c) / 2; }
  else { b0 = 1; b1 = -2 * c; b2 = 1; } // notch
  const a0 = 1 + a;
  return { b0: b0 / a0, b1: b1 / a0, b2: b2 / a0, a1: (-2 * c) / a0, a2: (1 - a) / a0, x1: 0, x2: 0, y1: 0, y2: 0 };
}
function run(f, x) {
  const y = f.b0 * x + f.b1 * f.x1 + f.b2 * f.x2 - f.a1 * f.y1 - f.a2 * f.y2;
  f.x2 = f.x1; f.x1 = x; f.y2 = f.y1; f.y1 = y;
  return y;
}
const BW = Math.SQRT1_2;

// ---------------------------------------------------------------- FFT (radix 2)
function fft(re, im) {
  const n = re.length;
  for (let i = 1, j = 0; i < n; i++) {
    let bit = n >> 1;
    for (; j & bit; bit >>= 1) j ^= bit;
    j ^= bit;
    if (i < j) { [re[i], re[j]] = [re[j], re[i]]; [im[i], im[j]] = [im[j], im[i]]; }
  }
  for (let len = 2; len <= n; len <<= 1) {
    const ang = (-2 * Math.PI) / len, wr = Math.cos(ang), wi = Math.sin(ang);
    for (let i = 0; i < n; i += len) {
      let cr = 1, ci = 0;
      for (let k = 0; k < len / 2; k++) {
        const ar = re[i + k], ai = im[i + k];
        const br = re[i + k + len / 2] * cr - im[i + k + len / 2] * ci;
        const bi = re[i + k + len / 2] * ci + im[i + k + len / 2] * cr;
        re[i + k] = ar + br; im[i + k] = ai + bi;
        re[i + k + len / 2] = ar - br; im[i + k + len / 2] = ai - bi;
        const t = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = t;
      }
    }
  }
}

// exponentially weighted correlation of two streams
class EwCorr {
  constructor(tau) { this.a = 1 - Math.exp(-1 / (tau * FS)); this.warm = Math.round(tau * FS * 1.5); this.k = 0; this.mx = 0; this.my = 0; this.sxx = 1e-9; this.syy = 1e-9; this.sxy = 0; }
  push(x, y) {
    const a = Math.max(this.a, 1 / (++this.k + 1));
    this.mx += a * (x - this.mx); this.my += a * (y - this.my);
    const dx = x - this.mx, dy = y - this.my;
    this.sxx += a * (dx * dx - this.sxx); this.syy += a * (dy * dy - this.syy); this.sxy += a * (dx * dy - this.sxy);
    if (this.k < this.warm) return 0; // not enough history yet to call anything correlated
    return this.sxy / Math.sqrt(this.sxx * this.syy + 1e-12);
  }
}

export class SignalHub {
  constructor() { this.reset(); }

  reset() {
    this.n = 0; // samples processed in total
    this.mains = 50;
    this.bandsHz = { delta: [1, 4], theta: [4, 8], alpha: [8, 13], beta: [13, 30], gamma: [30, 45] };
    this._build();
  }

  setConfig(bandsHz, mains) {
    const changed = JSON.stringify(bandsHz) !== JSON.stringify(this.bandsHz) || mains !== this.mains;
    if (!changed) return;
    this.bandsHz = { ...this.bandsHz, ...bandsHz };
    this.mains = mains || 50;
    this._build();
  }

  _build() {
    // per electrode: DC block, mains notch, then a band-pass per band
    this.pre = ELECTRODES.map(() => [biquad("hp", 0.5, BW), biquad("notch", this.mains, 25)]);
    this.bp = ELECTRODES.map(() => BANDS.map((b) => {
      const [lo, hi] = this.bandsHz[b];
      return [biquad("hp", lo, BW), biquad("hp", lo, BW), biquad("lp", hi, BW), biquad("lp", hi, BW)];
    }));
    // envelope smoothing: about two cycles of the band's centre frequency
    this.envA = BANDS.map((b) => { const [lo, hi] = this.bandsHz[b]; const tau = Math.max(0.06, 2 / Math.sqrt(lo * hi)); return 1 - Math.exp(-1 / (tau * FS)); });
    this.chMs = BANDS.map(() => new Float64Array(4));
    this.val = {}; this.env = {};
    for (const s of SOURCES) for (const b of BANDS) {
      this.val[`${s}|${b}`] = new Float32Array(N);
      this.env[`${s}|${b}`] = new Float32Array(N);
    }
    this.clean = new Uint8Array(N).fill(1);
    // correlations, stored per sample
    this.corrBand = [0, 1, 2, 3].map(() => new Float32Array(N));   // envelope corr of band i with i+1
    this.corrLR = BANDS.map(() => new Float32Array(N));             // left vs right wave corr per band
    this.corrPair = BANDS.map(() => PAIRS.map(() => new Float32Array(N))); // electrode pairs per band
    this._cb = [0, 1, 2, 3].map(() => new EwCorr(2.0));
    this._clr = BANDS.map(() => new EwCorr(1.0));
    this._cp = BANDS.map(() => PAIRS.map(() => new EwCorr(1.0)));
    // spectra
    this.spec = new Float32Array(SPEC_N * SPEC_BINS);
    this.specN = 0;
    this.raw = ELECTRODES.map(() => new Float32Array(N));
    this.win = new Float32Array(256).map((_, i) => 0.5 - 0.5 * Math.cos((2 * Math.PI * i) / 256));
    this.runRms = BANDS.map(() => 0); // slow running amplitude, used until a reference exists
  }

  idx(i) { return ((i % N) + N) % N; }

  push(samples) {
    // samples: array of [TP9, AF7, AF8, TP10] in µV
    const nb = BANDS.length;
    const bandVal = new Float64Array(4 * nb);
    for (const smp of samples) {
      const i = this.idx(this.n);
      for (let c = 0; c < 4; c++) {
        let x = smp[c];
        if (!Number.isFinite(x)) x = 0;
        if (this.n === 0) { // start the DC blocker settled on the first value
          const f = this.pre[c][0]; f.x1 = f.x2 = x; f.y1 = f.y2 = 0;
        }
        x = run(this.pre[c][1], run(this.pre[c][0], x));
        this.raw[c][i] = x;
        for (let b = 0; b < nb; b++) {
          const q = this.bp[c][b];
          bandVal[c * nb + b] = run(q[3], run(q[2], run(q[1], run(q[0], x))));
        }
      }
      for (let b = 0; b < nb; b++) {
        const band = BANDS[b];
        // per-electrode mean square: the envelope of a source is the RMS of its electrodes,
        // so it matches the reference's per-electrode power; the wave itself is the average
        // signal, which is only as tall as the electrodes are in step with each other.
        const ms = this.chMs[b];
        for (let c = 0; c < 4; c++) { const v = bandVal[c * nb + b]; ms[c] += this.envA[b] * (v * v - ms[c]); }
        for (const s of SOURCES) {
          const w = SRC_W[s];
          const v = w[0] * bandVal[b] + w[1] * bandVal[nb + b] + w[2] * bandVal[2 * nb + b] + w[3] * bandVal[3 * nb + b];
          const key = `${s}|${band}`;
          this.val[key][i] = v;
          this.env[key][i] = Math.sqrt(2 * (w[0] * ms[0] + w[1] * ms[1] + w[2] * ms[2] + w[3] * ms[3]));
        }
        this.runRms[b] += Math.max(1 / (30 * FS), 1 / (this.n + 1)) * (this.env[`all|${band}`][i] - this.runRms[b]);
        this.corrLR[b][i] = this._clr[b].push(this.val[`L|${band}`][i], this.val[`R|${band}`][i]);
        for (let p = 0; p < PAIRS.length; p++) {
          const [a, c2] = PAIRS[p];
          this.corrPair[b][p][i] = this._cp[b][p].push(bandVal[a * nb + b], bandVal[c2 * nb + b]);
        }
      }
      for (let b = 0; b < nb - 1; b++) {
        this.corrBand[b][i] = this._cb[b].push(this.env[`all|${BANDS[b]}`][i], this.env[`all|${BANDS[b + 1]}`][i]);
      }
      this.clean[i] = this._cleanNow ? 1 : 0;
      this.n++;
      if (this.n % (FS / SPEC_HZ) === 0 && this.n >= 256) this._spectrum();
    }
  }

  setClean(clean) { this._cleanNow = !!clean; }

  // sensors in use (settings signal.sensors): whole-head strands average only those, and the
  // hemispheres use whichever of their sensors are in use
  setSensors(names) {
    const all = ["TP9", "AF7", "AF8", "TP10"];
    const use = (names && names.length ? names : all).map((n) => all.indexOf(n)).filter((i) => i >= 0);
    const w = (idx) => { const v = [0, 0, 0, 0]; const u = idx.filter((i) => use.includes(i)); const pick = u.length ? u : idx; pick.forEach((i) => (v[i] = 1 / pick.length)); return v; };
    SRC_W = { all: w([0, 1, 2, 3]), L: w([0, 1]), R: w([2, 3]), TP9: [1, 0, 0, 0], AF7: [0, 1, 0, 0], AF8: [0, 0, 1, 0], TP10: [0, 0, 0, 1] };
  }

  _spectrum() {
    const re = new Float64Array(256), im = new Float64Array(256), acc = new Float64Array(129);
    for (let c = 0; c < 4; c++) {
      for (let k = 0; k < 256; k++) { re[k] = this.raw[c][this.idx(this.n - 256 + k)] * this.win[k]; im[k] = 0; }
      fft(re, im);
      for (let k = 0; k < 129; k++) acc[k] += re[k] * re[k] + im[k] * im[k];
    }
    const row = this.specN % SPEC_N;
    for (let f = 1; f <= SPEC_BINS; f++) this.spec[row * SPEC_BINS + f - 1] = Math.log10(acc[f] / 4 + 1e-9);
    this.specN++;
  }

  // amplitude used to scale each band: the frozen reference if there is one
  refAmp(b, reference) {
    const band = BANDS[b];
    const lp = reference && reference.median && reference.median[`lp_${band}`];
    if (lp !== undefined) {
      const [lo, hi] = this.bandsHz[band];
      return Math.sqrt(Math.pow(10, lp) * (hi - lo));
    }
    return Math.max(0.5, this.runRms[b]);
  }
}
