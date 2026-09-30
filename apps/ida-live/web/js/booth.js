// The listening booth: music, three big levers, and your brain simply read.
//
// You listen for as long as you like and move the levers to say how you feel. The middle of
// each lever is you as usual; up is less, down is more. Nothing on screen follows your brain,
// so what the headband records is you, not you reacting to feedback. From enough of it the app
// learns whether your EEG can tell how you feel (a window) or only your body can (muscle,
// breath, the music), and a lever that passes can become what the levels reward.
//
//   FLOW      Q up · A down     stuck  ...  full flow
//   PRESENCE  W up · S down     scattered  ...  fully here
//   HORIZON   E up · D down     closed in  ...  wide open
//   Space     "This!"           a moment that feels most alive
//
// Samples go to the engine at 10 Hz as booth.csv: lever positions (0 none, 0.5 usual, 1 full),
// whether a lever was moving (those seconds are left out of the analysis), "this!" presses,
// what was playing and how loud.

import { LevelSound, sharedContext, unlockAudio } from "./audio.js";

const $ = (id) => document.getElementById(id);
const clamp = (x, a, b) => (x < a ? a : x > b ? b : x);
const esc = (t) => String(t ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const dbToGain = (db) => Math.pow(10, db / 20);

export const LEVERS = [
  { id: "flow", name: "Flow", top: "stuck", bottom: "full flow", up: "q", down: "a", color: "95, 227, 214" },
  { id: "presence", name: "Presence", top: "scattered", bottom: "fully here", up: "w", down: "s", color: "255, 180, 92" },
  { id: "horizon", name: "Horizon", top: "closed in", bottom: "wide open", up: "e", down: "d", color: "185, 156, 255" },
];
const SCORES = [["canon", "Canon (classical)"], ["still", "Still Water"], ["bloom", "Bloom"], ["steady", "Tightrope"], ["ride", "Ride"], ["storm", "Storm"], ["sky", "Night Sky"]];

// the IDA scores play open-loop in the booth: a slow tide that never looks at your brain
function tide(t) {
  const F = 0.5 + 0.3 * Math.sin((2 * Math.PI * t) / 190);
  const q = 0.5 + 0.3 * Math.sin((2 * Math.PI * t) / 250 + 1.1);
  const tier = 1 + Math.round(2.4 * (0.5 + 0.5 * Math.sin((2 * Math.PI * t) / 310 - 1.4)));
  return { F, Fe: F, q, h: 0.25, n: 0.3 + 0.1 * Math.sin(t / 23), l: 0, tier, TF: 0.55 * F, p: 0, a: 0.5 };
}

export class BoothRunner {
  constructor(app, plan) {
    this.app = app;
    this.plan = plan;
    this.v = { flow: 0.5, presence: 0.5, horizon: 0.5 };
    this.lastMove = { flow: -1e9, presence: -1e9, horizon: -1e9 };
    this.held = new Set();
    this.rows = [];
    this.userTracks = (plan.music || []).map((n) => ({ id: "file:" + n, name: n.replace(/\.[^.]+$/, ""), url: `/music/${encodeURIComponent(n)}` }));
    this.dropped = [];
    this.music = null;          // { kind: "score"|"file"|"silence", id, name }
    this.peaks = 0;
    this.started = false;
    this.t0 = performance.now() / 1000;
    this.lastSample = 0; this.lastSend = 0;
    this.time = { flow: [0, 0, 0], presence: [0, 0, 0], horizon: [0, 0, 0] };   // below, usual, above (seconds)
    this.build();
  }

  send(m) { this.app.send(m); }
  clock() { const tk = this.app.tick; return tk ? +(tk.t + (performance.now() - (this.app.lastTickAt || performance.now())) / 1000).toFixed(3) : performance.now() / 1000 - this.t0; }

  // ------------------------------------------------------------------ layout
  build() {
    const el = $("booth-stage");
    el.hidden = false;
    el.innerHTML = `
      <div class="bt-sky"><i></i><i></i><i></i></div>
      <header class="bt-top">
        <div class="bt-title"><b>Listening booth</b><span id="bt-clock" class="mono">0:00</span><span id="bt-sig" class="bt-sig"></span></div>
        <div class="bt-music" id="bt-music"></div>
        <div class="bt-actions"><label class="bt-vol">Volume <input type="range" id="bt-vol" min="0" max="1" step="0.05"></label>
          <button class="ghost" id="bt-end">End</button></div>
      </header>
      <main class="bt-levers" id="bt-levers">${LEVERS.map((L) => this.leverHTML(L)).join("")}</main>
      <footer class="bt-foot">
        <button id="bt-this" class="bt-this" title="Space"><b>This!</b><small>a moment that feels most alive · Space</small></button>
        <p class="fine">Nothing here follows your brain. It is only listening. Double-click a lever to put it back to usual.</p>
      </footer>
      <div id="bt-card" class="bt-card"></div>`;
    $("bt-vol").value = (this.app.status && this.app.status.audio && this.app.status.audio.volume) ?? 0.6;
    $("bt-vol").oninput = (e) => this.setVolume(Number(e.target.value));
    $("bt-end").onclick = () => this.finish();
    $("bt-this").onclick = () => this.peak();
    LEVERS.forEach((L) => this.wireLever(L));
    this.renderMusic();
    this.keys = (e) => this.onKey(e, true); this.keysUp = (e) => this.onKey(e, false);
    window.addEventListener("keydown", this.keys, true);
    window.addEventListener("keyup", this.keysUp, true);
    this.dropH = (e) => this.onDrop(e);
    el.addEventListener("dragover", (e) => e.preventDefault());
    el.addEventListener("drop", this.dropH);
    this.intro();
    LEVERS.forEach((L) => this.paint(L.id));
  }

  leverHTML(L) {
    return `<div class="bl" data-id="${L.id}" style="--c:${L.color}">
      <div class="bl-name">${L.name}</div>
      <div class="bl-end">${L.top}</div>
      <div class="bl-track" id="bl-${L.id}">
        <div class="bl-fill"></div><div class="bl-notch"><span>usual</span></div>
        <div class="bl-handle" tabindex="0" role="slider" aria-label="${L.name}" aria-valuemin="0" aria-valuemax="100"><i></i><i></i><i></i></div>
      </div>
      <div class="bl-end">${L.bottom}</div>
      <div class="bl-keys"><kbd>${L.up.toUpperCase()}</kbd><kbd>${L.down.toUpperCase()}</kbd></div>
    </div>`;
  }

  wireLever(L) {
    const track = $(`bl-${L.id}`);
    const handle = track.querySelector(".bl-handle");
    const at = (e) => { const r = track.getBoundingClientRect(); return clamp((e.clientY - r.top) / r.height, 0, 1); };
    let drag = false;
    const down = (e) => { drag = true; track.setPointerCapture(e.pointerId); this.set(L.id, at(e), true); e.preventDefault(); };
    track.addEventListener("pointerdown", down);
    track.addEventListener("pointermove", (e) => { if (drag) this.set(L.id, at(e)); });
    track.addEventListener("pointerup", () => { drag = false; });
    track.addEventListener("pointercancel", () => { drag = false; });
    track.addEventListener("dblclick", () => this.set(L.id, 0.5, true));
    track.addEventListener("wheel", (e) => { e.preventDefault(); this.set(L.id, this.v[L.id] + Math.sign(e.deltaY) * 0.04); }, { passive: false });
    handle.addEventListener("keydown", (e) => {
      if (e.key === "ArrowDown") { this.set(L.id, this.v[L.id] + 0.05); e.preventDefault(); e.stopPropagation(); }
      if (e.key === "ArrowUp") { this.set(L.id, this.v[L.id] - 0.05); e.preventDefault(); e.stopPropagation(); }
    });
  }

  set(id, v, snap = false) {
    v = clamp(v, 0, 1);
    if (!snap && Math.abs(v - 0.5) < 0.025) v = 0.5;            // a gentle detent at "usual"
    if (Math.abs(v - this.v[id]) < 1e-4) return;
    this.v[id] = v;
    this.lastMove[id] = performance.now() / 1000;
    this.paint(id);
  }

  paint(id) {
    const v = this.v[id];
    const el = document.querySelector(`.bl[data-id="${id}"]`);
    if (!el) return;
    const top = Math.min(v, 0.5), h = Math.abs(v - 0.5);
    el.querySelector(".bl-fill").style.cssText = `top:${top * 100}%;height:${h * 100}%;opacity:${0.25 + 1.3 * h}`;
    el.querySelector(".bl-handle").style.top = `${v * 100}%`;
    el.querySelector(".bl-handle").setAttribute("aria-valuenow", Math.round(v * 100));
    el.classList.toggle("more", v > 0.5); el.classList.toggle("less", v < 0.5);
    el.classList.toggle("max", v > 0.96);
    el.style.setProperty("--glow", String(0.15 + 1.6 * Math.max(0, v - 0.5)));
  }

  // ------------------------------------------------------------------ music
  renderMusic() {
    const cur = this.music ? this.music.id : "";
    const chip = (id, name, cls = "") => `<button class="bt-chip ${cls} ${cur === id ? "on" : ""}" data-m="${esc(id)}">${esc(name)}</button>`;
    const mine = [...this.userTracks, ...this.dropped];
    $("bt-music").innerHTML = `<div class="bt-row"><span class="fine">IDA scores</span>${SCORES.map(([id, n]) => chip("score:" + id, n)).join("")}</div>
      <div class="bt-row"><span class="fine">Your music</span>${mine.length ? mine.map((m) => chip(m.id, m.name, "mine")).join("") : `<span class="fine">none yet</span>`}
        <button class="bt-chip add" id="bt-add" title="Put music files in this folder (or drop files onto this window)">+ Add</button>
        <button class="bt-chip" data-m="silence">Silence</button></div>`;
    $("bt-music").querySelectorAll("[data-m]").forEach((b) => (b.onclick = () => this.play(b.dataset.m)));
    $("bt-add").onclick = () => { this.send({ cmd: "open_music" }); this.toast("Put music files in the folder that opened, then press + Add again to refresh (or drop files on this window)."); this.send({ cmd: "music_list" }); };
  }
  setMusicList(list) {
    this.userTracks = (list || []).map((n) => ({ id: "file:" + n, name: n.replace(/\.[^.]+$/, ""), url: `/music/${encodeURIComponent(n)}` }));
    this.renderMusic();
  }
  onDrop(e) {
    e.preventDefault();
    for (const f of e.dataTransfer.files) {
      if (!f.type.startsWith("audio/")) continue;
      this.dropped.push({ id: "drop:" + f.name, name: f.name.replace(/\.[^.]+$/, ""), url: URL.createObjectURL(f) });
    }
    this.renderMusic();
  }

  ensureOut() {
    const ctx = (this.ctx = sharedContext());
    if (!ctx || this.out) return;
    const s = (this.app.status && this.app.status.audio) || {};
    this.analyser = ctx.createAnalyser(); this.analyser.fftSize = 2048;
    this.buf = new Float32Array(this.analyser.fftSize);
    this.out = ctx.createGain(); this.out.gain.value = Number($("bt-vol").value);
    this.ceiling = ctx.createGain(); this.ceiling.gain.value = dbToGain(s.max_db ?? -12);
    this.out.connect(this.analyser);
    this.out.connect(this.ceiling).connect(ctx.destination);
  }

  stopMusic() {
    if (this.snd) { try { this.snd.setVolume(0, 0.8); const s = this.snd; setTimeout(() => s.close && s.close(), 1200); } catch (e) { /* gone */ } this.snd = null; }
    if (this.audio) { this.audio.pause(); this.audio.src = ""; this.audio = null; }
    if (this.mediaSrc) { try { this.mediaSrc.disconnect(); } catch (e) { /* gone */ } this.mediaSrc = null; }
  }

  play(id) {
    unlockAudio();
    this.ensureOut();
    this.stopMusic();
    const s = (this.app.status && this.app.status.audio) || {};
    if (id.startsWith("score:")) {
      const scene = id.slice(6);
      this.snd = new LevelSound({ ...s, enabled: true, music: true, volume: Number($("bt-vol").value) }, scene, "none", 0, scene === "canon" ? "still" : scene);
      this.snd.resume();
      if (this.snd.master && this.analyser) this.snd.master.connect(this.analyser);
      this.tMusic0 = performance.now() / 1000;
      this.music = { kind: "score", id, name: SCORES.find((x) => x[0] === scene)[1] };
    } else if (id === "silence") {
      this.music = { kind: "silence", id, name: "silence" };
    } else {
      const tr = [...this.userTracks, ...this.dropped].find((m) => m.id === id);
      if (!tr) return;
      const a = (this.audio = new Audio());
      a.src = tr.url; a.crossOrigin = "anonymous";
      a.onended = () => { const all = [...this.userTracks, ...this.dropped]; const i = all.findIndex((m) => m.id === id); if (all.length) this.play(all[(i + 1) % all.length].id); };
      try { this.mediaSrc = this.ctx.createMediaElementSource(a); this.mediaSrc.connect(this.out); } catch (e) { /* plays directly */ }
      a.play().catch(() => this.toast("That file won't play here. MP3, OGG, WAV, M4A and FLAC work."));
      this.music = { kind: "file", id, name: tr.name };
    }
    this.rows.push({ t: this.clock(), event: `music:${this.music.id}`, music: this.music.id });
    this.send({ cmd: "booth_event", kind: "music", data: { music: this.music.id, name: this.music.name } });
    this.renderMusic();
  }

  setVolume(v) {
    if (this.out) this.out.gain.setTargetAtTime(v, this.ctx.currentTime, 0.1);
    if (this.snd) this.snd.setVolume(v, 0.3);
  }

  level() {
    if (!this.analyser) return 0;
    this.analyser.getFloatTimeDomainData(this.buf);
    let s = 0; for (let i = 0; i < this.buf.length; i++) s += this.buf[i] * this.buf[i];
    return Math.sqrt(s / this.buf.length);
  }

  // ------------------------------------------------------------------ cards
  card(html) { const c = $("bt-card"); c.innerHTML = html; c.classList.toggle("on", !!html); }
  toast(text) { const t = document.createElement("div"); t.className = "bt-toast"; t.textContent = text; $("booth-stage").appendChild(t); setTimeout(() => t.remove(), 5200); }

  intro() {
    this.card(`<p class="lv-num">IDA Live · listening booth</p><h2>Listen, and tell it how you feel</h2>
      <ol class="bt-steps">
        <li><b>Pick music</b> and settle in, for as long as you like. Put your own tracks in the music folder with <b>+ Add</b>.</li>
        <li>The levers start in the <b>middle: you as usual</b>. Pull one <b>down</b> when you feel more of it, push it <b>up</b> for less.</li>
        <li><b>Flow</b>: how much it flows. <b>Presence</b>: how here, how deep your focus. <b>Horizon</b>: how freely you can see ahead.</li>
        <li>Press <b>Space</b> ("This!") at a moment that feels most alive and connected.</li>
      </ol>
      <p class="fine">Mouse, touch, wheel or keys (Q/A, W/S, E/D). After a few sessions the app tells you whether your brain reading can see these feelings, or only your body can.</p>
      <div class="row center"><button class="solid" id="bt-go">Start listening</button><button class="ghost" id="bt-cancel">Not now</button></div>`);
    $("bt-go").onclick = () => { this.card(""); this.started = true; this.tStart = performance.now() / 1000; if (!this.music) this.play("score:still"); };
    $("bt-cancel").onclick = () => this.close(true);
  }

  finish() {
    if (!this.started) return this.close(true);
    const mins = (performance.now() / 1000 - this.tStart) / 60;
    this.flush();
    this.stopMusic();
    const summ = {};
    for (const L of LEVERS) { const [lo, mid, hi] = this.time[L.id]; const tot = lo + mid + hi || 1; summ[L.id] = { below: +(lo / tot).toFixed(3), usual: +(mid / tot).toFixed(3), above: +(hi / tot).toFixed(3) }; }
    this.send({ cmd: "booth_end", summary: { minutes: +mins.toFixed(2), peaks: this.peaks, levers: summ, music: this.music && this.music.id } });
    this.ended = true;
    const bars = LEVERS.map((L) => { const s = summ[L.id]; return `<tr><td>${L.name}</td><td>${Math.round(100 * s.below)}%</td><td>${Math.round(100 * s.usual)}%</td><td>${Math.round(100 * s.above)}%</td></tr>`; }).join("");
    this.card(`<p class="lv-num">Listening booth · ${Math.round(mins)} min · ${this.peaks} "this!" moment${this.peaks === 1 ? "" : "s"}</p><h2>Thank you. Working out what your brain showed…</h2>
      <table class="lv-table"><tr><th>Lever</th><th>Less</th><th>Usual</th><th>More</th></tr>${bars}</table>
      <div id="bt-verdict" class="fine">Analysing (a few seconds)…</div>
      <div class="row center"><button class="ghost" id="bt-map" disabled>Your experience map</button><button class="solid" id="bt-close">Done</button></div>`);
    $("bt-close").onclick = () => this.close();
    $("bt-map").onclick = () => { this.close(); this.app.openReport && this.app.openReport("booth"); };
  }

  done(m) {
    const host = $("bt-verdict");
    if (!host) return;
    $("bt-map").disabled = false;
    if (m.error) { host.textContent = m.error; return; }
    const lv = (m.summary && m.summary.levers) || {};
    const word = { window: "your EEG can see it", body: "your body shows it, your EEG doesn't add to it yet", emerging: "a signature is forming", nothing: "nothing yet", unmoved: "lever hardly moved" };
    host.innerHTML = Object.values(lv).map((e) => `<b>${esc(e.title)}</b>: ${esc(word[e.verdict] || e.verdict)}${e.heldout_r != null ? ` (r = ${Number(e.heldout_r).toFixed(2)})` : ""}`).join(" · ");
    const pass = Object.entries(lv).find(([, e]) => e.passes_gate);
    if (pass) {
      host.insertAdjacentHTML("beforeend", `<div class="row center"><button class="solid" id="bt-use">Let the levels reveal at my ${esc(pass[1].title)}</button></div>`);
      $("bt-use").onclick = () => { this.send({ cmd: "set_knob", path: "levels.target", value: "booth:" + pass[0] }); $("bt-use").textContent = "Done: levels now reward it"; $("bt-use").disabled = true; };
    }
  }

  // ------------------------------------------------------------------ input
  onKey(e, isDown) {
    if (e.target && e.target.matches && e.target.matches("input, select, textarea")) return;
    const k = e.key.toLowerCase();
    const L = LEVERS.find((x) => x.up === k || x.down === k);
    if (L) { e.stopPropagation(); e.preventDefault(); if (isDown) this.held.add(k); else this.held.delete(k); return; }
    if (!isDown) return;
    if (k === " ") { e.stopPropagation(); e.preventDefault(); if (this.started && !this.ended) this.peak(); return; }
    if (k === "escape") { e.stopPropagation(); e.preventDefault(); if (this.ended || !this.started || confirm("End the listening session? It is saved.")) this.started && !this.ended ? this.finish() : this.close(true); return; }
    e.stopPropagation();
  }

  peak() {
    if (!this.started || this.ended) return;
    this.peaks++;
    this.pendingPeak = true;
    this.send({ cmd: "booth_event", kind: "this", data: { flow: this.v.flow, presence: this.v.presence, horizon: this.v.horizon } });
    const b = $("bt-this"); b.classList.remove("burst"); void b.offsetWidth; b.classList.add("burst");
  }

  // ------------------------------------------------------------------ every frame
  frame(now) {
    const t = now / 1000;
    const dt = Math.min(0.1, t - (this._last || t)); this._last = t;
    for (const L of LEVERS) {
      const d = (this.held.has(L.down) ? 1 : 0) - (this.held.has(L.up) ? 1 : 0);
      if (d) this.set(L.id, this.v[L.id] + d * 0.45 * dt, true);
    }
    if (!this.started || this.ended) return;
    const el = t - this.tStart;
    $("bt-clock").textContent = `${Math.floor(el / 60)}:${String(Math.floor(el % 60)).padStart(2, "0")}`;
    if (this.snd && this.snd.ok) this.snd.update(tide(t - (this.tMusic0 || t)), 0, false, t - (this.tMusic0 || t));
    const st = this.app.tick && this.app.tick.state;
    const sig = $("bt-sig");
    const fresh = performance.now() - (this.app.lastTickAt || 0) < 2000;
    const good = fresh && st && st.clean !== false;
    sig.className = "bt-sig " + (good ? "ok" : "bad");
    sig.textContent = !fresh ? "no headband signal" : good ? "reading" : "signal unclear: relax your face, sit still";
    if (t - this.lastSample >= 0.1) {
      this.lastSample = t;
      const moving = LEVERS.some((L) => t - this.lastMove[L.id] < 0.15) ? 1 : 0;
      for (const L of LEVERS) { const v = this.v[L.id]; this.time[L.id][v < 0.47 ? 0 : v > 0.53 ? 2 : 1] += 0.1; }
      let ev = "";
      if (this.snd && this.snd.score && this.snd.score.events) { const evs = this.snd.score.events; if (evs.length > (this._musN || 0)) { ev = "music:" + evs[evs.length - 1].kind; this._musN = evs.length; } }
      this.rows.push({ t: this.clock(), flow: +this.v.flow.toFixed(3), presence: +this.v.presence.toFixed(3), horizon: +this.v.horizon.toFixed(3),
        moving, peak: this.pendingPeak ? 1 : 0, music: this.music ? this.music.id : "", music_t: this.audio ? +this.audio.currentTime.toFixed(2) : +(t - (this.tMusic0 || t)).toFixed(2),
        music_level: +this.level().toFixed(4), event: ev || (this.pendingPeak ? "this" : "") });
      this.pendingPeak = false;
    }
    if (t - this.lastSend > 1) { this.lastSend = t; this.flush(); }
  }

  flush() { if (this.rows.length) this.send({ cmd: "booth_samples", rows: this.rows.splice(0, 600) }); }

  close(early = false) {
    if (!this.ended && this.started) { this.flush(); this.send({ cmd: "booth_end", summary: { ended_early: true, peaks: this.peaks } }); }
    else if (!this.started && !this.ended) this.send({ cmd: "booth_end", summary: { ended_early: true, reason: "not started" } });
    this.ended = true;
    this.stopMusic();
    window.removeEventListener("keydown", this.keys, true);
    window.removeEventListener("keyup", this.keysUp, true);
    $("booth-stage").hidden = true; $("booth-stage").innerHTML = "";
    if (this.app.booth === this) this.app.booth = null;
    setTimeout(() => this.app.openHome && this.app.openHome(), 50);
  }
}
