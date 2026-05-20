import json, os

with open(r'C:\Users\guilhermmell\Downloads\wc_data.json', encoding='utf-8') as f:
    raw_json = f.read()

html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'unsafe-inline' https://cdn.plot.ly; style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'none'">
<title>World Cup Dashboard (1930–2014)</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0b0f14;
  --surface:#131920;
  --surface2:#1a2232;
  --border:#1f2d3d;
  --gold:#f5c842;
  --gold2:#e6a817;
  --green:#2ecc71;
  --white:#e8edf3;
  --muted:#7a8fa6;
  --red:#e74c3c;
  --radius:12px;
}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--white);font-family:'Inter',system-ui,sans-serif;font-size:15px;line-height:1.5;min-height:100vh}
/* HEADER */
.header{background:linear-gradient(135deg,#0b1a0e 0%,#0f1f2e 50%,#1a1200 100%);border-bottom:2px solid var(--gold2);padding:2rem 2rem 1.5rem;text-align:center;position:relative;overflow:hidden}
.header::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 80% 60% at 50% 0%,rgba(245,200,66,.08) 0%,transparent 70%);pointer-events:none}
.header-icon{font-size:3rem;margin-bottom:.5rem;display:block}
.header h1{font-size:clamp(1.6rem,4vw,2.6rem);font-weight:700;color:var(--gold);letter-spacing:-.02em;text-shadow:0 0 30px rgba(245,200,66,.3)}
.header p{color:var(--muted);font-size:.95rem;margin-top:.4rem}
/* LAYOUT */
.container{max-width:1400px;margin:0 auto;padding:1.5rem}
.section{margin-bottom:2.5rem}
.section-title{font-size:1.1rem;font-weight:600;color:var(--gold);border-left:3px solid var(--gold);padding-left:.75rem;margin-bottom:1.25rem}
/* =========================================================
   MULTI-SELECT FILTER COMPONENT
   ========================================================= */
.filters-bar{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.25rem 1.5rem;margin-bottom:2rem;display:flex;flex-wrap:wrap;gap:1rem;align-items:flex-end}
.filter-group{display:flex;flex-direction:column;gap:.4rem;min-width:180px;flex:1}
.filter-group>label{font-size:.78rem;font-weight:500;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
/* The trigger button */
.ms-wrap{position:relative}
.ms-btn{
  width:100%;display:flex;justify-content:space-between;align-items:center;gap:.5rem;
  background:var(--surface2);border:1px solid var(--border);color:var(--white);
  padding:.5rem .75rem;border-radius:8px;font-size:.88rem;font-family:inherit;
  cursor:pointer;outline:none;transition:border-color .2s;text-align:left;
}
.ms-btn:focus,.ms-btn[aria-expanded="true"]{border-color:var(--gold)}
.ms-label{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ms-arrow{flex-shrink:0;color:var(--muted);font-size:.7rem;transition:transform .2s}
.ms-btn[aria-expanded="true"] .ms-arrow{transform:rotate(180deg)}
/* The dropdown panel */
.ms-panel{
  position:absolute;top:calc(100% + 4px);left:0;right:0;z-index:100;
  background:var(--surface2);border:1px solid var(--gold);border-radius:8px;
  box-shadow:0 8px 32px rgba(0,0,0,.6);max-height:240px;overflow-y:auto;
  padding:.4rem 0;
}
.ms-panel:not([hidden]){display:block}
.ms-panel[hidden]{display:none}
/* "Limpar" row at top */
.ms-sa{padding:.35rem .75rem;border-bottom:1px solid var(--border);margin-bottom:.25rem}
.ms-sa a{font-size:.75rem;color:var(--muted);text-decoration:none;cursor:pointer}
.ms-sa a:hover{color:var(--gold)}
/* Each checkbox option */
.ms-option{
  display:flex;align-items:center;gap:.5rem;padding:.32rem .75rem;cursor:pointer;
  font-size:.86rem;transition:background .15s;
}
.ms-option:hover{background:rgba(245,200,66,.07)}
.ms-option input[type=checkbox]{
  accent-color:var(--gold);width:14px;height:14px;cursor:pointer;flex-shrink:0
}
.ms-option span{color:var(--white)}
/* Active tag chips below the filter bar */
.active-tags{display:flex;flex-wrap:wrap;gap:.4rem;margin-bottom:1rem}
.tag{
  display:inline-flex;align-items:center;gap:.3rem;
  background:rgba(245,200,66,.1);border:1px solid rgba(245,200,66,.3);
  color:var(--gold);border-radius:20px;padding:.2rem .6rem;font-size:.75rem;
}
.tag-close{cursor:pointer;font-size:.9rem;opacity:.7;background:none;border:none;color:var(--gold);padding:0;line-height:1}
.tag-close:hover{opacity:1}
/* Reset button */
.btn-reset{padding:.5rem 1.25rem;background:var(--surface2);border:1px solid var(--border);color:var(--muted);border-radius:8px;cursor:pointer;font-size:.88rem;font-family:inherit;transition:all .2s;align-self:flex-end;white-space:nowrap}
.btn-reset:hover{border-color:var(--gold);color:var(--gold)}
/* =========================================================
   KPI CARDS — 4 per row
   ========================================================= */
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}
.kpi-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.3rem 1.4rem;position:relative;overflow:hidden;transition:transform .2s,border-color .2s}
.kpi-card:hover{transform:translateY(-2px);border-color:var(--gold2)}
.kpi-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--gold),var(--green))}
.kpi-icon{font-size:1.6rem;margin-bottom:.5rem}
.kpi-label{font-size:.75rem;color:var(--muted);font-weight:500;text-transform:uppercase;letter-spacing:.05em}
.kpi-value{font-size:2rem;font-weight:700;color:var(--white);line-height:1.1;margin-top:.2rem}
.kpi-sub{font-size:.78rem;color:var(--muted);margin-top:.3rem}
/* CHARTS */
.charts-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(480px,1fr));gap:1.5rem}
.chart-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.25rem;min-height:340px}
.chart-card.full{grid-column:1/-1}
.chart-title{font-size:.9rem;font-weight:600;color:var(--muted);margin-bottom:1rem;text-transform:uppercase;letter-spacing:.05em}
.chart-inner{width:100%;min-height:280px}
/* War note below evolution chart */
.war-note{
  margin-top:.9rem;display:flex;align-items:flex-start;gap:.6rem;
  padding:.65rem 1rem;
  background:rgba(231,76,60,.07);
  border-left:3px solid rgba(231,76,60,.6);
  border-radius:0 6px 6px 0;
  font-size:.82rem;color:#c9967a;line-height:1.5;
}
.war-note-icon{font-size:1rem;flex-shrink:0;margin-top:.05rem}
/* TABLES */
.table-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.25rem;overflow:hidden}
.table-controls{display:flex;gap:.75rem;margin-bottom:.75rem;flex-wrap:wrap;align-items:center}
.table-search{background:var(--surface2);border:1px solid var(--border);color:var(--white);padding:.4rem .75rem;border-radius:8px;font-size:.85rem;font-family:inherit;outline:none;flex:1;min-width:150px;max-width:300px}
.table-search:focus{border-color:var(--gold)}
.table-wrapper{overflow-x:auto;max-height:420px;overflow-y:auto}
table{width:100%;border-collapse:collapse;font-size:.83rem}
thead tr{position:sticky;top:0;z-index:2;background:var(--surface2)}
th{padding:.6rem .75rem;text-align:left;color:var(--muted);font-weight:600;text-transform:uppercase;font-size:.72rem;letter-spacing:.06em;cursor:pointer;white-space:nowrap;user-select:none;border-bottom:1px solid var(--border)}
th:hover{color:var(--gold)}
th.sort-asc::after{content:' ▲';color:var(--gold)}
th.sort-desc::after{content:' ▼';color:var(--gold)}
td{padding:.55rem .75rem;border-bottom:1px solid rgba(31,45,61,.5);white-space:nowrap}
tr:last-child td{border-bottom:none}
tbody tr:hover{background:rgba(245,200,66,.04)}
.td-num{text-align:right;font-variant-numeric:tabular-nums}
.td-team{font-weight:500}
.badge{display:inline-block;padding:.15rem .5rem;border-radius:4px;font-size:.72rem;font-weight:600}
.badge-gold{background:rgba(245,200,66,.15);color:var(--gold)}
.badge-green{background:rgba(46,204,113,.12);color:var(--green)}
.badge-red{background:rgba(231,76,60,.12);color:var(--red)}
.badge-gray{background:rgba(122,143,166,.18);color:var(--muted)}
.td-saldo{text-align:center;vertical-align:middle}
/* INSIGHTS */
.insights-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem}
.insight-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1rem 1.25rem;display:flex;gap:.75rem;align-items:flex-start}
.insight-icon{font-size:1.4rem;flex-shrink:0;margin-top:.1rem}
.insight-text{font-size:.85rem;color:var(--muted);line-height:1.6}
.insight-text strong{color:var(--white)}
/* EMPTY */
.empty-state{text-align:center;padding:3rem 1rem;color:var(--muted)}
.empty-icon{font-size:3rem;margin-bottom:.75rem}
/* FOOTER */
.footer{text-align:center;color:var(--muted);font-size:.8rem;padding:2rem;border-top:1px solid var(--border);margin-top:2rem}
/* SCROLLBAR */
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:var(--surface)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:var(--muted)}
@media(max-width:900px){
  .kpi-grid{grid-template-columns:repeat(2,1fr)}
  .charts-grid{grid-template-columns:1fr}
  .chart-card.full{grid-column:1}
  .header h1{font-size:1.4rem}
}
@media(max-width:480px){
  .kpi-grid{grid-template-columns:1fr 1fr}
}
</style>
</head>
<body>
<header class="header">
  <span class="header-icon">&#127942;</span>
  <h1>World Cup Dashboard (1930&ndash;2014)</h1>
  <p>Dados por partida + agregados por edi&ccedil;&atilde;o &mdash; 20 Copas do Mundo &bull; 852 partidas</p>
</header>
<main class="container">

  <!-- FILTERS -->
  <div class="filters-bar" role="search" aria-label="Filtros">
    <div class="filter-group">
      <label>Ano</label>
      <div class="ms-wrap" id="ms-year">
        <button class="ms-btn" type="button" aria-haspopup="listbox" aria-expanded="false">
          <span class="ms-label">Todas as Copas</span><span class="ms-arrow">&#9662;</span>
        </button>
        <div class="ms-panel" hidden role="listbox" aria-multiselectable="true"></div>
      </div>
    </div>
    <div class="filter-group">
      <label>Fase</label>
      <div class="ms-wrap" id="ms-stage">
        <button class="ms-btn" type="button" aria-haspopup="listbox" aria-expanded="false">
          <span class="ms-label">Todas as Fases</span><span class="ms-arrow">&#9662;</span>
        </button>
        <div class="ms-panel" hidden role="listbox" aria-multiselectable="true"></div>
      </div>
    </div>
    <div class="filter-group">
      <label>Sele&ccedil;&atilde;o</label>
      <div class="ms-wrap" id="ms-team">
        <button class="ms-btn" type="button" aria-haspopup="listbox" aria-expanded="false">
          <span class="ms-label">Todas</span><span class="ms-arrow">&#9662;</span>
        </button>
        <div class="ms-panel" hidden role="listbox" aria-multiselectable="true"></div>
      </div>
    </div>
    <div class="filter-group">
      <label>Pa&iacute;s Sede</label>
      <div class="ms-wrap" id="ms-country">
        <button class="ms-btn" type="button" aria-haspopup="listbox" aria-expanded="false">
          <span class="ms-label">Todos</span><span class="ms-arrow">&#9662;</span>
        </button>
        <div class="ms-panel" hidden role="listbox" aria-multiselectable="true"></div>
      </div>
    </div>
    <button class="btn-reset" id="btn-reset" type="button">&#8635; Resetar</button>
  </div>
  <!-- Active filter tags -->
  <div class="active-tags" id="active-tags"></div>

  <!-- KPIs -->
  <section class="section">
    <h2 class="section-title">Indicadores Gerais</h2>
    <div class="kpi-grid" id="kpi-grid"></div>
  </section>

  <!-- EVOLUTION -->
  <section class="section">
    <h2 class="section-title">Evolu&ccedil;&atilde;o Hist&oacute;rica</h2>
    <div class="charts-grid">
      <div class="chart-card full">
        <div class="chart-title">Gols por Copa &amp; M&eacute;dia por Partida</div>
        <div class="chart-inner" id="chart-goals-time"></div>
        <div class="war-note">
          <span class="war-note-icon">&#9888;&#65039;</span>
          <span>N&atilde;o houve Copa do Mundo entre <strong>1939 e 1949</strong> devido &agrave; <strong>Segunda Guerra Mundial</strong> (1939&ndash;1945) e ao per&iacute;odo de recupera&ccedil;&atilde;o p&oacute;s-guerra. A competi&ccedil;&atilde;o foi retomada no Brasil em <strong>1950</strong>.</span>
        </div>
      </div>
    </div>
  </section>

  <!-- RANKINGS TOP 5 -->
  <section class="section">
    <h2 class="section-title">Rankings por Sele&ccedil;&atilde;o (Top 5)</h2>
    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-title">&#127942; Mais Vit&oacute;rias</div>
        <div class="chart-inner" id="chart-top-wins"></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">&#9917; Mais Gols Marcados</div>
        <div class="chart-inner" id="chart-top-gf"></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">&#128683; Mais Gols Sofridos</div>
        <div class="chart-inner" id="chart-top-ga"></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">&#128577; Mais Derrotas</div>
        <div class="chart-inner" id="chart-top-losses"></div>
      </div>
    </div>
  </section>

  <!-- DISTRIBUTIONS -->
  <section class="section">
    <h2 class="section-title">Distribui&ccedil;&otilde;es &amp; P&ecirc;naltis</h2>
    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-title">Distribui&ccedil;&atilde;o de Gols por Partida</div>
        <div class="chart-inner" id="chart-goals-dist"></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">Disputas de P&ecirc;naltis por Ano</div>
        <div class="chart-inner" id="chart-pen-year"></div>
      </div>
      <div class="chart-card full">
        <div class="chart-title">Desfecho das Partidas: Tempo Normal vs Prorroga&ccedil;&atilde;o vs P&ecirc;naltis</div>
        <div class="chart-inner" id="chart-outcome-stack"></div>
      </div>
    </div>
  </section>

  <!-- TABLE TEAMS -->
  <section class="section">
    <h2 class="section-title">Tabela por Sele&ccedil;&atilde;o</h2>
    <div class="table-card">
      <div class="table-controls">
        <input class="table-search" id="search-teams" type="text" placeholder="Buscar sele&ccedil;&atilde;o..." maxlength="60" autocomplete="off">
        <span id="teams-count" style="font-size:.8rem;color:var(--muted)"></span>
      </div>
      <div class="table-wrapper">
        <table id="table-teams" aria-label="Tabela por sele&ccedil;&atilde;o">
          <thead><tr>
            <th data-col="t" data-type="s">Sele&ccedil;&atilde;o</th>
            <th data-col="g" data-type="n">Jogos</th>
            <th data-col="w" data-type="n">Vit&oacute;rias</th>
            <th data-col="d" data-type="n">Empates</th>
            <th data-col="l" data-type="n">Derrotas</th>
            <th data-col="gf" data-type="n">Gols Pr&oacute;</th>
            <th data-col="ga" data-type="n">Gols Contra</th>
            <th data-col="gd" data-type="n">Saldo</th>
            <th data-col="gpg" data-type="n">G/Jogo</th>
            <th data-col="gag" data-type="n">Sof/Jogo</th>
          </tr></thead>
          <tbody id="tbody-teams"></tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- TABLE EDITIONS -->
  <section class="section">
    <h2 class="section-title">Tabela por Edi&ccedil;&atilde;o</h2>
    <div class="table-card">
      <div class="table-wrapper">
        <table id="table-editions" aria-label="Tabela por edi&ccedil;&atilde;o">
          <thead><tr>
            <th data-col="year" data-type="n">Ano</th>
            <th data-col="country" data-type="s">Pa&iacute;s Sede</th>
            <th data-col="winner" data-type="s">Campe&atilde;o</th>
            <th data-col="runners_up" data-type="s">Vice</th>
            <th data-col="third" data-type="s">3&ordm;</th>
            <th data-col="goals" data-type="n">Gols</th>
            <th data-col="matches" data-type="n">Partidas</th>
            <th data-col="gpm" data-type="n">Gols/Part.</th>
            <th data-col="att_cup" data-type="n">P&uacute;blico Total</th>
            <th data-col="att_avg" data-type="n">P&uacute;blico M&eacute;d.</th>
          </tr></thead>
          <tbody id="tbody-editions"></tbody>
        </table>
      </div>
    </div>
  </section>

  <!-- INSIGHTS -->
  <section class="section">
    <h2 class="section-title">&#128161; Insights Autom&aacute;ticos</h2>
    <div class="insights-grid" id="insights-grid"></div>
  </section>
</main>
<footer class="footer">World Cup Dashboard &bull; FIFA World Cup 1930&ndash;2014 &bull; Plotly.js</footer>

<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
<script>
// =============================================================
// DATA: pre-processed from WorldCupFull.csv
// - Year -> int; goals/attendance -> numbers; NaN treated
// - has_et: regex "extra time|aet|golden goal"
// - has_pen: regex "penalt|penalties|penalty"
// - Attendance_cup: European dot-format (1.045.246) -> int
// =============================================================
const RAW = ''' + raw_json + ''';

// =============================================================
// HELPERS
// =============================================================
const fmt    = n => n == null ? 'N/A' : Number(n).toLocaleString('pt-BR');
const fmtDec = (n, d=2) => n == null ? 'N/A' : Number(n).toFixed(d);

// Abbreviated thousands/millions for KPI "P\xfablico Total"
function fmtK(n) {
  if (n == null || isNaN(n)) return 'N/A';
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace('.',',') + 'M';
  if (n >= 1_000)     return Math.round(n / 1_000) + 'K';
  return String(n);
}

// XSS-safe escape for data values used inside innerHTML
function esc(s) {
  return String(s ?? '')
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// =============================================================
// FILTER STATE — arrays allow multiple selections
// Empty array means "all values accepted" for that dimension
// =============================================================
let activeFilters = { year:[], stage:[], team:[], country:[] };

// Default placeholder labels per filter key
const PLACEHOLDERS = {
  year:'Todas as Copas', stage:'Todas as Fases',
  team:'Todas', country:'Todos'
};

// =============================================================
// MULTI-SELECT COMPONENT
// Builds checkbox panel inside .ms-panel for a given filter key
// =============================================================
function buildMultiSelect(wrapId, filterKey, vals) {
  const wrap  = document.getElementById(wrapId);
  const btn   = wrap.querySelector('.ms-btn');
  const label = btn.querySelector('.ms-label');
  const panel = wrap.querySelector('.ms-panel');

  // "Limpar sele\xe7\xe3o" row
  const saRow = document.createElement('div');
  saRow.className = 'ms-sa';
  const saLink = document.createElement('a');
  saLink.href = '#';
  saLink.textContent = 'Limpar sele\xe7\xe3o';
  saLink.addEventListener('click', e => {
    e.preventDefault();
    panel.querySelectorAll('input[type=checkbox]').forEach(cb => cb.checked = false);
    activeFilters[filterKey] = [];
    label.textContent = PLACEHOLDERS[filterKey];
    renderActiveTags();
    scheduleRender();
  });
  saRow.appendChild(saLink);
  panel.appendChild(saRow);

  // One checkbox per value
  vals.forEach(v => {
    const row = document.createElement('label');
    row.className = 'ms-option';
    const cb = document.createElement('input');
    cb.type = 'checkbox';
    // Year values come as numbers in the data; keep as-is for comparison
    cb.value = v;
    cb.dataset.key = filterKey;
    cb.addEventListener('change', () => {
      const checked = [...panel.querySelectorAll('input:checked')].map(c =>
        filterKey === 'year' ? parseInt(c.value, 10) : c.value
      );
      activeFilters[filterKey] = checked;
      // Update button label
      if (!checked.length) {
        label.textContent = PLACEHOLDERS[filterKey];
      } else if (checked.length === 1) {
        label.textContent = String(checked[0]);
      } else {
        label.textContent = checked.length + ' selecionados';
      }
      renderActiveTags();
      scheduleRender();
    });
    const span = document.createElement('span');
    span.textContent = v; // textContent — never innerHTML with data values
    row.appendChild(cb);
    row.appendChild(span);
    panel.appendChild(row);
  });

  // Toggle panel on button click
  btn.addEventListener('click', e => {
    e.stopPropagation();
    const isOpen = !panel.hidden;
    closeAllPanels();
    if (!isOpen) {
      panel.hidden = false;
      btn.setAttribute('aria-expanded', 'true');
    }
  });
}

function closeAllPanels() {
  document.querySelectorAll('.ms-panel').forEach(p => { p.hidden = true; });
  document.querySelectorAll('.ms-btn').forEach(b => b.setAttribute('aria-expanded','false'));
}

// Close panels when clicking outside
document.addEventListener('click', closeAllPanels);

// =============================================================
// ACTIVE FILTER TAGS (chips shown below the filter bar)
// =============================================================
const TAG_LABELS = { year:'Ano', stage:'Fase', team:'Sele\xe7\xe3o', country:'Pa\xeds Sede' };

function renderActiveTags() {
  const bar = document.getElementById('active-tags');
  bar.innerHTML = ''; // static structure — no data in innerHTML
  Object.entries(activeFilters).forEach(([key, vals]) => {
    vals.forEach(v => {
      const tag = document.createElement('span');
      tag.className = 'tag';
      // Label: "Fase: Group A" — built with textContent nodes, not innerHTML
      const lbl = document.createElement('span');
      lbl.textContent = TAG_LABELS[key] + ': ' + v;
      const x = document.createElement('button');
      x.className = 'tag-close';
      x.type = 'button';
      x.setAttribute('aria-label', 'Remover filtro ' + v);
      x.textContent = '\xd7';
      x.addEventListener('click', () => removeTag(key, v));
      tag.appendChild(lbl);
      tag.appendChild(x);
      bar.appendChild(tag);
    });
  });
}

function removeTag(key, val) {
  activeFilters[key] = activeFilters[key].filter(v => String(v) !== String(val));
  // Uncheck the matching checkbox
  const wrap = document.getElementById('ms-' + key);
  if (wrap) {
    const cb = [...wrap.querySelectorAll('input[type=checkbox]')]
      .find(c => String(c.value) === String(val));
    if (cb) cb.checked = false;
    // Update button label
    const label = wrap.querySelector('.ms-label');
    const sel = activeFilters[key];
    if (!sel.length) label.textContent = PLACEHOLDERS[key];
    else if (sel.length === 1) label.textContent = String(sel[0]);
    else label.textContent = sel.length + ' selecionados';
  }
  renderActiveTags();
  scheduleRender();
}

// =============================================================
// POPULATE ALL DROPDOWNS (called once at init)
// =============================================================
function populateFilters() {
  const years    = [...new Set(RAW.matches.map(m=>m.year))].sort((a,b)=>a-b);
  const stages   = [...new Set(RAW.matches.map(m=>m.stage))].sort();
  const teams    = [...new Set(RAW.matches.flatMap(m=>[m.home,m.away]))].sort();
  const countries= [...new Set(RAW.matches.map(m=>m.country))].sort();

  buildMultiSelect('ms-year',    'year',    years);
  buildMultiSelect('ms-stage',   'stage',   stages);
  buildMultiSelect('ms-team',    'team',    teams);
  buildMultiSelect('ms-country', 'country', countries);
}

// =============================================================
// FILTER MATCHES (supports multi-select arrays)
// =============================================================
function getFiltered() {
  const {year, stage, team, country} = activeFilters;
  return RAW.matches.filter(m => {
    if (year.length    && !year.includes(m.year))                           return false;
    if (stage.length   && !stage.includes(m.stage))                         return false;
    if (team.length    && !team.includes(m.home) && !team.includes(m.away)) return false;
    if (country.length && !country.includes(m.country))                     return false;
    return true;
  });
}

// =============================================================
// KPI CARDS
// =============================================================
function renderKPIs(filtered) {
  const n        = filtered.length;
  const goals    = filtered.reduce((s,m)=>s+m.hg+m.ag,0);
  const gpm      = n ? (goals/n).toFixed(2) : 0;
  const teams    = new Set(filtered.flatMap(m=>[m.home,m.away]));
  const attRows  = filtered.filter(m=>m.att>0);
  const totalAtt = attRows.reduce((s,m)=>s+m.att,0);
  const avgAtt   = attRows.length ? Math.round(totalAtt/attRows.length) : null;
  const penCount = filtered.filter(m=>m.has_pen).length;
  const etCount  = filtered.filter(m=>m.has_et && !m.has_pen).length;
  const etPenCnt = filtered.filter(m=>m.has_et||m.has_pen).length;

  const defs = [
    {icon:'&#9917;',   label:'Total de Partidas',          val:fmt(n),                     sub:''},
    {icon:'&#127919;', label:'Total de Gols',               val:fmt(goals),                 sub:''},
    {icon:'&#128200;', label:'Gols por Partida',            val:String(gpm),                sub:''},
    {icon:'&#127942;', label:'Sele&ccedil;&otilde;es',      val:fmt(teams.size),            sub:'distintas'},
    // P\xfablico Total: abbreviated with K/M
    {icon:'&#128101;', label:'P&uacute;blico Total',
      val: totalAtt>0 ? fmtK(totalAtt) : 'N/A',
      sub: avgAtt ? 'M\xe9dia: ' + fmtK(avgAtt) + '/jogo' : ''},
    {icon:'&#128260;', label:'Partidas c/ P\xeanaltis',      val:fmt(penCount),              sub:n?((penCount/n)*100).toFixed(1)+'% das partidas':''},
    {icon:'&#128336;', label:'S\xf3 Prorroga\xe7\xe3o',    val:fmt(etCount),               sub:'sem disputa de p\xeanaltis'},
    {icon:'&#127758;', label:'Edi\xe7\xf5es no recorte',   val:fmt(new Set(filtered.map(m=>m.year)).size), sub:'Copas do Mundo'},
  ];

  const grid = document.getElementById('kpi-grid');
  grid.innerHTML = '';
  defs.forEach(k => {
    const card = document.createElement('div');
    card.className = 'kpi-card';
    // icon/label: static HTML entities; val/sub: numbers via esc() or fmtK()
    card.innerHTML =
      '<div class="kpi-icon">'  + k.icon  + '</div>' +
      '<div class="kpi-label">' + k.label + '</div>' +
      '<div class="kpi-value">' + esc(k.val) + '</div>' +
      '<div class="kpi-sub">'   + esc(k.sub) + '</div>';
    grid.appendChild(card);
  });
}

// =============================================================
// PLOTLY DEFAULTS
// =============================================================
const PL = {
  paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)',
  font:{color:'#7a8fa6',family:'Inter,system-ui'},
  margin:{t:20,b:60,l:60,r:20},
  xaxis:{gridcolor:'#1f2d3d',zerolinecolor:'#1f2d3d'},
  yaxis:{gridcolor:'#1f2d3d',zerolinecolor:'#1f2d3d'},
  hoverlabel:{bgcolor:'#131920',bordercolor:'#1f2d3d',font:{color:'#e8edf3'}},
  showlegend:true,
  legend:{bgcolor:'rgba(0,0,0,0)',bordercolor:'rgba(0,0,0,0)'},
};
const PC = {displayModeBar:false,responsive:true};

function pl(id, traces, extra) {
  const lay = Object.assign({},PL,extra,{
    xaxis:Object.assign({},PL.xaxis,extra&&extra.xaxis),
    yaxis:Object.assign({},PL.yaxis,extra&&extra.yaxis),
  });
  Plotly.newPlot(id, traces, lay, PC);
}

function showEmpty(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = '<div class="empty-state"><div class="empty-icon">&#128202;</div><div>Sem dados para o filtro atual</div></div>';
}

// =============================================================
// CHART: Goals over time
// =============================================================
function chartGoalsTime(filtered) {
  const byY = {};
  filtered.forEach(m=>{
    if(!byY[m.year])byY[m.year]={g:0,n:0};
    byY[m.year].g+=m.hg+m.ag; byY[m.year].n++;
  });
  const yrs = Object.keys(byY).map(Number).sort((a,b)=>a-b);
  if(!yrs.length){showEmpty('chart-goals-time');return;}
  pl('chart-goals-time',[
    {x:yrs,y:yrs.map(y=>byY[y].g),type:'bar',name:'Gols Totais',marker:{color:'#f5c842'},yaxis:'y'},
    {x:yrs,y:yrs.map(y=>+(byY[y].g/byY[y].n).toFixed(2)),type:'scatter',mode:'lines+markers',
     name:'Gols/Partida',line:{color:'#2ecc71',width:2.5},marker:{size:7},yaxis:'y2'},
  ],{
    barmode:'group',
    xaxis:{title:{text:'Ano'},tickmode:'array',tickvals:yrs,ticktext:yrs.map(String),tickangle:-45},
    yaxis:{title:{text:'Gols Totais'},titlefont:{color:'#f5c842'},tickfont:{color:'#f5c842'}},
    yaxis2:{title:{text:'Gols/Partida'},titlefont:{color:'#2ecc71'},tickfont:{color:'#2ecc71'},
            overlaying:'y',side:'right',showgrid:false},
    legend:{x:.01,y:.99},
    margin:{t:20,b:80,l:60,r:60},
  });
}

// =============================================================
// CHART: Horizontal bar ranking — TOP 5
// To add more rankings: call chartRankTeams with a new metric key
// =============================================================
function chartRankTeams(filtered, metric, chartId, color, label) {
  const s = {};
  filtered.forEach(m=>{
    [m.home,m.away].forEach(t=>{if(!s[t])s[t]={w:0,l:0,d:0,gf:0,ga:0,g:0};});
    s[m.home].gf+=m.hg; s[m.home].ga+=m.ag; s[m.home].g++;
    s[m.away].gf+=m.ag; s[m.away].ga+=m.hg; s[m.away].g++;
    if(m.hg>m.ag){s[m.home].w++;s[m.away].l++;}
    else if(m.ag>m.hg){s[m.away].w++;s[m.home].l++;}
    else{s[m.home].d++;s[m.away].d++;}
  });
  // Slice to 5 — change here to increase the top-N
  const entries = Object.entries(s).map(([t,v])=>({t,v:v[metric]})).sort((a,b)=>b.v-a.v).slice(0,5);
  if(!entries.length){showEmpty(chartId);return;}
  pl(chartId,[{
    x:entries.map(e=>e.v), y:entries.map(e=>e.t),
    type:'bar',orientation:'h',
    marker:{color},
    text:entries.map(e=>e.v), textposition:'outside',
    hovertemplate:'<b>%{y}</b><br>'+esc(label)+': %{x}<extra></extra>',
  }],{
    xaxis:{title:{text:label}},
    yaxis:{autorange:'reversed',tickfont:{size:12}},
    margin:{t:20,b:40,l:170,r:70},
    showlegend:false,
  });
}

// =============================================================
// CHART: Goals histogram
// =============================================================
function chartGoalsDist(filtered) {
  if(!filtered.length){showEmpty('chart-goals-dist');return;}
  pl('chart-goals-dist',[{
    x:filtered.map(m=>m.hg+m.ag), type:'histogram',
    marker:{color:'#3498db',opacity:.85},
    xbins:{start:0,end:22,size:1},
    hovertemplate:'%{x} gols: %{y} partidas<extra></extra>',
  }],{
    xaxis:{title:{text:'Gols na Partida'},dtick:1},
    yaxis:{title:{text:'N\xba de Partidas'}},
    showlegend:false,
  });
}

// =============================================================
// CHART: Penalties per year
// =============================================================
function chartPenYear(filtered) {
  const byY = {};
  filtered.forEach(m=>{
    if(!byY[m.year])byY[m.year]=0;
    if(m.has_pen)byY[m.year]++;
  });
  const yrs = Object.keys(byY).map(Number).sort((a,b)=>a-b);
  if(!yrs.length){showEmpty('chart-pen-year');return;}
  const vals = yrs.map(y=>byY[y]);
  pl('chart-pen-year',[{
    x:yrs,y:vals,type:'bar',marker:{color:'#e74c3c'},
    text:vals,textposition:'outside',
    hovertemplate:'%{x}: %{y} disputas<extra></extra>',
  }],{
    xaxis:{title:{text:'Ano'},tickmode:'array',tickvals:yrs,ticktext:yrs.map(String),tickangle:-45},
    yaxis:{title:{text:'Partidas'},dtick:1},
    showlegend:false,
    margin:{t:30,b:80,l:50,r:20},
  });
}

// =============================================================
// CHART: Outcome stacked
// =============================================================
function chartOutcomeStack(filtered) {
  const byY = {};
  filtered.forEach(m=>{
    if(!byY[m.year])byY[m.year]={n:0,et:0,p:0};
    if(m.has_pen)byY[m.year].p++;
    else if(m.has_et)byY[m.year].et++;
    else byY[m.year].n++;
  });
  const yrs = Object.keys(byY).map(Number).sort((a,b)=>a-b);
  if(!yrs.length){showEmpty('chart-outcome-stack');return;}
  pl('chart-outcome-stack',[
    {x:yrs,y:yrs.map(y=>byY[y].n), name:'Tempo Normal',     type:'bar',marker:{color:'#2ecc71'}},
    {x:yrs,y:yrs.map(y=>byY[y].et),name:'Prorroga\xe7\xe3o',type:'bar',marker:{color:'#f5c842'}},
    {x:yrs,y:yrs.map(y=>byY[y].p), name:'P\xeanaltis',      type:'bar',marker:{color:'#e74c3c'}},
  ],{
    barmode:'stack',
    xaxis:{title:{text:'Ano'},tickmode:'array',tickvals:yrs,ticktext:yrs.map(String),tickangle:-45},
    yaxis:{title:{text:'Partidas'}},
    margin:{t:20,b:80,l:50,r:20},
  });
}

// =============================================================
// TABLE: Teams
// =============================================================
let teamsSort = {col:'w',dir:-1};

function renderTeamsTable(filtered, q) {
  const s = {};
  filtered.forEach(m=>{
    [m.home,m.away].forEach(t=>{if(!s[t])s[t]={t,w:0,l:0,d:0,gf:0,ga:0,g:0};});
    s[m.home].gf+=m.hg; s[m.home].ga+=m.ag; s[m.home].g++;
    s[m.away].gf+=m.ag; s[m.away].ga+=m.hg; s[m.away].g++;
    if(m.hg>m.ag){s[m.home].w++;s[m.away].l++;}
    else if(m.ag>m.hg){s[m.away].w++;s[m.home].l++;}
    else{s[m.home].d++;s[m.away].d++;}
  });
  let rows = Object.values(s).map(r=>({
    t:r.t,g:r.g,w:r.w,d:r.d,l:r.l,gf:r.gf,ga:r.ga,
    gd:r.gf-r.ga,
    gpg:r.g?+(r.gf/r.g).toFixed(2):0,
    gag:r.g?+(r.ga/r.g).toFixed(2):0,
  }));
  // q is the search input value — used only for comparison, never rendered as HTML
  if(q){const lq=q.toLowerCase();rows=rows.filter(r=>r.t.toLowerCase().includes(lq));}
  const {col,dir}=teamsSort;
  rows.sort((a,b)=>{const va=a[col],vb=b[col];return typeof va==='string'?dir*va.localeCompare(vb):dir*(va-vb);});
  const tbody=document.getElementById('tbody-teams');
  const cnt=document.getElementById('teams-count');
  tbody.innerHTML='';
  if(!rows.length){
    const tr=document.createElement('tr');const td=document.createElement('td');
    td.colSpan=10;td.style.textAlign='center';td.style.padding='2rem';td.style.color='var(--muted)';
    td.textContent='Sem dados para o filtro atual';tr.appendChild(td);tbody.appendChild(tr);
    if(cnt)cnt.textContent='0 sele\xe7\xf5es';return;
  }
  if(cnt)cnt.textContent=rows.length+' sele\xe7'+(rows.length!==1?'\xf5es':'\xe3o');
  rows.forEach(r=>{
    const tr=document.createElement('tr');
    const gdTxt=(r.gd>0?'+':'')+r.gd;
    const gdCls=r.gd>0?'badge badge-green':r.gd<0?'badge badge-red':'badge badge-gray';
    [{v:r.t,cls:'td-team'},{v:r.g,cls:'td-num'},{v:r.w,cls:'td-num'},{v:r.d,cls:'td-num'},
     {v:r.l,cls:'td-num'},{v:r.gf,cls:'td-num'},{v:r.ga,cls:'td-num'},
     {v:gdTxt,cls:'td-saldo '+gdCls},{v:fmtDec(r.gpg),cls:'td-num'},{v:fmtDec(r.gag),cls:'td-num'}]
    .forEach(c=>{const td=document.createElement('td');td.className=c.cls.trim();td.textContent=c.v;tr.appendChild(td);});
    tbody.appendChild(tr);
  });
}

// =============================================================
// TABLE: Editions
// =============================================================
let editionsSort = {col:'year',dir:1};

function renderEditionsTable(filtered) {
  const yrs=new Set(filtered.map(m=>m.year));
  let rows=RAW.editions.filter(e=>yrs.has(e.year));
  const {col,dir}=editionsSort;
  rows.sort((a,b)=>{const va=a[col],vb=b[col];if(va==null)return 1;if(vb==null)return -1;return typeof va==='string'?dir*va.localeCompare(vb):dir*(va-vb);});
  const tbody=document.getElementById('tbody-editions');
  tbody.innerHTML='';
  if(!rows.length){
    const tr=document.createElement('tr');const td=document.createElement('td');
    td.colSpan=10;td.style.textAlign='center';td.style.padding='2rem';td.style.color='var(--muted)';
    td.textContent='Sem dados para o filtro atual';tr.appendChild(td);tbody.appendChild(tr);return;
  }
  rows.forEach(r=>{
    const tr=document.createElement('tr');
    [{v:r.year,cls:'td-num badge badge-gold'},{v:r.country,cls:''},{v:r.winner,cls:'td-team'},
     {v:r.runners_up,cls:''},{v:r.third,cls:''},{v:r.goals,cls:'td-num'},{v:r.matches,cls:'td-num'},
     {v:fmtDec(r.gpm),cls:'td-num'},
     {v:r.att_cup!=null?fmt(r.att_cup):'N/A',cls:'td-num'},
     {v:r.att_avg!=null?fmt(r.att_avg):'N/A',cls:'td-num'}]
    .forEach(c=>{const td=document.createElement('td');td.className=c.cls.trim();td.textContent=c.v;tr.appendChild(td);});
    tbody.appendChild(tr);
  });
}

// =============================================================
// INSIGHTS
// =============================================================
function renderInsights(filtered) {
  const grid=document.getElementById('insights-grid');
  grid.innerHTML='';
  if(!filtered.length){
    grid.innerHTML='<div class="insight-card"><div class="insight-icon">&#128161;</div><div class="insight-text">Sem dados para o filtro atual.</div></div>';
    return;
  }
  const n=filtered.length;
  const byY={};
  filtered.forEach(m=>{if(!byY[m.year])byY[m.year]={g:0,n:0};byY[m.year].g+=m.hg+m.ag;byY[m.year].n++;});
  const bestGoalYr=Object.entries(byY).sort((a,b)=>b[1].g-a[1].g)[0];
  const bestGPMYr =Object.entries(byY).sort((a,b)=>(b[1].g/b[1].n)-(a[1].g/a[1].n))[0];
  const ts={};
  filtered.forEach(m=>{
    [m.home,m.away].forEach(t=>{if(!ts[t])ts[t]={w:0,g:0};});
    ts[m.home].g++;ts[m.away].g++;
    if(m.hg>m.ag)ts[m.home].w++;else if(m.ag>m.hg)ts[m.away].w++;
  });
  const topT   =Object.entries(ts).sort((a,b)=>b[1].w-a[1].w)[0];
  const penC   =filtered.filter(m=>m.has_pen).length;
  const penPct =n?((penC/n)*100).toFixed(1):0;
  const hiScore=filtered.reduce((b,m)=>(m.hg+m.ag)>(b?b.hg+b.ag:-1)?m:b,null);
  const bigW   =filtered.reduce((b,m)=>{const d=Math.abs(m.hg-m.ag);return d>(b?Math.abs(b.hg-b.ag):-1)?m:b;},null);

  const ins=[
    bestGoalYr&&{icon:'&#127942;',fn:()=>{const d=document.createElement('div');d.className='insight-text';
      d.innerHTML='A Copa com mais gols foi <strong>'+esc(bestGoalYr[0])+'</strong> com <strong>'+esc(String(bestGoalYr[1].g))+' gols</strong>.';return d;}},
    bestGPMYr&&{icon:'&#128200;',fn:()=>{const d=document.createElement('div');d.className='insight-text';
      d.innerHTML='Maior m\xe9dia de gols/partida: <strong>'+esc(bestGPMYr[0])+'</strong> (<strong>'+esc((bestGPMYr[1].g/bestGPMYr[1].n).toFixed(2))+' gols/jogo</strong>).';return d;}},
    topT&&{icon:'&#127881;',fn:()=>{const d=document.createElement('div');d.className='insight-text';
      d.innerHTML='Sele\xe7\xe3o com mais vit\xf3rias: <strong>'+esc(topT[0])+'</strong> (<strong>'+esc(String(topT[1].w))+' vit\xf3rias</strong> em '+esc(String(topT[1].g))+' jogos).';return d;}},
    {icon:'&#128260;',fn:()=>{const d=document.createElement('div');d.className='insight-text';
      d.innerHTML='Disputas de p\xeanaltis: <strong>'+esc(String(penC))+'</strong> (<strong>'+esc(String(penPct))+'%</strong> das partidas no recorte).';return d;}},
    hiScore&&{icon:'&#128293;',fn:()=>{const d=document.createElement('div');d.className='insight-text';
      d.innerHTML='Partida com mais gols: <strong>'+esc(hiScore.home)+' '+esc(String(hiScore.hg))+' x '+esc(String(hiScore.ag))+' '+esc(hiScore.away)+'</strong> ('+esc(String(hiScore.year))+', '+(hiScore.hg+hiScore.ag)+' gols).';return d;}},
    bigW&&{icon:'&#9889;',fn:()=>{const d=document.createElement('div');d.className='insight-text';
      d.innerHTML='Maior goleada: <strong>'+esc(bigW.home)+' '+esc(String(bigW.hg))+' x '+esc(String(bigW.ag))+' '+esc(bigW.away)+'</strong> ('+esc(String(bigW.year))+', '+esc(bigW.stage)+').';return d;}},
  ].filter(Boolean);

  ins.forEach(i=>{
    const card=document.createElement('div');card.className='insight-card';
    const ic=document.createElement('div');ic.className='insight-icon';ic.innerHTML=i.icon;
    card.appendChild(ic);card.appendChild(i.fn());grid.appendChild(card);
  });
}

// =============================================================
// SORTABLE TABLE HEADERS
// =============================================================
function initSort(tableId, state, renderFn) {
  const tbl=document.getElementById(tableId);if(!tbl)return;
  tbl.querySelectorAll('th[data-col]').forEach(th=>{
    th.addEventListener('click',()=>{
      const col=th.dataset.col;
      if(state.col===col)state.dir*=-1;
      else{state.col=col;state.dir=th.dataset.type==='n'?-1:1;}
      tbl.querySelectorAll('th').forEach(h=>h.classList.remove('sort-asc','sort-desc'));
      th.classList.add(state.dir===1?'sort-asc':'sort-desc');
      renderFn();
    });
  });
  const init=tbl.querySelector('th[data-col="'+state.col+'"]');
  if(init)init.classList.add(state.dir===1?'sort-asc':'sort-desc');
}

// =============================================================
// DEBOUNCED MAIN RENDER
// =============================================================
let _rt=null;
function scheduleRender(){clearTimeout(_rt);_rt=setTimeout(doRender,120);}

function doRender(){
  const f=getFiltered();
  const q=document.getElementById('search-teams')?.value??'';
  renderKPIs(f);
  chartGoalsTime(f);
  chartRankTeams(f,'w', 'chart-top-wins',  '#f5c842','Vit\xf3rias');
  chartRankTeams(f,'gf','chart-top-gf',    '#2ecc71','Gols Marcados');
  chartRankTeams(f,'ga','chart-top-ga',    '#e74c3c','Gols Sofridos');
  chartRankTeams(f,'l', 'chart-top-losses','#9b59b6','Derrotas');
  chartGoalsDist(f);
  chartPenYear(f);
  chartOutcomeStack(f);
  renderTeamsTable(f,q);
  renderEditionsTable(f);
  renderInsights(f);
}

// =============================================================
// BOOTSTRAP
// =============================================================
document.addEventListener('DOMContentLoaded',()=>{
  populateFilters();

  document.getElementById('btn-reset').addEventListener('click',()=>{
    activeFilters={year:[],stage:[],team:[],country:[]};
    document.querySelectorAll('.ms-panel input[type=checkbox]').forEach(cb=>{cb.checked=false;});
    Object.keys(PLACEHOLDERS).forEach(k=>{
      const wrap=document.getElementById('ms-'+k);
      if(wrap)wrap.querySelector('.ms-label').textContent=PLACEHOLDERS[k];
    });
    document.getElementById('search-teams').value='';
    renderActiveTags();
    scheduleRender();
  });

  document.getElementById('search-teams').addEventListener('input',()=>scheduleRender());

  initSort('table-teams',teamsSort,()=>renderTeamsTable(getFiltered(),document.getElementById('search-teams')?.value??''));
  initSort('table-editions',editionsSort,()=>renderEditionsTable(getFiltered()));

  doRender();
});
</script>
</body>
</html>'''

out_path = r'C:\Users\guilhermmell\Downloads\world_cup_dashboard.html'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

size = os.path.getsize(out_path)
print(f'Done. {out_path}')
print(f'Size: {size:,} bytes ({size/1024:.1f} KB)')
