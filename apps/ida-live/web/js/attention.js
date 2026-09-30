// The attention map: calibrating the app to how YOU focus.
//
// Each task makes you attend in one particular way, and checks that you did: a small light
// blinks now and then where you are meant to be attending (press Space), and decoys blink where
// you are not (ignore them). Hits, misses, reaction times and false presses label every second
// of EEG with what your attention was actually doing, so the app can learn your own signature
// of focused vs free attention, and of narrow vs broad attention, and test it on blocks it has
// not seen before it is ever allowed to reward anything.
//
//   Hold the centre   a still, sharp circle while the city moves around it   focus vs free
//   The jellyfish     the jellyfish clears while the background falls away   focus vs free
//   The summit        the climber alone, then the whole view at once        narrow vs broad

import { FS } from "./dsp.js";

const $ = (id) => document.getElementById(id);
const clamp = (x, a, b) => (x < a ? a : x > b ? b : x);
const esc = (t) => String(t ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

const VS = `#version 300 es
in vec2 a; out vec2 uv; void main() { uv = a * 0.5 + 0.5; gl_Position = vec4(a, 0.0, 1.0); }`;
const FSH = `#version 300 es
precision highp float;
in vec2 uv; out vec4 o;
uniform sampler2D uTex, uStill;
uniform vec2 uRes; uniform float uVidAspect, uBlur, uDim, uZoom, uUseStill, t;
uniform vec4 uRoi;              // centre x, y and radii, in video coordinates
uniform vec4 uDot[3];           // x, y (video coords), intensity, unused
vec2 cover(vec2 s) {
  float sa = uRes.x / uRes.y; vec2 c = (s - 0.5) * uZoom;
  if (sa > uVidAspect) c.y *= uVidAspect / sa; else c.x *= sa / uVidAspect;
  return c + 0.5;
}
void main() {
  vec2 v = cover(uv);
  v.y = 1.0 - v.y;                                       // video coordinates: y down from the top
  vec2 d = (v - uRoi.xy) / uRoi.zw;
  float inside = 1.0 - smoothstep(0.85, 1.15, length(d));
  float rad = uBlur * (1.0 - inside);
  vec3 col = vec3(0.0);
  for (int k = 0; k < 16; k++) {
    float fk = float(k), rr = sqrt((fk + 0.5) / 16.0) * rad, an = fk * 2.39996;
    vec2 off = vec2(cos(an), sin(an)) * rr * vec2(1.0 / uVidAspect, 1.0);
    col += texture(uTex, v + off).rgb;          // v is already in texture orientation (y down)
  }
  col /= 16.0;
  if (uUseStill > 0.5) col = mix(col, texture(uStill, v).rgb, inside);
  col *= 1.0 - uDim * (1.0 - inside);
  float asp = uRes.x / uRes.y;
  for (int i = 0; i < 3; i++) {
    vec2 q = (v - uDot[i].xy) * vec2(uVidAspect, 1.0);
    col += uDot[i].z * exp(-dot(q, q) / 0.00012) * vec3(1.0, 0.97, 0.85);
  }
  vec2 dv = (uv - 0.5) * vec2(asp, 1.0);
  col *= 1.0 - 0.22 * dot(dv, dv);
  o = vec4(clamp(col, 0.0, 1.0), 1.0);
}`;

function shader(gl, type, src) { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s)); return s; }

class View {
  constructor(canvas, video) {
    const gl = (this.gl = canvas.getContext("webgl2", { antialias: false, alpha: false }));
    if (!gl) throw new Error("No WebGL2");
    this.c = canvas; this.v = video;
    const pr = (this.pr = gl.createProgram());
    gl.attachShader(pr, shader(gl, gl.VERTEX_SHADER, VS)); gl.attachShader(pr, shader(gl, gl.FRAGMENT_SHADER, FSH)); gl.linkProgram(pr);
    this.buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, this.buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    const mk = () => { const t = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, t);
      for (const [p, v] of [[gl.TEXTURE_MIN_FILTER, gl.LINEAR], [gl.TEXTURE_MAG_FILTER, gl.LINEAR], [gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE], [gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE]]) gl.texParameteri(gl.TEXTURE_2D, p, v);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, 1, 1, 0, gl.RGB, gl.UNSIGNED_BYTE, new Uint8Array([0, 0, 0])); return t; };
    this.tex = mk(); this.still = mk();
    this.loc = {};
    for (const n of ["uTex", "uStill", "uRes", "uVidAspect", "uBlur", "uDim", "uZoom", "uUseStill", "t", "uRoi", "uDot"]) this.loc[n] = gl.getUniformLocation(pr, n);
    this.aLoc = gl.getAttribLocation(pr, "a");
  }
  captureStill() { const gl = this.gl; if (this.v.readyState < 2) return; gl.bindTexture(gl.TEXTURE_2D, this.still); try { gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, this.v); } catch (e) { /* not ready */ } }
  draw(s) {
    const gl = this.gl, c = this.c, v = this.v;
    const dpr = Math.min(1.5, window.devicePixelRatio || 1), W = Math.round(c.clientWidth * dpr), H = Math.round(c.clientHeight * dpr);
    if (c.width !== W || c.height !== H) { c.width = W; c.height = H; }
    gl.viewport(0, 0, W, H);
    if (v.readyState >= 2) { gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, this.tex); try { gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, v); } catch (e) { /* skip */ } }
    gl.useProgram(this.pr);
    gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, this.tex); gl.uniform1i(this.loc.uTex, 0);
    gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, this.still); gl.uniform1i(this.loc.uStill, 1);
    gl.bindBuffer(gl.ARRAY_BUFFER, this.buf); gl.enableVertexAttribArray(this.aLoc); gl.vertexAttribPointer(this.aLoc, 2, gl.FLOAT, false, 0, 0);
    gl.uniform2f(this.loc.uRes, W, H);
    gl.uniform1f(this.loc.uVidAspect, v.videoWidth && v.videoHeight ? v.videoWidth / v.videoHeight : 16 / 9);
    gl.uniform1f(this.loc.uBlur, s.blur); gl.uniform1f(this.loc.uDim, s.dim); gl.uniform1f(this.loc.uZoom, s.zoom); gl.uniform1f(this.loc.uUseStill, s.still ? 1 : 0);
    gl.uniform4f(this.loc.uRoi, ...s.roi);
    const dots = new Float32Array(12);
    s.dots.slice(0, 3).forEach((d, i) => dots.set([d.x, d.y, d.i, 0], i * 4));
    gl.uniform4fv(this.loc.uDot, dots);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }
}

// seeded random numbers, so a run's schedule can be reproduced from its logged seed
function rng(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }

export class AttentionRunner {
  constructor(app, plan) {
    this.app = app; this.tasks = plan.tasks; this.rand = rng(plan.seed || 1);
    this.ti = -1; this.bi = -1; this.phase = "loading";
    this.rows = []; this.lastSample = 0; this.lastSend = 0;
    this.trials = []; this.dots = []; this.stats = [];
    this.t0 = performance.now() / 1000;
    this.build();
  }
  now() { return performance.now() / 1000 - this.t0; }
  clock() { const tk = this.app.tick; return tk ? tk.t + (performance.now() - (this.app.lastTickAt || performance.now())) / 1000 : this.now(); }
  send(m) { this.app.send(m); }

  build() {
    const el = $("level-stage"); el.hidden = false;
    el.innerHTML = `<video id="at-video" muted playsinline loop preload="auto" crossorigin="anonymous"></video><canvas id="lv-canvas"></canvas>
      <div id="lv-card" class="lv-card"></div><div id="lv-tier" class="lv-tier"></div>
      <div id="at-cue" class="lv-hint lv-sound"></div><div id="lv-dots" class="lv-dots"></div>
      <button id="lv-skip" class="lv-skip" title="Skip this block (S or →)">Skip ›</button>`;
    document.body.classList.add("leveling");
    this.video = $("at-video");
    try { this.view = new View($("lv-canvas"), this.video); } catch (e) { this.card(`<h2>Graphics unavailable</h2><p>${esc(e.message)}</p>`, true); return; }
    $("lv-skip").onclick = (e) => { e.stopPropagation(); this.skip(); };
    this.keys = (e) => this.onKey(e); window.addEventListener("keydown", this.keys, true);
    this.card(`<p class="lv-num">Calibration</p><h1>Attention map</h1>
      <p class="lv-sub">Three short tasks teach the app how <i>your</i> attention looks: focused and free, narrow and wide.</p>
      <p class="fine">Each task tells you where to attend. A small light will blink there now and then: press <b>Space</b> as soon as you see it. Lights elsewhere are decoys; let them go. About 8 minutes. Head still and supported. S skips a block, Esc leaves.</p>
      <button class="solid" id="at-go">Begin</button>`);
    $("at-go").onclick = () => this.nextTask();
  }

  card(html, closable = false) {
    const c = $("lv-card"); c.innerHTML = html + (closable ? `<button class="solid" id="lv-close">Close</button>` : ""); c.classList.add("on");
    if (closable) $("lv-close").onclick = () => this.close();
  }
  hideCard() { $("lv-card").classList.remove("on"); }

  nextTask() {
    this.ti += 1; this.bi = -1;
    if (this.ti >= this.tasks.length) return this.finish();
    const T = (this.task = this.tasks[this.ti]);
    this.phase = "loading";
    this.video.src = T.media.url; this.video.playbackRate = 1;
    this.video.onloadeddata = () => { this.video.play().catch(() => {}); this.video.playbackRate = T.id === "attn_jelly" ? 0.6 : 0.85; this.nextBlock(); };
    this.send({ cmd: "attention_event", kind: "task", data: { task: T.id } });
  }

  nextBlock() {
    this.bi += 1;
    const T = this.task;
    if (this.bi >= T.blocks.length) return this.nextTask();
    const [cond, secs] = T.blocks[this.bi];
    this.cond = cond; this.secs = secs;
    this.phase = "instr"; this.phaseStart = this.now();
    // the full instruction the first time; after that a short cue, so the blocks can be many and short
    const first = !T.blocks.slice(0, this.bi).some(([c]) => c === cond);
    this.instrS = first ? 6 : 3;
    this.card(first ? `<p class="lv-num">${esc(T.title)} · ${this.bi + 1} of ${T.blocks.length}</p><p class="lv-sub">${esc(T.say[cond])}</p>`
      : `<p class="lv-sub">${esc((T.cue || {})[cond] || T.say[cond])}</p>`);
    $("lv-dots").innerHTML = T.blocks.map((_, i) => `<i class="${i < this.bi ? "done" : i === this.bi ? "now" : ""}"></i>`).join("");
    this.dots = [];
    this.send({ cmd: "attention_event", kind: "block_instr", data: { task: T.id, block: this.bi, cond } });
  }

  startBlock() {
    this.phase = "block"; this.phaseStart = this.now(); this.hideCard();
    if (this.task.still_centre && this.cond === "focus") this.view.captureStill();
    this.nextTarget = this.now() + 2.5 + 2 * this.rand();
    this.nextDecoy = this.now() + 4 + 4 * this.rand();
    this.blockStat = { task: this.task.id, block: this.bi, cond: this.cond, targets: 0, hits: 0, rts: [], decoys: 0, decoy_presses: 0, false_presses: 0 };
    this.stats.push(this.blockStat);
    this.send({ cmd: "attention_event", kind: "block_start", data: { task: this.task.id, block: this.bi, cond: this.cond } });
  }

  endBlock(skipped = false) {
    const b = this.blockStat;
    for (const tr of this.trials) if (tr.block === b && tr.kind === "target" && !tr.done) { tr.done = true; this.log("miss", tr.x, tr.y, null); }
    this.send({ cmd: "attention_event", kind: "block_end", data: { ...b, rts: undefined, median_rt: med(b.rts), skipped } });
    this.nextBlock();
  }

  skip() {
    if (this.phase === "instr") { this.startBlock(); return; }
    if (this.phase === "block") { this.send({ cmd: "attention_event", kind: "skip", data: { task: this.task.id, block: this.bi, after_s: +(this.now() - this.phaseStart).toFixed(1) } }); this.endBlock(true); }
  }

  // where a probe can appear: on the attended region, off it, or anywhere
  place(where) {
    const [cx, cy, rx, ry] = this.task.roi;
    for (let k = 0; k < 40; k++) {
      let x, y;
      if (where === "in") { const a = this.rand() * 6.283, r = Math.sqrt(this.rand()) * 0.6; x = cx + Math.cos(a) * r * rx; y = cy + Math.sin(a) * r * ry; }
      else { x = 0.1 + 0.8 * this.rand(); y = 0.12 + 0.76 * this.rand(); }
      const d = Math.hypot((x - cx) / rx, (y - cy) / ry);
      if (where === "in" || where === "any" || d > 1.4) return [x, y];
    }
    return [cx, cy];
  }

  spawn(kind) {
    const where = kind === "decoy" ? "out" : this.cond === "broad" ? "any" : "in";
    const [x, y] = this.place(where);
    const tr = { kind, x, y, at: this.now(), block: this.blockStat, done: false };
    this.trials.push(tr); this.dots.push(tr);
    if (kind === "target") this.blockStat.targets += 1; else this.blockStat.decoys += 1;
    this.log(kind, x, y, null);
  }

  onKey(e) {
    if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); if (confirm("Leave the attention map? What you did so far is saved.")) this.close(true); return; }
    if (e.key === "s" || e.key === "S" || e.key === "ArrowRight") { e.preventDefault(); e.stopPropagation(); this.skip(); return; }
    if (e.code === "Space") {
      e.preventDefault(); e.stopPropagation();
      if (this.phase === "instr") return;
      if (this.phase !== "block") return;
      const t = this.now();
      const cand = this.trials.filter((tr) => !tr.done && t - tr.at >= 0.15 && t - tr.at <= 1.2).sort((a, b) => b.at - a.at);
      const tg = cand.find((c) => c.kind === "target"), dc = cand.find((c) => c.kind === "decoy");
      if (tg) { tg.done = true; const rt = t - tg.at; this.blockStat.hits += 1; this.blockStat.rts.push(rt); this.log("hit", tg.x, tg.y, rt); }
      else if (dc) { dc.done = true; this.blockStat.decoy_presses += 1; this.log("decoy_press", dc.x, dc.y, t - dc.at); }
      else { this.blockStat.false_presses += 1; this.log("false_press", null, null, null); }
      return;
    }
    e.stopPropagation();
  }

  log(event, x, y, rt) {
    this.rows.push({ t: +this.clock().toFixed(3), task: this.task.id, block: this.bi, cond: this.cond, phase: this.phase, event,
      x: x === null ? null : +x.toFixed(3), y: y === null ? null : +y.toFixed(3), rt: rt === null ? null : +rt.toFixed(3),
      roi_blur: +(this.blur || 0).toFixed(4), video_t: +(this.video.currentTime || 0).toFixed(2) });
  }

  frame() {
    if (!this.view || this.phase === "loading" || this.phase === "done") return;
    const t = this.now(), el = t - this.phaseStart;
    if (this.phase === "instr" && el > (this.instrS || 6)) this.startBlock();
    if (this.phase === "block") {
      if (el > this.secs) { this.endBlock(); return; }
      const probing = this.cond !== "watch";
      if (probing && t >= this.nextTarget) { this.spawn("target"); this.nextTarget = t + 2.2 + Math.min(5, -Math.log(1 - this.rand()) * 2.2); }
      if ((this.cond === "focus" || this.cond === "narrow") && t >= this.nextDecoy) { this.spawn("decoy"); this.nextDecoy = t + 3 + Math.min(7, -Math.log(1 - this.rand()) * 3.5); }
      // unanswered targets become misses after 1.2 s
      for (const tr of this.trials) if (!tr.done && tr.kind === "target" && t - tr.at > 1.2) { tr.done = true; this.log("miss", tr.x, tr.y, null); }
      for (const tr of this.trials) if (!tr.done && tr.kind === "decoy" && t - tr.at > 1.2) tr.done = true;
    }
    // what the scene does in each condition (it helps you do what the task asks)
    const ramp = clamp((this.phase === "block" ? el : 0) / 5, 0, 1);
    const narrowing = this.cond === "focus" || this.cond === "narrow";
    const target = narrowing ? (this.task.id === "attn_centre" ? 0.012 : 0.02) * ramp : 0;
    this.blur = (this.blur ?? 0) + (target - (this.blur ?? 0)) * 0.05;
    const dim = narrowing ? 0.25 * ramp : 0;
    const zoom = this.cond === "narrow" ? 0.9 : this.cond === "broad" ? 1.0 : 1.0;
    this.zoom = (this.zoom ?? 1) + (zoom - (this.zoom ?? 1)) * 0.03;
    const dots = this.dots.map((d) => { const a = t - d.at; const i = a < 0.08 ? a / 0.08 : a < 0.15 ? 1 : a < 0.25 ? 1 - (a - 0.15) / 0.1 : 0; return { x: d.x, y: d.y, i: 0.9 * clamp(i, 0, 1) }; }).filter((d) => d.i > 0);
    this.dots = this.dots.filter((d) => t - d.at < 0.3);
    this.view.draw({ blur: this.blur, dim, zoom: this.zoom, still: !!(this.task.still_centre && this.cond === "focus" && this.phase === "block"), roi: this.task.roi, dots });
    if (t - this.lastSample > 0.25) { this.lastSample = t; this.log("", null, null, null); }
    if (t - this.lastSend > 2 && this.rows.length) { this.lastSend = t; this.send({ cmd: "attention_samples", rows: this.rows.splice(0) }); }
  }

  finish() {
    this.phase = "done";
    if (this.rows.length) this.send({ cmd: "attention_samples", rows: this.rows.splice(0) });
    const by = (cond) => this.stats.filter((b) => b.cond === cond);
    const rate = (bs) => { const n = bs.reduce((s, b) => s + b.targets, 0); return n ? bs.reduce((s, b) => s + b.hits, 0) / n : null; };
    const summary = { blocks: this.stats.map((b) => ({ ...b, median_rt: med(b.rts), rts: undefined })),
      hit_rate: { focus: rate(by("focus")), narrow: rate(by("narrow")), broad: rate(by("broad")) } };
    this.send({ cmd: "attention_end", summary });
    const f = (x) => (x === null || x === undefined ? "–" : `${Math.round(100 * x)}%`);
    this.card(`<p class="lv-num">Attention map</p><h2>Done. Working out your profile…</h2>
      <p class="fine">You caught ${f(summary.hit_rate.focus)} of the lights when focused, ${f(summary.hit_rate.narrow)} when narrow and ${f(summary.hit_rate.broad)} when wide.</p>
      <p><button class="ghost" id="at-report" disabled>Your attention profile</button></p>`, true);
  }

  profileReady() {
    const b = $("at-report"); if (!b) return;
    b.disabled = false; b.onclick = () => { this.close(); this.app.openReport && this.app.openReport("attention"); };
    const h = $("lv-card").querySelector("h2"); if (h) h.textContent = "Done. Your profile is ready.";
  }

  close(early = false) {
    window.removeEventListener("keydown", this.keys, true);
    if (early && this.phase !== "done") {
      if (this.rows.length) this.send({ cmd: "attention_samples", rows: this.rows.splice(0) });
      this.send({ cmd: "attention_end", summary: { ended_early: true, task: this.task && this.task.id, block: this.bi } });
    }
    try { this.video.pause(); } catch (e) { /* ignore */ }
    $("level-stage").hidden = true; $("level-stage").innerHTML = "";
    document.body.classList.remove("leveling");
    this.app.attention = null;
  }
}

function med(xs) { if (!xs || !xs.length) return null; const s = [...xs].sort((a, b) => a - b); return +s[Math.floor(s.length / 2)].toFixed(3); }
