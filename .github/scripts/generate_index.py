#!/usr/bin/env python3
"""Regenera appindex/index.html (el portal) a partir del checkout local de
este mismo repo, usando portal_render.py (misma carpeta). Recorre cada
carpeta de app en la raíz del repo (excluyendo appindex/ y .github/) en
vez de una única carpeta "artifacts/", porque cada app vive directamente
en la raíz (p.ej. /consultar/index.html -> https://.../apps/consultar/).

No hace llamadas a la API de GitHub ni necesita ningún secreto: el
workflow que invoca este script es el que hace commit/push del resultado
con el GITHUB_TOKEN propio del repo."""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import datetime, re
from portal_render import extract_app_metadata, render_portal_html, render_portal_html_temas, clase_de_app, render_footer_html, _fecha_es

ROOT = "."
EXCLUDE_DIRS = {"appindex", ".github", ".git"}
OUT_PATH = "appindex/index.html"
OUT_PATH_TEMAS = "appindex/temas/index.html"
TITLE = "Herramientas de IA para la Docencia (HIAD)"
SUBTITLE = "Moda, patrones y outfits generados con IA; detección de uso de IA en PDF; consulta documental asistida; monitorización en vivo de una estación meteorológica; y telemetría y control de enchufes inteligentes — todo en apps de un solo archivo, listas para el aula."
EYEBROW = "RafaUMH2110 · UMH"
CONTACT_NAME = "Rafael Puerto"
CONTACT_EMAIL = "r.puerto@umh.es"
DEPARTMENT = "Departamento de Ingeniería de Sistemas y Automática"
UNIVERSITY = "Universidad Miguel Hernández de Elche"
REPO_URL = "https://github.com/RafaUMH2110/apps"
# Página de entrada de la raíz: se escribe a mano, pero el generador rellena
# los bloques entre marcadores <!--HIAD:nombre--> … <!--/HIAD:nombre--> (pie
# común y cifras del catálogo) para que no se queden desfasados.
INICIO_PATH = "index.html"

# Categorías que se añaden automáticamente (al final de la lista, para no
# cambiar la categoría principal de cada app) a todas las apps de una
# carpeta de nivel superior, sin tener que editar el data-categories de
# cada app: carpeta -> categorías.
AUTO_CATEGORIES_BY_GROUP = {
    "moda": ["moda"],
}

# Lo mismo, pero por prefijo de ruta (más específico): las apps de
# telemetria/meteo/ y telemetria/home/ reciben además su área (Meteo u
# Hogar), para poder filtrarlas por separado en los dos portales.
AUTO_CATEGORIES_BY_PATH = {
    "telemetria/meteo/": ["telemetria", "meteo"],
    "telemetria/home/": ["telemetria", "hogar"],
}

# Subgrupo dentro de un tema (segundo nivel de carpeta): solo para los
# temas que lo usan; el portal por temas los muestra como subsecciones.
SUBGROUP_THEMES = {"telemetria"}


def list_local_apps(root):
    """Recorre cada carpeta de app en la raíz (salvo las excluidas)
    buscando .html/.htm con metadatos data-app-title."""
    apps = []
    for entry in sorted(os.listdir(root)):
        full_dir = os.path.join(root, entry)
        if entry.startswith(".") or entry in EXCLUDE_DIRS:
            continue
        if not os.path.isdir(full_dir):
            continue
        for dirpath, _, files in os.walk(full_dir):
            for fn in files:
                if not fn.lower().endswith((".html", ".htm")):
                    continue
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                with open(full, encoding="utf-8", errors="replace") as f:
                    content = f.read()
                meta = extract_app_metadata(content)
                if meta is None:
                    continue
                meta["group"] = rel.split("/")[0]
                meta["clase_app"] = clase_de_app(rel, meta)
                extra = list(AUTO_CATEGORIES_BY_GROUP.get(meta["group"], []))
                for prefijo, cats in AUTO_CATEGORIES_BY_PATH.items():
                    if rel.startswith(prefijo):
                        extra += cats
                for slug in extra:
                    if slug not in meta["categories"]:
                        meta["categories"].append(slug)
                partes = rel.split("/")
                meta["subgroup"] = partes[1] if meta["group"] in SUBGROUP_THEMES and len(partes) > 2 else ""
                apps.append((rel, meta))
    return apps


def path_to_url(pages_owner, pages_repo, rel):
    owner_lc = pages_owner.lower()
    base = f"https://{owner_lc}.github.io/{pages_repo}"
    if rel == "index.html":
        return f"{base}/"
    if rel.endswith("/index.html"):
        slug = rel[: -len("/index.html")]
        return f"{base}/{slug}/"
    return f"{base}/{rel}"


def main():
    pages_owner_repo = os.environ.get("GITHUB_REPOSITORY", "")
    if "/" not in pages_owner_repo:
        print("ERROR: no se pudo determinar GITHUB_REPOSITORY", file=sys.stderr)
        sys.exit(1)
    pages_owner, pages_repo = pages_owner_repo.split("/", 1)

    local_apps = list_local_apps(ROOT)
    if not local_apps:
        print("No se encontraron apps con metadatos de catálogo; no se actualiza el portal.")
        return

    catalog = []
    for rel, meta in local_apps:
        meta["url"] = path_to_url(pages_owner, pages_repo, rel)
        catalog.append(meta)
    catalog.sort(key=lambda m: m["title"].casefold())

    # Una sola fecha para las tres páginas, para que los pies coincidan.
    fecha = _fecha_es(datetime.datetime.now(datetime.timezone.utc))
    pie = dict(contact_name=CONTACT_NAME, contact_email=CONTACT_EMAIL, department=DEPARTMENT,
               university=UNIVERSITY, repo_url=REPO_URL, fecha=fecha)

    # Versión principal: cuadrícula plana, la que se usa en producción.
    html_out = render_portal_html(catalog, TITLE, SUBTITLE, EYEBROW, **pie)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"Portal actualizado con {len(catalog)} apps -> {OUT_PATH}")

    # Versión alternativa: agrupada por tema, estilo "forja". Punto de
    # acceso adicional, no sustituye a la versión principal de arriba.
    html_out_temas = render_portal_html_temas(catalog, TITLE, SUBTITLE, EYEBROW, **pie)
    os.makedirs(os.path.dirname(OUT_PATH_TEMAS), exist_ok=True)
    with open(OUT_PATH_TEMAS, "w", encoding="utf-8") as f:
        f.write(html_out_temas)
    print(f"Portal (agrupado por tema) actualizado con {len(catalog)} apps -> {OUT_PATH_TEMAS}")

    actualizar_inicio(catalog, pie)


def actualizar_inicio(catalog, pie):
    """Rellena en index.html (raíz) el pie común y las cifras del catálogo."""
    if not os.path.exists(INICIO_PATH):
        return
    with open(INICIO_PATH, encoding="utf-8") as f:
        texto = f.read()
    temas = len({a["group"] for a in catalog})
    navegador = sum(1 for a in catalog if a.get("client_only"))
    pct = round(100 * navegador / len(catalog)) if catalog else 0
    bloques = {
        "pie": render_footer_html("inicio", "", **pie),
        "cifras": (f'<li><b>{len(catalog)}</b> herramientas</li><li><b>{temas}</b> temas</li>'
                   f'<li><b>{pct}&nbsp;%</b> en el navegador</li>'),
    }
    for nombre, contenido in bloques.items():
        texto, n = re.subn(rf"(<!--HIAD:{nombre}-->).*?(<!--/HIAD:{nombre}-->)",
                           lambda m: m.group(1) + contenido + m.group(2), texto, flags=re.S)
        if not n:
            print(f"AVISO: index.html no tiene el bloque <!--HIAD:{nombre}-->; no se actualiza.")
    with open(INICIO_PATH, "w", encoding="utf-8") as f:
        f.write(texto)
    print(f"Página de entrada actualizada -> {INICIO_PATH}")


if __name__ == "__main__":
    main()
