/* The site runs the same maths the capstone proves. This checks it against the same
   identities as toolkit/tests/test_theorems.py. Run with:  node site/bo.test.mjs  */
import { law, boundary, disk, coupling, cones } from './bo.js';

let failed = 0;
const ok = (name, cond) => { if (!cond) failed++; console.log((cond ? 'ok   ' : 'FAIL ') + name); };
const close = (a, b, t = 1e-9) => Math.abs(a - b) < t;

// Theorems 1, 7
ok('Einstein composition is associative',
  close(law.einstein(law.einstein(.3, -.55), .8), law.einstein(.3, law.einstein(-.55, .8))));
ok('rapidity turns the law into addition',
  close(law.rapidity(law.einstein(.3, .5)), law.rapidity(.3) + law.rapidity(.5)));
ok('equal steps never reach the horizon', (() => {
  let x = 0; for (let i = 0; i < 15; i++) x = law.einstein(x, 0.5); return x < 1;
})());

// Theorem 4
ok('trichotomy: elliptic wraps, 2 (+) 2 = -4/3', close(law.trichotomy(2, 2, -1), -4 / 3));
ok('trichotomy: parabolic is flat addition', law.trichotomy(.5, .5, 0) === 1);

// Theorem 8
for (const al of [-3, -1, 0, 0.5, 0.9]) {
  ok(`dial adds in its own rapidity, alpha=${al}`,
    close(law.dialRapidity(law.dial(.3, .45, al), al), law.dialRapidity(.3, al) + law.dialRapidity(.45, al)));
}
ok('dial landmark: alpha = 0 is Bliss', close(law.dial(.3, .45, 0), law.bliss(.3, .45)));
ok('dial landmark: alpha -> 1 is Loewe', close(law.dial(.3, .45, 1), law.loewe(.3, .45)));
ok('dial landmark: alpha = -1 is Einstein', close(law.dial(.3, .45, -1), law.einstein(.3, .45)));

// Theorem 19
ok('far side: artanh(1.25) = 1.0986 + i pi/2',
  close(law.farSide(1.25).re, 1.0986122886681098) && close(law.farSide(1.25).im, Math.PI / 2));
ok('simultaneity slope follows the same law',
  close(law.einstein(1 / 0.3, 0.5), 1 / law.einstein(0.3, 0.5)));

// Proposition 9
ok('Osgood: gamma < 1 arrives', close(boundary.arrivalTime(0.5, 1), 2));
ok('Osgood: gamma >= 1 never arrives',
  boundary.arrivalTime(1, 1) === Infinity && boundary.arrivalTime(2, 1) === Infinity);

// Theorem 29
{
  const o = disk.C(.4, .3), x = disk.C(-.2, .6), y = disk.C(.5, -.1);
  ok('every observer sits at its own centre', disk.abs(disk.recentre(o, o)) < 1e-12);
  ok('observers disagree on values, agree on distances',
    disk.abs(disk.recentre(o, x)) !== disk.abs(x) &&
    close(disk.distance(x, y), disk.distance(disk.recentre(o, x), disk.recentre(o, y))));
}

// Theorem 26 and section 5.2
{
  const a = disk.C(.4, .2), b = disk.C(.7 * Math.cos(2), .7 * Math.sin(2));
  ok('gyration angle is 0.600 rad', close(Math.abs(disk.gyrationAngle(a, b)), 0.600, 5e-4));
  const A = disk.C(.3, .1), B = disk.C(-.2, .5), Z = disk.C(.1, -.4);
  const g = disk.gyration(A, B);
  const L = disk.add(A, disk.add(B, Z));
  const R = disk.add(disk.add(A, B), { x: g.x * Z.x - g.y * Z.y, y: g.x * Z.y + g.y * Z.x });
  ok('gyration is exactly what the order of changes leaves behind',
    Math.hypot(L.x - R.x, L.y - R.y) < 1e-12);
}

// section 8.4
ok('a circle of radius 5 has circumference 466, not 31', close(disk.circumference(5), 466.3, 0.1));

// Theorem 16
{
  let d = 0; for (let i = 0; i < 300000; i++) d = coupling.step(d, 1.2, 1, 'tanh', 1e-4);
  ok('bounded coupling locks below threshold', close(d, coupling.lockGap(1.2, 1, 'tanh'), 1e-3));
  ok('bounded coupling unlocks above it, unbounded never does',
    coupling.lockGap(3, 1, 'tanh') === null && coupling.lockGap(3, 1, 'sinh') !== null);
}

// Theorem 25 item 4
{
  const M = [[2, 1, 0.5], [0.3, 1.7, 0.9], [1.1, 0.4, 2.2]];
  const k = cones.birkhoff(M);
  let worst = 0;
  for (let i = 0; i < 3000; i++) {
    const r = () => 0.01 + Math.random();
    const X = [r(), r(), r()], Y = [r(), r(), r()];
    worst = Math.max(worst, cones.hilbert(cones.apply(M, X), cones.apply(M, Y)) / cones.hilbert(X, Y));
  }
  ok(`forward-only maps contract by at least tanh(D/4) (worst ${worst.toFixed(3)} <= ${k.toFixed(3)})`,
    worst <= k + 1e-9);
}

console.log(failed ? `\n${failed} FAILED` : '\nall passed');
process.exit(failed ? 1 : 0);
