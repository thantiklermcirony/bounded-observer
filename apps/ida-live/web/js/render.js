// Footage compositor: every frame of the chamber is built on the GPU from the video,
// shaped by the world state w = (q clarity, h rhythm, n novelty, p perturbation) and flow F.
// Nothing flickers: the rhythm is a 0.1 Hz swell (6 per minute) of at most 7% brightness; the
// storm's lightning is a single soft flash per knock, several seconds apart.
// Each scene has its own answer (uMode): ripples and mist, warmth, sway, speed, rain, stars.

const VS = `#version 300 es
in vec2 a; out vec2 uv;
void main() { uv = a * 0.5 + 0.5; gl_Position = vec4(a, 0.0, 1.0); }`;

const FS = `#version 300 es
precision highp float;
in vec2 uv; out vec4 o;
uniform sampler2D uTex;
uniform vec2 uRes; uniform float uVidAspect;
uniform float t, q, n, p, h, F, seed;
uniform vec3 uShake;   // x, y offset (uv units), rotation (rad)
uniform float uMode;   // 0 bloom, 1 steady, 2 water, 3 ride, 4 storm, 5 sky
uniform float uWarm, uOver, uUnder, uFlash, uZoom, uEdge;
uniform vec3 uDrop;    // water: x, y (screen uv) and age (s) of the last drop
uniform vec4 uMeteor;  // sky: x, y, angle, age
uniform float uPacer;  // breath pacer phase (radians): brighter on the inhale
uniform float uPeak;   // a tier climb: warm light gathers, then settles

float hash(vec2 x) { return fract(sin(dot(x, vec2(127.1, 311.7)) + seed) * 43758.5453); }
vec2 hash2(vec2 x) { return vec2(hash(x), hash(x + 17.17)); }
float vnoise(vec2 x) {
  vec2 i = floor(x), f = fract(x); f = f * f * (3.0 - 2.0 * f);
  return mix(mix(hash(i), hash(i + vec2(1, 0)), f.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), f.x), f.y);
}
float fbm(vec2 x) { float s = 0.0, a = 0.5; for (int k = 0; k < 5; k++) { s += a * vnoise(x); x = x * 2.03 + 11.1; a *= 0.5; } return s; }

vec2 cover(vec2 s) { // screen uv -> video uv, object-fit: cover
  float sa = uRes.x / uRes.y;
  vec2 c = (s - 0.5) * uZoom;
  if (sa > uVidAspect) c.y *= uVidAspect / sa; else c.x *= sa / uVidAspect;
  return c + 0.5;
}
vec3 tap(vec2 v) { return texture(uTex, vec2(v.x, 1.0 - v.y)).rgb; }

void main() {
  int mode = int(uMode + 0.5);
  vec2 s = uv;
  float asp = uRes.x / uRes.y;
  // camera sway / tremor / knock
  vec2 c0 = s - 0.5;
  float cr = cos(uShake.z), sr = sin(uShake.z);
  c0 = vec2(c0.x * cr - c0.y * sr / asp, c0.x * sr * asp + c0.y * cr);
  s = c0 + 0.5 + uShake.xy;
  // novelty: a slow warp field
  vec2 w = vec2(fbm(s * 2.4 + t * 0.07), fbm(s * 2.4 + 5.2 - t * 0.06)) - 0.5;
  if (mode == 2) {
    // water: wind ripples on the lower part of the frame, finer toward the horizon, and the
    // rings of a drop; the upper frame (sky, trees) only shimmers in the reflection's mist
    float water = smoothstep(0.58, 0.38, uv.y);
    float depth = 1.0 / (0.06 + max(0.0, 0.6 - uv.y));
    float rip = sin(uv.y * depth * 55.0 + t * 1.7 + fbm(s * vec2(5.0, 28.0) + t * 0.2) * 7.0);
    s.y += water * (0.0015 + 0.009 * n) * rip;
    s.x += water * 0.004 * n * (fbm(s * vec2(3.0, 18.0) - t * 0.3) - 0.5);
    vec2 dd = (uv - uDrop.xy) * vec2(asp, 3.2);
    float r = length(dd), a = uDrop.z;
    float ring = sin(46.0 * r - a * 11.0) * exp(-1.6 * a) * smoothstep(a * 0.32 + 0.06, a * 0.32 - 0.02, r) * smoothstep(0.0, 0.05, r);
    s += water * ring * 0.018 * normalize(dd + 1e-5) * vec2(1.0 / asp, 1.0 / 3.2);
    s += (1.0 - water) * n * 0.01 * w;
  } else {
    s += n * 0.05 * w;
    // the image breaks into shards that drift, and re-knit as novelty falls (not for water)
    vec2 g = s * vec2(7.0 * asp, 7.0);
    vec2 gi = floor(g), best = vec2(0); float bd = 9.0;
    for (int y = -1; y <= 1; y++) for (int x = -1; x <= 1; x++) {
      vec2 cell = gi + vec2(x, y);
      vec2 pt = cell + hash2(cell);
      float dd = length(g - pt);
      if (dd < bd) { bd = dd; best = cell; }
    }
    float shardAmt = mode == 5 ? 0.35 : 1.0;
    s += (hash2(best + 3.3) - 0.5) * n * n * 0.07 * shardAmt;
  }
  vec2 v = cover(s);
  // defocus: golden-angle disc, radius from clarity; ride adds a zoom blur when overdriven
  float rad = (1.0 - q) * 0.022;
  vec2 toC = (vec2(0.5) - v) * (mode == 3 ? uOver * 0.11 : 0.0);
  vec3 col = vec3(0); float wsum = 0.0;
  for (int k = 0; k < 20; k++) {
    float fk = float(k);
    float rr = sqrt((fk + 0.5) / 20.0) * rad;
    float an = fk * 2.39996;
    vec2 off = vec2(cos(an), sin(an)) * rr * vec2(1.0 / uVidAspect, 1.0) + toC * (fk / 19.0);
    col += tap(v + off); wsum += 1.0;
  }
  col /= wsum;
  // perturbation: chromatic split
  vec2 ca = vec2(p * 0.008, 0.0);
  col.r = mix(col.r, tap(v + ca).r, clamp(p * 1.5, 0.0, 1.0));
  col.b = mix(col.b, tap(v - ca).b, clamp(p * 1.5, 0.0, 1.0));
  float lum = dot(col, vec3(0.299, 0.587, 0.114));
  // clarity: fog (mist over water, murk elsewhere) and colour
  vec3 fog = (mode == 2 ? vec3(0.78, 0.8, 0.82) : vec3(0.42, 0.45, 0.52)) * (0.6 + 0.4 * lum);
  float fogAmt = (1.0 - q) * (mode == 2 ? 0.62 : mode == 5 ? 0.3 : 0.55) + (mode == 3 ? 0.35 * uUnder : 0.0);
  if (mode == 2) fogAmt *= 0.75 + 0.5 * fbm(uv * vec2(3.0, 6.0) + vec2(t * 0.03, 0.0)); // drifting mist
  col = mix(col, fog, clamp(fogAmt, 0.0, 0.9));
  float sat = clamp(0.28 + 0.85 * q - 0.35 * p + 0.35 * uWarm - 0.3 * uUnder, 0.0, 1.45);
  col = mix(vec3(lum), col, sat);
  col = (col - 0.5) * (0.85 + 0.25 * q) + 0.5;
  if (mode == 0) {
    // bloom: warmth gathers in the light as you lean toward it; the chill turns it blue
    col *= mix(vec3(1.0), vec3(1.1, 1.0, 0.86), uWarm);
    col += smoothstep(0.35, 1.0, lum) * uWarm * 0.12 * vec3(1.0, 0.8, 0.55);
    col = mix(col, vec3(lum) * vec3(0.82, 0.93, 1.12), clamp(p * 0.8, 0.0, 0.7));
  } else if (mode == 4) {
    // storm: darkness and rain until you come back; lightning on each hit
    col *= 0.5 + 0.5 * q;
    vec2 rg = vec2(uv.x * 260.0 + uv.y * 55.0, 0.0);
    float lane = floor(rg.x);
    float rn = hash(vec2(lane, floor(uv.y * 7.0 + t * 13.0 + hash(vec2(lane, 3.0)) * 7.0)));
    col += step(0.975, rn) * smoothstep(0.2, 1.0, fract(rg.x)) * (0.05 + 0.14 * n) * vec3(0.8, 0.85, 0.95);
    col += uFlash * (0.35 + 0.65 * lum) * vec3(0.8, 0.86, 1.0) * 0.9;
  } else if (mode == 5) {
    // sky: faint stars come up as you open (the darks lift, the points brighten)
    col = pow(max(col, 0.0), vec3(1.0 - 0.35 * q));
    col += smoothstep(0.25, 0.8, lum) * q * 0.25;
    // a meteor: attention's pull
    vec2 mdir = vec2(cos(uMeteor.z), sin(uMeteor.z));
    vec2 head = uMeteor.xy + mdir * uMeteor.w * 0.9;
    vec2 rel = (uv - head) * vec2(asp, 1.0);
    float along = dot(rel, -mdir), across = abs(dot(rel, vec2(-mdir.y, mdir.x)));
    float trail = smoothstep(0.22, 0.0, along) * step(0.0, along) * exp(-across * across / 0.00001);
    col += trail * smoothstep(0.9, 0.2, uMeteor.w) * vec3(0.9, 0.95, 1.0) * 1.4;
  }
  // rhythm: a slow swell with the breath pacer (6 per minute), as strong as h
  col *= 1.0 + 0.07 * h * (-cos(uPacer));
  // a climb: warm light gathers over the whole scene and settles (rise 0.4 s, fall 2.5 s)
  col += uPeak * (0.06 + 0.2 * smoothstep(0.25, 1.0, lum)) * vec3(1.0, 0.9, 0.72);
  // flow: light gathers in the highlights
  col += smoothstep(0.5, 1.0, lum) * F * 0.22 * vec3(1.0, 0.95, 0.86);
  // vignette narrows when out of the corridor
  vec2 dv = (uv - 0.5) * vec2(asp, 1.0);
  col *= 1.0 - (0.25 + 0.45 * (1.0 - F)) * dot(dv, dv);
  // loop seam
  col *= 0.55 + 0.45 * uEdge;
  // grain, stronger when unclear
  col += (hash(uv * uRes + fract(t)) - 0.5) * (0.015 + 0.05 * (1.0 - q));
  o = vec4(clamp(col, 0.0, 1.0), 1.0);
}`;

function compile(gl, type, src) {
  const s = gl.createShader(type);
  gl.shaderSource(s, src); gl.compileShader(s);
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
  return s;
}

export class Compositor {
  constructor(canvas, video) {
    this.c = canvas; this.v = video;
    const gl = canvas.getContext("webgl2", { antialias: false, alpha: false });
    if (!gl) throw new Error("No WebGL2");
    this.gl = gl;
    const pr = gl.createProgram();
    gl.attachShader(pr, compile(gl, gl.VERTEX_SHADER, VS));
    gl.attachShader(pr, compile(gl, gl.FRAGMENT_SHADER, FS));
    gl.linkProgram(pr);
    if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(pr));
    this.pr = pr;
    this.buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, this.buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    this.tex = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, this.tex);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    this.loc = {};
    for (const n of ["uTex", "uRes", "uVidAspect", "t", "q", "n", "p", "h", "F", "seed", "uShake", "uMode",
      "uWarm", "uOver", "uUnder", "uFlash", "uZoom", "uEdge", "uDrop", "uMeteor", "uPacer", "uPeak"]) this.loc[n] = gl.getUniformLocation(pr, n);
    this.aLoc = gl.getAttribLocation(pr, "a");
    this.seed = Math.random() * 100;
  }

  draw(w, time) {
    const gl = this.gl, c = this.c, v = this.v;
    const dpr = Math.min(1.5, window.devicePixelRatio || 1);
    const W = Math.round(c.clientWidth * dpr), H = Math.round(c.clientHeight * dpr);
    if (c.width !== W || c.height !== H) { c.width = W; c.height = H; }
    gl.viewport(0, 0, W, H);
    if (v.readyState >= 2) {
      gl.bindTexture(gl.TEXTURE_2D, this.tex);
      gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
      try { gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, v); } catch (e) { /* frame not ready */ }
    }
    gl.useProgram(this.pr);
    gl.bindBuffer(gl.ARRAY_BUFFER, this.buf);
    gl.enableVertexAttribArray(this.aLoc);
    gl.vertexAttribPointer(this.aLoc, 2, gl.FLOAT, false, 0, 0);
    gl.uniform1i(this.loc.uTex, 0);
    gl.uniform2f(this.loc.uRes, W, H);
    gl.uniform1f(this.loc.uVidAspect, v.videoWidth && v.videoHeight ? v.videoWidth / v.videoHeight : 16 / 9);
    gl.uniform1f(this.loc.t, time);
    gl.uniform1f(this.loc.q, w.q); gl.uniform1f(this.loc.n, w.n); gl.uniform1f(this.loc.p, w.p);
    gl.uniform1f(this.loc.h, w.h); gl.uniform1f(this.loc.F, w.F);
    gl.uniform1f(this.loc.seed, this.seed);
    gl.uniform3f(this.loc.uShake, w.sx || 0, w.sy || 0, w.sr || 0);
    gl.uniform1f(this.loc.uMode, w.mode || 0);
    gl.uniform1f(this.loc.uWarm, w.warm || 0); gl.uniform1f(this.loc.uOver, w.over || 0);
    gl.uniform1f(this.loc.uUnder, w.under || 0); gl.uniform1f(this.loc.uFlash, w.flash || 0);
    gl.uniform1f(this.loc.uZoom, w.zoom || 1); gl.uniform1f(this.loc.uEdge, w.edge ?? 1);
    const d = w.drop || [0.5, 0.3, 9], m = w.meteor || [0, 0, 0, 9];
    gl.uniform3f(this.loc.uDrop, d[0], d[1], d[2]);
    gl.uniform4f(this.loc.uMeteor, m[0], m[1], m[2], m[3]);
    gl.uniform1f(this.loc.uPeak, Math.min(1, w.peak || 0));
    gl.uniform1f(this.loc.uPacer, (w.pacer ?? 0.628 * time) % 6.2831853);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }
}
