/* Inside: a situated observer receives only the model's public projection. */
import { createValley, stepValley, observeValley, revealValley, VALLEY_RULES } from './valley-world.mjs';
import { drawValley } from './valley-view.mjs';

const $ = (id) => document.getElementById(id);
const ids = ['entry','simulation','experience','debrief','era-label','day-label','days-remaining',
  'place-label','scene-line','travel-btn','inspect-btn','listen-btn','decision','outcome',
  'outcome-title','outcome-copy','compare-btn','next-btn','replay-btn','identity-label',
  'identity-copy','seen-copy','memory-copy','inference-copy','learned-list','record-list',
  'lineage-list','cause-title','cause-copy','estuary-record','ridge-record','alternative-list',
  'debrief-lesson','debrief-next','valley-canvas'];
const ui = Object.fromEntries(ids.map((id) => [id, $(id)]));
const inquiry = document.querySelector('.inside-inquiry');
const inquiryHead = document.querySelector('.inside-actions-head');
const decisionCopy = ui.decision.querySelector('p');
const coordinateCopy = document.querySelector('[data-choice="coordinate"] span');
const eraSteps = [...document.querySelectorAll('[data-era-step]')];
const motionPreference = matchMedia('(prefers-reduced-motion: reduce)');
const choices = ['open', 'hold', 'coordinate'];
const choiceNames = { open: 'Open it', hold: 'Keep it shut', coordinate: 'Seek a joint response' };
const placeNames = { estuary: 'Estuary', ridge: 'Ridge' };
let world = null;
let checkpoint = null;
let reading = null;
let compared = false;
let animationFrame = null;
let lastFrameTime = 0;

function put(id, value) { ui[id].textContent = String(value ?? ''); }
function item(list, value, tag = 'li') {
  const node = document.createElement(tag);
  node.textContent = value;
  list.append(node);
  return node;
}
function press(element, handler) {
  // Pointerdown also works in the in-app browser. Ignore its follow-up click;
  // retain native keyboard and assistive-technology click activation.
  let lastPointer = -Infinity;
  element.addEventListener('pointerdown', (event) => {
    if (event.button !== 0 || element.disabled) return;
    lastPointer = event.timeStamp;
    handler(event);
  });
  element.addEventListener('click', (event) => {
    if (event.detail > 0 && event.timeStamp - lastPointer < 1000) {
      event.preventDefault();
      return;
    }
    if (!element.disabled) handler(event);
  });
}
function show(element, section) {
  requestAnimationFrame(() => {
    element.tabIndex = -1;
    section.scrollIntoView({ block: 'start' });
    element.focus({ preventScroll: true });
  });
}
function draw(time = performance.now()) {
  if (reading) drawValley(ui['valley-canvas'], reading, { time, reducedMotion: motionPreference.matches });
}
function animate(time) {
  animationFrame = requestAnimationFrame(animate);
  if (!reading || motionPreference.matches || document.hidden || time - lastFrameTime < 40) return;
  lastFrameTime = time;
  draw(time);
}

function start(home, seed = 1) {
  world = createValley(home, seed);
  checkpoint = world;
  compared = false;
  render();
  if (animationFrame === null) animationFrame = requestAnimationFrame(animate);
  show(ui['scene-line'], ui.experience);
}
function act(action) {
  if (!world) return;
  const next = stepValley(world, action);
  if (next === world) return;
  world = next;
  compared = false;
  render();
  if (reading.phase === 'result') show(ui['outcome-title'], ui.outcome);
}
function renderLearned(o) {
  const list = ui['learned-list'];
  list.replaceChildren();
  if (!o.learned.length) item(list, 'Nothing beyond your starting view yet.');
  for (const entry of o.learned) {
    item(list, `Day ${entry.day}, ${placeNames[entry.location]} ${entry.kind}: ${entry.text}`);
  }
  const record = ui['record-list'];
  record.replaceChildren();
  for (const entry of o.journal) item(record, `Day ${entry.day}: ${entry.text}`);
}
function renderLineage(o, revealedRecord = null) {
  const list = ui['lineage-list'];
  list.replaceChildren();
  for (let era = 0; era < VALLEY_RULES.generations; era++) {
    const article = document.createElement('article');
    if (era === o.era) article.classList.add('current');
    item(article, `Generation ${era + 1} · Year ${era * VALLEY_RULES.yearsBetweenGenerations}`, 'b');
    const inherited = o.lineage.find((entry) => entry.year === era * VALLEY_RULES.yearsBetweenGenerations);
    const currentAccount = revealedRecord ?? (o.phase === 'result'
      ? 'Your record is sealed until you compare both accounts.'
      : 'You are here. This account is still being made.');
    item(article, inherited?.text ?? (era === o.era ? currentAccount : 'Not yet lived.'), 'p');
    list.append(article);
  }
}
function render() {
  if (!world) return;
  reading = observeValley(world);
  const o = reading;
  const result = o.phase === 'result';
  ui.entry.hidden = true;
  ui.simulation.hidden = false;
  ui.debrief.hidden = !compared;
  put('era-label', `${o.eraLabel} · Generation ${o.era + 1} of ${VALLEY_RULES.generations}`);
  put('day-label', o.dayLabel);
  put('days-remaining', result ? 'A response has been made' : o.day >= VALLEY_RULES.lastInquiryDay
    ? 'Choose an action now' : `${VALLEY_RULES.lastInquiryDay - o.day} day${VALLEY_RULES.lastInquiryDay - o.day === 1 ? '' : 's'} left to investigate`);
  for (const step of eraSteps) {
    const era = Number(step.dataset.eraStep);
    step.classList.toggle('done', era < o.era);
    step.classList.toggle('current', era === o.era);
    step.setAttribute('aria-label', `Generation ${era + 1}${era < o.era ? ' completed' : era === o.era ? ' current' : ' forthcoming'}`);
  }
  put('place-label', `${placeNames[o.location].toUpperCase()} · ${o.location === 'estuary' ? 'DOWNRIVER' : 'UPRIVER'}`);
  put('scene-line', o.scene.eventCue || o.sceneLine);
  inquiryHead.hidden = result;
  inquiry.hidden = result;
  ui.decision.hidden = result;
  ui.outcome.hidden = !result;
  ui['travel-btn'].disabled = !o.available.travel;
  ui['inspect-btn'].disabled = !o.available.inspect;
  ui['listen-btn'].disabled = !o.available.listen;
  for (const button of document.querySelectorAll('[data-choice]')) {
    button.disabled = !o.available.decide[button.dataset.choice];
  }
  decisionCopy.textContent = `Decide now or spend a day investigating. Under this valley’s rules, a response on Day ${VALLEY_RULES.lateResponseAt} or later dries more downstream fields. A joint response uses one extra day and a supply unit.`;
  coordinateCopy.textContent = o.available.coordinationReady
    ? `A shared plan can form. It uses one day and a supply unit; response on Day ${o.available.coordinationResponseDay}.`
    : 'A shared plan needs contact plus a Ridge gauge reading or both local accounts. Without that, the gate stays shut.';
  put('identity-label', o.identity.label);
  put('identity-copy', `${o.identity.copy}${o.location === o.home ? '' : ` You are now visiting ${placeNames[o.location]}, carrying your home account.`}`);
  put('seen-copy', o.seen);
  put('memory-copy', o.inherited);
  put('inference-copy', o.inference);
  renderLearned(o);
  renderLineage(o);
  if (result) {
    put('outcome-title', o.outcome.title);
    put('outcome-copy', `${o.outcome.copy} This is what reached you at ${placeNames[o.location]}; the other bank’s full result is not in your present view.`);
    const nextName = o.available.next ? 'Enter the next generation' : 'Begin from the other bank';
    put('next-btn', nextName);
    put('debrief-next', nextName);
  }
  draw();
}
function effects(outcome) {
  const e = outcome.effects;
  return `Estuary homes flooded: ${e.estuaryHomesFlooded}; dry fields: ${e.estuaryFieldsDry}. Ridge dry fields: ${e.ridgeFieldsDry}; gate repairs: ${e.gateRepairsNeeded}. Joint supplies spent: ${e.jointSuppliesSpent}. Response Day ${outcome.responseDay}.`;
}
function compare() {
  if (!world || reading.phase !== 'result') return;
  const r = revealValley(world);
  compared = true;
  ui.debrief.hidden = false;
  if (r.cause === 'pressure') {
    put('cause-title', 'The barrier held a dangerous crest.');
    put('cause-copy', 'The gate was under high stress. In this authored world, fully opening it at once sent a damaging surge downstream. The local closed-gate view did not expose that cause.');
  } else {
    put('cause-title', 'The barrier retained usable water.');
    put('cause-copy', 'The gate stress was low. In this authored world, water was being held above the gate. Keeping it shut dried downstream fields. The local closed-gate view looked the same as in the high-stress world.');
  }
  put('estuary-record', `Inherited account: ${r.inheritedRecords.estuary.text} After this action, Estuary passed on: ${r.records.estuary.at(-1)?.text ?? 'No new record.'}`);
  put('ridge-record', `Inherited account: ${r.inheritedRecords.ridge.text} After this action, Ridge passed on: ${r.records.ridge.at(-1)?.text ?? 'No new record.'}`);
  renderLineage(reading, r.records[reading.home].at(-1)?.text ?? 'No new record.');
  const list = ui['alternative-list'];
  list.replaceChildren();
  for (const choice of choices) {
    const article = document.createElement('article');
    item(article, `${choiceNames[choice]}${choice === r.chosen.choice ? ' · your action' : ''}`, 'b');
    item(article, `With the actual ${r.cause === 'pressure' ? 'high-stress' : 'water-retention'} cause: ${effects(r.counterfactuals.sameCause[choice])}`, 'p');
    item(article, `With the other possible cause under the same visible closure: ${effects(r.counterfactuals.oppositeCause.choices[choice])}`, 'p');
    list.append(article);
  }
  put('debrief-lesson', 'These alternatives follow the valley’s authored rules. The same local sign hid different causes and possible outcomes. Each community passed on the consequences it could witness. Listening can tell you what another person says; it does not give you their whole experience or erase material conflicts.');
  show(ui['cause-title'], ui.debrief);
}
function nextGeneration() {
  if (!world || reading.phase !== 'result') return;
  world = reading.available.next ? stepValley(world, { type: 'next' })
    : createValley(world.home === 'estuary' ? 'ridge' : 'estuary', world.seed);
  checkpoint = world;
  compared = false;
  render();
  show(ui['scene-line'], ui.experience);
}
function replay() {
  if (!checkpoint) return;
  world = checkpoint;
  compared = false;
  render();
  show(ui['scene-line'], ui.experience);
}

for (const button of document.querySelectorAll('[data-home]')) press(button, () => start(button.dataset.home));
press(ui['travel-btn'], () => act({ type: 'travel' }));
press(ui['inspect-btn'], () => act({ type: 'inspect' }));
press(ui['listen-btn'], () => act({ type: 'listen' }));
for (const button of document.querySelectorAll('[data-choice]')) {
  press(button, () => act({ type: 'decide', choice: button.dataset.choice }));
}
press(ui['compare-btn'], compare);
press(ui['next-btn'], nextGeneration);
press(ui['replay-btn'], replay);
press(ui['debrief-next'], nextGeneration);
new ResizeObserver(() => draw()).observe(ui['valley-canvas']);
motionPreference.addEventListener('change', () => draw());
