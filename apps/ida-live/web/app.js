/* IDA Live display. A client of the engine: it draws what it is sent and sends commands. */
"use strict";

const $ = (id) => document.getElementById(id);
const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const C = {};
["--disk", "--ink", "--ink-soft", "--text", "--muted", "--self", "--ref", "--artifact", "--aware", "--drift", "--warn"]
  .forEach((k) => (C[k.slice(2)] = css(k)));

const TRAIL_S = 90;
const TRACE_S = 5;
const EEG_NAMES = ["TP9", "AF7", "AF8", "TP10"];

const app = {
  ws: null,
  status: null,
  tick: null,
  trail: [],
  markers: [],
  eeg: EEG_NAMES.map(() => []),
  eegRate: 128,
  optics: [],
  opticsRate: 64,
  question: null,
  lastT: 0,
};

/* ------------------------------------------------------------------ socket */
function connectSocket() {
  const ws = new WebSocket(`ws://${location.host}/ws`);
  app.ws = ws;
  ws.onopen = () => send({ cmd: "hello" });
  ws.onmessage = (ev) => handle(JSON.parse(ev.data));
  ws.onclose = () => {
    if (app.quitting) return;
    $("source-line").textContent = "Lost contact with IDA Live. Is its window still open? Retrying…";
    setTimeout(connectSocket, 1500);
  };
}
function send(msg) {
  if (app.ws && app.ws.readyState === 1) app.ws.send(JSON.stringify(msg));
}

function handle(m) {
  switch (m.type) {
    case "status": app.status = m; renderStatus(); break;
    case "tick": onTick(m); break;
    case "raw": onRaw(m); break;
    case "event": onEvent(m); break;
    case "question": openQuestion(m); break;
    case "question_closed": if (app.question && app.question.id === m.id) closeQuestion(); break;
    case "scan_result": onScan(m.devices); break;
    case "reveal": showReveal(m); break;
    case "recipe_reveal": showReveal({ phase: m.name, arms: m.arms }); break;
    case "knobs": app.knobs = m.knobs; renderKnobs(); break;
    case "recipes": app.recipes = m.recipes; renderRecipes(); break;
    case "serial_ports": $("tf-status").textContent = m.ports.length
      ? m.ports.map((p) => `${p.port} (${p.description})`).join(" · ") : "No serial ports found."; break;
    case "log": addLog(m.text); if (m.text.includes("Test fire")) $("tf-status").textContent = m.text; break;
    case "error": toast(m.text); break;
    case "quit": app.quitting = true; document.body.innerHTML =
      '<main style="display:grid;place-items:center;height:100vh"><p>IDA Live is closed. Your recordings are saved in Documents\\IDA Live. You can close this tab.</p></main>'; break;
  }
}

/* ------------------------------------------------------------------ data */
function onTick(m) {
  app.tick = m;
  app.lastT = m.t;
  const s = m.state || {};
  if (s.x !== undefined) {
    app.trail.push({ t: m.t, x: s.x, y: s.y, clean: s.clean });
    const cut = m.t - TRAIL_S;
    while (app.trail.length && app.trail[0].t < cut) app.trail.shift();
    app.markers = app.markers.filter((k) => k.t >= cut);
  }
  renderReadouts(m);
  renderInstruments(m);
  if (m.calibration && !m.calibration.failed) {
    $("cal-bar").style.width = `${Math.round(100 * m.calibration.progress)}%`;
    $("cal-status").textContent = `${Math.round(100 * m.calibration.progress)}% · ${m.calibration.clean} clean moments`;
  }
}

function onRaw(m) {
  if (m.eeg) {
    app.eegRate = m.eeg.rate;
    const max = Math.round(TRACE_S * m.eeg.rate);
    for (const row of m.eeg.data) row.forEach((v, i) => app.eeg[i] && app.eeg[i].push(v));
    app.eeg.forEach((a) => { if (a.length > max) a.splice(0, a.length - max); });
  }
  if (m.optics) {
    app.opticsRate = m.optics.rate;
    const ir = m.optics.channels.map((c, i) => (c.endsWith("_IR") ? i : -1)).filter((i) => i >= 0);
    const max = Math.round(TRACE_S * m.optics.rate);
    for (const row of m.optics.data) {
      const v = ir.length ? ir.reduce((a, i) => a + row[i], 0) / ir.length : row[0];
      app.optics.push(v);
    }
    if (app.optics.length > max) app.optics.splice(0, app.optics.length - max);
  }
}

function onEvent(m) {
  const last = app.trail[app.trail.length - 1];
  if (!last) return;
  if (m.kind === "answer" && m.question === "probe" && m.answer) {
    app.markers.push({ t: app.lastT, x: last.x, y: last.y, kind: "probe", answer: m.answer });
  } else if (m.kind === "self_caught") {
    app.markers.push({ t: app.lastT, x: last.x, y: last.y, kind: "probe", answer: "drifting" });
  } else if (m.kind === "trigger") {
    app.markers.push({ t: app.lastT, x: last.x, y: last.y, kind: "trigger" });
  } else if (m.kind === "switch" && m.trial) {
    app.markers.push({ t: app.lastT, x: last.x, y: last.y, kind: "switch" });
  }
}

/* ------------------------------------------------------------------ disk */
const disk = $("disk");
const dctx = disk.getContext("2d");

function fitCanvas(c) {
  const r = c.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  const w = Math.max(10, Math.round(r.width * dpr));
  const h = Math.max(10, Math.round(r.height * dpr));
  if (c.width !== w || c.height !== h) { c.width = w; c.height = h; }
  return { w, h, dpr };
}

function geodesic(ctx, a, b) {
  // circle orthogonal to the unit circle through boundary points at angles a and b
  const half = (b - a) / 2, mid = (a + b) / 2;
  const cx = Math.cos(mid) / Math.cos(half), cy = Math.sin(mid) / Math.cos(half);
  const r = Math.abs(Math.tan(half));
  const t1 = Math.atan2(Math.sin(a) - cy, Math.cos(a) - cx);
  const t2 = Math.atan2(Math.sin(b) - cy, Math.cos(b) - cx);
  let d = t2 - t1;
  while (d > Math.PI) d -= 2 * Math.PI;
  while (d <= -Math.PI) d += 2 * Math.PI;
  ctx.beginPath();
  ctx.arc(cx, cy, r, t1, t2, d < 0);
  ctx.stroke();
}

function drawDisk() {
  const { w, h, dpr } = fitCanvas(disk);
  const ctx = dctx;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.clearRect(0, 0, w, h);
  const margin = 90 * dpr;
  const R = Math.max(40, Math.min(w, h) / 2 - margin / 2);
  const cx = w / 2, cy = h / 2;
  const px = 1 / R;

  ctx.save();
  ctx.translate(cx, cy);
  ctx.scale(R, -R);

  ctx.fillStyle = C.disk;
  ctx.beginPath(); ctx.arc(0, 0, 1, 0, 2 * Math.PI); ctx.fill();

  // geodesic web: a fixed tiling-like family of hyperbolic lines
  ctx.lineWidth = 1 * dpr * px;
  ctx.strokeStyle = C["ink-soft"];
  const N = 10;
  for (let k = 0; k < N; k++) {
    const a = (2 * Math.PI * k) / N + Math.PI / 2;
    geodesic(ctx, a, a + (3 * 2 * Math.PI) / N);
  }
  // distance rings at hyperbolic distance 1, 2, 3
  ctx.strokeStyle = C.ink;
  ctx.setLineDash([4 * dpr * px, 6 * dpr * px]);
  for (const d of [1, 2, 3]) {
    ctx.beginPath(); ctx.arc(0, 0, Math.tanh(d / 2), 0, 2 * Math.PI); ctx.stroke();
  }
  ctx.setLineDash([]);
  ctx.lineWidth = 1.5 * dpr * px;
  ctx.beginPath(); ctx.arc(0, 0, 1, 0, 2 * Math.PI); ctx.stroke();

  const st = app.tick && app.tick.state;
  const calibrated = st && st.calibrated;
  const cal = app.tick && app.tick.calibration;

  // calibration progress along the rim
  if (cal && !cal.failed) {
    ctx.strokeStyle = C.ref;
    ctx.lineWidth = 3 * dpr * px;
    ctx.beginPath();
    ctx.arc(0, 0, 1, Math.PI / 2, Math.PI / 2 - 2 * Math.PI * cal.progress, true);
    ctx.stroke();
  }

  // reference at the centre
  ctx.strokeStyle = C.ref;
  ctx.lineWidth = 1.5 * dpr * px;
  const s = 7 * dpr * px;
  ctx.beginPath(); ctx.moveTo(-s, 0); ctx.lineTo(s, 0); ctx.moveTo(0, -s); ctx.lineTo(0, s); ctx.stroke();

  if (calibrated && st.drift_x !== undefined) {
    ctx.setLineDash([2 * dpr * px, 4 * dpr * px]);
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(st.drift_x, st.drift_y); ctx.stroke();
    ctx.setLineDash([]);
    ctx.beginPath(); ctx.arc(st.drift_x, st.drift_y, 5 * dpr * px, 0, 2 * Math.PI); ctx.stroke();
  }

  // trail, fading with age
  const now = app.lastT;
  ctx.lineWidth = 2 * dpr * px;
  for (let i = 1; i < app.trail.length; i++) {
    const a = app.trail[i - 1], b = app.trail[i];
    const age = (now - b.t) / TRAIL_S;
    ctx.globalAlpha = Math.max(0.05, 0.7 * (1 - age));
    ctx.strokeStyle = b.clean ? C.self : C.artifact;
    ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
  }
  ctx.globalAlpha = 1;

  // markers where events happened
  for (const k of app.markers) {
    ctx.lineWidth = 2 * dpr * px;
    if (k.kind === "probe") {
      ctx.strokeStyle = k.answer === "aware" ? C.aware : k.answer === "drifting" ? C.drift : C.muted;
      ctx.beginPath(); ctx.arc(k.x, k.y, 9 * dpr * px, 0, 2 * Math.PI); ctx.stroke();
    } else if (k.kind === "trigger") {
      ctx.strokeStyle = C.muted;
      const q = 7 * dpr * px;
      ctx.beginPath(); ctx.moveTo(k.x, k.y + q); ctx.lineTo(k.x - q, k.y - q * 0.6); ctx.lineTo(k.x + q, k.y - q * 0.6); ctx.closePath(); ctx.stroke();
    } else {
      ctx.strokeStyle = C.muted;
      const q = 5 * dpr * px;
      ctx.strokeRect(k.x - q, k.y - q, 2 * q, 2 * q);
    }
  }

  // the current point
  if (calibrated && st.x !== undefined) {
    const r = 8 * dpr * px;
    if (st.clean) {
      const g = ctx.createRadialGradient(st.x, st.y, 0, st.x, st.y, r * 3);
      g.addColorStop(0, "rgba(232,185,106,0.35)");
      g.addColorStop(1, "rgba(232,185,106,0)");
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(st.x, st.y, r * 3, 0, 2 * Math.PI); ctx.fill();
      ctx.fillStyle = C.self;
      ctx.beginPath(); ctx.arc(st.x, st.y, r, 0, 2 * Math.PI); ctx.fill();
    } else {
      ctx.strokeStyle = C.artifact;
      ctx.lineWidth = 2 * dpr * px;
      ctx.beginPath(); ctx.arc(st.x, st.y, r, 0, 2 * Math.PI); ctx.stroke();
    }
  }
  ctx.restore();

  // axis labels outside the rim (drawn unscaled so text is upright)
  const map = app.status && app.status.map;
  ctx.font = `${13 * dpr}px "Atkinson Hyperlegible", sans-serif`;
  ctx.fillStyle = C.muted;
  if (map) {
    for (const ax of map.axes) {
      const th = (ax.angle_deg * Math.PI) / 180;
      const lx = cx + Math.cos(th) * (R + 12 * dpr);
      const ly = cy - Math.sin(th) * (R + 12 * dpr);
      ctx.textAlign = Math.cos(th) > 0.3 ? "left" : Math.cos(th) < -0.3 ? "right" : "center";
      ctx.textBaseline = Math.sin(th) > 0.3 ? "bottom" : Math.sin(th) < -0.3 ? "top" : "middle";
      ctx.fillText(`${ax.label || ax.feature}, higher`, lx, ly);
    }
  }
  // ring labels
  ctx.textAlign = "left"; ctx.textBaseline = "middle";
  ctx.fillStyle = C.ink;
  for (const d of [1, 2, 3]) {
    const r = Math.tanh(d / 2) * R;
    ctx.fillText(String(d), cx + r * Math.cos(-0.35) + 4 * dpr, cy - r * Math.sin(-0.35));
  }
  if (!calibrated) {
    ctx.textAlign = "center";
    ctx.fillStyle = C.muted;
    ctx.font = `${15 * dpr}px "Atkinson Hyperlegible", sans-serif`;
    const msg = cal && !cal.failed ? "Setting your reference…" : app.status && app.status.source
      ? "Calibrate to set your reference" : "Connect a headband to begin";
    ctx.fillText(msg, cx, cy + 40 * dpr);
  }
}

/* ------------------------------------------------------------------ traces */
const traces = $("traces");
const tctx = traces.getContext("2d");
function drawTraces() {
  const { w, h, dpr } = fitCanvas(traces);
  tctx.clearRect(0, 0, w, h);
  const lanes = app.optics.length ? 5 : 4;
  const lh = h / lanes;
  tctx.font = `${11 * dpr}px "Atkinson Hyperlegible", sans-serif`;
  tctx.textBaseline = "top";
  const drawLane = (arr, i, rate, scale, color, label) => {
    const mid = lh * i + lh / 2;
    tctx.fillStyle = C.muted;
    tctx.fillText(label, 0, lh * i + 2 * dpr);
    if (arr.length < 2) return;
    tctx.strokeStyle = color;
    tctx.lineWidth = 1 * dpr;
    tctx.beginPath();
    const n = Math.round(TRACE_S * rate);
    const x0 = 34 * dpr, span = w - x0;
    arr.forEach((v, k) => {
      const x = x0 + span * ((n - arr.length + k) / n);
      const y = mid - Math.max(-1, Math.min(1, v * scale)) * (lh / 2 - 2 * dpr);
      k ? tctx.lineTo(x, y) : tctx.moveTo(x, y);
    });
    tctx.stroke();
  };
  app.eeg.forEach((a, i) => drawLane(a, i, app.eegRate, 1 / 100, C.text, EEG_NAMES[i]));
  if (app.optics.length) {
    const mean = app.optics.reduce((a, b) => a + b, 0) / app.optics.length;
    const dev = Math.max(1e-6, Math.max(...app.optics.map((v) => Math.abs(v - mean))));
    drawLane(app.optics.map((v) => v - mean), 4, app.opticsRate, 1 / dev, C.ref, "IR");
  }
}

/* ------------------------------------------------------------------ panels */
function fmt(v, d = 2) { return v === undefined || v === null || Number.isNaN(v) ? "–" : Number(v).toFixed(d); }

function renderReadouts(m) {
  const s = m.state || {};
  $("r-d").textContent = s.calibrated ? fmt(s.d) : "–";
  $("r-drift").textContent = s.calibrated ? fmt(s.drift_d) : "–";
  if (s.last_return) {
    $("r-return").textContent = `${fmt(s.last_return.seconds, 1)} s`;
    $("r-return-label").textContent = `back after ${s.last_return.kind === "self_caught" ? "catching a drift" : s.last_return.kind}`;
  }
  const reasons = (s.reasons || []).filter((r) => r !== "no signal");
  let note = "";
  if (!s.clean && reasons.length) note = `Holding the point: ${reasons.join(", ")}.`;
  if ((s.reasons || []).includes("no signal")) note = "Waiting for signal…";
  if (m.flags && m.flags.eeg === "missing" && app.status && app.status.light && app.status.light.state === "switch") note = "Switching the optics…";
  $("disk-note").textContent = note;
  $("battery").textContent = m.battery != null ? `Battery ${Math.round(m.battery)}%` : "";
}

function renderInstruments(m) {
  const q = (m.flags && m.flags.quality) || [];
  document.querySelectorAll("#contact li").forEach((li, i) => {
    li.querySelector(".dot").className = `dot ${q[i] || ""}`;
    li.title = q[i] ? `Contact ${q[i]}` : "No signal";
  });
  const map = app.status && app.status.map;
  const z = (m.state && m.state.z) || {};
  if (map) {
    $("axes").innerHTML = map.axes.map((ax) => {
      const v = z[ax.feature];
      const frac = v === undefined ? 0 : Math.max(-1, Math.min(1, v / 4));
      const left = frac < 0 ? 50 + frac * 50 : 50, width = Math.abs(frac) * 50;
      return `<li><span>${ax.label || ax.feature}</span><span class="meter"><i style="left:${left}%;width:${width}%"></i></span><span class="num">${v === undefined ? "–" : (v >= 0 ? "+" : "") + v.toFixed(1)}</span></li>`;
    }).join("");
  }
  const bl = m.flags && m.flags.band_log;
  if (bl) {
    const lin = Object.fromEntries(Object.entries(bl).map(([k, v]) => [k, Math.pow(10, v)]));
    const tot = Object.values(lin).reduce((a, b) => a + b, 0);
    $("bands").innerHTML = Object.entries(lin).map(([k, v]) => {
      const pc = (100 * v) / tot;
      return `<li><span>${k}</span><span class="meter"><i style="left:0;width:${pc}%"></i></span><span class="num">${pc.toFixed(0)}%</span></li>`;
    }).join("");
  }
  const hr = m.features && m.features.heart_bpm;
  $("heart").textContent = hr ? `${Math.round(hr)}` : "–";
  const opt = m.flags && m.flags.optics;
  $("optics").textContent = opt === "on" ? `On (${m.preset})` : opt === "filling" ? "Starting" : `Off (${m.preset || "–"})`;
}

function renderStatus() {
  const st = app.status;
  const src = st.source;
  const line = src
    ? `${src.name || src.kind}${src.address ? " · " + src.address : ""}${src.connected ? "" : " · disconnected"}`
    : "Not connected";
  $("source-line").textContent = st.session ? `${line} · recording ${st.session.label || ""}` : line;
  const connected = !!(src && src.connected);
  if (src && [...$("src-kind").options].some((o) => o.value === src.kind) && $("src-kind").value !== src.kind) {
    $("src-kind").value = src.kind;
    $("src-kind").onchange();
  }
  $("connect").disabled = connected;
  $("disconnect").disabled = !src;
  $("step-connect").classList.toggle("done", connected);
  $("calibrate").disabled = !connected || !!st.session || !!(st.calibration && !st.calibration.failed);
  if (st.reference && !(st.calibration && !st.calibration.failed)) {
    $("cal-status").textContent = `Reference ${st.reference.id} · ${st.reference.created}`;
    $("cal-bar").style.width = "100%";
  }
  if (st.calibration && st.calibration.failed) {
    $("cal-status").textContent = st.calibration.failed;
    $("cal-bar").style.width = "0";
  }
  $("step-cal").classList.toggle("done", !!st.reference);
  $("start-session").disabled = !connected || !st.reference || !!st.session;
  $("end-session").disabled = !st.session;
  $("drifted").disabled = !st.session;
  $("step-session").classList.toggle("done", !!st.session);
  const L = st.light;
  const running = L && !["done", "stopped"].includes(L.state);
  $("light-start").disabled = !st.session || !st.can_light || running;
  $("light-stop").disabled = !running;
  $("reveal").disabled = !(L && ["done", "stopped"].includes(L.state));
  const R = st.recipe;
  const rRunning = R && R.state === "watching";
  $("rc-start").disabled = !st.session || rRunning || !app.selectedRecipe;
  $("rc-stop").disabled = !rRunning;
  $("rc-reveal").disabled = !(R && ["done", "stopped"].includes(R.state));
  $("rc-status").textContent = R ? `${R.name}: ${R.state}, fired ${R.fired} of ${R.max_fires} · ${R.actuator} · light on ${R.pattern.light_on_s} s per fire${R.bench ? " · bench" : ""}${R.covered ? " · covered" : ""}` : (st.session ? "" : "Start a recording first.");
  $("light-status").textContent = !st.can_light && connected
    ? "Light trials need the direct headband connection (or the simulator)."
    : L ? `${L.phase}: trial ${L.current} of ${L.trials} · ${L.state}${L.bench ? " · bench" : ""}` : "";
}

/* ------------------------------------------------------------------ questions */
const Q = {
  probe: {
    title: "Just before this appeared, where was your attention?",
    options: [["aware", "On what I meant to be doing"], ["drifting", "It had wandered off"], ["unsure", "Not sure"]],
  },
  guess: {
    title: "Do you think the light was on in that trial?",
    options: [["yes", "Yes"], ["no", "No"], ["unsure", "Can't tell"]],
  },
};
function openQuestion(m) {
  const spec = Q[m.kind];
  if (!spec) return;
  app.question = m;
  $("q-title").textContent = m.kind === "guess" ? `Trial ${m.trial}. ${spec.title}` : spec.title;
  $("q-buttons").innerHTML = "";
  spec.options.forEach(([value, label], i) => {
    const b = document.createElement("button");
    b.innerHTML = `${label}<kbd>${i + 1}</kbd>`;
    b.onclick = () => answer(value);
    $("q-buttons").appendChild(b);
  });
  $("q-hint").textContent = "Answer with the keys 1, 2 or 3. It closes by itself after 30 seconds.";
  $("question").hidden = false;
  $("q-buttons").firstChild.focus();
}
function answer(value) {
  if (!app.question) return;
  send({ cmd: "answer", id: app.question.id, value });
  closeQuestion();
}
function closeQuestion() { app.question = null; $("question").hidden = true; }

function showReveal(m) {
  $("rv-title").textContent = `Allocation · ${m.phase}${m.bench ? " · bench" : ""}`;
  $("rv-list").innerHTML = m.arms.map((a) => `<li>${a === "active" ? "Light on" : "Sham"}</li>`).join("");
  $("reveal-panel").hidden = false;
}

/* ------------------------------------------------------------------ controls */
function onScan(devices) {
  $("scan").disabled = false;
  const sel = $("device");
  sel.innerHTML = devices.length
    ? devices.map((d) => `<option value="${d.address}">${d.name} · ${d.address}</option>`).join("")
    : `<option value="">No headband found</option>`;
}
$("src-kind").onchange = () => {
  const k = $("src-kind").value;
  $("scan").hidden = k !== "athena";
  $("device").hidden = k !== "athena";
  $("replay-path").hidden = k !== "replay";
};
$("scan").onclick = () => { $("scan").disabled = true; send({ cmd: "scan" }); };
$("connect").onclick = () => {
  const kind = $("src-kind").value;
  const msg = { cmd: "connect", kind };
  if (kind === "athena") {
    msg.address = $("device").value;
    if (!msg.address) return toast("Find your headband first, then pick it from the list.");
  }
  if (kind === "replay") msg.path = $("replay-path").value.trim();
  app.trail = []; app.markers = [];
  send(msg);
};
$("disconnect").onclick = () => send({ cmd: "disconnect" });
$("calibrate").onclick = () => send({ cmd: "calibrate" });
$("start-session").onclick = () => {
  app.trail = []; app.markers = [];
  send({ cmd: "start_session", label: $("label").value, probes: $("probes").checked });
};
$("end-session").onclick = () => send({ cmd: "end_session" });
$("drifted").onclick = () => send({ cmd: "self_caught" });
$("light-start").onclick = () => send({ cmd: "light_start", phase: $("phase").value, bench: $("bench").checked });
$("light-stop").onclick = () => send({ cmd: "light_stop" });
$("reveal").onclick = () => {
  if (confirm("Reveal which trials had the light on? Do this only after you have finished guessing.")) send({ cmd: "reveal" });
};
$("quit").onclick = () => {
  if (confirm("Quit IDA Live? Any recording in progress is saved first.")) send({ cmd: "quit" });
};
$("rv-close").onclick = () => ($("reveal-panel").hidden = true);
$("log-toggle").onclick = () => {
  const log = $("log");
  log.hidden = !log.hidden;
  $("log-toggle").setAttribute("aria-expanded", String(!log.hidden));
};
document.addEventListener("keydown", (e) => {
  if (["INPUT", "TEXTAREA", "SELECT"].includes(e.target.tagName)) return;
  if (app.question && ["1", "2", "3"].includes(e.key)) {
    const spec = Q[app.question.kind];
    answer(spec.options[Number(e.key) - 1][0]);
  } else if ((e.key === "d" || e.key === "D") && !$("drifted").disabled) {
    send({ cmd: "self_caught" });
    toast("Noted: you caught a drift.");
  }
});

function addLog(text) {
  const p = document.createElement("div");
  p.textContent = text;
  $("log").appendChild(p);
  while ($("log").childNodes.length > 200) $("log").removeChild($("log").firstChild);
  $("log").scrollTop = $("log").scrollHeight;
}
let toastTimer = null;
function toast(text) {
  const t = $("toast");
  t.textContent = text;
  t.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (t.hidden = true), 5000);
  $("scan").disabled = false;
}

/* ------------------------------------------------------------------ control drawer */
app.knobs = [];
app.recipes = {};
app.selectedRecipe = null;
app.knobDefaults = null;

$("control-toggle").onclick = () => {
  const d = $("control");
  d.hidden = !d.hidden;
  $("control-toggle").setAttribute("aria-expanded", String(!d.hidden));
  if (!d.hidden) { send({ cmd: "knobs" }); send({ cmd: "recipes" }); }
};
$("control-close").onclick = () => $("control-toggle").onclick();
document.querySelectorAll(".tabs button").forEach((b) => {
  b.onclick = () => {
    document.querySelectorAll(".tabs button").forEach((x) => x.setAttribute("aria-selected", String(x === b)));
    ["knobs", "recipes", "fire"].forEach((t) => ($(`tab-${t}`).hidden = t !== b.dataset.tab));
  };
});

function esc(t) { return String(t).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }

function renderKnobs() {
  if (!app.knobDefaults) app.knobDefaults = Object.fromEntries(app.knobs.map((k) => [k.path, k.value]));
  const q = $("knob-search").value.trim().toLowerCase();
  const groups = {};
  for (const k of app.knobs) {
    if (q && !(k.path.toLowerCase().includes(q) || k.description.toLowerCase().includes(q))) continue;
    (groups[k.group] = groups[k.group] || []).push(k);
  }
  $("knob-list").innerHTML = Object.entries(groups).map(([g, ks]) => `
    <div class="knob-group"><h3>${esc(g)}</h3>${ks.map(knobRow).join("")}</div>`).join("") ||
    `<p class="muted small">No knob matches “${esc(q)}”.</p>`;
  document.querySelectorAll("[data-knob]").forEach((el) => {
    el.onchange = () => {
      const v = el.type === "checkbox" ? el.checked : el.value;
      send({ cmd: "set_knob", path: el.dataset.knob, value: v });
    };
  });
}
function knobRow(k) {
  const id = `k-${k.path.replace(/[^a-z0-9]/gi, "_")}`;
  let input;
  if (k.choices) {
    input = `<select id="${id}" data-knob="${esc(k.path)}">${k.choices.map((c) =>
      `<option ${String(c) === String(k.value) ? "selected" : ""}>${esc(c)}</option>`).join("")}</select>`;
  } else if (k.type === "bool") {
    input = `<input id="${id}" type="checkbox" data-knob="${esc(k.path)}" ${k.value ? "checked" : ""}>`;
  } else if (k.type === "number") {
    const attrs = [k.min != null ? `min="${k.min}"` : "", k.max != null ? `max="${k.max}"` : "", `step="${k.step || "any"}"`].join(" ");
    input = `<input id="${id}" type="number" ${attrs} value="${k.value}" data-knob="${esc(k.path)}">`;
  } else {
    input = `<input id="${id}" type="text" value="${esc(k.value ?? "")}" data-knob="${esc(k.path)}">`;
  }
  const changed = app.knobDefaults && String(app.knobDefaults[k.path]) !== String(k.value);
  const applies = k.applies && k.applies !== "now" ? ` Applies: ${k.applies}.` : "";
  return `<div class="knob${changed ? " changed" : ""}"><label class="name" for="${id}">${esc(k.path.split(".").slice(1).join(".") || k.path)}</label>${input}
    <span class="desc">${esc(k.description)}${applies}</span></div>`;
}
$("knob-search").oninput = renderKnobs;
$("knobs-save").onclick = () => send({ cmd: "save_knobs" });

function renderRecipes() {
  const list = Object.values(app.recipes);
  $("recipe-list").innerHTML = list.map((r) => r._error
    ? `<li class="bad"><b>${esc(r.name)}</b><span>Cannot load ${esc(r._file)}: ${esc(r._error)}</span></li>`
    : `<li data-name="${esc(r.name)}" aria-selected="${r.name === app.selectedRecipe}" tabindex="0"><b>${esc(r.name)}</b>
       <span>${esc(r.description || "")}</span><span> · ${esc(r.actuator)} · real on ${Math.round(100 * r.randomize)}% of triggers</span></li>`).join("")
    || `<li class="bad"><span>No recipes in the recipes folder yet.</span></li>`;
  document.querySelectorAll("#recipe-list li[data-name]").forEach((li) => {
    li.onclick = li.onkeydown = (e) => {
      if (e.type === "keydown" && e.key !== "Enter") return;
      app.selectedRecipe = li.dataset.name;
      const r = app.recipes[app.selectedRecipe];
      const clean = Object.fromEntries(Object.entries(r).filter(([k]) => !k.startsWith("_")));
      $("rc-text").value = JSON.stringify(clean, null, 1);
      renderRecipes();
      if (app.status) renderStatus();
    };
  });
}
$("rc-start").onclick = () => send({ cmd: "recipe_start", name: app.selectedRecipe, bench: $("rc-bench").checked, covered: $("rc-covered").checked });
$("rc-stop").onclick = () => send({ cmd: "recipe_stop" });
$("rc-reveal").onclick = () => {
  if (confirm("Reveal which triggers were real? Stop watching the screen for the effect first.")) send({ cmd: "recipe_reveal" });
};
$("rc-save").onclick = () => {
  try { JSON.parse($("rc-text").value); } catch (e) { return toast(`That is not valid JSON: ${e.message}`); }
  send({ cmd: "save_recipe", text: $("rc-text").value });
};
$("tf-fire").onclick = () => {
  let pattern;
  try { pattern = JSON.parse($("tf-pattern").value); } catch (e) { return toast(`Pattern is not valid JSON: ${e.message}`); }
  $("tf-status").textContent = "Firing…";
  send({ cmd: "test_fire", actuator: $("tf-actuator").value, pattern, sham: $("tf-sham").checked });
};
$("tf-ports").onclick = () => send({ cmd: "serial_ports" });

/* ------------------------------------------------------------------ loop */
let lastDraw = 0;
function frame(ts) {
  if (ts - lastDraw > 33) {
    drawDisk();
    drawTraces();
    lastDraw = ts;
  }
  requestAnimationFrame(frame);
}
$("src-kind").onchange();
connectSocket();
requestAnimationFrame(frame);
