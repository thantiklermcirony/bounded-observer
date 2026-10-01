// A dimensionless teaching model. These parameters are not fitted to people,
// any radiation source, or an emergency. See docs/radiation-safety.md.
export const LARGE = 0.8;
export const SMALL = 0.2;
export const CHALLENGE = 0.24;
export const EXPOSURE_SPAN = 0.55;

export function potential(x, model = 'curve') {
  if (x < 0 || !Number.isFinite(x)) throw new RangeError('state must be finite and nonnegative');
  if (model === 'quadratic') return x * x;
  if (model !== 'curve') throw new RangeError('unknown model');
  // An illustrative 5PL-shaped acute response C, converted to H=-log(1-C).
  // Its shape is deliberately not Jack Devanney's fitted parameter set.
  const z = (x / 0.55) ** 2.18;
  const response = 0.88 * (1 - (1 + z) ** -0.55);
  return -Math.log1p(-response);
}

export function potentialSlope(x, model = 'curve') {
  if (x < 0 || !Number.isFinite(x)) throw new RangeError('state must be finite and nonnegative');
  if (model === 'quadratic') return 2 * x;
  if (model !== 'curve') throw new RangeError('unknown model');
  if (x === 0) return 0;
  const z = (x / 0.55) ** 2.18;
  const response = 0.88 * (1 - (1 + z) ** -0.55);
  const responseSlope = 0.88 * 0.55 * (1 + z) ** -1.55 *
    2.18 * (x / 0.55) ** 1.18 / 0.55;
  return responseSlope / (1 - response);
}

export function pulseLedger(first, second, retention, model = 'curve') {
  if (![first, second, retention].every(Number.isFinite) || first < 0 || second < 0 || retention < 0 || retention > 1) {
    throw new RangeError('invalid pulse inputs');
  }
  return potential(first, model) + potential(retention * first + second, model) -
    potential(retention * first, model);
}

export function simulate({ order = 'large-small', gap = 0.9, tau = 1.25,
  model = 'curve', challenge = false, step = 0.006 } = {}) {
  if (order !== 'large-small' && order !== 'small-large') throw new RangeError('unknown order');
  if (![gap, tau, step].every(Number.isFinite) || gap < 0 || tau <= 0 || step <= 0) {
    throw new RangeError('invalid timing');
  }
  const doses = order === 'large-small' ? [LARGE, SMALL] : [SMALL, LARGE];
  const segments = [
    { kind: 'first', duration: EXPOSURE_SPAN, rate: doses[0] / EXPOSURE_SPAN },
    { kind: 'gap', duration: gap, rate: 0 },
    { kind: 'second', duration: EXPOSURE_SPAN, rate: doses[1] / EXPOSURE_SPAN },
  ];
  if (challenge) segments.push(
    { kind: 'wait', duration: 0.45, rate: 0 },
    { kind: 'challenge', duration: 0.4, rate: CHALLENGE / 0.4 },
  );
  let t = 0, x = 0, H = 0;
  const points = [{ t, x, H, rate: 0 }];
  let afterPair = null, beforeChallenge = null;
  const windows = [];
  for (const segment of segments) {
    const start = t;
    const n = Math.max(1, Math.ceil(segment.duration / step));
    const delta = segment.duration / n;
    for (let i = 0; i < n; i++) {
      const half = Math.exp(-delta / (2 * tau));
      const full = half * half;
      const midpoint = x * half + segment.rate * tau * (1 - half);
      H += potentialSlope(midpoint, model) * segment.rate * delta;
      x = x * full + segment.rate * tau * (1 - full);
      t += delta;
      points.push({ t, x, H, rate: segment.rate });
    }
    windows.push({ kind: segment.kind, start, end: t, dose: segment.rate * segment.duration });
    if (segment.kind === 'second') afterPair = { t, x, H };
    if (segment.kind === 'wait') beforeChallenge = { t, x, H };
  }
  return { order, model, gap, tau, challenge, points, windows, afterPair,
    beforeChallenge, final: { t, x, H } };
}
