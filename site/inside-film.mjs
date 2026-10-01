/* Inside: an original, constructed visual argument.
 * The canvas supplies imagery. The page controller should expose FILM_SCENES'
 * captions and boundaries as real text, including for screen readers.
 * Nothing in the fictional social scenes is evidence about actual cultures or
 * about subjective consciousness. The mathematical scenes name their gates.
 */
import { disk } from './bo.js';

export const FILM_DURATION = 155;

export const FILM_SCENES = Object.freeze([
  {
    start: 0, end: 18, title: 'Inside the world',
    caption: 'I measure from here, and my actions enter what I measure.',
    status: 'Premise · Gate 1',
    boundary: 'A situated observer is the programme’s starting premise. The reflection is a visual metaphor, not a simulation or explanation of consciousness.',
  },
  {
    start: 18, end: 35, title: 'What survives',
    caption: 'A history leaves more than one trace; only some are kept.',
    status: 'Constructed illustration',
    boundary: 'These changing filters and inherited records belong to a fictional world. They do not establish a law of real cultures.',
  },
  {
    start: 35, end: 55, title: 'One event, two views',
    caption: 'The same event can reach us as different evidence.',
    status: 'Constructed illustration · Gate 1',
    boundary: 'The two viewpoints illustrate finite access. Neither is a claim about any real community, nor does combining them reveal every fact.',
  },
  {
    start: 55, end: 76, title: 'One reading, two futures',
    caption: 'If one reading hides futures that diverge under the same action, it was not enough.',
    status: '[P] Predictive-state criterion · Gate 2',
    boundary: 'Theorem 10 gives the conditional criterion under admissible interventions. The two numerical histories shown here are constructed.',
  },
  {
    start: 76, end: 96, title: 'Which actions count?',
    caption: 'If an action changes with hidden context, one simple rule is not enough.',
    status: '[P] Conditional action gate · Gate 3',
    boundary: 'Theorem 12 applies when an intervention’s endpoint from rest determines its action from every state. The animation does not certify any real intervention.',
  },
  {
    start: 96, end: 122, title: 'Two ways to read a step',
    caption: 'One path can be straight in its own measure, yet crowd a limit on a bounded scale.',
    status: '[P] Aczél representation · Gate 4',
    boundary: 'C1 continuous composition, C2 associativity, C3 strict monotonicity and C4 a neutral state are required. x = tanh ψ is one selected two-horizon chart, not the law of every saturating system.',
  },
  {
    start: 122, end: 137, title: 'A route can leave a turn',
    caption: 'In this selected geometry, a closed route turns a carried direction.',
    status: '[P] Selected hyperbolic branch · Gate 5',
    boundary: 'The loop is in the curvature −1 Poincaré disk. Holonomy is conditional on this geometry and admissible comparison; boundedness alone does not select spatial curvature.',
  },
  {
    start: 137, end: 155, title: 'Compare with the world',
    caption: 'We can compare partial records against a shared world; tests can support or rule out specific uses.',
    status: 'Evidence and testing · Gate 6',
    boundary: 'A replicated effect-scale comparison does not prove the universal law. H1’s drug-dial prediction was refuted; H7 remains open. The records retain disagreement and unknowns.',
  },
].map((scene) => Object.freeze({ ...scene, claim: `${scene.status} — ${scene.boundary}` })));

const P = {
  void: '#06121b', deep: '#0b2430', blue: '#153749',
  ice: '#c9e8e7', muted: '#829eaa', cyan: '#70e3e8',
  gold: '#ffd098', coral: '#f58b78', violet: '#afa2ff',
  green: '#9ed7ac', white: '#f2f2e9',
};
const TAU = Math.PI * 2;
const clamp = (v, lo = 0, hi = 1) => Math.min(hi, Math.max(lo, v));
const ease = (v) => { const x = clamp(v); return x * x * (3 - 2 * x); };
const mix = (a, b, t) => a + (b - a) * t;
const nrand = (n) => {
  const v = Math.sin(n * 127.1 + 78.233) * 43758.5453123;
  return v - Math.floor(v);
};

function path(g, points, color, width = 1, alpha = 1, dash = null) {
  if (points.length < 2) return;
  g.save();
  g.globalAlpha *= alpha;
  g.strokeStyle = color;
  g.lineWidth = width;
  g.lineCap = 'round';
  g.lineJoin = 'round';
  if (dash) g.setLineDash(dash);
  g.beginPath();
  g.moveTo(points[0][0], points[0][1]);
  for (let i = 1; i < points.length; i++) g.lineTo(points[i][0], points[i][1]);
  g.stroke();
  g.restore();
}

function circle(g, x, y, r, color, { fill = true, width = 1, alpha = 1, glow = 0 } = {}) {
  if (r <= 0) return;
  g.save();
  g.globalAlpha *= alpha;
  if (glow) { g.shadowColor = color; g.shadowBlur = glow; }
  g.beginPath();
  g.arc(x, y, r, 0, TAU);
  if (fill) { g.fillStyle = color; g.fill(); }
  else { g.strokeStyle = color; g.lineWidth = width; g.stroke(); }
  g.restore();
}

function rounded(g, x, y, w, h, r, fill, stroke = null, alpha = 1) {
  r = Math.max(0, Math.min(r, w / 2, h / 2));
  g.save();
  g.globalAlpha *= alpha;
  g.beginPath();
  g.moveTo(x + r, y);
  g.lineTo(x + w - r, y);
  g.quadraticCurveTo(x + w, y, x + w, y + r);
  g.lineTo(x + w, y + h - r);
  g.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  g.lineTo(x + r, y + h);
  g.quadraticCurveTo(x, y + h, x, y + h - r);
  g.lineTo(x, y + r);
  g.quadraticCurveTo(x, y, x + r, y);
  g.closePath();
  if (fill) { g.fillStyle = fill; g.fill(); }
  if (stroke) { g.strokeStyle = stroke; g.lineWidth = 1; g.stroke(); }
  g.restore();
}

function text(g, str, x, y, size, color = P.ice, align = 'left', weight = 600, alpha = 1) {
  g.save();
  g.globalAlpha *= alpha;
  g.fillStyle = color;
  g.textAlign = align;
  g.textBaseline = 'middle';
  g.font = `${weight} ${Math.max(9, size)}px ui-sans-serif, system-ui, sans-serif`;
  g.fillText(str, x, y);
  g.restore();
}

function glow(g, x, y, r, color, intensity = .25) {
  const grad = g.createRadialGradient(x, y, 0, x, y, r);
  grad.addColorStop(0, color);
  grad.addColorStop(1, 'rgba(0,0,0,0)');
  g.save();
  g.globalAlpha *= intensity;
  g.fillStyle = grad;
  g.beginPath();
  g.arc(x, y, r, 0, TAU);
  g.fill();
  g.restore();
}

function triangle(g, points, fill, alpha = 1) {
  g.save();
  g.globalAlpha *= alpha;
  g.beginPath();
  g.moveTo(points[0][0], points[0][1]);
  for (let i = 1; i < points.length; i++) g.lineTo(points[i][0], points[i][1]);
  g.closePath();
  g.fillStyle = fill;
  g.fill();
  g.restore();
}

function drawBackground(g, w, h, seconds, still) {
  const bg = g.createLinearGradient(0, 0, w, h);
  bg.addColorStop(0, P.void);
  bg.addColorStop(.56, '#102c38');
  bg.addColorStop(1, '#071820');
  g.fillStyle = bg;
  g.fillRect(0, 0, w, h);
  const S = Math.min(w, h);
  glow(g, w * .52, h * .46, Math.max(w, h) * .55, '#21516b', .18);
  for (let i = 0; i < 95; i++) {
    const xx = nrand(i * 3 + 1) * w;
    const yy = ((nrand(i * 3 + 2) + (still ? 0 : seconds * (.00012 + .00007 * nrand(i + 201)))) % 1) * h;
    const a = .06 + nrand(i * 3 + 3) * .2;
    circle(g, xx, yy, Math.max(.45, S * (.0008 + .0011 * nrand(i + 75))), P.ice, { alpha: a });
  }
  // The same current of light runs through every scene.
  const current = [];
  for (let i = 0; i <= 72; i++) {
    const x = i / 72 * w;
    const phase = (still ? 0 : seconds * .055);
    const y = h * (.84 + .02 * Math.sin(i * .18 + phase) + .012 * Math.sin(i * .43 - phase));
    current.push([x, y]);
  }
  path(g, current, P.cyan, Math.max(1, S * .0017), .19);
  const vignette = g.createRadialGradient(w * .5, h * .48, h * .2, w * .5, h * .48, Math.max(w, h) * .78);
  vignette.addColorStop(0, 'rgba(0,0,0,0)');
  vignette.addColorStop(1, 'rgba(0,5,12,.68)');
  g.fillStyle = vignette;
  g.fillRect(0, 0, w, h);
}

function drawHuman(g, x, y, scale, color, alpha = 1, turned = false) {
  const r = 14 * scale;
  glow(g, x, y - 32 * scale, 76 * scale, color, .23 * alpha);
  circle(g, x + (turned ? 4 : 0) * scale, y - 45 * scale, r, color, { alpha: .78 * alpha, glow: 11 * scale });
  triangle(g, [
    [x - 11 * scale, y - 26 * scale],
    [x + 11 * scale, y - 26 * scale],
    [x + 22 * scale, y + 28 * scale],
    [x - 22 * scale, y + 28 * scale],
  ], color, .24 * alpha);
  path(g, [[x - 10 * scale, y - 23 * scale], [x - 19 * scale, y + 28 * scale], [x + 19 * scale, y + 28 * scale], [x + 10 * scale, y - 23 * scale]], color, 2 * scale, .6 * alpha);
  circle(g, x, y - 45 * scale, r + 8 * scale, color, { fill: false, width: 1.1 * scale, alpha: .35 * alpha });
}

function drawEye(g, x, y, r, color, alpha = 1) {
  g.save();
  g.globalAlpha *= alpha;
  g.beginPath();
  g.moveTo(x - r, y);
  g.quadraticCurveTo(x, y - r * .75, x + r, y);
  g.quadraticCurveTo(x, y + r * .75, x - r, y);
  g.strokeStyle = color;
  g.lineWidth = Math.max(1.3, r * .055);
  g.stroke();
  circle(g, x, y, r * .27, color, { alpha: .85 });
  g.restore();
}

function sceneInside(g, w, h, p, pointerX, pointerY) {
  const S = Math.min(w, h);
  const dx = clamp(pointerX, -1, 1) * S * .025;
  const dy = clamp(pointerY, -1, 1) * S * .018;
  const hx = w * .39 + dx, hy = h * .62 + dy;
  const mirrorX = w * .72, mirrorY = h * .44;
  const world = g.createRadialGradient(mirrorX, mirrorY, S * .02, mirrorX, mirrorY, S * .38);
  world.addColorStop(0, 'rgba(103,226,233,.24)');
  world.addColorStop(.7, 'rgba(75,143,172,.08)');
  world.addColorStop(1, 'rgba(75,143,172,0)');
  g.fillStyle = world;
  g.fillRect(0, 0, w, h);
  for (let i = 0; i < 5; i++) {
    const rr = S * (.16 + i * .075 + p * .01);
    circle(g, mirrorX, mirrorY, rr, P.cyan, { fill: false, width: 1, alpha: .07 + .035 * (5 - i) });
  }
  triangle(g, [[hx, hy - S * .08], [w * .93, h * .1], [w * .93, h * .75]], P.cyan, .055);
  for (let i = 0; i < 18; i++) {
    const angle = -.75 + i / 17 * 1.5;
    const len = S * (.28 + nrand(i + 401) * .42);
    path(g, [[hx, hy - S * .08], [hx + Math.cos(angle) * len, hy - S * .08 + Math.sin(angle) * len]], P.cyan, 1, .08 + .12 * nrand(i + 304));
  }
  drawHuman(g, hx, hy, S / 520, P.gold);
  circle(g, mirrorX, mirrorY, S * .155, P.ice, { fill: false, width: Math.max(1.3, S * .0022), alpha: .62 });
  drawHuman(g, mirrorX, mirrorY + S * .05, S / 1050, P.cyan, .35 + .3 * ease(p));
  drawEye(g, mirrorX, mirrorY - S * .022, S * .056, P.ice, .55);
  const signal = ease((p - .22) / .62);
  const a = [mirrorX - S * .14, mirrorY + S * .06];
  const b = [hx + S * .025, hy - S * .11];
  const point = [mix(a[0], b[0], signal), mix(a[1], b[1], signal)];
  path(g, [a, b], P.gold, Math.max(1.4, S * .003), .23);
  circle(g, point[0], point[1], Math.max(2.5, S * .006), P.gold, { glow: S * .045 });
  text(g, 'WORLD', mirrorX, h * .73, Math.min(16, S * .028), P.muted, 'center', 700, .66);
  text(g, 'HERE', hx, h * .83, Math.min(16, S * .028), P.gold, 'center', 700, .75);
}

function sceneFilters(g, w, h, p) {
  const S = Math.min(w, h);
  const centres = [w * .2, w * .5, w * .8];
  const pulse = ease(p);
  for (let i = 0; i < 3; i++) {
    const x = centres[i];
    const span = w * .22;
    rounded(g, x - span * .48, h * .25, span * .96, h * .44, S * .025,
      i === 1 ? 'rgba(106,155,178,.08)' : 'rgba(125,137,161,.065)',
      'rgba(178,220,222,.18)', .85);
    drawHuman(g, x, h * .57, S / 850, i === 0 ? P.gold : i === 1 ? P.cyan : P.violet, .7 + i * .07);
    for (let j = 0; j < 8; j++) {
      const sy = h * (.27 + j * .06);
      const length = span * (.7 + nrand(i * 15 + j) * .35);
      path(g, [[x - length * .58, sy], [x + length * .4, sy + (nrand(j + i * 7) - .5) * S * .035]],
        i === 0 ? P.gold : i === 1 ? P.cyan : P.violet, 1.3, .08 + .18 * nrand(j * 11 + i));
    }
    // A selective record: two bright marks survive each passage.
    rounded(g, x - S * .054, h * .19, S * .108, S * .082, S * .008,
      'rgba(9,30,42,.83)', 'rgba(183,225,223,.38)', .88);
    for (let k = 0; k < 2; k++) {
      path(g, [[x - S * .034, h * .217 + k * S * .019], [x + S * (.017 + .009 * ((i + k) % 2)), h * .217 + k * S * .019]],
        k === 0 ? P.gold : P.cyan, 2, .72);
    }
    if (i < 2) {
      const nextX = centres[i + 1];
      const y = h * .46;
      const xm = mix(x + S * .07, nextX - S * .07, pulse);
      path(g, [[x + S * .07, y], [nextX - S * .07, y]], P.ice, Math.max(1, S * .002), .2, [4, 7]);
      circle(g, xm, y, S * .006, P.gold, { alpha: .9, glow: S * .026 });
    }
  }
  for (let i = 0; i < 28; i++) {
    const x = nrand(i + 910) * w;
    const y = h * (.08 + nrand(i + 740) * .13);
    path(g, [[x, y], [x - S * .011, y + S * (.03 + .02 * p)]], P.ice, 1, .18 + .22 * nrand(i + 9));
  }
  text(g, 'EVENT', w * .2, h * .77, Math.min(16, S * .025), P.gold, 'center', 700, .8);
  text(g, 'MEMORY', w * .5, h * .77, Math.min(16, S * .025), P.cyan, 'center', 700, .8);
  text(g, 'INHERITED RECORD', w * .8, h * .77, Math.min(16, S * .025), P.violet, 'center', 700, .8);
}

function sceneBanks(g, w, h, p) {
  const S = Math.min(w, h);
  const gateX = w * .5, gateY = h * .45;
  // Two banks and one shared, partly obscured event.
  const terrain = g.createLinearGradient(0, h * .51, 0, h);
  terrain.addColorStop(0, 'rgba(31,82,91,.24)');
  terrain.addColorStop(1, 'rgba(7,24,34,.72)');
  g.fillStyle = terrain; g.fillRect(0, h * .5, w, h * .4);
  const river = [];
  for (let i = 0; i <= 32; i++) {
    const y = h * (.22 + i / 32 * .62);
    river.push([gateX + Math.sin(i * .29 + p * 3) * S * .024, y]);
  }
  path(g, river, P.cyan, S * .075, .1);
  path(g, river, P.cyan, 1.5, .3);
  path(g, [[w * .18, gateY + S * .06], [w * .82, gateY + S * .06]], P.ice, S * .016, .25);
  const close = ease((p - .35) / .31);
  const lift = (1 - close) * S * .085;
  rounded(g, gateX - S * .036, gateY - S * .08 - lift, S * .072, S * .16,
    S * .005, 'rgba(244,186,121,.32)', P.gold, .8);
  for (let i = -1; i <= 1; i++) {
    path(g, [[gateX + i * S * .017, gateY - S * .072 - lift], [gateX + i * S * .017, gateY + S * .072 - lift]], P.gold, 1.5, .7);
  }
  const L = [w * .22, h * .56], R = [w * .78, h * .56];
  drawHuman(g, L[0], L[1], S / 880, P.gold);
  drawHuman(g, R[0], R[1], S / 880, P.cyan, 1, true);
  triangle(g, [[L[0] + S * .01, L[1] - S * .09], [gateX - S * .018, gateY - S * .065], [gateX - S * .018, gateY + S * .07]], P.gold, .12);
  triangle(g, [[R[0] - S * .01, R[1] - S * .09], [gateX + S * .018, gateY - S * .06], [gateX + S * .018, gateY + S * .075]], P.cyan, .12);
  // Each archive retains a different fragment, not an omniscient replay.
  for (const [x, color, flip] of [[w * .18, P.gold, 1], [w * .82, P.cyan, -1]]) {
    rounded(g, x - S * .045, h * .24, S * .09, S * .083, S * .009,
      'rgba(6,23,33,.85)', color, .75);
    path(g, [[x - S * .026, h * .267], [x + flip * S * .021, h * .267]], color, 2, .8);
    path(g, [[x - S * .026, h * .29], [x + flip * S * .007, h * .29]], color, 2, .55);
    path(g, [[x, h * .325], [x + flip * S * .015, h * .405]], color, 1, .35, [3, 4]);
  }
  glow(g, gateX, gateY, S * (.13 + .04 * close), P.coral, .12 + .1 * close);
  text(g, 'BANK A', L[0], h * .75, Math.min(16, S * .025), P.gold, 'center', 700, .8);
  text(g, 'BANK B', R[0], h * .75, Math.min(16, S * .025), P.cyan, 'center', 700, .8);
}

function sceneState(g, w, h, p) {
  const S = Math.min(w, h);
  const mid = w * .52, gaugeY = h * .43;
  const startX = w * .12, endX = w * .88;
  const histories = [
    [[startX, h * .25], [w * .27, h * .21], [w * .37, h * .32], [mid - S * .065, gaugeY]],
    [[startX, h * .67], [w * .27, h * .71], [w * .37, h * .56], [mid - S * .065, gaugeY]],
  ];
  path(g, histories[0], P.gold, Math.max(2, S * .004), .76);
  path(g, histories[1], P.cyan, Math.max(2, S * .004), .76);
  for (let i = 0; i < 2; i++) {
    const pts = histories[i];
    const q = clamp(p * 1.4);
    const seg = q * (pts.length - 1);
    const k = Math.min(pts.length - 2, Math.floor(seg));
    const t = seg - k;
    circle(g, mix(pts[k][0], pts[k + 1][0], t), mix(pts[k][1], pts[k + 1][1], t), S * .008,
      i ? P.cyan : P.gold, { glow: S * .04 });
  }
  circle(g, mid, gaugeY, S * .068, P.ice, { fill: false, width: 1.5, alpha: .67 });
  circle(g, mid, gaugeY, S * .091, P.cyan, { fill: false, width: 1, alpha: .2 });
  text(g, '0.50', mid, gaugeY, Math.min(30, S * .051), P.white, 'center', 700);
  const pulse = ease((p - .46) / .17);
  if (pulse > 0) {
    circle(g, mid, gaugeY, S * (.095 + pulse * .1), P.coral, { fill: false, width: 2, alpha: (1 - pulse) * .7 });
    path(g, [[mid, h * .15], [mid, gaugeY - S * .1]], P.coral, 3, .18 + .53 * (1 - pulse));
    triangle(g, [[mid, gaugeY - S * .07], [mid - S * .012, gaugeY - S * .095], [mid + S * .012, gaugeY - S * .095]], P.coral, .75);
  }
  const reveal = ease((p - .54) / .37);
  const branchA = [[mid + S * .065, gaugeY], [w * .69, mix(gaugeY, h * .22, reveal)], [endX, mix(gaugeY, h * .2, reveal)]];
  const branchB = [[mid + S * .065, gaugeY], [w * .69, mix(gaugeY, h * .65, reveal)], [endX, mix(gaugeY, h * .69, reveal)]];
  path(g, branchA, P.gold, Math.max(2, S * .004), .22 + .62 * reveal);
  path(g, branchB, P.cyan, Math.max(2, S * .004), .22 + .62 * reveal);
  circle(g, endX, branchA[2][1], S * .01, P.gold, { alpha: reveal, glow: S * .03 });
  circle(g, endX, branchB[2][1], S * .01, P.cyan, { alpha: reveal, glow: S * .03 });
  text(g, 'HISTORY A', startX, h * .18, Math.min(15, S * .023), P.gold, 'left', 700, .8);
  text(g, 'HISTORY B', startX, h * .76, Math.min(15, S * .023), P.cyan, 'left', 700, .8);
  text(g, 'SAME READING', mid, h * .67, Math.min(16, S * .025), P.ice, 'center', 700, .65);
}

function sceneAction(g, w, h, p) {
  const S = Math.min(w, h);
  const rows = [h * .32, h * .64];
  const x0 = w * .15, x1 = w * .77;
  const progress = ease((p - .16) / .59);
  rows.forEach((y, i) => {
    const col = i === 0 ? P.cyan : P.gold;
    circle(g, x0, y, S * .032, col, { fill: false, width: 1.4, alpha: .7 });
    circle(g, x0, y, S * .008, col, { glow: S * .03 });
    const targetY = i === 0 ? y : y - S * .038;
    const actualY = i === 0 ? y : y + S * .095 * progress;
    path(g, [[x0 + S * .04, y], [x1, targetY]], col, 2.2, .22, [5, 5]);
    path(g, [[x0 + S * .04, y], [mix(x0 + S * .04, x1, progress), mix(y, actualY, progress)]], col, Math.max(2.1, S * .004), .82);
    circle(g, x1, targetY, S * .027, col, { fill: false, width: 1.5, alpha: .5 });
    circle(g, mix(x0 + S * .04, x1, progress), mix(y, actualY, progress), S * .009, col, { glow: S * .04 });
    text(g, i === 0 ? 'FROM REST' : 'FROM ANOTHER STATE', x0, y - S * .09,
      Math.min(15, S * .024), col, 'left', 700, .86);
    text(g, i === 0 ? 'RULE HOLDS' : 'HIDDEN CONTEXT', x1, y + (i ? S * .14 : S * .08),
      Math.min(15, S * .024), i ? P.coral : P.green, 'center', 700, .55 + .4 * progress);
  });
  // The same intervention enters both rows; the second trajectory misses.
  const bx = w * .5, by = h * .13;
  path(g, [[bx, by], [bx, rows[0] - S * .07]], P.coral, 2, .52);
  path(g, [[bx, by], [bx + S * .07, rows[1] - S * .08]], P.coral, 2, .4);
  circle(g, bx, by, S * .015, P.coral, { glow: S * .04 });
  text(g, 'SAME PROPOSED ACTION', bx, by - S * .045, Math.min(16, S * .026), P.coral, 'center', 700, .82);
}

function sceneChart(g, w, h, p) {
  const S = Math.min(w, h);
  const left = w * .13, right = w * .87;
  const span = right - left;
  const topY = h * .36, lowY = h * .67;
  const small = w < 620;
  const badges = [
    ['C1', 'CONTINUOUS'], ['C2', 'ASSOCIATIVE'],
    ['C3', 'MONOTONE'], ['C4', 'NEUTRAL'],
  ];
  badges.forEach(([head, desc], i) => {
    const x = small ? w * (.27 + (i % 2) * .46) : w * (.14 + i * .24);
    const y = small ? h * (.105 + Math.floor(i / 2) * .082) : h * .13;
    rounded(g, x - (small ? w * .19 : w * .105), y - S * .027,
      small ? w * .38 : w * .21, S * .055, S * .012,
      'rgba(79,132,149,.12)', 'rgba(156,219,220,.35)', .95);
    text(g, `${head} ${desc}`, x, y, Math.min(small ? 10 : 13, S * .021), P.ice, 'center', 700, .85);
  });
  if (!small) {
    text(g, 'VELOCITY · ESTABLISHED', w * .2, h * .25, 11, P.green, 'center', 700, .65);
    text(g, 'TWO-CHOICE ODDS · IF BAYES', w * .5, h * .25, 11, P.ice, 'center', 700, .65);
    text(g, 'BIOLOGICAL RESPONSE · TEST', w * .8, h * .25, 11, P.gold, 'center', 700, .65);
  }
  path(g, [[left, topY], [right, topY]], P.ice, 1.4, .65);
  path(g, [[left, lowY], [right, lowY]], P.cyan, 1.7, .75);
  text(g, 'ADDITIVE COORDINATE  ψ', w * .5, topY - S * .065, Math.min(15, S * .024), P.white, 'center', 700, .86);
  text(g, 'SELECTED TWO-HORIZON CHART  x = tanh ψ', w * .5, lowY + S * .084,
    Math.min(small ? 10 : 15, S * .024), P.cyan, 'center', 700, .88);
  const mapX = (psi) => left + span * ((Math.tanh(psi) + 1) / 2);
  for (let i = -4; i <= 4; i++) {
    const tx = left + span * ((i + 4) / 8);
    const bx = mapX(i);
    path(g, [[tx, topY - S * .012], [tx, topY + S * .012]], P.ice, 1.3, .65);
    path(g, [[bx, lowY - S * .014], [bx, lowY + S * .014]], P.cyan, 1.3, .72);
    if (i > -4 && i < 4) {
      const bend = [[tx, topY + S * .015], [mix(tx, bx, .38), mix(topY, lowY, .37)], [bx, lowY - S * .012]];
      path(g, bend, P.cyan, 1, .08 + .06 * (i + 4));
    }
  }
  text(g, '−1', left, lowY + S * .04, Math.min(13, S * .021), P.gold, 'center', 700, .72);
  text(g, '+1', right, lowY + S * .04, Math.min(13, S * .021), P.gold, 'center', 700, .72);
  const psi = mix(0, 4, ease(p));
  const equalX = left + span * ((psi + 4) / 8);
  const boundedX = mapX(psi);
  path(g, [[equalX, topY], [boundedX, lowY]], P.gold, Math.max(1.6, S * .003), .55);
  circle(g, equalX, topY, S * .009, P.gold, { glow: S * .033 });
  circle(g, boundedX, lowY, S * .009, P.gold, { glow: S * .033 });
  for (const edgeX of [left, right]) {
    path(g, [[edgeX, lowY - S * .035], [edgeX, lowY + S * .035]], P.gold, 2, .56);
  }
}

const loopA = disk.C(0, 0);
const loopB = disk.C(.58, .08);
const loopC = disk.add(loopB, disk.C(-.19, .57));
const loopSegments = [
  disk.geodesic(loopA, loopB, 42),
  disk.geodesic(loopB, loopC, 42),
  disk.geodesic(loopC, loopA, 42),
];
const loopRoute = [...loopSegments[0], ...loopSegments[1].slice(1), ...loopSegments[2].slice(1)];
const loopTurn = disk.gyrationAngle(loopB, disk.C(-.19, .57));

function sceneLoop(g, w, h, p) {
  const S = Math.min(w, h);
  const cx = w * .5, cy = h * .48;
  const rad = Math.min(w * .33, h * .35);
  glow(g, cx, cy, rad * 1.36, P.cyan, .16);
  circle(g, cx, cy, rad, P.ice, { fill: false, width: 1.7, alpha: .66 });
  for (const rho of [1, 2, 3, 4]) {
    circle(g, cx, cy, rad * Math.tanh(rho / 2), P.cyan, { fill: false, width: 1, alpha: .14 });
  }
  for (let i = 0; i < 12; i++) {
    const a = i * TAU / 12;
    path(g, [[cx, cy], [cx + Math.cos(a) * rad, cy - Math.sin(a) * rad]], P.cyan, 1, .07);
  }
  const xy = (v) => [cx + v.x * rad, cy - v.y * rad];
  loopSegments.forEach((seg) => path(g, seg.map(xy), P.gold, Math.max(1.8, S * .0037), .52));
  const routeIndex = Math.min(loopRoute.length - 1, Math.floor(ease(p) * (loopRoute.length - 1)));
  path(g, loopRoute.slice(0, routeIndex + 1).map(xy), P.gold, Math.max(2.2, S * .005), .9);
  const walker = xy(loopRoute[routeIndex]);
  circle(g, walker[0], walker[1], Math.max(3, S * .008), P.gold, { glow: S * .038 });
  const angle = loopTurn * ease((p - .73) / .27);
  const ar = rad * .23;
  path(g, [[cx, cy], [cx + Math.sin(angle) * ar, cy - Math.cos(angle) * ar]], P.gold, Math.max(2, S * .004), .95);
  path(g, [[cx, cy], [cx, cy - ar]], P.ice, 1.4, .33, [4, 4]);
  const ah = [cx + Math.sin(angle) * ar, cy - Math.cos(angle) * ar];
  const tail = [ah[0] - Math.sin(angle) * S * .022, ah[1] + Math.cos(angle) * S * .022];
  triangle(g, [ah,
    [tail[0] - Math.cos(angle) * S * .011, tail[1] - Math.sin(angle) * S * .011],
    [tail[0] + Math.cos(angle) * S * .011, tail[1] + Math.sin(angle) * S * .011]], P.gold, .8);
  text(g, 'SELECTED HYPERBOLIC MODEL · CURVATURE −1', w * .5, h * .13,
    Math.min(w < 550 ? 10 : 16, S * .024), P.ice, 'center', 700, .85);
  text(g, 'CARRIED DIRECTION', w * .5, h * .78, Math.min(14, S * .021), P.gold, 'center', 700, .74);
}

function sceneEvidence(g, w, h, p) {
  const S = Math.min(w, h);
  const join = ease((p - .13) / .54);
  const left = w * (.19 + .09 * join), right = w * (.81 - .09 * join);
  const bandY = h * .46;
  const len = w * .32;
  for (const [x, c, sign] of [[left, P.gold, -1], [right, P.cyan, 1]]) {
    rounded(g, x - len * .5, bandY - S * .14, len, S * .28, S * .018,
      'rgba(12,37,49,.56)', c, .42 + .18 * join);
    for (let i = 0; i < 4; i++) {
      const yy = bandY - S * .09 + i * S * .055;
      const start = x - len * .37;
      const width = len * (.38 + .36 * nrand(i + (sign + 1) * 9));
      path(g, [[start, yy], [start + width, yy]], c, Math.max(1.6, S * .003), .34 + .36 * nrand(i + 16));
    }
  }
  // Shared observations brighten; empty segments remain visible as unknowns.
  const tl = [[w * .12, h * .69], [w * .88, h * .69]];
  path(g, tl, P.ice, Math.max(1.5, S * .0025), .5);
  for (let i = 0; i < 13; i++) {
    const x = w * (.12 + .76 * i / 12);
    path(g, [[x, h * .675], [x, h * .705]], i % 4 === 2 ? P.muted : i % 2 ? P.cyan : P.gold, 1.4, .55);
  }
  const overlaps = [[.31, .39], [.49, .58], [.68, .74]];
  overlaps.forEach(([a, b], i) => {
    const x = w * a, width = w * (b - a);
    rounded(g, x, h * .675, width, h * .03, S * .006, P.green, null, join * (.5 + .14 * i));
  });
  for (const a of [.43, .62, .8]) {
    rounded(g, w * a, h * .67, w * .025, h * .04, S * .005,
      'rgba(5,16,23,.8)', 'rgba(170,184,190,.38)', .8);
  }
  const cards = [
    { x: .2, color: P.green, head: 'REPLICATED', sub: 'effect-scale comparison' },
    { x: .5, color: P.coral, head: 'REFUTED', sub: 'H1 drug dial' },
    { x: .8, color: P.violet, head: 'OPEN', sub: 'H7 geometry' },
  ];
  for (const card of cards) {
    const x = w * card.x;
    const cw = Math.min(w * .27, S * .41);
    const y = h * .13;
    rounded(g, x - cw / 2, y, cw, S * .105, S * .01,
      'rgba(8,29,41,.8)', card.color, .5 + .45 * join);
    text(g, card.head, x, y + S * .036, Math.min(w < 550 ? 10 : 14, S * .022), card.color, 'center', 750, .9);
    if (w > 630) text(g, card.sub, x, y + S * .072, Math.min(11, S * .018), P.ice, 'center', 500, .7);
  }
  text(g, 'OVERLAP', w * .5, h * .78, Math.min(15, S * .024), P.green, 'center', 700, .5 + .3 * join);
  text(g, 'UNKNOWN', w * .82, h * .78, Math.min(15, S * .024), P.muted, 'center', 700, .65);
}

const sceneDrawers = [sceneInside, sceneFilters, sceneBanks, sceneState,
  sceneAction, sceneChart, sceneLoop, sceneEvidence];

function sceneAt(seconds) {
  const t = clamp(Number.isFinite(seconds) ? seconds : 0, 0, FILM_DURATION - 1e-7);
  let index = FILM_SCENES.findIndex((s) => t >= s.start && t < s.end);
  if (index < 0) index = FILM_SCENES.length - 1;
  const scene = FILM_SCENES[index];
  return { t, index, scene, progress: clamp((t - scene.start) / (scene.end - scene.start)) };
}

/** Draw one deterministic frame. `pointerX/Y` are optional centred values in [-1, 1].
 * Resize the backing store for the canvas's CSS size, capped at 2× DPR.
 * Returns the scene descriptor so a controller can synchronize accessible text.
 */
export function drawFilmFrame(canvas, seconds, { reducedMotion = false, pointerX = 0, pointerY = 0 } = {}) {
  if (!canvas || typeof canvas.getContext !== 'function') throw new TypeError('drawFilmFrame requires a canvas');
  const rect = typeof canvas.getBoundingClientRect === 'function' ? canvas.getBoundingClientRect() : null;
  const w = Math.max(1, Math.round((rect && rect.width) || canvas.clientWidth || canvas.width || 960));
  const h = Math.max(1, Math.round((rect && rect.height) || canvas.clientHeight || canvas.height || 540));
  const dpr = Math.min(2, Math.max(1, typeof window !== 'undefined' ? window.devicePixelRatio || 1 : 1));
  const backingW = Math.round(w * dpr), backingH = Math.round(h * dpr);
  if (canvas.width !== backingW || canvas.height !== backingH) {
    canvas.width = backingW;
    canvas.height = backingH;
  }
  const g = canvas.getContext('2d', { alpha: false });
  if (!g) throw new Error('A Canvas 2D context is required');
  g.setTransform(dpr, 0, 0, dpr, 0, 0);
  const frame = sceneAt(seconds);
  drawBackground(g, w, h, frame.t, reducedMotion);
  const render = (index, progress, alpha) => {
    g.save();
    g.globalAlpha *= alpha;
    sceneDrawers[index](g, w, h, progress,
      reducedMotion ? 0 : pointerX, reducedMotion ? 0 : pointerY);
    g.restore();
  };
  if (reducedMotion) {
    render(frame.index, .72, 1);
  } else if (frame.index > 0 && frame.t - frame.scene.start < 1.4) {
    const blend = ease((frame.t - frame.scene.start) / 1.4);
    render(frame.index - 1, 1, 1 - blend);
    render(frame.index, frame.progress, blend);
  } else {
    render(frame.index, frame.progress, 1);
  }
  return frame;
}
