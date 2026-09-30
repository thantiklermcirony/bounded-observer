// Adaptive score for the levels: real orchestral samples (VSCO 2 CE, CC0) played by Tone.js,
// composed live from the TAO world state. The rules (docs/EXPERIENCE.md):
//
//   * The music is unfinished until your brain finishes it. Off target the harmony hangs on
//     suspended and dominant chords and the melody rests; in the corridor it may cadence home
//     on the next strong beat. That landing is the reward (Salimpoor 2011; Huron 2006).
//   * One instrument enters per tier, on a bar line (TAO's blended mode switch). A tier-up is a
//     peak: a swell in the bar before, then a full cadence, a cymbal and the theme on the
//     downbeat (Sloboda 1991: new voice, crescendo and unexpected harmony give chills).
//   * A knock displaces the harmony; every bar you spend in the corridor walks it one step home,
//     and the theme returns when you do (the IDA return, heard).
//   * The phrase breathes with the pacer: bars are sized so a breath is a whole number of bars;
//     arpeggios rise on the inhale and fall on the exhale; the strings swell on the inhale.
//   * Clarity q opens the sound from a far hall to near; strain l narrows and quietens it.

const Tn = () => window.Tone;
const clamp = (x, a, b) => (x < a ? a : x > b ? b : x);

const SCALES = {
  major: [0, 2, 4, 5, 7, 9, 11], lydian: [0, 2, 4, 6, 7, 9, 11], mixolydian: [0, 2, 4, 5, 7, 9, 10],
  minor: [0, 2, 3, 5, 7, 8, 10], dorian: [0, 2, 3, 5, 7, 9, 10],
};

// Each scene: key, mode, bars per breath, progression (scale degrees; {abs, q} for borrowed
// chords), the theme (degree, beats; 16 beats = 4 bars), layers in order of entrance by tier.
export const SCORES = {
  still: { tonic: 62, mode: "major", barsPerBreath: 2, prog: [1, 4, 6, 5], feel: "serene",
    theme: [[3, 3], [2, 1], [1, 2], [5, 2], [6, 3], [5, 1], [3, 4]],
    layers: [["pad", ["violas", "celli"]], ["arp", "harp"], ["bass", "bass"], ["melody", "piano"], ["counter", "violins"], ["shimmer", "glock"], ["theme2", "flute"], ["swell", "fx"], ["full", "violin"]] },
  bloom: { tonic: 65, mode: "major", barsPerBreath: 3, prog: [1, 3, 4, 5], feel: "warm, rising",
    theme: [[5, 2], [6, 1], [8, 3], [7, 1], [6, 1], [5, 4], [3, 2], [4, 2]],
    layers: [["arp", "piano"], ["pad", ["violins", "violas"]], ["bass", "celli"], ["melody", "violin"], ["shimmer", "glock"], ["counter", "flute"], ["arp2", "harp"], ["swell", "fx"], ["full", "violins"]] },
  steady: { tonic: 57, mode: "minor", barsPerBreath: 3, prog: [1, 6, 3, 7], picardy: true, feel: "suspense, then triumph",
    theme: [[1, 2], [2, 1], [3, 1], [5, 4], [4, 2], [3, 2], [2, 4]],
    layers: [["ostinato", "piano"], ["bass", "bass"], ["pad", ["celli", "violas"]], ["pulse", "fx"], ["melody", "flute"], ["counter", "violins"], ["arp", "harp"], ["swell", "fx"], ["full", "violin"]] },
  ride: { tonic: 64, mode: "mixolydian", barsPerBreath: 4, prog: [1, 7, 4, 1], feel: "exhilaration",
    theme: [[5, 1], [5, 1], [6, 1], [8, 3], [7, 2], [5, 2], [4, 2], [5, 4]],
    layers: [["arp", "harp"], ["bass", "bass"], ["pad", ["violas", "celli"]], ["pulse", "fx"], ["melody", "violins"], ["ostinato", "piano"], ["shimmer", "glock"], ["swell", "fx"], ["full", "flute"]] },
  storm: { tonic: 62, mode: "minor", barsPerBreath: 3, prog: [1, 6, 4, { deg: 5, maj: true }], picardy: true, feel: "courage",
    theme: [[1, 3], [5, 1], [4, 2], [3, 2], [2, 3], [3, 1], [1, 4]],
    layers: [["ostinato", "celli"], ["bass", "bass"], ["pulse", "fx"], ["pad", ["violas", "violins"]], ["melody", "violin"], ["counter", "flute"], ["arp", "harp"], ["swell", "fx"], ["full", "piano"]] },
  // a classical ground: Pachelbel's canon (c. 1680, public domain). The ground bass never stops;
  // voices enter as you climb, each playing the same line two bars after the last, and a carry
  // brings the next voices in early. Classical music that evolves in real time, the way a canon
  // always did: by layering.
  canon: { tonic: 62, mode: "major", barsPerBreath: 2, prog: [1, 5, 6, 3, 4, 1, 4, 5], ground: true, feel: "a ground that grows with you",
    theme: [[3, 4], [2, 4], [1, 4], [0, 4], [-1, 4], [-2, 4], [-1, 4], [0, 4]],
    layers: [["bass", "celli"], ["pad", ["violas"]], ["arp", "harp"], ["melody", "violins"], ["counter", "violin"], ["ostinato", "piano"], ["theme2", "flute"], ["shimmer", "glock"], ["full", "violins"]] },
  sky: { tonic: 60, mode: "lydian", barsPerBreath: 2, prog: [1, 2, 1, 6], feel: "awe",
    theme: [[5, 4], [9, 4], [8, 2], [7, 2], [5, 4]],
    layers: [["pad", ["violins", "violas"]], ["arp", "harp"], ["shimmer", "glock"], ["bass", "celli"], ["melody", "flute"], ["counter", "violin"], ["bowed", "fx"], ["swell", "fx"], ["full", "piano"]] },
};

// displaced harmony after a knock, and the road home (one step per bar in the corridor)
const DISPLACE = [{ abs: 8, q: "maj" }, 4, 5];

const RANGES = { pad: [48, 76], bass: [31, 45], arp: [55, 86], melody: [64, 88], counter: [72, 91], shimmer: [84, 100], ostinato: [57, 76] };

let manifestP = null;
function sampleManifest() { return (manifestP ||= fetch("samples/manifest.json").then((r) => r.json())); }

export class Score {
  constructor(sceneId, out, opts = {}) {
    this.id = sceneId in SCORES ? sceneId : "still";
    this.S = SCORES[this.id];
    this.out = out;                    // a native AudioNode to feed (the level's master chain)
    this.pacerBpm = opts.pacerBpm || 6;
    this.ready = false; this.running = false;
    this.state = { q: 0.2, F: 0, Fs: 0, h: 0.2, n: 0.3, p: 0, l: 0, a: 0.5, tier: 1, TF: 0, pacer: 0 };
    this.tension = 0.8; this.tier = 1; this.bar = -1; this.beat = -1;
    this.displaced = 0; this.arrival = false; this.themeAt = -1; this.themeIdx = 0; this.riser = false;
    this.events = [];                  // what the music did, for the log (peak moments are testable)
    this.chord = null;
  }

  async load() {
    const Tone = Tn();
    if (!Tone) throw new Error("Tone.js not loaded");
    const man = await sampleManifest();
    const need = new Set();
    for (const [, inst] of this.S.layers) (Array.isArray(inst) ? inst : [inst]).forEach((x) => need.add(x));
    need.add("violin"); need.add("glock");
    this.inst = {};
    for (const name of need) {
      if (name === "fx" || !man[name]) continue;
      const s = new Tone.Sampler({ urls: man[name], baseUrl: "", release: name === "piano" || name === "harp" || name === "glock" ? 1.2 : 2.2 });
      this.inst[name] = s;
    }
    this.fx = {};
    for (const [k, url] of Object.entries(man.fx || {})) this.fx[k] = new Tone.Player({ url, fadeOut: 0.3 });
    // the room: clarity filter -> reverb -> music gain -> out
    this.filter = new Tone.Filter({ type: "lowpass", frequency: 600, rolloff: -12, Q: 0.3 });
    this.reverb = new Tone.Reverb({ decay: this.id === "sky" ? 9 : this.id === "storm" ? 5 : 6.5, preDelay: 0.03, wet: 0.6 });
    this.gain = new Tone.Gain(0);
    this.filter.chain(this.reverb, this.gain);
    Tone.connect(this.gain, this.out);
    this.layerGain = {};
    this.S.layers.forEach((_, i) => { this.layerGain[i] = new Tone.Gain(i < 2 ? 1 : 0).connect(this.filter); });
    // every instrument gets its own gain per layer that uses it
    this.voices = this.S.layers.map(([k, inst], i) => (Array.isArray(inst) ? inst : [inst]).map((nm) => {
      if (nm === "fx") return null;
      const src = this.inst[nm];
      if (!src) return null;
      const g = new Tone.Gain(1).connect(this.layerGain[i]);
      return { nm, src, g };
    }).filter(Boolean));
    // one sampler can only have one output route, so layers share instruments through clones
    const used = {};
    this.voices.forEach((vs) => vs.forEach((v) => {
      if (!used[v.nm]) { used[v.nm] = true; v.src.connect(v.g); }
      else { const c = new Tone.Sampler({ urls: man[v.nm], baseUrl: "", release: v.src.release }); c.connect(v.g); v.src = c; }
    }));
    const fxOut = new Tone.Gain(0.8).connect(this.reverb);
    for (const p of Object.values(this.fx)) p.connect(fxOut);
    await Tone.loaded();
    this.ready = true;
  }

  get bpm() { return this.pacerBpm * 4 * this.S.barsPerBreath; }
  get barDur() { return (60 / this.bpm) * 4; }

  // start on the next inhale, so bars line up with the breath (clock = shared session clock)
  start(clock) {
    if (!this.ready || this.running) return;
    const Tone = Tn(), tr = Tone.getTransport();
    tr.cancel(); tr.stop(); tr.position = 0;
    tr.bpm.value = this.bpm; tr.timeSignature = 4;
    const f = this.pacerBpm / 60;
    const wait = Number.isFinite(clock) ? ((Math.ceil(clock * f) / f) - clock) : 0.1;
    this.beatId = tr.scheduleRepeat((time) => this.onBeat(time), "4n", 0);
    tr.start(Tone.now() + clamp(wait, 0.05, 12));
    this.gain.gain.rampTo(1, 3);
    this.running = true;
  }

  stop() {
    const Tone = Tn(); if (!Tone) return;
    try { this.gain.gain.rampTo(0, 1.2); } catch (e) { /* ignore */ }
    setTimeout(() => { try { const tr = Tone.getTransport(); tr.stop(); tr.cancel(); } catch (e) { /* ignore */ } this.dispose(); }, 1500);
    this.running = false;
  }

  dispose() {
    for (const o of [...Object.values(this.inst || {}), ...Object.values(this.fx || {}), this.filter, this.reverb, this.gain, ...Object.values(this.layerGain || {})]) { try { o && o.dispose(); } catch (e) { /* ignore */ } }
    (this.voices || []).forEach((vs) => vs.forEach((v) => { try { v.g.dispose(); v.src.dispose(); } catch (e) { /* ignore */ } }));
  }

  // --------------------------------------------------------------- the world state, each frame
  update(w, pacerPhase) {
    const s = this.state;
    Object.assign(s, { q: w.q ?? s.q, F: w.F ?? s.F, h: w.h ?? s.h, n: w.n ?? s.n, p: w.p ?? s.p, l: w.l ?? s.l, a: w.a ?? s.a, TF: w.TF ?? s.TF, pacer: pacerPhase || 0 });
    s.Fs += 0.04 * ((w.Fe ?? w.F ?? 0) - s.Fs);
    if (!this.ready) return;
    const Tone = Tn();
    // clarity and strain: immediate, continuous feedback
    const cut = 700 * Math.pow(14000 / 700, clamp(s.q, 0, 1)) * (1 - 0.55 * clamp(s.l, 0, 1));
    this.filter.frequency.rampTo(Math.max(this.carrying ? 6000 : 1200, cut), 0.25);
    this.reverb.wet.rampTo(clamp(0.75 - 0.45 * s.q, 0.2, 0.8), 0.5);
    // dynamics: waiting music is softer, in the corridor it opens up, strain pulls it back
    // the music leads rather than mirrors: it stays present when you slip, and surges in a carry
    const dyn = this.carrying ? 1.12 : 0.72 + 0.28 * clamp(s.Fs * 1.2, 0, 1);
    this.gain.gain.rampTo(this.running ? clamp(dyn * (1 - 0.3 * s.l), 0.5, 1.25) : 0, this.carrying ? 2 : 0.6);
    // the strings breathe with the pacer, as strong as the rhythm variable h
    const inhale = 0.5 - 0.5 * Math.cos(s.pacer);
    const padIdx = this.S.layers.findIndex(([k]) => k === "pad");
    if (padIdx >= 0 && this.nLayers > padIdx) this.layerGain[padIdx].gain.rampTo(0.75 + 0.35 * s.h * inhale, 0.3);
    // tiers: one layer per tier, entering on the next bar; a climb is a peak moment
    if (w.tier && w.tier !== this.tier) { const up = w.tier > this.tier; this.tier = w.tier; this.pendingTier = up ? "up" : "down"; }
    // anticipation: a cymbal swell once the next tier is close (occupancy near the ascent line)
    const near = (s.TF || 0) / 0.7;
    if (near > 0.85 && !this.riser && this.tier < this.S.layers.length && this.fx.susCymb1_cresc_Short_v1) {
      this.riser = true; this.play("susCymb1_cresc_Short_v1", Tone.now(), -8); this.log("anticipation");
    }
    if (near < 0.6) this.riser = false;
    // a knock: the harmony is displaced and the music ducks; the way home starts now
    if (w.event) this.knock(String(w.event).split(" ")[0], parseFloat(String(w.event).split(" ")[1]) || 0.6);
  }

  // a carry: the harmony comes home, two more voices enter on the next bar, a swell rises
  carry(on) {
    if (on === this.carrying) return;
    this.carrying = on;
    const Tone = Tn(), t = Tone.now();
    if (on) {
      this.play("susCymb1_cresc_Short_v1", t, -10);
      this.displaced = 0; this.arrival = true;
      this.log("carry");
    } else this.log("carry_end");
  }

  knock(kind, mag) {
    const Tone = Tn(), t = Tone.now();
    this.displaced = DISPLACE.length; this.homeStep = 0;
    this.gain.gain.cancelScheduledValues(t);
    this.gain.gain.setValueAtTime(this.gain.gain.value, t);
    this.gain.gain.linearRampTo(0.55, 0.08, t);
    this.gain.gain.linearRampTo(1, 3.5, t + 0.4);
    if (kind === "thunder" || kind === "rapids" || kind === "gust") { this.play("Timpani2_Roll_v3_rr1_Sum", t, -6 + 6 * mag); this.play("bassdrum_rub1_v1", t, -8); }
    else if (kind === "meteor") this.play("BellTree_Stroke1_v1_Sum", t, -6);
    else this.play("Timpani4_Hit_v3_rr1_Sum", t, -10 + 6 * mag);
    this.log("knock", { kind });
  }

  play(name, time, db = 0) {
    const p = this.fx[name];
    if (!p || !p.loaded) return;
    try { p.volume.value = db; p.start(time); } catch (e) { /* already playing */ }
  }

  log(kind, extra = {}) { this.events.push({ kind, at: Tn().now(), bar: this.bar, tier: this.tier, ...extra }); if (this.events.length > 200) this.events.shift(); }

  // --------------------------------------------------------------- composition, beat by beat
  onBeat(time) {
    const Tone = Tn();
    this.beat = (this.beat + 1) % 4;
    const s = this.state;
    // tension: distance from the corridor, plus strain (smoothed per beat)
    const target = this.carrying ? 0.05 : clamp(0.9 * (1 - s.Fs) + 0.5 * s.l, 0, 1);
    this.tension += 0.35 * (target - this.tension);
    const bd = this.barDur, qd = bd / 4;
    if (this.beat === 0) {
      this.bar += 1;
      if (this.pendingTier) {
        if (this.pendingTier === "up") { this.arrival = true; this.peak(time); }
        this.pendingTier = null;
      }
      this.fadeLayers(time);
      this.chord = this.chooseChord();
      this.voiceBar(time, this.chord, bd, true);
    } else if (this.beat === 2 && this.tension < 0.35 && this.chord && this.chord.waiting) {
      // earned early: the moment you are in, the waiting chord resolves on the next strong beat
      this.chord = this.home(true);
      this.voiceBar(time, this.chord, bd / 2, true);
      this.log("resolve");
    }
    this.pattern(time, qd);
  }

  // which chord this bar: the progression, held back by tension, displaced by knocks
  chooseChord() {
    const S = this.S, T = this.tension;
    if (this.displaced > 0) {
      const c = DISPLACE[DISPLACE.length - this.displaced];
      if (this.state.Fs > 0.45) {
        this.displaced -= 1;
        if (this.displaced === 0) { this.arrival = true; this.returning = true; this.log("return"); }
      }
      return this.make(c, { waiting: true });
    }
    const pos = ((this.bar % S.prog.length) + S.prog.length) % S.prog.length;
    const deg = S.prog[pos];
    if (S.ground) { this.arrival = false; return this.make(deg, { full: this.carrying || T < 0.2 }); }  // a ground never stops
    if (this.arrival) { this.arrival = false; return this.home(true); }
    if (T < 0.35) return this.make(deg, { add9: pos === 0, full: false });
    if (T < 0.65) return this.make(pos === 0 ? 4 : deg, { sus: true, waiting: true });            // the tonic is withheld
    return this.make(5, { sus: true, pedal: true, waiting: true });                                  // hovering on the dominant
  }

  home(full) { const pic = this.S.picardy && this.tier >= 6; return this.make(1, { add9: !pic, full, picardy: pic }); }

  // build a chord: pitch classes over the scene's key and mode
  make(c, o = {}) {
    const S = this.S, sc = SCALES[S.mode];
    const p = (i) => S.tonic + sc[((i % 7) + 7) % 7] + 12 * Math.floor(i / 7);
    let tones;
    if (typeof c === "object" && c.abs !== undefined) {
      const r = S.tonic + c.abs;
      tones = c.q === "maj" ? [r, r + 4, r + 7] : [r, r + 3, r + 7];
    } else {
      const d = (typeof c === "object" ? c.deg : c) - 1;
      tones = o.sus ? [p(d), p(d + 3), p(d + 4)] : [p(d), p(d + 2), p(d + 4)];
      if (typeof c === "object" && c.maj) tones[1] = tones[0] + 4;
      if (o.picardy && d === 0) tones[1] = tones[0] + 4;
      if (o.add9) tones.push(p(d + 8));
      if (o.sus && !o.pedal) tones.push(p(d + 1));
    }
    return { tones, root: tones[0], waiting: !!o.waiting, full: !!o.full, pedal: !!o.pedal };
  }

  // notes of a chord inside a range, spread upwards
  voice(tones, lo, hi, n) {
    const pcs = [...new Set(tones.map((t) => ((t % 12) + 12) % 12))];
    const all = [];
    for (let m = lo; m <= hi; m++) if (pcs.includes(m % 12)) all.push(m);
    if (all.length <= n) return all;
    const out = [];
    for (let i = 0; i < n; i++) out.push(all[Math.round((i * (all.length - 1)) / Math.max(1, n - 1))]);
    return [...new Set(out)];
  }

  get nLayers() { return Math.min(this.S.layers.length, this.tier + 1 + (this.carrying ? 2 : 0)); }   // two at tier 1, one more per tier; a carry brings two in early
  active(k) { const i = this.S.layers.findIndex(([kk]) => kk === k); return i >= 0 && i < this.nLayers ? i : -1; }

  fadeLayers(time) {
    this.S.layers.forEach((_, i) => {
      const on = i < this.nLayers;
      const g = this.layerGain[i].gain;
      g.cancelScheduledValues(time);
      g.linearRampToValueAtTime(on ? (this.S.layers[i][0] === "pad" ? 0.85 : 1) : 0, time + (on ? this.barDur * 0.8 : 1.5));
    });
  }

  // a tier-up: cymbal, a low hit and the theme on the downbeat
  peak(time) {
    this.play("cymbal_crash1_mp_rr1", time, -10);
    this.play("Timpani1_Hit_v3_rr1_Sum", time, -9);
    if (this.tier >= 5) this.play("Triangle3_Hit_v1_rr1_Sum", time + 0.02, -12);
    this.themeAt = this.bar; this.themeIdx = 0; this.themeBeat = 0; this.appoggiatura = true;
    this.log("peak", { tier: this.tier });
  }

  play1(layer, notes, dur, time, vel) {
    const i = this.S.layers.findIndex(([k]) => k === layer);
    if (i < 0 || i >= this.nLayers) return;
    for (const v of this.voices[i]) {
      try { v.src.triggerAttackRelease(notes.map((m) => Tn().Frequency(m, "midi").toNote()), dur, time, clamp(vel, 0.05, 1)); } catch (e) { /* not loaded yet */ }
    }
  }

  voiceBar(time, ch, dur, change) {
    const s = this.state, lush = ch.full ? 1.2 : 1;
    if (change) {
      this.play1("pad", this.voice(ch.tones, ...RANGES.pad, 5), dur * 1.15, time, (0.5 + 0.35 * s.q) * lush);
      const bass = ch.pedal ? this.make(5).root : ch.root;
      this.play1("bass", [RANGES.bass[0] + ((bass - RANGES.bass[0]) % 12 + 12) % 12], dur * 1.05, time, 0.45 + 0.2 * s.q);
      const top = this.voice(ch.tones, ...RANGES.counter, 3);
      this.play1("counter", [top[Math.min(top.length - 1, this.bar % 2)]], dur * 1.05, time, 0.25 + 0.3 * s.q);
      if (ch.full) this.play1("full", this.voice(ch.tones, 60, 84, 4), dur, time, 0.45);
    }
  }

  // the beat's figures: arpeggios with the breath, ostinato, shimmer, pulse and the theme
  pattern(time, qd) {
    const s = this.state, ch = this.chord;
    if (!ch) return;
    const Tone = Tn();
    const inhale = Math.sin(s.pacer) >= 0;             // rising half of the breath
    const arpNotes = this.voice(ch.tones, ...RANGES.arp, 8);
    const seq = inhale ? arpNotes : [...arpNotes].reverse();
    const subdiv = this.id === "ride" ? 4 : 2;
    for (let k = 0; k < subdiv; k++) {
      const idx = ((this.beat * subdiv + k) % seq.length);
      const t = time + (k * qd) / subdiv;
      const skip = Math.random() > 0.55 + 0.45 * s.h;  // the figure fills in as breath locks
      if (!skip) {
        this.play1("arp", [seq[idx]], qd * 1.5, t, 0.35 + 0.3 * s.q);
        this.play1("arp2", [seq[(idx + 3) % seq.length] + 12], qd, t, 0.15 + 0.2 * s.q);
      }
    }
    if (this.active("ostinato") >= 0) {
      const o = this.voice(ch.tones, ...RANGES.ostinato, 3);
      for (let k = 0; k < 2; k++) this.play1("ostinato", [o[(this.beat + k) % o.length]], qd * 0.45, time + (k * qd) / 2, 0.2 + 0.25 * (1 - this.tension));
    }
    if (this.active("shimmer") >= 0 && Math.random() < 0.15 + 0.6 * s.n * (1 - 0.6 * s.l)) {
      const sh = this.voice(ch.tones, ...RANGES.shimmer, 5);
      this.play1("shimmer", [sh[Math.floor(Math.random() * sh.length)]], qd * 2, time + qd * Math.random() * 0.5, 0.2 + 0.2 * s.n);
    }
    if (this.active("pulse") >= 0 && this.beat === 0) this.play(this.id === "ride" ? "bassdrum_rub1_v1" : "Timpani5_Hit_v3_rr1_Sum", time, -18 + 6 * (1 - this.tension));
    if (this.active("bowed") >= 0 && this.beat === 0 && this.bar % 4 === 0 && this.tension < 0.5) this.play("susCymb1_bow_1", time, -14);
    if (this.active("swell") >= 0 && this.beat === 0 && this.bar % 8 === 7 && this.tension < 0.4) this.play("susCymb1_cresc_Median_v1", time, -16);
    // the canon: the line in the melody, the same line two bars later in the counter voice, and
    // four bars later in the flute, each once its layer is in (earned or carried)
    if (this.S.ground) {
      if (this.beat === 0) {
        const th = this.S.theme, L = th.length, pos = ((this.bar % L) + L) % L, sc = SCALES[this.S.mode];
        const note = (i) => { const d = th[((i % L) + L) % L][0] - 1; return this.S.tonic + 12 + sc[((d % 7) + 7) % 7] + 12 * Math.floor(d / 7); };
        const vel = 0.4 + 0.3 * s.q + (this.carrying ? 0.15 : 0);
        this.play1("melody", [note(pos)], this.barDur * 0.98, time, vel);
        if (this.bar >= 2) this.play1("counter", [note(pos - 2) + 12], this.barDur * 0.98, time, vel * 0.8);
        if (this.bar >= 4) this.play1("theme2", [note(pos - 4) + 12], this.barDur * 0.98, time, vel * 0.7);
      }
      return;
    }
    // the theme: only when earned (in the corridor), or on a peak or a return
    const earned = this.tension < 0.4 || this.themeAt === this.bar || this.returning;
    const lay = this.active("melody") >= 0 ? "melody" : null;
    if (lay && earned) this.theme(time, qd, lay);
    else if (this.returning) this.theme(time, qd, "full");
  }

  theme(time, qd, lay) {
    const S = this.S, th = S.theme, sc = SCALES[S.mode];
    if (this.themeIdx >= th.length) { this.themeIdx = 0; this.themeBeat = 0; this.returning = false; if (this.bar % 4 !== 0) return; }
    this.themeBeat = (this.themeBeat || 0);
    if (this.themeBeat > 0) { this.themeBeat -= 1; return; }
    const [deg, beats] = th[this.themeIdx];
    const d = deg - 1;
    let m = S.tonic + 12 + sc[((d % 7) + 7) % 7] + 12 * Math.floor(d / 7);
    const vel = 0.35 + 0.35 * this.state.q;
    if (this.appoggiatura && this.themeIdx === 0) {    // a leaning note that resolves: the chill point
      this.play1(lay, [m + 1], qd * 0.5, time, vel);
      this.play1(lay, [m], qd * (beats - 0.5), time + qd * 0.5, vel * 1.1);
      this.appoggiatura = false;
    } else this.play1(lay, [m], qd * beats * 0.98, time, vel);
    if (this.active("theme2") >= 0 && this.tension < 0.3) this.play1("theme2", [m + 12], qd * beats * 0.9, time, vel * 0.7);
    this.themeBeat = beats - 1; this.themeIdx += 1;
  }
}

// a guided demo of a scene's music, without a headband: tension, arrival, climbs, a knock and
// the way home, so you can hear what each state sounds like
export function demoTrack(t, prev = t - 0.05) {
  const F = t < 12 ? 0.1 : t < 20 ? 0.45 : t < 58 ? 0.9 : t < 63 ? 0.15 : t < 75 ? 0.75 : 0.95;
  const tier = t < 26 ? 1 : t < 34 ? 2 : t < 42 ? 3 : t < 50 ? 4 : t < 80 ? 5 : t < 88 ? 6 : 7;
  const q = Math.min(0.95, 0.15 + t / 60);
  return { F, Fe: F, q, h: Math.min(0.9, t / 70), n: 0.3 + 0.3 * Math.sin(t / 9), l: t > 58 && t < 62 ? 0.7 : 0.05, tier, TF: F, p: 0,
    event: prev < 58 && t >= 58 ? "knock 0.8" : "" };
}
