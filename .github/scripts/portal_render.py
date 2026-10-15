"""
Lógica compartida para el portal de artifacts de IAC.

Este archivo se usa de dos formas:
  1. Importado localmente por generate_portal.py (vía la API de GitHub).
  2. Copiado tal cual a .github/scripts/portal_render.py en el repo ORIGEN,
     donde lo importa el script de CI que corre en cada push (ver
     setup_cross_repo_sync.py).

Por eso no depende de nada más que la librería estándar de Python.

Este módulo expone DOS generadores de portal, pensados para dos archivos
de salida distintos (ver generate_index.py):

  - render_portal_html(...)       -> appindex/index.html (PRINCIPAL)
      Diseño original azul/índigo con iconos Lucide (CDN) y cuadrícula
      plana de tarjetas, sin agrupar por tema. Es la versión que se usa
      en producción / la que se enlaza en el README.

  - render_portal_html_temas(...) -> appindex/temas/index.html (ALTERNATIVO)
      Mismo catálogo de apps, pero agrupado en contenedores por tema (la
      carpeta de nivel superior de cada app: moda, telemetría, pdfs,
      consultar), con estilo "forja" (paleta y tipografía de la app
      ClarIA: Bricolage Grotesque + Instrument Sans + JetBrains Mono,
      tinta/acero/brasa/forjado) e iconos SVG propios embebidos (sin
      CDN). El filtro de categorías existente se mantiene intacto y
      sigue aplicándose de forma transversal a todos los contenedores.
      Es un punto de acceso adicional, no sustituye a la versión
      principal.
"""

import datetime
import html
import json
import re


def extract_app_metadata(html_text):
    """
    Busca la etiqueta <body ...> y extrae sus atributos data-app-title,
    data-app-description, data-categories, data-tags y data-client-only.
    Devuelve None si el archivo no tiene data-app-title (se ignora: no todo
    HTML en la carpeta tiene por qué ser una app catalogada).
    """
    m = re.search(r"<body\b([^>]*)>", html_text, re.IGNORECASE | re.DOTALL)
    if not m:
        return None
    attrs_blob = m.group(1)

    def get_attr(name):
        am = re.search(rf'{name}\s*=\s*"([^"]*)"', attrs_blob)
        return am.group(1) if am else None

    title = get_attr("data-app-title")
    if not title:
        return None
    title = html.unescape(title)

    description = html.unescape(get_attr("data-app-description") or "")
    categories = [c.strip() for c in html.unescape(get_attr("data-categories") or "").split(",") if c.strip()]
    tags = [html.unescape(t.strip()) for t in (get_attr("data-tags") or "").split(",") if t.strip()]
    client_only = (get_attr("data-client-only") or "").strip().lower() == "true"

    return {
        "title": title,
        "description": description,
        "categories": categories,
        "tags": tags,
        "client_only": client_only,
    }


_MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def _fecha_es(dt):
    # Convierte a hora de Madrid (CET/CEST) cuando hay datos de zona horaria
    # disponibles; si no (por ejemplo, un runner sin tzdata instalado), se
    # deja en UTC en vez de fallar o de aplicar un desfase fijo incorrecto
    # la mitad del año por el cambio de horario de verano.
    try:
        from zoneinfo import ZoneInfo
        dt = dt.astimezone(ZoneInfo("Europe/Madrid"))
    except Exception:
        pass
    return f"{dt.day} de {_MESES_ES[dt.month - 1]} de {dt.year}, {dt.hour:02d}:{dt.minute:02d}"


# ============================================================================
# VERSIÓN PRINCIPAL — appindex/index.html
# Diseño azul/índigo original, iconos Lucide vía CDN, cuadrícula plana.
# ============================================================================

# Catálogo de categorías conocidas: slug -> (etiqueta legible, icono de Lucide).
# Si aparece un slug nuevo que no esté aquí, se genera una etiqueta a partir
# del propio slug y se usa un icono genérico ("tag"), para que el sistema no
# se rompa cuando se añadan categorías nuevas en el futuro.
CATEGORY_INFO = {
    "ia": {"label": "Inteligencia Artificial", "icon": "brain-circuit"},
    "diseno-creatividad": {"label": "Diseño y creatividad", "icon": "palette"},
    "generacion-contenido": {"label": "Generación de contenido", "icon": "sparkles"},
    "docencia": {"label": "Docencia", "icon": "graduation-cap"},
    "automatizacion": {"label": "Automatización", "icon": "cog"},
    "evaluacion": {"label": "Evaluación", "icon": "clipboard-check"},
    "investigacion": {"label": "Investigación", "icon": "microscope"},
    "analisis-datos": {"label": "Análisis de datos", "icon": "bar-chart-3"},
    "programacion": {"label": "Programación", "icon": "code"},
    "productividad": {"label": "Productividad", "icon": "wrench"},
    "telemetria": {"label": "Telemetría", "icon": "radio-tower"},
}


def category_info(slug):
    if slug in CATEGORY_INFO:
        return CATEGORY_INFO[slug]
    label = slug.replace("-", " ").replace("_", " ").strip().title() or slug
    return {"label": label, "icon": "tag"}


PORTAL_TEMPLATE = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA2NCA2NCIgd2lkdGg9IjY0IiBoZWlnaHQ9IjY0Ij4KICA8ZGVmcz4KICAgIDxsaW5lYXJHcmFkaWVudCBpZD0iYmciIHgxPSIwIiB5MT0iMCIgeDI9IjEiIHkyPSIxIj4KICAgICAgPHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iIzRGNDZFNSIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiM3QzNBRUQiLz4KICAgIDwvbGluZWFyR3JhZGllbnQ+CiAgPC9kZWZzPgoKICA8IS0tIEZvbmRvIHJlZG9uZGVhZG8gLS0+CiAgPHJlY3QgeD0iMiIgeT0iMiIgd2lkdGg9IjYwIiBoZWlnaHQ9IjYwIiByeD0iMTQiIGZpbGw9InVybCgjYmcpIi8+CgogIDwhLS0gQmlycmV0ZSAoZ29ycm8gZGUgZ3JhZHVhY2nDs24pIC0tPgogIDxnIHRyYW5zZm9ybT0idHJhbnNsYXRlKDMyLDI1KSI+CiAgICA8cG9seWdvbiBwb2ludHM9IjAsLTkgMjIsLTEuNSAwLDYgLTIyLC0xLjUiIGZpbGw9IiNGRkZGRkYiLz4KICAgIDxwb2x5Z29uIHBvaW50cz0iMCwtOSAyMiwtMS41IDAsNiAtMjIsLTEuNSIgZmlsbD0iI0ZGRkZGRiIgb3BhY2l0eT0iMCIvPgogICAgPHBhdGggZD0iTSAtMTEgMyBMIC0xMSAxMiBDIC0xMSAxNiAxMSAxNiAxMSAxMiBMIDExIDMgTCAwIDcgWiIgZmlsbD0iI0UwRTdGRiIvPgogICAgPGxpbmUgeDE9IjE4IiB5MT0iLTIuNSIgeDI9IjE4IiB5Mj0iMTAiIHN0cm9rZT0iI0ZERTY4QSIgc3Ryb2tlLXdpZHRoPSIxLjYiLz4KICAgIDxjaXJjbGUgY3g9IjE4IiBjeT0iMTEuNSIgcj0iMi4xIiBmaWxsPSIjRkRFNjhBIi8+CiAgPC9nPgoKICA8IS0tIENoaXNwYSBkZSBJQSAtLT4KICA8ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSg0NiwxNikiIGZpbGw9IiNGREU2OEEiPgogICAgPHBhdGggZD0iTTAgLTcgTDIgLTEgTDggMCBMMiAxIEwwIDcgTC0yIDEgTC04IDAgTC0yIC0xIFoiLz4KICA8L2c+Cjwvc3ZnPgo=">
<script src="https://unpkg.com/lucide@latest"></script>
<style>
  :root {
    --blue-900:#0b2545; --blue-800:#123a6b; --blue-700:#1656a3; --blue-600:#1d6fd1;
    --blue-500:#3b82f6; --blue-100:#e5f0fd; --blue-50:#f4f9ff;
    --ink:#0f172a; --muted:#5b6b82; --border:#dde7f5; --card-bg:#ffffff;
    --bg:#f6f9fc; --radius:16px; --shadow:0 4px 22px rgba(15,45,90,0.07);
  }
  * { box-sizing: border-box; }
  body { margin:0; font-family: "Segoe UI", system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--ink); }
  .header { background: linear-gradient(135deg, var(--blue-900), var(--blue-700)); color:#fff; padding: 56px 24px 92px; }
  .header-inner { max-width: 1100px; margin: 0 auto; text-align: center; }
  .header-logo { margin: 0 auto 18px; display:block; filter: drop-shadow(0 4px 14px rgba(0,0,0,.18)); }
  .eyebrow { font-size: .85rem; letter-spacing:.03em; opacity:.85; margin-bottom: 14px; }
  .header h1 { font-size: 2.1rem; margin: 0 0 14px; font-weight: 700; }
  .header p.lede { max-width: 640px; margin: 0 auto 32px; opacity:.92; line-height:1.6; }
  .stats { display:flex; gap: 44px; flex-wrap:wrap; justify-content: center; }
  .stat-num { font-size: 2rem; font-weight: 700; }
  .stat-label { font-size:.82rem; opacity:.82; }
  .container { max-width: 1100px; margin: -60px auto 60px; padding: 0 24px; }
  .searchbar { background:#fff; border:1px solid var(--border); border-radius: 14px; box-shadow: var(--shadow); padding: 6px 6px 6px 18px; display:flex; align-items:center; gap:10px; }
  .searchbar input { flex:1; border:none; outline:none; font-size:1rem; padding: 12px 0; color: var(--ink); background: transparent; }
  .searchbar svg { color: var(--muted); flex-shrink:0; }
  .categories { display:flex; flex-wrap:wrap; gap: 10px; margin: 28px 0 8px; }
  .category-btn { display:flex; align-items:center; gap:8px; padding: 9px 16px; border-radius: 999px; border:1px solid var(--border); background:#fff; cursor:pointer; font-size:.9rem; color: var(--ink); transition: all .15s ease; }
  .category-btn:hover { border-color: var(--blue-500); color: var(--blue-700); }
  .category-btn.active { background: var(--blue-700); color:#fff; border-color: var(--blue-700); }
  .category-btn .count { background: rgba(15,45,90,.07); border-radius: 999px; padding: 1px 8px; font-size:.76rem; }
  .category-btn.active .count { background: rgba(255,255,255,.25); }
  .category-btn svg { width:16px; height:16px; }
  .results-line { color: var(--muted); font-size:.88rem; margin: 18px 0 14px; }
  .grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(270px, 1fr)); gap: 20px; }
  .card { background: var(--card-bg); border:1px solid var(--border); border-radius: var(--radius); padding: 22px; box-shadow: var(--shadow); display:flex; flex-direction:column; gap: 12px; transition: transform .15s ease, box-shadow .15s ease; }
  .card:hover { transform: translateY(-3px); box-shadow: 0 12px 32px rgba(15,45,90,.12); }
  .card-top { display:flex; align-items:center; gap:12px; }
  .card-icon { width:40px; height:40px; border-radius:10px; background: var(--blue-100); display:flex; align-items:center; justify-content:center; color: var(--blue-700); flex-shrink:0; }
  .card-icon svg { width:20px; height:20px; }
  .card h3 { margin:0; font-size:1.08rem; }
  .card p.desc { margin:0; color: var(--muted); font-size:.9rem; line-height:1.55; flex:1; }
  .badges { display:flex; flex-wrap:wrap; gap:6px; }
  .badge { font-size:.72rem; padding:3px 10px; border-radius:999px; background: var(--blue-50); color: var(--blue-700); border:1px solid var(--border); }
  .card a.open { margin-top:auto; text-decoration:none; background: var(--blue-700); color:#fff; text-align:center; padding: 11px; border-radius: 10px; font-size:.9rem; font-weight:600; transition: background .15s ease; }
  .card a.open:hover { background: var(--blue-800); }
  .empty-state { text-align:center; color: var(--muted); padding: 70px 0; }
  footer { text-align:center; color: var(--muted); font-size:.82rem; padding: 20px 24px 48px; }
  @media (max-width:640px) {
    .header { padding: 44px 18px 80px; }
    .header h1 { font-size: 1.6rem; }
    .stats { gap: 26px; }
    .container { margin-top: -50px; }
  }
</style>
</head>
<body>
  <header class="header">
    <div class="header-inner">
      <svg class="header-logo" width="96" height="96" viewBox="0 0 120 120" aria-hidden="true">
        <defs>
          <linearGradient id="hiadCapGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#ffffff"/>
            <stop offset="100%" stop-color="#E0E7FF"/>
          </linearGradient>
        </defs>
        <circle cx="60" cy="60" r="56" fill="rgba(255,255,255,0.10)" stroke="rgba(255,255,255,0.32)" stroke-width="2"/>
        <path d="M 38 66 L 38 80 C 38 88 82 88 82 80 L 82 66 L 60 76 Z" fill="#E0E7FF"/>
        <line x1="94" y1="48" x2="94" y2="72" stroke="#FDE68A" stroke-width="2.4"/>
        <circle cx="94" cy="75" r="4" fill="#FDE68A"/>
        <polygon points="60,34 100,50 60,66 20,50" fill="url(#hiadCapGrad)"/>
        <g stroke="#4F46E5" stroke-width="1.6" stroke-linecap="round" fill="none" opacity="0.85">
          <path d="M38 50 L50 50 L54 44 L60 50 L66 44 L70 50 L82 50"/>
          <path d="M50 50 L50 56 L44 60"/>
          <path d="M70 50 L70 56 L76 60"/>
          <path d="M60 50 L60 58"/>
        </g>
        <g fill="#4F46E5">
          <circle cx="38" cy="50" r="2.1"/>
          <circle cx="82" cy="50" r="2.1"/>
          <circle cx="54" cy="44" r="1.8"/>
          <circle cx="66" cy="44" r="1.8"/>
          <circle cx="44" cy="60" r="1.8"/>
          <circle cx="76" cy="60" r="1.8"/>
          <circle cx="60" cy="58" r="2.1"/>
        </g>
        <g transform="translate(92,30)" fill="#FDE68A">
          <path d="M0 -9 L2.4 -1.6 L10 0 L2.4 1.6 L0 9 L-2.4 1.6 L-10 0 L-2.4 -1.6 Z"/>
        </g>
      </svg>
      <div class="eyebrow">__EYEBROW__</div>
      <h1>__TITLE__</h1>
      <p class="lede">__SUBTITLE__</p>
      <div class="stats">
        <div><div class="stat-num">__STAT_TOTAL__</div><div class="stat-label">Herramientas</div></div>
        <div><div class="stat-num">__STAT_CATEGORIES__</div><div class="stat-label">Categorías</div></div>
        <div><div class="stat-num">__STAT_PCT__</div><div class="stat-label">__STAT_PCT_LABEL__</div></div>
      </div>
    </div>
  </header>

  <div class="container">
    <div class="searchbar">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
      <input id="search" type="text" placeholder="Buscar por nombre, descripción, categoría o etiqueta...">
    </div>

    <div id="categories" class="categories"></div>
    <div id="results-line" class="results-line"></div>
    <div id="grid" class="grid"></div>
    <div id="empty" class="empty-state" style="display:none;">No se encontraron aplicaciones con ese criterio.</div>
  </div>

  <footer>
    Generado automáticamente a partir de las aplicaciones publicadas.<br>
    __CONTACT_NAME__ (<a href="mailto:__CONTACT_EMAIL__">__CONTACT_EMAIL__</a>) · Última actualización: __LAST_UPDATED__
  </footer>

<script id="catalog-data" type="application/json">__CATALOG_JSON__</script>
<script id="category-meta" type="application/json">__CATEGORY_META_JSON__</script>
<script>
  const CATALOG = JSON.parse(document.getElementById('catalog-data').textContent);
  const CATEGORY_META = JSON.parse(document.getElementById('category-meta').textContent);

  let activeCategory = 'all';
  let query = '';

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  function matches(app) {
    const inCategory = activeCategory === 'all' || app.categories.includes(activeCategory);
    if (!inCategory) return false;
    if (!query) return true;
    const haystack = [
      app.title, app.description,
      ...app.categories.map(c => (CATEGORY_META[c] || {}).label || c),
      ...app.tags,
    ].join(' ').toLowerCase();
    return haystack.includes(query);
  }

  function renderCategories() {
    const counts = {};
    CATALOG.forEach(app => app.categories.forEach(c => { counts[c] = (counts[c] || 0) + 1; }));
    const slugs = Object.keys(counts).sort((a, b) =>
      ((CATEGORY_META[a] || {}).label || a).localeCompare((CATEGORY_META[b] || {}).label || b)
    );

    const allBtn = `<button class="category-btn ${activeCategory === 'all' ? 'active' : ''}" data-cat="all">
        <i data-lucide="layout-grid"></i> Todas <span class="count">${CATALOG.length}</span>
      </button>`;

    const buttons = slugs.map(slug => {
      const meta = CATEGORY_META[slug] || { label: slug, icon: 'tag' };
      const active = activeCategory === slug ? 'active' : '';
      return `<button class="category-btn ${active}" data-cat="${slug}">
          <i data-lucide="${meta.icon}"></i> ${escapeHtml(meta.label)} <span class="count">${counts[slug]}</span>
        </button>`;
    }).join('');

    document.getElementById('categories').innerHTML = allBtn + buttons;
    document.querySelectorAll('.category-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        activeCategory = btn.dataset.cat;
        renderAll();
      });
    });
  }

  function renderGrid() {
    const filtered = CATALOG.filter(matches);
    const grid = document.getElementById('grid');
    const empty = document.getElementById('empty');
    const resultsLine = document.getElementById('results-line');

    resultsLine.textContent = filtered.length === CATALOG.length
      ? `${CATALOG.length} herramienta${CATALOG.length === 1 ? '' : 's'} disponible${CATALOG.length === 1 ? '' : 's'}`
      : `${filtered.length} resultado${filtered.length === 1 ? '' : 's'}`;

    if (filtered.length === 0) {
      grid.style.display = 'none';
      empty.style.display = 'block';
      return;
    }
    grid.style.display = 'grid';
    empty.style.display = 'none';

    grid.innerHTML = filtered.map(app => {
      const primaryCat = app.categories[0];
      const meta = CATEGORY_META[primaryCat] || { label: primaryCat, icon: 'sparkles' };
      const badges = app.categories.map(c => {
        const m = CATEGORY_META[c] || { label: c };
        return `<span class="badge">${escapeHtml(m.label)}</span>`;
      }).join('');
      return `<div class="card">
          <div class="card-top">
            <div class="card-icon"><i data-lucide="${meta.icon}"></i></div>
            <h3>${escapeHtml(app.title)}</h3>
          </div>
          <p class="desc">${escapeHtml(app.description)}</p>
          <div class="badges">${badges}</div>
          <a class="open" href="${app.url}" target="_blank" rel="noopener">Abrir aplicación</a>
        </div>`;
    }).join('');
  }

  function renderAll() {
    renderCategories();
    renderGrid();
    if (window.lucide) lucide.createIcons();
  }

  document.getElementById('search').addEventListener('input', (e) => {
    query = e.target.value.trim().toLowerCase();
    renderAll();
  });

  renderAll();
</script>
</body>
</html>
"""


def render_portal_html(catalog, title, subtitle, eyebrow, contact_name="", contact_email=""):
    """
    catalog: lista de dicts {title, description, categories, tags, client_only, url}
    Devuelve el HTML completo del portal (versión principal) como string.
    """
    total = len(catalog)
    all_categories = sorted({c for app in catalog for c in app["categories"]})
    category_meta = {slug: category_info(slug) for slug in all_categories}

    client_only_count = sum(1 for app in catalog if app.get("client_only"))
    if total > 0 and client_only_count == total:
        stat_pct = "100%"
        stat_pct_label = "En el navegador"
    elif total > 0:
        stat_pct = f"{round(100 * client_only_count / total)}%"
        stat_pct_label = "En el navegador"
    else:
        stat_pct = "0"
        stat_pct_label = "Herramientas sin backend"

    out = PORTAL_TEMPLATE
    out = out.replace("__TITLE__", html.escape(title))
    out = out.replace("__SUBTITLE__", html.escape(subtitle))
    out = out.replace("__EYEBROW__", html.escape(eyebrow))
    out = out.replace("__STAT_TOTAL__", str(total))
    out = out.replace("__STAT_CATEGORIES__", str(len(all_categories)))
    out = out.replace("__STAT_PCT_LABEL__", stat_pct_label)
    out = out.replace("__STAT_PCT__", stat_pct)
    out = out.replace("__CATALOG_JSON__", json.dumps(catalog, ensure_ascii=False))
    out = out.replace("__CATEGORY_META_JSON__", json.dumps(category_meta, ensure_ascii=False))
    out = out.replace("__CONTACT_NAME__", html.escape(contact_name))
    out = out.replace("__CONTACT_EMAIL__", html.escape(contact_email))
    out = out.replace("__LAST_UPDATED__", _fecha_es(datetime.datetime.now(datetime.timezone.utc)))
    return out


# ============================================================================
# VERSIÓN ALTERNATIVA — appindex/temas/index.html
# Agrupada en contenedores por tema (carpeta raíz de cada app), estilo
# "forja" (ClarIA), iconos SVG propios embebidos (sin CDN).
# ============================================================================

# Catálogo de categorías para esta versión: mismos slugs/etiquetas que
# CATEGORY_INFO, pero el icono referencia un <symbol id="i-<icon>"> del
# sprite SVG propio (ICON_SPRITE más abajo) en vez de un nombre de Lucide.
CATEGORY_INFO_TEMAS = {
    "ia": {"label": "Inteligencia Artificial", "icon": "cpu"},
    "diseno-creatividad": {"label": "Diseño y creatividad", "icon": "palette"},
    "generacion-contenido": {"label": "Generación de contenido", "icon": "sparkles"},
    "docencia": {"label": "Docencia", "icon": "cap"},
    "automatizacion": {"label": "Automatización", "icon": "cog"},
    "evaluacion": {"label": "Evaluación", "icon": "clipcheck"},
    "investigacion": {"label": "Investigación", "icon": "flask"},
    "analisis-datos": {"label": "Análisis de datos", "icon": "barchart"},
    "programacion": {"label": "Programación", "icon": "code"},
    "productividad": {"label": "Productividad", "icon": "wrench"},
    "telemetria": {"label": "Telemetría", "icon": "radio"},
}


def category_info_temas(slug):
    if slug in CATEGORY_INFO_TEMAS:
        return CATEGORY_INFO_TEMAS[slug]
    label = slug.replace("-", " ").replace("_", " ").strip().title() or slug
    return {"label": label, "icon": "tag"}


# Catálogo de "temas" (contenedores): slug de la carpeta de nivel superior
# -> etiqueta, icono, color de acento (uno de los tonos de categoría de
# ClarIA) y una línea de contexto. Un tema nuevo que no esté aquí recibe una
# etiqueta derivada del slug, el icono genérico y el tono de acero, para que
# el portal no se rompa al añadir una carpeta de apps nueva.
THEME_INFO = {
    "moda": {
        "label": "Moda",
        "icon": "shirt",
        "color": "#6B4FD8",
        "lede": "Generación de imágenes y patrones de moda, e investigación de logística del sector, con IA generativa.",
    },
    "telemetria": {
        "label": "Telemetría",
        "icon": "radio",
        "color": "#0E8C7A",
        "lede": "Monitorización en vivo de una estación meteorológica personal: sondeo continuo, histórico y paneles instalables.",
    },
    "pdfs": {
        "label": "Evaluación de PDF",
        "icon": "doc",
        "color": "#C98200",
        "lede": "Detección de indicios de uso de IA en documentos PDF entregados por el alumnado.",
    },
    "consultar": {
        "label": "General",
        "icon": "chat",
        "color": "#1F6FB2",
        "lede": "Consulta asistida por IA de uso general.",
    },
}

# Orden fijo en el que se muestran los contenedores de tema cuando existen;
# cualquier tema nuevo que no esté en esta lista se añade al final, por
# orden alfabético de su etiqueta.
THEME_ORDER = ["moda", "telemetria", "pdfs", "consultar"]


def theme_info(slug):
    if slug in THEME_INFO:
        return THEME_INFO[slug]
    label = slug.replace("-", " ").replace("_", " ").strip().title() or slug
    return {"label": label, "icon": "tag", "color": "#2E4B6B", "lede": ""}


# Sprite de iconos en línea (sin dependencias externas), estilo trazo
# Feather/Lucide: viewBox 24x24, stroke-width 2, extremos redondeados. Cubre
# todas las categorías e iconos de tema conocidos, más unos pocos de uso
# general (buscar, cerrar, enlace externo, cuadrícula "Todas").
ICON_SPRITE = """<svg style="display:none" aria-hidden="true">
<symbol id="i-anvil" viewBox="0 0 24 24"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path></symbol>
<symbol id="i-grid" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1.5"></rect><rect x="14" y="3" width="7" height="7" rx="1.5"></rect><rect x="3" y="14" width="7" height="7" rx="1.5"></rect><rect x="14" y="14" width="7" height="7" rx="1.5"></rect></symbol>
<symbol id="i-search" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.3-4.3"></path></symbol>
<symbol id="i-ext" viewBox="0 0 24 24"><path d="M15 3h6v6M10 14 21 3M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path></symbol>
<symbol id="i-tag" viewBox="0 0 24 24"><path d="M20.59 13.41 13.42 20.6a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82Z"></path><circle cx="7" cy="7" r="1.3"></circle></symbol>
<symbol id="i-cpu" viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="2"></rect><rect x="9" y="9" width="6" height="6"></rect><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3"></path></symbol>
<symbol id="i-palette" viewBox="0 0 24 24"><path d="M12 22a10 10 0 1 1 0-20 8 8 0 0 1 0 16h-1.5a1.5 1.5 0 0 0-1 2.6c.3.3.5.7.5 1.1a1.3 1.3 0 0 1-1.3 1.3Z"></path><circle cx="6.5" cy="11.5" r="1.3"></circle><circle cx="9.5" cy="7.5" r="1.3"></circle><circle cx="14.5" cy="7.5" r="1.3"></circle><circle cx="17.5" cy="11.5" r="1.3"></circle></symbol>
<symbol id="i-sparkles" viewBox="0 0 24 24"><path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"></path><path d="M19 3v4M17 5h4M5 17v4M3 19h4"></path></symbol>
<symbol id="i-cap" viewBox="0 0 24 24"><path d="M22 10 12 5 2 10l10 5 10-5Z"></path><path d="M6 12.5V17c0 1.5 2.7 3 6 3s6-1.5 6-3v-4.5"></path><path d="M22 10v6"></path></symbol>
<symbol id="i-cog" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 13a7.6 7.6 0 0 0 0-2l2-1.5-2-3.5-2.3.9a7.6 7.6 0 0 0-1.7-1l-.4-2.4h-4l-.4 2.4a7.6 7.6 0 0 0-1.7 1l-2.3-.9-2 3.5 2 1.5a7.6 7.6 0 0 0 0 2l-2 1.5 2 3.5 2.3-.9a7.6 7.6 0 0 0 1.7 1l.4 2.4h4l.4-2.4a7.6 7.6 0 0 0 1.7-1l2.3.9 2-3.5-2-1.5Z"></path></symbol>
<symbol id="i-clipcheck" viewBox="0 0 24 24"><rect x="6" y="4" width="12" height="18" rx="2"></rect><path d="M9 4V2.6A1.6 1.6 0 0 1 10.6 1h2.8A1.6 1.6 0 0 1 15 2.6V4"></path><path d="m9.5 13.5 2 2 4-4.5"></path></symbol>
<symbol id="i-flask" viewBox="0 0 24 24"><path d="M9 2h6M10 2v6.3L4.6 18a2 2 0 0 0 1.7 3h11.4a2 2 0 0 0 1.7-3L14 8.3V2"></path></symbol>
<symbol id="i-barchart" viewBox="0 0 24 24"><path d="M3 3v18h18"></path><rect x="7" y="13" width="3" height="5"></rect><rect x="12" y="9" width="3" height="9"></rect><rect x="17" y="5" width="3" height="13"></rect></symbol>
<symbol id="i-code" viewBox="0 0 24 24"><path d="m16 18 6-6-6-6"></path><path d="m8 6-6 6 6 6"></path></symbol>
<symbol id="i-wrench" viewBox="0 0 24 24"><path d="M14.7 6.3a4 4 0 0 0-5.1 5.1L2 19l3 3 7.6-7.6a4 4 0 0 0 5.1-5.1l-2.8 2.8-2-2Z"></path></symbol>
<symbol id="i-radio" viewBox="0 0 24 24"><path d="M12 2v4"></path><path d="M8.5 5.5a6 6 0 0 1 7 0"></path><path d="M6 8a9 9 0 0 1 12 0"></path><circle cx="12" cy="12" r="2"></circle><path d="m12 14-3 8h6l-3-8Z"></path></symbol>
<symbol id="i-shirt" viewBox="0 0 24 24"><path d="M16 3 12 6 8 3 2 7l3 4 2-1v9a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1v-9l2 1 3-4Z"></path></symbol>
<symbol id="i-doc" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"></path></symbol>
<symbol id="i-chat" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path><path d="M8 9h8M8 13h5"></path></symbol>
<symbol id="i-github" viewBox="0 0 24 24"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></symbol>
</svg>"""


PORTAL_TEMPLATE_TEMAS = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__</title>
<meta name="theme-color" content="#0F2237">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0' y1='0' x2='1' y2='1'%3E%3Cstop offset='0' stop-color='%23E4572E'/%3E%3Cstop offset='1' stop-color='%230E7C6B'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='32' height='32' rx='8' fill='%230F2237'/%3E%3Crect x='4' y='4' width='24' height='24' rx='6' fill='url(%23g)'/%3E%3Cpath d='M20 9 11 14l9 5 9-5Z' fill='none' stroke='white' stroke-width='1.6' stroke-linejoin='round'/%3E%3Cpath d='M14 16v4c0 1.3 2.7 2.3 6 2.3s6-1 6-2.3v-4' fill='none' stroke='white' stroke-width='1.6'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=Instrument+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --tinta:#0F2237; --acero:#2E4B6B; --acero-claro:#7C93AC; --gris:#5D7691;
  --papel:#F3F6FA; --blanco:#FFFFFF; --linea:#D8E0E9; --linea-2:#E8EEF4;
  --brasa:#E4572E; --brasa-osc:#C9441F; --brasa-suave:#FDEBE4;
  --forjado:#0E7C6B; --forjado-suave:#E0F3EE; --aviso:#8A3617;
  --sombra:0 1px 0 rgba(15,34,55,.05), 0 14px 34px -22px rgba(15,34,55,.45);
  --sombra-alta:0 2px 0 rgba(15,34,55,.04), 0 22px 50px -24px rgba(15,34,55,.55);
  --r:14px;
  --display:"Bricolage Grotesque",Georgia,serif;
  --texto:"Instrument Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
  --mono:"JetBrains Mono",ui-monospace,monospace;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{background:var(--papel);color:var(--tinta);font-family:var(--texto);font-size:16px;line-height:1.55;-webkit-font-smoothing:antialiased}
a{color:var(--acero)}
:focus-visible{outline:3px solid var(--brasa);outline-offset:2px;border-radius:6px}
svg.i{width:1.15em;height:1.15em;vertical-align:-.2em;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex:none}

.topbar{position:sticky;top:0;z-index:40;background:var(--tinta);color:#EAF1F7;box-shadow:0 6px 24px -14px rgba(0,0,0,.6)}
.tb-in{max-width:1180px;margin:0 auto;padding:12px 16px;display:flex;align-items:center;gap:14px}
.logo{background:none;border:0;color:#fff;font-family:var(--display);font-weight:800;font-size:21px;letter-spacing:-.02em;display:flex;align-items:center;gap:10px}
.logo .anv{width:32px;height:32px;border-radius:9px;background:linear-gradient(135deg,var(--brasa),var(--forjado));display:grid;place-items:center;color:#fff;flex:none}
.logo em{font-style:normal;color:var(--brasa)}
.tb-sub{flex:1;min-width:0;font-size:12.5px;color:#8FA7BE;font-family:var(--mono)}
.tb-btn{background:transparent;border:1px solid #3E5C7D;color:#C9D8E6;border-radius:9px;padding:7px 12px;font:600 13px var(--texto);cursor:pointer;display:flex;align-items:center;gap:6px;text-decoration:none}
.tb-btn:hover{border-color:var(--brasa);color:#fff}
@media(max-width:600px){.tb-sub{display:none}}

main{max-width:1180px;margin:0 auto;padding:26px 16px 50px}

.hero{background:var(--tinta);color:#EAF1F7;border-radius:22px;padding:44px 40px;position:relative;overflow:hidden;margin-bottom:0;box-shadow:var(--sombra-alta);text-align:center}
.hero::before{content:"";position:absolute;right:-80px;top:-80px;width:360px;height:360px;border-radius:50%;background:radial-gradient(circle,rgba(228,87,46,.5),transparent 65%)}
.hero::after{content:"";position:absolute;left:30%;bottom:-140px;width:420px;height:280px;border-radius:50%;background:radial-gradient(circle,rgba(14,140,122,.32),transparent 65%)}
.hero>*{position:relative;z-index:1}
@media(max-width:600px){.hero{padding:30px 22px;border-radius:18px}}
.eyebrow{font:600 11.5px var(--mono);letter-spacing:.16em;text-transform:uppercase;color:#8FA7BE;margin:0 0 14px}
.hero h1{font-family:var(--display);font-weight:800;font-size:clamp(30px,4.6vw,46px);line-height:1.04;letter-spacing:-.03em;margin:0 auto 16px;max-width:22ch}
.hero h1 em{font-style:normal;color:var(--brasa)}
.hero p.lede{max-width:62ch;font-size:17px;color:#C3D3E2;margin:0 auto 26px}
.draft{display:inline-flex;gap:22px;flex-wrap:wrap;justify-content:center;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);border-radius:14px;padding:14px 26px}
.draft .stat{text-align:center}
.draft .stat b{display:block;font:800 26px var(--display);letter-spacing:-.02em;color:#fff}
.draft .stat span{display:block;font:600 11px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:#A9C0D4;margin-top:2px}

.searchwrap{background:var(--blanco);border:1px solid var(--linea);border-radius:16px;box-shadow:var(--sombra-alta);padding:5px 5px 5px 18px;display:flex;align-items:center;gap:10px;margin:-26px auto 0;max-width:680px;position:relative;z-index:2}
.searchwrap svg{color:var(--gris);flex:none}
.searchwrap input{flex:1;border:none;outline:none;font:16px var(--texto);padding:13px 0;color:var(--tinta);background:transparent}
.searchwrap input::placeholder{color:#9DB0C2}

.chips{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:26px 0 6px}
.chip{background:#fff;border:1.5px solid var(--linea);border-radius:999px;padding:8px 15px;font-size:13.5px;font-weight:600;color:var(--acero);cursor:pointer;display:inline-flex;align-items:center;gap:7px;line-height:1.25}
.chip:hover{border-color:var(--acero-claro)}
.chip[aria-pressed="true"]{background:var(--tinta);border-color:var(--tinta);color:#fff}
.chip .count{background:rgba(15,34,55,.08);border-radius:999px;padding:1px 8px;font-size:11.5px}
.chip[aria-pressed="true"] .count{background:rgba(255,255,255,.22)}

.results-line{text-align:center;color:var(--gris);font-size:13.5px;margin:16px 0 30px}

.theme-block{margin-bottom:40px}
.theme-block.is-hidden{display:none}
.sh{display:flex;gap:16px;align-items:flex-start;margin:4px 0 18px}
.sh-ico{width:52px;height:52px;border-radius:15px;background:var(--c,var(--brasa));color:#fff;display:grid;place-items:center;flex:none;box-shadow:0 12px 24px -14px var(--c,var(--brasa))}
.sh-ico svg{width:26px;height:26px}
.sh-step{font:600 11.5px var(--mono);letter-spacing:.12em;text-transform:uppercase;color:var(--acero-claro);margin:2px 0}
.sh h2{font-family:var(--display);font-weight:800;font-size:clamp(21px,2.6vw,28px);letter-spacing:-.02em;line-height:1.1;margin:0 0 5px}
.sh-lede{margin:0;color:var(--gris);font-size:15px;max-width:72ch}
@media(max-width:600px){.sh-ico{width:42px;height:42px;border-radius:12px}.sh-ico svg{width:21px;height:21px}}

.app-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:16px}
.app-card{background:var(--blanco);border:1px solid var(--linea);border-radius:var(--r);box-shadow:var(--sombra);padding:20px;display:flex;flex-direction:column;gap:12px;transition:transform .15s ease,box-shadow .15s ease}
.app-card:hover{transform:translateY(-3px);box-shadow:var(--sombra-alta)}
.app-card-top{display:flex;align-items:center;gap:12px}
.app-icon{width:40px;height:40px;border-radius:11px;background:var(--papel);color:var(--acero);display:grid;place-items:center;flex:none}
.app-icon svg{width:19px;height:19px}
.app-card h3{font-family:var(--display);font-weight:700;font-size:16.5px;margin:0;letter-spacing:-.01em;line-height:1.3}
.app-card p.desc{margin:0;color:var(--gris);font-size:13.5px;line-height:1.55;flex:1}
.app-badges{display:flex;flex-wrap:wrap;gap:6px}
.app-badge{font-size:11.3px;font-weight:600;padding:3px 10px;border-radius:999px;background:var(--linea-2);color:var(--acero)}
.app-open{margin-top:auto;text-decoration:none;display:flex;align-items:center;justify-content:center;gap:7px;background:var(--brasa);color:#fff;text-align:center;padding:11px;border-radius:11px;font-size:14px;font-weight:700;box-shadow:0 8px 18px -10px var(--brasa);transition:background .15s ease}
.app-open:hover{background:var(--brasa-osc)}
.app-open svg{width:15px;height:15px}

.empty-state{text-align:center;color:var(--gris);padding:70px 10px;font-size:15px}

footer{max-width:1180px;margin:10px auto 0;padding:0 16px 40px;font-size:13px;color:#6E8299}
footer hr{border:0;border-top:1px solid var(--linea);margin:0 0 16px}
</style>
</head>
<body>
__ICON_SPRITE__

<div class="topbar">
  <div class="tb-in">
    <span class="logo"><span class="anv"><svg class="i"><use href="#i-anvil"></use></svg></span><span>HIAD</span></span>
    <span class="tb-sub">__EYEBROW__ · agrupado por tema</span>
    <a class="tb-btn" href="https://github.com/RafaUMH2110/apps" target="_blank" rel="noopener"><svg class="i"><use href="#i-github"></use></svg><span>GitHub</span></a>
  </div>
</div>

<main>
  <div class="hero">
    <p class="eyebrow">Catálogo de aplicaciones · versión agrupada por tema</p>
    <h1>Herramientas de IA <em>para la Docencia</em></h1>
    <p class="lede">__SUBTITLE__</p>
    <div class="draft">
      <div class="stat"><b>__STAT_TOTAL__</b><span>Herramientas</span></div>
      <div class="stat"><b>__STAT_THEMES__</b><span>Temas</span></div>
      <div class="stat"><b>__STAT_CATEGORIES__</b><span>Categorías</span></div>
      <div class="stat"><b>__STAT_PCT__</b><span>__STAT_PCT_LABEL__</span></div>
    </div>
  </div>

  <div class="searchwrap">
    <svg class="i"><use href="#i-search"></use></svg>
    <input id="search" type="text" placeholder="Buscar por nombre, descripción, categoría o etiqueta...">
  </div>

  <div id="categories" class="chips"></div>
  <div id="results-line" class="results-line"></div>
  <div id="groups"></div>
  <div id="empty" class="empty-state" style="display:none;">No se encontraron aplicaciones con ese criterio.</div>
</main>

<footer>
  <hr>
  <p>Generado automáticamente a partir de las aplicaciones publicadas en este repositorio, agrupadas por tema. También disponible en su <a href="../">versión principal</a>.<br>
  __CONTACT_NAME__ (<a href="mailto:__CONTACT_EMAIL__">__CONTACT_EMAIL__</a>) · Última actualización: __LAST_UPDATED__</p>
</footer>

<script id="catalog-data" type="application/json">__CATALOG_JSON__</script>
<script id="category-meta" type="application/json">__CATEGORY_META_JSON__</script>
<script id="theme-meta" type="application/json">__THEME_META_JSON__</script>
<script id="theme-order" type="application/json">__THEME_ORDER_JSON__</script>
<script>
  const CATALOG = JSON.parse(document.getElementById('catalog-data').textContent);
  const CATEGORY_META = JSON.parse(document.getElementById('category-meta').textContent);
  const THEME_META = JSON.parse(document.getElementById('theme-meta').textContent);
  const THEME_ORDER = JSON.parse(document.getElementById('theme-order').textContent);

  let activeCategory = 'all';
  let query = '';

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  function matches(app) {
    const inCategory = activeCategory === 'all' || app.categories.includes(activeCategory);
    if (!inCategory) return false;
    if (!query) return true;
    const haystack = [
      app.title, app.description,
      ...app.categories.map(c => (CATEGORY_META[c] || {}).label || c),
      ...app.tags,
    ].join(' ').toLowerCase();
    return haystack.includes(query);
  }

  function iconSymbol(name) {
    return '<svg class="i"><use href="#i-' + name + '"></use></svg>';
  }

  function renderCategories() {
    const counts = {};
    CATALOG.forEach(app => app.categories.forEach(c => { counts[c] = (counts[c] || 0) + 1; }));
    const slugs = Object.keys(counts).sort((a, b) =>
      ((CATEGORY_META[a] || {}).label || a).localeCompare((CATEGORY_META[b] || {}).label || b)
    );

    const allBtn = `<button class="chip" aria-pressed="${activeCategory === 'all'}" data-cat="all">
        ${iconSymbol('grid')} Todas <span class="count">${CATALOG.length}</span>
      </button>`;

    const buttons = slugs.map(slug => {
      const meta = CATEGORY_META[slug] || { label: slug, icon: 'tag' };
      return `<button class="chip" aria-pressed="${activeCategory === slug}" data-cat="${slug}">
          ${iconSymbol(meta.icon)} ${escapeHtml(meta.label)} <span class="count">${counts[slug]}</span>
        </button>`;
    }).join('');

    document.getElementById('categories').innerHTML = allBtn + buttons;
    document.querySelectorAll('.chip').forEach(btn => {
      btn.addEventListener('click', () => {
        activeCategory = btn.dataset.cat;
        renderAll();
      });
    });
  }

  function appCardHtml(app) {
    const primaryCat = app.categories[0];
    const meta = CATEGORY_META[primaryCat] || { label: primaryCat, icon: 'tag' };
    const badges = app.categories.map(c => {
      const m = CATEGORY_META[c] || { label: c };
      return `<span class="app-badge">${escapeHtml(m.label)}</span>`;
    }).join('');
    return `<div class="app-card">
        <div class="app-card-top">
          <div class="app-icon">${iconSymbol(meta.icon)}</div>
          <h3>${escapeHtml(app.title)}</h3>
        </div>
        <p class="desc">${escapeHtml(app.description)}</p>
        <div class="app-badges">${badges}</div>
        <a class="app-open" href="${app.url}" target="_blank" rel="noopener">Abrir aplicación ${iconSymbol('ext')}</a>
      </div>`;
  }

  function renderGroups() {
    const groups = document.getElementById('groups');
    let totalFiltered = 0;
    let html = '';

    THEME_ORDER.forEach(slug => {
      const apps = CATALOG.filter(app => app.group === slug && matches(app));
      if (apps.length === 0) return;
      totalFiltered += apps.length;
      const meta = THEME_META[slug] || { label: slug, icon: 'tag', color: '#2E4B6B', lede: '' };
      html += `<section class="theme-block">
          <header class="sh" style="--c:${meta.color}">
            <div class="sh-ico">${iconSymbol(meta.icon)}</div>
            <div>
              <p class="sh-step">Tema · ${apps.length} herramienta${apps.length === 1 ? '' : 's'}</p>
              <h2>${escapeHtml(meta.label)}</h2>
              ${meta.lede ? `<p class="sh-lede">${escapeHtml(meta.lede)}</p>` : ''}
            </div>
          </header>
          <div class="app-grid">${apps.map(appCardHtml).join('')}</div>
        </section>`;
    });

    groups.innerHTML = html;

    const resultsLine = document.getElementById('results-line');
    const empty = document.getElementById('empty');
    resultsLine.style.display = totalFiltered === 0 ? 'none' : 'block';
    resultsLine.textContent = totalFiltered === CATALOG.length
      ? `${CATALOG.length} herramienta${CATALOG.length === 1 ? '' : 's'} disponible${CATALOG.length === 1 ? '' : 's'} en ${THEME_ORDER.length} tema${THEME_ORDER.length === 1 ? '' : 's'}`
      : `${totalFiltered} resultado${totalFiltered === 1 ? '' : 's'}`;
    empty.style.display = totalFiltered === 0 ? 'block' : 'none';
  }

  function renderAll() {
    renderCategories();
    renderGroups();
  }

  document.getElementById('search').addEventListener('input', (e) => {
    query = e.target.value.trim().toLowerCase();
    renderAll();
  });

  renderAll();
</script>
</body>
</html>
"""


def _theme_order_for(catalog):
    """Orden de los contenedores de tema: THEME_ORDER primero (solo los que
    de verdad tienen apps), seguido de cualquier tema nuevo no contemplado
    en THEME_ORDER, por orden alfabético de su etiqueta."""
    present = {app["group"] for app in catalog if app.get("group")}
    ordered = [slug for slug in THEME_ORDER if slug in present]
    extra = sorted(
        (slug for slug in present if slug not in THEME_ORDER),
        key=lambda slug: theme_info(slug)["label"].casefold(),
    )
    return ordered + extra


def render_portal_html_temas(catalog, title, subtitle, eyebrow, contact_name="", contact_email=""):
    """
    catalog: lista de dicts {title, description, categories, tags,
    client_only, url, group} (group = carpeta de nivel superior de la app,
    usada para agrupar en contenedores por tema).
    Devuelve el HTML completo del portal (versión agrupada por tema), como
    string. Punto de acceso alternativo a render_portal_html(), no la
    versión principal.
    """
    total = len(catalog)
    all_categories = sorted({c for app in catalog for c in app["categories"]})
    category_meta = {slug: category_info_temas(slug) for slug in all_categories}

    theme_order = _theme_order_for(catalog)
    theme_meta = {slug: theme_info(slug) for slug in theme_order}

    client_only_count = sum(1 for app in catalog if app.get("client_only"))
    if total > 0 and client_only_count == total:
        stat_pct = "100%"
        stat_pct_label = "En el navegador"
    elif total > 0:
        stat_pct = f"{round(100 * client_only_count / total)}%"
        stat_pct_label = "En el navegador"
    else:
        stat_pct = "0"
        stat_pct_label = "Herramientas sin backend"

    out = PORTAL_TEMPLATE_TEMAS
    out = out.replace("__TITLE__", html.escape(title))
    out = out.replace("__SUBTITLE__", html.escape(subtitle))
    out = out.replace("__EYEBROW__", html.escape(eyebrow))
    out = out.replace("__STAT_TOTAL__", str(total))
    out = out.replace("__STAT_THEMES__", str(len(theme_order)))
    out = out.replace("__STAT_CATEGORIES__", str(len(all_categories)))
    out = out.replace("__STAT_PCT_LABEL__", stat_pct_label)
    out = out.replace("__STAT_PCT__", stat_pct)
    out = out.replace("__CATALOG_JSON__", json.dumps(catalog, ensure_ascii=False))
    out = out.replace("__CATEGORY_META_JSON__", json.dumps(category_meta, ensure_ascii=False))
    out = out.replace("__THEME_META_JSON__", json.dumps(theme_meta, ensure_ascii=False))
    out = out.replace("__THEME_ORDER_JSON__", json.dumps(theme_order, ensure_ascii=False))
    out = out.replace("__CONTACT_NAME__", html.escape(contact_name))
    out = out.replace("__CONTACT_EMAIL__", html.escape(contact_email))
    out = out.replace("__LAST_UPDATED__", _fecha_es(datetime.datetime.now(datetime.timezone.utc)))
    out = out.replace("__ICON_SPRITE__", ICON_SPRITE)
    return out
