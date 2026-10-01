/* A fictional valley seen from a single lived position at a time.
   This draws only observeValley(world)'s public scene and era. The distant
   landscape is scenery, never a diagram of the private world model. */

const TAU = Math.PI * 2;
const clamp = (n, lo, hi) => Math.min(hi, Math.max(lo, n));

function prepare(canvas) {
  const w = canvas.clientWidth || canvas.width || 1200;
  const h = canvas.clientHeight || canvas.height || 680;
  if (!w || !h) return null;
  const dpr = clamp(typeof window === 'undefined' ? 1 : window.devicePixelRatio || 1, 1, 2);
  const pw = Math.round(w * dpr);
  const ph = Math.round(h * dpr);
  if (canvas.width !== pw || canvas.height !== ph) {
    canvas.width = pw;
    canvas.height = ph;
  }
  const g = canvas.getContext('2d');
  if (!g) return null;
  g.setTransform(dpr, 0, 0, dpr, 0, 0);
  g.clearRect(0, 0, w, h);
  return { g, w, h };
}

function stroke(g, points, color, width = 1) {
  g.beginPath();
  g.moveTo(points[0][0], points[0][1]);
  for (let i = 1; i < points.length; i++) g.lineTo(points[i][0], points[i][1]);
  g.strokeStyle = color;
  g.lineWidth = width;
  g.stroke();
}

function roundRect(g, x, y, w, h, r, fill, border) {
  r = Math.min(r, w / 2, h / 2);
  g.beginPath();
  g.moveTo(x + r, y);
  g.lineTo(x + w - r, y);
  g.quadraticCurveTo(x + w, y, x + w, y + r);
  g.lineTo(x + w, y + h - r);
  g.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  g.lineTo(x + r, y + h);
  g.quadraticCurveTo(x, y + h, x + r, y);
  g.closePath();
  if (fill) { g.fillStyle = fill; g.fill(); }
  if (border) { g.strokeStyle = border; g.lineWidth = 1; g.stroke(); }
}

function sky(g, w, h, kind) {
  const storm = /storm|rain|dark/i.test(kind || '');
  const clear = /clear|sun|bright/i.test(kind || '');
  const gradient = g.createLinearGradient(0, 0, 0, h * 0.68);
  if (storm) {
    gradient.addColorStop(0, '#17252f');
    gradient.addColorStop(0.58, '#435a60');
    gradient.addColorStop(1, '#82948a');
  } else if (clear) {
    gradient.addColorStop(0, '#1e3c50');
    gradient.addColorStop(0.55, '#71969a');
    gradient.addColorStop(1, '#d1b995');
  } else {
    gradient.addColorStop(0, '#263b49');
    gradient.addColorStop(0.58, '#829494');
    gradient.addColorStop(1, '#c4baa0');
  }
  g.fillStyle = gradient;
  g.fillRect(0, 0, w, h);
  const glow = g.createRadialGradient(w * 0.7, h * 0.31, 0, w * 0.7, h * 0.31, w * 0.5);
  glow.addColorStop(0, clear ? 'rgba(255,211,143,.30)' : 'rgba(236,211,164,.11)');
  glow.addColorStop(1, 'rgba(255,211,143,0)');
  g.fillStyle = glow;
  g.fillRect(0, 0, w, h);
  for (const cloud of [
    [0.08, 0.16, 0.21, 0.045], [0.34, 0.12, 0.28, 0.055],
    [0.75, 0.20, 0.31, 0.06], [0.53, 0.28, 0.19, 0.035],
  ]) {
    g.fillStyle = storm ? 'rgba(10,28,34,.19)' : 'rgba(234,225,201,.16)';
    g.beginPath();
    g.ellipse(w * cloud[0], h * cloud[1], w * cloud[2], h * cloud[3], 0, 0, TAU);
    g.fill();
  }
  if (storm) {
    g.strokeStyle = 'rgba(210,222,215,.19)';
    g.lineWidth = 1;
    for (let i = 0; i < 45; i++) {
      const x = (i * 137.5 % 1220) / 1220 * w;
      const y = (i * 63.7 % 680) / 680 * h;
      stroke(g, [[x, y], [x - w * 0.006, y + h * 0.03]], 'rgba(210,222,215,.19)');
    }
  }
}

function distantHills(g, w, h, high) {
  const baseline = high ? 0.46 : 0.52;
  g.fillStyle = '#536c6a';
  g.beginPath();
  g.moveTo(0, h * baseline);
  g.bezierCurveTo(w * 0.16, h * 0.29, w * 0.25, h * 0.44, w * 0.42, h * 0.34);
  g.bezierCurveTo(w * 0.58, h * 0.26, w * 0.72, h * 0.43, w, h * 0.27);
  g.lineTo(w, h * 0.68);
  g.lineTo(0, h * 0.68);
  g.closePath();
  g.fill();
  g.fillStyle = '#334f51';
  g.beginPath();
  g.moveTo(0, h * (baseline + 0.07));
  g.bezierCurveTo(w * 0.12, h * 0.49, w * 0.20, h * 0.37, w * 0.37, h * 0.50);
  g.bezierCurveTo(w * 0.52, h * 0.39, w * 0.68, h * 0.54, w * 0.85, h * 0.40);
  g.lineTo(w, h * 0.48);
  g.lineTo(w, h * 0.70);
  g.lineTo(0, h * 0.70);
  g.closePath();
  g.fill();
  stroke(g, [[0, h * 0.58], [w * 0.2, h * 0.51], [w * 0.42, h * 0.53],
    [w * 0.73, h * 0.49], [w, h * 0.48]], 'rgba(226,222,188,.09)', Math.max(1, h * 0.002));
}

function riverHighlight(g, w, h, segments) {
  for (const segment of segments) {
    stroke(g, segment.map(([x, y]) => [x * w, y * h]), 'rgba(216,221,199,.31)', Math.max(1, h * 0.002));
  }
}

function estuaryTerrain(g, w, h, scene) {
  const low = scene.riverLevel === 'low';
  const surge = scene.riverLevel === 'surge';
  g.fillStyle = '#53614e';
  g.fillRect(0, h * 0.54, w, h * 0.46);
  g.fillStyle = '#787960';
  g.beginPath();
  g.moveTo(0, h * 0.62);
  g.bezierCurveTo(w * 0.25, h * 0.51, w * 0.38, h * 0.63, w * 0.59, h * 0.55);
  g.lineTo(w, h * 0.64);
  g.lineTo(w, h);
  g.lineTo(0, h);
  g.closePath();
  g.fill();

  // Exposed banks stay broad in the low-water view. Water is visible in the
  // same river corridor under either public river-level reading.
  g.fillStyle = '#9c9473';
  g.beginPath();
  g.moveTo(w * 0.57, h * 0.57);
  g.bezierCurveTo(w * 0.47, h * 0.64, w * 0.38, h * 0.76, w * 0.19, h);
  g.lineTo(w, h);
  g.bezierCurveTo(w * 0.87, h * 0.80, w * 0.72, h * 0.64, w * 0.68, h * 0.57);
  g.closePath();
  g.fill();

  const water = g.createLinearGradient(w * 0.6, h * 0.56, w * 0.62, h);
  water.addColorStop(0, '#4f7b79');
  water.addColorStop(0.55, '#305a62');
  water.addColorStop(1, '#163b48');
  g.fillStyle = water;
  g.beginPath();
  g.moveTo(w * (low ? 0.59 : surge ? 0.48 : 0.54), h * 0.57);
  g.bezierCurveTo(w * (low ? 0.54 : surge ? 0.39 : 0.47), h * 0.67,
    w * (low ? 0.50 : surge ? 0.31 : 0.39), h * 0.79,
    w * (low ? 0.42 : surge ? 0.13 : 0.24), h);
  g.lineTo(w * (low ? 0.83 : surge ? 1 : 0.96), h);
  g.bezierCurveTo(w * (low ? 0.72 : surge ? 0.91 : 0.81), h * 0.78,
    w * (surge ? 0.72 : 0.65), h * 0.63, w * 0.65, h * 0.57);
  g.closePath();
  g.fill();
  riverHighlight(g, w, h, [
    [[0.59, 0.63], [0.60, 0.66], [0.58, 0.69]],
    [[0.55, 0.77], [0.61, 0.76], [0.66, 0.78]],
    [[0.45, 0.91], [0.55, 0.90], [0.63, 0.93]],
  ]);
  if (surge) {
    riverHighlight(g, w, h, [
      [[0.28, 0.84], [0.42, 0.82], [0.58, 0.85]],
      [[0.36, 0.94], [0.56, 0.93], [0.79, 0.96]],
    ]);
  }
  if (low) {
    for (const [x, y, rx] of [[0.42, 0.76, 0.043], [0.30, 0.91, 0.055], [0.75, 0.87, 0.067]]) {
      g.fillStyle = 'rgba(206,184,137,.46)';
      g.beginPath();
      g.ellipse(w * x, h * y, w * rx, h * 0.009, -0.16, 0, TAU);
      g.fill();
    }
  }
  g.fillStyle = '#334b40';
  g.beginPath();
  g.moveTo(0, h * 0.68);
  g.bezierCurveTo(w * 0.13, h * 0.63, w * 0.30, h * 0.66, w * 0.42, h * 0.70);
  g.lineTo(w * 0.26, h);
  g.lineTo(0, h);
  g.closePath();
  g.fill();
}

function ridgeTerrain(g, w, h, scene) {
  const pooled = scene.riverLevel === 'pooled';
  const managed = scene.riverLevel === 'managed';
  g.fillStyle = '#65806e';
  g.fillRect(0, h * 0.52, w, h * 0.48);
  g.fillStyle = '#3d6255';
  g.beginPath();
  g.moveTo(0, h * 0.60);
  g.bezierCurveTo(w * 0.18, h * 0.45, w * 0.36, h * 0.57, w * 0.54, h * 0.58);
  g.bezierCurveTo(w * 0.79, h * 0.65, w * 0.85, h * 0.44, w, h * 0.49);
  g.lineTo(w, h);
  g.lineTo(0, h);
  g.closePath();
  g.fill();

  // Above the gate a broad visible pool holds water; downstream the channel
  // contracts. This is a view from the ridge, not an overhead map.
  const pool = g.createLinearGradient(0, h * 0.48, w * 0.64, h * 0.70);
  pool.addColorStop(0, '#688f8a');
  pool.addColorStop(1, '#315e67');
  g.fillStyle = pool;
  g.beginPath();
  g.moveTo(0, h * (pooled ? 0.55 : managed ? 0.565 : 0.59));
  g.bezierCurveTo(w * 0.18, h * (pooled ? 0.53 : 0.57), w * 0.36, h * 0.50, w * 0.60, h * 0.57);
  g.lineTo(w * 0.66, h * 0.61);
  g.bezierCurveTo(w * 0.50, h * (pooled ? 0.69 : managed ? 0.665 : 0.64),
    w * 0.30, h * (pooled ? 0.75 : managed ? 0.72 : 0.69),
    0, h * (pooled ? 0.74 : managed ? 0.71 : 0.68));
  g.closePath();
  g.fill();
  const downstream = g.createLinearGradient(w * 0.63, h * 0.6, w * 0.41, h);
  downstream.addColorStop(0, '#426e70');
  downstream.addColorStop(1, '#173d49');
  g.fillStyle = downstream;
  g.beginPath();
  g.moveTo(w * 0.64, h * 0.60);
  g.bezierCurveTo(w * 0.60, h * 0.73, w * 0.48, h * 0.84, w * 0.25, h);
  g.lineTo(w * 0.45, h);
  g.bezierCurveTo(w * 0.65, h * 0.86, w * 0.70, h * 0.72, w * 0.70, h * 0.60);
  g.closePath();
  g.fill();
  riverHighlight(g, w, h, [
    [[0.05, 0.62], [0.20, 0.63], [0.32, 0.60]],
    [[0.40, 0.65], [0.49, 0.64], [0.55, 0.61]],
    [[0.60, 0.77], [0.56, 0.80], [0.50, 0.84]],
  ]);

  g.fillStyle = '#29483f';
  g.beginPath();
  g.moveTo(w * 0.78, h * 0.49);
  g.bezierCurveTo(w * 0.76, h * 0.61, w * 0.79, h * 0.72, w, h * 0.75);
  g.lineTo(w, h);
  g.lineTo(w * 0.60, h);
  g.bezierCurveTo(w * 0.67, h * 0.85, w * 0.72, h * 0.64, w * 0.78, h * 0.49);
  g.fill();
}

function houses(g, w, h, era, location) {
  const count = clamp(4 + era * 3, 4, 12);
  const ridge = location === 'ridge';
  for (let i = 0; i < count; i++) {
    const row = Math.floor(i / 4);
    const col = i % 4;
    const x = ridge ? w * (0.10 + col * 0.095 + row * 0.02)
      : w * (0.08 + col * 0.095 + row * 0.015);
    const y = ridge ? h * (0.56 + row * 0.042 + col * 0.006)
      : h * (0.57 + row * 0.043 + col * 0.006);
    const size = Math.max(7, Math.min(w * 0.019, h * (ridge ? 0.029 : 0.038)) * (1 + row * 0.08));
    g.fillStyle = i % 3 === 0 ? '#c6b48b' : '#a79776';
    g.fillRect(x - size * 0.46, y - size * 0.64, size * 0.92, size * 0.64);
    g.fillStyle = i % 2 ? '#514a42' : '#61544a';
    g.beginPath();
    g.moveTo(x - size * 0.62, y - size * 0.62);
    g.lineTo(x, y - size * 1.1);
    g.lineTo(x + size * 0.62, y - size * 0.62);
    g.closePath();
    g.fill();
    if (era > 0 && i % 3 === 0) {
      g.fillStyle = 'rgba(237,197,124,.69)';
      g.fillRect(x - size * 0.08, y - size * 0.47, size * 0.16, size * 0.15);
    }
  }
  if (era > 1) {
    const x = ridge ? w * 0.41 : w * 0.34;
    const y = ridge ? h * 0.58 : h * 0.60;
    const tower = Math.max(17, Math.min(w * 0.025, h * 0.065));
    g.fillStyle = '#b9a77f';
    g.fillRect(x - tower * 0.25, y - tower, tower * 0.5, tower);
    g.fillStyle = '#514b40';
    g.beginPath();
    g.moveTo(x - tower * 0.39, y - tower);
    g.lineTo(x, y - tower * 1.29);
    g.lineTo(x + tower * 0.39, y - tower);
    g.closePath();
    g.fill();
  }
}

function person(g, x, y, size, coat, carrying) {
  g.save();
  g.fillStyle = '#d1b999';
  g.beginPath();
  g.arc(x, y - size * 0.79, size * 0.11, 0, TAU);
  g.fill();
  g.fillStyle = coat;
  g.beginPath();
  g.moveTo(x - size * 0.12, y - size * 0.66);
  g.lineTo(x + size * 0.12, y - size * 0.66);
  g.lineTo(x + size * 0.20, y - size * 0.22);
  g.lineTo(x - size * 0.20, y - size * 0.22);
  g.closePath();
  g.fill();
  stroke(g, [[x - size * 0.05, y - size * 0.20], [x - size * 0.08, y]], '#182729', Math.max(1, size * 0.07));
  stroke(g, [[x + size * 0.05, y - size * 0.20], [x + size * 0.09, y]], '#182729', Math.max(1, size * 0.07));
  stroke(g, [[x - size * 0.11, y - size * 0.56], [x - size * 0.25, y - size * 0.32]],
    coat, Math.max(1, size * 0.07));
  stroke(g, [[x + size * 0.11, y - size * 0.56], [x + size * 0.24, y - size * 0.30]],
    coat, Math.max(1, size * 0.07));
  if (carrying) {
    g.fillStyle = '#8b6745';
    g.beginPath();
    g.ellipse(x + size * 0.26, y - size * 0.24, size * 0.15, size * 0.10, 0, 0, TAU);
    g.fill();
    stroke(g, [[x + size * 0.16, y - size * 0.28], [x + size * 0.20, y - size * 0.40],
      [x + size * 0.33, y - size * 0.40], [x + size * 0.36, y - size * 0.28]],
    '#b89565', Math.max(1, size * 0.05));
  }
  g.restore();
}

function civicLife(g, w, h, era, location) {
  if (location === 'estuary') {
    // A working bank: awnings, baskets, a boathouse, and people moving goods.
    const stalls = era === 0 ? 2 : era === 1 ? 3 : 4;
    for (let i = 0; i < stalls; i++) {
      const x = w * (0.055 + i * 0.073);
      const y = h * (0.695 + i * 0.014);
      const width = Math.max(15, w * 0.055);
      const height = Math.max(11, h * 0.042);
      g.fillStyle = i % 2 ? '#b8a47f' : '#b57359';
      g.beginPath();
      g.moveTo(x, y - height);
      g.lineTo(x + width * 0.45, y - height * 1.36);
      g.lineTo(x + width, y - height);
      g.closePath();
      g.fill();
      stroke(g, [[x + width * 0.07, y - height], [x + width * 0.07, y]],
        '#554a3c', Math.max(1, h * 0.003));
      stroke(g, [[x + width * 0.92, y - height], [x + width * 0.92, y]],
        '#554a3c', Math.max(1, h * 0.003));
      g.fillStyle = '#6f533b';
      g.fillRect(x + width * 0.23, y - height * 0.43, width * 0.49, height * 0.28);
      for (let j = 0; j < 3; j++) {
        g.fillStyle = j % 2 ? '#c6a96f' : '#d0ba83';
        g.beginPath();
        g.arc(x + width * (0.33 + j * 0.13), y - height * 0.35,
          Math.max(1.5, h * 0.004), 0, TAU);
        g.fill();
      }
    }
    const houseX = w * 0.34;
    const houseY = h * 0.69;
    g.fillStyle = '#766952';
    g.fillRect(houseX, houseY - h * 0.057, w * 0.073, h * 0.057);
    g.fillStyle = '#403e36';
    g.beginPath();
    g.moveTo(houseX - w * 0.008, houseY - h * 0.057);
    g.lineTo(houseX + w * 0.036, houseY - h * 0.085);
    g.lineTo(houseX + w * 0.081, houseY - h * 0.057);
    g.closePath();
    g.fill();
    g.fillStyle = '#243e42';
    g.fillRect(houseX + w * 0.025, houseY - h * 0.042, w * 0.024, h * 0.042);
    stroke(g, [[w * 0.38, h * 0.72], [w * 0.49, h * 0.74]],
      '#957d5d', Math.max(2, h * 0.006));
    g.fillStyle = '#493f36';
    g.beginPath();
    g.ellipse(w * 0.48, h * 0.77, w * 0.045, h * 0.013, -0.14, 0, TAU);
    g.fill();
    person(g, w * 0.21, h * 0.75, Math.max(14, h * 0.052), '#56635d', true);
    person(g, w * 0.42, h * 0.76, Math.max(13, h * 0.047), '#654d44', false);
  } else {
    // Terraces, paths, and people tending them distinguish this high view from
    // an aerial chart. Later generations add visible rows and homes.
    const rows = 4 + era * 2;
    for (let i = 0; i < rows; i++) {
      const y = h * (0.73 + i * 0.033);
      const right = w * (0.46 - i * 0.035);
      stroke(g, [[w * 0.015, y], [w * 0.14, y - h * 0.014], [right, y + h * 0.014]],
        'rgba(200,184,126,.53)', Math.max(1, h * 0.002));
      stroke(g, [[w * 0.80, h * (0.57 + i * 0.036)],
        [w, h * (0.59 + i * 0.041)]], 'rgba(200,184,126,.44)', Math.max(1, h * 0.002));
    }
    stroke(g, [[w * 0.78, h * 0.57], [w * 0.87, h * 0.68], [w * 0.89, h * 0.83]],
      'rgba(204,184,137,.62)', Math.max(2, h * 0.008));
    person(g, w * 0.87, h * 0.75, Math.max(13, h * 0.044), '#75614b', true);
    person(g, w * 0.13, h * 0.80, Math.max(12, h * 0.038), '#54615a', false);
  }
}

function drawGate(g, w, h, location, scene, era) {
  const landmark = Array.isArray(scene.localLandmarks)
    ? scene.localLandmarks.find((item) => /gate/i.test(String(item.id || item.label || '')))
    : null;
  const gx = Number.isFinite(landmark?.x) ? clamp(landmark.x, 0.08, 0.92) : location === 'ridge' ? 0.65 : 0.62;
  // The landmark's normalized y marks the far sightline in the text model.
  // This panorama puts the gate's feet at the depicted waterline.
  const gy = location === 'ridge' ? 0.59 : 0.57;
  const x = gx * w;
  const y = gy * h;
  const s = location === 'ridge' ? Math.min(w * 0.054, h * 0.105) : Math.min(w * 0.082, h * 0.16);
  const width = s * 2.58;
  const top = y - s * 0.95;
  const closed = scene.gateClosed !== false;
  g.save();
  g.fillStyle = 'rgba(16,36,40,.30)';
  g.beginPath();
  g.ellipse(x, y + s * 0.12, width * 0.73, s * 0.16, 0, 0, TAU);
  g.fill();
  g.fillStyle = '#c5b092';
  g.fillRect(x - width * 0.52, top, s * 0.34, s * 1.13);
  g.fillRect(x + width * 0.52 - s * 0.34, top, s * 0.34, s * 1.13);
  g.fillStyle = '#6f6252';
  g.fillRect(x - width * 0.54, top - s * 0.14, s * 0.39, s * 0.16);
  g.fillRect(x + width * 0.54 - s * 0.39, top - s * 0.14, s * 0.39, s * 0.16);
  g.fillStyle = '#6b6052';
  g.fillRect(x - width * 0.51, top + s * 0.07, width * 1.02, s * 0.18);
  g.fillStyle = '#d2bb96';
  g.fillRect(x - width * 0.53, top - s * 0.04, width * 1.06, s * 0.10);
  const doorTop = top + s * 0.25;
  if (closed) {
    const door = g.createLinearGradient(x - width * 0.35, doorTop, x + width * 0.35, y);
    door.addColorStop(0, '#66594a');
    door.addColorStop(0.5, '#897458');
    door.addColorStop(1, '#62564a');
    g.fillStyle = door;
    g.fillRect(x - width * 0.35, doorTop, width * 0.7, y - doorTop);
    for (let i = -2; i <= 2; i++) {
      stroke(g, [[x + i * width * 0.115, doorTop], [x + i * width * 0.115, y]],
        'rgba(28,27,24,.40)', Math.max(1, s * 0.018));
    }
    stroke(g, [[x - width * 0.35, y - s * 0.13], [x + width * 0.35, y - s * 0.13]],
      'rgba(218,177,118,.48)', Math.max(1, s * 0.02));
  } else {
    g.fillStyle = 'rgba(19,61,70,.72)';
    g.fillRect(x - width * 0.35, doorTop, width * 0.7, y - doorTop);
    stroke(g, [[x - width * 0.33, doorTop], [x - width * 0.33, y]],
      'rgba(227,210,172,.65)', Math.max(1, s * 0.02));
    stroke(g, [[x + width * 0.33, doorTop], [x + width * 0.33, y]],
      'rgba(227,210,172,.65)', Math.max(1, s * 0.02));
  }
  if (era > 0) {
    g.fillStyle = '#d6b881';
    g.beginPath();
    g.arc(x, top + s * 0.17, Math.max(1.5, s * 0.045), 0, TAU);
    g.fill();
  }
  g.restore();
  return { x: x - width * 0.55, y: top - s * 0.2, width: width * 1.1, height: y - top + s * 0.35 };
}

function reeds(g, w, h, x, y, count, color) {
  for (let i = 0; i < count; i++) {
    const spread = (i - (count - 1) / 2) * w * 0.007;
    const topY = y - h * (0.042 + (i * 7 % 5) * 0.008);
    stroke(g, [[x + spread, y], [x + spread * 0.8 - w * 0.003, topY]], color, Math.max(1, h * 0.002));
    g.fillStyle = color;
    g.beginPath();
    g.ellipse(x + spread * 0.8 - w * 0.003, topY, Math.max(1, w * 0.002), h * 0.012,
      -0.25, 0, TAU);
    g.fill();
  }
}

function foreground(g, w, h, location, opts) {
  const time = Number(opts.time) || 0;
  const sway = opts.reducedMotion ? 0 : Math.sin(time * 0.0011) * Math.min(2, h * 0.003);
  if (location === 'ridge') {
    g.fillStyle = '#263b39';
    g.beginPath();
    g.moveTo(0, h * 0.91);
    g.lineTo(w * 0.10, h * 0.84);
    g.lineTo(w * 0.18, h * 0.88);
    g.lineTo(w * 0.30, h * 0.82);
    g.lineTo(w * 0.39, h);
    g.lineTo(0, h);
    g.closePath();
    g.fill();
    g.fillStyle = '#1b302f';
    g.beginPath();
    g.moveTo(w * 0.74, h);
    g.lineTo(w * 0.84, h * 0.85);
    g.lineTo(w * 0.94, h * 0.89);
    g.lineTo(w, h * 0.82);
    g.lineTo(w, h);
    g.closePath();
    g.fill();
    stroke(g, [[w * 0.79, h], [w * 0.79 + sway, h * 0.70]], '#9e8a67', Math.max(3, h * 0.009));
    stroke(g, [[w * 0.79 + sway, h * 0.71], [w * 0.78 + sway, h * 0.65]], '#d3b98d', Math.max(2, h * 0.003));
  } else {
    reeds(g, w, h, w * 0.08, h * 0.84, 8, '#263f35');
    reeds(g, w, h, w * 0.91, h * 0.82, 8, '#36523f');
    g.fillStyle = '#3e4037';
    g.fillRect(0, h * 0.87, w, h * 0.038);
    g.fillStyle = '#8b7859';
    g.fillRect(0, h * 0.86, w, h * 0.018);
    for (const x of [0.12, 0.86]) {
      g.fillStyle = '#3f423a';
      g.fillRect(w * x, h * 0.76, Math.max(8, w * 0.022), h * 0.24);
      g.fillStyle = '#a18a66';
      g.fillRect(w * x, h * 0.76, Math.max(8, w * 0.022), h * 0.025);
    }
  }
  // A restrained near-field hand anchors the view in a person at this site.
  const palmX = location === 'ridge' ? w * 0.74 : w * 0.68;
  const palmY = h * 0.96 + sway;
  const hand = Math.min(w * 0.115, h * 0.16);
  g.fillStyle = '#1b282a';
  g.strokeStyle = 'rgba(215,205,173,.48)';
  g.lineWidth = Math.max(1, h * 0.002);
  g.beginPath();
  g.moveTo(palmX - hand * 0.62, h);
  g.lineTo(palmX - hand * 0.44, palmY - hand * 0.28);
  g.quadraticCurveTo(palmX - hand * 0.36, palmY - hand * 0.51, palmX - hand * 0.20, palmY - hand * 0.48);
  g.lineTo(palmX - hand * 0.06, palmY - hand * 0.31);
  g.quadraticCurveTo(palmX + hand * 0.21, palmY - hand * 0.44, palmX + hand * 0.36, palmY - hand * 0.14);
  g.lineTo(palmX + hand * 0.52, h);
  g.closePath();
  g.fill();
  g.stroke();
  stroke(g, [[palmX - hand * 0.40, palmY + hand * 0.05],
    [palmX + hand * 0.36, palmY + hand * 0.05]], 'rgba(215,193,151,.48)', Math.max(1, h * 0.003));
}

function localLandmarks(g, w, h, scene) {
  const hits = [];
  const landmarks = Array.isArray(scene.localLandmarks) ? scene.localLandmarks : [];
  const fs = clamp(h * 0.021, 10, 14);
  for (const item of landmarks) {
    if (/gate/i.test(String(item.id || item.label || ''))) continue;
    if (!Number.isFinite(item.x) || !Number.isFinite(item.y)) continue;
    const x = clamp(item.x, 0, 1) * w;
    const y = clamp(item.y, 0, 1) * h;
    const label = String(item.label || item.id || '').slice(0, 25);
    if (!label) continue;
    const textWidth = Math.min(w * 0.32, label.length * fs * 0.64 + 18);
    const labelX = clamp(x - textWidth / 2, 6, w - textWidth - 6);
    const labelY = clamp(y - fs * 2.5, 6, h - fs * 2);
    stroke(g, [[x, y], [x, labelY + fs * 1.7]], 'rgba(244,226,184,.50)');
    g.fillStyle = '#edd6ab';
    g.beginPath();
    g.arc(x, y, Math.max(2, fs * 0.18), 0, TAU);
    g.fill();
    roundRect(g, labelX, labelY, textWidth, fs * 1.7, 3,
      'rgba(14,30,34,.82)', 'rgba(224,214,187,.48)');
    g.fillStyle = '#f5e4c7';
    g.textAlign = 'center';
    g.textBaseline = 'middle';
    g.font = `600 ${fs}px ui-sans-serif, system-ui, sans-serif`;
    g.fillText(label, labelX + textWidth / 2, labelY + fs * 0.84, textWidth - 8);
    hits.push({ id: item.id, x: labelX, y: labelY, width: textWidth, height: fs * 1.7 });
  }
  return hits;
}

function title(g, w, h, location, observation) {
  const scale = clamp(Math.min(w / 1200, h / 680), 0.60, 1.5);
  const margin = 20 * scale;
  const name = location === 'ridge' ? 'THE RIDGE' : 'THE ESTUARY';
  const subtitle = location === 'ridge' ? 'from above the gate' : 'from below the gate';
  const boxW = Math.min(w - margin * 2, 246 * scale);
  const boxH = 55 * scale;
  roundRect(g, margin, margin, boxW, boxH, 5 * scale,
    'rgba(11,26,30,.72)', 'rgba(226,211,174,.37)');
  g.fillStyle = '#f3e8d0';
  g.textAlign = 'left';
  g.textBaseline = 'top';
  g.font = `700 ${clamp(13 * scale, 11, 17)}px ui-sans-serif, system-ui, sans-serif`;
  g.fillText(name, margin + 12 * scale, margin + 10 * scale);
  g.fillStyle = '#c8d7cf';
  g.font = `500 ${clamp(11 * scale, 10, 14)}px ui-sans-serif, system-ui, sans-serif`;
  g.fillText(subtitle, margin + 12 * scale, margin + 31 * scale);
  if (Number.isFinite(observation.year)) {
    const year = `YEAR ${observation.year}`;
    const yearW = 81 * scale;
    roundRect(g, w - margin - yearW, margin, yearW, 29 * scale, 4 * scale,
      'rgba(11,26,30,.72)', 'rgba(226,211,174,.37)');
    g.fillStyle = '#f3e8d0';
    g.font = `700 ${clamp(11 * scale, 10, 14)}px ui-monospace, Consolas, monospace`;
    g.textAlign = 'center';
    g.textBaseline = 'middle';
    g.fillText(year, w - margin - yearW / 2, margin + 14.5 * scale);
  }
}

/**
 * Draw the current public view in CSS canvas pixels.
 * `observation` is the output of observeValley(world); only `scene`, `era`,
 * and `year` are read. `opts` may supply `{time, reducedMotion}` for the small
 * hand sway. All coordinates returned are CSS pixels relative to the canvas.
 * @returns {{gate:{x:number,y:number,width:number,height:number},landmarks:Array}}
 */
export function drawValley(canvas, observation = {}, opts = {}) {
  const surface = prepare(canvas);
  if (!surface) return { gate: null, landmarks: [] };
  const { g, w, h } = surface;
  const scene = observation.scene || {};
  const location = scene.location === 'ridge' ? 'ridge' : 'estuary';
  const era = clamp(Number.isFinite(observation.era) ? observation.era : 0, 0, 2);
  sky(g, w, h, scene.sky);
  distantHills(g, w, h, location === 'ridge');
  if (location === 'ridge') ridgeTerrain(g, w, h, scene);
  else estuaryTerrain(g, w, h, scene);
  houses(g, w, h, era, location);
  civicLife(g, w, h, era, location);
  const gate = drawGate(g, w, h, location, scene, era);
  const landmarks = localLandmarks(g, w, h, scene);
  foreground(g, w, h, location, opts);
  title(g, w, h, location, observation);
  return { gate, landmarks };
}
