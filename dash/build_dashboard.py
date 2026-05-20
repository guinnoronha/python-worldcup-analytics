import json, os, re, csv as _csv

# ─── Build raw_json from WorldCupFull.csv (adds ht_hg/ht_ag for HT analysis) ─
_CSV = r'C:\Users\guilhermmell\Downloads\WorldCupFull.csv'

def _int(v):
    try: return int(float(str(v).strip()))
    except: return None

def _flt(v):
    try:
        f = float(str(v).strip())
        return None if f != f else f   # NaN → None
    except: return None

def _att_cup(s):
    c = re.sub(r'[^\d]', '', str(s or ''))
    return int(c) if c else None

def _et(wc):  return bool(re.search(r'extra time|aet|golden goal', str(wc or ''), re.I))
def _pen(wc): return bool(re.search(r'penalt|penalties|penalty',   str(wc or ''), re.I))

_matches, _eds = [], {}
with open(_CSV, encoding='utf-8', newline='') as _f:
    for _row in _csv.DictReader(_f):
        _yr = _int(_row.get('Year'))
        if _yr is None: continue
        _hg = _flt(_row.get('Home Team Goals')) or 0.0
        _ag = _flt(_row.get('Away Team Goals')) or 0.0
        _wc = str(_row.get('Win conditions') or '').strip()
        _matches.append({
            'year':  _yr,
            'stage': str(_row.get('Stage', '')          or '').strip(),
            'home':  str(_row.get('Home Team Name', '')  or '').strip(),
            'away':  str(_row.get('Away Team Name', '')  or '').strip(),
            'hg': _hg, 'ag': _ag,
            'ht_hg': _flt(_row.get('Half-time Home Goals')),
            'ht_ag': _flt(_row.get('Half-time Away Goals')),
            'wc': _wc, 'has_et': _et(_wc), 'has_pen': _pen(_wc),
            'att':     _flt(_row.get('Attendance_matches')) or 0.0,
            'country': str(_row.get('Country', '') or '').strip(),
            'winner':  str(_row.get('Winner',  '') or '').strip(),
        })
        if _yr not in _eds:
            _eds[_yr] = {
                'year':       _yr,
                'country':    str(_row.get('Country',    '') or '').strip(),
                'winner':     str(_row.get('Winner',     '') or '').strip(),
                'runners_up': str(_row.get('Runners-Up', '') or '').strip(),
                'third':      str(_row.get('Third',      '') or '').strip(),
                'goals':      _flt(_row.get('GoalsScored')),
                'matches_n':  _int(_row.get('MatchesPlayed')),
                'att_cup':    _att_cup(_row.get('Attendance_cup')),
            }

_editions = []
for _yr, _e in sorted(_eds.items()):
    _n  = _e['matches_n'] or 0
    _g  = _e['goals'] or 0.0
    _ac = _e['att_cup']
    _editions.append({
        'year': _yr, 'country': _e['country'], 'winner': _e['winner'],
        'runners_up': _e['runners_up'], 'third': _e['third'],
        'goals': _g, 'matches': _n,
        'gpm':     round(_g / _n, 2) if _n else None,
        'att_cup': _ac,
        'att_avg': round(_ac / _n)   if (_ac and _n) else None,
        'pen_count': sum(1 for _m in _matches if _m['year'] == _yr and _m['has_pen']),
    })

_traw = {}
for _m in _matches:
    for _t, _gf, _ga in [(_m['home'], _m['hg'], _m['ag']), (_m['away'], _m['ag'], _m['hg'])]:
        if not _t: continue
        if _t not in _traw: _traw[_t] = {'t': _t, 'w': 0, 'l': 0, 'd': 0, 'gf': 0, 'ga': 0, 'g': 0}
        _r = _traw[_t]; _r['gf'] += _gf; _r['ga'] += _ga; _r['g'] += 1
        if _gf > _ga: _r['w'] += 1
        elif _ga > _gf: _r['l'] += 1
        else: _r['d'] += 1

_teams = [{
    't': _v['t'], 'g': _v['g'], 'w': _v['w'], 'd': _v['d'], 'l': _v['l'],
    'gf': _v['gf'], 'ga': _v['ga'], 'gd': _v['gf'] - _v['ga'],
    'gpg': round(_v['gf'] / _v['g'], 2) if _v['g'] else 0,
    'gag': round(_v['ga'] / _v['g'], 2) if _v['g'] else 0,
} for _v in sorted(_traw.values(), key=lambda x: x['t'])]

_raw_data = {'matches': _matches, 'editions': _editions, 'teams': _teams}
raw_json  = json.dumps(_raw_data, ensure_ascii=False)
# Also persist updated wc_data.json (now includes ht_hg/ht_ag)
with open(r'C:\Users\guilhermmell\Downloads\wc_data.json', 'w', encoding='utf-8') as _f:
    json.dump(_raw_data, _f, ensure_ascii=False)

html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'unsafe-inline' https://cdn.plot.ly; style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src https://cdn.plot.ly">
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
.td-saldo{display:table-cell;text-align:center;vertical-align:middle}
/* CORRELATION SECTION */
.corr-intro{font-size:.87rem;color:var(--muted);line-height:1.8;margin-bottom:1.25rem;padding:.75rem 1rem;background:var(--surface);border-left:3px solid var(--border);border-radius:0 6px 6px 0}
.corr-intro strong{color:var(--white)}
.corr-badge{display:inline-flex;align-items:center;padding:.22rem .7rem;border-radius:20px;font-size:.74rem;font-weight:600;margin-bottom:.55rem;letter-spacing:.02em}
.corr-badge.strong  {background:rgba(46,204,113,.14);color:#2ecc71;border:1px solid rgba(46,204,113,.25)}
.corr-badge.moderate{background:rgba(245,200,66,.12);color:#f5c842;border:1px solid rgba(245,200,66,.25)}
.corr-badge.weak    {background:rgba(122,143,166,.12);color:#7a8fa6;border:1px solid rgba(122,143,166,.2)}
.corr-suggest{margin-top:1.5rem;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.25rem 1.5rem}
.corr-suggest-title{font-size:.95rem;font-weight:600;color:var(--gold);margin-bottom:.85rem;display:flex;align-items:center;gap:.5rem}
.corr-suggest-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:.6rem}
.corr-suggest-item{display:flex;gap:.6rem;align-items:flex-start;padding:.5rem .75rem;background:var(--surface2);border-radius:8px;border:1px solid var(--border)}
.corr-suggest-item-icon{font-size:1rem;flex-shrink:0;margin-top:.1rem}
.corr-suggest-item-text{font-size:.82rem;color:var(--muted);line-height:1.55}
.corr-suggest-item-text strong{color:var(--white);display:block;margin-bottom:.1rem}
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
/* WORLD MAP metric toggle buttons */
.map-controls{display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:1rem}
.map-btn{
  padding:.38rem 1rem;background:var(--surface2);border:1px solid var(--border);
  color:var(--muted);border-radius:20px;cursor:pointer;font-size:.83rem;
  font-family:inherit;transition:all .2s;white-space:nowrap;
}
.map-btn:hover{border-color:var(--gold);color:var(--gold)}
.map-btn.active{background:rgba(245,200,66,.12);border-color:var(--gold);color:var(--gold);font-weight:600}
/* HT ANALYSIS stat mini-cards */
.ht-stats-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(195px,1fr));gap:1rem;margin-bottom:1.5rem}
.ht-stat{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.1rem 1.25rem;text-align:center}
.ht-stat-icon{font-size:1.55rem;margin-bottom:.3rem}
.ht-stat-val{font-size:1.75rem;font-weight:700;color:var(--white);line-height:1.1}
.ht-stat-label{font-size:.76rem;color:var(--muted);margin-top:.3rem;font-weight:500;line-height:1.4}
.ht-stat-sub{font-size:.71rem;color:var(--muted);margin-top:.18rem;opacity:.65}
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

  <!-- WORLD MAP -->
  <section class="section">
    <h2 class="section-title">&#127758; Distribui&ccedil;&atilde;o Geogr&aacute;fica</h2>
    <div class="chart-card full">
      <div class="map-controls">
        <button class="map-btn active" id="map-btn-wins"   onclick="setMapMetric('wins')">&#127942; Vit&oacute;rias</button>
        <button class="map-btn"        id="map-btn-titles" onclick="setMapMetric('titles')">&#127351; T&iacute;tulos</button>
        <button class="map-btn"        id="map-btn-gf"     onclick="setMapMetric('gf')">&#9917; Gols Marcados</button>
        <button class="map-btn"        id="map-btn-games"  onclick="setMapMetric('games')">&#128196; Partidas</button>
      </div>
      <div class="chart-inner" id="chart-world-map" style="min-height:400px"></div>
    </div>
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

  <!-- CORRELATIONS -->
  <section class="section">
    <h2 class="section-title">&#128202; An&aacute;lises de Correla&ccedil;&atilde;o</h2>
    <p class="corr-intro">
      Mede a rela&ccedil;&atilde;o linear entre vari&aacute;veis usando o <strong>coeficiente de Pearson (r)</strong>.
      Interpreta&ccedil;&atilde;o: <strong style="color:#2ecc71">|r| &ge; 0,7 = forte</strong> &bull;
      <strong style="color:#f5c842">0,4&ndash;0,7 = moderada</strong> &bull;
      <strong style="color:#7a8fa6">&lt; 0,4 = fraca</strong>.
      A dire&ccedil;&atilde;o positiva indica que as vari&aacute;veis crescem juntas; negativa, que uma cresce enquanto a outra diminui.
      A linha tracejada &eacute; a regress&atilde;o linear simples (tend&ecirc;ncia).
    </p>
    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-title">Tend&ecirc;ncia hist&oacute;rica &mdash; Ano &times; Gols/Partida</div>
        <span class="corr-badge weak" id="chart-corr-ano-gpm-badge">calculando&hellip;</span>
        <div class="chart-inner" id="chart-corr-ano-gpm"></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">P&uacute;blico M&eacute;dio &times; Gols/Partida (por edi&ccedil;&atilde;o)</div>
        <span class="corr-badge weak" id="chart-corr-att-gpm-badge">calculando&hellip;</span>
        <div class="chart-inner" id="chart-corr-att-gpm"></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">Gols Marcados &times; Vit&oacute;rias (por sele&ccedil;&atilde;o)</div>
        <span class="corr-badge weak" id="chart-corr-gf-wins-badge">calculando&hellip;</span>
        <div class="chart-inner" id="chart-corr-gf-wins"></div>
      </div>
      <div class="chart-card">
        <div class="chart-title">M&eacute;dia de Gols por Fase &mdash; em qual etapa se marca mais?</div>
        <div class="chart-inner" id="chart-corr-stage"></div>
      </div>
    </div>
    <!-- Sugest&otilde;es de dados adicionais -->
    <div class="corr-suggest">
      <div class="corr-suggest-title">&#128279; Dados que enriqueceriam as correla&ccedil;&otilde;es</div>
      <div class="corr-suggest-grid">
        <div class="corr-suggest-item">
          <span class="corr-suggest-item-icon">&#127942;</span>
          <div class="corr-suggest-item-text">
            <strong>FIFA Ranking hist&oacute;rico</strong>
            Correlacionar posi&ccedil;&atilde;o no ranking com vit&oacute;rias e t&iacute;tulos por edi&ccedil;&atilde;o &mdash; mede se o melhor ranqueado de fato vence mais.
          </div>
        </div>
        <div class="corr-suggest-item">
          <span class="corr-suggest-item-icon">&#128176;</span>
          <div class="corr-suggest-item-text">
            <strong>PIB per capita do pa&iacute;s sede</strong>
            Investigar se pa&iacute;ses mais ricos sediam Copas com maior p&uacute;blico, mais partidas e melhor infraestrutura.
          </div>
        </div>
        <div class="corr-suggest-item">
          <span class="corr-suggest-item-icon">&#127777;&#65039;</span>
          <div class="corr-suggest-item-text">
            <strong>Temperatura m&eacute;dia durante a Copa</strong>
            Clima quente pode reduzir intensidade f&iacute;sica e influenciar o n&uacute;mero de gols e o estilo de jogo.
          </div>
        </div>
        <div class="corr-suggest-item">
          <span class="corr-suggest-item-icon">&#128200;</span>
          <div class="corr-suggest-item-text">
            <strong>Valor de mercado das sele&ccedil;&otilde;es</strong>
            Dispon&iacute;vel no Transfermarkt a partir de 2000 &mdash; correlacionar investimento com desempenho e gols marcados.
          </div>
        </div>
        <div class="corr-suggest-item">
          <span class="corr-suggest-item-icon">&#9917;</span>
          <div class="corr-suggest-item-text">
            <strong>Posse de bola &amp; chutes a gol</strong>
            Datasets modernos (Opta, StatsBomb) permitem medir se dom&iacute;nio territorial se converte em mais gols.
          </div>
        </div>
        <div class="corr-suggest-item">
          <span class="corr-suggest-item-icon">&#127760;</span>
          <div class="corr-suggest-item-text">
            <strong>Jogadores nas top 5 ligas europeias</strong>
            Proxy de n&iacute;vel t&eacute;cnico por sele&ccedil;&atilde;o &mdash; correlacionar experi&ecirc;ncia em ligas de elite com resultados na Copa.
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- HT ANALYSIS -->
  <section class="section">
    <h2 class="section-title">&#8987; An&aacute;lise de Virada &mdash; Intervalo &rarr; Final</h2>
    <div id="ht-stats-row" class="ht-stats-row"></div>
    <div class="charts-grid">
      <div class="chart-card full">
        <div class="chart-title">Situa&ccedil;&atilde;o no Intervalo &times; Resultado Final (% empilhado &bull; perspectiva do time da casa)</div>
        <div class="chart-inner" id="chart-ht-analysis" style="min-height:320px"></div>
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
  const etPenCnt = filtered.filter(m=>m.has_et||m.has_pen).length;
  // Conta títulos por seleção dentro das edições presentes no recorte filtrado
  const _filtYrs = new Set(filtered.map(m=>m.year));
  const _titles  = {};
  RAW.editions.filter(e=>_filtYrs.has(e.year)).forEach(e=>{
    if(e.winner) _titles[e.winner] = (_titles[e.winner]||0)+1;
  });
  const _topTitle  = Object.entries(_titles).sort((a,b)=>b[1]-a[1])[0];
  // Detecta empate: coleta todos com o mesmo número máximo de títulos
  const _topCount  = _topTitle ? _topTitle[1] : 0;
  const _topTied   = _topCount > 0
    ? Object.entries(_titles).filter(([,v])=>v===_topCount)
    : [];
  // val: nome único | "Time A · Time B" | "N empatadas"
  const _topValStr = _topTied.length===0 ? 'N/A'
    : _topTied.length===1 ? _topTied[0][0]
    : _topTied.length===2 ? _topTied[0][0]+' \xb7 '+_topTied[1][0]
    : _topTied.length+' empatadas';
  // sub: "X título(s)" + aviso de empate quando necessário
  const _topSubStr = _topTied.length===0 ? ''
    : _topCount+' t\xedtulo'+(_topCount>1?'s':'')+(_topTied.length>1?' (empate)':'');

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
    {icon:'&#129351;', label:'Mais t\xedtulos',             val:_topValStr, sub:_topSubStr},
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
    yaxis:{autorange:'reversed',tickfont:{size:12},ticklabelstandoff:14},
    margin:{t:20,b:40,l:190,r:70},
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
// CORRELAÇÃO — helpers estatísticos
// Nenhum dado bruto do CSV é inserido via innerHTML aqui:
// badges usam textContent; hovertemplate usa esc() nas labels
// =============================================================

// Coeficiente de Pearson
function pearson(xs, ys) {
  const n = xs.length;
  if (n < 3) return NaN;
  const mx = xs.reduce((s,v)=>s+v,0)/n;
  const my = ys.reduce((s,v)=>s+v,0)/n;
  let num=0, dx2=0, dy2=0;
  for (let i=0;i<n;i++) {
    const dx=xs[i]-mx, dy=ys[i]-my;
    num+=dx*dy; dx2+=dx*dx; dy2+=dy*dy;
  }
  return (dx2&&dy2) ? num/Math.sqrt(dx2*dy2) : NaN;
}

// Regressão linear simples → y = a + b*x
function linReg(xs, ys) {
  const n=xs.length;
  const mx=xs.reduce((s,v)=>s+v,0)/n;
  const my=ys.reduce((s,v)=>s+v,0)/n;
  let num=0, den=0;
  xs.forEach((x,i)=>{ const d=x-mx; num+=d*(ys[i]-my); den+=d*d; });
  const b = den ? num/den : 0;
  return { a: my-b*mx, b };
}

// Classifica a força e direção da correlação
function corrLabel(r) {
  if (isNaN(r)) return { txt:'dados insuficientes', cls:'weak' };
  const abs=Math.abs(r);
  const dir=r>=0 ? 'positiva' : 'negativa';
  const rStr='r = '+r.toFixed(2);
  if (abs>=0.7) return { txt:rStr+' · forte '+dir,     cls:'strong'   };
  if (abs>=0.4) return { txt:rStr+' · moderada '+dir,  cls:'moderate' };
  return             { txt:rStr+' · fraca '+dir,       cls:'weak'     };
}

// Scatter genérico com trendline e badge de correlação
function chartCorrScatter(id, pts, xLabel, yLabel, color) {
  if (pts.length < 3) { showEmpty(id); return; }
  const xs=pts.map(p=>p.x), ys=pts.map(p=>p.y);
  const r = pearson(xs, ys);
  const {a,b} = linReg(xs, ys);
  const xMin=Math.min(...xs), xMax=Math.max(...xs);
  const {txt,cls} = corrLabel(r);

  // Badge: textContent apenas — nenhum dado bruto em innerHTML
  const badge = document.getElementById(id+'-badge');
  if (badge) { badge.textContent=txt; badge.className='corr-badge '+cls; }

  pl(id, [
    {
      x:xs, y:ys, mode:'markers', type:'scatter', showlegend:false,
      // esc() aplicado em todas as labels derivadas de dados
      text: pts.map(p => esc(String(p.label||''))),
      hovertemplate: '<b>%{text}</b><br>'+esc(xLabel)+': %{x}<br>'+esc(yLabel)+': %{y:.2f}<extra></extra>',
      marker:{ color, size:10, opacity:.85, line:{color:'rgba(255,255,255,.2)',width:1} },
    },
    {
      x:[xMin,xMax], y:[+(a+b*xMin).toFixed(3), +(a+b*xMax).toFixed(3)],
      mode:'lines', type:'scatter', showlegend:false,
      line:{ color:'rgba(255,255,255,.22)', width:2, dash:'dot' },
      hoverinfo:'skip',
    },
  ], {
    xaxis:{ title:{ text:xLabel } },
    yaxis:{ title:{ text:yLabel } },
    showlegend:false,
    margin:{ t:10, b:55, l:60, r:20 },
  });
}

// --- Correlação 1: Ano × Gols/Partida (nível de edição) ---
// Hipótese: o número de gols por jogo diminuiu ao longo das décadas?
function chartCorrAnoGPM(filtered) {
  const yrs = new Set(filtered.map(m=>m.year));
  const pts = RAW.editions
    .filter(e => yrs.has(e.year) && e.gpm != null)
    .map(e => ({ x:e.year, y:e.gpm, label:e.year+' ('+e.country+')' }));
  chartCorrScatter('chart-corr-ano-gpm', pts, 'Ano', 'Gols/Partida', '#f5c842');
}

// --- Correlação 2: Público médio × Gols/Partida (nível de edição) ---
// Hipótese: mais torcedores nas arquibancadas estimula mais gols?
function chartCorrAttGPM(filtered) {
  const yrs = new Set(filtered.map(m=>m.year));
  const pts = RAW.editions
    .filter(e => yrs.has(e.year) && e.gpm != null && e.att_avg != null)
    .map(e => ({ x:Math.round(e.att_avg/1000), y:e.gpm, label:e.year+' ('+e.country+')' }));
  chartCorrScatter('chart-corr-att-gpm', pts, 'P\xfablico M\xe9dio (K)', 'Gols/Partida', '#3498db');
}

// --- Correlação 3: Gols Marcados × Vitórias (nível de seleção) ---
// Hipótese: ataques mais eficientes ganham significativamente mais jogos?
function chartCorrGFWins(filtered) {
  const s = {};
  filtered.forEach(m => {
    [m.home,m.away].forEach(t => { if(!s[t]) s[t]={gf:0,w:0}; });
    s[m.home].gf+=m.hg; s[m.away].gf+=m.ag;
    if (m.hg>m.ag) s[m.home].w++;
    else if (m.ag>m.hg) s[m.away].w++;
  });
  const pts = Object.entries(s)
    .filter(([,v]) => v.gf>0 || v.w>0)
    .map(([t,v]) => ({ x:v.gf, y:v.w, label:t }));
  chartCorrScatter('chart-corr-gf-wins', pts, 'Gols Marcados', 'Vit\xf3rias', '#2ecc71');
}

// --- Análise 4: Média de Gols por Fase ---
// Identifica em qual etapa do torneio o jogo é mais aberto/artilheiro
function chartCorrStageGoals(filtered) {
  const byS = {};
  filtered.forEach(m => {
    if (!byS[m.stage]) byS[m.stage]={sum:0,n:0};
    byS[m.stage].sum += m.hg+m.ag;
    byS[m.stage].n++;
  });
  const entries = Object.entries(byS)
    .map(([s,v]) => ({ s, avg:+(v.sum/v.n).toFixed(2), n:v.n }))
    .sort((a,b) => b.avg-a.avg);
  if (!entries.length) { showEmpty('chart-corr-stage'); return; }
  pl('chart-corr-stage', [{
    x: entries.map(e=>e.avg),
    y: entries.map(e=>e.s),
    type:'bar', orientation:'h',
    marker:{ color:'#9b59b6' },
    text: entries.map(e=>e.avg),
    textposition:'outside',
    hovertemplate: '<b>%{y}</b><br>M\xe9dia: %{x:.2f} gols<br>(%{customdata} partidas)<extra></extra>',
    customdata: entries.map(e=>e.n),
  }], {
    xaxis:{ title:{ text:'M\xe9dia de Gols por Partida' } },
    yaxis:{ autorange:'reversed', tickfont:{ size:10 } },
    showlegend:false,
    margin:{ t:10, b:45, l:175, r:70 },
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
     {v:gdTxt,cls:'td-saldo',badge:gdCls},{v:fmtDec(r.gpg),cls:'td-num'},{v:fmtDec(r.gag),cls:'td-num'}]
    .forEach(c=>{
      const td=document.createElement('td');
      td.className=c.cls;
      if(c.badge){
        // Badge lives inside a <span> so the <td> keeps display:table-cell alignment
        const sp=document.createElement('span');
        sp.className=c.badge;
        sp.textContent=c.v;
        td.appendChild(sp);
      } else {
        td.textContent=c.v;
      }
      tr.appendChild(td);
    });
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
// TEAM → COUNTRY MAPPING (historical/renamed teams for choropleth)
// Maps legacy national team names to modern Plotly country names
// =============================================================
const TEAM_TO_COUNTRY = {
  'Germany FR':'Germany','West Germany':'Germany','German DR':'Germany',
  'Soviet Union':'Russia','Czechoslovakia':'Czech Republic',
  'Yugoslavia':'Serbia','Dutch East Indies':'Indonesia',
  'Korea Republic':'South Korea','Korea DPR':'North Korea',
  'USA':'United States',
  'England':'United Kingdom','Scotland':'United Kingdom',
  'Wales':'United Kingdom','Northern Ireland':'United Kingdom',
  'Republic of Ireland':'Ireland','China PR':'China',
  'Ivory Coast':"Cote d'Ivoire",'DR Congo':'Dem. Rep. Congo',
  'Bosnia and Herzegovina':'Bosnia and Herz.',
};
function teamToCountry(t){ return TEAM_TO_COUNTRY[t] || t; }

// =============================================================
// WORLD MAP — choropleth with metric toggle
// Security: all data rendered via Plotly text array (not innerHTML).
// esc() applied to label used in hovertemplate format string.
// =============================================================
let _mapMetric = 'wins';

function setMapMetric(m) {
  _mapMetric = m;
  document.querySelectorAll('.map-btn').forEach(b => b.classList.remove('active'));
  const btn = document.getElementById('map-btn-' + m);
  if (btn) btn.classList.add('active');
  chartWorldMap(getFiltered());
}

function chartWorldMap(filtered) {
  const s = {};
  const _yrs = new Set(filtered.map(m => m.year));
  filtered.forEach(m => {
    const hc = teamToCountry(m.home), ac = teamToCountry(m.away);
    [hc, ac].forEach(c => { if (!s[c]) s[c] = {wins:0, gf:0, games:0, titles:0}; });
    s[hc].games++; s[ac].games++;
    s[hc].gf += m.hg; s[ac].gf += m.ag;
    if (m.hg > m.ag) s[hc].wins++;
    else if (m.ag > m.hg) s[ac].wins++;
  });
  // Titles come from editions, not individual matches
  RAW.editions.filter(e => _yrs.has(e.year) && e.winner).forEach(e => {
    const c = teamToCountry(e.winner);
    if (!s[c]) s[c] = {wins:0, gf:0, games:0, titles:0};
    s[c].titles++;
  });
  const entries = Object.entries(s).filter(([, v]) => v[_mapMetric] > 0);
  if (!entries.length) { showEmpty('chart-world-map'); return; }
  const lbls = { wins:'Vit\xf3rias', titles:'T\xedtulos', gf:'Gols Marcados', games:'Partidas' };
  const lbl  = lbls[_mapMetric];
  Plotly.newPlot('chart-world-map', [{
    type: 'choropleth', locationmode: 'country names',
    locations: entries.map(([c]) => c),
    z:    entries.map(([, v]) => v[_mapMetric]),
    // text array values come from teamToCountry() — not raw CSV data in innerHTML
    text: entries.map(([c, v]) => c + '<br>' + esc(lbl) + ': ' + v[_mapMetric]),
    colorscale: [[0,'#131920'],[0.12,'#0d2137'],[0.35,'#0f3d6e'],[0.65,'#1a6291'],[0.85,'#e6a817'],[1,'#f5c842']],
    colorbar: {
      title: { text: lbl, font: { color: '#7a8fa6' } },
      tickfont: { color: '#7a8fa6' },
      bgcolor: 'rgba(0,0,0,0)', bordercolor: 'rgba(0,0,0,0)',
      len: 0.65, thickness: 13,
    },
    hovertemplate: '%{text}<extra></extra>',
    marker: { line: { color: '#1f2d3d', width: 0.5 } },
  }], {
    paper_bgcolor: 'rgba(0,0,0,0)',
    font: { color: '#7a8fa6', family: 'Inter,system-ui' },
    geo: {
      showframe: false,
      showcoastlines: true, coastlinecolor: '#1f2d3d',
      showland: true,       landcolor: '#131920',
      showocean: true,      oceancolor: '#0b0f14',
      showlakes: false,     showborder: false,
      showcountries: true,  countrycolor: '#1f2d3d',
      projection: { type: 'natural earth' },
      bgcolor: 'rgba(0,0,0,0)',
    },
    margin: { t: 10, b: 10, l: 0, r: 0 },
    dragmode: false,
  }, { displayModeBar: false, responsive: true });
}

// =============================================================
// HT ANALYSIS — Half-time situation → Full-time outcome
// Security: all dynamic values set via textContent (not innerHTML).
// ht-stat-icon uses innerHTML with hardcoded HTML entities only.
// =============================================================
function renderHTStats(filtered) {
  const row = document.getElementById('ht-stats-row');
  row.innerHTML = '';
  const ht = filtered.filter(m => m.ht_hg != null && m.ht_ag != null);
  if (!ht.length) {
    const p = document.createElement('p');
    p.style.cssText = 'color:var(--muted);font-size:.85rem;padding:.5rem 0';
    p.textContent = 'Dados de intervalo n\xe3o dispon\xedveis para o filtro atual.';
    row.appendChild(p); return;
  }
  const leading = ht.filter(m => m.ht_hg !== m.ht_ag);
  const level   = ht.filter(m => m.ht_hg === m.ht_ag);
  let comebacks = 0, heldLead = 0;
  ht.forEach(m => {
    const htD = m.ht_hg - m.ht_ag, ftD = m.hg - m.ag;
    if      (htD > 0) { if (ftD > 0) heldLead++; else if (ftD < 0) comebacks++; }
    else if (htD < 0) { if (ftD < 0) heldLead++; else if (ftD > 0) comebacks++; }
  });
  const lN = leading.length;
  const lW = level.filter(m => m.hg !== m.ag).length;
  const pct = (n, d) => d ? (n / d * 100).toFixed(1) + '%' : 'N/A';
  const stats = [
    { icon:'&#9989;',   val:pct(heldLead, lN),          label:'Manteve a lideran\xe7a',                  sub:heldLead+' de '+lN+' jogos liderando no HT' },
    { icon:'&#128260;', val:pct(comebacks, lN),          label:'Taxa de virada',                           sub:comebacks+' viradas em '+lN+' jogos c/ l\xedder no HT' },
    { icon:'&#9878;',   val:pct(lW, level.length),       label:'Empatados no HT que decidiram no 2\xba T', sub:lW+' de '+level.length+' empatados no intervalo' },
    { icon:'&#128202;', val:String(ht.length),            label:'Partidas com dados de intervalo',          sub:'de '+filtered.length+' no recorte atual' },
  ];
  stats.forEach(s => {
    const d  = document.createElement('div'); d.className  = 'ht-stat';
    // icon: hardcoded HTML entity — safe for innerHTML
    const ic = document.createElement('div'); ic.className = 'ht-stat-icon'; ic.innerHTML = s.icon;
    // remaining: data-derived — always textContent
    const vl = document.createElement('div'); vl.className = 'ht-stat-val';   vl.textContent = s.val;
    const lb = document.createElement('div'); lb.className = 'ht-stat-label'; lb.textContent = s.label;
    const sb = document.createElement('div'); sb.className = 'ht-stat-sub';   sb.textContent = s.sub;
    d.appendChild(ic); d.appendChild(vl); d.appendChild(lb); d.appendChild(sb);
    row.appendChild(d);
  });
}

function chartHTAnalysis(filtered) {
  const ht = filtered.filter(m => m.ht_hg != null && m.ht_ag != null);
  if (ht.length < 5) { showEmpty('chart-ht-analysis'); return; }
  const groups = [
    ht.filter(m => m.ht_hg > m.ht_ag),   // Home leading at HT
    ht.filter(m => m.ht_hg === m.ht_ag),  // Level at HT
    ht.filter(m => m.ht_hg < m.ht_ag),   // Away leading at HT
  ];
  const ylbls = ['Casa liderava no HT', 'Empatados no HT', 'Visitante liderava no HT'];
  const wins = [], draws = [], losses = [];
  groups.forEach(g => {
    const n = g.length || 1;
    wins.push(+((g.filter(m => m.hg > m.ag).length / n) * 100).toFixed(1));
    draws.push(+((g.filter(m => m.hg === m.ag).length / n) * 100).toFixed(1));
    losses.push(+((g.filter(m => m.hg < m.ag).length / n) * 100).toFixed(1));
  });
  pl('chart-ht-analysis', [
    {
      name: 'Vit\xf3ria (casa)', x: wins, y: ylbls, type: 'bar', orientation: 'h',
      marker: { color: '#2ecc71' },
      text: wins.map(v => v + '%'), textposition: 'inside', insidetextanchor: 'middle',
      textfont: { size: 11, color: '#0a1a0a' },
      hovertemplate: '<b>%{y}</b><br>Vit\xf3ria casa: %{x:.1f}%<extra></extra>',
    },
    {
      name: 'Empate', x: draws, y: ylbls, type: 'bar', orientation: 'h',
      marker: { color: '#f5c842' },
      text: draws.map(v => v + '%'), textposition: 'inside', insidetextanchor: 'middle',
      textfont: { size: 11, color: '#1a1200' },
      hovertemplate: '<b>%{y}</b><br>Empate: %{x:.1f}%<extra></extra>',
    },
    {
      name: 'Vit\xf3ria (fora)', x: losses, y: ylbls, type: 'bar', orientation: 'h',
      marker: { color: '#e74c3c' },
      text: losses.map(v => v + '%'), textposition: 'inside', insidetextanchor: 'middle',
      textfont: { size: 11, color: '#fff' },
      hovertemplate: '<b>%{y}</b><br>Vit\xf3ria fora: %{x:.1f}%<extra></extra>',
    },
  ], {
    barmode: 'stack',
    xaxis: { title: { text: '% de Partidas' }, range: [0, 100.5], ticksuffix: '%' },
    yaxis: { autorange: 'reversed', tickfont: { size: 12 } },
    margin: { t: 20, b: 75, l: 210, r: 30 },
    legend: { orientation: 'h', x: 0, y: -0.28 },
  });
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
  chartWorldMap(f);
  chartGoalsTime(f);
  chartRankTeams(f,'w', 'chart-top-wins',  '#f5c842','Vit\xf3rias');
  chartRankTeams(f,'gf','chart-top-gf',    '#2ecc71','Gols Marcados');
  chartRankTeams(f,'ga','chart-top-ga',    '#e74c3c','Gols Sofridos');
  chartRankTeams(f,'l', 'chart-top-losses','#9b59b6','Derrotas');
  chartCorrAnoGPM(f);
  chartCorrAttGPM(f);
  chartCorrGFWins(f);
  chartCorrStageGoals(f);
  renderHTStats(f);
  chartHTAnalysis(f);
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
