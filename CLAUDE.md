# apps — normas para trabajar en este repositorio

Colección de apps web de un solo HTML publicada en GitHub Pages
(`https://rafaumh2110.github.io/apps/`). Idioma de trabajo: español.

## Antes de tocar nada
- Un push a `main` **publica el sitio**. Trabaja en una rama (`feat/…`, `fix/…`, `docs/…`) y abre un PR; no hagas force-push a `main`.
- Las URLs de las apps (`<familia>/<app>/`) están publicadas y enlazadas desde el portal, los manuales y los instaladores de `RafaUMH2110/code`. **No renombres ni muevas carpetas de apps.**
- El portal (`appindex/index.html` y `appindex/temas/index.html`) lo genera el workflow `Portal y Pages` a partir de `data-app-title`, `data-app-description`, `data-categories` y `data-tags` del `<body>` de cada app. No lo edites a mano. `appindex/index-anterior.html` sí es manual y está enlazado desde el portal: no lo borres.
- `appindex/` se mantiene versionado porque los instaladores copian el repo a Apache.

## Al editar una app
- Actualiza siempre el pie «Última modificación» (fecha y hora actuales) antes de subirla.
- Cada app es un único `index.html`, sin backend. Las claves de API las introduce el usuario en el navegador: no pongas claves en el código.
- Parejas español/inglés con nombre distinto: `historial`/`history`, `multi`/`multistation`, `telemetcolector`/`telemetcollector`.
- El colector (`telemetria/telemetcolector` y `telemetcollector`) tiene **aquí su única fuente**: los instaladores lo instalan desde este repo. Mantén ES y EN sincronizados.

## Commits
- Mensajes en español. Termina los commits de Claude Code con las líneas de atribución que indique la sesión (`Co-Authored-By` y `Claude-Session`).
- No commitees `__pycache__`, claves, `config.ini` ni bases de datos.
