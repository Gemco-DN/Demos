import json

with open("/sessions/eloquent-modest-tesla/mnt/outputs/proto/julio_buckets.json", encoding="utf-8") as f:
    data = json.load(f)
DATA_JSON = json.dumps(data, ensure_ascii=False)

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
<title>GEMCO . Trazabilidad Equipos - Panel TV</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box;}
  :root{
    --navy-900:#0b1220; --navy-800:#0f172a;
    --demo:#2f6fed; --demo-soft:#e8f0fe;
    --prestamo:#22a06b; --prestamo-soft:#e1f7ec;
    --incompleto:#ef4360; --incompleto-soft:#fde7ec;
    --nota:#8892a6; --nota-soft:#eef1f5;
    --disp:#0ea5b7; --disp-soft:#e1f7f9;
    --bg:#f4f6fa; --card:#ffffff; --border:#e4e8f0;
    --ink-1:#0b1220; --ink-2:#46516a; --ink-3:#8892a6;
  }
  html,body{width:100vw;height:100vh;overflow:hidden;background:var(--bg);
    font-family:'Inter',system-ui,sans-serif;color:var(--ink-1);}
  .stage{width:100vw;height:100vh;display:flex;flex-direction:column;}
  header{flex:0 0 9vh;background:var(--navy-800);color:#fff;display:flex;align-items:center;
    justify-content:space-between;padding:0 2.2vw;}
  .brand{font-weight:800;font-size:2.1vh;letter-spacing:-.01em;}
  .brand span{color:#93c5fd;font-weight:600;}
  .grupo-actual{font-weight:700;font-size:2.3vh;display:flex;align-items:center;gap:.8vw;}
  .grupo-actual .dot{width:1.6vh;height:1.6vh;border-radius:50%;}
  .meta{text-align:right;font-size:1.3vh;opacity:.8;font-weight:600;text-transform:uppercase;letter-spacing:.08em;}
  .meta b{display:block;font-size:1.7vh;opacity:1;margin-top:.2vh;}

  .progress{flex:0 0 4px;background:#1e293b;position:relative;overflow:hidden;}
  .progress .bar{position:absolute;inset:0 auto 0 0;width:0%;background:var(--gcolor,#93c5fd);}

  main{flex:1 1 auto;padding:2vh 2.2vw;min-height:0;display:flex;flex-direction:column;}
  .summary{flex:0 0 auto;display:flex;gap:1vw;margin-bottom:1.6vh;}
  .stat{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:1vh 1.1vw;
    box-shadow:0 1px 2px rgba(11,18,32,.05);flex:1;text-align:center;}
  .stat .n{font-size:2.3vh;font-weight:800;}
  .stat .l{font-size:1vh;color:var(--ink-3);text-transform:uppercase;letter-spacing:.05em;font-weight:700;margin-top:.2vh;}

  table{flex:1;width:100%;border-collapse:collapse;background:var(--card);border-radius:12px;
    overflow:hidden;box-shadow:0 1px 2px rgba(11,18,32,.05);}
  thead th{text-align:left;font-size:1.15vh;text-transform:uppercase;letter-spacing:.05em;color:var(--ink-3);
    font-weight:700;padding:1vh 1.2vw;border-bottom:2px solid var(--border);background:#fbfcfe;}
  tbody td{padding:1.05vh 1.2vw;border-bottom:1px solid var(--border);font-size:1.85vh;vertical-align:middle;}
  .estado-pill{display:inline-flex;align-items:center;font-size:1.35vh;font-weight:700;padding:.5vh 1vw;border-radius:999px;}
  .serie{font-family:'JetBrains Mono',monospace;font-size:1.5vh;color:var(--ink-2);}
  .modelo{font-weight:700;}
  .lugar{font-weight:600;}
  .rango{color:var(--ink-3);font-size:1.5vh;}
  .daybar{display:flex;gap:1px;width:14vw;}
  .daybar i{flex:1;height:1.6vh;border-radius:1px;background:#eef0f5;}
  .daybar i.on{background:var(--c);}

  .dots{flex:0 0 auto;display:flex;justify-content:center;gap:.6vw;padding-top:1.4vh;}
  .dots i{width:1vh;height:1vh;border-radius:50%;background:#d7dce6;}
  .dots i.on{background:var(--navy-800);}
</style>
</head>
<body>
<div class="stage">
  <header>
    <div class="brand">GEMCO <span>. Trazabilidad Equipos</span></div>
    <div class="grupo-actual" id="grupoActual"></div>
    <div class="meta">MES<b id="mesLabel"></b></div>
  </header>
  <div class="progress"><div class="bar" id="bar"></div></div>
  <main>
    <div class="summary" id="summary"></div>
    <table>
      <thead><tr><th>Categoría</th><th>Modelo</th><th>N. Serie</th><th>Lugar / Nota</th><th>Rango</th><th>Días del mes</th></tr></thead>
      <tbody id="tbody"></tbody>
    </table>
    <div class="dots" id="dots"></div>
  </main>
</div>
<script>
const DATA = __DATA_JSON__;
const COLORS = {
  "Demostración": {c:"#2f6fed", soft:"#e8f0fe"},
  "Préstamo": {c:"#22a06b", soft:"#e1f7ec"},
  "Incompleto": {c:"#ef4360", soft:"#fde7ec"},
  "Nota/Servicio": {c:"#8892a6", soft:"#eef1f5"},
  "Disponible": {c:"#0ea5b7", soft:"#e1f7f9"}
};
const ROWS_PER_SLIDE = 8;
const SLIDE_MS = 9000;

document.getElementById('mesLabel').textContent = DATA.mes + ' ' + DATA.anio;

// build slides: one per chunk of ROWS_PER_SLIDE within each non-empty estado group
const slides = [];
Object.entries(DATA.buckets).forEach(([estado, items]) => {
  if(items.length === 0) return;
  for(let i=0; i<items.length; i+=ROWS_PER_SLIDE){
    slides.push({estado, items: items.slice(i, i+ROWS_PER_SLIDE), page: Math.floor(i/ROWS_PER_SLIDE)+1,
      totalPages: Math.ceil(items.length/ROWS_PER_SLIDE), total: items.length});
  }
});

const summaryEl = document.getElementById('summary');
Object.entries(DATA.buckets).forEach(([estado, items]) => {
  const color = COLORS[estado].c;
  summaryEl.innerHTML += `<div class="stat" style="border-top:3px solid ${color}"><div class="n" style="color:${color}">${items.length}</div><div class="l">${estado}</div></div>`;
});

function dayBar(seg, color){
  let html = '<div class="daybar">';
  for(let d=1; d<=DATA.num_dias; d++){
    const on = seg && d>=seg.inicio && d<=seg.fin;
    html += `<i class="${on?'on':''}" style="--c:${color}"></i>`;
  }
  html += '</div>';
  return html;
}

let current = 0;
function renderSlide(){
  const slide = slides[current];
  const color = COLORS[slide.estado].c, soft = COLORS[slide.estado].soft;
  document.getElementById('grupoActual').innerHTML =
    `<span class="dot" style="background:${color}"></span>${slide.estado} <span style="opacity:.6;font-weight:500;font-size:1.6vh;margin-left:.5vw;">(pág. ${slide.page}/${slide.totalPages} - ${slide.total} equipos)</span>`;
  document.getElementById('tbody').innerHTML = slide.items.map(eq => {
    const seg = eq.segmento;
    return `<tr>
      <td>${eq.categoria||''}</td>
      <td class="modelo">${eq.modelo}</td>
      <td class="serie">${eq.numero_serie}</td>
      <td class="lugar">${seg ? seg.lugar : 'Sin asignación este mes'}</td>
      <td class="rango">${seg ? 'Día '+seg.inicio+'-'+seg.fin : '-'}</td>
      <td>${dayBar(seg, color)}</td>
    </tr>`;
  }).join('');
  document.getElementById('dots').innerHTML = slides.map((s,i) =>
    `<i class="${i===current?'on':''}"></i>`).join('');
  const bar = document.getElementById('bar');
  bar.style.setProperty('--gcolor', color);
  bar.style.background = color;
  bar.style.transition = 'none';
  bar.style.width = '0%';
  requestAnimationFrame(()=>{
    bar.style.transition = `width ${SLIDE_MS}ms linear`;
    bar.style.width = '100%';
  });
}

function nextSlide(){
  current = (current+1) % slides.length;
  renderSlide();
}

renderSlide();
setInterval(nextSlide, SLIDE_MS);
</script>
</body>
</html>
"""

with open("/sessions/eloquent-modest-tesla/mnt/outputs/proto/prototipo_C_tv_slides.html", "w", encoding="utf-8") as f:
    f.write(HTML.replace("__DATA_JSON__", DATA_JSON))
print("done", len(slides) if False else "ok")
