/* A constructed observer world. These are exact rules of this toy world, not
   empirical claims about nature. The geometry reuses the site's checked math. */
import { disk } from './bo.js';

const TAU = Math.PI * 2;
const DEFAULT_SEED = 20261001;
const TURN_STEP = Math.PI / 12;

function finite(value, name) {
  if (!Number.isFinite(value)) throw new RangeError(`${name} must be finite`);
}

function inside(point, name) {
  if (!point || typeof point !== 'object') throw new TypeError(`${name} must be a disk point`);
  finite(point.x, `${name}.x`);
  finite(point.y, `${name}.y`);
  if (Math.hypot(point.x, point.y) >= 1) throw new RangeError(`${name} must lie inside the disk`);
}

function wrap(angle) {
  return ((angle + Math.PI) % TAU + TAU) % TAU - Math.PI;
}

function randomGenerator(seed) {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6D2B79F5) >>> 0;
    let z = state;
    z = Math.imul(z ^ (z >>> 15), z | 1);
    z ^= z + Math.imul(z ^ (z >>> 7), z | 61);
    return ((z ^ (z >>> 14)) >>> 0) / 4294967296;
  };
}

/** Stable world for a given seed. Radii are intrinsic distances, not screen radii. */
export function makeWorld(seed = DEFAULT_SEED) {
  finite(seed, 'seed');
  const rand = randomGenerator(seed);
  const specs = [
    ['beacon', 'The first signal', 1.05, 0.05],
    ['fork', 'One reading, two histories', 1.92, 0.88],
    ['turn', 'The return loop', 2.78, 2.18],
    ['filter', 'The forgetting gate', 3.70, 3.76],
    ['horizon', 'The distant boundary', 5.15, 5.42],
  ];
  const landmarks = specs.map(([id, label, rho, angle]) => ({
    id,
    label,
    point: disk.fromPolar(rho + (rand() - 0.5) * 0.12, angle + (rand() - 0.5) * 0.12),
  }));

  // Uniform density in hyperbolic area: area(r) is proportional to cosh(r)-1.
  const radius = 6.25;
  const stars = Array.from({ length: 190 }, (_, id) => {
    const rho = Math.acosh(1 + rand() * (Math.cosh(radius) - 1));
    const angle = rand() * TAU;
    return {
      id,
      point: disk.fromPolar(rho, angle),
      strength: 0.35 + 0.65 * rand(),
    };
  });
  return { seed, radius, start: disk.C(0, 0), landmarks, stars };
}

/** One fixed intrinsic-distance step in a direction relative to the observer.
    Heading zero faces +x. Positive angles turn toward +y in disk coordinates. */
export function move(observer, heading, command, stepDistance = 0.24) {
  inside(observer, 'observer');
  finite(heading, 'heading');
  finite(stepDistance, 'stepDistance');
  if (stepDistance <= 0) throw new RangeError('stepDistance must be positive');

  const directions = {
    forward: 0, w: 0, ArrowUp: 0,
    backward: Math.PI, back: Math.PI, s: Math.PI, ArrowDown: Math.PI,
    left: -Math.PI / 2, a: -Math.PI / 2, ArrowLeft: -Math.PI / 2,
    right: Math.PI / 2, d: Math.PI / 2, ArrowRight: Math.PI / 2,
  };
  if (command === 'turn-left' || command === 'turn-right') {
    return {
      observer: disk.C(observer.x, observer.y),
      heading: wrap(heading + (command === 'turn-left' ? -TURN_STEP : TURN_STEP)),
      travelled: 0,
    };
  }
  if (!Object.hasOwn(directions, command)) throw new RangeError(`unknown command: ${command}`);
  const delta = disk.fromPolar(stepDistance, heading + directions[command]);
  const next = disk.add(observer, delta);
  return { observer: next, heading: wrap(heading), travelled: disk.distance(observer, next) };
}

/** Observer-centred reading. Zoom spends field width to extend intrinsic range.
    Its aperture and range are explicit game rules, not consequences of theorems. */
export function observePoint(observer, heading, point, zoom = 1) {
  inside(observer, 'observer');
  inside(point, 'point');
  finite(heading, 'heading');
  finite(zoom, 'zoom');
  if (zoom < 1 || zoom > 8) throw new RangeError('zoom must be between 1 and 8');

  const centred = disk.recentre(observer, point);
  const c = Math.cos(heading), s = Math.sin(heading);
  const local = disk.C(centred.x * c + centred.y * s, -centred.x * s + centred.y * c);
  const intrinsicDistance = disk.distance(observer, point);
  const bearing = Math.hypot(local.x, local.y) < 1e-12 ? 0 : wrap(Math.atan2(local.y, local.x));
  const halfAperture = Math.PI / (3 * zoom); // 120 degrees wide at zoom 1
  const maxRange = 2.2 + 1.2 * Math.log2(zoom);
  return {
    local,
    intrinsicDistance,
    bearing,
    visible: Math.abs(bearing) <= halfAperture && intrinsicDistance <= maxRange,
    halfAperture,
    maxRange,
  };
}

/** Constructed response rule: equal present readings conceal different reserve.
    A common pulse exposes that the displayed reading alone is not predictive state. */
export function trial(reading = 0.5, reserve = 0.9, pulse = 0.25) {
  for (const [name, value] of Object.entries({ reading, reserve, pulse })) {
    finite(value, name);
    if (value < 0 || value > 1) throw new RangeError(`${name} must be between 0 and 1`);
  }
  const unclamped = reading + 2 * pulse * (reserve - 0.5);
  const futureReading = Math.max(0, Math.min(1, unclamped));
  const change = futureReading - reading;
  return {
    reading,
    reserve,
    pulse,
    futureReading,
    change,
    outcome: change > 1e-12 ? 'rises' : change < -1e-12 ? 'falls' : 'holds',
  };
}

/** A closed geodesic triangle translated to base. For the listed traversal,
    the transported compass turns by the gyration angle (clockwise for a
    counterclockwise loop); at curvature -1 its magnitude is triangle area. */
export function loopTriangle(base, a, b) {
  inside(base, 'base');
  inside(a, 'a');
  inside(b, 'b');
  const second = disk.add(base, a);
  const third = disk.add(base, disk.add(a, b));
  const turn = disk.gyrationAngle(a, b);
  return {
    vertices: [disk.C(base.x, base.y), second, third, disk.C(base.x, base.y)],
    turn,
    area: Math.abs(turn),
  };
}

/** Two-horizon projective chart with ceiling 1. n steps of rapidity step/2. */
export function horizonProgress(n, step) {
  finite(n, 'n');
  finite(step, 'step');
  if (n < 0 || step < 0) throw new RangeError('n and step must be nonnegative');
  const value = Math.tanh((n * step) / 2);
  // The mathematical value is always below 1 for finite input; floating-point
  // tanh may round it up at large arguments, so preserve the open interval.
  return Math.min(value, 1 - Number.EPSILON);
}
