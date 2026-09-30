// Levels: real footage driven by your EEG in real time. A settle phase measures your own
// baseline in that scene, then (v0.9 default) one continuous journey. At each fall a sealed coin
// decides whether the scene, music and pulse carry you back up or simply follow you, so the carry
// is tested fall by fall. The older design (rounds, one a secret replay, each rated) is still
// there: Control > Knobs > levels.replay = one.
//
// Each scene invites the state it measures and answers in the same language:
//   Still Water  calm (relative alpha)          the wind drops, the mist lifts
//   Bloom        warmth (frontal asymmetry)     the flower opens and glows
//   Tightrope    focus (engagement, steady)     the rope stops swaying, the walker crosses
//   Ride         flow (frontal theta in a band) the wave carries you; too hard breaks it up
//   Storm        recovery (return to baseline)  the sea slows as you come back after each hit
//   Night Sky    open awareness (complexity)    the sky widens and fills with stars

import { FS } from "./dsp.js";
import { Chamber } from "./chamber.js";
import { Compositor } from "./render.js";
import { LevelSound } from "./audio.js";

const $ = (id) => document.getElementById(id);
const clamp = (x, a, b) => (x < a ? a : x > b ? b : x);
const sig = (r) => 1 / (1 + Math.exp(-r));
const esc = (t) => String(t ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const mean = (xs) => xs.reduce((a, b) => a + b, 0) / Math.max(1, xs.length);
const sd = (xs) => { const m = mean(xs); return Math.sqrt(mean(xs.map((x) => (x - m) ** 2))); };

const RATING = ["Not at all", "A little", "Somewhat", "A lot", "Completely"];
const MODES = { bloom: 0, steady: 1, water: 2, ride: 3, storm: 4, sky: 5 };
const WHY = { contact: "a sensor lost contact", movement: "head movement: rest your head and stay still",
  muscle: "muscle: soften your jaw, face and brow", eyes: "eyes moving: let your gaze rest on the scene", "no signal": "no signal" };
const SENSOR_NAME = ["left ear", "left forehead", "right forehead", "right ear"];
const FOREHEAD_ONLY = new Set(["frontal_asymmetry", "frontal_theta"]);
// say which sensor and why, in plain words (the per-sensor verdicts come with every tick)
export function explain(reason, quality) {
  if (reason === "contact" && Array.isArray(quality)) {
    const loose = quality.map((q, i) => (q === "loose" ? SENSOR_NAME[i] : null)).filter(Boolean);
    const off = quality.map((q, i) => (["noise", "poor", "flat"].includes(q) ? SENSOR_NAME[i] : null)).filter(Boolean);
    if (loose.length) return `${loose.join(" and ")} sensor loose (picking up mains hum): press it in gently`;
    if (off.length) return `${off.join(" and ")} sensor not reading: press it in, move hair from under it`;
  }
  return WHY[reason] || reason || "";
}

// ------------------------------------------------------------------ EEG indices (fast, from the live band envelopes)
function power(hub, src, band, secs) {
  const env = hub.env[`${src}|${band}`];
  const n = Math.round(FS * secs);
  let s = 0;
  for (let k = 0; k < n; k++) { const v = env[hub.idx(hub.n - 1 - k)]; s += v * v; }
  return s / n + 1e-9;
}
const af = (hub, band, secs) => 0.5 * (power(hub, "AF7", band, secs) + power(hub, "AF8", band, secs));
export const INDICES = {
  // share of power in alpha (delta left out: blinks and eye movements live there)
  relative_alpha: (hub) => { const a = power(hub, "all", "alpha", 1); return Math.log(a / (power(hub, "all", "theta", 1) + a + power(hub, "all", "beta", 1))); },
  // Pope et al. 1995: beta / (alpha + theta)
  engagement: (hub) => Math.log(power(hub, "all", "beta", 1) / (power(hub, "all", "alpha", 1) + power(hub, "all", "theta", 1))),
  // ln(alpha right) - ln(alpha left) over the forehead: up = approach, warmth
  frontal_asymmetry: (hub) => Math.log(power(hub, "AF8", "alpha", 2)) - Math.log(power(hub, "AF7", "alpha", 2)),
  // forehead theta as a share of theta + alpha + beta
  frontal_theta: (hub) => { const t = af(hub, "theta", 1.5); return Math.log(t / (t + af(hub, "alpha", 1.5) + af(hub, "beta", 1.5))); },
  // The Search's candidate shapes of clarity (higher = more of it)
  // side to side: left and right alpha alike, at the forehead and behind the ears
  symmetry: (hub) => -0.5 * (Math.abs(Math.log(power(hub, "AF8", "alpha", 2)) - Math.log(power(hub, "AF7", "alpha", 2)))
    + Math.abs(Math.log(power(hub, "TP10", "alpha", 2)) - Math.log(power(hub, "TP9", "alpha", 2)))),
  // front to back: forehead and ear alpha alike
  axis: (hub) => -Math.abs(Math.log(af(hub, "alpha", 2)) - Math.log(0.5 * (power(hub, "TP9", "alpha", 2) + power(hub, "TP10", "alpha", 2)))),
  // waves moving together: the alpha waves' correlation, averaged over all six sensor pairs, last 2 s
  coherence: (hub) => {
    const b = 2, n = 2 * FS; let s = 0, k = 0;
    for (const arr of hub.corrPair[b]) for (let j = 0; j < n; j += 16) { const v = arr[hub.idx(hub.n - 1 - j)]; if (Number.isFinite(v)) { s += v; k++; } }
    return k ? s / k : NaN;
  },
};
// candidate -> the index it steers
const SEARCH_INDEX = { symmetry: "symmetry", axis: "axis", coherence: "coherence", calm: "relative_alpha", flow: "frontal_theta",
  focus: "engagement", openness: "complexity" };
const CLARITY = ["Foggy", "Dull", "Ordinary", "Clear", "Crystal"];
// the engine's own version of each index, used to put the fast one into reference units
const SLOW = { relative_alpha: "ix_alpha_rel3", engagement: "ix_engagement", frontal_asymmetry: "ix_faa",
  frontal_theta: "ix_theta_af_rel", complexity: "lzc" };

// A unit: the fast index, zeroed at your settle mean in this scene, scaled into your frozen
// reference's units (the fast signal's spread is first matched to the engine's version of it).
class Unit {
  constructor(name, app) { this.name = name; this.slow = SLOW[name]; this.app = app; this.pairs = []; this.fit = null; }
  add(fast, slowVal) { if (Number.isFinite(fast) && Number.isFinite(slowVal)) this.pairs.push([fast, slowVal]); if (this.pairs.length > 3000) this.pairs.shift(); }
  solve() {
    const P = this.pairs;
    if (P.length < 20) return null;
    const f = P.map((p) => p[0]), s = P.map((p) => p[1]);
    const mf = mean(f), ms = mean(s), sf = sd(f) || 1, ss = sd(s) || 1;
    const ref = this.app.status && this.app.status.reference;
    const med = ref && ref.median ? ref.median[this.slow] : undefined;
    const sc = ref && ref.scale ? ref.scale[this.slow] : undefined;
    const anchored = med !== undefined && sc > 0;
    // no reference value for this index (an older calibration): your settle spread stands in
    const scale = anchored ? sc : Math.max(ss, 0.1);
    this.fit = { mf, ms, sf, ss, scale, med, anchored, n: P.length };
    return this.fit;
  }
  z(x) { const F = this.fit || this.solve(); if (!F || !Number.isFinite(x)) return 0; return clamp(((x - F.mf) * F.ss) / F.sf / F.scale, -6, 6); }
  zRef(x) { const F = this.fit || this.solve(); if (!F || !F.anchored || !Number.isFinite(x)) return null; return clamp((F.ms + ((x - F.mf) * F.ss) / F.sf - F.med) / F.scale, -8, 8); }
}

// ------------------------------------------------------------------ video
class Scrubber {
  constructor(video) { this.v = video; this.lastSeek = 0; this.rate = 1; }
  to(T, now) { // follow a target time, forwards by playing, backwards by gentle seeks
    const v = this.v;
    if (!v.duration || v.readyState < 2) return;
    v.loop = false;
    T = clamp(T, 0, v.duration - 0.05);
    const cur = v.currentTime;
    if (T > cur + 0.04) {
      this.setRate(clamp((T - cur) * 1.6, 0.1, 3));
      if (v.paused) v.play().catch(() => {});
    } else if (T < cur - 0.12) {
      if (!v.paused) v.pause();
      if (now - this.lastSeek > 140 && !v.seeking) { v.currentTime = Math.max(T, cur - 0.3); this.lastSeek = now; }
    } else if (!v.paused) v.pause();
  }
  run(rate) { // continuous play, looping, at a rate the brain sets
    const v = this.v;
    if (!v.duration || v.readyState < 2) return;
    v.loop = true;
    this.setRate(clamp(rate, 0.1, 3));
    if (v.paused) v.play().catch(() => {});
  }
  setRate(r) { if (Math.abs(r - this.rate) > 0.02) { this.v.playbackRate = r; this.rate = r; } }
}

// smooth tremor-like noise (sum of incommensurate sines)
function tremor(t, seed) {
  return 0.55 * Math.sin(t * 2 * Math.PI * 3.1 + seed) + 0.3 * Math.sin(t * 2 * Math.PI * 7.3 + seed * 2.1)
    + 0.15 * Math.sin(t * 2 * Math.PI * 11.7 + seed * 3.7);
}
function sway(t, seed) { return Math.sin(t * 2 * Math.PI * 0.35 + seed) + 0.4 * Math.sin(t * 2 * Math.PI * 0.9 + seed * 1.7); }

// ------------------------------------------------------------------ select screen
export function renderSelect(app, levels) {
  const host = $("levels-grid");
  const missing = levels.filter((lv) => !lv.media.ready);
  host.innerHTML = (missing.length ? `<div class="lvl-all"><button class="solid" id="lvl-get-all">Get footage for ${missing.length === levels.length ? "all levels" : `the other ${missing.length}`}</button>
    <span class="fine">Free-licence clips, downloaded once to this computer (about ${missing.length * 20} MB).</span></div>` : "") + levels.map((lv) => {
    const m = lv.media;
    const img = m.previews && m.previews.length ? `style="background-image:url('${m.previews[Math.min(1, m.previews.length - 1)]}')"` : "";
    const action = m.ready
      ? `<button class="solid" data-play="${lv.id}">Play</button>`
      : `<button class="ghost" data-fetch="${lv.id}">Get footage</button>`;
    return `<article class="lvl-card" data-id="${lv.id}">
      <div class="lvl-img ${m.ready ? "" : "empty"}" ${img}><span>${lv.number}</span></div>
      <div class="lvl-body">
        <h3>${esc(lv.title)}</h3><p class="lvl-sub">${esc(lv.subtitle)}</p>
        <p class="fine"><b>Tests:</b> ${esc(lv.tests)}${(app.bests || {})[lv.id] && app.bests[lv.id].best_tier ? ` · <b>Best:</b> ${app.bests[lv.id].best_tier} · ${esc(app.bests[lv.id].best_tier_name || "")}${app.bests[lv.id].fastest_return_s ? ` · fastest return ${app.bests[lv.id].fastest_return_s} s` : ""}` : ""}</p>
        <details><summary class="fine">Why this signal, why this scene</summary>${lv.basis.map((b) => `<p class="fine">${esc(b)}</p>`).join("")}
          <p class="fine">Footage: ${esc(lv.clip.credit)}${m.own ? " · you're using your own clip" : ""}.</p>
          <p class="fine">Your own clip: drop a video into <span class="mono">${esc(m.folder)}</span></p></details>
        <div class="row">${action}<span class="fine" data-status="${lv.id}"></span></div>
      </div></article>`;
  }).join("");
  const fetchOne = (b) => { b.disabled = true; b.textContent = "Downloading…"; app.send({ cmd: "media_fetch", level: b.dataset.fetch }); };
  host.querySelectorAll("[data-fetch]").forEach((b) => (b.onclick = () => fetchOne(b)));
  const all = $("lvl-get-all");
  if (all) all.onclick = () => { all.disabled = true; host.querySelectorAll("[data-fetch]").forEach(fetchOne); };
  host.querySelectorAll("[data-play]").forEach((b) => (b.onclick = () => app.send({ cmd: "level_start", level: b.dataset.play })));
  // save a few frames of each clip so the footage can be checked without opening it
  for (const lv of levels) if (lv.media.ready && !(lv.media.previews || []).length) grabPreviews(lv).catch(() => {});
}

export function mediaProgress(m) {
  const el = document.querySelector(`[data-status="${m.level}"]`);
  if (!el) return;
  if (m.state === "downloading") el.textContent = m.total ? `${Math.round((100 * m.got) / m.total)}% of ${(m.total / 1e6).toFixed(0)} MB` : `${(m.got / 1e6).toFixed(1)} MB`;
  else if (m.state === "done") el.textContent = "Ready.";
  else if (m.state === "failed") el.textContent = `Couldn't download (${(m.errors || []).join("; ").slice(0, 160)}). You can put any video file in ${m.folder}.`;
}

async function grabPreviews(lv) {
  const v = document.createElement("video");
  v.muted = true; v.preload = "auto"; v.src = lv.media.url; v.crossOrigin = "anonymous";
  await new Promise((res, rej) => { v.onloadeddata = res; v.onerror = rej; setTimeout(rej, 20000); });
  const c = document.createElement("canvas");
  const w = 640, h = Math.round((640 * v.videoHeight) / Math.max(1, v.videoWidth));
  c.width = w; c.height = h;
  const g = c.getContext("2d");
  let n = 1;
  for (const f of [0.1, 0.5, 0.9]) {
    v.currentTime = f * v.duration;
    await new Promise((res) => { v.onseeked = res; setTimeout(res, 3000); });
    g.drawImage(v, 0, 0, w, h);
    const blob = await new Promise((res) => c.toBlob(res, "image/jpeg", 0.82));
    await fetch(`/api/preview/${lv.id}/${n++}`, { method: "POST", headers: { "X-IDA-Live": "preview" }, body: blob });
  }
}

// ------------------------------------------------------------------ blink detector
// Blinks are big, slow, shared deflections on both forehead sensors. They are held out
// (the index freezes for half a second) instead of counting as lost signal.
class BlinkGate {
  constructor() { this.typ = 20; this.until = -1; }
  step(hub, t) {
    if (hub.n < FS) return false;
    let peak = 0;
    for (let k = 0; k < 64; k++) { const i = hub.idx(hub.n - 1 - k); const v = Math.abs(0.5 * (hub.raw[1][i] + hub.raw[2][i])); if (v > peak) peak = v; }
    const on = peak > Math.max(60, 3.5 * this.typ);
    if (on) this.until = t + 0.5;
    else this.typ += 0.02 * (peak - this.typ);
    return t < this.until;
  }
}

// ------------------------------------------------------------------ how you feel (Russell's affect grid)
function affectGrid(prompt) {
  const cells = [];
  for (let r = 0; r < 9; r++) for (let c = 0; c < 9; c++) cells.push(`<i data-x="${(c - 4) / 4}" data-y="${(4 - r) / 4}"></i>`);
  return `<h2>${prompt}</h2><div class="affect"><span class="ax ax-top">energised</span><span class="ax ax-left">unpleasant</span>
    <div class="affect-grid">${cells.join("")}</div><span class="ax ax-right">pleasant</span><span class="ax ax-bottom">calm</span></div><p class="fine">Click the square that fits. Top right: excited, elated. Bottom right: serene, relaxed. Bottom left: flat, low. Top left: tense, stressed.</p>`;
}
function moodWord([x, y]) {
  const v = x > 0.25 ? "pleasant" : x < -0.25 ? "unpleasant" : "neutral", a = y > 0.25 ? "energised" : y < -0.25 ? "calm" : "";
  return a ? `${v} and ${a}` : v;
}
function onAffect(cb) {
  document.querySelectorAll(".affect-grid i").forEach((el) => (el.onclick = () => { el.classList.add("on"); setTimeout(() => cb(Number(el.dataset.x), Number(el.dataset.y)), 250); }));
}

// ------------------------------------------------------------------ the runner
// Phases: intro -> settle (your baseline in this scene, and the scale of the fast signal) ->
// rounds (the chamber; one round is a sealed replay of an earlier round) -> rating -> results.

export class LevelRunner {
  constructor(app, plan) {
    this.app = app;
    this.plan = plan;
    this.lv = plan.level;
    this.mode = this.lv.mode || this.lv.effect || "bloom";
    this.phase = "loading";
    this.t0 = performance.now() / 1000;
    this.rounds = plan.arms.map((arm) => ({ arm, tape: [], rating: null, summary: null }));
    this.k = -1;
    // the target index and, where the level needs them, the gate and the two parts of "return"
    // a personal signature from the attention map (when it passed its gate) replaces the textbook index
    this.profile = plan.profile || null;
    if (this.profile) this.lv = { ...this.lv, index: "profile", tests: this.lv.tests + " (your own signature)" };
    this.search = plan.search || null;
    if (this.search) this.lv = { ...this.lv, title: "The Search", tests: "what clarity is, for you", index: SEARCH_INDEX[this.search.schedule.find((c) => c !== "free")] };
    const ix = this.lv.index;
    this.parts = ix === "return" ? ["relative_alpha", "engagement"] : [ix];
    if (this.search) for (const c of Object.values(SEARCH_INDEX)) if (!this.parts.includes(c)) this.parts.push(c);
    if (this.lv.gate) this.parts.push(this.lv.gate.index);
    if (!this.parts.includes("engagement")) this.parts.push("engagement");
    this.units = Object.fromEntries(this.parts.map((p) => [p, new Unit(p, app)]));
    this.x = {};
    this.snaps = [];
    this.rows = []; this.lastSample = 0; this.lastSend = 0;
    this.seed = Math.random() * 10;
    this.blinks = new BlinkGate();
    // ease: the lower tiers come nearer and wider; the top tier (Monk) stays exactly as declared
    this.ease = clamp(plan.ease ?? 0, 0, 1);
    if (this.ease > 0 && Array.isArray(this.lv.tiers)) {
      const n = this.lv.tiers.length;
      this.lv = { ...this.lv, tiers: this.lv.tiers.map((T, i) => {
        const w = this.ease * (1 - i / Math.max(1, n - 1));
        return { ...T, depth: +(T.depth * (1 - 0.45 * w)).toFixed(3), tau: +(T.tau * (1 + 0.5 * w)).toFixed(3) };
      }) };
    }
    this.journey = !!plan.journey;
    this.carryPlan = plan.carry || [];
    this.carryIdx = 0; this.carry = null; this.dips = []; this.carryNext = 0; this.fHist = [];
    // ease also lifts the scene's resting clarity (the TAO rest point of q), so it settles grey-ish
    // rather than grey when nothing is happening; the declared contract records the value used
    const qRest = +(0.12 + 0.25 * this.ease).toFixed(3);
    this.chamber = new Chamber(this.lv, { z_smooth_s: plan.smooth_s ?? 5, world: { q: { target: qRest, start: qRest } } });
    this.world = { q: 0.12, h: 0.25, n: 0.5, p: 0, F: 0 };
    this.Fs = 0; this.speed = 1; this.fx = { drop: [0.5, 0.25, 9], meteor: [0, 0, 0, 9], flash: 0 };
    this.badSince = null;
    this.effortStats = []; this.breathStats = [];
    this.sound = (plan.sound || plan.arms.map(() => "none"));
    const au = plan.audio || (app.status && app.status.settings && app.status.settings.audio) || {};
    this.snd = au.enabled === false ? null : new LevelSound(au, plan.music_style === "canon" ? "canon" : this.lv.id, "none", plan.entrain_hz || 0, this.lv.id);
    this.pacerHz = (au.pacer_bpm || 6) / 60;
    this.build();
  }

  send(msg) { this.app.send(msg); }
  clockNow() { const tk = this.app.tick; return tk ? +(tk.t + (performance.now() - (this.app.lastTickAt || performance.now())) / 1000).toFixed(3) : this.now(); }
  now() { return performance.now() / 1000 - this.t0; }

  build() {
    const el = $("level-stage");
    el.hidden = false;
    el.innerHTML = `<video id="lv-video" muted playsinline preload="auto" crossorigin="anonymous"></video>
      <canvas id="lv-canvas"></canvas>
      <div id="lv-card" class="lv-card"></div>
      <div id="lv-tier" class="lv-tier"></div>
      <div id="lv-hint" class="lv-hint"></div>
      <div id="lv-dots" class="lv-dots"></div>
      <button id="lv-skip" class="lv-skip" title="Skip (S or →)">Skip ›</button>
      <div id="lv-sound" class="lv-hint lv-sound"></div>`;
    $("lv-skip").onclick = (e) => { e.stopPropagation(); this.skip(); };
    el.addEventListener("pointerdown", () => this.snd && this.snd.resume());
    document.body.classList.add("leveling");
    this.video = $("lv-video");
    this.scrub = new Scrubber(this.video);
    try { this.comp = new Compositor($("lv-canvas"), this.video); }
    catch (e) { this.card(`<h2>This computer's graphics can't run the chamber.</h2><p>${esc(e.message)}</p>`, true); return; }
    this.video.src = (this.lv.media && this.lv.media.url) || "";
    this.video.onloadeddata = () => { if (this.phase === "loading") this.go("intro"); };
    this.video.onerror = () => this.card(`<h2>This level's footage couldn't be played.</h2><p>Open Levels and press Get footage, or drop a video (mp4 or webm) into its folder.</p>`, true);
    this.keys = (e) => this.onKey(e);
    window.addEventListener("keydown", this.keys, true);
  }

  card(html, closable = false) {
    const c = $("lv-card");
    c.innerHTML = html + (closable ? `<button class="solid" id="lv-close">Close</button>` : "");
    c.classList.add("on");
    if (closable) $("lv-close").onclick = () => this.close();
  }
  hideCard() { $("lv-card").classList.remove("on"); }

  go(phase) {
    this.phase = phase;
    this.phaseStart = this.now();
    const n = this.plan.rounds, T = this.lv.tiers;
    if (phase === "intro") {
      // the declared contract goes into the record before any outcome exists (pre-registration)
      this.send({ cmd: "level_event", kind: "contract", data: { contract: this.chamber.K, sound: this.sound, entrain_hz: this.plan.entrain_hz || 0 } });
      this.introReady = false;
      this.card(`<p class="lv-num">Level ${this.lv.number} · before we start</p>${affectGrid("How do you feel right now?")}`);
      onAffect((x, y) => {
        this.send({ cmd: "level_event", kind: "affect", data: { when: "pre", valence: x, arousal: y } });
        this.affect = { pre: [x, y] };
        this.phaseStart = this.now(); this.introReady = true;
        this.card(`<p class="lv-num">Level ${this.lv.number} · ${esc(this.lv.tests)}</p><h1>${esc(this.lv.title)}</h1><p class="lv-sub">${esc(this.lv.instruction || this.lv.subtitle)}</p>
          <p class="fine">${this.search
            ? `Eight rounds of a minute. In each, the water answers one idea of what a clear mind is (balance side to side, front to back, waves moving together, calm, absorption, focus, openness), or nothing at all; you won't be told which. Just let your mind do what it does. After each round tap how clear your mind feels. Now and then a faint light blinks in the small circle below the centre: press <b>Space</b> when you see it. Esc leaves.`
            : this.journey
            ? `Twenty seconds just to watch (your baseline in this scene), then one ${Math.round(this.plan.round_s / 60)}-minute journey through nine tiers, from ${esc(T[0].name)} to ${esc(T[T.length - 1].name)}. When you start to lose it, the scene, the music and the pulse will usually <b>carry you back up</b>: let them. Press <b>C</b> for a chill or a rush. Head still, jaw soft. Esc leaves.`
            : `First half a minute just to watch: that sets your baseline in this scene. Then ${n} rounds of ${Math.round(this.plan.round_s)} s, nine tiers from ${esc(T[0].name)} to ${esc(T[T.length - 1].name)}. The music is unfinished until you finish it: it resolves when you are in, and each tier brings in a new voice. Press <b>C</b> whenever you feel a chill or a rush. Head still, jaw soft. Esc leaves.`}</p>`);
      });
    } else if (phase === "settle") {
      this.card(`<p class="lv-sub">Just watch. Nothing to do yet.</p>`);
      setTimeout(() => { if (this.phase === "settle") this.hideCard(); }, 3500);
    } else if (phase === "round") {
      this.k += 1;
      this.chamber.reset();
      if (this.search) {
        this.cand = this.search.schedule[this.k] || "free";
        this.lv = { ...this.lv, index: this.cand === "free" ? "free" : SEARCH_INDEX[this.cand] };
        // a shape with a known sweet spot is steered TO that point (every tier's corridor centred
        // there, narrowing as you climb), not towards "more"
        const zt = this.search.targets && this.search.targets[this.cand];
        const base0 = this.chamber.base;
        if (Number.isFinite(zt)) {
          this.chamber = new Chamber({ ...this.lv, corridor: null, tiers: this.lv.tiers.map((T) => ({ ...T, depth: zt })) }, this.chamber.K);
        } else if (this._searchBaseTiers) this.chamber = new Chamber({ ...this.lv, tiers: this._searchBaseTiers }, this.chamber.K);
        this._searchBaseTiers ||= this.lv.tiers;
        this.chamber.base = base0;                        // keep the settle's critical-slowing baseline
        const R_s = this.plan.round_s || 60;
        this.probeTimes = [0.2, 0.47, 0.73].map((f) => R_s * (f + Math.random() * 0.13));
        this.send({ cmd: "level_event", kind: "search_round", data: { round: this.k + 1, cand: this.cand } });
      }
      this.hideCard();
      if (this.snd) this.snd.setCondition(this.sound[this.k] || "none");
      this.send({ cmd: "level_event", kind: "round_start", data: { round: this.k + 1 } });
    } else if (phase === "rate") {
      const labels = this.search ? CLARITY : RATING;
      this.card(`<p class="lv-num">Round ${this.k + 1} of ${n}</p><h2>${this.search ? "How clear is your mind right now?" : "How much did the scene follow you?"}</h2>
        <div class="lv-rate">${labels.map((t, i) => `<button data-r="${i}"><b>${i}</b>${t}</button>`).join("")}</div>`);
      $("lv-card").querySelectorAll("[data-r]").forEach((b) => (b.onclick = () => this.rate(Number(b.dataset.r))));
    } else if (phase === "reset") {
      this.card(`<p class="lv-sub">Round ${this.k + 2}</p>`);
    } else if (phase === "done") {
      this.finish();
    }
    this.renderDots();
  }

  renderDots() {
    $("lv-dots").innerHTML = this.rounds.map((_, i) => `<i class="${i < this.k || (i === this.k && this.phase !== "round") ? "done" : i === this.k ? "now" : ""}"></i>`).join("");
  }

  rate(v) {
    if (this.phase !== "rate" || this.rounds[this.k].rated) return;
    this.rounds[this.k].rating = v; this.rounds[this.k].rated = true;
    this.send({ cmd: "level_event", kind: "rating", data: { round: this.k + 1, rating: v } });
    const next = () => this.go(this.k + 1 < this.plan.rounds ? "reset" : "done");
    if (v === null || this.search) { next(); return; }        // the Search keeps moving: one tap per round
    this.phaseStart = this.now();
    this.card(`<p class="lv-num">Round ${this.k + 1}</p>${affectGrid("And how did it feel?")}`);
    onAffect((x, y) => {
      this.rounds[this.k].affect = [x, y];
      this.send({ cmd: "level_event", kind: "affect", data: { when: "round", round: this.k + 1, valence: x, arousal: y } });
      next();
    });
  }

  // skip: hurry past whatever is on now. Every skip is logged; a skipped round still counts
  // for what it recorded, and the settle can only be cut short once it has a usable baseline.
  skip() {
    const el = this.now() - this.phaseStart, ph = this.phase;
    if (ph === "intro") this.go("settle");
    else if (ph === "settle") {
      const n = this.units[this.parts[0]].pairs.length;
      if (n < 60) { this.flash(`Baseline needs ${Math.ceil((60 - n) / 10)} more seconds of clean signal`); return; }
      this._skipSettle = true;
    } else if (ph === "round") {
      const R = this.rounds[this.k];
      R.summary = { ...this.chamber.summary(), skipped_at_s: +el.toFixed(1) };
      this.send({ cmd: "level_event", kind: "round_end", data: { round: this.k + 1, ...R.summary } });
      this.go("rate");
    } else if (ph === "rate") this.rate(null);
    else if (ph === "reset") this.go("round");
    else return;
    this.send({ cmd: "level_event", kind: "skip", data: { phase: ph, after_s: +el.toFixed(1), round: this.k + 1 } });
  }

  flash(text) {
    const h = $("lv-sound"); h.textContent = text; h.classList.add("on");
    clearTimeout(this._fl); this._fl = setTimeout(() => h.classList.remove("on"), 2500);
  }

  onKey(e) {
    if (e.key === " " && this.search) {
      e.stopPropagation(); e.preventDefault();
      if (this.probe) this.endProbe(true, +(this.now() - this.probe.t).toFixed(3));
      else { this.falsePresses = (this.falsePresses || 0) + 1; this.send({ cmd: "level_event", kind: "false_press", data: { round: this.k + 1 } }); }
      return;
    }
    if ((e.key === "c" || e.key === "C") && (this.phase === "round" || this.phase === "settle")) {
      e.stopPropagation(); e.preventDefault();
      this.chills = (this.chills || 0) + 1;
      this.rows.push({ t: this.clockNow(), level: this.lv.id, round: this.phase === "round" ? this.k + 1 : 0, phase: this.phase, event: "chill" });
      this.send({ cmd: "level_event", kind: "chill", data: { round: this.k + 1, phase: this.phase } });
      const d = document.createElement("i"); d.className = "lv-chill"; $("level-stage").appendChild(d); setTimeout(() => d.remove(), 1200);
      return;
    }
    if ((e.key === "s" || e.key === "S" || e.key === "ArrowRight") && this.phase !== "done") { e.stopPropagation(); e.preventDefault(); this.skip(); return; }
    if (e.key === "Escape") { e.stopPropagation(); e.preventDefault(); if (this.phase === "done" || confirm("Leave this level? It is saved as far as it got.")) this.close(true); return; }
    if (this.phase === "rate" && /^[0-4]$/.test(e.key)) { e.stopPropagation(); e.preventDefault(); this.rate(Number(e.key)); }
    else e.stopPropagation();
  }

  // read every index this level uses; blinks freeze them, lost signal is reported
  sense(t) {
    const hub = this.app.hub, tick = this.app.tick || {};
    const st = tick.state || {}, feats = tick.features || {};
    let reasons = (st.reasons || []).filter((r) => r !== "blink");
    // a forehead-only index (warmth, frontal theta) doesn't care what the ear sensors are doing:
    // if both forehead sensors are fine, ear contact or ear muscle doesn't hold the level back
    const q = (tick.flags && tick.flags.quality) || null;
    if (FOREHEAD_ONLY.has(this.lv.index) && q && ["good", "ok", "interference"].includes(q[1]) && ["good", "ok", "interference"].includes(q[2])) {
      reasons = reasons.filter((r) => r !== "contact" && r !== "muscle");
    }
    const blink = this.blinks.step(hub, t);
    const clean = hub.n > FS && reasons.length === 0;
    if (t - (this._tIdx || 0) > 0.1 && hub.n > FS) {
      const a = 1 - Math.exp(-(t - (this._tIdx || t)) / 0.6);
      this._tIdx = t;
      for (const p of this.parts) {
        const v = p === "complexity" ? (st.lzc ?? feats.lzc) : p === "profile" ? this.profileScore(feats) : INDICES[p](hub);
        const slow = p === "complexity" || p === "profile";
        if (!Number.isFinite(v) || (blink && !slow)) continue;
        this.x[p] = this.x[p] === undefined ? v : this.x[p] + (slow ? 0.05 : a || 0.15) * (v - this.x[p]);
        if (this.phase === "settle" && clean) this.units[p].add(this.x[p], slow || !SLOW[p] ? this.x[p] : feats[SLOW[p]]);
      }
    }
    if (this.phase === "settle" && t - (this._tSolve || 0) > 1) { this._tSolve = t; for (const u of Object.values(this.units)) u.solve(); }
    if (!clean) this.badSince ??= t; else this.badSince = null;
    return { clean, blink, reasons, motion: feats.motion_dps || 0 };
  }

  // the attention-map model: w0 + sum w_k (x_k - mean_k) / sd_k, signed so that up = the level's aim
  profileScore(feats) {
    const m = this.profile.model;
    let s = m.w[0];
    for (let k = 0; k < m.features.length; k++) {
      const v = feats[m.features[k]];
      if (!Number.isFinite(v)) return NaN;
      s += m.w[k + 1] * (v - m.mean[k]) / m.sd[k];
    }
    return this.profile.sign * s;
  }

  target(x = this.x) {
    const u = this.units;
    if (this.lv.index === "free") return { z: 0.2 + 0.6 * Math.sin(this.now() / 9) , zRef: null };   // nothing steered: a slow tide
    if (this.lv.index === "return") { // distance from your baseline state in this scene
      const za = u.relative_alpha.z(x.relative_alpha), ze = u.engagement.z(x.engagement);
      return { z: -Math.sqrt((za * za + ze * ze) / 2), zRef: null };
    }
    const ix = this.lv.index;
    return { z: u[ix].z(x[ix]), zRef: u[ix].zRef(x[ix]) };
  }

  frame(nowMs) {
    const t = this.now();
    const dt = Math.min(0.1, t - (this._tPrev ?? t));
    this._tPrev = t;
    if (this.phase === "loading" || !this.comp) return;
    const el = t - this.phaseStart;
    const s = this.sense(t);
    let { z, zRef } = this.target();
    const zLive = z; // your brain now, even while a replay round shows an earlier round
    let ze = this.units.engagement.z(this.x.engagement);
    let cl = s.clean, mo = s.motion;
    // effort (muscle, forehead first) and breathing, each against this scene's settle
    const feats = (this.app.tick || {}).features || {};
    const emg = feats.emg_af ?? feats.emg_tp;
    if (this.phase === "settle" && Number.isFinite(emg) && t - (this._tEff || 0) > 0.5) {
      this._tEff = t; this.effortStats.push(emg);
      if (Number.isFinite(feats.breath_bpm) && (feats.breath_conf || 0) > 0.3) this.breathStats.push(feats.breath_bpm);
    }
    const effort = this.effortBase && Number.isFinite(emg) ? clamp((emg - this.effortBase[0]) / this.effortBase[1], -4, 8) : 0;
    const breath = { sync: feats.breath_sync, conf: feats.breath_conf || 0,
      rate_z: this.breathBase && Number.isFinite(feats.breath_bpm) ? clamp((feats.breath_bpm - this.breathBase[0]) / this.breathBase[1], -3, 3) : 0 };

    if (this.phase === "intro" && this.introReady && el > 9) this.go("settle");
    const live = this.phase === "round";
    const R = this.k >= 0 ? this.rounds[this.k] : null;
    if (this.phase === "settle") {
      if (s.clean && !s.blink && t - (this._tSnap || 0) > 0.1) { this._tSnap = t; this.snaps.push({ ...this.x }); }
      const n = this.units[this.parts[0]].pairs.length;
      // the settle ends once it has enough clean signal to set the scale (up to a minute longer)
      if (this._skipSettle || (el > this.plan.settle_s && (n >= 100 || el > this.plan.settle_s + 45))) {
        this._skipSettle = false;
        const m = (a) => a.reduce((x, y) => x + y, 0) / Math.max(1, a.length);
        const sdv = (a, floor) => Math.max(floor, Math.sqrt(m(a.map((v) => (v - m(a)) ** 2))));
        this.effortBase = this.effortStats.length > 10 ? [m(this.effortStats), sdv(this.effortStats, 0.05)] : null;
        this.breathBase = this.breathStats.length > 5 ? [m(this.breathStats), sdv(this.breathStats, 1.5)] : null;
        for (const u of Object.values(this.units)) u.solve();
        // critical-slowing baseline: the settle, re-expressed in the units the rounds use
        this.chamber.setBaseline(this.snaps.slice(-600).map((x) => this.target(x).z));
        this.snaps = [];
        const fits = Object.fromEntries(Object.entries(this.units).map(([k, u]) => [k, u.fit]));
        this.send({ cmd: "level_event", kind: "baseline", data: { zero: "settle", fits, base: this.chamber.base } });
        this.go("round");
      }
    } else if (live) {
      // tape every 0.1 s; a replay round plays back an earlier real round's tape (TAO's state-replay condition)
      const i = Math.floor(el * 10);
      if (R.arm === "real") { if (i >= R.tape.length) R.tape.push({ z, ze, clean: cl, motion: mo, effort, breath }); }
      else {
        const src = this.rounds.slice(0, this.k).reverse().find((q) => q.arm === "real" && q.tape.length > 50);
        if (src) { const r = src.tape[i % src.tape.length]; z = r.z; ze = r.ze; cl = r.clean; mo = r.motion; this._replay = r; }
      }
      if (el > this.plan.round_s) {
        R.summary = { ...this.chamber.summary(), dips: this.dips.map((d) => ({ ...d })) };
        this.send({ cmd: "level_event", kind: "round_end", data: { round: this.k + 1, ...R.summary } });
        if (this.carry && this.carry.active) this.endCarry();
        this.go(this.journey ? "done" : "rate");
      }
    } else if (this.phase === "reset" && el > 4) this.go("round");
    else if (this.phase === "rate" && el > 40) { if (this.rounds[this.k].rated) this.go(this.k + 1 < this.plan.rounds ? "reset" : "done"); else this.rate(null); }

    // secondary constraint: flow needs engagement inside a band (an inverted U)
    let gate = 1, over = 0, under = 0;
    if (this.lv.gate) {
      const G = this.lv.gate, k = 4 / (G.soft || 0.5);
      gate = sig(k * (ze - G.lo)) * sig(k * (G.hi - ze));
      over = clamp(ze - G.hi, 0, 1.5) / 1.5; under = clamp(G.lo - ze, 0, 1.5) / 1.5;
    }

    // the chamber: player state -> world state (TAO law), then the compositor draws it
    const stepping = this.phase === "round" || this.phase === "settle";
    const w = stepping
      ? this.chamber.step({ dt, z, ze, clean: cl, motion: mo, live, gate,
        effort: live && R.arm !== "real" && this._replay ? this._replay.effort : effort,
        breath: live && R.arm !== "real" && this._replay ? this._replay.breath : breath })
      : { ...this.world, pos: this.world.pos || 0, tier: this.chamber.tier, name: this.chamber.tierSpec.name, event: "" };
    if (this.phase === "reset") { w.q = Math.max(0.1, w.q - dt * 0.3); w.n = Math.min(0.6, w.n + dt * 0.1); }
    this.world = { ...w };
    this.Fs += (1 - Math.exp(-dt / 1.5)) * ((w.Fe ?? 0) - this.Fs);
    if (live && !this.search) this.carryStep(w, t, R);
    if (live && this.search) this.probeStep(t, el);
    // ease: some of the scene always shows (the image never collapses to nothing)
    if (this.ease > 0) w.q = 0.28 * this.ease + (1 - 0.28 * this.ease) * w.q;
    this.scene(w, t, dt, { over, under, motion: mo });
    // the breath pacer's phase comes from the shared clock, so picture, sound and the engine's
    // breath-synchrony measure all agree on it
    const tick = this.app.tick;
    const clock = tick ? tick.t + (performance.now() - (this.app.lastTickAt || performance.now())) / 1000 : t;
    w.pacer = 2 * Math.PI * this.pacerHz * clock;
    this.comp.draw(w, t);
    this.drive(w, t, nowMs, over);
    if (this.snd && t - (this._tSnd || 0) > 0.05) {
      this._tSnd = t;
      if (!this.snd.running) { this.snd.resume(); if (this.snd.ok && t > 3 && !this._soundHint) { this._soundHint = true; this.flash("Click once for sound"); } }
      this.snd.update({ ...w, l: w.l }, w.pacer, stepping || this.phase === "reset", clock);
      const sc = this.snd.score;
      if (sc && sc.events.length > (this._musN || 0)) {
        for (const ev of sc.events.slice(this._musN || 0)) this.rows.push({ t: clock, level: this.lv.id, round: this.phase === "round" ? this.k + 1 : 0, phase: this.phase, tier: ev.tier, event: `music:${ev.kind}` });
        this._musN = sc.events.length;
      }
    }

    const tierEl = $("lv-tier");
    const label = live ? `${w.tier} · ${w.name}` : "";
    if (tierEl.textContent !== label) { tierEl.textContent = label; tierEl.classList.remove("pulse"); void tierEl.offsetWidth; if (label) tierEl.classList.add("pulse"); }
    // say why nothing is responding, but only after it has lasted a moment
    const hint = stepping && this.badSince !== null && t - this.badSince > 2.5 ? explain(s.reasons[0], ((this.app.tick || {}).flags || {}).quality) : "";
    const hEl = $("lv-hint");
    if (hEl.textContent !== hint) { hEl.textContent = hint; hEl.classList.toggle("on", !!hint); }

    // record, 4 times a second
    if (t - this.lastSample > 0.25) {
      this.lastSample = t;
      const r4 = (x, d = 4) => (x === undefined || x === null || !Number.isFinite(x) ? null : +x.toFixed(d));
      const ix = this.lv.index === "return" ? "relative_alpha" : this.lv.index;
      this.rows.push({ t: this.app.tick ? this.app.tick.t : t, level: this.lv.id, round: live ? this.k + 1 : 0, arm: R && live ? R.arm : "",
        phase: this.phase, tier: w.tier, x_fast: r4(this.x[ix], 5), z: r4(z), z_live: r4(zLive), z_ref: r4(zRef), z_eng: r4(ze), gate: r4(gate, 3),
        F: r4(w.F), Fe: r4(w.Fe), conf: r4(w.conf, 3), a: r4(w.a, 3), c: r4(w.c, 3), l: r4(w.l, 3),
        q: r4(w.q), h: r4(w.h), n: r4(w.n), p: r4(w.p), warning: w.warning ? 1 : 0, blink: s.blink ? 1 : 0, speed: r4(this.speed, 3),
        emg: r4(emg, 3), effort: r4(effort, 3), breath_sync: r4(breath.sync, 3), breath_bpm: r4(feats.breath_bpm, 2),
        sound: live ? this.sound[this.k] || "none" : "", admissible: w.admissible === false ? 0 : 1, pressure: r4(w.pressure, 3), tau: r4(w.tau, 3),
        video_t: r4(this.video.currentTime || 0, 2), carry: this.carry && this.carry.active ? 1 : 0,
        ...(this.search ? { cand: live ? this.cand : "", ...Object.fromEntries(Object.entries(SEARCH_INDEX).map(([c, ix]) => [`z_${c}`, r4(this.units[ix] ? this.units[ix].z(this.x[ix]) : null)])) } : {}),
        event: w.event || this._dipEvent || "" });
      this._dipEvent = "";
    }
    if (t - this.lastSend > 2 && this.rows.length) { this.lastSend = t; this.send({ cmd: "level_samples", rows: this.rows.splice(0) }); }
  }

  // Faint lights: how clearly you actually perceive, measured the same way in every round. Three
  // per round at unpredictable moments, in a small fixed window below the centre (not part of the
  // scene, so the scene's own clarity can't make them easier). A staircase keeps them near your
  // threshold: two catches in a row make the next one fainter, a miss makes it brighter.
  probeStep(t, el) {
    if (!this.probeEl) {
      const d = document.createElement("div"); d.className = "lv-probe"; d.innerHTML = "<i></i>";
      $("level-stage").appendChild(d); this.probeEl = d;
      try { this.contrast = Number(localStorage.getItem("ida.probeContrast")) || 0.12; } catch (e) { this.contrast = 0.12; }
      this.streak = 0;
    }
    if (this.probe && t - this.probe.t > 1.5) this.endProbe(false, null);
    if (!this.probe && this.probeTimes && this.probeTimes.length && el >= this.probeTimes[0]) {
      this.probeTimes.shift();
      this.probe = { t, contrast: this.contrast, round: this.k + 1, cand: this.cand };
      const i = this.probeEl.querySelector("i");
      i.style.opacity = String(this.contrast);
      setTimeout(() => { i.style.opacity = "0"; }, 110);
    }
  }
  endProbe(hit, rt) {
    const p = this.probe; if (!p) return;
    this.probe = null;
    this.send({ cmd: "level_event", kind: "probe", data: { round: p.round, cand: p.cand, contrast: +p.contrast.toFixed(4), hit, rt } });
    this.rows.push({ t: this.clockNow(), level: this.lv.id, round: p.round, phase: this.phase, cand: p.cand, event: `probe:${hit ? "hit" : "miss"}:${p.contrast.toFixed(4)}` });
    (this.probes ||= []).push({ ...p, hit, rt });
    if (hit) { this.streak++; if (this.streak >= 2) { this.contrast = Math.max(0.01, this.contrast * 0.8); this.streak = 0; } }
    else { this.streak = 0; this.contrast = Math.min(0.6, this.contrast * 1.25); }
    try { localStorage.setItem("ida.probeContrast", String(this.contrast)); } catch (e) { /* fine */ }
  }

  // The carry. A fall is when your smoothed occupancy (from your live brain, never the display)
  // drops below 55% of its peak over the last 8 s, having been at least 0.35. At each fall the
  // next sealed coin decides: carry (the scene holds and lifts, the music resolves and swells,
  // the pulse strengthens, for 12 s) or follow (the scene simply follows you, as before). The
  // time to get back to 90% of the peak is measured from your brain either way, so the carry can
  // be tested against following, fall by fall, without any replay rounds.
  carryStep(w, t, R) {
    if (!(this.carry && this.carry.active)) {
      this.posHist = (this.posHist || []).concat([[t, w.pos || 0, w.q || 0]]).filter((x) => t - x[0] <= 8);
      this._posHi = Math.max(...this.posHist.map((x) => x[1]));
      this._qHi = Math.max(...this.posHist.map((x) => x[2]));
    }
    this.fHist.push([t, this.Fs]);
    while (this.fHist.length && t - this.fHist[0][0] > 8) this.fHist.shift();
    const peak = Math.max(...this.fHist.map((x) => x[1]));
    for (const d of this.dips) if (d.back === null && this.Fs >= 0.9 * d.pre) d.back = +(t - d.t).toFixed(2);
    for (const d of this.dips) if (d.back === null && t - d.t > 30) d.back = 30;
    const C = this.carry;
    if (C && C.active) {
      const since = t - C.t0;
      if (since > 12) { this.endCarry(); }
      else {
        // hold what you had, then lift a little beyond it; calm the noise; strengthen the pulse
        const lift = clamp(since / 8, 0, 1);
        // (only what you see and hear changes: F, Fe and the tier stay your brain's, and are what is recorded)
        w.q = Math.max(w.q, Math.min(0.97, C.q0 + 0.18 * lift));
        w.n = w.n * 0.4; w.l = 0; w.h = Math.max(w.h, 0.85); w.carry = 1;
        w.pos = Math.max(w.pos || 0, (C.pos0 || 0) + 0.035 * lift);   // the flower holds, then opens a touch
        return;
      }
    }
    if (t < this.carryNext || peak < 0.35 || this.Fs >= 0.55 * peak) return;
    const arm = this.carryPlan[this.carryIdx++] ?? false;
    const d = { t: +t.toFixed(2), arm: arm ? "carry" : "follow", pre: +peak.toFixed(3), back: null, tier: w.tier };
    this.dips.push(d);
    this._dipEvent = `dip:${d.arm}`;
    this.send({ cmd: "level_event", kind: "dip", data: { at_s: d.t, arm: d.arm, pre: d.pre, tier: d.tier, n: this.dips.length } });
    this.carryNext = t + 20;
    this.carry = { active: arm, t0: t, q0: this._qHi ?? w.q, F0: peak, tier: w.tier, pos0: this._posHi ?? w.pos };
    if (arm && this.snd) this.snd.carry(true);
  }
  endCarry() {
    if (this.carry) this.carry.active = false;
    if (this.snd) this.snd.carry(false);
  }

  // per-scene answers, in the language of the scene
  scene(w, t, dt, x) {
    w.mode = MODES[this.mode] ?? 0;
    w.warm = 0; w.over = x.over; w.under = x.under; w.zoom = 1; w.sx = 0; w.sy = 0; w.sr = 0;
    const p = w.p || 0, ev = w.event || "";
    const fx = this.fx;
    if (ev) { // a perturbation just fired
      if (this.mode === "water") fx.drop = [0.2 + 0.6 * Math.random(), 0.12 + 0.22 * Math.random(), 0];
      if (this.mode === "sky") { const up = Math.random() < 0.5; fx.meteor = [0.15 + 0.7 * Math.random(), 0.72 + 0.2 * Math.random(), up ? -0.5 : -2.6, 0]; }
      if (this.mode === "storm") fx.flash = 1;
    }
    fx.drop[2] += dt; fx.meteor[3] += dt; fx.flash *= Math.exp(-dt / 0.35);
    // a tier climb: light gathers in the scene (a slow swell, never a flash), with the music's peak
    if (this.phase === "round" && w.tier > (this._lastTier || 1)) { fx.peak = 1; this.bestMoments = (this.bestMoments || 0) + 1; }
    if (this.phase === "round") this._lastTier = w.tier;
    fx.peak = (fx.peak || 0) * Math.exp(-dt / 2.5);
    w.peak = fx.peak;
    w.drop = fx.drop; w.meteor = fx.meteor; w.flash = fx.flash;
    const knock = 0.004 * p;
    if (this.mode === "steady") {
      // the rope sways with unsteady attention, and the gust knocks it (plus real head motion)
      const unsteady = Math.pow(clamp(1 - (w.c ?? 0.5) * (w.Fe ?? 0), 0, 1), 1.4);
      const amp = 0.02 * unsteady + 0.035 * p + Math.min(0.01, x.motion / 2000);
      w.sx = amp * (0.6 * sway(t, this.seed) + 0.4 * tremor(t, this.seed)); w.sy = 0.5 * amp * tremor(t, this.seed + 5);
      w.sr = 0.9 * amp * (sway(t, this.seed + 9) + 0.3 * tremor(t, this.seed + 2));
    } else if (this.mode === "ride") {
      const amp = 0.01 * x.over + 0.02 * p;
      w.sx = amp * tremor(t * 0.8, this.seed); w.sy = amp * tremor(t * 0.8, this.seed + 4); w.sr = 0.3 * amp * tremor(t, this.seed + 7);
    } else if (this.mode === "storm") {
      const amp = 0.004 + 0.012 * (1 - this.Fs) + 0.03 * p;
      w.sx = amp * sway(t * 1.3, this.seed); w.sy = 0.6 * amp * tremor(t * 0.4, this.seed + 4); w.sr = 0.5 * amp * sway(t * 0.9, this.seed + 7);
    } else if (this.mode === "bloom") {
      w.warm = w.carry && this.carry ? Math.max(this.Fs, this.carry.F0) : this.Fs;
      w.sx = knock * tremor(t * 0.5, this.seed); w.sy = knock * tremor(t * 0.5, this.seed + 4);
    } else if (this.mode === "sky") {
      w.zoom = 0.82 + 0.18 * w.q; // the view widens as you open
    } else {
      w.sx = knock * tremor(t * 0.5, this.seed); w.sy = knock * tremor(t * 0.5, this.seed + 4);
    }
    // loop seam: a soft dip for the last and first 0.35 s of a looping clip
    const v = this.video, d = v.duration || 0;
    w.edge = v.loop && d > 2 ? clamp(Math.min(v.currentTime, d - v.currentTime) / 0.35, 0, 1) : 1;
  }

  // how the footage moves: scrubbed by progress, or carried at a speed the brain sets
  drive(w, t, nowMs, over) {
    const stepping = this.phase === "round" || this.phase === "settle" || this.phase === "reset";
    const how = this.lv.video || "scrub";
    const p = w.p || 0;
    if (how === "scrub") {
      if (!stepping) return;
      const prog = clamp(w.pos || 0, 0, 1);
      const shaped = 1 - Math.pow(1 - prog, 1.6); // early tiers show more change; the last of it needs the top
      this.scrub.to(shaped * (this.video.duration || 0), nowMs);
      return;
    }
    let rate = 0.6;
    if (how === "travel" && this.mode === "storm") rate = 0.3 + 1.1 * (1 - this.Fs) + 0.8 * p;   // the sea slows as you return
    else if (how === "travel") rate = 0.25 + 0.9 * this.Fs + 0.5 * over + 0.4 * p;               // the wave carries you in flow
    else rate = 0.5 + 0.2 * this.Fs;                                                               // still water: a slow drift
    if (this.phase === "intro" || this.phase === "rate") rate = 0.4;
    this.speed = rate;
    this.scrub.run(rate);
  }

  finish() {
    if (!this.affect || !this.affect.post) {
      this.card(`<p class="lv-num">Level ${this.lv.number} · done</p>${affectGrid("How do you feel now?")}`);
      onAffect((x, y) => {
        (this.affect ||= {}).post = [x, y];
        this.send({ cmd: "level_event", kind: "affect", data: { when: "post", valence: x, arousal: y } });
        this.finish();
      });
      return;
    }
    if (this.rows.length) this.send({ cmd: "level_samples", rows: this.rows.splice(0) });
    const rows = this.rounds.map((R, i) => ({ round: i + 1, arm: R.arm, rating: R.rating, ...(R.summary || {}) }));
    const real = rows.filter((r) => r.arm === "real"), sham = rows.filter((r) => r.arm === "sham");
    const avg = (xs, k) => { const v = xs.map((r) => r[k]).filter((x) => x !== null && x !== undefined); return v.length ? v.reduce((a, b) => a + b, 0) / v.length : null; };
    const summary = { rounds: rows.map((r) => ({ ...r, tier_log: undefined })), best_tier: Math.max(...real.map((r) => r.max_tier || 1)),
      rating_real: avg(real, "rating"), rating_replay: avg(sham, "rating"), chills: this.chills || 0, affect: this.affect || null,
      journey: this.journey, dips: this.dips };
    this.send({ cmd: "level_end", summary });
    const f = (x, d = 1) => (x === null || x === undefined ? "–" : Number(x).toFixed(d));
    const best = summary.best_tier, top = this.lv.tiers[this.lv.tiers.length - 1];
    if (this.search) {
      const pr = this.probes || [];
      const rowsS = this.rounds.map((R, i) => {
        const c = this.search.schedule[i] || "free";
        const ps = pr.filter((p) => p.round === i + 1);
        return `<tr><td>${i + 1}</td><td>${esc(c === "free" ? "nothing steered" : c)}</td><td class="fine">${esc(c === "free" ? "the scene drifted on its own" : this.search.labels[c] || "")}</td><td>${R.rating === null || R.rating === undefined ? "–" : `${R.rating} · ${CLARITY[R.rating]}`}</td><td>${ps.filter((p) => p.hit).length} of ${ps.length}</td></tr>`;
      }).join("");
      this.card(`<p class="lv-num">The Search · revealed</p><h2>Which shape of your mind was being steered, round by round</h2>
        <table class="lv-table"><tr><th>Round</th><th>Steered towards</th><th></th><th>Your clarity</th><th>Faint lights caught</th></tr>${rowsS}</table>
        <p class="fine">Every round also measured all seven shapes at once, whatever was being steered. Over several searches the report finds which shape, and which point along it, goes with your clearest moments.</p>
        <p><button class="ghost" id="lv-report">The leaderboard so far</button></p>`, true);
      const rb3 = $("lv-report");
      if (rb3) rb3.onclick = () => { rb3.disabled = true; rb3.textContent = "Working it out…"; setTimeout(() => { this.close(); this.app.openReport && this.app.openReport("search"); }, 2500); };
      return;
    }
    if (this.journey) {
      const ds = this.dips, med = (a) => { const v = a.filter((x) => x !== null).sort((x, y) => x - y); return v.length ? v[Math.floor(v.length / 2)] : null; };
      const cb = ds.filter((d) => d.arm === "carry").map((d) => d.back), fb = ds.filter((d) => d.arm === "follow").map((d) => d.back);
      this.card(`<p class="lv-num">Level ${this.lv.number} · ${esc(this.lv.title)} · journey</p>
        <h1 class="lv-best">${best} · ${esc(this.lv.tiers[best - 1].name)}</h1><p class="lv-sub">highest tier you held${this.plan.best && best > (this.plan.best.best_tier || 0) ? " · a new personal best" : this.plan.best && this.plan.best.best_tier ? ` · your best is ${this.plan.best.best_tier}` : ""}</p>
        <p class="fine">${this.bestMoments || 0} climb${(this.bestMoments || 0) === 1 ? "" : "s"} · ${ds.length} fall${ds.length === 1 ? "" : "s"}: ${cb.length} carried (back in ${f(med(cb))} s, median), ${fb.length} followed (back in ${f(med(fb))} s). Which falls got carried was sealed before you started; over many journeys this shows whether the carry really brings you back.</p>
        ${this.affect && this.affect.pre && this.affect.post ? `<p class="fine">Mood: ${moodWord(this.affect.pre)} before, ${moodWord(this.affect.post)} after. Chills marked: ${this.chills || 0}.</p>` : ""}
        <p><button class="ghost" id="lv-report">What did my brain do?</button></p>`, true);
      const rb2 = $("lv-report");
      if (rb2) rb2.onclick = () => { rb2.disabled = true; rb2.textContent = "Working it out…"; setTimeout(() => { this.close(); this.app.openReport && this.app.openReport("latest"); }, 1800); };
      return;
    }
    const rule = this.lv.corridor === "near"
      ? `${esc(top.name)} needs you back within ${Math.abs(top.depth)} of your baseline`
      : `${esc(top.name)} needs your signal ${top.depth} beyond your baseline in this scene`;
    this.card(`<p class="lv-num">Level ${this.lv.number} · ${esc(this.lv.title)}</p>
      <h1 class="lv-best">${best} · ${esc(this.lv.tiers[best - 1].name)}</h1><p class="lv-sub">highest tier you held${this.plan.best && best > (this.plan.best.best_tier || 0) ? " · a new personal best" : this.plan.best && this.plan.best.best_tier ? ` · your best is ${this.plan.best.best_tier}` : ""}</p>
      <p class="fine">${this.bestMoments || 0} climb${(this.bestMoments || 0) === 1 ? "" : "s"}${(() => { const rs = rows.filter((r) => r.arm === "real").flatMap((r) => r.recoveries_s || []).filter((x) => x < 15); return rs.length ? ` · ${rs.length} returns, fastest ${Math.min(...rs).toFixed(1)} s` : ""; })()}</p>
      <table class="lv-table"><tr><th>Round</th><th>Highest tier</th><th>Recovery after a knock</th><th>Effort</th><th>Your rating</th><th>It was</th><th>Sound</th></tr>
      ${rows.map((r) => `<tr><td>${r.round}</td><td>${r.max_tier || "–"} · ${esc(r.max_tier_name || "")}</td><td>${r.mean_recovery_s === null || r.mean_recovery_s === undefined ? "–" : f(r.mean_recovery_s) + " s"}</td><td>${f(r.semantic_work, 0)}</td><td>${r.rating === null ? "–" : `${r.rating} · ${RATING[r.rating]}`}</td><td class="${r.arm}">${r.arm === "real" ? "Your brain" : "Replay of an earlier round"}</td><td>${{ entrain: "Rhythm at " + (this.plan.entrain_hz || "") + " Hz", control: "Irregular pulses", none: "–" }[this.sound[r.round - 1] || "none"]}</td></tr>`).join("")}</table>
      <p class="fine">Real rounds rated ${f(summary.rating_real)}, the replay ${f(summary.rating_replay)}. Across many runs, a real sense of control shows as real rounds rated clearly above replays. Tiers are fixed: ${rule} (units of your calibration), held for 70% of 12 s through the strongest knocks.</p>
      ${this.affect && this.affect.pre && this.affect.post ? `<p class="fine">Mood: ${moodWord(this.affect.pre)} before, ${moodWord(this.affect.post)} after. Chills marked: ${this.chills || 0}.</p>` : ""}
      <p><button class="ghost" id="lv-report">What did my brain do?</button></p>`, true);
    const rb = $("lv-report");
    if (rb) rb.onclick = () => { rb.disabled = true; rb.textContent = "Working it out…"; setTimeout(() => { this.close(); this.app.openReport && this.app.openReport("latest"); }, 1800); };
  }

  close(early = false) {
    window.removeEventListener("keydown", this.keys, true);
    if (early && this.phase !== "done") {
      if (this.rows.length) this.send({ cmd: "level_samples", rows: this.rows.splice(0) });
      this.send({ cmd: "level_end", summary: { ended_early: true, phase: this.phase, round: this.k + 1 } });
    }
    try { this.video.pause(); } catch (e) { /* ignore */ }
    if (this.snd) this.snd.close();
    $("level-stage").hidden = true;
    $("level-stage").innerHTML = "";
    document.body.classList.remove("leveling");
    this.app.level = null;
  }
}
