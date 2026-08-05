import json

with open("/sessions/eloquent-modest-tesla/mnt/outputs/proto/julio_buckets.json", encoding="utf-8") as f:
    data = json.load(f)

DATA_JSON = json.dumps(data, ensure_ascii=False)

COMMON_HEAD = """
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
"""

PROTO_A = """<!DOCTYPE html>
<html lang="es">
<head>
""" + COMMON_HEAD + """
<title>GEMCO . Trazabilidad Equipos - Prototipo A (Tarjetas)</title>
<style>
  :root{
    --navy-900:#0b1220; --navy-800:#0f172a; --bg:#f4f6fa; --card:#ffffff;
    --ink-1:#0b1220; --ink-2:#46516a; --ink-3:#8892a6; --border:#e4e8f0;
    --demo:#2f6fed; --demo-soft:#e8f0fe;
    --prestamo:#22a06b; --prestamo-soft:#e1f7ec;
    --incompleto:#ef4360; --incompleto-soft:#fde7ec;
    --nota:#8892a6; --nota-soft:#eef1f5;
    --disp:#0ea5b7; --disp-soft:#e1f7f9;
    --radius:14px; --shadow:0 1px 2px rgba(11,18,32,.04), 0 8px 22px -8px rgba(11,18,32,.12);
  }
  *{box-sizing:border-box;}
  body{margin:0;font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--ink-1);}
  header{background:var(--navy-800);color:#fff;padding:18px 28px;display:flex;align-items:center;justify-content:space-between;}
  header .brand{font-weight:800;letter-spacing:-.02em;font-size:1.15rem;}
  header .brand span{color:#93c5fd;font-weight:600;}
  header .mes{font-weight:600;font-size:.95rem;opacity:.85;text-transform:uppercase;letter-spacing:.08em;}
  main{padding:22px 28px 60px;max-width:1400px;margin:0 auto;}
  .summary{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:26px;}
  .stat{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px 18px;box-shadow:var(--shadow);min-width:140px;}
  .stat .n{font-size:1.6rem;font-weight:800;}
  .stat .l{font-size:.78rem;color:var(--ink-3);text-transform:uppercase;letter-spacing:.05em;font-weight:600;}
  .stat.demo .n{color:var(--demo);} .stat.prestamo .n{color:var(--prestamo);}
  .stat.incompleto .n{color:var(--incompleto);} .stat.nota .n{color:var(--nota);} .stat.disp .n{color:var(--disp);}

  section.grupo{margin-bottom:34px;}
  .grupo h2{display:flex;align-items:center;gap:10px;font-size:1.05rem;font-weight:700;margin:0 0 14px;}
  .grupo h2 .dot{width:11px;height:11px;border-radius:50%;}
  .grupo h2 .count{font-weight:600;color:var(--ink-3);font-size:.85rem;}
  .cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;}
  .card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:14px 16px;box-shadow:var(--shadow);position:relative;overflow:hidden;}
  .card::before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--c,var(--navy-800));}
  .card .cat{font-size:.72rem;color:var(--ink-3);text-transform:uppercase;letter-spacing:.06em;font-weight:600;}
  .card .modelo{font-size:1.05rem;font-weight:700;margin-top:2px;}
  .card .serie{font-family:'JetBrains Mono',monospace;font-size:.78rem;color:var(--ink-2);margin-top:1px;}
  .card .lugar{margin-top:8px;font-size:.9rem;font-weight:600;}
  .card .rango{font-size:.8rem;color:var(--ink-2);margin-top:2px;}
  .daybar{display:flex;gap:2px;margin-top:10px;}
  .daybar i{flex:1;height:10px;border-radius:2px;background:var(--border);}
  .daybar i.on{background:var(--c,var(--navy-800));}
  .card.disp{opacity:.75;}
  .card.disp .modelo{color:var(--ink-2);}
</style>
</head>
<body>
<header>
  <div class="brand">GEMCO <span>. Trazabilidad Equipos</span></div>
  <div class="mes" id="mesLabel"></div>
</header>
<main>
  <div class="summary" id="summary"></div>
  <div id="grupos"></div>
</main>
<script>
const DATA = __DATA_JSON__;
const COLORS = {
  "Demostración": {c:"var(--demo)", soft:"var(--demo-soft)"},
  "Préstamo": {c:"var(--prestamo)", soft:"var(--prestamo-soft)"},
  "Incompleto": {c:"var(--incompleto)", soft:"var(--incompleto-soft)"},
  "Nota/Servicio": {c:"var(--nota)", soft:"var(--nota-soft)"},
  "Disponible": {c:"var(--disp)", soft:"var(--disp-soft)"}
};
document.getElementById('mesLabel').textContent = DATA.mes + ' ' + DATA.anio;

const summaryEl = document.getElementById('summary');
Object.entries(DATA.buckets).forEach(([estado, items]) => {
  const cls = estado==='Demostración'?'demo':estado==='Préstamo'?'prestamo':estado==='Incompleto'?'incompleto':estado==='Nota/Servicio'?'nota':'disp';
  summaryEl.innerHTML += `<div class="stat ${cls}"><div class="n">${items.length}</div><div class="l">${estado}</div></div>`;
});

const gruposEl = document.getElementById('grupos');
function dayBar(seg, color, numDias){
  let html = '<div class="daybar">';
  for(let d=1; d<=numDias; d++){
    const on = seg && d>=seg.inicio && d<=seg.fin;
    html += `<i class="${on?'on':''}" style="--c:${color}"></i>`;
  }
  html += '</div>';
  return html;
}

Object.entries(DATA.buckets).forEach(([estado, items]) => {
  if(items.length===0) return;
  const color = COLORS[estado].c;
  let cardsHtml = '';
  items.forEach(eq => {
    const seg = eq.segmento;
    const isDisp = estado==='Disponible';
    cardsHtml += `<div class="card ${isDisp?'disp':''}" style="--c:${color}">
      <div class="cat">${eq.categoria||''}</div>
      <div class="modelo">${eq.modelo}</div>
      <div class="serie">${eq.numero_serie}</div>
      ${seg ? `<div class="lugar">${seg.lugar}</div><div class="rango">Día ${seg.inicio}-${seg.fin}</div>` : '<div class="lugar">Sin asignación este mes</div>'}
      ${dayBar(seg, color, DATA.num_dias)}
    </div>`;
  });
  gruposEl.innerHTML += `<section class="grupo">
    <h2><span class="dot" style="background:${color}"></span>${estado} <span class="count">(${items.length})</span></h2>
    <div class="cards">${cardsHtml}</div>
  </section>`;
});
</script>
</body>
</html>
"""

PROTO_B = """<!DOCTYPE html>
<html lang="es">
<head>
""" + COMMON_HEAD + """
<title>GEMCO . Trazabilidad Equipos - Prototipo B (Lista densa)</title>
<style>
  :root{
    --navy-900:#0b1220; --navy-800:#0f172a; --bg:#f7f8fb; --card:#ffffff;
    --ink-1:#0b1220; --ink-2:#46516a; --ink-3:#8892a6; --border:#e6e9f1;
    --demo:#2f6fed; --demo-soft:#e8f0fe;
    --prestamo:#22a06b; --prestamo-soft:#e1f7ec;
    --incompleto:#ef4360; --incompleto-soft:#fde7ec;
    --nota:#8892a6; --nota-soft:#eef1f5;
    --disp:#0ea5b7; --disp-soft:#e1f7f9;
  }
  *{box-sizing:border-box;}
  body{margin:0;font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--ink-1);font-size:14px;}
  header{background:var(--navy-800);color:#fff;padding:14px 24px;display:flex;align-items:center;justify-content:space-between;}
  header .brand{font-weight:800;letter-spacing:-.02em;font-size:1.05rem;}
  header .brand span{color:#93c5fd;font-weight:600;}
  header .mes{font-weight:600;font-size:.85rem;opacity:.85;text-transform:uppercase;letter-spacing:.08em;}
  main{padding:16px 24px 60px;max-width:1500px;margin:0 auto;}
  .filtros{display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap;}
  .pill{font:inherit;font-size:.8rem;font-weight:600;padding:6px 14px;border-radius:999px;border:1px solid var(--border);background:var(--card);cursor:pointer;color:var(--ink-2);}
  .pill.active{background:var(--navy-800);border-color:var(--navy-800);color:#fff;}
  table{width:100%;border-collapse:collapse;background:var(--card);border-radius:10px;overflow:hidden;box-shadow:0 1px 2px rgba(11,18,32,.04);}
  thead th{text-align:left;font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;color:var(--ink-3);font-weight:700;padding:8px 12px;border-bottom:2px solid var(--border);background:#fbfcfe;position:sticky;top:0;}
  tbody td{padding:7px 12px;border-bottom:1px solid var(--border);vertical-align:middle;}
  tbody tr:hover{background:#f9fafc;}
  .estado-pill{display:inline-flex;align-items:center;gap:5px;font-size:.75rem;font-weight:700;padding:3px 9px;border-radius:999px;}
  .serie{font-family:'JetBrains Mono',monospace;font-size:.78rem;color:var(--ink-2);}
  .daybar{display:flex;gap:1px;width:210px;}
  .daybar i{flex:1;height:12px;border-radius:1px;background:#eef0f5;}
  .daybar i.on{background:var(--c);}
  .lugar{font-weight:600;}
  .rango{color:var(--ink-3);font-size:.78rem;}
  .grupo-row td{background:#eef1f8;font-weight:700;font-size:.85rem;padding:8px 12px;}
</style>
</head>
<body>
<header>
  <div class="brand">GEMCO <span>. Trazabilidad Equipos</span></div>
  <div class="mes" id="mesLabel"></div>
</header>
<main>
  <div class="filtros" id="filtros"></div>
  <table>
    <thead><tr>
      <th>Estado</th><th>Categoría</th><th>Modelo</th><th>N. Serie</th><th>Lugar / Nota</th><th>Rango</th><th>Días del mes</th>
    </tr></thead>
    <tbody id="tbody"></tbody>
  </table>
</main>
<script>
const DATA = __DATA_JSON__;
const COLORS = {
  "Demostración": {c:"#2f6fed", soft:"#e8f0fe"},
  "Préstamo": {c:"#22a06b", soft:"#e1f7ec"},
  "Incompleto": {c:"#ef4360", soft:"#fde7ec"},
  "Nota/Servicio": {c:"#8892a6", soft:"#eef1f5"},
  "Disponible": {c:"#0ea5b7", soft:"#e1f7f9"}
};
document.getElementById('mesLabel').textContent = DATA.mes + ' ' + DATA.anio;

let activeFilter = 'Todos';
const estados = Object.keys(DATA.buckets);
const filtrosEl = document.getElementById('filtros');
function renderFiltros(){
  filtrosEl.innerHTML = ['Todos', ...estados].map(e =>
    `<button class="pill ${e===activeFilter?'active':''}" data-e="${e}">${e}${e!=='Todos' ? ' ('+DATA.buckets[e].length+')' : ''}</button>`
  ).join('');
  filtrosEl.querySelectorAll('.pill').forEach(btn=>{
    btn.onclick = () => { activeFilter = btn.dataset.e; renderFiltros(); renderTabla(); };
  });
}

function dayBar(seg, color){
  let html = '<div class="daybar">';
  for(let d=1; d<=DATA.num_dias; d++){
    const on = seg && d>=seg.inicio && d<=seg.fin;
    html += `<i class="${on?'on':''}" style="--c:${color}"></i>`;
  }
  html += '</div>';
  return html;
}

function renderTabla(){
  const tbody = document.getElementById('tbody');
  let rows = '';
  estados.forEach(estado => {
    if(activeFilter!=='Todos' && activeFilter!==estado) return;
    const items = DATA.buckets[estado];
    if(items.length===0) return;
    const color = COLORS[estado].c, soft = COLORS[estado].soft;
    rows += `<tr class="grupo-row"><td colspan="7" style="color:${color}">${estado} - ${items.length} equipo(s)</td></tr>`;
    items.forEach(eq=>{
      const seg = eq.segmento;
      rows += `<tr>
        <td><span class="estado-pill" style="background:${soft};color:${color}">${estado}</span></td>
        <td>${eq.categoria||''}</td>
        <td><b>${eq.modelo}</b></td>
        <td class="serie">${eq.numero_serie}</td>
        <td class="lugar">${seg ? seg.lugar : 'Sin asignación este mes'}</td>
        <td class="rango">${seg ? 'Día '+seg.inicio+'-'+seg.fin : '-'}</td>
        <td>${dayBar(seg, color)}</td>
      </tr>`;
    });
  });
  tbody.innerHTML = rows;
}
renderFiltros();
renderTabla();
</script>
</body>
</html>
"""

with open("/sessions/eloquent-modest-tesla/mnt/outputs/proto/prototipo_A_tarjetas.html", "w", encoding="utf-8") as f:
    f.write(PROTO_A.replace("__DATA_JSON__", DATA_JSON))

with open("/sessions/eloquent-modest-tesla/mnt/outputs/proto/prototipo_B_lista.html", "w", encoding="utf-8") as f:
    f.write(PROTO_B.replace("__DATA_JSON__", DATA_JSON))

print("done")
