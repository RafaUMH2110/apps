#!/usr/bin/env python3
"""Regenera appindex/artifacts/index.html (el portal) a partir del checkout
local de este mismo repo, usando portal_render.py (misma carpeta). No hace
llamadas a la API de GitHub ni necesita ningún secreto: el workflow que
invoca este script es el que hace commit/push del resultado con el
GITHUB_TOKEN propio del repo."""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from portal_render import extract_app_metadata, render_portal_html

FOLDER = "artifacts"
OUT_PATH = "appindex/index.html"
TITLE = "Herramientas de IA para la Docencia (HIAD)"
SUBTITLE = "Aplicaciones de inteligencia artificial para diseño de moda, generación de contenido y automatización de procesos académicos."
EYEBROW = "RafaUMH2110 · UMH"
CONTACT_NAME = "Rafael Puerto"
CONTACT_EMAIL = "r.puerto@umh.es"


def list_local_apps(folder):
    """Recorre folder buscando .html/.htm con metadatos data-app-title."""
    apps = []
    for root, _, files in os.walk(folder):
        for fn in files:
            if not fn.lower().endswith((".html", ".htm")):
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, folder).replace(os.sep, "/")
            with open(full, encoding="utf-8", errors="replace") as f:
                content = f.read()
            meta = extract_app_metadata(content)
            if meta is None:
                continue
            apps.append((rel, meta))
    return apps


def path_to_url(pages_owner, pages_repo, rel):
    owner_lc = pages_owner.lower()
    base = f"https://{owner_lc}.github.io/{pages_repo}/artifacts"
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

    local_apps = list_local_apps(FOLDER)
    if not local_apps:
        print("No se encontraron apps con metadatos de catálogo; no se actualiza el portal.")
        return

    catalog = []
    for rel, meta in local_apps:
        meta["url"] = path_to_url(pages_owner, pages_repo, rel)
        catalog.append(meta)
    catalog.sort(key=lambda m: m["title"].casefold())

    html_out = render_portal_html(
        catalog, TITLE, SUBTITLE, EYEBROW,
        contact_name=CONTACT_NAME, contact_email=CONTACT_EMAIL,
    )

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"Portal actualizado con {len(catalog)} apps -> {OUT_PATH}")


if __name__ == "__main__":
    main()
