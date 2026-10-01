import { simulate } from './radiation-model.mjs';

const canvas = document.querySelector('#rad-chart');
const ctx = canvas.getContext('2d');
const gapInput = document.querySelector('#rad-gap');
const tauInput = document.querySelector('#rad-tau');
const modeButtons = [...document.querySelectorAll('[data-rad-mode]')];
const challengeButton = document.querySelector('#rad-challenge');
const replayButton = document.querySelector('#rad-replay');
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
let mode = 'curve';
let challenge = false;
let progress = 1;
let animation = 0;
let width = 0, height = 0;
let warm, cool;

function numeric(id, value) { document.querySelector(id).textContent = value.toFixed(3); }

function update() {
  const gap = Number(gapInput.value);
  const tau = Number(tauInput.value);
  document.querySelector('#rad-gap-out').textContent = gap.toFixed(2);
  document.querySelector('#rad-tau-out').textContent = tau.toFixed(2);
  warm = simulate({ order: 'large-small', gap, tau, model: mode, challenge });
  cool = simulate({ order: 'small-large', gap, tau, model: mode, challenge });
  numeric('#rad-state-a', warm.afterPair.x);
  numeric('#rad-state-b', cool.afterPair.x);
  numeric('#rad-response-a', challenge ? warm.final.H : warm.afterPair.H);
  numeric('#rad-response-b', challenge ? cool.final.H : cool.afterPair.H);
  document.querySelector('#rad-response-label').textContent = challenge ?
    'Model response after the shared challenge' : 'Model response after the pair';
  document.querySelector('#rad-chart-status').textContent = challenge ? 'A COMMON NEXT TEST' : 'TWO HISTORIES';
  const pairedDifference = Math.abs(warm.afterPair.H - cool.afterPair.H);
  const futureDifference = Math.abs(warm.final.H - cool.final.H);
  const interpretation = document.querySelector('#rad-interpretation');
  if (challenge && mode === 'quadratic') {
    interpretation.innerHTML = '<span class="tag tag-P">P</span> The quadratic pair has the same response ledger within numerical precision. Its retained states differ; the same next exposure makes the future ledgers differ by ' + futureDifference.toFixed(3) + ' in this model.';
  } else if (challenge) {
    interpretation.innerHTML = '<span class="tag tag-D">D</span> After the same next exposure, these histories give different model ledgers (' + warm.final.H.toFixed(3) + ' versus ' + cool.final.H.toFixed(3) + '). That is a conditional prediction to test, not a measured risk.';
  } else if (mode === 'quadratic') {
    interpretation.innerHTML = '<span class="tag tag-P">P</span> The two-period ledgers agree within numerical precision, yet the retained states differ. Apply the same next exposure to reveal what that apparently equal reading missed.';
  } else if (pairedDifference < 0.0005) {
    interpretation.innerHTML = '<span class="tag tag-D">D</span> At this timing, the modelled pair responses are nearly equal. Compare the retained states or apply the same next exposure; a near match is not proof of no memory.';
  } else {
    interpretation.innerHTML = '<span class="tag tag-D">D</span> Same total; different modelled two-period responses (' + warm.afterPair.H.toFixed(3) + ' versus ' + cool.afterPair.H.toFixed(3) + '). The later input arrived into a different retained state.';
  }
  progress = 1;
  cancelAnimationFrame(animation);
  draw();
}

function fitCanvas() {
  const box = canvas.getBoundingClientRect();
  width = box.width;
  height = box.height;
  const dpr = Math.min(devicePixelRatio || 1, 2);
  canvas.width = Math.round(width * dpr);
  canvas.height = Math.round(height * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  draw();
}

function draw() {
  if (!warm || !width || !height) return;
  const mobile = width < 570;
  const left = mobile ? 34 : 72;
  const right = mobile ? 17 : 36;
  const plotWidth = width - left - right;
  const lastT = warm.final.t;
  const showUntil = lastT * progress;
  const xAt = t => left + t / lastT * plotWidth;
  const stateTop = mobile ? 119 : 139;
  const stateBottom = height * 0.53;
  const ledgerTop = stateBottom + (mobile ? 27 : 40);
  const ledgerBottom = height - (mobile ? 58 : 70);
  const maxState = Math.max(0.85, ...[warm, cool].flatMap(run => run.points.map(p => p.x))) * 1.08;
  const maxLedger = Math.max(0.7, warm.final.H, cool.final.H) * 1.09;
  const yState = value => stateBottom - value / maxState * (stateBottom - stateTop);
  const yLedger = value => ledgerBottom - value / maxLedger * (ledgerBottom - ledgerTop);

  ctx.clearRect(0, 0, width, height);
  const wash = ctx.createLinearGradient(0, 0, width, height);
  wash.addColorStop(0, '#102c34'); wash.addColorStop(0.55, '#0b2028'); wash.addColorStop(1, '#10252d');
  ctx.fillStyle = wash; ctx.fillRect(0, 0, width, height);
  ctx.strokeStyle = 'rgba(139,184,183,.105)'; ctx.lineWidth = 1;
  for (let i = 0; i <= 10; i++) {
    const x = left + plotWidth * i / 10;
    ctx.beginPath(); ctx.moveTo(x, 37); ctx.lineTo(x, ledgerBottom); ctx.stroke();
  }
  for (const [top, bottom] of [[stateTop, stateBottom], [ledgerTop, ledgerBottom]]) {
    for (let i = 0; i <= 4; i++) {
      const y = top + (bottom - top) * i / 4;
      ctx.beginPath(); ctx.moveTo(left, y); ctx.lineTo(left + plotWidth, y); ctx.stroke();
    }
  }
  ctx.fillStyle = '#a7c2c1'; ctx.font = `700 ${mobile ? 10 : 11}px ui-monospace, Consolas, monospace`;
  ctx.fillText('DOSE RATE', left, 51);
  ctx.fillText('RETAINED STATE x(t)', left, stateTop - 13);
  ctx.fillText('ACCUMULATED RESPONSE H(t)', left, ledgerTop - 11);
  ctx.fillStyle = '#87aaa9'; ctx.font = `600 ${mobile ? 9 : 10}px ui-monospace, Consolas, monospace`;
  ctx.fillText('0', mobile ? 12 : 40, stateBottom + 3);
  ctx.fillText('0', mobile ? 12 : 40, ledgerBottom + 3);
  ctx.fillText('TIME →', left + plotWidth - (mobile ? 43 : 50), ledgerBottom + 27);
  const afterPair = xAt(warm.afterPair.t);
  ctx.save(); ctx.setLineDash([5, 6]); ctx.strokeStyle = '#f3c4977f';
  ctx.beginPath(); ctx.moveTo(afterPair, 39); ctx.lineTo(afterPair, ledgerBottom); ctx.stroke();
  if (challenge && warm.beforeChallenge) {
    const nextAt = xAt(warm.beforeChallenge.t);
    ctx.strokeStyle = '#a1e7df9c'; ctx.beginPath(); ctx.moveTo(nextAt, 39); ctx.lineTo(nextAt, ledgerBottom); ctx.stroke();
    ctx.fillStyle = '#c5eee5'; ctx.font = `700 ${mobile ? 8 : 10}px ui-monospace, Consolas, monospace`;
    ctx.fillText(mobile ? 'NEXT' : 'SAME NEXT EXPOSURE', Math.min(nextAt + 5, width - (mobile ? 44 : 150)), 52);
  }
  ctx.restore();
  for (const [run, row, color] of [[warm, 69, '#f3b77d'], [cool, 93, '#85d9da']]) {
    for (const window of run.windows) {
      if (window.dose <= 0 || window.start >= showUntil) continue;
      const start = xAt(window.start);
      const end = xAt(Math.min(window.end, showUntil));
      const barHeight = window.kind === 'challenge' ? 5 : window.dose > 0.5 ? 12 : 5;
      ctx.fillStyle = color + (window.kind === 'challenge' ? '82' : window.dose > 0.5 ? 'ed' : '92');
      ctx.fillRect(start, row + 12 - barHeight, Math.max(1, end - start), barHeight);
    }
    ctx.fillStyle = color; ctx.font = `700 ${mobile ? 10 : 11}px ui-monospace, Consolas, monospace`;
    ctx.fillText(row === 69 ? 'A' : 'B', mobile ? 12 : 43, row + 11);
  }
  if (progress > 0.03) {
    for (const [key, mapper] of [['x', yState], ['H', yLedger]]) {
      const partialWarm = warm.points.filter((p, i) => i % 3 === 0 && p.t <= showUntil);
      const partialCool = cool.points.filter((p, i) => i % 3 === 0 && p.t <= showUntil);
      if (partialWarm.length > 1 && partialCool.length > 1) {
        ctx.beginPath();
        partialWarm.forEach((p, i) => i ? ctx.lineTo(xAt(p.t), mapper(p[key])) : ctx.moveTo(xAt(p.t), mapper(p[key])));
        [...partialCool].reverse().forEach(p => ctx.lineTo(xAt(p.t), mapper(p[key])));
        ctx.closePath(); ctx.fillStyle = key === 'x' ? '#86d9dc12' : '#f3b77d0f'; ctx.fill();
      }
      for (const [run, color] of [[warm, '#f3b77d'], [cool, '#85d9da']]) {
        ctx.beginPath();
        let found = false;
        for (let i = 0; i < run.points.length; i += 2) {
          const p = run.points[i];
          if (p.t > showUntil) break;
          if (!found) { ctx.moveTo(xAt(p.t), mapper(p[key])); found = true; }
          else ctx.lineTo(xAt(p.t), mapper(p[key]));
        }
        ctx.strokeStyle = color; ctx.lineWidth = mobile ? 2.2 : 2.8;
        ctx.shadowColor = color; ctx.shadowBlur = 13; ctx.stroke(); ctx.shadowBlur = 0;
      }
    }
  }
  if (progress >= 0.999) {
    for (const [run, color] of [[warm, '#f3b77d'], [cool, '#85d9da']]) {
      for (const [point, mapper, key] of [[run.afterPair, yState, 'x'], [run.afterPair, yLedger, 'H']]) {
        ctx.beginPath(); ctx.arc(xAt(point.t), mapper(point[key]), mobile ? 3 : 4, 0, 2 * Math.PI);
        ctx.fillStyle = color; ctx.shadowColor = color; ctx.shadowBlur = 12; ctx.fill(); ctx.shadowBlur = 0;
      }
    }
  }
}

function replay() {
  cancelAnimationFrame(animation);
  if (reducedMotion.matches) { progress = 1; draw(); return; }
  const start = performance.now();
  const run = now => {
    progress = Math.min(1, (now - start) / 1800);
    draw();
    if (progress < 1) animation = requestAnimationFrame(run);
  };
  progress = 0; draw(); animation = requestAnimationFrame(run);
}

for (const button of modeButtons) button.addEventListener('click', () => {
  mode = button.dataset.radMode;
  for (const other of modeButtons) other.setAttribute('aria-pressed', String(other === button));
  update();
});
for (const input of [gapInput, tauInput]) input.addEventListener('input', update);
challengeButton.addEventListener('click', () => {
  challenge = !challenge;
  challengeButton.setAttribute('aria-pressed', String(challenge));
  challengeButton.innerHTML = challenge ? 'Hide the next exposure <span aria-hidden="true">↶</span>' :
    'Apply the same next exposure <span aria-hidden="true">→</span>';
  update(); replay();
});
replayButton.addEventListener('click', replay);

const horizonSteps = [
  ['Only the total is known', 'Many dose-rate histories fit one number. Their predicted retained states and later responses need not agree.', 'Uncertainty remains: timing, recovery, person, endpoint, model fit.'],
  ['The order and rate are recorded', 'Histories that differ in timing can now be separated. A sum-only description has lost information this record keeps.', 'Uncertainty remains: recovery, person, endpoint, model fit.'],
  ['Recovery is measured', 'A separately tested recovery law can constrain the state entering the next exposure.', 'Uncertainty remains: person, endpoint, model fit.'],
  ['The observer is specified', 'Age, organ, health, care conditions and past exposure can narrow which comparisons are relevant.', 'Uncertainty remains: endpoint variation, model fit and future chance.'],
  ['Future outcomes are tested', 'Prospective matched challenges can show whether the proposed state and response rule actually predict.', 'Uncertainty remains: sampling error, unmeasured context, model failure and future chance.'],
];
const horizonButtons = [...document.querySelectorAll('[data-horizon]')];
for (const button of horizonButtons) button.addEventListener('click', () => {
  const index = Number(button.dataset.horizon);
  horizonButtons.forEach(other => other.setAttribute('aria-pressed', String(other === button)));
  document.querySelector('.rad-fan').style.setProperty('--narrow', [1, .76, .54, .36, .2][index]);
  document.querySelector('#rad-horizon-step').textContent = `0${index + 1} / 05`;
  document.querySelector('#rad-horizon-title').textContent = horizonSteps[index][0];
  document.querySelector('#rad-horizon-copy').textContent = horizonSteps[index][1];
  document.querySelector('#rad-horizon-remaining').textContent = horizonSteps[index][2];
});

const fukuButtons = [...document.querySelectorAll('[data-fuku]')];
for (const button of fukuButtons) button.addEventListener('click', () => {
  fukuButtons.forEach(other => other.setAttribute('aria-pressed', String(other === button)));
  document.querySelector('#rad-fuku-then').hidden = button.dataset.fuku !== 'then';
  document.querySelector('#rad-fuku-later').hidden = button.dataset.fuku !== 'later';
});

update();
new ResizeObserver(fitCanvas).observe(canvas);
