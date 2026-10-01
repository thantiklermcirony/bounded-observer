/* Inside film — one fictional valley, two bounded viewpoints.
 * Images are original site assets. The player owns the accessible captions.
 * The story is constructed; a visual overlap is not a theorem of empathy,
 * agreement, historical explanation, or subjective consciousness.
 */
export const FILM_DURATION = 123;

export const FILM_SCENES = Object.freeze([
  {
    start: 0, end: 14, title: 'The shut gate',
    caption: 'The gate is shut. I know what that means.',
    narration: 'The gate is shut. From my bank, the river is thinning. I already know the story. I heard it before I knew the people across the water: when they close the gate, we pay.',
    claim: 'Fictional story. Gate 1 treats finite access as a premise; this image does not simulate or explain consciousness.',
  },
  {
    start: 14, end: 27, title: 'An inherited answer',
    caption: 'I inherited the answer before I saw the gate.',
    narration: 'I thought I was looking directly at the world. But my view carried old summers, rationed cups, names of people who waited, sentences repeated until they felt like sight. History had arrived with me.',
    claim: 'Fictional, selective transmission of records. No general law of real cultures is asserted.',
  },
  {
    start: 27, end: 46, title: 'The loss',
    caption: 'Our water fell. We rationed. That loss was real.',
    narration: 'We measure the falling channel. The loss is real. Children carry buckets farther. A record of harm is not a mistake. The mistake begins when that record pretends to tell us why the other bank acted.',
    claim: 'The water loss is a fact inside this constructed story. Its cause and the other bank’s intent are not yet established.',
  },
  {
    start: 46, end: 65, title: 'Across the river',
    caption: 'Across the river, another account survived.',
    narration: 'Across the river, Ridge remembers a different danger. Their wall broke under an old crest. They rebuilt it. From there, a closed gate looks less like punishment, more like protection. Their record, too, is true and incomplete.',
    claim: 'A second fictional observer adds evidence while remaining situated and fallible. This is not a theorem of empathy or agreement.',
  },
  {
    start: 65, end: 82, title: 'The crest',
    caption: 'They had watched a dangerous crest. I had not.',
    narration: 'Today the gauge is rising again. Neither inherited sentence can tell us whether opening the gate will help or flood another home. We need the reading both banks can check.',
    claim: 'The crest is an observation in the constructed world. That observation need not erase the loss on the other bank.',
  },
  {
    start: 82, end: 94, title: 'True, and incomplete',
    caption: 'What I saw was true. It was not enough.',
    narration: 'What I saw was true. It was not enough. I knew our loss. I was guessing at their reason. The guess had become a person in my mind, and I had begun to blame it.',
    claim: 'Fictional insight under Gate 1: access to a real loss can still leave another actor’s reason unknown. The story does not demonstrate Gate 2’s predictive-state criterion.',
  },
  {
    start: 94, end: 108, title: 'Different futures',
    caption: 'We each carried a different future for the other.',
    narration: 'Pull back. Each of us projects a future from a different past. One fact enters both views. It does not make the past fair or the risks equal. It changes which next actions we can see.',
    claim: 'The projected futures are fictional inferences, not observed facts. No theorem promises that another viewpoint produces agreement.',
  },
  {
    start: 108, end: 123, title: 'What we pass on',
    caption: 'We cannot change that day. We can change what the next generation inherits.',
    narration: 'They do not have to agree about everything. They can warn each other, share what the gauge shows, and choose a costly response together. That day is gone. What reaches the next generation is still being made.',
    claim: 'The common action and inherited record are possibilities in this constructed story. Shared evidence leaves unresolved uncertainty; it does not solve consciousness or guarantee moral unity.',
  },
].map((scene) => Object.freeze(scene)));

const ASSET_FILES = {
  observer: 'inside-observer.webp',
  ridge: 'inside-ridge.webp',
  gate: 'inside-gate.webp',
  inheritance: 'inside-inheritance.webp',
};
const assets = Object.fromEntries(Object.keys(ASSET_FILES).map((key) => [key, { image: null, ready: false }]));
let lastDraw = null;

export const FILM_ASSETS_READY = typeof Image === 'undefined'
  ? Promise.resolve(false)
  : Promise.all(Object.entries(ASSET_FILES).map(([key, file]) => new Promise((resolve) => {
      const image = new Image();
      image.decoding = 'async';
      image.onload = () => {
        assets[key].image = image;
        assets[key].ready = true;
        resolve(true);
      };
      image.onerror = () => resolve(false);
      image.src = new URL(file, import.meta.url).href;
    }))).then((results) => {
      if (lastDraw) drawFilmFrame(lastDraw.canvas, lastDraw.seconds, lastDraw.options);
      return results.every(Boolean);
    });

const C = {
  dark: '#07131b', navy: '#10232b', slate: '#234453',
  ink: '#ecf1ea', dim: '#9cb2b5', gold: '#ffd39a',
  ember: '#f5aa72', teal: '#8de4dc', blue: '#70bccc',
  green: '#c2e0ae', shadow: '#081821',
};
const TAU = Math.PI * 2;
const clamp = (x, lo = 0, hi = 1) => Math.max(lo, Math.min(hi, x));
const smooth = (x) => { const v = clamp(x); return v * v * (3 - 2 * v); };
const lerp = (a, b, t) => a + (b - a) * t;
const hash = (n) => {
  const v = Math.sin(n * 127.1 + 78.233) * 43758.5453123;
  return v - Math.floor(v);
};

function rect(g, x, y, w, h, fill, alpha = 1) {
  g.save(); g.globalAlpha *= alpha; g.fillStyle = fill; g.fillRect(x, y, w, h); g.restore();
}
function line(g, points, color, width = 1, alpha = 1, dash = []) {
  if (points.length < 2) return;
  g.save();
  g.globalAlpha *= alpha;
  g.strokeStyle = color;
  g.lineWidth = width;
  g.lineCap = 'round';
  g.lineJoin = 'round';
  g.setLineDash(dash);
  g.beginPath();
  g.moveTo(points[0][0], points[0][1]);
  for (let i = 1; i < points.length; i++) g.lineTo(points[i][0], points[i][1]);
  g.stroke();
  g.restore();
}
function dot(g, x, y, r, color, alpha = 1, blur = 0) {
  if (r <= 0) return;
  g.save();
  g.globalAlpha *= alpha;
  g.fillStyle = color;
  if (blur) { g.shadowColor = color; g.shadowBlur = blur; }
  g.beginPath(); g.arc(x, y, r, 0, TAU); g.fill();
  g.restore();
}
function glow(g, x, y, r, color, alpha = .25) {
  const grad = g.createRadialGradient(x, y, 0, x, y, r);
  grad.addColorStop(0, color);
  grad.addColorStop(1, 'rgba(0,0,0,0)');
  g.save();
  g.globalAlpha *= alpha;
  g.fillStyle = grad;
  g.beginPath(); g.arc(x, y, r, 0, TAU); g.fill();
  g.restore();
}
function label(g, value, x, y, size, color = C.ink, align = 'center', alpha = 1) {
  g.save();
  g.globalAlpha *= alpha;
  g.fillStyle = color;
  g.font = '700 ' + Math.max(9, size) + 'px ui-sans-serif, system-ui, sans-serif';
  g.textAlign = align;
  g.textBaseline = 'middle';
  g.shadowColor = 'rgba(0,0,0,.75)';
  g.shadowBlur = 7;
  g.fillText(value, x, y);
  g.restore();
}
function polygon(g, points, color, alpha = 1) {
  if (points.length < 3) return;
  g.save();
  g.globalAlpha *= alpha;
  g.beginPath();
  g.moveTo(points[0][0], points[0][1]);
  for (let i = 1; i < points.length; i++) g.lineTo(points[i][0], points[i][1]);
  g.closePath();
  g.fillStyle = color;
  g.fill();
  g.restore();
}
function bezier(g, start, c1, c2, end, color, width, alpha) {
  g.save();
  g.globalAlpha *= alpha;
  g.strokeStyle = color;
  g.lineWidth = width;
  g.lineCap = 'round';
  g.shadowColor = color;
  g.shadowBlur = width * 5;
  g.beginPath();
  g.moveTo(start[0], start[1]);
  g.bezierCurveTo(c1[0], c1[1], c2[0], c2[1], end[0], end[1]);
  g.stroke();
  g.restore();
}
function bezierPoint(a, b, c, d, t) {
  const u = 1 - t;
  return [
    u*u*u*a[0] + 3*u*u*t*b[0] + 3*u*t*t*c[0] + t*t*t*d[0],
    u*u*u*a[1] + 3*u*u*t*b[1] + 3*u*t*t*c[1] + t*t*t*d[1],
  ];
}

function shot(g, key, x, y, w, h, zoom, focusX, focusY, shiftX = 0, shiftY = 0, alpha = 1) {
  const record = assets[key];
  g.save();
  g.globalAlpha *= alpha;
  g.beginPath(); g.rect(x, y, w, h); g.clip();
  if (record.ready && record.image.naturalWidth) {
    const image = record.image;
    const dw = image.naturalWidth * Math.max(w / image.naturalWidth, h / image.naturalHeight) * zoom;
    const dh = image.naturalHeight * Math.max(w / image.naturalWidth, h / image.naturalHeight) * zoom;
    let dx = x + w * .5 - focusX * dw + shiftX * w;
    let dy = y + h * .5 - focusY * dh + shiftY * h;
    dx = clamp(dx, x + w - dw, x);
    dy = clamp(dy, y + h - dh, y);
    g.drawImage(image, dx, dy, dw, dh);
  } else {
    const sky = g.createLinearGradient(x, y, x, y + h);
    sky.addColorStop(0, '#304255');
    sky.addColorStop(.43, '#a65d47');
    sky.addColorStop(1, '#0a1d25');
    g.fillStyle = sky;
    g.fillRect(x, y, w, h);
    const yy = y + h * .56;
    polygon(g, [[x, yy], [x+w*.18, yy-h*.2], [x+w*.34, yy], [x+w*.54, yy-h*.29], [x+w*.74, yy], [x+w, yy-h*.12], [x+w, y+h]], '#101f2b', .7);
    glow(g, x+w*.5, y+h*.48, h*.28, C.ember, .36);
  }
  g.restore();
}

function filmGrade(g, w, h, warm = .2, cool = .1) {
  const wash = g.createLinearGradient(0, 0, w, h);
  wash.addColorStop(0, 'rgba(24,43,59,' + cool + ')');
  wash.addColorStop(.55, 'rgba(6,19,28,0)');
  wash.addColorStop(1, 'rgba(91,43,24,' + warm + ')');
  rect(g, 0, 0, w, h, wash);
  const vignette = g.createRadialGradient(w*.49, h*.43, h*.2, w*.49, h*.43, Math.max(w,h)*.72);
  vignette.addColorStop(0, 'rgba(0,0,0,0)');
  vignette.addColorStop(1, 'rgba(3,10,15,.64)');
  rect(g, 0, 0, w, h, vignette);
}
function motes(g, w, h, t, still, count = 50) {
  const s = Math.min(w,h);
  for (let i = 0; i < count; i++) {
    const x = ((hash(i*4+1) + (still ? 0 : t * (.002 + .001*hash(i+420)))) % 1) * w;
    const y = ((hash(i*4+2) - (still ? 0 : t * (.0007 + .0005*hash(i+270))) + 100) % 1) * h;
    dot(g, x, y, Math.max(.5, s*(.0008+.0013*hash(i+710))), i%4 ? C.gold : C.teal, .12+.23*hash(i+240));
  }
}
function rain(g, w, h, t, still, alpha = .25) {
  const s = Math.min(w,h);
  for (let i = 0; i < 54; i++) {
    const x = hash(i*7+81) * w;
    const y = ((hash(i*7+25) + (still ? 0 : t*.018*(.8+hash(i)))) % 1) * h;
    line(g, [[x,y],[x-s*.009,y+s*.03]], C.ink, Math.max(.55,s*.0011), alpha*(.35+.65*hash(i+77)));
  }
}
function memoryThreads(g, w, h, p, t, still, color = C.gold, weight = 1) {
  const s = Math.min(w,h);
  for (let i = 0; i < 5; i++) {
    const y0 = h*(.24+i*.11);
    const a = [w*.91, y0];
    const b = [w*.76, y0 - h*.13];
    const c = [w*.58, y0 + h*.17];
    const d = [w*.32, h*(.31+i*.075)];
    bezier(g,a,b,c,d,color,Math.max(1,s*.0015)*weight,.08+.18*p);
    const pulse = (still ? .68 : (p*1.3+i*.18+t*.012)%1);
    const q = bezierPoint(a,b,c,d,pulse);
    dot(g,q[0],q[1],Math.max(1.6,s*.003),color,.35+.3*p,s*.016);
  }
}
function crossingThread(g,w,h,p,t,still) {
  const s = Math.min(w,h);
  const a = [w*.13,h*.52], b = [w*.36,h*.33], c = [w*.64,h*.63], d = [w*.88,h*.43];
  bezier(g,a,b,c,d,C.gold,Math.max(2,s*.003),.47);
  bezier(g,a,[w*.35,h*.48],[w*.62,h*.28],d,C.teal,Math.max(1,s*.0016),.26);
  const q = bezierPoint(a,b,c,d,still ? .64 : smooth(p));
  dot(g,q[0],q[1],Math.max(2,s*.006),C.gold,.9,s*.035);
}

function scene1(g,w,h,p,t,still,px,py) {
  shot(g,'observer',0,0,w,h,1.05+p*.1,lerp(.72,.48,smooth(p)),.48,px*.015,py*.01);
  filmGrade(g,w,h,.13,.18);
  rain(g,w,h,t,still,.28);
  glow(g,w*.37,h*.51,Math.min(w,h)*.22,C.ember,.11+.08*p);
  const s = Math.min(w,h);
  line(g,[[w*.34,h*.51],[w*.39,h*.51]],C.gold,Math.max(1,s*.0016),.36);
  line(g,[[w*.365,h*.485],[w*.365,h*.535]],C.gold,Math.max(1,s*.0016),.36);
  motes(g,w,h,t,still,32);
}
function scene2(g,w,h,p,t,still,px,py) {
  shot(g,'inheritance',0,0,w,h,1.08+p*.08,lerp(.69,.77,p),.48,px*.012,py*.008);
  filmGrade(g,w,h,.19,.07);
  memoryThreads(g,w,h,.5+.5*p,t,still,C.gold,1.12);
  for (let i=0;i<3;i++) {
    const x=w*(.17+i*.085), y=h*(.65+i*.055);
    glow(g,x,y,Math.min(w,h)*.065,C.gold,.12);
    dot(g,x,y,Math.max(1.5,Math.min(w,h)*.004),C.gold,.65,8);
  }
  motes(g,w,h,t,still,58);
}
function scene3(g,w,h,p,t,still,px,py) {
  shot(g,'observer',0,0,w,h,1.23+p*.07,lerp(.37,.43,p),lerp(.57,.61,p),px*.01,py*.009);
  filmGrade(g,w,h,.23,.13);
  const s=Math.min(w,h);
  const waterY=h*(.65+.04*p);
  const shade=g.createLinearGradient(0,waterY-h*.12,0,waterY+h*.1);
  shade.addColorStop(0,'rgba(7,20,27,0)');
  shade.addColorStop(1,'rgba(7,20,27,.54)');
  rect(g,0,waterY-h*.12,w,h*.25,shade,.75);
  for(let i=0;i<12;i++) {
    const x=w*(.11+.064*i), y=waterY+s*.014*Math.sin(i*.8+t*.35);
    line(g,[[x,y],[x+s*.025,y]],C.gold,Math.max(.8,s*.0015),.13+.12*(1-p));
  }
  rain(g,w,h,t,still,.13);
  motes(g,w,h,t,still,34);
}
function scene4(g,w,h,p,t,still,px,py) {
  shot(g,'gate',0,0,w,h,1.14-p*.045,.5,.49,px*.009,py*.007);
  const arrival=smooth((p-.39)/.36);
  shot(g,'ridge',0,0,w,h,1.13,lerp(.5,.69,p),.47,px*.011,py*.008,arrival);
  filmGrade(g,w,h,.14,.15);
  crossingThread(g,w,h,p,t,still);
  motes(g,w,h,t,still,50);
}
function scene5(g,w,h,p,t,still,px,py) {
  shot(g,'ridge',0,0,w,h,1.06+p*.12,lerp(.72,.49,smooth(p)),lerp(.47,.51,p),px*.012,py*.009);
  filmGrade(g,w,h,.08,.23);
  const s=Math.min(w,h);
  const crest=[];
  for(let i=0;i<=35;i++) {
    const x=w*(.08+.84*i/35);
    const y=h*(.66-.055*Math.sin(i*.25+p*2)) - s*.013*Math.sin(i*.6);
    crest.push([x,y]);
  }
  line(g,crest,C.teal,Math.max(1.3,s*.0025),.25);
  for(let i=0;i<6;i++) {
    const x=w*(.25+i*.1),y=h*(.45+.03*Math.sin(i+t*.28));
    glow(g,x,y,s*.06,C.teal,.06);
  }
  rain(g,w,h,t,still,.18);
  motes(g,w,h,t,still,38);
}
function scene6(g,w,h,p,t,still,px,py) {
  const half=w*.5;
  shot(g,'observer',0,0,half,h,1.18,.56,.5,px*.008,py*.005);
  shot(g,'ridge',half,0,half,h,1.18,.69,.47,px*.008,py*.005);
  rect(g,0,0,half,h,'rgba(88,47,22,.17)');
  rect(g,half,0,half,h,'rgba(23,78,94,.17)');
  const blend=smooth((p-.27)/.45);
  shot(g,'gate',w*.42,h*.18,w*.16,h*.5,1.12,.5,.5,0,0,blend*.65);
  filmGrade(g,w,h,.12,.12);
  line(g,[[half,h*.09],[half,h*.75]],C.ink,Math.max(1.5,Math.min(w,h)*.002),.3);
  const s=Math.min(w,h);
  const labelSize=Math.min(w<650?10:14,s*.024);
  label(g,'OBSERVED · WATER FELL',w*.26,h*.23,labelSize,C.gold,'center',.9);
  label(g,'OBSERVED · CREST ROSE',w*.74,h*.23,labelSize,C.teal,'center',.9);
  label(g,'OBSERVED · GATE SHUT',w*.5,h*.37,labelSize,C.ink,'center',.55+.4*blend);
  line(g,[[w*.23,h*.31],[w*.43,h*.37]],C.gold,1.3,.45);
  line(g,[[w*.77,h*.31],[w*.57,h*.37]],C.teal,1.3,.45);
  label(g,'INFERRED · THEIR INTENT',w*.5,h*.62,labelSize,C.dim,'center',.42+.3*blend);
  motes(g,w,h,t,still,37);
}
function scene7(g,w,h,p,t,still,px,py) {
  const split=w*.5;
  shot(g,'observer',0,0,split,h,1.17,lerp(.67,.56,p),.48,px*.008,py*.005);
  shot(g,'ridge',split,0,split,h,1.17,lerp(.71,.6,p),.48,px*.008,py*.005);
  filmGrade(g,w,h,.13,.12);
  rect(g,0,0,w,h,'rgba(3,13,20,.28)');
  rect(g,split-w*.017,0,w*.034,h,'rgba(5,17,24,.68)');
  const s=Math.min(w,h);
  const openness=smooth((p-.09)/.56);
  const a=[w*.25,h*.56], b=[w*.75,h*.56];
  const leftCone=[a,[w*.13,h*.22],[w*.45,h*.23],[w*.58,h*.45]];
  const rightCone=[b,[w*.87,h*.22],[w*.55,h*.23],[w*.42,h*.45]];
  polygon(g,leftCone,C.gold,.17+.24*openness);
  polygon(g,rightCone,C.teal,.17+.24*openness);
  line(g,[...leftCone,a],C.gold,Math.max(1.7,s*.0035),.7*openness);
  line(g,[...rightCone,b],C.teal,Math.max(1.7,s*.0035),.7*openness);
  line(g,[a,[w*.46,h*.37]],C.gold,Math.max(1.5,s*.0026),.66*openness,[4,6]);
  line(g,[b,[w*.54,h*.37]],C.teal,Math.max(1.5,s*.0026),.66*openness,[4,6]);
  dot(g,a[0],a[1],Math.max(3,s*.008),C.gold,openness,s*.035);
  dot(g,b[0],b[1],Math.max(3,s*.008),C.teal,openness,s*.035);
  glow(g,w*.5,h*.4,s*.13,C.ink,.11*openness);
  label(g,'POSSIBLE',w*.25,h*.34,Math.min(14,s*.023),C.gold,'center',.9*openness);
  label(g,'POSSIBLE',w*.75,h*.34,Math.min(14,s*.023),C.teal,'center',.9*openness);
  motes(g,w,h,t,still,39);
}

function contour(g,w,h,cx,cy,rx,ry,color,alpha) {
  g.save();
  g.globalAlpha*=alpha;
  g.strokeStyle=color;
  g.lineWidth=Math.max(.8,Math.min(w,h)*.0012);
  g.beginPath();
  g.ellipse(cx,cy,rx,ry,.04,0,TAU);
  g.stroke();
  g.restore();
}
function aerialMap(g,w,h,p) {
  const s=Math.min(w,h);
  const sky=g.createLinearGradient(0,0,w,h);
  sky.addColorStop(0,'#0b1b25');
  sky.addColorStop(.57,'#132e34');
  sky.addColorStop(1,'#07161d');
  rect(g,0,0,w,h,sky);
  g.save();
  const zoom=lerp(2.15,.88,smooth(p));
  g.translate(w*.5,h*.44);
  g.scale(zoom,zoom);
  g.translate(-w*.5,-h*.44);
  for(let i=0;i<7;i++) {
    const r=s*(.14+i*.075);
    contour(g,w,h,w*.2,h*.44,r*.72,r*1.4,C.gold,.055+.009*i);
    contour(g,w,h,w*.8,h*.44,r*.72,r*1.4,C.teal,.055+.009*i);
  }
  const river=[];
  for(let i=0;i<=70;i++) {
    const y=h*(.06+.83*i/70);
    const x=w*(.5+.045*Math.sin(i*.115)+.019*Math.sin(i*.3));
    river.push([x,y]);
  }
  line(g,river,'#285a66',s*.092,.4);
  line(g,river,C.teal,s*.013,.37);
  line(g,[[w*.36,h*.48],[w*.64,h*.48]],C.gold,Math.max(2,s*.006),.72);
  dot(g,w*.5,h*.48,s*.009,C.ink,.85,s*.03);
  for(let side of [-1,1]) {
    for(let i=0;i<9;i++) {
      const x=w*(.5+side*(.15+.026*hash(i+side*9+35)));
      const y=h*(.19+i*.067);
      dot(g,x,y,s*(.002+.002*hash(i+17)),side<0?C.gold:C.teal,.2+.23*hash(i+49));
    }
  }
  g.restore();
}
function hatchUnknown(g,w,h,alpha) {
  const s=Math.min(w,h);
  const regions=[
    [[0,h*.12],[w*.18,h*.12],[w*.31,h*.42],[w*.11,h*.71],[0,h*.71]],
    [[w,h*.12],[w*.82,h*.12],[w*.69,h*.42],[w*.89,h*.71],[w,h*.71]],
  ];
  for(const poly of regions) {
    polygon(g,poly,'#020a0f',.72*alpha);
    line(g,[poly[1],poly[2],poly[3]],C.dim,Math.max(1.2,s*.002),.44*alpha);
  }
  for(let i=0;i<17;i++) {
    const y=h*(.16+i*.03);
    line(g,[[0,y],[w*.08,y+s*.014]],C.dim,1,.2*alpha);
    line(g,[[w,y],[w*.92,y+s*.014]],C.dim,1,.2*alpha);
  }
}
function scene8(g,w,h,p,t,still,px,py) {
  aerialMap(g,w,h,p);
  // The gate is pulled away from the viewer as the same valley becomes a map.
  // This is a change of vantage, not access to a perfect outside account.
  const retreat=smooth((p-.025)/.59);
  const photoW=lerp(w,w*.54,retreat), photoH=lerp(h,h*.52,retreat);
  const photoX=(w-photoW)*.5, photoY=lerp(0,h*.055,retreat);
  const departure=1-smooth((p-.17)/.29);
  shot(g,'gate',photoX,photoY,photoW,photoH,lerp(1.22,1.02,retreat),.5,.47,px*.008,py*.006,departure);
  const s=Math.min(w,h);
  if(retreat>0) {
    const corners=[[photoX,photoY+photoH],[photoX+photoW,photoY+photoH]];
    line(g,[corners[0],[w*.23,h*.61]],C.gold,Math.max(1,s*.0017),.21*departure);
    line(g,[corners[1],[w*.77,h*.61]],C.teal,Math.max(1,s*.0017),.21*departure);
    for(let i=0;i<3;i++) {
      contour(g,w,h,w*.5,h*.44,s*(.18+i*.105+retreat*.13),s*(.1+i*.07+retreat*.09),C.ink,
        .15*(1-retreat));
    }
  }
  const reveal=smooth((p-.065)/.32);
  rect(g,0,0,w,h,'rgba(2,10,16,.33)',reveal);
  g.save();
  g.globalAlpha*=reveal;
  g.globalCompositeOperation='screen';
  const a=[w*.23,h*.61], b=[w*.77,h*.61];
  // Unequal inherited records produce unequal possibility fields.
  const leftCone=[a,[w*.09,h*.24],[w*.31,h*.17],[w*.56,h*.2],[w*.61,h*.38],[w*.49,h*.57]];
  const rightCone=[b,[w*.91,h*.25],[w*.74,h*.16],[w*.59,h*.2],[w*.37,h*.4],[w*.51,h*.57]];
  polygon(g,leftCone,C.gold,.43);
  polygon(g,rightCone,C.teal,.42);
  g.restore();
  line(g,[...leftCone,a],C.gold,Math.max(2.2,s*.0048),.91*reveal);
  line(g,[...rightCone,b],C.teal,Math.max(2.2,s*.0048),.91*reveal);
  const goldBranches=[
    [a,[w*.25,h*.42],[w*.31,h*.28]],
    [a,[w*.33,h*.45],[w*.46,h*.26]],
    [a,[w*.36,h*.5],[w*.5,h*.44]],
  ];
  const tealBranches=[
    [b,[w*.76,h*.4],[w*.78,h*.24]],
    [b,[w*.67,h*.39],[w*.59,h*.27]],
    [b,[w*.62,h*.5],[w*.5,h*.44]],
  ];
  for(const branch of goldBranches) line(g,branch,C.gold,Math.max(1.2,s*.0022),.49*reveal);
  for(const branch of tealBranches) line(g,branch,C.teal,Math.max(1.2,s*.0022),.49*reveal);
  const overlap=[[w*.42,h*.31],[w*.58,h*.31],[w*.62,h*.45],[w*.5,h*.57],[w*.38,h*.45]];
  polygon(g,overlap,C.green,.41*reveal);
  line(g,[...overlap,overlap[0]],C.green,Math.max(2.5,s*.0054),.94*reveal);
  glow(g,w*.5,h*.41,s*.19,C.green,.42*reveal);
  hatchUnknown(g,w,h,reveal);
  for(const [x,color] of [[w*.23,C.gold],[w*.77,C.teal]]) {
    dot(g,x,h*.61,Math.max(4,s*.012),color,reveal,s*.055);
    contour(g,w,h,x,h*.61,s*.031,s*.031,color,.9*reveal);
  }
  const pulse=still?.7:smooth((p-.31)/.58);
  for(const [x,color] of [[w*.23,C.gold],[w*.77,C.teal]]) {
    const qx=lerp(x,w*.5,pulse),qy=lerp(h*.61,h*.44,pulse);
    line(g,[[x,h*.61],[qx,qy]],color,Math.max(1.8,s*.0035),.76*reveal);
    dot(g,qx,qy,Math.max(2.3,s*.006),color,reveal,s*.035);
  }
  const fs=Math.min(w<650?10:14,s*.022);
  label(g,'OBSERVED · GATE SHUT',w*.5,h*.18,fs,C.ink,'center',.66*reveal);
  label(g,'INFERRED FUTURES',w*.5,h*.265,fs,C.dim,'center',.7*reveal);
  label(g,'CHECKED FACT',w*.5,h*.345,fs,C.green,'center',.94*reveal);
  label(g,'JOINT ACTION',w*.5,h*.425,Math.min(w<650?12:17,s*.027),C.ink,'center',reveal);
  const compact=w<650;
  const originSize=compact?10:Math.min(12,s*.019);
  label(g,compact?'ESTUARY · LOSS':'ESTUARY · INHERITED LOSS',w*.23,h*.535,originSize,C.gold,'center',.95*reveal);
  label(g,compact?'RIDGE · DANGER':'RIDGE · INHERITED DANGER',w*.77,h*.535,originSize,C.teal,'center',.95*reveal);
  label(g,'UNRESOLVED',w*.14,h*.44,fs,C.dim,'center',.85*reveal);
  motes(g,w,h,t,still,41);
}

const drawers=[scene1,scene2,scene3,scene4,scene5,scene6,scene7,scene8];
function currentScene(seconds) {
  const t=clamp(Number.isFinite(seconds)?seconds:0,0,FILM_DURATION);
  const index=Math.max(0,FILM_SCENES.findIndex((scene,i)=>t>=scene.start&&(t<scene.end||i===FILM_SCENES.length-1)));
  const scene=FILM_SCENES[index];
  return {t,index,scene,progress:clamp((t-scene.start)/(scene.end-scene.start))};
}

export function drawFilmFrame(canvas,seconds,{reducedMotion=false,pointerX=0,pointerY=0}={}) {
  if(!canvas||typeof canvas.getContext!=='function') throw new TypeError('drawFilmFrame requires a canvas');
  lastDraw={canvas,seconds,options:{reducedMotion,pointerX,pointerY}};
  const box=typeof canvas.getBoundingClientRect==='function'?canvas.getBoundingClientRect():null;
  const w=Math.max(1,Math.round((box&&box.width)||canvas.clientWidth||canvas.width||960));
  const h=Math.max(1,Math.round((box&&box.height)||canvas.clientHeight||canvas.height||540));
  const dpr=Math.min(2,Math.max(1,typeof window==='undefined'?1:window.devicePixelRatio||1));
  if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)) {
    canvas.width=Math.round(w*dpr);
    canvas.height=Math.round(h*dpr);
  }
  const g=canvas.getContext('2d',{alpha:false});
  if(!g) throw new Error('A Canvas 2D context is required');
  g.setTransform(dpr,0,0,dpr,0,0);
  rect(g,0,0,w,h,C.dark);
  const frame=currentScene(seconds);
  const t=reducedMotion?0:frame.t;
  const render=(index,progress,alpha)=>{
    g.save();g.globalAlpha*=alpha;
    drawers[index](g,w,h,progress,t,reducedMotion,reducedMotion?0:clamp(pointerX,-1,1),reducedMotion?0:clamp(pointerY,-1,1));
    g.restore();
  };
  if(reducedMotion) render(frame.index,.68,1);
  else if(frame.index>0&&frame.t-frame.scene.start<1.5) {
    const blend=smooth((frame.t-frame.scene.start)/1.5);
    render(frame.index-1,1,1-blend);
    render(frame.index,frame.progress,blend);
  } else render(frame.index,frame.progress,1);
  return frame;
}
