import json
import base64
import io
from pathlib import Path
from PIL import Image

BASE = Path(__file__).parent.parent
PROTO = BASE / "proto"
PNG_DIR = BASE / "PNG Empresas"

with open(PROTO / "datos_mes_actual.json", encoding="utf-8") as f:
    data = json.load(f)
DATA_JSON = json.dumps(data, ensure_ascii=False)

def b64(path):
    return base64.b64encode(path.read_bytes()).decode("ascii")

def gemco_icon_b64(path):
    # Isotipos.png trae los 3 isotipos (GEMCO/INCARDIA/MMQ) lado a lado.
    # Para la marca de agua solo queremos el de GEMCO (el del extremo izquierdo).
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    icon = im.crop((0, 0, w // 3, h))
    bbox = icon.getbbox()
    if bbox:
        icon = icon.crop(bbox)
    buf = io.BytesIO()
    icon.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")

LOGO_B64 = b64(PNG_DIR / "Gemco-logo-blanco-v2.png")
ISOTIPO_B64 = b64(PNG_DIR / "Isotipos.png")
WATERMARK_B64 = gemco_icon_b64(PNG_DIR / "Isotipos.png")

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Lexend:wght@500;600;700&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
<title>GEMCO · Trazabilidad Equipos Demostración</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box;}
  :root{
    --bg:#f4f6fb; --card:#fff; --border:#e5e9f4; --text:#0f1a3c; --text-dim:#7c86a6;
    --header-bg-1:#0a1030; --header-bg-2:#1c2f6b;
    --demo:#2f6fed; --demo-soft:#e8f0fe;
    --prestamo:#22a06b; --prestamo-soft:#e1f7ec;
    --incompleto:#ef4360; --incompleto-soft:#fde7ec;
    --nota:#8892a6; --nota-soft:#eef1f5;
    --disp:#0ea5b7; --disp-soft:#e1f7f9;
    --shadow:0 4px 20px rgba(15,26,60,.07);
    --font-display:'Lexend','Segoe UI',Arial,sans-serif;
    --font-body:'Inter','Segoe UI',Arial,sans-serif;
    --font-mono:'JetBrains Mono','Consolas',monospace;
  }
  html,body{width:100vw;height:100vh;overflow:hidden;background:var(--bg);
    font-family:var(--font-body);color:var(--text);cursor:pointer;user-select:none;}
  .stage-root{width:100vw;height:100vh;display:flex;flex-direction:column;}

  .pause-indicator{
    position:fixed;top:18px;right:38px;z-index:50;display:none;align-items:center;gap:8px;
    background:rgba(10,16,48,.92);color:#fff;padding:8px 16px;border-radius:20px;
    font-size:13px;font-weight:600;box-shadow:0 4px 16px rgba(0,0,0,.25);
  }
  .pause-indicator.visible{display:flex;}

  header{
    flex:0 0 9vh;display:flex;align-items:center;justify-content:space-between;
    padding:0 2.4vw;position:relative;overflow:hidden;
    background:radial-gradient(circle at 10% -60%,rgba(66,110,240,.5),transparent 60%),
      linear-gradient(120deg,var(--header-bg-1),var(--header-bg-2));
  }
  .brand{display:flex;align-items:center;gap:16px;position:relative;}
  .brand img{height:3.4vh;width:auto;display:block;}
  .brand .subtitle{color:#aeb9e8;font-size:1.35vh;font-family:var(--font-body);
    border-left:1px solid rgba(255,255,255,.2);padding-left:16px;}
  .meta{text-align:right;color:#aeb9e8;font-size:1.15vh;font-family:var(--font-mono);
    text-transform:uppercase;letter-spacing:.06em;position:relative;}
  .meta strong{display:block;color:#fff;font-size:1.7vh;font-family:var(--font-display);
    text-transform:none;letter-spacing:.02em;margin-top:.3vh;}
  .meta .gen{display:block;color:#7f8bc0;font-size:1vh;margin-top:.35vh;letter-spacing:.04em;}

  main{flex:1 1 auto;padding:2vh 2.4vw 1.4vh;min-height:0;display:flex;flex-direction:column;}

  .kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:.9vw;margin-bottom:1.6vh;flex:0 0 auto;}
  .kpi-card{background:var(--card);border:1px solid var(--border);border-radius:12px;
    padding:1.1vh 1vw;box-shadow:var(--shadow);display:flex;align-items:center;gap:.7vw;}
  .kpi-card .icon{width:3.4vh;height:3.4vh;border-radius:9px;display:flex;align-items:center;
    justify-content:center;flex-shrink:0;}
  .kpi-card .icon svg{width:1.9vh;height:1.9vh;}
  .kpi-text{display:flex;flex-direction:column;gap:1px;min-width:0;}
  .kpi-label{font-size:1.05vh;color:var(--text-dim);font-weight:600;text-transform:uppercase;
    letter-spacing:.04em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  .kpi-value{font-family:var(--font-display);font-size:2.7vh;font-weight:600;line-height:1.1;}
  .kpi-sub{font-size:1.05vh;color:var(--text-dim);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}

  .slide-header{display:flex;align-items:baseline;gap:.9vw;margin-bottom:1.2vh;flex:0 0 auto;}
  .slide-header h2{font-family:var(--font-display);font-weight:600;font-size:2.5vh;
    letter-spacing:.01em;text-transform:uppercase;}
  .slide-header .badge{font-size:1.4vh;font-weight:700;color:#fff;padding:.4vh 1vw;
    border-radius:20px;font-family:var(--font-mono);}
  .slide-header .subtitle2{color:var(--text-dim);font-size:1.65vh;}

  .stage{position:relative;flex:1;min-height:0;}
  .slide{position:absolute;inset:0;opacity:0;transform:translateY(14px);
    transition:opacity .6s ease,transform .6s ease;pointer-events:none;}
  .slide.active{opacity:1;transform:translateY(0);pointer-events:auto;}

  .card-table{background:var(--card);border:1px solid var(--border);border-radius:14px;
    box-shadow:var(--shadow);overflow:hidden;height:100%;display:flex;flex-direction:column;
    position:relative;}
  .card-table::before{
    content:'';position:absolute;inset:0;z-index:0;pointer-events:none;
    background-image:url("data:image/png;base64,__WATERMARK_B64__");background-repeat:no-repeat;
    background-position:right -8vh bottom -10vh;background-size:60vh auto;
    filter:brightness(0);opacity:.08;
  }
  .table-head,.table-body{position:relative;z-index:1;}
  .table-columns{display:grid;grid-template-columns:6px 14% 18% 1fr 20%;column-gap:1.2vw;}
  .table-head{flex:0 0 auto;padding:0 1.3vw;border-bottom:2px solid var(--border);background:#fbfcfe;}
  .table-head>div{font-size:1.15vh;text-transform:uppercase;letter-spacing:.05em;
    color:var(--text-dim);font-weight:700;padding:1.15vh 0;}
  .table-body{flex:1 1 auto;display:grid;min-height:0;padding:0 1.3vw;}
  .table-row{border-bottom:1px solid var(--border);}
  .table-row:last-child{border-bottom:none;}
  .table-row>div{min-width:0;display:flex;height:100%;}
  .table-row .col-accent,.table-row .col-cat{align-items:center;}
  .accent-bar{width:6px;height:64%;border-radius:3px;}
  .cat-tag{display:inline-block;font-size:1.15vh;font-weight:600;padding:.4vh .85vw;
    border-radius:20px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%;}
  .col-equipo{flex-direction:column;justify-content:center;gap:.2vh;}
  .modelo{font-weight:700;font-size:2vh;line-height:1.15;}
  .serie{font-family:var(--font-mono);font-size:1.25vh;color:var(--text-dim);}
  .col-desc{align-items:center;}
  .desc{font-size:1.6vh;color:var(--text);line-height:1.35;display:-webkit-box;
    -webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
  .col-dias{align-items:center;flex-direction:column;justify-content:center;gap:.5vh;}
  .dias-num{font-family:var(--font-mono);font-weight:700;font-size:2.1vh;}
  .dias-pair{display:flex;align-items:center;gap:.9vw;}
  .dias-item{display:flex;flex-direction:column;align-items:center;gap:.15vh;line-height:1.1;}
  .dias-item .dias-label{font-size:.85vh;color:var(--text-dim);text-transform:uppercase;
    letter-spacing:.05em;font-weight:600;font-family:var(--font-body);}
  .dias-item .dias-val{font-family:var(--font-mono);font-weight:700;font-size:2.1vh;}
  .dias-divider{width:1px;height:2.4vh;background:var(--border);flex-shrink:0;}

  .lugar-header{display:flex;align-items:center;gap:.7vw;padding:1vh 0 .5vh;
    font-family:var(--font-display);font-weight:600;font-size:1.6vh;color:var(--text);
    text-transform:uppercase;letter-spacing:.03em;border-bottom:1px solid var(--border);}
  .lugar-header .lugar-dot{width:1vh;height:1vh;border-radius:50%;flex-shrink:0;}
  .lugar-header .lugar-count{font-family:var(--font-mono);font-weight:600;color:var(--text-dim);
    text-transform:none;letter-spacing:0;font-size:1.3vh;}

  .grid-stage{background:var(--card);border:1px solid var(--border);border-radius:14px;
    box-shadow:var(--shadow);height:100%;padding:1.8vh 1.6vw;display:grid;
    grid-template-columns:repeat(4,1fr);grid-auto-rows:1fr;align-content:stretch;gap:1.1vh 1vw;
    position:relative;}
  .grid-stage::before{
    content:'';position:absolute;inset:0;z-index:0;pointer-events:none;
    background-image:url("data:image/png;base64,__WATERMARK_B64__");background-repeat:no-repeat;
    background-position:right -8vh bottom -10vh;background-size:60vh auto;
    filter:brightness(0);opacity:.08;
  }
  .eq-chip{border-left:4px solid var(--disp);background:var(--disp-soft);border-radius:8px;
    padding:.9vh 1vw;min-width:0;display:flex;flex-direction:column;justify-content:center;gap:.25vh;
    position:relative;z-index:1;}
  .eq-chip .cat{font-size:1.1vh;font-weight:600;color:#0a7d8c;text-transform:uppercase;
    letter-spacing:.03em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  .eq-chip .modelo{font-size:1.65vh;font-weight:700;color:var(--text);white-space:nowrap;
    overflow:hidden;text-overflow:ellipsis;}
  .eq-chip .serie{font-size:1.25vh;color:var(--text-dim);font-family:var(--font-mono);
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}

  .isotipo-slide{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
    flex-direction:column;gap:2vh;opacity:0;pointer-events:none;transition:opacity .6s ease;
    background:var(--card);border:1px solid var(--border);border-radius:14px;box-shadow:var(--shadow);}
  .isotipo-slide.active{opacity:1;pointer-events:auto;}
  .isotipo-slide img{height:12vh;width:auto;animation:pulse-iso 2.5s ease-in-out infinite;}
  .isotipo-slide .tag{font-family:var(--font-display);font-size:1.7vh;color:var(--text-dim);
    letter-spacing:.03em;text-transform:uppercase;}
  @keyframes pulse-iso{0%,100%{transform:scale(1);opacity:1;}50%{transform:scale(1.05);opacity:.85;}}

  footer{flex:0 0 auto;display:flex;justify-content:center;gap:.5vw;padding-top:1.3vh;}
  .progress-dot{width:2.2vw;height:5px;border-radius:3px;background:var(--border);
    overflow:hidden;position:relative;}
  .progress-dot .fill{position:absolute;inset:0;background:#334;transform:scaleX(0);transform-origin:left;}
  .progress-dot.done .fill{transform:scaleX(1);transition:none;}
  .progress-dot.active .fill{transform:scaleX(0);animation:fillbar var(--dur,9s) linear forwards;}
  .progress-dot.paused .fill{animation-play-state:paused;}
  @keyframes fillbar{to{transform:scaleX(1);}}
</style>
</head>
<body>

<div class="pause-indicator" id="pause-indicator">⏸ Panel en pausa — clic o espacio para continuar</div>

<div class="stage-root">
  <header>
    <div class="brand">
      <img src="data:image/png;base64,__LOGO_B64__" alt="GEMCO">
      <span class="subtitle">Trazabilidad · Equipos Demostración</span>
    </div>
    <div class="meta" id="mes-meta">Mes actual<strong id="mes-label">—</strong><span class="gen" id="gen-label"></span></div>
  </header>

  <main>
    <div class="kpis" id="kpis"></div>

    <div class="slide-header" id="slide-header">
      <h2 id="slide-title">—</h2>
      <span class="badge" id="slide-badge">0</span>
      <span class="subtitle2" id="slide-subtitle"></span>
    </div>

    <div class="stage" id="stage">
      <div class="isotipo-slide" id="isotipo-slide">
        <img src="data:image/png;base64,__ISOTIPO_B64__" alt="GEMCO">
        <span class="tag">Trazabilidad de Equipos de Demostración</span>
      </div>
    </div>

    <footer id="progress"></footer>
  </main>
</div>

<script>
const DATA = __DATA_JSON__;

const ESTADOS = ["Demostración","Préstamo","Incompleto","Nota/Servicio","Disponible"];
const COLORS = {
  "Demostración": {c:"#2f6fed", soft:"#e8f0fe"},
  "Préstamo":     {c:"#22a06b", soft:"#e1f7ec"},
  "Incompleto":   {c:"#ef4360", soft:"#fde7ec"},
  "Nota/Servicio":{c:"#8892a6", soft:"#eef1f5"},
  "Disponible":   {c:"#0ea5b7", soft:"#e1f7f9"}
};
const KPI_SUB = {
  "Demostración": "en terreno",
  "Préstamo": "en préstamo",
  "Incompleto": "por completar",
  "Nota/Servicio": "con nota o en servicio",
  "Disponible": "listos para asignar"
};
const ICONS = {
  "Demostración": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/></svg>',
  "Préstamo": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7h13l-3-3M20 17H7l3 3"/></svg>',
  "Incompleto": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l10 18H2L12 3z"/><path d="M12 10v4M12 17h.01"/></svg>',
  "Nota/Servicio": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a4 4 0 1 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.8 2.8-2-2z"/></svg>',
  "Disponible": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/></svg>'
};

const TABLE_ROWS_PER_SLIDE = 8;
const GRID_ITEMS_PER_SLIDE = 32; // grid Disponible: 4 cols x 8 filas
const SEGUNDOS_POR_SLIDE = 9;
const SEGUNDOS_ISOTIPO = 5;

document.getElementById('mes-label').textContent = DATA.mes + ' ' + DATA.anio;
if (DATA.es_mes_actual === false) {
  document.getElementById('mes-meta').firstChild.textContent = '⚠ Últ. dato disponible';
}
if (DATA.generado_en) {
  document.getElementById('gen-label').textContent = 'Actualizado ' + DATA.generado_en;
}

// ---- Auto-refresco: la TV queda encendida semanas, así que la página se
// recarga sola para tomar el último deploy de GitHub Pages (el PC de Martin
// regenera y publica todos los días). El query param evita la caché.
const MINUTOS_RECARGA = 30;
const MESES_NUM = {"Enero":1,"Febrero":2,"Marzo":3,"Abril":4,"Mayo":5,"Junio":6,"Julio":7,
  "Agosto":8,"Septiembre":9,"Octubre":10,"Noviembre":11,"Diciembre":12};
const MES_RENDERIZADO = (DATA.anio || 0) * 100 + (MESES_NUM[DATA.mes] || 0);
function recargar(){ location.replace(location.pathname + '?t=' + Date.now()); }
setInterval(recargar, MINUTOS_RECARGA * 60 * 1000);
// Cambio de mes con el panel encendido: recarga apenas el reloj entra al mes
// siguiente al que se está mostrando, sin esperar el ciclo de 30 minutos.
setInterval(() => {
  const ahora = new Date();
  if (ahora.getFullYear() * 100 + (ahora.getMonth() + 1) > MES_RENDERIZADO) recargar();
}, 60 * 1000);

// ---- KPIs (siempre los 5 estados, aunque estén en 0) ----
const kpiEl = document.getElementById('kpis');
kpiEl.innerHTML = ESTADOS.map(estado => {
  const n = (DATA.buckets[estado] || []).length;
  const col = COLORS[estado];
  return `<div class="kpi-card">
    <div class="icon" style="background:${col.soft};color:${col.c}">${ICONS[estado]}</div>
    <div class="kpi-text">
      <div class="kpi-label">${estado}</div>
      <div class="kpi-value" style="color:${col.c}">${n}</div>
      <div class="kpi-sub">${KPI_SUB[estado]}</div>
    </div>
  </div>`;
}).join('');

// ---- construir slides: tabla para estados con actividad, grid para Disponible ----
function segmentos(eq){
  if (eq.segmento) return [eq.segmento];
  return eq.segmentos || [];
}

const MES_ACTUAL_NUM = MESES_NUM[DATA.mes] || 1;
function fechaDDMM(dia){
  return `${String(dia).padStart(2,'0')}/${String(MES_ACTUAL_NUM).padStart(2,'0')}`;
}

function diasCell(segs, color){
  if(!segs.length){
    return `<div class="dias-num" style="color:${color}">—</div>`;
  }
  return segs.map(s => `<div class="dias-pair">
    <div class="dias-item"><span class="dias-label">Fecha de Inicio</span><span class="dias-val" style="color:${color}">${fechaDDMM(s.inicio)}</span></div>
    <div class="dias-divider"></div>
    <div class="dias-item"><span class="dias-label">Fecha de Término</span><span class="dias-val" style="color:${color}">${fechaDDMM(s.fin)}</span></div>
  </div>`).join('');
}

function lugarDe(eq){
  const segs = segmentos(eq);
  return [...new Set(segs.map(s=>s.lugar))].join(' + ') || 'Sin lugar asignado';
}

// Agrupa por lugar (preservando el orden de primera aparición de cada lugar)
// sin romper el orden original dentro de cada grupo.
function ordenarPorLugar(items){
  const orden = [];
  const vistos = new Set();
  items.forEach(eq => {
    const l = lugarDe(eq);
    if(!vistos.has(l)){ vistos.add(l); orden.push(l); }
  });
  const rank = new Map(orden.map((l,i) => [l,i]));
  return [...items].sort((a,b) => rank.get(lugarDe(a)) - rank.get(lugarDe(b)));
}

function tableSlideHTML(estado, items){
  const color = COLORS[estado].c, soft = COLORS[estado].soft;
  let lastLugar = null;
  const rowSizes = [];
  const rowsHTML = items.map(eq => {
    const lugar = lugarDe(eq);
    const segs = segmentos(eq);
    let header = '';
    if(lugar !== lastLugar){
      lastLugar = lugar;
      const total = items.filter(x => lugarDe(x) === lugar).length;
      rowSizes.push('auto');
      header = `<div class="lugar-header"><span class="lugar-dot" style="background:${color}"></span>${lugar}
        <span class="lugar-count">· ${total} equipo${total===1?'':'s'}</span></div>`;
    }
    rowSizes.push('1fr');
    return header + `<div class="table-row table-columns">
      <div class="col-accent"><span class="accent-bar" style="background:${color}"></span></div>
      <div class="col-cat"><span class="cat-tag" style="background:${soft};color:${color}">${eq.categoria||''}</span></div>
      <div class="col-equipo"><div class="modelo">${eq.modelo||''}</div><div class="serie">${eq.numero_serie||''}</div></div>
      <div class="col-desc"><div class="desc">${eq.descripcion||''}</div></div>
      <div class="col-dias">${diasCell(segs, color)}</div>
    </div>`;
  }).join('');
  return `<div class="card-table">
    <div class="table-head table-columns">
      <div></div><div>Categoría</div><div>Equipo</div><div>Descripción</div><div>Días del mes</div>
    </div>
    <div class="table-body" style="grid-template-rows:${rowSizes.join(' ')}">${rowsHTML}</div>
  </div>`;
}

function gridSlideHTML(items){
  const chips = items.map(eq => `<div class="eq-chip">
      <div class="cat">${eq.categoria||''}</div>
      <div class="modelo">${eq.modelo||''}</div>
      <div class="serie">${eq.numero_serie||''}</div>
    </div>`).join('');
  return `<div class="grid-stage">${chips}</div>`;
}

const slidesDatos = [];
ESTADOS.forEach(estado => {
  let items = DATA.buckets[estado] || [];
  if (items.length === 0) return;
  if (estado !== "Disponible") items = ordenarPorLugar(items);
  const perSlide = estado === "Disponible" ? GRID_ITEMS_PER_SLIDE : TABLE_ROWS_PER_SLIDE;
  const totalPages = Math.ceil(items.length / perSlide);
  for (let i=0; i<items.length; i+=perSlide){
    slidesDatos.push({
      estado, items: items.slice(i, i+perSlide),
      page: Math.floor(i/perSlide)+1, totalPages, total: items.length
    });
  }
});

const stage = document.getElementById('stage');
const isotipoSlide = document.getElementById('isotipo-slide');
const slideTitle = document.getElementById('slide-title');
const slideBadge = document.getElementById('slide-badge');
const slideSubtitle = document.getElementById('slide-subtitle');
const progress = document.getElementById('progress');
const pauseIndicator = document.getElementById('pause-indicator');

slidesDatos.forEach((s,i) => {
  const d = document.createElement('div');
  d.className = 'slide';
  d.id = `slide-${i}`;
  d.innerHTML = s.estado === "Disponible" ? gridSlideHTML(s.items) : tableSlideHTML(s.estado, s.items);
  stage.insertBefore(d, isotipoSlide);
});

const TOTAL_PASOS = slidesDatos.length + 1;
const ES_ISOTIPO = (idx) => idx === slidesDatos.length;

slidesDatos.forEach((s,i) => {
  const dot = document.createElement('div');
  dot.className = 'progress-dot'; dot.id = `dot-${i}`;
  dot.innerHTML = '<span class="fill"></span>';
  progress.appendChild(dot);
});
const dotIso = document.createElement('div');
dotIso.className = 'progress-dot'; dotIso.id = `dot-${slidesDatos.length}`;
dotIso.innerHTML = '<span class="fill"></span>';
progress.appendChild(dotIso);

let current = 0, timer = null, paused = false;

function duracion(idx){ return ES_ISOTIPO(idx) ? SEGUNDOS_ISOTIPO : SEGUNDOS_POR_SLIDE; }

function showSlide(idx){
  for(let i=0;i<slidesDatos.length;i++){
    const el = document.getElementById(`slide-${i}`);
    el.classList.toggle('active', i===idx);
  }
  isotipoSlide.classList.toggle('active', ES_ISOTIPO(idx));

  document.getElementById('slide-header').style.visibility = ES_ISOTIPO(idx) ? 'hidden' : 'visible';
  if (!ES_ISOTIPO(idx)){
    const s = slidesDatos[idx];
    const col = COLORS[s.estado].c;
    slideTitle.textContent = s.estado;
    slideBadge.textContent = `${s.page}/${s.totalPages}`;
    slideBadge.style.background = col;
    slideSubtitle.textContent = `${s.total} equipo${s.total===1?'':'s'}`;
  }

  for(let i=0;i<TOTAL_PASOS;i++){
    const dot = document.getElementById(`dot-${i}`);
    dot.className = 'progress-dot' + (i<idx?' done':'') + (i===idx?' active'+(paused?' paused':''):'');
    if(i===idx) dot.style.setProperty('--dur', duracion(idx)+'s');
  }
}

function irA(idx){
  current = ((idx % TOTAL_PASOS) + TOTAL_PASOS) % TOTAL_PASOS;
  showSlide(current);
  clearTimeout(timer);
  if(!paused) timer = setTimeout(avanzar, duracion(current)*1000);
}
function avanzar(){ irA(current+1); }

function togglePausa(){
  paused = !paused;
  pauseIndicator.classList.toggle('visible', paused);
  const dot = document.getElementById(`dot-${current}`);
  if(paused){ clearTimeout(timer); dot.classList.add('paused'); }
  else { dot.classList.remove('paused'); timer = setTimeout(avanzar, duracion(current)*1000); }
}

document.body.addEventListener('click', togglePausa);
document.addEventListener('keydown', e => {
  if(e.code==='Space'){ e.preventDefault(); togglePausa(); return; }
  if(e.code==='ArrowRight' || e.code==='ArrowDown'){ e.preventDefault(); irA(current+1); return; }
  if(e.code==='ArrowLeft' || e.code==='ArrowUp'){ e.preventDefault(); irA(current-1); return; }
});

irA(0);
</script>
</body>
</html>
"""

out = (HTML
       .replace("__DATA_JSON__", DATA_JSON)
       .replace("__LOGO_B64__", LOGO_B64)
       .replace("__ISOTIPO_B64__", ISOTIPO_B64)
       .replace("__WATERMARK_B64__", WATERMARK_B64))

out_path = PROTO / "prototipo_D_gemco.html"
out_path.write_text(out, encoding="utf-8")
print("Generado:", out_path)

# Copia publicable: GitHub Pages sirve index.html desde la raíz del repo.
publish_path = BASE / "index.html"
publish_path.write_text(out, encoding="utf-8")
print("Generado:", publish_path)
