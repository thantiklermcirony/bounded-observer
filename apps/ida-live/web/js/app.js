// IDA Live display: connects to the local engine, turns its stream into the live view,
// and carries your (and Claude's) commands back. Nothing here decides anything about
// the data; the engine owns the measurements, the recording and the protocols.

import { SignalHub, BANDS, FS } from "./dsp.js";
import { Renderer, Batch } from "./gl.js";
import { LENSES, BAND_COLORS, BAND_GLYPH } from "./lenses.js";
import { renderSelect, mediaProgress, LevelRunner } from "./levels.js";
import { LevelSound, outputDevices } from "./audio.js";
import { demoTrack } from "./music.js";
import { AttentionRunner } from "./attention.js";
import { BoothRunner } from "./booth.js";

const $ = (id) => document.getElementById(id);
const esc = (t) => String(t ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const fmt = (v, d = 2) => (v === undefined || v === null || Number.isNaN(v) ? "–" : Number(v).toFixed(d));

const DEFAULT_DISPLAY = {
  lens: "stream", bands: [...BANDS], amplitude: true, rainbows: true, rainbow_threshold: 0.55, hemispheres: false,
  ida: true, grid: true, speed: 1.4, gain: 1, tilt: 38, glow: 1,
};

const app = {
  ws: null, status: null, tick: null, disp: { ...DEFAULT_DISPLAY }, hub: new SignalHub(),
  tDisp: 0, trail: [], markers: [], spark: {}, knobs: [], recipes: {}, selectedRecipe: null,
  question: null, lastInput: performance.now(), connectedOnce: false, srcKind: "athena", device: null,
  phase: "nothing", claudeUntil: 0, lastTickAt: 0, lastRawAt: 0, _claudeChanges: new Map(),
};
window.ida = app; // handy for debugging in the console
app.send = (m) => send(m);

// ------------------------------------------------------------------ socket
let retry = 0;
function connectSocket() {
  const ws = new WebSocket(`ws://${location.host}/ws`);
  app.ws = ws;
  ws.onopen = () => { retry = 0; send({ cmd: "hello" }); send({ cmd: "knobs" }); send({ cmd: "recipes" }); if (app.connectedOnce) toast("Reconnected."); app.connectedOnce = true; };
  ws.onmessage = (ev) => { try { handle(JSON.parse(ev.data)); } catch (e) { console.error(e); } };
  ws.onclose = () => {
    if (app.quitting) return;
    setPrimary({ label: "Reconnecting…", sub: "The IDA Live engine isn't answering. It restarts itself if you open IDA Live again.", mode: "waiting" });
    setTimeout(connectSocket, Math.min(5000, 400 * 2 ** retry++));
  };
}
function send(msg) { if (app.ws && app.ws.readyState === 1) app.ws.send(JSON.stringify(msg)); }

function handle(m) {
  switch (m.type) {
    case "status": onStatus(m); break;
    case "tick": onTick(m); break;
    case "raw": onRaw(m); break;
    case "event": onEvent(m); break;
    case "display": onDisplay(m.display, m.by); break;
    case "question": openQuestion(m); break;
    case "question_closed": if (app.question && app.question.id === m.id) closeQuestion(); break;
    case "scan_result": onScan(m.devices); break;
    case "reveal": showReveal(m); break;
    case "recipe_reveal": showReveal({ phase: m.name, arms: m.arms }); break;
    case "knobs": app.knobs = m.knobs; renderKnobs(); break;
    case "sessions": renderSessions(m.sessions); break;
    case "levels": app.levels = m.levels; app.bests = m.bests || {}; renderSelect(app, m.levels); break;
    case "media_progress": mediaProgress(m); if (m.state === "done") { send({ cmd: "levels" }); send({ cmd: "attention_list" }); }
      if (m.level && m.level.startsWith("attn_") && $("attn-status")) $("attn-status").textContent = m.state === "downloading" ? `${m.level.slice(5)} ${m.total ? Math.round((100 * m.got) / m.total) + "%" : ""}` : m.state === "failed" ? "A download failed; see Activity." : ""; break;
    case "level_plan":
      $("levels-screen").hidden = true;
      if (app.level) app.level.close();
      app.level = new LevelRunner(app, m);
      break;
    case "level_aborted": if (app.level) app.level.close(); if (app.attention) app.attention.close(); if (app.booth && !app.booth.ended) app.booth.close(); break;
    case "booth_plan":
      closeHome(); $("levels-screen").hidden = true;
      if (app.booth) app.booth.close();
      app.booth = new BoothRunner(app, m);
      break;
    case "search_done": toast("The Search is analysed: Home › Results › The Search."); send({ cmd: "home" }); break;
    case "booth_done": if (app.booth) app.booth.done(m); else toast("Your experience map is updated (Home › Results)."); send({ cmd: "home" }); break;
    case "music_list": if (app.booth) app.booth.setMusicList(m.music); break;
    case "home": app.home = m; renderHome(); break;
    case "attention_tasks": renderAttentionCard(m.tasks); break;
    case "attention_plan":
      $("levels-screen").hidden = true;
      if (app.level) app.level.close();
      if (app.attention) app.attention.close();
      app.attention = new AttentionRunner(app, m);
      break;
    case "attention_done": if (app.attention) app.attention.profileReady(); else toast("Your attention profile is ready (Levels → What the levels did)."); break;
    case "session_detail": renderSessionDetail(m); break;
    case "session_saved": toast(`Saved ${m.name}. A plain-text summary is in its folder.`); if (app._tab === "sessions") send({ cmd: "sessions" }); break;
    case "recipes": app.recipes = m.recipes; renderRecipes(); break;
    case "serial_ports": $("tf-status").textContent = m.ports.length ? `Serial ports: ${m.ports.map((p) => `${p.device} (${p.description})`).join(", ")}` : "No serial ports found."; break;
    case "mre": if (app.status) { app.status.mre = { ...app.status.mre, ...m }; } if (app._tab === "mre") renderMre(true); break;
    case "mre_ports": app.mrePorts = m.ports; if (app._tab === "mre") renderMre(); break;
    case "log": addLog(m.text); if (m.text.includes("Test fire")) $("tf-status").textContent = m.text; break;
    case "error": toast(m.text, "error"); break;
    case "say": toast(esc(m.text), "claude", true); claudeSeen(); break;
    case "control": claudeSeen(m.cmd); break;
    case "quit": app.quitting = true; document.body.innerHTML = `<div class="modal"><div class="card glass"><h2>IDA Live has closed.</h2><p class="muted">You can close this window.</p></div></div>`; break;
  }
}

// ------------------------------------------------------------------ data in
function onStatus(m) {
  app.status = m;
  if (m.display) onDisplay(m.display, null, true);
  if (m.signal) { app.hub.setConfig(m.signal.bands, m.signal.mains_hz); app.hub.setSensors(m.signal.sensors); }
  $("control-path").textContent = m.data_dir ? `${m.data_dir}\\control` : "";
  renderStatus();
  if (app._tab === "mre" && !$("drawer").hidden) renderMre(true);
}

function onRaw(m) {
  if (!m.eeg) return;
  const rows = m.eeg.data;
  if (app.lastTotal !== undefined && m.eeg.total - rows.length > app.lastTotal + 2) {
    // gap in the stream (preset switch, Bluetooth hiccup): keep time honest with zeros marked unclean
    const gap = Math.min(FS * 5, m.eeg.total - rows.length - app.lastTotal);
    app.hub.setClean(false);
    app.hub.push(Array.from({ length: gap }, () => [0, 0, 0, 0]));
  }
  app.lastTotal = m.eeg.total;
  app.hub.push(rows);
  app.lastRawAt = performance.now();
  if (app.traceRows) { app.traceRows.push(...rows); if (app.traceRows.length > FS * 5) app.traceRows.splice(0, app.traceRows.length - FS * 5); }
}

function onTick(m) {
  app.tick = m;
  if (app.status) {
    // calibration progress arrives with every tick; keep the countdown live
    const was = app.status.calibration;
    app.status.calibration = m.calibration;
    if (!!was !== !!m.calibration) send({ cmd: "hello" });
  }
  app.lastTickAt = performance.now();
  const st = m.state || {};
  app.hub.setClean(st.clean !== false);
  if (st.x !== undefined) {
    app.trail.push({ t: m.t, x: st.x, y: st.y, clean: st.clean, residue: st.residue });
    while (app.trail.length && m.t - app.trail[0].t > 90) app.trail.shift();
  }
  const f = m.features || {};
  const vals = { phi: st.phi, lzc: st.lzc, alt: st.alt, aperiodic: f.aperiodic, d: st.d, residue: st.residue };
  for (const [k, v] of Object.entries(vals)) {
    if (v === undefined || v === null) continue;
    (app.spark[k] ||= []).push(v);
    if (app.spark[k].length > 240) app.spark[k].shift();
  }
  renderCluster(m);
  renderSignal(m);
  renderPrimary();
}

function onEvent(m) {
  const last = app.trail[app.trail.length - 1];
  if (m.kind === "knob" && m.by && m.by !== "you") toast(`<b>Claude</b>${esc(m.path)} → ${esc(JSON.stringify(m.new))}`, "claude", true);
  if (m.kind === "mark") toast(`${m.by && m.by !== "you" ? "<b>Claude</b>" : ""}Marker: ${esc(m.label)}`, m.by && m.by !== "you" ? "claude" : "", true);
  if (!last) return;
  const at = { t: last.t, x: last.x, y: last.y };
  if (m.kind === "answer" && m.question === "probe" && m.answer) app.markers.push({ ...at, kind: "probe", answer: m.answer });
  else if (m.kind === "self_caught") app.markers.push({ ...at, kind: "probe", answer: "drifting" });
  else if (m.kind === "trigger") app.markers.push({ ...at, kind: "trigger" });
  else if (m.kind === "switch" && m.trial) app.markers.push({ ...at, kind: "switch" });
  if (app.markers.length > 200) app.markers.shift();
}

function onDisplay(d, by, silent) {
  const before = { ...app.disp };
  app.disp = { ...DEFAULT_DISPLAY, ...app.disp, ...d };
  if (before.lens !== app.disp.lens) fadeCanvas();
  syncFilterControls();
  if (by && by !== "you" && !silent) {
    const changed = Object.keys(app.disp).filter((k) => JSON.stringify(before[k]) !== JSON.stringify(app.disp[k]));
    for (const k of changed) app._claudeChanges.set(k, app.disp[k]);
    clearTimeout(app._claudeT);
    app._claudeT = setTimeout(() => {
      const txt = [...app._claudeChanges].map(([k, v]) => `${k.replace("_", " ")} → ${Array.isArray(v) ? v.join(", ") : typeof v === "boolean" ? (v ? "on" : "off") : v}`).join(" · ");
      if (txt) toast(`<b>Claude</b>${esc(txt)}`, "claude", true);
      app._claudeChanges.clear();
    }, 400);
    claudeSeen();
  }
}

// ------------------------------------------------------------------ display settings
let pending = {};
let pendTimer = null;
function setDisplay(key, value) {
  app.disp[key] = value;
  pending[key] = value;
  clearTimeout(pendTimer);
  pendTimer = setTimeout(() => {
    for (const [k, v] of Object.entries(pending)) send({ cmd: "set_knob", path: `display.${k}`, value: v });
    pending = {};
  }, 250);
  syncFilterControls();
}
function setLens(lens) {
  if (!LENSES[lens] || lens === app.disp.lens) return;
  fadeCanvas();
  setDisplay("lens", lens);
}
function fadeCanvas() {
  const c = $("gl");
  c.animate([{ opacity: 0.15 }, { opacity: 1 }], { duration: 420, easing: "ease-out" });
}

function buildBandChips() {
  $("band-chips").innerHTML = BANDS.map((b) => {
    const c = BAND_COLORS[b].map((v) => Math.round(v * 255)).join(",");
    const hz = app.hub.bandsHz[b];
    return `<button data-band="${b}" style="--c: rgb(${c})"><i style="background: rgb(${c})">${BAND_GLYPH[b]}</i>${b} <small class="muted">${hz[0]}–${hz[1]} Hz</small></button>`;
  }).join("");
  $("band-chips").querySelectorAll("button").forEach((btn) => {
    btn.onclick = () => {
      const b = btn.dataset.band;
      let bands = app.disp.bands.includes(b) ? app.disp.bands.filter((x) => x !== b) : [...app.disp.bands, b];
      if (!bands.length) bands = [b];
      setDisplay("bands", BANDS.filter((x) => bands.includes(x)));
    };
  });
}
function syncFilterControls() {
  document.querySelectorAll("#lenses button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.lens === app.disp.lens)));
  document.querySelectorAll("#band-chips button").forEach((b) => b.setAttribute("aria-pressed", String(app.disp.bands.includes(b.dataset.band))));
  document.querySelectorAll("#filters [data-d]").forEach((el) => {
    const v = app.disp[el.dataset.d];
    if (el.type === "checkbox") el.checked = !!v;
    else if (document.activeElement !== el) { el.value = v; }
    const out = el.parentElement.querySelector("output");
    if (out) out.textContent = Number(el.value).toFixed(el.step < 0.1 ? 2 : el.step < 1 ? 1 : 0);
  });
}

// ------------------------------------------------------------------ render loop
const renderer = new Renderer($("gl"));
const batch = new Batch();
const labelPool = [];
let lastFrame = performance.now();
function frame(now) {
  const dt = Math.min(0.1, (now - lastFrame) / 1000);
  lastFrame = now;
  // display clock: runs smoothly in real time and is gently pulled toward the newest
  // sample minus a small buffer, so the view never stutters when packets arrive in bursts
  const target = app.hub.n - FS * 0.3;
  app.tDisp += dt * FS;
  const err = target - app.tDisp;
  if (Math.abs(err) > FS * 1.5) app.tDisp = target;
  else app.tDisp += err * Math.min(1, dt * 1.5);
  if (app.tDisp > app.hub.n) app.tDisp = app.hub.n;

  if (app.level) { try { app.level.frame(now); } catch (e) { console.error(e); } requestAnimationFrame(frame); return; }
  if (app.attention) { try { app.attention.frame(now); } catch (e) { console.error(e); } requestAnimationFrame(frame); return; }
  if (app.booth) { try { app.booth.frame(now); } catch (e) { console.error(e); } requestAnimationFrame(frame); return; }
  renderer.resize();
  batch.clear();
  const W = renderer.w, H = renderer.h, dpr = renderer.dpr;
  const ctx = {
    batch, W, H, dpr, hub: app.hub, disp: app.disp, state: app.tick ? app.tick.state : null, status: app.status,
    tDisp: app.tDisp, time: now / 1000, trail: app.trail, markers: app.markers,
    quality: app.tick && app.tick.flags ? app.tick.flags.quality : null,
    deadBand: app.status && app.status.ida ? app.status.ida.dead_band : 0.6,
  };
  let out = { labels: [], bg: { cx: W / 2, cy: H / 2, r: Math.min(W, H) / 2, disk: 1 } };
  try { out = (LENSES[app.disp.lens] || LENSES.stream)(ctx); } catch (e) { console.error(e); }
  renderer.draw(batch, { ...out.bg, t: now / 1000 });
  placeLabels(out.labels, dpr);
  if (now - (app._sparkAt || 0) > 250) { drawSparks(); app._sparkAt = now; }
  if (!$("drawer").hidden && app._tab === "signal" && now - (app._traceAt || 0) > 60) { drawTraces(); app._traceAt = now; }
  requestAnimationFrame(frame);
}
function placeLabels(labels, dpr) {
  const host = $("labels");
  while (labelPool.length < labels.length) { const s = document.createElement("span"); host.appendChild(s); labelPool.push(s); }
  labelPool.forEach((el, i) => {
    const l = labels[i];
    if (!l) { if (el.style.display !== "none") el.style.display = "none"; return; }
    el.style.display = "";
    if (el.textContent !== l.text) el.textContent = l.text;
    const cls = l.cls || "";
    if (el.className !== cls) el.className = cls;
    el.style.left = `${l.x / dpr}px`;
    el.style.top = `${l.y / dpr}px`;
  });
}

// ------------------------------------------------------------------ measures cluster
const TILES = {
  phi: { d: 0 }, lzc: { d: 3 }, alt: { d: 2 }, aperiodic: { d: 2 }, d: { d: 2 }, residue: { d: 2 },
};
function renderCluster(m) {
  const st = m.state || {}, f = m.features || {};
  const set = (k, v) => { const el = document.querySelector(`.tile[data-m="${k}"] .val b`); if (el) el.textContent = fmt(v, TILES[k] ? TILES[k].d : 2); };
  set("phi", st.phi); set("lzc", st.lzc); set("alt", st.alt); set("aperiodic", f.aperiodic);
  set("d", st.d); set("residue", st.residue);
  const rs = st.return_score || {};
  $("ret-dir").textContent = rs.S5 === undefined ? "" : rs.S5 > 0.005 ? "returning" : rs.S5 < -0.005 ? "moving away" : "steady";
  const lr = st.last_return;
  document.querySelector('.tile[data-m="return"] .val b').textContent = lr ? `${lr.seconds} s after ${lr.kind.replace("mark:", "")}` : "–";
}
function drawSparks() {
  document.querySelectorAll(".tile canvas").forEach((cv) => {
    const k = cv.parentElement.dataset.m;
    const data = app.spark[k];
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    const w = cv.clientWidth * dpr, h = cv.clientHeight * dpr;
    if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; }
    const g = cv.getContext("2d");
    g.clearRect(0, 0, w, h);
    if (!data || data.length < 2) return;
    let lo = Infinity, hi = -Infinity;
    for (const v of data) { if (v < lo) lo = v; if (v > hi) hi = v; }
    if (hi - lo < 1e-9) { hi += 1; lo -= 1; }
    const grad = g.createLinearGradient(0, 0, w, 0);
    grad.addColorStop(0, "rgba(95,227,214,0.05)"); grad.addColorStop(1, "rgba(95,227,214,0.9)");
    g.strokeStyle = grad; g.lineWidth = 1.4 * dpr; g.beginPath();
    data.forEach((v, i) => { const x = (i / 239) * w, y = h - 2 - ((v - lo) / (hi - lo)) * (h - 4); i ? g.lineTo(x, y) : g.moveTo(x, y); });
    g.stroke();
  });
}

// ------------------------------------------------------------------ status, primary action, guidance
function sourceConnected() { const s = app.status && app.status.source; return !!(s && s.connected); }
function readiness() { return app.tick && app.tick.state ? app.tick.state.readiness : undefined; }

function renderStatus() {
  const st = app.status;
  const src = st.source;
  const on = sourceConnected();
  $("conn-dot").classList.toggle("on", on);
  $("conn-name").textContent = src ? (src.name || (src.kind === "sim" ? "Simulated headband" : src.kind === "replay" ? `Replay · ${src.file || ""}` : src.kind)) + (on ? "" : " · disconnected") : "Not connected";
  if (!app._homeShown && !st.session && !app.level && !app.attention && !app.booth) { app._homeShown = true; openHome(); }
  if (!on && !app._sheetDismissed && !st.session && $("home").hidden) $("connect").hidden = false;
  if (on) { $("connect").hidden = true; $("connect-go").disabled = false; $("connect-go").textContent = "Connect"; }
  $("btn-drift").disabled = !st.session;
  $("btn-mark").disabled = !on;
  const L = st.light, running = L && !["done", "stopped"].includes(L.state);
  $("light-start").disabled = !st.session || !st.can_light || running;
  $("light-stop").disabled = !running;
  $("reveal").disabled = !(L && ["done", "stopped"].includes(L.state));
  $("light-status").textContent = !st.can_light && on ? "Light trials need the direct headband connection (or the simulator)."
    : L ? `${L.phase}: trial ${L.current} of ${L.trials} · ${L.state}${L.bench ? " · bench" : ""}` : st.session ? "" : "Start a recording first.";
  const R = st.recipe, rRun = R && R.state === "watching";
  $("rc-start").disabled = !st.session || rRun || !app.selectedRecipe;
  $("rc-stop").disabled = !rRun;
  $("rc-reveal").disabled = !(R && ["done", "stopped"].includes(R.state));
  $("rc-status").textContent = R ? `${R.name}: ${R.state}, fired ${R.fired} of ${R.max_fires} · ${R.actuator}${R.bench ? " · bench" : ""}${R.covered ? " · covered" : ""}` : st.session ? "" : "Start a recording first.";
  renderPrimary();
}

function setPrimary({ label, sub = "", mode = "", progress = null, action = null }) {
  const btn = $("primary-btn");
  $("primary-label").textContent = label;
  $("primary-sub").innerHTML = sub;
  btn.className = `primary-btn ${mode}`;
  $("pring-bar").style.strokeDashoffset = progress === null ? 97.4 : 97.4 * (1 - Math.max(0, Math.min(1, progress)));
  btn.onclick = action;
  btn.disabled = !action;
  const sw = $("primary-sub").querySelector("[data-act]");
  if (sw) sw.onclick = () => ACTIONS[sw.dataset.act]();
}
const ACTIONS = {
  recal: () => send({ cmd: "calibrate" }),
  force: () => send({ cmd: "calibrate", force: true }),
  connect: () => { app._sheetDismissed = false; $("connect").hidden = false; },
};
function mmss(s) { s = Math.max(0, Math.round(s)); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`; }

function renderPrimary() {
  const st = app.status;
  if (!st) return;
  const on = sourceConnected();
  const cal = st.calibration;
  const need = (st.min_readiness ?? 0.6);
  const ready = readiness();
  const hasRef = !!st.reference && st.reference_fits_map !== false;
  let guide = false;
  if (st.source && st.source.reconnecting) {
    setPrimary({ label: "Reconnecting to headband…", mode: "waiting", progress: null,
      sub: "The Bluetooth link dropped. IDA Live is reconnecting by itself; a running calibration or recording waits and carries on." , action: null });
  } else if (!on) {
    setPrimary({ label: "Connect headband", sub: st.source ? "The headband disconnected. Check its battery, then connect again." : "", action: ACTIONS.connect });
  } else if (st.session) {
    const secs = (app.tick ? app.tick.t : 0) - st.session.started;
    setPrimary({ label: `End recording · ${mmss(secs)}`, mode: "recording", progress: 1,
      sub: `Recording <b>${esc(st.session.label || "session")}</b>${st.session.probes ? ` · ${st.session.n_probes} probes answered` : ""}`,
      action: () => send({ cmd: "end_session" }) });
  } else if (cal && !cal.failed) {
    const got = Math.floor(cal.clean_s ?? 0), need = Math.round(cal.seconds);
    const WHY = { contact: "a sensor isn't clean", blink: "blink", movement: "head movement", muscle: "muscle", eyes: "eyes moving", "no signal": "no signal" };
    const hold = (cal.holding || []).map((r) => WHY[r] || r);
    setPrimary({ label: cal.paused ? "Calibration paused · no signal" : `Calibrating · ${got} of ${need} s`, mode: "waiting", progress: cal.progress,
      sub: cal.paused ? "Waiting for the headband's signal; it carries on by itself."
        : hold.length ? `Holding for a moment: ${hold.join(", ")}. It only counts clean seconds, so it just takes a little longer.`
        : `Collecting clean signal. Sit still, eyes open, soft gaze. (${mmss(cal.elapsed || 0)} so far, gives up at ${mmss(cal.limit || 300)})`, action: null });
  } else if (!hasRef && app.tick && app.tick.state && app.tick.state.can_calibrate === false) {
    guide = true;
    const okr = app.tick.state.sensor_ok || [0, 0, 0, 0];
    const nOk = okr.filter((r, i) => r >= (i === 0 || i === 3 ? 0.8 : 0.5)).length;
    setPrimary({ label: `Fitting · ${nOk} of 4 sensors steady`, mode: "waiting", progress: Math.min(1, (okr[1] + okr[2]) / 2 / 0.5),
      sub: `Calibrate unlocks when both forehead sensors are clean most of the time. <button class="linkish" data-act="force">Calibrate anyway</button>`, action: null });
  } else if (!hasRef) {
    const failed = cal && cal.failed ? `<span style="color:var(--warn)">${esc(cal.failed)}</span> ` : st.reference && !hasRef ? "This sensor set needs its own calibration. " : st.note ? `${esc(st.note)} ` : "";
    const okr = app.tick && app.tick.state && app.tick.state.sensor_ok;
    const skip = okr ? SENSOR.filter((_, i) => okr[i] < 0.5) : [];
    setPrimary({ label: "Calibrate", sub: `${failed}About a minute of clean signal, sitting still, eyes open, soft gaze. This becomes your frozen reference.${skip.length ? ` The ${skip.join(" and ").toLowerCase()} sensor${skip.length > 1 ? "s" : ""} will be left out (not clean enough).` : ""}`, action: () => send({ cmd: "calibrate" }) });
  } else {
    const failed = cal && cal.failed ? `<span style="color:var(--warn)">${esc(cal.failed)}</span> ` : "";
    setPrimary({ label: "Start recording", sub: `${failed}Reference ${esc(st.reference.id)} · ${esc(st.reference.created)} · <button class="linkish" data-act="recal">Recalibrate</button>`,
      action: startRecording });
    guide = ready !== undefined && ready < need;
  }
  renderGuide(guide);
  if (!$("home").hidden && performance.now() - (app._homeAt || 0) > 700) { app._homeAt = performance.now(); renderHome(); }
}
function startRecording() { send({ cmd: "start_session", label: app.sessionLabel || "", probes: true }); }

const ADVICE = {
  muscle: "spiky bursts on this sensor alone (muscle): teeth apart, jaw soft, don't lean your head on anything",
  noise: "no brain rhythm at all: press it to the skin, move hair from under it, wet it",
  poor: "swinging too much: it is loose or moving; settle the band and keep still",
  flat: "flat: no contact at all",
  loose: "picking up mains hum (the contact loosened): press it in gently; running the laptop on battery cuts the hum a lot",
  eyes: "eye movement or a blink (that is your eyes, not tension): let your gaze rest",
};
const SENSOR = ["Left ear", "Left forehead", "Right forehead", "Right ear"];
function renderGuide(show) {
  const g = $("guide");
  const q = app.tick && app.tick.flags ? app.tick.flags.quality : null;
  if (!show || !q) { g.hidden = true; return; }
  g.hidden = false;
  const bad = q.map((k, i) => [k, i]).filter(([k]) => ADVICE[k]);
  g.innerHTML = `<h4>${bad.length ? "Getting a clean signal" : "Almost there. Hold still."}</h4>
    <div class="sensors">${q.map((k, i) => `<div class="sensor ${k}"><b>${SENSOR[i]}</b>${k}</div>`).join("")}</div>
    <div class="meter"><i style="width:${Math.round((readiness() || 0) * 100)}%"></i></div>
    ${bad.length ? `<p class="fine">${bad.map(([k, i]) => `<b>${SENSOR[i]}</b> ${ADVICE[k]}`).join(". ")}.</p>` : ""}
    ${sensorSwitch(q)}`;
  const b = g.querySelector("[data-sensors]");
  if (b) b.onclick = () => setSensors(b.dataset.sensors);
}
function foreheadOnly() { const s = app.status && app.status.signal && app.status.signal.sensors; return !!s && s.length === 2 && s.includes("AF7") && s.includes("AF8"); }
function sensorSwitch(q) {
  if (foreheadOnly()) return `<p class="fine">Forehead-only mode. <button class="linkish" data-sensors="all">Use all four sensors</button></p>`;
  const OK = ["good", "ok", "interference"];
  const ears = [0, 3].some((i) => !OK.includes(q[i]));
  const fore = [1, 2].every((i) => OK.includes(q[i]));
  return ears && fore ? `<p class="fine">Ears won't settle? <button class="linkish" data-sensors="forehead">Use the forehead sensors only</button> (needs its own calibration)</p>` : "";
}
function setSensors(which) {
  const fore = which === "forehead";
  send({ cmd: "set_knob", path: "signal.sensors", value: fore ? ["AF7", "AF8"] : ["TP9", "AF7", "AF8", "TP10"] });
  send({ cmd: "set_knob", path: "state.map", value: fore ? "forehead" : "default" });
  toast(fore ? "Forehead-only mode: calibrate to make its reference." : "Using all four sensors.");
}

function renderSignal(m) {
  const ch = m.flags && m.flags.channel, q = m.flags && m.flags.quality;
  const pips = $("pips").children;
  for (let i = 0; i < 4; i++) pips[i].className = q ? q[i] : "";
  const bat = m.battery;
  $("battery").textContent = bat === null || bat === undefined ? "" : `${Math.round(bat)}%`;
  if (!ch || $("drawer").hidden || app._tab !== "signal") return;
  document.querySelectorAll("#sensor-seg button").forEach((b) => b.setAttribute("aria-pressed", String((b.dataset.sensors === "forehead") === foreheadOnly())));
  const k = (a, i) => (a ? a[i] : "–");
  $("sig-body").innerHTML = SENSOR.map((n, i) => `<tr><td>${n}</td><td class="st-${q[i]}">${q[i]}${ch.burst && ch.burst[i] ? " ·burst" : ""}</td><td>${ch.sd_uv[i]}</td><td>${k(ch.hf_kurtosis, i)}</td><td>${k(ch.hf_shared, i)}</td><td>${k(ch.lf_shared, i)}</td><td>${ch.aperiodic[i]}</td><td>${k(ch.hum_up, i)}</td></tr>`).join("");
}
function drawTraces() {
  const cv = $("traces");
  const rows = app.traceRows || (app.traceRows = []);
  const dpr = Math.min(2, window.devicePixelRatio || 1);
  const w = cv.clientWidth * dpr, h = cv.clientHeight * dpr;
  if (cv.width !== w || cv.height !== h) { cv.width = w; cv.height = h; }
  const g = cv.getContext("2d");
  g.clearRect(0, 0, w, h);
  if (rows.length < 10) return;
  const cols = ["#7C6CFF", "#3FA7FF", "#2EF2C4", "#FF5FD0"];
  for (let c = 0; c < 4; c++) {
    let mean = 0; for (const r of rows) mean += r[c]; mean /= rows.length;
    g.strokeStyle = cols[c]; g.lineWidth = dpr; g.beginPath();
    const y0 = ((c + 0.5) / 4) * h;
    rows.forEach((r, i) => { const x = (i / (FS * 5)) * w, y = y0 - ((r[c] - mean) / 100) * (h / 8); i ? g.lineTo(x, y) : g.moveTo(x, y); });
    g.stroke();
  }
}

// ------------------------------------------------------------------ toasts, log, Claude
function toast(html, kind = "", isHtml = false) {
  const el = document.createElement("div");
  el.className = `toast ${kind}`;
  if (isHtml) el.innerHTML = html; else el.textContent = html;
  $("toasts").appendChild(el);
  setTimeout(() => el.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 400 }).onfinish = () => el.remove(), kind === "error" ? 8000 : 4500);
  while ($("toasts").children.length > 4) $("toasts").firstChild.remove();
}
function addLog(text) {
  const log = $("log");
  log.textContent = (log.textContent + text + "\n").split("\n").slice(-300).join("\n");
  if (/error|could not|cannot|failed/i.test(text)) toast(text, "error");
}
function claudeSeen(cmd) {
  app.claudeUntil = performance.now() + 15000;
  $("claude-live").hidden = false;
  if (cmd) $("claude-last").textContent = `Last command from Claude: ${cmd} at ${new Date().toLocaleTimeString()}`;
}
setInterval(() => { if (performance.now() > app.claudeUntil) $("claude-live").hidden = true; }, 2000);

// ------------------------------------------------------------------ questions
const Q = {
  probe: { title: "Just before this appeared, where was your attention?",
    options: [["aware", "On what I meant to be doing", "A"], ["drifting", "It had wandered off", "W"], ["unsure", "Not sure", "N"]] },
  guess: { title: "Do you think the light was on in that trial?",
    options: [["yes", "Yes", "Y"], ["no", "No", "N"], ["unsure", "Can't tell", "U"]] },
};
function openQuestion(m) {
  const spec = Q[m.kind];
  if (!spec) return;
  app.question = m;
  $("q-title").textContent = m.kind === "guess" ? `Trial ${m.trial}. ${spec.title}` : spec.title;
  $("q-buttons").innerHTML = "";
  spec.options.forEach(([value, label, key]) => {
    const b = document.createElement("button");
    b.className = value;
    b.innerHTML = `${label}<kbd>${key}</kbd>`;
    b.onclick = () => answer(value);
    $("q-buttons").appendChild(b);
  });
  $("q-hint").textContent = "Answer by clicking or with the key shown. It closes by itself after 30 seconds.";
  $("question").hidden = false;
  document.body.classList.remove("cinema");
}
function answer(value) { if (!app.question) return; send({ cmd: "answer", id: app.question.id, value }); closeQuestion(); }
function closeQuestion() { app.question = null; $("question").hidden = true; }
function showReveal(m) {
  $("rv-title").textContent = `Allocation · ${m.phase}${m.bench ? " · bench" : ""}`;
  $("rv-list").innerHTML = m.arms.map((a) => `<li>${a === "active" ? "Light on" : "Sham"}</li>`).join("");
  $("reveal-panel").hidden = false;
}
$("rv-close").onclick = () => ($("reveal-panel").hidden = true);

const INFO = {
  candidates: `<h3>Awareness candidates</h3>
    <p>Four ways of reading awareness from the raw signal, each computed live on every clean moment. None is assumed to work: your thought-probe answers test every one of them on the same pre-declared rule (docs/GATE.md, version 2), and the report says which earn their place.</p>
    <ul><li><b>Φ information rate</b>: the entropy rate of the EEG in bits per second, the observer rate of the Murray Reality Equation (estimated here with Lempel-Ziv; the paper specifies CTW on frontal EEG, not yet implemented).</li>
    <li><b>Complexity (LZ)</b>: Lempel–Ziv complexity, the most used marker of conscious level; it falls in sleep and anaesthesia.</li>
    <li><b>EEG alternation</b>: switch minus stay of the EEG's own binarized signal at 20 Hz, in (−1, 1). A proxy only: the MRE's δ is the alternation bias of an external random source (a Geiger counter), which the app does not have yet.</li>
    <li><b>1/f exponent</b>: how steeply power falls with frequency; flatter when more aroused.</li></ul>`,
  ida: `<h3>IDA</h3>
    <p><b>Displacement</b> is your hyperbolic distance from the frozen reference. <b>Residue</b> is the leaky memory of displacement left outside the dead band (IDA and the Boundedness Engine, section 6): it builds while you stay away and drains as you return. The direction under it is the return score over 5 seconds. <b>Last return</b> is how long you took to come back inside the return radius after a probe, a marker or a trigger.</p>`,
};
document.querySelectorAll(".info").forEach((b) => (b.onclick = () => { $("info-body").innerHTML = INFO[b.dataset.info]; $("info-panel").hidden = false; }));
$("info-close").onclick = () => ($("info-panel").hidden = true);

// ------------------------------------------------------------------ connect sheet
document.querySelectorAll("#src-seg button").forEach((b) => (b.onclick = () => {
  app.srcKind = b.dataset.src;
  document.querySelectorAll("#src-seg button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
  $("src-athena").hidden = app.srcKind !== "athena";
  $("src-replay").hidden = app.srcKind !== "replay";
}));
$("scan").onclick = () => { $("scan").disabled = true; $("scan").textContent = "Searching…"; send({ cmd: "scan" }); };
function onScan(devices) {
  $("scan").disabled = false; $("scan").textContent = "Search again";
  $("devices").innerHTML = devices.length
    ? devices.map((d, i) => `<button data-addr="${esc(d.address)}" aria-pressed="${i === 0}"><span>${esc(d.name)}</span><span class="muted">${esc(d.address)}</span></button>`).join("")
    : `<p class="muted">No headband found. Is it switched on, charged, and not connected to your phone?</p>`;
  app.device = devices.length ? devices[0].address : null;
  $("devices").querySelectorAll("button").forEach((b) => (b.onclick = () => {
    app.device = b.dataset.addr;
    $("devices").querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
  }));
}
$("connect-go").onclick = () => {
  const msg = { cmd: "connect", kind: app.srcKind };
  if (app.srcKind === "athena") {
    if (!app.device) return toast("Find your headband first.");
    msg.address = app.device;
  }
  if (app.srcKind === "replay") msg.path = $("replay-path").value;
  app.hub.reset(); app.tDisp = 0; app.lastTotal = undefined; app.trail = [];
  send(msg);
  const btn = $("connect-go");
  btn.disabled = true; btn.textContent = "Connecting…";
  setTimeout(() => { btn.disabled = false; btn.textContent = "Connect"; }, 15000);
};
$("connect-cancel").onclick = () => { $("connect").hidden = true; app._sheetDismissed = true; };
$("conn-chip").onclick = () => { if (sourceConnected()) openDrawer("signal"); else ACTIONS.connect(); };

// ------------------------------------------------------------------ top bar, filters, drawer
document.querySelectorAll("#lenses button").forEach((b) => (b.onclick = () => setLens(b.dataset.lens)));
$("btn-filters").onclick = () => toggleTray();
function toggleTray(force) {
  const t = $("filters");
  t.hidden = force === undefined ? !t.hidden : !force;
  $("btn-filters").setAttribute("aria-expanded", String(!t.hidden));
  if (!t.hidden) closeDrawer();
}
document.querySelectorAll("#filters [data-d]").forEach((el) => {
  el.addEventListener("input", () => setDisplay(el.dataset.d, el.type === "checkbox" ? el.checked : Number(el.value)));
});
$("btn-control").onclick = () => ($("drawer").hidden ? openDrawer(app._tab || "knobs") : closeDrawer());
$("drawer-close").onclick = () => closeDrawer();
function openDrawer(tab) {
  $("drawer").hidden = false; toggleTray(false);
  $("btn-control").setAttribute("aria-expanded", "true");
  selectTab(tab);
  send({ cmd: "knobs" }); send({ cmd: "recipes" });
}
function closeDrawer() { $("drawer").hidden = true; $("btn-control").setAttribute("aria-expanded", "false"); }
function selectTab(tab) {
  app._tab = tab;
  document.querySelectorAll(".tabs button").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.tab === tab)));
  document.querySelectorAll(".drawer .tab").forEach((s) => (s.hidden = s.dataset.tab !== tab));
  if (tab === "signal") app.traceRows = app.traceRows || [];
  if (tab === "sessions") send({ cmd: "sessions" });
  if (tab === "sound") renderSound();
  if (tab === "mre") { renderMre(); send({ cmd: "mre_ports" }); }
}

// ------------------------------------------------------------------ sound settings
async function renderSound() {
  const a = (app.status && app.status.audio) || {};
  $("au-enabled").checked = a.enabled !== false;
  $("au-volume").value = a.volume ?? 0.5; $("au-volume-v").textContent = Math.round(100 * (a.volume ?? 0.5)) + "%";
  $("au-max").value = a.max_db ?? -12; $("au-max-v").textContent = `${a.max_db ?? -12} dB`;
  $("au-pacer").value = a.pacer_bpm ?? 6; $("au-pacer-v").textContent = `${a.pacer_bpm ?? 6} per minute`;
  $("au-entrain").value = a.entrain || "sealed";
  const devs = await outputDevices();
  $("au-device").innerHTML = `<option value="">System default</option>` + devs.filter((d) => d.id && d.id !== "default").map((d) => `<option value="${d.id}">${d.label}</option>`).join("");
  $("au-device").value = a.device || "";
  $("au-note").textContent = devs.some((d) => d.label && !d.label.startsWith("Output")) ? "" : "Device names are hidden by the browser; the system default is whatever Windows is using.";
}
const auSet = (path, value) => send({ cmd: "set_knob", path, value });
$("au-enabled").onchange = (e) => auSet("audio.enabled", e.target.checked);
$("au-volume").oninput = (e) => { $("au-volume-v").textContent = Math.round(100 * e.target.value) + "%"; if (app.level && app.level.snd) app.level.snd.setVolume(Number(e.target.value)); };
$("au-volume").onchange = (e) => auSet("audio.volume", Number(e.target.value));
$("au-max").onchange = (e) => { $("au-max-v").textContent = `${e.target.value} dB`; auSet("audio.max_db", Number(e.target.value)); };
$("au-pacer").onchange = (e) => { $("au-pacer-v").textContent = `${e.target.value} per minute`; auSet("audio.pacer_bpm", Number(e.target.value)); };
$("au-entrain").onchange = (e) => auSet("audio.entrain", e.target.value);
$("au-device").onchange = (e) => auSet("audio.device", e.target.value);
$("au-test").onclick = () => LevelSound.test((app.status && app.status.audio) || {});
// a guided preview of a level's music (no headband needed)
let demo = null;
$("au-demo").onclick = () => {
  if (demo) { clearInterval(demo.iv); demo.snd.close(); demo = null; $("au-demo").textContent = "Play preview"; $("au-demo-state").textContent = ""; return; }
  const snd = new LevelSound({ ...((app.status && app.status.audio) || {}), enabled: true }, $("au-scene").value, "none", 0, $("au-scene").value === "canon" ? "bloom" : $("au-scene").value);
  snd.resume();
  const t0 = performance.now() / 1000, f = ((app.status && app.status.audio && app.status.audio.pacer_bpm) || 6) / 60;
  let prev = -1;
  demo = { snd, iv: setInterval(() => {
    const t = performance.now() / 1000 - t0;
    const w = demoTrack(t, prev); prev = t;
    snd.update(w, 2 * Math.PI * f * t, true, t);
    $("au-demo-state").textContent = `${Math.floor(t)} s · tier ${w.tier} · ${w.F > 0.6 ? "in the corridor" : w.F > 0.3 ? "arriving" : "waiting"}${w.l > 0.5 ? " · strain" : ""}${t > 58 && t < 63 ? " · knock" : ""}`;
    if (t > 95) $("au-demo").click();
  }, 50) };
  $("au-demo").textContent = "Stop";
  window.__idaDemo = demo;
};
app.demoMusic = () => $("au-demo").click();

// ------------------------------------------------------------------ MRE: random bits against Φ
function renderMre(liveOnly = false) {
  const st = (app.status && app.status.mre) || {};
  if (!liveOnly) {
    const cfg = (app.status && app.status.mre) || {};
    $("mre-source").value = cfg.source || "off";
    $("mre-control").value = cfg.control || "off";
    $("mre-keep").checked = cfg.keep_running !== false;
    const ports = app.mrePorts || [];
    const cur = (app.knobs || []).find((k) => k.path === "mre.port");
    $("mre-port").innerHTML = `<option value="auto">Find it automatically</option>` + ports.map((p) => `<option value="${esc(p.device)}">${esc(p.device)} · ${esc(p.description)}</option>`).join("");
    $("mre-port").value = (cur && cur.value) || "auto";
    const mode = (app.knobs || []).find((k) => k.path === "mre.mode");
    $("mre-mode").value = (mode && mode.value) || "raw";
  }
  const lg = st.loggers || {};
  const line = (t, s) => {
    if (!s) return "";
    const th = s.theta ? Object.entries(s.theta).map(([k, v]) => `${"AB"[k]} ${Number(v).toFixed(1)}`).join(", ") : "being set (5 min of automation)";
    const h = (n) => (n / 36000).toFixed(1);
    const state = s.state === "running" ? "logging" : s.state;
    return `<div class="mre-arm"><b>${t === "main" ? "Device under test" : "Control arm"}</b> · ${esc(s.source || "")} · <span class="${s.state === "error" ? "bad" : ""}">${esc(state)}</span>
      ${s.error ? `<div class="fine bad">${esc(s.error)}</div>` : ""}
      <div class="fine mono">automation ${h(s.c1)} h · attention ${h(s.c2)} h · other ${h(s.idle)} h · ${s.rate_bps} bit/s · median ${th}${s.p1 != null ? ` · share of ones ${s.p1}` : ""}${s.short ? ` · ${s.short} short bins` : ""}</div></div>`;
  };
  const feats = (app.tick && app.tick.features) || {};
  $("mre-live").innerHTML = (line("main", lg.main) + line("control", lg.control)) || `<p class="fine">Nothing is logging. Choose a device above.</p>`;
  $("mre-live").insertAdjacentHTML("beforeend", `<p class="fine mono">Your Φ now: ${feats.phi_ctw != null ? Math.round(feats.phi_ctw) + " bit/s (10 s average)" : "no headband signal"}</p>`);
}
$("mre-source").onchange = (e) => send({ cmd: "set_knob", path: "mre.source", value: e.target.value });
$("mre-control").onchange = (e) => send({ cmd: "set_knob", path: "mre.control", value: e.target.value });
$("mre-port").onchange = (e) => send({ cmd: "set_knob", path: "mre.port", value: e.target.value });
$("mre-mode").onchange = (e) => send({ cmd: "set_knob", path: "mre.mode", value: e.target.value });
$("mre-keep").onchange = (e) => send({ cmd: "set_knob", path: "mre.keep_running", value: e.target.checked });
$("mre-rescan").onclick = () => send({ cmd: "mre_ports" });
$("mre-report").onclick = () => openReport("mre");
setInterval(() => { if (app._tab === "mre" && !$("drawer").hidden) send({ cmd: "mre_status" }); }, 2000);
document.querySelectorAll(".tabs button").forEach((b) => (b.onclick = () => selectTab(b.dataset.tab)));
$("btn-full").onclick = () => (document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen());
$("btn-quit").onclick = () => { if (confirm("Quit IDA Live? Any recording in progress is saved first.")) send({ cmd: "quit" }); };
$("btn-drift").onclick = () => { send({ cmd: "self_caught" }); toast("Noted: you caught yourself drifting."); };
$("btn-mark").onclick = () => {
  const label = prompt("Marker label (e.g. eyes closed, music on)", "");
  if (label !== null) send({ cmd: "mark", label: label || "mark" });
};

// ------------------------------------------------------------------ home: one place to start everything
function openHome() {
  if (app.level || app.attention || app.booth) return;
  $("home").hidden = false; closeDrawer(); toggleTray(false); $("levels-screen").hidden = true;
  send({ cmd: "home" });
  renderHome();
}
function closeHome() { $("home").hidden = true; }
app.openHome = openHome;
const VERDICT = { window: "your EEG sees it", body: "body, not brain (yet)", emerging: "forming", nothing: "nothing yet", unmoved: "lever not moved" };
function renderHome() {
  const st = app.status;
  if (!st || $("home").hidden) return;
  const on = sourceConnected();
  const cal = st.calibration && !st.calibration.failed ? st.calibration : null;
  const hasRef = !!st.reference && st.reference_fits_map !== false;
  const ts = app.tick && app.tick.state;
  const okr = (ts && ts.sensor_ok) || [0, 0, 0, 0];
  const nOk = okr.filter((r, i) => r >= (i === 0 || i === 3 ? 0.8 : 0.5)).length;
  const sigOk = on && ts && (ts.can_calibrate || hasRef);
  const step = (n, done, title, body, btn) => `<li class="${done ? "done" : ""}"><span class="n">${done ? "✓" : n}</span><div><b>${title}</b><span>${body}</span></div>${btn || ""}</li>`;
  const stepsHTML =
    step(1, on, "Headband", on ? esc((st.source && st.source.name) || "connected") : "Switch it on, then connect.", on ? "" : `<button class="solid" data-h="connect">Connect</button>`) +
    step(2, sigOk, "Signal", !on ? "After connecting." : `${sigOk ? `${nOk} of 4 sensors steady` : `Settling: ${nOk} of 4 sensors steady`}${sensorWords()}`, "") +
    step(3, hasRef && !cal, "Calibrate", cal ? `Collecting clean signal · ${Math.floor(cal.clean_s || 0)} of ${Math.round(cal.seconds)} s. Sit still, soft gaze.` : hasRef ? `Done ${esc(st.reference.created || "")} · <button class="linkish" data-h="recal">redo</button>` : "One quiet minute, eyes open. It becomes your personal baseline.",
      !hasRef && !cal && on ? `<button class="solid" data-h="cal" ${sigOk ? "" : "disabled"}>Calibrate</button>` : "");
  // only touch the DOM when something changed, so a button is never replaced under the pointer
  if (stepsHTML !== app._stepsHTML) { app._stepsHTML = stepsHTML; $("home-steps").innerHTML = stepsHTML; }
  const ready = on && hasRef && !cal;
  const H = app.home || {};
  const b = H.booth;
  const boothStatus = b ? Object.values(b.levers || {}).map((l) => `${esc(l.title)}: ${VERDICT[l.verdict] || "–"}`).join(" · ") : "Not yet. Two or three sessions teach it the most.";
  const att = H.attention ? `Made ${esc(H.attention.made)} · ${Object.entries(H.attention.gate || {}).map(([k, v]) => `${k} ${v ? "passed" : "not passed"}`).join(", ")}` : "Not yet (8 minutes).";
  const tgt = H.target && H.target !== "auto" ? `Levels reward your ${esc(H.target.split(":")[1])}.` : `${H.level_sessions || 0} level session${H.level_sessions === 1 ? "" : "s"} so far.`;
  const door = (id, title, body, status, enabled) => `<button class="door ${id}" data-door="${id}" ${enabled ? "" : "disabled"}>
      <i class="art"></i><b>${title}</b><span>${body}</span><small>${enabled ? status : "Connect and calibrate first"}</small></button>`;
  const doorsHTML =
    door("booth", "Listening booth", "Music and three levers: Flow, Presence, Horizon. Your brain is simply read, and learns what your feelings look like.", boothStatus, ready) +
    door("attention", "Attention map", "Three short tasks that teach the app how you focus, checked with lights you catch.", att, ready) +
    door("search", "The Search", "Eight one-minute rounds that test seven ideas of what a clear mind is, against how clear you feel and how clearly you see.", H.search ? `${H.search.searches} done · leader: ${esc(H.search.top)} (${esc(H.search.status)})` : "Not yet (about 12 minutes).", ready) +
    door("levels", "Levels", "Real footage that your brain drives. Each one is a sealed test with a secret replay round.", tgt, ready) +
    door("results", "Results", "What the data says: your experience map, attention profile, levels and the random-bit test.", "Always available", true);
  if (doorsHTML !== app._doorsHTML) { app._doorsHTML = doorsHTML; $("home-doors").innerHTML = doorsHTML; }
  $("home-steps").querySelectorAll("[data-h]").forEach((x) => (x.onclick = () => ({ connect: () => { app._sheetDismissed = false; $("connect").hidden = false; }, cal: () => send({ cmd: "calibrate" }), recal: () => send({ cmd: "calibrate" }) })[x.dataset.h]()));
  $("home-doors").querySelectorAll("[data-door]").forEach((x) => (x.onclick = () => DOORS[x.dataset.door]()));
}
// each sensor in plain words, only when something is off (so the page stays quiet when all is well)
function sensorWords() {
  const q = app.tick && app.tick.flags && app.tick.flags.quality;
  if (!q) return "";
  const W = { loose: "loose (mains hum)", noise: "not reading", poor: "moving", flat: "no contact", muscle: "muscle", eyes: "eyes" };
  const bad = q.map((k, i) => (W[k] ? `${SENSOR[i].toLowerCase()}: ${W[k]}` : null)).filter(Boolean);
  const hum = q.some((k) => k === "loose") ? " Tip: unplug the laptop charger; mains hum reaches the ear sensors through it." : "";
  return bad.length ? `<br><span class="fine">${bad.join(" · ")}.${hum}</span>` : "";
}
const DOORS = {
  booth: () => send({ cmd: "booth_start" }),
  search: () => send({ cmd: "search_start" }),
  attention: () => { closeHome(); openLevels(); },
  levels: () => { closeHome(); openLevels(); },
  results: () => { $("results-pick").hidden = false; },
};
$("btn-home").onclick = () => ($("home").hidden ? openHome() : closeHome());
$("home-close").onclick = closeHome;
$("home-settings").onclick = () => { closeHome(); openDrawer("knobs"); };
$("home-mre").onclick = () => { closeHome(); openDrawer("mre"); };
$("home-record").onclick = () => { closeHome(); if (app.status && app.status.reference && !app.status.session) startRecording(); };
$("results-close").onclick = () => ($("results-pick").hidden = true);
document.querySelectorAll("#results-pick [data-r]").forEach((b) => (b.onclick = () => { $("results-pick").hidden = true; openReport(b.dataset.r); }));

// levels
function openLevels() {
  $("levels-screen").hidden = false;
  closeDrawer(); toggleTray(false);
  send({ cmd: "levels" });
  send({ cmd: "attention_list" });
}
$("btn-levels").onclick = openLevels;

// the attention map card: calibration that teaches the app how you focus
function renderAttentionCard(tasks) {
  const host = $("attn-card");
  const ready = tasks.every((t) => t.media.ready);
  host.innerHTML = `<div class="lvl-card attn"><div class="lvl-body">
    <p class="lv-num">Start here · calibration</p><h3>Attention map</h3>
    <p class="lvl-sub">Three short tasks (${tasks.map((t) => t.title).join(", ")}) that force your attention into focused, free, narrow and wide, and check it with a light you catch with Space. It learns your own signature of each, and tests it on blocks it hasn't seen, so levels only reward what really tracks your attention.</p>
    <div class="row">${ready ? `<button class="solid" id="attn-go">Start (8 min)</button>` : `<button class="ghost" id="attn-get">Get footage</button>`}
    <button class="ghost" id="attn-rep">Your profile</button><span class="fine" id="attn-status"></span></div></div></div>`;
  if ($("attn-go")) $("attn-go").onclick = () => send({ cmd: "attention_start" });
  if ($("attn-get")) $("attn-get").onclick = () => { $("attn-get").disabled = true; $("attn-status").textContent = "Downloading…"; tasks.filter((t) => !t.media.ready).forEach((t) => send({ cmd: "media_fetch", level: t.id })); };
  $("attn-rep").onclick = () => openReport("attention");
}
$("levels-close").onclick = () => ($("levels-screen").hidden = true);
// results: what the levels did (worked out from the saved recordings, on this computer)
export function openReport(which = "levels") {
  $("report-frame").src = `/report/${which}?t=${Date.now()}`;
  $("report-screen").hidden = false;
}
app.openReport = openReport;
$("levels-results").onclick = () => openReport("levels");
$("report-close").onclick = () => { $("report-screen").hidden = true; $("report-frame").src = "about:blank"; };

// sessions
function renderSessions(list) {
  $("sess-list").innerHTML = list.map((r) => `<li data-name="${esc(r.name)}" tabindex="0"><b>${esc(r.name.replace(/^\d{4}-\d\d-\d\d_\d{6}_/, ""))}</b><span>${esc(r.started || "")}${r.ended ? "" : " · not closed"}${r.probes ? ` · ${r.probes} probes` : ""}</span></li>`).join("")
    || `<li class="bad"><span>No recordings yet.</span></li>`;
  $("sess-list").querySelectorAll("li[data-name]").forEach((li) => (li.onclick = () => {
    $("sess-list").querySelectorAll("li").forEach((x) => x.setAttribute("aria-selected", String(x === li)));
    send({ cmd: "session_detail", name: li.dataset.name });
  }));
}
function renderSessionDetail(m) {
  $("sess-detail").hidden = false;
  $("sess-title").textContent = m.name;
  $("sess-summary").textContent = m.summary || "";
  const host = $("sess-charts");
  host.innerHTML = Object.entries(m.measures).map(([k, v]) => `<div class="sess-chart"><b>${esc(v.label)}</b><canvas data-k="${k}"></canvas></div>`).join("");
  requestAnimationFrame(() => host.querySelectorAll("canvas").forEach((cv) => {
    const d = m.measures[cv.dataset.k];
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    const w = (cv.width = cv.clientWidth * dpr), h = (cv.height = cv.clientHeight * dpr);
    const g = cv.getContext("2d");
    const vals = d.v.filter((x) => x !== null);
    if (vals.length < 2) return;
    let lo = Math.min(...vals), hi = Math.max(...vals);
    if (hi - lo < 1e-9) { hi += 1; lo -= 1; }
    const T = d.t[d.t.length - 1] || 1;
    const X = (t) => (t / T) * w, Y = (v) => h - 4 - ((v - lo) / (hi - lo)) * (h - 8);
    for (const e of m.events) {
      g.fillStyle = e.kind === "probe" ? (e.answer === "aware" ? "rgba(98,242,139,0.7)" : e.answer === "drifting" ? "rgba(255,111,168,0.7)" : "rgba(200,200,200,0.4)") : "rgba(95,227,214,0.45)";
      g.fillRect(X(e.t) - dpr / 2, 0, dpr, h);
    }
    g.strokeStyle = "rgba(234,241,255,0.85)"; g.lineWidth = 1.2 * dpr; g.beginPath();
    let pen = false;
    d.v.forEach((v, i) => { if (v === null) { pen = false; return; } const x = X(d.t[i]), y = Y(v); pen ? g.lineTo(x, y) : g.moveTo(x, y); pen = true; });
    g.stroke();
    g.fillStyle = "rgba(234,241,255,0.45)"; g.font = `${10 * dpr}px system-ui`;
    g.fillText(hi.toFixed(2), 4, 11 * dpr); g.fillText(lo.toFixed(2), 4, h - 4);
  }));
}
document.querySelectorAll("#sensor-seg button").forEach((b) => (b.onclick = () => setSensors(b.dataset.sensors)));
$("sess-refresh").onclick = () => send({ cmd: "sessions" });
$("sess-open").onclick = () => send({ cmd: "open_folder" });

// knobs
function renderKnobs() {
  const qy = $("knob-search").value.trim().toLowerCase();
  const rows = app.knobs.filter((k) => !qy || k.path.toLowerCase().includes(qy) || (k.description || "").toLowerCase().includes(qy));
  let group = "";
  $("knob-list").innerHTML = rows.map((k) => {
    const head = k.group !== group ? `<div class="group">${esc((group = k.group))}</div>` : "";
    return head + knobRow(k);
  }).join("") || `<p class="fine">No knob matches.</p>`;
  $("knob-list").querySelectorAll("[data-knob]").forEach((el) => {
    el.onchange = () => send({ cmd: "set_knob", path: el.dataset.knob, value: el.type === "checkbox" ? el.checked : el.value });
  });
}
function knobRow(k) {
  const name = k.path.split(".").slice(1).join(".") || k.path;
  let input;
  if (k.choices) input = `<select data-knob="${esc(k.path)}">${k.choices.map((c) => `<option ${String(c) === String(k.value) ? "selected" : ""}>${esc(c)}</option>`).join("")}</select>`;
  else if (k.type === "bool") input = `<label class="tog"><input type="checkbox" data-knob="${esc(k.path)}" ${k.value ? "checked" : ""}></label>`;
  else if (k.type === "number") input = `<input type="number" data-knob="${esc(k.path)}" value="${esc(k.value)}" ${k.min !== null ? `min="${k.min}"` : ""} ${k.max !== null ? `max="${k.max}"` : ""} step="${k.step || "any"}">`;
  else input = `<input type="text" data-knob="${esc(k.path)}" value="${esc(k.value ?? "")}">`;
  return `<div class="knob"><span class="k">${esc(name)}<small>${esc(k.description || "")}${k.applies && k.applies !== "now" ? ` · applies ${esc(k.applies)}` : ""}</small></span>${input}</div>`;
}
$("knob-search").oninput = renderKnobs;
$("knobs-save").onclick = () => send({ cmd: "save_knobs" });

// recipes
function renderRecipes() {
  const list = Object.values(app.recipes);
  $("recipe-list").innerHTML = list.map((r) => r._error
    ? `<li class="bad"><b>${esc(r.name)}</b><span>Cannot load ${esc(r._file)}: ${esc(r._error)}</span></li>`
    : `<li data-name="${esc(r.name)}" aria-selected="${r.name === app.selectedRecipe}" tabindex="0"><b>${esc(r.name)}</b><span>${esc(r.description || "")} · ${esc(r.actuator)} · real on ${Math.round(100 * r.randomize)}% of triggers</span></li>`).join("")
    || `<li class="bad"><span>No recipes yet.</span></li>`;
  $("recipe-list").querySelectorAll("li[data-name]").forEach((li) => {
    li.onclick = () => {
      app.selectedRecipe = li.dataset.name;
      const r = app.recipes[app.selectedRecipe];
      $("rc-text").value = JSON.stringify(Object.fromEntries(Object.entries(r).filter(([k]) => !k.startsWith("_"))), null, 1);
      renderRecipes();
      if (app.status) renderStatus();
    };
  });
}
$("rc-start").onclick = () => send({ cmd: "recipe_start", name: app.selectedRecipe, bench: $("rc-bench").checked, covered: $("rc-covered").checked });
$("rc-stop").onclick = () => send({ cmd: "recipe_stop" });
$("rc-reveal").onclick = () => { if (confirm("Reveal which triggers were real? Stop watching for the effect first.")) send({ cmd: "recipe_reveal" }); };
$("rc-save").onclick = () => {
  try { JSON.parse($("rc-text").value); } catch (e) { return toast(`That is not valid JSON: ${e.message}`, "error"); }
  send({ cmd: "save_recipe", text: $("rc-text").value });
};
// light trials
document.querySelectorAll("#phase-seg button").forEach((b) => (b.onclick = () => {
  app.phase = b.dataset.phase;
  document.querySelectorAll("#phase-seg button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
}));
$("light-start").onclick = () => send({ cmd: "light_start", phase: app.phase, bench: $("bench").checked });
$("light-stop").onclick = () => send({ cmd: "light_stop" });
$("reveal").onclick = () => { if (confirm("Reveal which trials had the light on? Only after you have finished guessing.")) send({ cmd: "reveal" }); };
// test fire
$("tf-fire").onclick = () => {
  let pattern;
  try { pattern = JSON.parse($("tf-pattern").value); } catch (e) { return toast(`Pattern is not valid JSON: ${e.message}`, "error"); }
  $("tf-status").textContent = "Firing…";
  send({ cmd: "test_fire", actuator: $("tf-actuator").value, pattern, sham: $("tf-sham").checked });
};
$("tf-ports").onclick = () => send({ cmd: "serial_ports" });

// ------------------------------------------------------------------ keyboard, cinema mode
document.addEventListener("keydown", (e) => {
  if (e.target.matches("input, textarea, select")) return;
  const k = e.key.toLowerCase();
  if (app.question) {
    const spec = Q[app.question.kind];
    const opt = spec.options.find((o, i) => o[2].toLowerCase() === k || String(i + 1) === k);
    if (opt) { e.preventDefault(); answer(opt[0]); }
    return;
  }
  const lenses = ["stream", "tunnel", "map", "aurora", "web"];
  if (/^[1-5]$/.test(k)) setLens(lenses[Number(k) - 1]);
  else if (k === "f") toggleTray();
  else if (k === "l") openLevels();
  else if (k === "g") openHome();
  else if (k === "k") $("btn-control").onclick();
  else if (k === "h") document.body.classList.toggle("bare");
  else if (k === "d" && app.status && app.status.session) $("btn-drift").onclick();
  else if (k === "m" && sourceConnected()) $("btn-mark").onclick();
  else if (k === "escape") {
    const anyOpen = !$("drawer").hidden || !$("filters").hidden || !$("info-panel").hidden || !$("levels-screen").hidden || !$("report-screen").hidden || !$("results-pick").hidden;
    closeDrawer(); toggleTray(false); $("info-panel").hidden = true; $("levels-screen").hidden = true; $("report-screen").hidden = true; $("results-pick").hidden = true;
    if (!anyOpen) ($("home").hidden ? openHome() : closeHome());
  }
});
for (const ev of ["mousemove", "mousedown", "keydown", "wheel", "touchstart"]) {
  window.addEventListener(ev, () => { app.lastInput = performance.now(); document.body.classList.remove("cinema"); }, { passive: true });
}
setInterval(() => {
  const busy = !$("drawer").hidden || !$("filters").hidden || !$("connect").hidden || app.question || !$("guide").hidden || !$("levels-screen").hidden || !$("report-screen").hidden;
  if (!busy && performance.now() - app.lastInput > 7000) document.body.classList.add("cinema");
}, 1000);
window.addEventListener("resize", () => renderer.resize());

// ------------------------------------------------------------------ start
buildBandChips();
syncFilterControls();
connectSocket();
requestAnimationFrame(frame);
