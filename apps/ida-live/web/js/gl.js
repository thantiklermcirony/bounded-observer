// A small WebGL2 renderer: everything on screen is soft-edged, additive light.
// Lenses fill a Batch with triangles (pixel coordinates, premultiplied colour);
// the renderer draws the background, then the light, in one or two draw calls.

const VS = `#version 300 es
in vec2 a_pos; in vec4 a_col;
uniform vec2 u_res;
out vec4 v_col;
void main() {
  vec2 p = a_pos / u_res * 2.0 - 1.0;
  gl_Position = vec4(p.x, -p.y, 0.0, 1.0);
  v_col = a_col;
}`;
const FS = `#version 300 es
precision mediump float;
in vec4 v_col; out vec4 o;
void main() { o = v_col; }`;

// background: deep field with a faint horizon glow at the disk boundary
const BG_VS = `#version 300 es
in vec2 a_pos; out vec2 v_uv;
void main() { v_uv = a_pos * 0.5 + 0.5; gl_Position = vec4(a_pos, 0.0, 1.0); }`;
const BG_FS = `#version 300 es
precision highp float;
in vec2 v_uv; out vec4 o;
uniform vec2 u_res; uniform vec2 u_c; uniform float u_r; uniform float u_t; uniform float u_disk; uniform vec3 u_tint;
float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
void main() {
  vec2 px = vec2(v_uv.x, 1.0 - v_uv.y) * u_res;
  float d = length(px - u_c) / u_r;
  vec3 deep = vec3(0.012, 0.016, 0.034);
  vec3 col = deep + u_tint * 0.05 * exp(-d * d * 1.6);
  // horizon ring (the disk's boundary is infinitely far away)
  float ring = exp(-pow((d - 1.0) * 26.0, 2.0)) * u_disk;
  col += vec3(0.25, 0.45, 0.65) * ring * 0.22;
  col += vec3(0.02, 0.03, 0.06) * smoothstep(1.4, 0.0, d);
  // outside the disk: slightly darker
  col *= mix(1.0, 0.55, smoothstep(1.0, 1.02, d) * u_disk);
  // film grain so gradients never band
  col += (hash(px + fract(u_t)) - 0.5) / 255.0 * 2.0;
  o = vec4(col, 1.0);
}`;

function compile(gl, type, src) {
  const s = gl.createShader(type);
  gl.shaderSource(s, src);
  gl.compileShader(s);
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
  return s;
}
function program(gl, vs, fs) {
  const p = gl.createProgram();
  gl.attachShader(p, compile(gl, gl.VERTEX_SHADER, vs));
  gl.attachShader(p, compile(gl, gl.FRAGMENT_SHADER, fs));
  gl.linkProgram(p);
  if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
  return p;
}

// ------------------------------------------------------------------ geometry batch
export class Batch {
  constructor() { this.buf = new ArrayBuffer(1 << 22); this.f = new Float32Array(this.buf); this.u = new Uint8Array(this.buf); this.n = 0; }
  clear() { this.n = 0; }
  _grow() {
    const nb = new ArrayBuffer(this.buf.byteLength * 2);
    new Uint8Array(nb).set(this.u);
    this.buf = nb; this.f = new Float32Array(nb); this.u = new Uint8Array(nb);
  }
  // vertex: x, y (float32) + rgba (4 x uint8, premultiplied) = 12 bytes
  v(x, y, r, g, b, a) {
    if ((this.n + 1) * 12 > this.buf.byteLength) this._grow();
    const o = this.n * 3;
    this.f[o] = x; this.f[o + 1] = y;
    const ob = o * 4 + 8;
    a = a < 0 ? 0 : a > 1 ? 1 : a;
    this.u[ob] = Math.min(255, r * a * 255); this.u[ob + 1] = Math.min(255, g * a * 255);
    this.u[ob + 2] = Math.min(255, b * a * 255); this.u[ob + 3] = a * 255;
    this.n++;
  }
  tri(x1, y1, c1, x2, y2, c2, x3, y3, c3) {
    this.v(x1, y1, c1[0], c1[1], c1[2], c1[3]);
    this.v(x2, y2, c2[0], c2[1], c2[2], c2[3]);
    this.v(x3, y3, c3[0], c3[1], c3[2], c3[3]);
  }
  quad(ax, ay, ca, bx, by, cb, cx, cy, cc, dx, dy, cd) { // a-b on one side, d-c on the other
    this.tri(ax, ay, ca, bx, by, cb, cx, cy, cc);
    this.tri(ax, ay, ca, cx, cy, cc, dx, dy, cd);
  }

  // A soft glowing line. pts: flat array [x, y, halfWidthPx, r, g, b, a, ...] (7 per point).
  // glow: extra soft halo as a multiple of the width.
  ribbon(pts, glow = 3) {
    const n = pts.length / 7;
    if (n < 2) return;
    let pnx = 0, pny = 0;
    const L = [], R = [], GL = [], GR = [], C = [], CE = [], CG = [];
    for (let i = 0; i < n; i++) {
      const o = i * 7;
      const x = pts[o], y = pts[o + 1];
      const j0 = Math.max(0, i - 1) * 7, j1 = Math.min(n - 1, i + 1) * 7;
      let dx = pts[j1] - pts[j0], dy = pts[j1 + 1] - pts[j0 + 1];
      const len = Math.hypot(dx, dy);
      let nx, ny;
      if (len < 1e-6) { nx = pnx; ny = pny; } else { nx = -dy / len; ny = dx / len; }
      pnx = nx; pny = ny;
      const w = Math.max(0.35, pts[o + 2]);
      const gw = w * glow + 1.2;
      const r = pts[o + 3], g = pts[o + 4], b = pts[o + 5], a = pts[o + 6];
      L.push(x + nx * w, y + ny * w); R.push(x - nx * w, y - ny * w);
      GL.push(x + nx * gw, y + ny * gw); GR.push(x - nx * gw, y - ny * gw);
      C.push(x, y);
      // core is brighter toward white when the line is strong
      const hot = Math.min(1, a) * 0.35;
      CE.push([r + (1 - r) * hot, g + (1 - g) * hot, b + (1 - b) * hot, a]);
      CG.push([r, g, b, a * 0.16]);
    }
    const Z = [0, 0, 0, 0];
    for (let i = 0; i < n - 1; i++) {
      const i2 = i * 2, j2 = i2 + 2;
      const ce = CE[i], cf = CE[i + 1], ge = CG[i], gf = CG[i + 1];
      const e0 = [ce[0], ce[1], ce[2], ce[3] * 0.55], e1 = [cf[0], cf[1], cf[2], cf[3] * 0.55];
      // core: edge(0.55a) - centre(a) - edge(0.55a)
      this.quad(L[i2], L[i2 + 1], e0, C[i2], C[i2 + 1], ce, C[j2], C[j2 + 1], cf, L[j2], L[j2 + 1], e1);
      this.quad(C[i2], C[i2 + 1], ce, R[i2], R[i2 + 1], e0, R[j2], R[j2 + 1], e1, C[j2], C[j2 + 1], cf);
      if (glow > 0) { // halo: centre(glow) fading to nothing
        this.quad(GL[i2], GL[i2 + 1], Z, C[i2], C[i2 + 1], ge, C[j2], C[j2 + 1], gf, GL[j2], GL[j2 + 1], Z);
        this.quad(C[i2], C[i2 + 1], ge, GR[i2], GR[i2 + 1], Z, GR[j2], GR[j2 + 1], Z, C[j2], C[j2 + 1], gf);
      }
    }
  }

  // a translucent sheet between two polylines of equal length: [x, y, r, g, b, a] each
  sheet(A, B) {
    const n = Math.min(A.length, B.length) / 6;
    for (let i = 0; i < n - 1; i++) {
      const o = i * 6, p = o + 6;
      this.quad(A[o], A[o + 1], [A[o + 2], A[o + 3], A[o + 4], A[o + 5]],
                B[o], B[o + 1], [B[o + 2], B[o + 3], B[o + 4], B[o + 5]],
                B[p], B[p + 1], [B[p + 2], B[p + 3], B[p + 4], B[p + 5]],
                A[p], A[p + 1], [A[p + 2], A[p + 3], A[p + 4], A[p + 5]]);
    }
  }

  // soft disc: bright centre fading to nothing at radius r
  glowDisc(x, y, r, col, seg = 28) {
    const Z = [col[0], col[1], col[2], 0];
    for (let k = 0; k < seg; k++) {
      const a0 = (k / seg) * Math.PI * 2, a1 = ((k + 1) / seg) * Math.PI * 2;
      this.tri(x, y, col, x + Math.cos(a0) * r, y + Math.sin(a0) * r, Z, x + Math.cos(a1) * r, y + Math.sin(a1) * r, Z);
    }
  }
  disc(x, y, r, col, seg = 24) {
    for (let k = 0; k < seg; k++) {
      const a0 = (k / seg) * Math.PI * 2, a1 = ((k + 1) / seg) * Math.PI * 2;
      this.tri(x, y, col, x + Math.cos(a0) * r, y + Math.sin(a0) * r, col, x + Math.cos(a1) * r, y + Math.sin(a1) * r, col);
    }
  }
  ring(x, y, r, w, col, seg = 64, glow = 2) {
    const pts = [];
    for (let k = 0; k <= seg; k++) {
      const a = (k / seg) * Math.PI * 2;
      pts.push(x + Math.cos(a) * r, y + Math.sin(a) * r, w, col[0], col[1], col[2], col[3]);
    }
    this.ribbon(pts, glow);
  }
}

// ------------------------------------------------------------------ renderer
export class Renderer {
  constructor(canvas) {
    this.canvas = canvas;
    const gl = canvas.getContext("webgl2", { antialias: true, premultipliedAlpha: true, alpha: false, powerPreference: "high-performance" });
    if (!gl) throw new Error("This computer's browser has no WebGL2.");
    this.gl = gl;
    this.prog = program(gl, VS, FS);
    this.bg = program(gl, BG_VS, BG_FS);
    this.vbo = gl.createBuffer();
    this.quadVbo = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, this.quadVbo);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]), gl.STATIC_DRAW);
    this.loc = {
      pos: gl.getAttribLocation(this.prog, "a_pos"), col: gl.getAttribLocation(this.prog, "a_col"),
      res: gl.getUniformLocation(this.prog, "u_res"),
      bpos: gl.getAttribLocation(this.bg, "a_pos"),
      bres: gl.getUniformLocation(this.bg, "u_res"), bc: gl.getUniformLocation(this.bg, "u_c"),
      br: gl.getUniformLocation(this.bg, "u_r"), bt: gl.getUniformLocation(this.bg, "u_t"),
      bdisk: gl.getUniformLocation(this.bg, "u_disk"), btint: gl.getUniformLocation(this.bg, "u_tint"),
    };
    this.dpr = 1; this.w = 1; this.h = 1;
    this.resize();
  }
  resize() {
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    const w = Math.round(this.canvas.clientWidth * dpr), h = Math.round(this.canvas.clientHeight * dpr);
    if (w !== this.canvas.width || h !== this.canvas.height) { this.canvas.width = w; this.canvas.height = h; }
    this.dpr = dpr; this.w = w; this.h = h;
  }
  draw(batch, bgOpts) {
    const gl = this.gl;
    gl.viewport(0, 0, this.w, this.h);
    gl.disable(gl.BLEND);
    gl.useProgram(this.bg);
    gl.bindBuffer(gl.ARRAY_BUFFER, this.quadVbo);
    gl.enableVertexAttribArray(this.loc.bpos);
    gl.vertexAttribPointer(this.loc.bpos, 2, gl.FLOAT, false, 0, 0);
    gl.uniform2f(this.loc.bres, this.w, this.h);
    gl.uniform2f(this.loc.bc, bgOpts.cx, bgOpts.cy);
    gl.uniform1f(this.loc.br, bgOpts.r);
    gl.uniform1f(this.loc.bt, bgOpts.t);
    gl.uniform1f(this.loc.bdisk, bgOpts.disk ?? 1);
    const tint = bgOpts.tint || [0.3, 0.5, 0.9];
    gl.uniform3f(this.loc.btint, tint[0], tint[1], tint[2]);
    gl.drawArrays(gl.TRIANGLES, 0, 6);
    gl.disableVertexAttribArray(this.loc.bpos);

    if (!batch.n) return;
    gl.useProgram(this.prog);
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.ONE, gl.ONE); // light adds up
    gl.bindBuffer(gl.ARRAY_BUFFER, this.vbo);
    gl.bufferData(gl.ARRAY_BUFFER, new Uint8Array(batch.buf, 0, batch.n * 12), gl.STREAM_DRAW);
    gl.enableVertexAttribArray(this.loc.pos);
    gl.vertexAttribPointer(this.loc.pos, 2, gl.FLOAT, false, 12, 0);
    gl.enableVertexAttribArray(this.loc.col);
    gl.vertexAttribPointer(this.loc.col, 4, gl.UNSIGNED_BYTE, true, 12, 8);
    gl.uniform2f(this.loc.res, this.w, this.h);
    gl.drawArrays(gl.TRIANGLES, 0, batch.n);
  }
}

// colour helpers
export function hsl(h, s, l) {
  h = ((h % 1) + 1) % 1;
  const f = (n) => { const k = (n + h * 12) % 12; const a = s * Math.min(l, 1 - l); return l - a * Math.max(-1, Math.min(k - 3, 9 - k, 1)); };
  return [f(0), f(8), f(4)];
}
export function hex(h) { const n = parseInt(h.slice(1), 16); return [((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255]; }
