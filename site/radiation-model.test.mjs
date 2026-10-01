import assert from 'node:assert/strict';
import { test } from 'node:test';
import { LARGE, SMALL, CHALLENGE, potential, pulseLedger, simulate } from './radiation-model.mjs';

const near = (a, b, epsilon = 1e-7) => Math.abs(a - b) < epsilon;

test('both schedules deliver exactly the same amount, including the common challenge', () => {
  for (const order of ['large-small', 'small-large']) {
    const run = simulate({ order, challenge: true });
    assert.ok(near(run.windows.reduce((sum, w) => sum + w.dose, 0), LARGE + SMALL + CHALLENGE));
    assert.ok(run.points.every(p => p.x >= 0 && p.H >= 0));
  }
});

test('a quadratic acute potential hides pair order while leaving different future states', () => {
  const a = simulate({ order: 'large-small', model: 'quadratic' });
  const b = simulate({ order: 'small-large', model: 'quadratic' });
  assert.ok(near(a.afterPair.H, b.afterPair.H, 1e-5));
  assert.ok(Math.abs(a.afterPair.x - b.afterPair.x) > 0.1);
  const aa = simulate({ order: 'large-small', model: 'quadratic', challenge: true });
  const bb = simulate({ order: 'small-large', model: 'quadratic', challenge: true });
  assert.ok(Math.abs(aa.final.H - bb.final.H) > 0.01);
});

test('nonquadratic illustrative continuous response can separate reversed equal totals', () => {
  const a = simulate({ order: 'large-small' });
  const b = simulate({ order: 'small-large' });
  assert.ok(Math.abs(a.afterPair.H - b.afterPair.H) > 0.01);
});

test('add-subtract pulse rule has quadratic reversal null but a common third challenge can distinguish it', () => {
  const retention = 0.53;
  const a = pulseLedger(LARGE, SMALL, retention, 'quadratic');
  const b = pulseLedger(SMALL, LARGE, retention, 'quadratic');
  assert.ok(near(a, b));
  const stateA = retention * (retention * LARGE + SMALL);
  const stateB = retention * (retention * SMALL + LARGE);
  const nextA = potential(stateA + CHALLENGE, 'quadratic') - potential(stateA, 'quadratic');
  const nextB = potential(stateB + CHALLENGE, 'quadratic') - potential(stateB, 'quadratic');
  assert.ok(!near(nextA, nextB));
});

test('a zero gap or full recovery removes pulse order separation', () => {
  for (const retention of [0, 1]) {
    assert.ok(near(pulseLedger(LARGE, SMALL, retention),
      pulseLedger(SMALL, LARGE, retention)));
  }
});

test('finer integration leaves the teaching curves effectively unchanged', () => {
  const coarse = simulate({ step: 0.01, challenge: true });
  const fine = simulate({ step: 0.002, challenge: true });
  assert.ok(near(coarse.final.H, fine.final.H, 1e-4));
  assert.ok(near(coarse.final.x, fine.final.x, 1e-9));
});
