import assert from 'node:assert/strict';
import { test } from 'node:test';
import { disk } from './bo.js';
import { makeWorld, move, observePoint, trial, loopTriangle, horizonProgress } from './inside-core.mjs';

const close = (a, b, tolerance = 1e-9) => Math.abs(a - b) <= tolerance;
const pointClose = (a, b, tolerance = 1e-9) =>
  close(a.x, b.x, tolerance) && close(a.y, b.y, tolerance);

test('the same world seed gives the same landmarks and stars', () => {
  const a = makeWorld(2026), b = makeWorld(2026), c = makeWorld(2027);
  assert.deepEqual(a, b);
  assert.notDeepEqual(a.stars, c.stars);
  assert.equal(a.landmarks.length, 5);
  assert.equal(a.stars.length, 190);
  for (const item of [...a.landmarks, ...a.stars]) {
    assert.ok(disk.abs(item.point) < 1);
  }
});

test('a key step has fixed intrinsic length at the centre and near the rim', () => {
  const step = 0.24;
  for (const origin of [disk.C(0, 0), disk.C(0.91, -0.12)]) {
    const result = move(origin, 0.37, 'forward', step);
    assert.ok(close(result.travelled, step));
    assert.ok(close(disk.distance(origin, result.observer), step));
    assert.ok(disk.abs(result.observer) < 1);
    const localStep = disk.recentre(origin, result.observer);
    assert.ok(close(disk.distance(disk.C(0, 0), localStep), step));
  }
  assert.ok(pointClose(move(disk.C(0, 0), 0, 'forward', step).observer,
    disk.fromPolar(step, 0)));
});

test('turning changes the heading without translating the observer', () => {
  const origin = disk.C(0.82, 0.1);
  const left = move(origin, 0, 'turn-left');
  const right = move(origin, 0, 'turn-right');
  assert.ok(pointClose(left.observer, origin));
  assert.equal(left.travelled, 0);
  assert.ok(close(left.heading, -Math.PI / 12));
  assert.ok(close(right.heading, Math.PI / 12));
});

test('recentering changes raw coordinates while keeping intrinsic distances', () => {
  const o = disk.C(0.4, 0.3);
  const p = disk.C(-0.2, 0.6);
  const q = disk.C(0.5, -0.1);
  assert.ok(disk.abs(disk.recentre(o, o)) < 1e-12);
  assert.ok(!pointClose(disk.recentre(o, p), p));
  assert.ok(close(disk.distance(p, q),
    disk.distance(disk.recentre(o, p), disk.recentre(o, q))));
});

test('zoom exchanges field width for range, and turning changes the bearing', () => {
  const origin = disk.C(0, 0);
  const far = disk.fromPolar(3, Math.PI / 9);
  const wide = observePoint(origin, 0, far, 1);
  const zoomed = observePoint(origin, 0, far, 2);
  assert.ok(close(wide.intrinsicDistance, 3));
  assert.equal(wide.visible, false);
  assert.equal(zoomed.visible, true);
  assert.ok(zoomed.halfAperture < wide.halfAperture);
  assert.ok(zoomed.maxRange > wide.maxRange);

  const side = disk.fromPolar(1, Math.PI * 5 / 18); // 50 degrees
  assert.equal(observePoint(origin, 0, side, 1).visible, true);
  assert.equal(observePoint(origin, 0, side, 2).visible, false);
  assert.ok(close(observePoint(origin, Math.PI / 3, side, 2).bearing,
    -Math.PI / 18));
});

test('the same reading under one pulse has different futures when reserve differs', () => {
  const full = trial(0.5, 0.9, 0.25);
  const spent = trial(0.5, 0.1, 0.25);
  assert.equal(full.reading, spent.reading);
  assert.equal(full.pulse, spent.pulse);
  assert.ok(close(full.futureReading, 0.7));
  assert.ok(close(spent.futureReading, 0.3));
  assert.equal(full.outcome, 'rises');
  assert.equal(spent.outcome, 'falls');
  assert.equal(trial(0.5, 0.1, 0).futureReading, 0.5);
});

function angleAt(vertex, one, two) {
  const tangent = (destination) => {
    const next = disk.geodesic(vertex, destination, 2048)[1];
    return { x: next.x - vertex.x, y: next.y - vertex.y };
  };
  const u = tangent(one), v = tangent(two);
  const cosine = (u.x * v.x + u.y * v.y) / (Math.hypot(u.x, u.y) * Math.hypot(v.x, v.y));
  return Math.acos(Math.max(-1, Math.min(1, cosine)));
}

test('a closed hyperbolic triangle returns to base with area sized compass turn', () => {
  const base = disk.C(0.23, -0.16);
  const a = disk.C(0.4, 0.2);
  const b = disk.fromPolar(2 * Math.atanh(0.7), 2);
  const path = loopTriangle(base, a, b);
  assert.ok(pointClose(path.vertices[0], path.vertices[3]));
  assert.ok(close(path.turn, disk.gyrationAngle(a, b)));
  assert.ok(path.turn < 0, 'a counterclockwise loop transports the compass clockwise');
  assert.ok(path.area > 0.5);
  const [A, B, C] = path.vertices;
  const angleSum = angleAt(A, B, C) + angleAt(B, A, C) + angleAt(C, A, B);
  const independentArea = Math.PI - angleSum;
  assert.ok(close(path.area, independentArea, 0.001),
    `gyration ${path.area} versus angle-defect area ${independentArea}`);
});

test('bounded coordinate approaches but does not reach the horizon in finite steps', () => {
  assert.equal(horizonProgress(0, 0.3), 0);
  let previous = 0;
  for (let n = 1; n <= 40; n++) {
    const x = horizonProgress(n, 0.3);
    assert.ok(x > previous);
    assert.ok(x < 1);
    assert.ok(close(x, Math.tanh(n * 0.3 / 2)));
    previous = x;
  }
  assert.ok(horizonProgress(10000, 0.3) < 1); // even when tanh rounds to 1
});
