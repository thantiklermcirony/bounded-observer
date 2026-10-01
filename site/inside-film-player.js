import { FILM_SCENES, drawFilmFrame } from './inside-film.mjs?v=film6';

const $ = (id) => document.getElementById(id);
const canvas = $('film-canvas');
const scrub = $('film-scrub');
const start = $('film-start');
const play = $('film-play');
const next = $('film-next');
const audio = $('film-audio');
const sound = $('film-sound');
const reduced = matchMedia('(prefers-reduced-motion: reduce)');
const duration = FILM_SCENES.at(-1).end;
const screenNotes = [
  'Constructed story · Situated observer',
  'Constructed story · Inherited record',
  'Constructed story · Downriver account',
  'Constructed story · Upriver account',
  'Constructed story · Observed crest',
  'Constructed story · A true observation can leave a cause unknown',
  'Constructed projections · Outcomes not yet known',
  'Constructed ending · Joint action remains a choice with costs',
];
let seconds = 0;
let playing = false;
let started = false;
let lastFrame = 0;
let sceneIndex = -1;
let pointerX = 0;
let pointerY = 0;
let soundOn = true;
let audioActive = false;
let audioFailed = false;

function clock(value) {
  const whole = Math.floor(value);
  return String(Math.floor(whole / 60)).padStart(2, '0') + ':' +
    String(whole % 60).padStart(2, '0');
}

function sceneAt(value) {
  return Math.max(0, FILM_SCENES.findIndex((scene, index) =>
    value >= scene.start && (value < scene.end || index === FILM_SCENES.length - 1)));
}

function draw() {
  drawFilmFrame(canvas, seconds, { reducedMotion: reduced.matches, pointerX, pointerY });
}

function update() {
  const index = sceneAt(seconds);
  if (index !== sceneIndex) {
    sceneIndex = index;
    const scene = FILM_SCENES[index];
    $('film-scene-label').textContent = String(index + 1).padStart(2, '0') +
      ' / ' + String(FILM_SCENES.length).padStart(2, '0') + ' · ' + scene.title.toUpperCase();
    $('film-caption').textContent = scene.caption;
    $('film-claim').textContent = screenNotes[index];
  }
  scrub.value = String(seconds);
  $('film-time').textContent = clock(seconds) + ' / ' + clock(duration);
  play.textContent = playing ? 'Pause' : seconds >= duration ? 'Replay' : 'Play';
  play.setAttribute('aria-label', playing ? 'Pause visual essay' :
    seconds >= duration ? 'Replay visual essay' : 'Play visual essay');
  start.hidden = started;
  draw();
}

function updateSound() {
  sound.disabled = audioFailed;
  sound.textContent = audioFailed ? 'Sound unavailable' : soundOn ? 'Sound on' : 'Sound off';
  sound.setAttribute('aria-label', audioFailed ? 'Audio unavailable; film remains playable with captions' :
    soundOn ? 'Turn sound off' : 'Turn sound on');
  sound.setAttribute('aria-pressed', String(soundOn && !audioFailed));
}

function audioFailure() {
  audioActive = false;
  audioFailed = true;
  lastFrame = 0;
  updateSound();
}

function startAudio() {
  if (audioFailed) return;
  audio.muted = !soundOn;
  try {
    audio.currentTime = Math.min(seconds, duration - .001);
    audioActive = true;
    const attempt = audio.play();
    if (attempt && typeof attempt.catch === 'function') {
      attempt.catch(() => { if (audio.paused) audioFailure(); });
    }
  } catch {
    audioFailure();
  }
}

function pause() {
  playing = false;
  audio.pause();
  lastFrame = 0;
  update();
}

function begin() {
  if (seconds >= duration) seconds = 0;
  started = true;
  playing = true;
  lastFrame = 0;
  startAudio();
  update();
}

function frame(now) {
  if (playing) {
    if (audioActive) seconds = Math.min(duration, audio.currentTime);
    else if (lastFrame) seconds = Math.min(duration, seconds + Math.min(.15, (now - lastFrame) / 1000));
    lastFrame = now;
    if (seconds >= duration) {
      playing = false;
      audio.pause();
      lastFrame = 0;
    }
    update();
  }
  requestAnimationFrame(frame);
}

function seek(value) {
  seconds = Math.min(duration, Math.max(0, value));
  started = true;
  lastFrame = 0;
  if (!audioFailed) {
    try {
      audio.currentTime = Math.min(seconds, duration - .001);
      if (playing && audio.paused) startAudio();
    } catch { audioFailure(); }
  }
  update();
}

function press(button, run) {
  let pointerTime = -Infinity;
  button.addEventListener('pointerdown', (event) => {
    if (event.button !== 0 || button.disabled) return;
    pointerTime = event.timeStamp;
    run();
  });
  button.addEventListener('click', (event) => {
    if (event.detail > 0 && event.timeStamp - pointerTime < 1000) {
      event.preventDefault();
      return;
    }
    if (!button.disabled) run();
  });
}

press(start, begin);
press(play, () => playing ? pause() : begin());
press(sound, () => {
  soundOn = !soundOn;
  audio.muted = !soundOn;
  updateSound();
});
press(next, () => {
  const upcoming = FILM_SCENES.find((scene) => scene.start > seconds + .25);
  seek(upcoming ? upcoming.start : 0);
});
scrub.max = String(duration);
scrub.addEventListener('input', () => seek(Number(scrub.value)));
document.addEventListener('visibilitychange', () => { if (document.hidden && playing) pause(); });
audio.addEventListener('error', audioFailure);
audio.addEventListener('ended', () => {
  if (!playing || !audioActive) return;
  seconds = duration;
  playing = false;
  audioActive = false;
  lastFrame = 0;
  update();
});
canvas.addEventListener('pointermove', (event) => {
  const rect = canvas.getBoundingClientRect();
  pointerX = Math.max(-1, Math.min(1, 2 * ((event.clientX - rect.left) / rect.width) - 1));
  pointerY = Math.max(-1, Math.min(1, 2 * ((event.clientY - rect.top) / rect.height) - 1));
  if (!playing) draw();
});
canvas.addEventListener('pointerleave', () => { pointerX = 0; pointerY = 0; if (!playing) draw(); });
new ResizeObserver(() => draw()).observe(canvas);
reduced.addEventListener('change', () => draw());

const transcript = $('film-transcript-list');
const gateDocs = ['1-access.md', '1-access.md', '1-access.md', '1-access.md',
  '1-access.md', '1-access.md', '3-action.md', '6-prediction.md'];
FILM_SCENES.forEach((scene, index) => {
  const item = document.createElement('li');
  const button = document.createElement('button');
  button.type = 'button';
  button.textContent = clock(scene.start) + ' · ' + scene.title;
  button.className = 'inside-film-jump';
  press(button, () => seek(scene.start));
  const caption = document.createElement('span');
  caption.textContent = scene.caption;
  const narration = document.createElement('p');
  narration.className = 'inside-film-narration';
  narration.textContent = scene.narration;
  const note = document.createElement('small');
  note.textContent = scene.claim;
  const source = document.createElement('a');
  source.href = 'https://github.com/thantiklermcirony/bounded-observer/blob/main/docs/' + gateDocs[index];
  source.textContent = 'Framework context';
  item.append(button, caption, narration, note, source);
  transcript.append(item);
});

updateSound();
update();
requestAnimationFrame(frame);
