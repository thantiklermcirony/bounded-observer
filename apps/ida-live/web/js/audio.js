// Sound for the levels: headphones or bone conduction (Shokz), all synthesized live, no files.
//
// Sound is an actuator of the same TAO world state that drives the picture (SSRN 6779487,
// Chamber contracts), so what you hear and what you see always say the same thing:
//   q clarity     the bed and the chord open from muffled to clear (low-pass), noise recedes
//   h rhythm      the breath pacer (6 per minute) and a felt low pulse on each inhale; stronger
//                 as your breathing locks to it and your signal steadies (h is a multiplicative gate)
//   n novelty     density of small sparkles and textures
//   p perturbation each knock has its own sound (a drop, a chill, a gust, rapids, thunder, a meteor)
//   F flow        the chord's voices drift apart (slow beating) out of the corridor and lock into
//                 a pure chord inside it: the sound literally tunes in as you do
//   l load        when you strain, the world thins out (TAO's density reduction for load)
// Entrainment (experimental, sealed per round): a soft pulsing tone at the level's target rhythm
// (10 Hz calm, 6 Hz flow, 18 Hz focus, 40 Hz open awareness) or, as its control, the same pulses
// at irregular intervals. Neither you nor the scene is told which; the reveal at the end is.
//
// Safety: one master limiter, a hard ceiling (audio.max_db), every change ramps (no clicks,
// no sudden loudness), thunder is a rumble, not a bang.

import { Score } from "./music.js";

const clamp = (x, a, b) => (x < a ? a : x > b ? b : x);
const dbToGain = (db) => Math.pow(10, db / 20);

const SCENES = {
  still: { root: 196.0, chord: [1, 1.5, 2.0, 2.5], bed: "water", bedDb: -26, padDb: -30, wave: "sine" },
  bloom: { root: 261.6, chord: [1, 1.25, 1.5, 2.0], bed: "air", bedDb: -34, padDb: -27, wave: "triangle" },
  steady: { root: 146.8, chord: [1, 1.5, 2.0, 3.0], bed: "wind", bedDb: -28, padDb: -32, wave: "sine" },
  ride: { root: 164.8, chord: [1, 1.5, 2.0, 2.5], bed: "surf", bedDb: -22, padDb: -31, wave: "triangle" },
  storm: { root: 110.0, chord: [1, 1.2, 1.5, 2.0], bed: "rain", bedDb: -21, padDb: -33, wave: "sine" },
  sky: { root: 220.0, chord: [1, 1.5, 2.25, 3.0], bed: "air", bedDb: -33, padDb: -28, wave: "sine" },
};
const SPARKLE = [1, 9 / 8, 5 / 4, 3 / 2, 5 / 3, 2, 9 / 4, 5 / 2, 3];

function noiseBuffer(ctx, kind, seconds = 4) {
  const n = Math.round(ctx.sampleRate * seconds), buf = ctx.createBuffer(1, n, ctx.sampleRate), d = buf.getChannelData(0);
  let b0 = 0, b1 = 0, b2 = 0, last = 0;
  for (let i = 0; i < n; i++) {
    const w = Math.random() * 2 - 1;
    if (kind === "white") d[i] = w * 0.5;
    else if (kind === "brown") { last = (last + 0.02 * w) / 1.02; d[i] = last * 3.5; }
    else { b0 = 0.99765 * b0 + w * 0.099; b1 = 0.963 * b1 + w * 0.2965; b2 = 0.57 * b2 + w * 1.0527; d[i] = (b0 + b1 + b2 + w * 0.1848) * 0.11; } // pink
  }
  return buf;
}

export class LevelSound {
  constructor(settings, levelId, condition, entrainHz, sceneId) {
    this.s = settings || {};
    this.id = levelId;                             // the score (a scene's own, or "canon")
    this.sc = SCENES[sceneId || levelId] || SCENES.still;   // the scene's sound bed
    this.carrying = false;
    this.condition = condition || "none";        // "entrain" | "control" | "none"
    this.entrainHz = entrainHz || 0;
    this.ok = false;
    this.nextSparkle = 0; this.nextPulse = 0;
    try { this.build(); } catch (e) { console.warn("sound off:", e); }
  }

  build() {
    const ctx = (this.ctx = sharedContext());
    if (!ctx) return;
    const now = ctx.currentTime;
    // master: volume -> limiter -> ceiling -> out
    this.master = ctx.createGain(); this.master.gain.value = 0;
    this.limiter = ctx.createDynamicsCompressor();
    // a true peak limiter only (the music's own dynamics, quiet waiting to full peaks, must survive)
    this.limiter.threshold.value = -6; this.limiter.knee.value = 3; this.limiter.ratio.value = 20;
    this.limiter.attack.value = 0.005; this.limiter.release.value = 0.25;
    this.ceiling = ctx.createGain(); this.ceiling.gain.value = dbToGain(this.s.max_db ?? -12);
    this.master.connect(this.limiter).connect(this.ceiling).connect(ctx.destination);
    if (this.s.device && ctx.setSinkId) ctx.setSinkId(this.s.device).catch(() => {});

    // clarity filter shared by the bed and the chord
    this.clarity = ctx.createBiquadFilter(); this.clarity.type = "lowpass"; this.clarity.frequency.value = 400; this.clarity.Q.value = 0.5;
    this.clarity.connect(this.master);

    // bed
    const kind = { water: "brown", rain: "white", surf: "pink", wind: "pink", air: "pink" }[this.sc.bed];
    this.bed = ctx.createBufferSource(); this.bed.buffer = noiseBuffer(ctx, kind, 6); this.bed.loop = true;
    this.bedShape = ctx.createBiquadFilter();
    if (this.sc.bed === "rain") { this.bedShape.type = "highpass"; this.bedShape.frequency.value = 900; }
    else if (this.sc.bed === "wind") { this.bedShape.type = "bandpass"; this.bedShape.frequency.value = 500; this.bedShape.Q.value = 1.2; }
    else if (this.sc.bed === "air") { this.bedShape.type = "bandpass"; this.bedShape.frequency.value = 2500; this.bedShape.Q.value = 0.4; }
    else { this.bedShape.type = "lowpass"; this.bedShape.frequency.value = 1400; }
    this.bedGain = ctx.createGain(); this.bedGain.gain.value = 0;
    this.bed.connect(this.bedShape).connect(this.bedGain).connect(this.clarity);
    // a slow swell on water and surf (the scene breathing), and a rumble under the storm
    if (this.sc.bed === "surf" || this.sc.bed === "water") {
      this.swell = ctx.createOscillator(); this.swell.frequency.value = this.sc.bed === "surf" ? 0.11 : 0.17;
      this.swellAmt = ctx.createGain(); this.swellAmt.gain.value = 0;
      this.swell.connect(this.swellAmt).connect(this.bedGain.gain); this.swell.start();
    }
    if (this.sc.bed === "rain") {
      this.rumble = ctx.createBufferSource(); this.rumble.buffer = noiseBuffer(ctx, "brown", 6); this.rumble.loop = true;
      const lp = ctx.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = 160;
      this.rumbleGain = ctx.createGain(); this.rumbleGain.gain.value = 0;
      this.rumble.connect(lp).connect(this.rumbleGain).connect(this.master); this.rumble.start();
    }
    this.bed.start();

    // the music: an adaptive orchestral score composed from the same world state (music.js)
    this.score = null;
    if (window.Tone && this.s.music !== false) {
      try {
        if (!window.Tone.getContext().rawContext || window.Tone.getContext().rawContext !== ctx) window.Tone.setContext(ctx);
        this.musicBus = ctx.createGain(); this.musicBus.gain.value = dbToGain(this.s.music_db ?? 8); this.musicBus.connect(this.master);
        this.score = new Score(this.id, this.musicBus, { pacerBpm: this.s.pacer_bpm || 6 });
        this.score.load().catch((e) => { console.warn("music unavailable:", e); this.score = null; });
      } catch (e) { console.warn("music unavailable:", e); this.score = null; }
    }

    // a low pulse on the inhale that bone conduction turns into a felt vibration
    this.thump = ctx.createOscillator(); this.thump.type = "sine"; this.thump.frequency.value = 58;
    this.thumpGain = ctx.createGain(); this.thumpGain.gain.value = 0;
    this.thump.connect(this.thumpGain).connect(this.master); this.thump.start();

    // entrainment carrier: regular pulses at the target rhythm ("entrain"), the same pulses at
    // irregular intervals ("control"), or silent ("none"); switched per round by setCondition
    if (this.entrainHz > 0) {
      this.carrier = ctx.createOscillator(); this.carrier.type = "sine";
      this.carrier.frequency.value = this.entrainHz >= 30 ? 440 : this.sc.root * 2;
      this.am = ctx.createGain(); this.am.gain.value = 0;
      this.entrainGain = ctx.createGain(); this.entrainGain.gain.value = 0;
      this.carrier.connect(this.am).connect(this.entrainGain).connect(this.master); this.carrier.start();
      this.lfo = ctx.createOscillator(); this.lfo.frequency.value = this.entrainHz;
      this.depth = ctx.createGain(); this.depth.gain.value = 0;
      this.lfo.connect(this.depth).connect(this.am.gain); this.lfo.start();
    }
    this.sparkBus = ctx.createGain(); this.sparkBus.gain.value = 1; this.sparkBus.connect(this.clarity);
    this.fxBus = ctx.createGain(); this.fxBus.gain.value = 1; this.fxBus.connect(this.master);
    this.ok = true;
    this.setVolume(this.s.volume ?? 0.5, 2.5, now);
  }

  // the carry: the music resolves and swells, and the pulse you feel through bone conduction
  // strengthens and slows, for as long as the level holds you up
  carry(on) {
    this.carrying = !!on;
    if (!this.ok) return;
    const T = this.ctx.currentTime;
    if (this.musicBus) this.musicBus.gain.setTargetAtTime(dbToGain((this.s.music_db ?? 8) + (on ? 2 : 0)), T, on ? 0.6 : 1.5);
    if (this.score && this.score.ready) this.score.carry(on);
  }

  setCondition(cond) {
    this.condition = cond || "none";
    if (!this.ok || !this.am) return;
    const T = this.ctx.currentTime;
    this.am.gain.cancelScheduledValues(T);
    if (this.condition === "entrain") { this.am.gain.setValueAtTime(0.5, T); this.depth.gain.setValueAtTime(0.5, T); }
    else { this.am.gain.setValueAtTime(0, T); this.depth.gain.setValueAtTime(0, T); }
    this.nextPulse = T;
  }

  get running() { return this.ctx && this.ctx.state === "running"; }
  resume() { if (this.ctx && this.ctx.state !== "running") this.ctx.resume().catch(() => {}); }

  setVolume(v, ramp = 0.5) {
    if (!this.ok) return;
    this.master.gain.setTargetAtTime(clamp(v, 0, 1), this.ctx.currentTime, ramp / 3);
  }

  // w: world state from the chamber (q, h, n, p, F, l, event); pacer: phase in radians, on/off
  update(w, pacerPhase, live, clock) {
    if (!this.ok || !this.running) return;
    if (this.score && this.score.ready) {
      if (!this.score.running) this.score.start(clock);
      this.score.update(w, pacerPhase);
    }
    const ctx = this.ctx, T = ctx.currentTime, sc = this.sc;
    const q = clamp(w.q ?? 0.2, 0, 1), F = clamp(w.F ?? 0, 0, 1), n = clamp(w.n ?? 0.3, 0, 1), h = clamp(w.h ?? 0.2, 0, 1);
    const l = clamp(w.l ?? 0, 0, 1), thin = 1 - 0.55 * l;              // load thins the world
    // clarity: low-pass from 350 Hz to 9 kHz on an exponential scale
    // the sound leads rather than mirrors: it never closes down below a warm, present floor
    this.clarity.frequency.setTargetAtTime(900 * Math.pow(9000 / 900, this.carrying ? Math.max(q, 0.7) : q), T, 0.25);
    this.bedGain.gain.setTargetAtTime(dbToGain(sc.bedDb - 4) * (1.25 - 0.55 * q) * thin, T, 0.4);
    if (this.swellAmt) this.swellAmt.gain.setTargetAtTime(dbToGain(sc.bedDb) * 0.45 * thin, T, 0.5);
    if (this.rumbleGain) this.rumbleGain.gain.setTargetAtTime(dbToGain(-24) * (1 - 0.7 * q), T, 0.6);
    const inhale = 0.5 - 0.5 * Math.cos(pacerPhase);                     // 0 at full exhale, 1 at full inhale
    const rising = Math.sin(pacerPhase) > 0;
    // the pulse: a low 58 Hz swell on each inhale (felt through bone conduction); in a carry it is
    // strong and certain, so there is something to lean on
    const pulse = this.carrying ? dbToGain(-19) : dbToGain(-27) * Math.max(0.35, h);
    this.thumpGain.gain.setTargetAtTime(live || this.pacerOn ? pulse * (rising ? inhale : 0) : 0, T, 0.15);
    // entrainment layer
    if (this.entrainGain) {
      this.entrainGain.gain.setTargetAtTime(live && this.condition !== "none" ? dbToGain(-33) * thin : 0, T, 0.5);
      if (this.condition === "control" && live && T >= this.nextPulse) {  // same mean rate, no steady rhythm
        const period = 1 / this.entrainHz, dur = period * 0.5;
        this.am.gain.cancelScheduledValues(T);
        this.am.gain.setValueAtTime(0, T); this.am.gain.linearRampToValueAtTime(1, T + dur * 0.3); this.am.gain.linearRampToValueAtTime(0, T + dur);
        this.nextPulse = T + period * (0.35 + 1.3 * Math.random());
      }
    }
    if (w.event) this.knock(String(w.event).split(" ")[0], parseFloat(String(w.event).split(" ")[1]) || 0.6);
  }

  sparkle(freq, gain) {
    const ctx = this.ctx, T = ctx.currentTime;
    const o = ctx.createOscillator(); o.type = "sine"; o.frequency.value = freq;
    const g = ctx.createGain(); g.gain.value = 0;
    g.gain.setValueAtTime(0, T); g.gain.linearRampToValueAtTime(gain, T + 0.01); g.gain.exponentialRampToValueAtTime(1e-4, T + 0.6);
    o.connect(g).connect(this.sparkBus); o.start(T); o.stop(T + 0.65);
  }

  noiseHit(kind, T, dur, filt, f0, f1, gain, q = 1) {
    const ctx = this.ctx;
    const src = ctx.createBufferSource(); src.buffer = this._nb ||= noiseBuffer(ctx, "pink", 3);
    const bq = ctx.createBiquadFilter(); bq.type = filt; bq.Q.value = q;
    bq.frequency.setValueAtTime(f0, T); bq.frequency.exponentialRampToValueAtTime(f1, T + dur);
    const g = ctx.createGain(); g.gain.setValueAtTime(0, T);
    g.gain.linearRampToValueAtTime(gain, T + Math.min(0.25, dur * 0.3)); g.gain.exponentialRampToValueAtTime(1e-4, T + dur);
    src.connect(bq).connect(g).connect(this.fxBus); src.start(T, Math.random() * 1.5); src.stop(T + dur + 0.05);
  }

  // each perturbation sounds like what the scene shows; loudness scales with the knock, capped
  knock(kind, mag) {
    if (!this.ok) return;
    const T = this.ctx.currentTime, G = dbToGain(-24) * clamp(0.5 + 0.6 * mag, 0.3, 1);
    if (kind === "drop") {
      const o = this.ctx.createOscillator(); o.type = "sine";
      o.frequency.setValueAtTime(1400, T); o.frequency.exponentialRampToValueAtTime(520, T + 0.12);
      const g = this.ctx.createGain(); g.gain.setValueAtTime(0, T); g.gain.linearRampToValueAtTime(G, T + 0.005); g.gain.exponentialRampToValueAtTime(1e-4, T + 0.5);
      o.connect(g).connect(this.fxBus); o.start(T); o.stop(T + 0.55);
      this.noiseHit("drop", T + 0.05, 1.6, "bandpass", 900, 300, G * 0.35, 3);
    } else if (kind === "chill") this.noiseHit(kind, T, 2.4, "bandpass", 4000, 1600, G * 0.7, 2);
    else if (kind === "gust") this.noiseHit(kind, T, 2.2, "bandpass", 300, 1400, G, 1.5);
    else if (kind === "rapids") this.noiseHit(kind, T, 1.8, "lowpass", 3000, 600, G, 0.7);
    else if (kind === "thunder") {
      this.noiseHit(kind, T, 0.35, "highpass", 2500, 1200, G * 0.5, 0.7);            // the crack, soft
      this.noiseHit(kind, T + 0.12, 3.8, "lowpass", 220, 70, G * 1.1, 0.7);          // the roll
    } else if (kind === "meteor") this.noiseHit(kind, T, 1.3, "bandpass", 5000, 700, G * 0.6, 6);
  }

  // a check for the headphones: a short chord, left then right
  static async test(settings) {
    const AC = window.AudioContext || window.webkitAudioContext;
    const ctx = new AC();
    if (settings && settings.device && ctx.setSinkId) await ctx.setSinkId(settings.device).catch(() => {});
    const out = ctx.createGain(); out.gain.value = dbToGain(settings?.max_db ?? -12) * (settings?.volume ?? 0.5);
    out.connect(ctx.destination);
    const T = ctx.currentTime + 0.05;
    [[-1, 0], [1, 0.9]].forEach(([pan, at]) => {
      const p = ctx.createStereoPanner(); p.pan.value = pan; p.connect(out);
      [261.6, 329.6, 392].forEach((f) => {
        const o = ctx.createOscillator(); o.frequency.value = f; const g = ctx.createGain();
        g.gain.setValueAtTime(0, T + at); g.gain.linearRampToValueAtTime(0.15, T + at + 0.05); g.gain.exponentialRampToValueAtTime(1e-4, T + at + 0.8);
        o.connect(g).connect(p); o.start(T + at); o.stop(T + at + 0.85);
      });
    });
    setTimeout(() => ctx.close(), 2500);
  }

  close() {
    if (!this.ok) return;
    const T = this.ctx.currentTime;
    try { this.master.gain.setTargetAtTime(0, T, 0.2); } catch (e) { /* ignore */ }
    if (this.score) this.score.stop();
    const nodes = [this.bed, this.swell, this.rumble, this.thump, this.carrier, this.lfo];
    setTimeout(() => { nodes.forEach((n) => { try { n && n.stop(); } catch (e) { /* ignore */ } }); try { this.master.disconnect(); } catch (e) { /* ignore */ } }, 1200);
    this.ok = false;
  }
}

// one audio context for the whole app, unlocked by the first click (browsers require a gesture)
let _ctx = null;
export function sharedContext() {
  const AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) return null;
  if (!_ctx || _ctx.state === "closed") _ctx = new AC({ latencyHint: "playback" });
  return _ctx;
}
export function unlockAudio() { const c = sharedContext(); if (c && c.state !== "running") c.resume().catch(() => {}); return c; }

// output devices the browser can see (labels appear only after the browser has permission)
export async function outputDevices() {
  try {
    const all = await navigator.mediaDevices.enumerateDevices();
    return all.filter((d) => d.kind === "audiooutput").map((d, i) => ({ id: d.deviceId, label: d.label || (d.deviceId === "default" ? "System default" : `Output ${i + 1}`) }));
  } catch (e) { return []; }
}
