/* Inside — a constructed world about the view from within.
   The trial and sensor limits are declared game rules. The disk identities are
   conditional mathematics of the chosen curvature -1 model. */
import { disk, fitCanvas } from './bo.js';
import { makeWorld, move, observePoint, trial, loopTriangle, horizonProgress } from './inside-core.mjs';

const $ = (id) => document.getElementById(id);
const ui = Object.fromEntries([
  'inside-canvas', 'chapter-label', 'scene-prompt', 'read-seen', 'read-kept',
  'read-hidden', 'read-bet', 'read-budget', 'read-distance', 'read-turn',
  'event-log', 'intro-start', 'start-overlay', 'start-button', 'scan-button', 'act-button', 'advance-button',
  'loop-button', 'reset-button', 'pause-button', 'slow-mode', 'flat-compare',
].map((id) => [id, $(id)]));
const canvas = ui['inside-canvas'];
const world = makeWorld();
const twin = [
  { label: 'A', point: disk.fromPolar(1.22, -0.37), reserve: 0.9, color: '#89d6e4' },
  { label: 'B', point: disk.fromPolar(1.22, 0.37), reserve: 0.1, color: '#f4aa79' },
];
const pulse = 0.5;
const outcomes = twin.map((node) => trial(0.5, node.reserve, pulse));
const STEP = 0.24;
const TURN = Math.PI / 12;
const motionPreference = matchMedia('(prefers-reduced-motion: reduce)');
let frame = null;
let tickFrame = null;
let state;

function fresh() {
  return {
    phase: 'ready', observer: disk.C(0, 0), heading: 0, zoom: 1,
    path: 0, steps: 0, edgeWitnessed: false, prediction: null, scanned: false,
    paused: false, animation: null, loop: null, compassBefore: 0,
  };
}

function log(message) {
  if (ui['event-log'].querySelector('[data-placeholder]')) ui['event-log'].replaceChildren();
  const row = document.createElement('p');
  row.textContent = message;
  ui['event-log'].append(row);
  ui['event-log'].scrollTop = ui['event-log'].scrollHeight;
}

function prompt(message) { ui['scene-prompt'].textContent = message; }

function isTrialPhase() { return ['trial', 'revealed', 'repair', 'repair-revealed'].includes(state.phase); }
function isWorldPhase() { return ['journey', 'horizon', 'looping', 'loop-result', 'debrief'].includes(state.phase); }
function isRevealed() { return ['revealed', 'repair-revealed'].includes(state.phase); }
function canNavigate() { return ['journey', 'horizon'].includes(state.phase); }
function isReduced() { return motionPreference.matches || ui['slow-mode'].checked; }
function focusNext(element) { requestAnimationFrame(() => element.focus({ preventScroll: true })); }
function showScene() { requestAnimationFrame(() => $('experience').scrollIntoView({ block: 'start' })); }

function visibleTwin() {
  return twin.map((node) => ({ node, reading: observePoint(state.observer, state.heading, node.point, state.zoom) }));
}

function updateUI() {
  const p = state.phase;
  const stopped = state.paused;
  const titles = {
    ready: 'Ready to enter', trial: '01 / Two identical readings',
    revealed: '01 / A broken prediction', repair: '02 / Keep one more fact',
    'repair-revealed': '02 / A better prediction', journey: '03 / Chase the edge',
    horizon: '03 / The edge stays ahead', looping: '04 / Take a closed path',
    'loop-result': '04 / Returned, but turned', debrief: 'From inside, with conditions',
  };
  ui['chapter-label'].textContent = titles[p];
  ui['start-overlay'].hidden = p !== 'ready';
  ui['start-button'].hidden = p !== 'ready';
  ui['scan-button'].hidden = !['trial', 'repair', 'journey', 'horizon'].includes(p);
  ui['act-button'].hidden = !['trial', 'repair'].includes(p);
  ui['advance-button'].hidden = !['revealed', 'repair-revealed', 'journey', 'horizon', 'loop-result'].includes(p);
  ui['loop-button'].hidden = !['journey', 'horizon'].includes(p);
  ui['scan-button'].disabled = stopped || (p === 'repair' && state.scanned);
  ui['act-button'].disabled = stopped || (p === 'repair' && !state.scanned);
  ui['advance-button'].disabled = stopped || Boolean(state.animation);
  ui['loop-button'].disabled = stopped || Boolean(state.animation) || !state.edgeWitnessed;
  ui['pause-button'].textContent = stopped ? 'Resume' : 'Pause';
  ui['pause-button'].disabled = p === 'ready';
  document.querySelector('.inside-prediction').hidden = !isTrialPhase();
  document.querySelector('.inside-control-grid').hidden = p === 'ready' || ['looping', 'loop-result', 'debrief'].includes(p);
  for (const group of document.querySelectorAll('.inside-motion-control')) group.hidden = !canNavigate();
  ui['flat-compare'].closest('label').hidden = !['loop-result', 'debrief'].includes(p);
  ui['slow-mode'].closest('label').hidden = !(canNavigate() || p === 'looping');
  ui['scan-button'].textContent = p === 'repair' ? 'Read the second channel' : 'Scan surroundings';
  ui['advance-button'].textContent = p === 'journey' || p === 'horizon'
    ? (isReduced() ? 'Take one equal step' : 'Run a straight route')
    : p === 'loop-result' ? 'What did I learn?' : 'Continue';

  const predictionButtons = [...document.querySelectorAll('[data-predict]')];
  predictionButtons[0].textContent = p === 'repair' || p === 'repair-revealed'
    ? 'A rises · B falls' : 'Both rise';
  predictionButtons[1].textContent = p === 'repair' || p === 'repair-revealed'
    ? 'A falls · B rises' : 'Both fall';
  for (const button of predictionButtons) {
    button.disabled = stopped || !['trial', 'repair'].includes(p) || (p === 'repair' && !state.scanned);
    button.setAttribute('aria-pressed', String(button.dataset.predict === state.prediction));
  }
  for (const button of document.querySelectorAll('[data-move], [data-look], [data-zoom]')) {
    button.disabled = stopped || Boolean(state.animation) || !canNavigate();
  }

  if (isTrialPhase()) {
    const found = visibleTwin().filter((v) => v.reading.visible).map((v) => v.node.label);
    const values = found.map((label) => {
      const idx = label === 'A' ? 0 : 1;
      return `${label} ${isRevealed() ? outcomes[idx].futureReading.toFixed(2) : '0.50'}`;
    });
    ui['read-seen'].textContent = values.length ? values.join(' · ') : 'Both signals outside your sensor';
    ui['read-kept'].textContent = state.scanned ? 'A reserve 0.90 · B reserve 0.10' : 'One surface number per signal';
    ui['read-hidden'].textContent = isRevealed() || state.scanned
      ? 'The wider world remains outside this channel'
      : 'The history and reserve behind each signal';
    ui['read-budget'].textContent = p === 'repair' && !state.scanned ? '1 reserve reading' : '0 extra readings';
    ui['read-bet'].textContent = state.prediction === null ? 'No prediction yet'
      : p === 'repair' || p === 'repair-revealed'
        ? (state.prediction === 'steady' ? 'A rises · B falls' : 'A falls · B rises')
        : (state.prediction === 'steady' ? 'Both rise' : 'Both fall');
  } else if (isWorldPhase()) {
    const seen = world.landmarks.filter((v) => observePoint(state.observer, state.heading, v.point, state.zoom).visible);
    const half = 60 / state.zoom;
    ui['read-seen'].textContent = `${seen.length} marker${seen.length === 1 ? '' : 's'} · ${Math.round(half * 2)}° window`;
    ui['read-kept'].textContent = `Path ${state.path.toFixed(2)} intrinsic units · ${state.steps} equal steps`;
    ui['read-hidden'].textContent = `Beyond ${sensorRange().toFixed(2)} units and outside the window`;
    ui['read-budget'].textContent = 'Finite aperture';
    ui['read-bet'].textContent = p === 'loop-result' || p === 'debrief'
      ? 'The compass turned on return' : 'Can a finite walk reach the rim?';
  } else {
    ui['read-seen'].textContent = 'No observation yet';
    ui['read-kept'].textContent = 'Nothing retained';
    ui['read-hidden'].textContent = 'The world beyond your view';
    ui['read-bet'].textContent = 'No prediction yet';
    ui['read-budget'].textContent = '—';
  }
  ui['read-distance'].textContent = `${state.path.toFixed(2)} units`;
  ui['read-turn'].textContent = state.loop && ['loop-result', 'debrief'].includes(p)
    ? `${(state.loop.turn * 180 / Math.PI).toFixed(1)}°${ui['flat-compare'].checked ? ' · flat 0°' : ''}` : '0°';
  renderSoon();
}

function sensorRange() { return 2.2 + 1.2 * Math.log2(state.zoom); }

function enter() {
  if (state.phase !== 'ready') return;
  state.phase = 'trial';
  prompt('At this station, two signals report exactly 0.50. Choose one prediction for both, then intervene with the same pulse. Movement unlocks after the twin-signal trial.');
  log('Entered a constructed instrument station. The same surface channel shows A 0.50 and B 0.50. Their histories are not in the reading.');
  updateUI();
  focusNext(ui['chapter-label']);
  showScene();
}

function choosePrediction(value) {
  if (!['trial', 'repair'].includes(state.phase) || state.paused || (state.phase === 'repair' && !state.scanned)) return;
  state.prediction = value;
  prompt(state.phase === 'trial'
    ? `You bet that both signals ${value === 'steady' ? 'rise' : 'fall'}. Apply one identical pulse to each.`
    : `You bet on ${value === 'steady' ? 'A rising and B falling' : 'A falling and B rising'}. Apply the same pulse again.`);
  updateUI();
}

function intervene() {
  if (state.paused || !['trial', 'repair'].includes(state.phase)) return;
  if (state.phase === 'repair' && !state.scanned) {
    prompt('Read the reserve channel before the second prediction. A lucky guess would not show what information was missing.');
    return;
  }
  if (!state.prediction) {
    prompt('Select a prediction before you intervene.');
    return;
  }
  if (state.phase === 'trial') {
    state.phase = 'revealed';
    prompt('A rises to 0.90. B falls to 0.10. One identical present reading could not predict both futures. Your single bet had to miss one.');
    log(`Same pulse, different futures: A 0.50 → 0.90; B 0.50 → 0.10. Betting “both ${state.prediction === 'steady' ? 'rise' : 'fall'}” got one wrong.`);
  } else {
    const correct = state.prediction === 'steady';
    state.phase = 'repair-revealed';
    prompt(correct
      ? 'The added reserve reading separated the histories. Your prediction gets both futures right for this pulse.'
      : 'The two-channel reading separates the histories for this pulse. A reserve of 0.90 rises; B reserve of 0.10 falls.');
    log(`With the reserve channel, you bet ${state.prediction === 'steady' ? 'A rises / B falls' : 'A falls / B rises'}. Actual futures: A 0.90 / B 0.10. ${correct ? 'Both correct for this pulse.' : 'Both reversed.'}`);
  }
  updateUI();
  focusNext(ui['chapter-label']);
  showScene();
}

function scan() {
  if (state.paused) return;
  if (state.phase === 'trial') {
    prompt('The surface scanner repeats 0.50 for both signals. It cannot read the hidden reserve in this pass. Make your bet.');
    log('Surface scan: A 0.50; B 0.50. Repeating this channel adds no distinguishing fact.');
  } else if (state.phase === 'repair' && !state.scanned) {
    state.scanned = true;
    prompt('Your one new channel sees A reserve 0.90 and B reserve 0.10. The two identical surface readings no longer mean the same state. Predict again.');
    log('Second-channel scan costs the one available reading: A reserve 0.90; B reserve 0.10.');
  } else if (canNavigate()) {
    const seen = world.landmarks.filter((v) => observePoint(state.observer, state.heading, v.point, state.zoom).visible);
    const names = seen.length ? seen.map((v) => v.label).join(', ') : 'no named markers';
    prompt(`Inside your ${Math.round(120 / state.zoom)}° aperture and ${sensorRange().toFixed(1)}-unit range: ${names}. Zoom in to reach farther, but your window narrows.`);
    log(`Sensor scan at zoom ${state.zoom}: ${names}. The rest is unobserved, not absent.`);
  }
  updateUI();
  if (state.phase === 'repair' && state.scanned) focusNext(document.querySelector('[data-predict="steady"]'));
}

function continueStory() {
  if (state.paused || state.animation) return;
  if (state.phase === 'revealed') {
    state.phase = 'repair'; state.prediction = null; state.scanned = false;
    prompt('Rewind. This time you may keep one more fact. Spend your single extra reading on reserve, then predict the two responses.');
    log('Rewound to the same present reading. One reserve-channel measurement is now available.');
    updateUI();
    focusNext(ui['scan-button']);
    showScene();
    return;
  } else if (state.phase === 'repair-revealed') {
    state.phase = 'journey'; state.observer = disk.C(0, 0); state.heading = 0;
    state.path = 0; state.steps = 0; state.zoom = 1;
    prompt('Now leave the signals. Walk toward the visible rim in equal intrinsic steps. The external chart at right is a teaching view unavailable to your observer.');
    log('At the origin of a chosen hyperbolic disk. Each forward press travels 0.24 intrinsic units. The chart radius is bounded by 1.');
    updateUI();
    focusNext(canvas);
    showScene();
    return;
  } else if (state.phase === 'journey' || state.phase === 'horizon') {
    if (isReduced()) {
      takeStep('forward');
      prompt(`Step ${state.steps}: chart radius ${disk.abs(state.observer).toFixed(5)}. You are still inside.${state.edgeWitnessed ? ' You can now walk the loop.' : ' Keep moving outward to unlock the loop.'}`);
    } else {
      startJourney();
    }
  } else if (state.phase === 'loop-result') {
    state.phase = 'debrief';
    prompt('You saw three different lessons: missing state can break a prediction; a bounded chart can contain unlimited intrinsic distance; a chosen curved geometry can turn a carried compass. Each needs its own assumptions.');
    log('Debrief: the trial is a model illustration; the horizon and loop are conditional mathematics of the chosen disk. None validates a claim about natural geometry.');
    updateUI();
    focusNext(ui['chapter-label']);
    showScene();
    return;
  }
  updateUI();
}

function takeStep(command, distance = STEP) {
  const result = move(state.observer, state.heading, command, distance);
  state.observer = result.observer;
  state.heading = result.heading;
  state.path += result.travelled;
  if (isWorldPhase() && result.travelled > 0) state.steps += 1;
  if (canNavigate() && disk.abs(state.observer) >= horizonProgress(8, STEP) - 1e-6) {
    state.edgeWitnessed = true;
    state.phase = 'horizon';
  }
  updateUI();
  return result;
}

function moveCommand(command) {
  if (state.paused || state.animation || !canNavigate()) return;
  const result = takeStep(command);
  if (result.travelled < 1e-6) {
    prompt('This digital chart has reached its display precision. The mathematical rim is still outside every finite path. Turn and move back to explore.');
  } else {
    prompt(`You moved one intrinsic step. Total path ${state.path.toFixed(2)}; external chart radius ${disk.abs(state.observer).toFixed(5)}. The rim is still outside.`);
  }
}

function look(direction) {
  if (state.paused || state.animation || !canNavigate()) return;
  const result = move(state.observer, state.heading, direction === 'left' ? 'turn-left' : 'turn-right');
  state.heading = result.heading;
  prompt(`You turned ${Math.round(TURN * 180 / Math.PI)}°. What falls outside your aperture is no longer in the current reading.`);
  updateUI();
}

function zoom(direction) {
  if (state.paused || state.animation || !canNavigate()) return;
  state.zoom = Math.max(1, Math.min(8, state.zoom + (direction === 'in' ? 1 : -1)));
  prompt(`Sensor zoom ${state.zoom}: range ${sensorRange().toFixed(1)} intrinsic units, window ${Math.round(120 / state.zoom)}° wide. Farther access costs field width.`);
  updateUI();
}

function startJourney() {
  // A controlled radial run gives the displayed closed-form radius an honest base.
  state.observer = disk.C(0, 0); state.heading = 0;
  state.path = 0; state.steps = 0; state.edgeWitnessed = false;
  state.phase = 'journey';
  state.animation = { kind: 'journey', remaining: 28, elapsed: 0, last: null };
  prompt('Returned to the origin for a controlled straight route. Watch the outside chart: path length grows while the drawn radius approaches 1.');
  log('Controlled run from the origin: 28 equal forward steps of 0.24 intrinsic units.');
  updateUI();
  queueTick();
}

function startLoop() {
  if (state.paused || state.animation || !canNavigate() || !state.edgeWitnessed) return;
  const a = disk.C(0.58, 0.10), b = disk.C(-0.18, 0.62);
  state.loop = loopTriangle(state.observer, a, b);
  state.compassBefore = state.heading;
  state.phase = 'looping';
  const route = [];
  for (let leg = 0; leg < 3; leg++) {
    const segment = disk.geodesic(state.loop.vertices[leg], state.loop.vertices[leg + 1], 34);
    route.push(...(leg === 0 ? segment : segment.slice(1)));
  }
  if (isReduced()) {
    let length = 0;
    for (let i = 1; i < route.length; i++) length += disk.distance(route[i - 1], route[i]);
    state.path += length;
    finishLoop();
  } else {
    state.animation = { kind: 'loop', route, index: 0, elapsed: 0, last: null };
    prompt('You carry a compass around a closed geodesic triangle. The orange route is a teaching overlay, beyond your finite sensor aperture.');
    log('Walking a plotted three-leg geodesic route. The carried compass is compared on return.');
    updateUI();
    focusNext(canvas);
    queueTick();
  }
}

function finishLoop() {
  state.observer = state.loop.vertices[0];
  state.heading = state.compassBefore + state.loop.turn;
  state.animation = null;
  state.phase = 'loop-result';
  const degrees = (state.loop.turn * 180 / Math.PI).toFixed(1);
  const direction = state.loop.turn < 0 ? 'clockwise' : 'counterclockwise';
  prompt(`Same place. The carried compass is turned ${Math.abs(Number(degrees)).toFixed(1)}° ${direction} relative to its original direction. In this curvature −1 model, the turn magnitude equals the enclosed area. Toggle flat comparison: its turn is 0°.`);
  log(`Closed loop returned to its start. Signed turn ${degrees}°; hyperbolic area ${state.loop.area.toFixed(3)} in curvature −1 units. A flat comparison gives 0°. Geometry was an extra model choice.`);
  updateUI();
  focusNext(ui['chapter-label']);
  showScene();
}

function queueTick() {
  if (tickFrame !== null) return;
  tickFrame = requestAnimationFrame((time) => { tickFrame = null; tick(time); });
}

function tick(time) {
  const anim = state.animation;
  if (!anim) return;
  if (state.paused) { anim.last = null; return; }
  const dt = anim.last === null ? 0 : Math.min(100, time - anim.last);
  anim.last = time;
  anim.elapsed += dt;
  if (anim.kind === 'journey') {
      while (anim.elapsed >= 115 && anim.remaining > 0) {
        anim.elapsed -= 115;
        takeStep('forward');
        anim.remaining--;
      }
      if (anim.remaining === 0) {
        state.animation = null; state.phase = 'horizon';
        const r = disk.abs(state.observer);
        prompt(`You travelled ${state.path.toFixed(2)} intrinsic units. The chart radius is ${r.toFixed(6)}, still below 1. The mathematical path can keep growing without reaching the rim.`);
        log(`After ${state.steps} straight steps from the origin: chart radius r = tanh(28 × 0.24 / 2) = ${horizonProgress(28, STEP).toFixed(6)} < 1.`);
        updateUI();
        showScene();
      }
  } else if (anim.kind === 'loop') {
      while (anim.elapsed >= 30 && anim.index < anim.route.length - 1) {
        anim.elapsed -= 30;
        const next = anim.route[++anim.index];
        state.path += disk.distance(state.observer, next);
        state.observer = next;
      }
      if (anim.index >= anim.route.length - 1) finishLoop();
  }
  renderSoon();
  if (state.animation) queueTick();
}

function pointOnScreen(reading, cx, cy, radius) {
  return { x: cx + radius * reading.local.y, y: cy - radius * reading.local.x };
}

function ring(g, x, y, r, stroke, width = 1) {
  g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.strokeStyle = stroke; g.lineWidth = width; g.stroke();
}

function line(g, a, b, stroke, width = 1) {
  g.beginPath(); g.moveTo(a.x, a.y); g.lineTo(b.x, b.y); g.strokeStyle = stroke; g.lineWidth = width; g.stroke();
}

function label(g, text, x, y, size = 12, color = '#d9e7e8', align = 'left', weight = 500) {
  g.fillStyle = color; g.textAlign = align; g.textBaseline = 'middle';
  g.font = `${weight} ${size}px ui-sans-serif, system-ui, sans-serif`;
  g.fillText(text, x, y);
}

function drawGrid(g, cx, cy, radius) {
  // In the observer-centred chart, intrinsic circles accumulate toward the rim.
  for (const rho of [0.5, 1, 1.6, 2.5, 4, 6, 9]) {
    ring(g, cx, cy, radius * Math.tanh(rho / 2), 'rgba(151,207,213,.16)', 1);
  }
  for (let i = 0; i < 16; i++) {
    const angle = i * Math.PI / 8;
    line(g, { x: cx, y: cy }, { x: cx + radius * Math.cos(angle), y: cy + radius * Math.sin(angle) }, 'rgba(151,207,213,.08)');
  }
}

function drawPath(g, points, cx, cy, radius, color, width = 2) {
  g.beginPath();
  let began = false;
  for (const point of points) {
    const view = observePoint(state.observer, state.heading, point, 1);
    const pt = pointOnScreen(view, cx, cy, radius);
    if (!began) { g.moveTo(pt.x, pt.y); began = true; } else g.lineTo(pt.x, pt.y);
  }
  g.strokeStyle = color; g.lineWidth = width; g.stroke();
}

function drawBeacon(g, node, index, cx, cy, radius) {
  const view = observePoint(state.observer, state.heading, node.point, state.zoom);
  if (!view.visible) return;
  const p = pointOnScreen(view, cx, cy, radius);
  const post = isRevealed();
  const color = post && index === 1 ? '#f38f74' : node.color;
  const halo = g.createRadialGradient(p.x, p.y, 2, p.x, p.y, 35);
  halo.addColorStop(0, post && index === 1 ? 'rgba(243,143,116,.35)' : 'rgba(137,214,228,.36)');
  halo.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = halo; g.fillRect(p.x - 35, p.y - 35, 70, 70);
  ring(g, p.x, p.y, post && index === 1 ? 13 : 10, color, 2);
  g.beginPath(); g.arc(p.x, p.y, 3.4, 0, Math.PI * 2); g.fillStyle = color; g.fill();
  label(g, node.label, p.x, p.y - 23, 14, '#f3f0e9', 'center', 700);
  label(g, post ? outcomes[index].futureReading.toFixed(2) : '0.50', p.x, p.y + 26, 12, color, 'center', 700);
  if (post && index === 1) {
    for (let i = 0; i < 5; i++) {
      const a = i * 2.4; const r = 18 + i * 3;
      ring(g, p.x + Math.cos(a) * r, p.y + Math.sin(a) * r, 1.6, '#f4aa79', 1.2);
    }
  }
}

function drawCompass(g, cx, cy, radius) {
  ring(g, cx, cy, 17, 'rgba(244,233,211,.78)', 1.4);
  line(g, { x: cx, y: cy + 14 }, { x: cx, y: cy - 19 }, '#f9ce97', 2.3);
  g.beginPath(); g.moveTo(cx, cy - 22); g.lineTo(cx - 5, cy - 13); g.lineTo(cx + 5, cy - 13); g.closePath();
  g.fillStyle = '#f9ce97'; g.fill();
  if (state.loop && ['loop-result', 'debrief'].includes(state.phase)) {
    const turn = state.loop.turn;
    const len = 50;
    // The view rotates with the transported compass, so carried stays up.
    // The old world-fixed direction appears at the opposite relative angle.
    line(g, { x: cx, y: cy }, { x: cx - len * Math.sin(turn), y: cy - len * Math.cos(turn) }, 'rgba(205,220,223,.75)', 2);
    label(g, 'before', cx - len * Math.sin(turn) + 8, cy - len * Math.cos(turn), 11, '#d7e2e0');
    label(g, 'carried', cx + 8, cy - len - 2, 11, '#f9ce97');
  }
}

function drawExternalChart(g, w, h) {
  if (w < 650 || !isWorldPhase()) return;
  const x = w * 0.84, y = h * 0.43;
  const r = Math.min(w * 0.105, h * 0.24);
  label(g, 'OUTSIDE CHART', x, h * 0.13, 11, '#f6cf9e', 'center', 700);
  label(g, 'teaching view', x, h * 0.13 + 19, 11, '#b8ced0', 'center');
  ring(g, x, y, r, 'rgba(228,237,230,.7)', 1.5);
  for (const rho of [1, 2, 4, 7]) ring(g, x, y, r * Math.tanh(rho / 2), 'rgba(151,207,213,.18)');
  line(g, { x: x - r, y }, { x: x + r, y }, 'rgba(151,207,213,.16)');
  line(g, { x, y: y - r }, { x, y: y + r }, 'rgba(151,207,213,.16)');
  if (state.loop) {
    g.beginPath(); let began = false;
    for (let leg = 0; leg < 3; leg++) {
      const segment = disk.geodesic(state.loop.vertices[leg], state.loop.vertices[leg + 1], 32);
      for (const v of segment) {
        const px = x + v.x * r, py = y - v.y * r;
        if (!began) { g.moveTo(px, py); began = true; } else g.lineTo(px, py);
      }
    }
    g.strokeStyle = 'rgba(244,170,121,.95)'; g.lineWidth = 2; g.stroke();
  }
  g.beginPath(); g.arc(x + state.observer.x * r, y - state.observer.y * r, 5, 0, Math.PI * 2);
  g.fillStyle = '#f6cf9e'; g.fill();
  label(g, `path  ${state.path.toFixed(2)}`, x, y + r + 31, 14, '#f3eee4', 'center', 700);
  label(g, `chart radius  ${disk.abs(state.observer).toFixed(5)}`, x, y + r + 52, 11, '#b8ced0', 'center');
  label(g, 'rim = 1 · never reached', x, y + r + 72, 11, '#f6cf9e', 'center');
  if (state.loop && ['loop-result', 'debrief'].includes(state.phase)) {
    const degrees = (state.loop.turn * 180 / Math.PI).toFixed(1);
    label(g, `turn ${degrees}°`, x, y + r + 99, 14, '#f4aa79', 'center', 700);
    if (ui['flat-compare'].checked) label(g, 'flat comparison 0°', x, y + r + 119, 11, '#b8ced0', 'center');
  }
}

function draw() {
  const { g, w, h } = fitCanvas(canvas);
  if (!w || !h) return;
  const background = g.createLinearGradient(0, 0, w, h);
  background.addColorStop(0, '#162b38'); background.addColorStop(0.6, '#14232d'); background.addColorStop(1, '#1a2528');
  g.fillStyle = background; g.fillRect(0, 0, w, h);

  const external = w >= 650 && isWorldPhase();
  const cx = external ? w * 0.39 : w * 0.5;
  const cy = h * 0.51;
  const radius = Math.min(h * 0.43, w * (external ? 0.31 : 0.43));
  const diskGlow = g.createRadialGradient(cx, cy, radius * 0.1, cx, cy, radius * 1.17);
  diskGlow.addColorStop(0, 'rgba(47,86,104,.30)');
  diskGlow.addColorStop(.78, 'rgba(45,82,99,.12)');
  diskGlow.addColorStop(1, 'rgba(113,184,185,0)');
  g.fillStyle = diskGlow; g.fillRect(cx - radius * 1.2, cy - radius * 1.2, radius * 2.4, radius * 2.4);

  g.save();
  g.beginPath(); g.arc(cx, cy, radius, 0, Math.PI * 2); g.clip();
  g.fillStyle = '#12242f'; g.fillRect(cx - radius, cy - radius, radius * 2, radius * 2);
  drawGrid(g, cx, cy, radius);

  // The sensor is a finite wedge; the disk frame is a teaching overlay.
  const aperture = Math.PI / (3 * state.zoom);
  const rangeRadius = radius * Math.tanh(sensorRange() / 2);
  const wedge = g.createRadialGradient(cx, cy, 0, cx, cy, rangeRadius);
  wedge.addColorStop(0, 'rgba(101,188,208,.18)'); wedge.addColorStop(1, 'rgba(101,188,208,.02)');
  g.beginPath(); g.moveTo(cx, cy); g.arc(cx, cy, rangeRadius, -Math.PI / 2 - aperture, -Math.PI / 2 + aperture); g.closePath();
  g.fillStyle = wedge; g.fill();
  for (const sign of [-1, 1]) {
    const a = -Math.PI / 2 + sign * aperture;
    line(g, { x: cx, y: cy }, { x: cx + rangeRadius * Math.cos(a), y: cy + rangeRadius * Math.sin(a) }, 'rgba(147,216,228,.38)', 1.4);
  }
  g.beginPath(); g.arc(cx, cy, rangeRadius, -Math.PI / 2 - aperture, -Math.PI / 2 + aperture);
  g.strokeStyle = 'rgba(147,216,228,.42)'; g.lineWidth = 1.3; g.stroke();

  for (const star of world.stars) {
    const reading = observePoint(state.observer, state.heading, star.point, state.zoom);
    if (!reading.visible) continue;
    const p = pointOnScreen(reading, cx, cy, radius);
    const size = 0.6 + 1.8 * star.strength * (1 - Math.min(.8, reading.intrinsicDistance / 10));
    g.beginPath(); g.arc(p.x, p.y, size, 0, Math.PI * 2);
    g.fillStyle = `rgba(210,230,226,${0.35 + 0.45 * star.strength})`; g.fill();
  }
  for (const mark of isWorldPhase() ? world.landmarks : []) {
    const reading = observePoint(state.observer, state.heading, mark.point, state.zoom);
    if (!reading.visible) continue;
    const p = pointOnScreen(reading, cx, cy, radius);
    ring(g, p.x, p.y, 6, 'rgba(244,203,152,.85)', 1.5);
    g.beginPath(); g.arc(p.x, p.y, 2, 0, Math.PI * 2); g.fillStyle = '#f8d6a9'; g.fill();
    if (w > 520) label(g, mark.label, p.x + 10, p.y - 8, 10, '#d9dad0');
  }
  if (isTrialPhase()) twin.forEach((node, i) => drawBeacon(g, node, i, cx, cy, radius));
  if (state.loop && ['looping', 'loop-result', 'debrief'].includes(state.phase)) {
    for (let leg = 0; leg < 3; leg++) {
      drawPath(g, disk.geodesic(state.loop.vertices[leg], state.loop.vertices[leg + 1], 36), cx, cy, radius, 'rgba(244,170,121,.78)', 2.2);
    }
    label(g, 'PLOTTED ROUTE · teaching overlay', 22, 48, 10, '#f4aa79', 'left', 700);
  }
  drawCompass(g, cx, cy, radius);
  g.restore();
  ring(g, cx, cy, radius, 'rgba(178,224,222,.8)', 1.6);
  ring(g, cx, cy, radius + 5, 'rgba(178,224,222,.13)', 6);

  label(g, 'HERE', cx, cy + 33, 10, '#f9ce97', 'center', 700);
  label(g, `ZOOM ${state.zoom}  ·  ${Math.round(120 / state.zoom)}°`, 22, h - 26, 11, '#b8ced0', 'left', 700);
  if (state.phase === 'ready') {
    g.fillStyle = 'rgba(10,20,27,.69)'; g.fillRect(0, 0, w, h);
    label(g, 'YOU CAN ONLY SEE FROM HERE', w / 2, h / 2 - 55, Math.min(20, w / 23), '#f3eee4', 'center', 700);
    label(g, 'YOUR FIRST MEASUREMENT AWAITS', w / 2, h / 2 - 27, 13, '#9eced3', 'center');
  }
  drawExternalChart(g, w, h);
}

function renderSoon() {
  if (frame !== null) return;
  frame = requestAnimationFrame(() => { frame = null; draw(); });
}

function reset(focus = false) {
  state = fresh();
  ui['slow-mode'].checked = false;
  ui['flat-compare'].checked = false;
  ui['event-log'].replaceChildren();
  const row = document.createElement('p'); row.dataset.placeholder = 'true'; row.textContent = 'Your record begins when you enter.';
  ui['event-log'].append(row);
  prompt('Your instruments are waiting. Enter to see what they can reach.');
  updateUI();
  if (focus) { focusNext(ui['start-button']); showScene(); }
}

ui['start-button'].addEventListener('click', enter);
ui['start-overlay'].addEventListener('click', enter);
ui['intro-start'].addEventListener('click', (event) => {
  event.preventDefault();
  if (state.phase === 'ready') enter(); else showScene();
});
ui['reset-button'].addEventListener('click', () => reset(true));
ui['scan-button'].addEventListener('click', scan);
ui['act-button'].addEventListener('click', intervene);
ui['advance-button'].addEventListener('click', continueStory);
ui['loop-button'].addEventListener('click', startLoop);
ui['pause-button'].addEventListener('click', () => {
  state.paused = !state.paused;
  if (!state.paused && state.animation) queueTick();
  prompt(state.paused ? 'Paused. Your present reading and path are held.' : 'Resumed. Continue from the same point.');
  updateUI();
});
for (const button of document.querySelectorAll('[data-predict]')) {
  button.addEventListener('click', () => choosePrediction(button.dataset.predict));
}
for (const button of document.querySelectorAll('[data-move]')) {
  button.addEventListener('click', () => moveCommand(button.dataset.move));
}
for (const button of document.querySelectorAll('[data-look]')) {
  button.addEventListener('click', () => look(button.dataset.look));
}
for (const button of document.querySelectorAll('[data-zoom]')) {
  button.addEventListener('click', () => zoom(button.dataset.zoom));
}
function settleForReducedMotion() {
  const anim = state.animation;
  if (!anim || !isReduced()) { updateUI(); return; }
  if (anim.kind === 'journey') {
    state.animation = null;
    state.phase = state.edgeWitnessed ? 'horizon' : 'journey';
    prompt(`Motion stopped at step ${state.steps}. The current chart radius is ${disk.abs(state.observer).toFixed(5)}. Continue one step at a time.`);
    log(`Step-by-step mode stopped the guided route at step ${state.steps}; no extra travel was added.`);
    updateUI();
  } else {
    for (let i = anim.index + 1; i < anim.route.length; i++) {
      state.path += disk.distance(i === anim.index + 1 ? state.observer : anim.route[i - 1], anim.route[i]);
    }
    finishLoop();
  }
}

ui['slow-mode'].addEventListener('change', settleForReducedMotion);
ui['flat-compare'].addEventListener('change', updateUI);
motionPreference.addEventListener('change', settleForReducedMotion);
window.addEventListener('resize', renderSoon);
new ResizeObserver(renderSoon).observe(canvas);

canvas.addEventListener('wheel', (event) => {
  if (document.activeElement !== canvas || !canNavigate() || state.paused || state.animation) return;
  const next = Math.max(1, Math.min(8, state.zoom + (event.deltaY < 0 ? 1 : -1)));
  if (next === state.zoom) return;
  event.preventDefault();
  zoom(event.deltaY < 0 ? 'in' : 'out');
}, { passive: false });

let dragging = false, lastX = 0;
canvas.addEventListener('pointerdown', (event) => {
  if (state.phase === 'ready') { enter(); return; }
  dragging = true; lastX = event.clientX; canvas.setPointerCapture(event.pointerId); canvas.focus();
});
canvas.addEventListener('pointermove', (event) => {
  if (!dragging || !canNavigate() || state.paused || state.animation) return;
  const delta = event.clientX - lastX;
  if (Math.abs(delta) < 5) return;
  state.heading += delta * 0.006;
  lastX = event.clientX;
  updateUI();
});
canvas.addEventListener('pointerup', () => { dragging = false; });
canvas.addEventListener('pointercancel', () => { dragging = false; });

document.addEventListener('keydown', (event) => {
  if (event.altKey || event.ctrlKey || event.metaKey) return;
  if (document.activeElement !== canvas) return;
  const map = { w: 'forward', ArrowUp: 'forward', s: 'back', ArrowDown: 'back', a: 'left', ArrowLeft: 'left', d: 'right', ArrowRight: 'right' };
  if (map[event.key] && canNavigate()) { event.preventDefault(); moveCommand(map[event.key]); return; }
  if ((event.key === 'q' || event.key === 'Q') && canNavigate()) { event.preventDefault(); look('left'); return; }
  if ((event.key === 'e' || event.key === 'E') && canNavigate()) { event.preventDefault(); look('right'); return; }
  if ((event.key === '+' || event.key === '=') && canNavigate()) { event.preventDefault(); zoom('in'); return; }
  if ((event.key === '-' || event.key === '_') && canNavigate()) { event.preventDefault(); zoom('out'); return; }
  if (event.code === 'Space') { event.preventDefault(); scan(); return; }
  if (event.key === 'Enter') { event.preventDefault(); state.phase === 'ready' ? enter() : intervene(); }
});

reset();
