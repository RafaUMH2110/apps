# apps

Herramientas de IA para la Docencia (HIAD) — colección de apps web de
un solo archivo HTML (sin backend propio) para la generación de
imágenes y patrones de moda, la investigación de logística de
empresas del sector y el apoyo a la evaluación académica. Cada app
llama directamente, desde el navegador, a las APIs de Anthropic Claude,
OpenAI, Google Gemini y/o fal.ai con la clave que introduce la propia
persona que la usa.

**Portal con el catálogo completo:** https://rafaumh2110.github.io/apps/appindex/
**Versión alternativa, agrupada por tema (moda, telemetría...):** https://rafaumh2110.github.io/apps/appindex/temas/

## Apps

| App | Descripción |
|---|---|
| [ConSultar](https://rafaumh2110.github.io/apps/consultar/) | Mejora automáticamente tu consulta y la envía a Claude para obtener una respuesta completa en Markdown, exportable a Word o PDF. |
| [DetectIApdf](https://rafaumh2110.github.io/apps/pdfs/detectiapdf/) | Analiza hasta 3 documentos PDF y genera un informe forense de indicios de uso de IA en su redacción, con exportación a PDF; pensada para profesorado universitario. |
| [DetectIApdfOne](https://rafaumh2110.github.io/apps/pdfs/detectiapdfone/) | Versión de un único documento de DetectIApdf. |
| [DetectIApdfLite](https://rafaumh2110.github.io/apps/pdfs/detectiapdflite/) | Versión ligera de DetectIApdfOne: prompt reducido, menos tokens y menor coste en documentos extensos. |
| [GenImOd](https://rafaumh2110.github.io/apps/moda/genimod/) | Genera imágenes de moda con IA: mejora la idea con Claude, OpenAI o Gemini y crea la imagen final con FLUX (fal.ai). Versión completa, con proveedor, modelos y parámetros configurables. |
| [GenImOda](https://rafaumh2110.github.io/apps/moda/genimoda/) | Versión de GenImOd para el aula, con opción de omitir la mejora del prompt y modelos/parámetros limitados por el profesor. |
| [GenImOd — alumnos](https://rafaumh2110.github.io/apps/moda/genimod-alumnos/) | Otra versión de GenImOd para el aula, con modelos y parámetros limitados y fijados por el profesor. |
| [GenOutFit](https://rafaumh2110.github.io/apps/moda/genoutfit/) | A partir de la foto de una prenda, genera un outfit completo a juego (prompts + imágenes), con un número de piezas configurable. |
| [GenOutFitFace](https://rafaumh2110.github.io/apps/moda/genoutfitface/) | Como GenOutFit, añadiendo la foto de una persona para generar la imagen del modelo conservando su rostro real (FLUX Kontext). |
| [GenOutFitFaceM](https://rafaumh2110.github.io/apps/moda/genoutfitfacem/) | Como GenOutFitFace, permitiendo subir hasta dos prendas y elegir complementos (gafas, collares, bolsos, zapatos...). |
| [GenOutFitS](https://rafaumh2110.github.io/apps/moda/genoutfits/) | Versión para alumnos de GenOutFit, con catálogo de modelos y parámetros limitados por el profesor. |
| [GenPatMod](https://rafaumh2110.github.io/apps/moda/genpatmod/) | Genera patrones de corte de moda en SVG a partir de una idea y los exporta a PDF A4, con revisión del plan de piezas e historial local. |
| [GenPatModa](https://rafaumh2110.github.io/apps/moda/genpatmoda/) | Versión para alumnos de GenPatMod, con catálogo de modelos y tokens limitados por el profesor. |
| [SearchLogMod](https://rafaumh2110.github.io/apps/moda/searchlogmod/) | Consulta asistida por IA sobre métodos y logística de empresas de la industria de la moda, con estimación de coste y exportación a Markdown/texto/Word. |
| [SearchLogModCB](https://rafaumh2110.github.io/apps/moda/searchlogmodcb/) | Versión de SearchLogMod con caché de resultados, caché de prompts de Anthropic y modo por lotes (cola propia o Batch API). |
| [TelemetriaWU](https://rafaumh2110.github.io/apps/telemetria/telemetriawu/) | Consulta bajo demanda los datos de una estación meteorológica personal (Vevor YT60234 u otra compatible) dada de alta en Weather Underground / Earth Network, directamente desde el navegador. Primera app de una serie que irá incorporando sondeo continuo, histórico persistente y otras funcionalidades. |
| [TelemetriaWU Monitor](https://rafaumh2110.github.io/apps/telemetria/telemetriawumonitor/) | Segunda app de la serie TelemetriaWU: sondeo continuo con backoff automático ante errores, lecturas en tarjetas gráficas con minigráficos en tiempo real, histórico de sesión y exportación a CSV. |
| [TelemetriaWU Histórico](https://rafaumh2110.github.io/apps/telemetria/telemetriawuhistorico/) | Tercera app de la serie TelemetriaWU: igual que TelemetriaWU Monitor, pero con histórico PERSISTENTE guardado en IndexedDB (sobrevive a recargar la página), con retención configurable, purga automática y exportación a CSV de todo el histórico guardado. |
| [TelemetriaWU MQTT](https://rafaumh2110.github.io/apps/telemetria/telemetriawumqtt/) | Cuarta app de la serie TelemetriaWU: igual que TelemetriaWU Histórico, añadiendo publicación de cada lectura en un topic MQTT sobre WebSocket (broker, topic, usuario/contraseña, QoS y retain configurables), con estado de conexión, contadores y registro de actividad independientes del sondeo. |
| [TelemetriaWU Gráficos](https://rafaumh2110.github.io/apps/telemetria/telemetriawugraficos/) | Quinta app de la serie TelemetriaWU, a partir de TelemetriaWU Monitor: sustituye los minigráficos por gráficos de líneas a tamaño completo que muestran la evolución de cada parámetro (temperatura y punto de rocío, viento y racha, humedad, presión, lluvia), con leyenda, cursor cruzado con tooltip y navegación por teclado; histórico de sesión y exportación a CSV. |
| [TelemetriaWU Móvil](https://rafaumh2110.github.io/apps/telemetria/telemetriawumovil/) | Sexta app de la serie TelemetriaWU: panel con aspecto de app nativa de iOS, instalable en la pantalla de inicio, con condiciones actuales (máximo/mínimo del día con hora), gráficos de evolución a lo largo del día completo (temperatura/rocío, presión, humedad, viento/racha, dirección del viento, radiación solar e índice UV en una sola gráfica con doble eje Y, y tasa de lluvia junto con la lluvia acumulada en otra), histórico del día persistente en IndexedDB con relleno opcional vía el endpoint de histórico de Weather Underground, hoja de ajustes, compartir y exportación a CSV. |
| [TelemetriaWU iPad](https://rafaumh2110.github.io/apps/telemetria/telemetriawuipad/) | Séptima app de la serie TelemetriaWU: igual motor de datos que TelemetriaWU Móvil, con un diseño de dos paneles pensado para el ancho de un iPad (barra lateral persistente con navegación/ajustes/compartir/CSV y un área de contenido con tiles y gráficos en cuadrícula de varias columnas que se adapta sola, vía CSS grid, a cualquier modelo, orientación y Split View/Slide Over); como TelemetriaWU Móvil, combina radiación solar + índice UV y tasa de lluvia + lluvia acumulada en gráficas de doble eje Y. |
| [TeleMet](https://rafaumh2110.github.io/apps/telemetria/telemet/) | Basada en TelemetriaWU Monitor: mismo sondeo continuo con backoff automático, pero con tiempo límite configurable por petición (AbortController), flechas de tendencia (▲/▼/—) en cada tarjeta respecto a la lectura anterior, aviso de valor fuera de rango ampliado a las siete variables, modo oscuro automático y exportación a CSV con BOM UTF-8. |
| [TeleMet Pro](https://rafaumh2110.github.io/apps/telemetria/telemet/pro/) | Misma base que TeleMet, con un rediseño editorial completo (tipografía Bricolage Grotesque + Instrument Sans + JetBrains Mono, paleta de tipo "forja", tarjetas con icono y color por variable): luz de estado persistente en la cabecera y en una barra inferior fija, visibilidad de la API Key, ajustes avanzados plegables y un glosario emergente de términos (Freshness, tendencia, backoff, plausibilidad). Sus gráficas de evolución de 12 h muestran radiación solar + índice UV y tasa de lluvia + lluvia acumulada en una misma gráfica cada una, con doble eje Y (escala izquierda y derecha, leyenda con unidades y tooltip con ambos valores). |
| [TeleMet Mobile](https://rafaumh2110.github.io/apps/telemetria/telemetmobile/) | Misma base que TelemetriaWU Móvil (panel estilo app nativa instalable en la pantalla de inicio, con tiles de condiciones actuales y gráficos del día), con el mismo rediseño editorial de tipo "forja" que TeleMet Pro, una luz de estado persistente en la cabecera (en vivo/reintentando/error/pausado), umbral de "obsoleto" ahora funcional, tiempo límite de petición configurable, visibilidad de la API Key y exportación a CSV con BOM UTF-8. Los gráficos del día combinan radiación solar + índice UV y tasa de lluvia + lluvia acumulada en gráficas de doble eje Y. |
| [TeleMet iPad](https://rafaumh2110.github.io/apps/telemetria/telemetipad/) | Misma base que TelemetriaWU iPad (diseño de dos paneles: barra lateral con navegación/ajustes/compartir/CSV y cuadrícula de tiles y gráficos adaptable a cualquier modelo/orientación/Split View), con el mismo rediseño editorial de tipo "forja" que TeleMet Pro y TeleMet Mobile, luz de estado persistente en la barra lateral, umbral de "obsoleto" ahora funcional, tiempo límite de petición configurable, visibilidad de la API Key y exportación a CSV con BOM UTF-8. Los gráficos del día combinan radiación solar + índice UV y tasa de lluvia + lluvia acumulada en gráficas de doble eje Y. |
| [TeleMet Multi](https://rafaumh2110.github.io/apps/telemetria/telemet/multi/) | Basada en TeleMet Historial pero para **varias estaciones a la vez**, cada una con su Station ID, su API Key, su nombre y su color: sondeo independiente por estación (un fallo en una no detiene las demás), tarjetas de condiciones actuales, tabla comparativa con máximos/mínimos y diferencias respecto a una estación de referencia, extremos entre estaciones, mapa esquemático, gráficas de 12 h / 24 h / 7 días con todas las estaciones superpuestas (o todas las variables de una sola estación), resumen de 7 días, consulta de un día concreto, histórico persistente por estación en IndexedDB, sincronización con los JSON de TeleMet Colector multiestación, estimación de cuota por clave, importación/exportación de la configuración y CSV. |
| [TeleMet MultiStation](https://rafaumh2110.github.io/apps/telemetria/telemet/multistation/) | Versión en inglés de TeleMet Multi: misma app para seguir **varias estaciones a la vez** (sondeo independiente, tarjetas, comparativa, gráficas superpuestas, resumen de 7 días, día concreto, mapa y sincronización con TeleMet Collector), con interfaz, mensajes y comentarios en inglés, almacenamiento propio (`telemetmultistation_*`) y lectura de `history_<ID>.json` (acepta también los nombres `historial_*`). |

## Estructura del repositorio

```
apps/
├── appindex/      portal con el catálogo (index.html, temas/, moda/) e iconos
├── consultar/     ConSultar
├── pdfs/          DetectIApdf y variantes
├── moda/          GenImOd, GenOutFit, GenPatMod, SearchLogMod y sus versiones
│   └── <app>/pro/    versión Pro de cada app
├── telemetria/    TelemetriaWU, TeleMet y los colectores (telemetcolector / telemetcollector)
└── .github/       workflow de portal + despliegue y scripts que generan el portal
```

Cada app vive en su propia carpeta y su URL en GitHub Pages es
`https://rafaumh2110.github.io/apps/<familia>/<app>/`. Esas URLs están
publicadas y enlazadas desde el portal, los manuales y los instaladores:
**no se renombran ni se mueven carpetas de apps**. Las parejas
español/inglés llevan nombres distintos (`historial`/`history`,
`multi`/`multistation`, `telemetcolector`/`telemetcollector`).

Los cambios de calendario (qué se añadió y cuándo) están en
[`CHANGELOG.md`](CHANGELOG.md).

## Despliegue automático

Un único workflow, `.github/workflows/portal-y-pages.yml`, se ejecuta en
cada `push` a `main` (o a mano desde la pestaña *Actions*) en dos pasos
encadenados:

1. **Portal** (`sync-portal`): regenera `appindex/index.html` (versión
   principal) y `appindex/temas/index.html` (agrupada por tema) a partir
   de los metadatos (`data-app-title`, `data-app-description`,
   `data-categories`, `data-tags`) declarados en la etiqueta `<body>` de
   cada app. Si hay cambios, hace commit del resultado. No requiere
   ningún secreto.
2. **Pages** (`deploy`): publica en
   https://rafaumh2110.github.io/apps/ el árbol ya con el portal
   regenerado, sin `.github/`, sin `.git` y sin ficheros `.zip`.

El portal se mantiene versionado porque los instaladores
(`instalar-todo*.sh`) copian el repositorio clonado a Apache y necesitan
`appindex/` tal cual.

## Componentes de servidor

| Carpeta | Descripción |
|---|---|
| [`telemetria/telemetcolector/`](telemetria/telemetcolector/) | **TeleMet Colector**: programa Python que lee de forma continua la estación meteorológica, guarda un histórico de 24 h (configurable) en el servidor Linux y lo publica como JSON para que TeleMet Historial complete sus gráficas de evolución de 12 h y 24 h. Admite **varias estaciones, cada una con su API Key** (secciones `[estacion:ID]`, un hilo, una BD y un `historial_<ID>.json` por estación). Ver su README. |
| [`telemetria/telemetcollector/`](telemetria/telemetcollector/) | **TeleMet Collector** (English version of TeleMet Colector): Python program that continuously reads the weather station, keeps a 24 h (configurable) history on the Linux server and publishes it as JSON so that TeleMet History can complete its evolution charts. Supports **several stations, each with its own API Key** (`[station:ID]` sections, one thread, DB and `history_<ID>.json` per station). English app: [`telemetria/telemet/history/`](telemetria/telemet/history/). See its README. |

## Despliegue en un servidor propio (Apache)

Los scripts `instalar-todo*.sh` del repositorio
[`code`](https://github.com/RafaUMH2110/code/tree/main/scripts)
(carpeta `scripts/`) clonan este repositorio, despliegan las apps en un
servidor Linux (Debian) propio con Apache y pueden instalar el colector
como servicio. Son una alternativa o complemento a GitHub Pages.

## Autor

Rafael Puerto — Departamento de Ingeniería de Sistemas y Automática.
Universidad Miguel Hernández de Elche (UMH),  Contacto: r.puerto@umh.es
