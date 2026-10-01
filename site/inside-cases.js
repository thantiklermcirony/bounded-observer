import { REAL_CASES } from './inside-cases-data.mjs?v=cases1';

const $ = (id) => document.getElementById(id);
const canvas = $('cases-canvas');
const ctx = canvas.getContext('2d');
const caseList = $('case-list');
const phaseButtons = [...document.querySelectorAll('[data-case-phase]')];
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const phaseNames = ['THE SCENE', 'FIRST VIEW', 'SECOND VIEW', 'PULL BACK'];
const nextLabels = ['Enter the first view →', 'Cross to the second view →', 'Pull back to the record →', 'Enter the next scene →'];
const evidenceLabels = {
  submarine: ['SIGNAL TO SURFACE', 'NUCLEAR TORPEDO UNKNOWN ABOVE'],
  trawlers: ['ROUTINE TRAWLING SIGNAL', 'NO HOSTILE TRAWLER ACTION'],
  radar: ['2 AUGUST ATTACK REAL', 'NO 4 AUGUST ATTACK'],
  runway: ['PAN AM STILL ON RUNWAY', 'NO KLM TAKEOFF CLEARANCE'],
  pump: ['CASES CLUSTER AT PUMP', 'WATER LINKS DISTANT CASES'],
  radio: ['SCRIPTED RADIO DRAMA', 'LATER PANIC STORY INFLATED'],
  grid: ['OHIO LINE FAILURES', 'ONE CROSS-BORDER CASCADE'],
  film: ['THE CLIP STOPPED EARLY', 'THE FULL SPEECH CONTINUED'],
  dress: ['SAME PHOTOGRAPH', 'BLUE / BLACK GARMENT'],
  alert: ['CONTRADICTORY DRILL SCRIPT', 'NO INCOMING MISSILE'],
};
let caseIndex = 0;
let phase = 0;
let lastChange = performance.now();
let visible = false;
let raf = 0;

function node(tag, className, value) {
  const result = document.createElement(tag);
  if (className) result.className = className;
  if (value !== undefined) result.textContent = value;
  return result;
}

function field(label, value) {
  const result = node('div', 'cases-field');
  result.append(node('b', '', label), node('p', '', value));
  return result;
}

function renderCopy(item) {
  const box = $('case-copy');
  box.replaceChildren();
  if (phase === 0) {
    box.append(node('span', 'cases-view-label', 'Before the interpretation'),
      node('h4', '', 'One event. An incomplete signal.'),
      node('p', '', item.scene),
      field('What to watch', 'Notice what the people in this scene can directly see, and what remains outside their view.'));
  } else if (phase === 1 || phase === 2) {
    const side = phase === 1 ? item.sideA : item.sideB;
    box.append(node('span', 'cases-view-label ' + (phase === 1 ? 'warm' : ''), phase === 1 ? 'From this position' : 'Across the scene'),
      node('h4', '', side.name),
      field('What reached them', side.observed),
      field('What they concluded', side.inferred));
  } else {
    box.append(node('span', 'cases-view-label', 'The later evidence'),
      node('h4', '', 'Now hold both accounts in view.'),
      node('p', '', item.finding));
    if (item.spread) box.append(field('Where the story ran ahead', item.spread));
    box.append(node('p', 'cases-boundary', item.boundary));
    const sources = node('div', 'cases-sources');
    item.sources.forEach((source) => {
      const link = node('a', '', source.label + ' ↗');
      link.href = source.url;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      sources.append(link);
    });
    box.append(sources);
  }
}

function render() {
  const item = REAL_CASES[caseIndex];
  $('case-count').textContent = String(caseIndex + 1).padStart(2, '0') + ' / ' + REAL_CASES.length + ' · REAL CASE';
  $('case-phase-count').textContent = '0' + (phase + 1) + ' / 04';
  $('case-title').textContent = item.title;
  $('case-stage-number').textContent = String(caseIndex + 1).padStart(2, '0') + ' / ' + REAL_CASES.length;
  $('case-stage-place').textContent = item.place.toUpperCase() + ' · ' + item.year;
  $('case-stage-lens').textContent = phaseNames[phase];
  $('case-stage-instruction').textContent = phase === 3 ? 'MORE EVIDENCE / STILL A BOUNDED VIEW' : 'ONE EVENT / MORE THAN ONE VIEW';
  $('case-evidence').hidden = phase !== 3;
  $('case-evidence-a').textContent = evidenceLabels[item.motif][0];
  $('case-evidence-b').textContent = evidenceLabels[item.motif][1];
  $('case-back').disabled = phase === 0;
  $('case-forward').textContent = nextLabels[phase];
  phaseButtons.forEach((button, index) => {
    if (index === phase) button.setAttribute('aria-current', 'step');
    else button.removeAttribute('aria-current');
  });
  [...caseList.children].forEach((button, index) => button.setAttribute('aria-pressed', String(index === caseIndex)));
  renderCopy(item);
  lastChange = performance.now();
  draw(lastChange);
}

function setPhase(value) {
  phase = Math.max(0, Math.min(3, value));
  render();
  document.querySelector('.cases-shell').scrollIntoView({ behavior: 'instant', block: 'start' });
}

function setCase(value, scroll = false) {
  caseIndex = (value + REAL_CASES.length) % REAL_CASES.length;
  phase = 0;
  render();
  $('case-title').focus({ preventScroll: true });
  if (scroll) document.querySelector('.cases-shell').scrollIntoView({ behavior: 'instant', block: 'start' });
}

REAL_CASES.forEach((item, index) => {
  const button = node('button');
  button.type = 'button';
  const meta = node('span', 'cases-index');
  meta.append(node('span', '', String(index + 1).padStart(2, '0')), node('span', '', item.year));
  button.append(meta, node('strong', '', item.title));
  button.addEventListener('click', () => setCase(index, true));
  caseList.append(button);
});
phaseButtons.forEach((button) => button.addEventListener('click', () => setPhase(Number(button.dataset.casePhase))));
$('case-back').addEventListener('click', () => setPhase(phase - 1));
$('case-forward').addEventListener('click', () => phase === 3 ? setCase(caseIndex + 1) : setPhase(phase + 1));

function line(x1, y1, x2, y2, stroke, width = 1) {
  ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2);
  ctx.strokeStyle = stroke; ctx.lineWidth = width; ctx.stroke();
}
function circle(x, y, r, fill, stroke, width = 1) {
  ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2);
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = width; ctx.stroke(); }
}
function polygon(points, fill, stroke, width = 1) {
  ctx.beginPath(); ctx.moveTo(...points[0]);
  for (let index = 1; index < points.length; index++) ctx.lineTo(...points[index]);
  ctx.closePath();
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = width; ctx.stroke(); }
}
function glow(x, y, r, color) {
  const gradient = ctx.createRadialGradient(x, y, 0, x, y, r);
  gradient.addColorStop(0, color); gradient.addColorStop(1, 'transparent');
  ctx.fillStyle = gradient; ctx.fillRect(x - r, y - r, r * 2, r * 2);
}
function arc(x, y, r, start, end, stroke, width = 1) {
  ctx.beginPath(); ctx.arc(x, y, r, start, end);
  ctx.strokeStyle = stroke; ctx.lineWidth = width; ctx.stroke();
}
function textAt(text, x, y, size = 18, color = '#a7c2c4', align = 'left') {
  ctx.fillStyle = color; ctx.font = `700 ${size}px ui-monospace, Consolas, monospace`;
  ctx.textAlign = align; ctx.fillText(text, x, y); ctx.textAlign = 'left';
}
function sky(time) {
  const skyFill = ctx.createLinearGradient(0, 0, 0, 1000);
  skyFill.addColorStop(0, '#071319'); skyFill.addColorStop(.5, '#17343b'); skyFill.addColorStop(1, '#061116');
  ctx.fillStyle = skyFill; ctx.fillRect(0, 0, 1600, 1000);
  const drift = reducedMotion.matches ? 0 : Math.sin(time / 5400) * 12;
  glow(1150 + drift, 260, 440, 'rgba(51,120,120,.23)');
  glow(330 - drift, 730, 420, 'rgba(204,115,65,.12)');
  for (let x = 0; x <= 1600; x += 80) line(x, 0, x, 1000, 'rgba(166,211,207,.035)');
  for (let y = 0; y <= 1000; y += 80) line(0, y, 1600, y, 'rgba(166,211,207,.035)');
  for (let i = 0; i < 80; i++) {
    const x = (i * 337 + 173) % 1600, y = (i * 193 + 71) % 1000;
    circle(x, y, i % 7 === 0 ? 1.6 : .8, 'rgba(228,235,217,.22)');
  }
}

function boat(x, y, size, color, light) {
  polygon([[x-size,y],[x+size,y],[x+size*.68,y+size*.3],[x-size*.58,y+size*.3]],color);
  line(x,y,x,y-size*.8,color,6);
  polygon([[x,y-size*.78],[x+size*.6,y-size*.05],[x,y-size*.05]],'rgba(164,199,189,.13)');
  glow(x-size*.5,y,32,light); circle(x-size*.5,y,4,light);
}
function water(y, time, color = 'rgba(103,161,167,.28)') {
  for (let j=0; j<12; j++) {
    const yy = y + j*42;
    ctx.beginPath();
    for (let x=-20; x<=1620; x+=20) {
      const wave = Math.sin(x/80 + j*.7 + (reducedMotion.matches ? 0 : time/2600)) * (3+j*.5);
      if (x === -20) ctx.moveTo(x, yy+wave); else ctx.lineTo(x, yy+wave);
    }
    ctx.strokeStyle = color; ctx.lineWidth = j%3===0 ? 2 : 1; ctx.stroke();
  }
}
function drawSubmarine(time) {
  water(335,time,'rgba(157,205,197,.23)');
  glow(1020,365,190,'rgba(238,183,128,.2)');
  boat(1140,333,125,'#142b2f','#e9ad7b');
  polygon([[350,685],[430,649],[685,649],[760,684],[686,715],[425,715]],'#07161b','#6ea4a5',2);
  ctx.fillStyle='#07161b'; ctx.fillRect(520,624,105,35);
  line(570,624,570,598,'#6ea4a5',5);
  for (let i=0;i<3;i++) {
    const x=930+i*80, yy=395+i*50;
    line(x,340,x,yy,'rgba(242,184,116,.6)',2);
    const pulse=reducedMotion.matches?0:(time/17+i*50)%160;
    arc(x,yy,30+pulse,0,Math.PI*2,'rgba(243,184,118,.32)',2);
    glow(x,yy,40,'rgba(249,176,91,.32)');
  }
  textAt('SURFACE',1000,282,14,'#baaa8d'); textAt('BELOW',550,770,14,'#82babc');
}
function drawTrawlers(time) {
  water(565,time);
  glow(1050,330,290,'rgba(95,148,140,.12)');
  boat(960,558,88,'#0a1a1d','#9ecbc1'); boat(1210,580,74,'#0c1c20','#a4c9be');
  boat(300,560,165,'#09191d','#e4b17e');
  line(1060,543,1120,270,'rgba(138,221,156,.6)',3);
  glow(1120,260,90,'rgba(133,239,148,.23)'); circle(1120,260,8,'#b5efac');
  for(let i=0;i<6;i++) line(150+i*18,525,520+i*5,505-i*10,'rgba(233,166,110,.13)',2);
  textAt('ONE SIGNAL',1090,173,16,'#a6d6b1');
}
function drawRadar(time) {
  const x=790,y=530;
  glow(x,y,420,'rgba(44,117,129,.24)');
  for(let r=120;r<=440;r+=80) circle(x,y,r,null,'rgba(121,195,193,.22)',2);
  for(let a=0;a<Math.PI*2;a+=Math.PI/4) line(x,y,x+460*Math.cos(a),y+460*Math.sin(a),'rgba(123,190,188,.12)');
  const angle=reducedMotion.matches?-.5:time/2500;
  polygon([[x,y],[x+470*Math.cos(angle-.21),y+470*Math.sin(angle-.21)],[x+470*Math.cos(angle),y+470*Math.sin(angle)]],'rgba(113,216,192,.10)');
  [[540,420],[1060,635],[870,260]].forEach(([bx,by],i)=>{glow(bx,by,45,i===1?'rgba(234,164,102,.3)':'rgba(108,206,192,.25)');circle(bx,by,8,i===1?'#edaa75':'#9dd7cc');});
  textAt('RADAR CONTACT',95,190,15,'#9bc9c8');
}
function drawRunway(time) {
  const fog=ctx.createLinearGradient(0,100,0,900);fog.addColorStop(0,'rgba(201,218,203,.16)');fog.addColorStop(1,'rgba(201,218,203,0)');ctx.fillStyle=fog;ctx.fillRect(0,100,1600,800);
  polygon([[740,355],[860,355],[1380,1000],[220,1000]],'rgba(7,15,19,.76)','#597174',3);
  for(let i=0;i<8;i++) {let y=390+i*i*8;let w=(y-320)*.08;line(800-w,y,800+w,y,'rgba(240,232,209,.22)',Math.max(1,i*.6));}
  for(let i=0;i<11;i++){let y=390+i*i*6;let spread=(y-300)*.74;circle(800-spread,y,3+i*.4,'#d6b98f');circle(800+spread,y,3+i*.4,'#d6b98f');}
  polygon([[645,755],[740,730],[855,730],[945,755],[855,778],[740,778]],'#061519','#9bb9b8',2);
  polygon([[765,487],[800,468],[835,487],[820,505],[780,505]],'#0a1b20','#a7c1be',2);
  glow(800,480,125,'rgba(220,212,172,.15)');textAt('LOW VISIBILITY',90,175,15,'#c6d5ce');
}
function drawPump() {
  for(let y=280;y<900;y+=70) for(let x=100;x<1500;x+=85) circle(x+((y/70)%2)*28,y,2,'rgba(160,194,173,.18)');
  for(let i=0;i<75;i++){const x=280+(i*157)%1000,y=310+(i*283)%500;circle(x,y,2+i%3,'rgba(198,96,76,.28)');}
  circle(800,580,245,'rgba(43,99,104,.12)','rgba(144,208,204,.34)',3);
  ctx.fillStyle='#081c21';ctx.fillRect(755,380,90,280);ctx.fillRect(710,645,180,28);
  arc(800,380,48,Math.PI,Math.PI*2,'#b4c9b6',9);
  line(800,380,915,320,'#b4c9b6',10);circle(915,320,13,'#e2b885');
  for(let r=310;r<=460;r+=70) circle(800,580,r,null,'rgba(159,202,188,.1)',2);
  if(phase===3){for(let i=0;i<12;i++){const x=280+(i*157)%1000,y=310+(i*283)%500;line(800,580,x,y,'rgba(122,215,209,.2)',2);}}
  textAt('WATER / AIR?',101,175,16,'#a7c8c5');
}
function drawRadio(time) {
  const x=800,y=560;
  glow(x,y,370,'rgba(227,147,86,.14)');
  polygon([[500,355],[1100,355],[1130,770],[470,770]],'#142a2c','#af9074',5);
  for(let i=0;i<16;i++) line(560+i*32,420,560+i*32,570,'rgba(219,196,152,.25)',4);
  circle(660,665,55,'#091b21','#d8ab80',5);circle(955,665,55,'#091b21','#d8ab80',5);
  for(let i=0;i<4;i++){const r=160+i*95+(reducedMotion.matches?0:(time/25)%95);arc(x,530,r,-Math.PI*.7,-Math.PI*.3,'rgba(207,173,131,.17)',3);}
  textAt(phase===3?'SCRIPTED BROADCAST':'URGENT BULLETIN',800,252,15,'#d1b797','center');
}
function drawGrid(time) {
  for(let x=160;x<1550;x+=155){
    const h=170+((x*7)%270);
    ctx.fillStyle=x<790?'#13282d':'#0c1b21';ctx.fillRect(x,750-h,115,h);
    for(let xx=x+15;xx<x+105;xx+=28)for(let yy=760-h+20;yy<740;yy+=32){
      if((xx+yy)%5<3){ctx.fillStyle=x<790?'rgba(244,192,119,.52)':'rgba(155,180,172,.07)';ctx.fillRect(xx,yy,10,14);}
    }
  }
  for(let i=0;i<4;i++){const x=260+i*350;line(x,370,x-70,800,'rgba(131,177,176,.45)',4);line(x,370,x+70,800,'rgba(131,177,176,.45)',4);line(x-100,470,x+100,470,'rgba(131,177,176,.45)',4);if(i<3)line(x+100,470,x+250,490,'rgba(131,177,176,.2)',3);}
  glow(810,460,150,'rgba(244,172,94,.18)');textAt(phase===3?'ONE CONNECTED GRID':'POWER FAILURE',800,224,15,'#b6d4cb','center');
}
function drawFilm() {
  glow(800,490,330,'rgba(183,122,89,.16)');
  polygon([[480,190],[1120,190],[1120,815],[480,815]],'#0e262c','#8ab7b8',5);
  for(let y=245;y<800;y+=96){line(505,y,1095,y,'rgba(207,224,207,.15)',4);circle(510,y+45,12,'#a9c8b3');circle(1090,y+45,12,'#a9c8b3');}
  const frame=phase===3?[[525,285],[1070,285],[1070,735],[525,735]]:[[635,305],[960,305],[960,700],[635,700]];
  polygon(frame,'rgba(196,139,94,.11)','#e6ab7b',4);
  line(frame[0][0],frame[0][1]+22,frame[1][0],frame[1][1]+22,'#e6ab7b',3);
  line(frame[3][0],frame[3][1]-22,frame[2][0],frame[2][1]-22,'#e6ab7b',3);
  textAt(phase===3?'CROPPED RECORD':'RECORDED SPEECH',800,252,15,'#e6bd95','center');
}
function drawDress(time) {
  glow(800,470,360,'rgba(226,215,157,.21)');
  const sway=reducedMotion.matches?0:Math.sin(time/1700)*8;
  const seenWhiteGold=phase===2;
  polygon([[715,235],[885,235],[915,335],[863,395],[970+sway,795],[630+sway,795],[735,395],[685,335]],seenWhiteGold?'#dfd8b7':'#334c66',seenWhiteGold?'#fff7d8':'#b5becc',5);
  for(let i=0;i<5;i++){const y=360+i*81;polygon([[727-(i*15)+sway,y],[873+(i*15)+sway,y],[888+(i*19)+sway,y+27],[713-(i*19)+sway,y+27]],seenWhiteGold?'#bb9a5b':'#151e26');}
  line(785,235,785,195,'rgba(239,222,187,.7)',3);arc(800,188,15,Math.PI,2*Math.PI,'rgba(239,222,187,.7)',3);
  textAt('SAME PHOTOGRAPH',800,155,15,'#e4d9b7','center');
}
function drawAlert(time) {
  water(740,time,'rgba(99,155,157,.13)');
  polygon([[390,260],[1000,260],[1030,805],[360,805]],'#0d2228','#84a9a9',5);
  polygon([[420,330],[970,330],[970,700],[420,700]],'#193840');
  polygon([[640,395],[730,395],[750,560],[620,560]],'#e4ae7d');
  circle(685,620,28,'#e4ae7d');
  for(let i=0;i<3;i++)arc(1180,470,100+i*72,-2.4,-.5,'rgba(211,166,105,.27)',3);
  line(1180,470,1180,705,'#8fbabb',7);circle(1180,470,8,'#e4ae7d');
  textAt('ALERT',705,309,16,'#d8ad80','center');
}
const motifDraw = { submarine:drawSubmarine,trawlers:drawTrawlers,radar:drawRadar,runway:drawRunway,pump:drawPump,radio:drawRadio,grid:drawGrid,film:drawFilm,dress:drawDress,alert:drawAlert };

function occlude(motif, fade) {
  if (phase !== 1 && phase !== 2) return;
  if (motif === 'dress') {
    ctx.fillStyle=phase===1?'rgba(87,139,180,.09)':'rgba(237,201,130,.15)';
    ctx.fillRect(0,0,1600,1000);
    return;
  }
  const vertical=motif==='submarine';
  const g=vertical?ctx.createLinearGradient(0,0,0,1000):ctx.createLinearGradient(0,0,1600,0);
  if(vertical){
    if(phase===1){g.addColorStop(0,'rgba(1,9,13,0)');g.addColorStop(.42,'rgba(1,9,13,.08)');g.addColorStop(.58,'rgba(1,9,13,.77)');g.addColorStop(1,'rgba(1,9,13,.84)');}
    else{g.addColorStop(0,'rgba(1,9,13,.82)');g.addColorStop(.42,'rgba(1,9,13,.7)');g.addColorStop(.62,'rgba(1,9,13,.08)');g.addColorStop(1,'rgba(1,9,13,0)');}
  }else if(phase===1){g.addColorStop(0,'rgba(1,9,13,0)');g.addColorStop(.42,'rgba(1,9,13,.08)');g.addColorStop(.64,'rgba(1,9,13,.7)');g.addColorStop(1,'rgba(1,9,13,.82)');}
  else{g.addColorStop(0,'rgba(1,9,13,.82)');g.addColorStop(.36,'rgba(1,9,13,.7)');g.addColorStop(.58,'rgba(1,9,13,.08)');g.addColorStop(1,'rgba(1,9,13,0)');}
  ctx.globalAlpha=fade;ctx.fillStyle=g;ctx.fillRect(0,0,1600,1000);ctx.globalAlpha=1;
}

function lens(time, fade, motif) {
  if (phase === 0) return;
  const warm = 'rgba(239,165,105,' + (.1*fade) + ')';
  const cool = 'rgba(126,216,217,' + (.1*fade) + ')';
  const submarine=motif==='submarine';
  if (phase === 1 || phase === 3) {
    const x=submarine?1190:340,y=submarine?300:790;
    polygon(submarine?[[x,y],[690,440],[800,580],[920,460]]:[[340,790],[735,410],[1000,500],[720,590]],warm,'rgba(239,165,105,.48)',2);
    glow(x,y,150,'rgba(242,164,98,.17)'); circle(x,y,38,'#e2ae80','#fff1d9',2);
    line(x,y,800,510,'rgba(244,180,118,.33)',2);
  }
  if (phase === 2 || phase === 3) {
    const x=submarine?490:1260,y=submarine?710:790;
    polygon(submarine?[[x,y],[690,440],[810,560],[740,690]]:[[1260,790],[865,410],[600,500],[880,590]],cool,'rgba(126,216,217,.48)',2);
    glow(x,y,150,'rgba(103,201,207,.17)');circle(x,y,38,'#82c8ca','#e8ffff',2);
    line(x,y,800,510,'rgba(136,221,222,.33)',2);
  }
  if (phase === 3) {
    const pulse = reducedMotion.matches ? 0 : Math.sin(time/1200)*14;
    circle(800,510,152+pulse,null,'rgba(237,232,196,.33)',2);
    circle(800,510,224+pulse,null,'rgba(237,232,196,.17)',2);
    circle(800,510,10,'#fff2cd');
    for(let i=0;i<8;i++){const a=i*Math.PI/4;const x=800+330*Math.cos(a),y=510+250*Math.sin(a);line(800,510,x,y,'rgba(200,226,214,.12)',2);circle(x,y,5,'rgba(211,228,210,.55)');}
    textAt('RETROSPECTIVE RECORD',800,125,17,'#e9e6cd','center');
  }
}

function draw(time) {
  if (!ctx) return;
  const item=REAL_CASES[caseIndex];
  ctx.clearRect(0,0,1600,1000);
  sky(time);
  const zoom=phase===3?.79:phase===0?1:1.05;
  const xShift=phase===1?70:phase===2?-70:0;
  ctx.save();ctx.translate(800+xShift,500);ctx.scale(zoom,zoom);ctx.translate(-800,-500);
  motifDraw[item.motif]?.(time);
  ctx.restore();
  const fade=reducedMotion.matches?1:Math.min(1,(time-lastChange)/550);
  occlude(item.motif,fade);
  lens(time,fade,item.motif);
}

function loop(now) {
  raf=0;
  if (!visible || document.hidden || reducedMotion.matches) return;
  draw(now);
  raf=requestAnimationFrame(loop);
}
function wake() {
  if (raf) cancelAnimationFrame(raf);
  raf=0;
  draw(performance.now());
  if (visible && !document.hidden && !reducedMotion.matches) raf=requestAnimationFrame(loop);
}
new IntersectionObserver((entries)=>{visible=entries[0].isIntersecting;wake();},{threshold:.01}).observe(canvas);
document.addEventListener('visibilitychange',wake);
reducedMotion.addEventListener('change',wake);
render();
