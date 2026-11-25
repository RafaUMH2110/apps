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
| [TelemetriaWU](https://rafaumh2110.github.io/apps/telemetria/meteo/telemetriawu/) | Consulta bajo demanda los datos de una estación meteorológica personal (Vevor YT60234 u otra compatible) dada de alta en Weather Underground / Earth Network, directamente desde el navegador. Primera app de una serie que irá incorporando sondeo continuo, histórico persistente y otras funcionalidades. |
| [TelemetriaWU Monitor](https://rafaumh2110.github.io/apps/telemetria/meteo/telemetriawumonitor/) | Segunda app de la serie TelemetriaWU: sondeo continuo con backoff automático ante errores, lecturas en tarjetas gráficas con minigráficos en tiempo real, histórico de sesión y exportación a CSV. |
| [TelemetriaWU Histórico](https://rafaumh2110.github.io/apps/telemetria/meteo/telemetriawuhistorico/) | Tercera app de la serie TelemetriaWU: igual que TelemetriaWU Monitor, pero con histórico PERSISTENTE guardado en IndexedDB (sobrevive a recargar la página), con retención configurable, purga automática y exportación a CSV de todo el histórico guardado. |
| [TelemetriaWU MQTT](https://rafaumh2110.github.io/apps/telemetria/meteo/telemetriawumqtt/) | Cuarta app de la serie TelemetriaWU: igual que TelemetriaWU Histórico, añadiendo publicación de cada lectura en un topic MQTT sobre WebSocket (broker, topic, usuario/contraseña, QoS y retain configurables), con estado de conexión, contadores y registro de actividad independientes del sondeo. |
| [TelemetriaWU Gráficos](https://rafaumh2110.github.io/apps/telemetria/meteo/telemetriawugraficos/) | Quinta app de la serie TelemetriaWU, a partir de TelemetriaWU Monitor: sustituye los minigráficos por gráficos de líneas a tamaño completo que muestran la evolución de cada parámetro (temperatura y punto de rocío, viento y racha, humedad, presión, lluvia), con leyenda, cursor cruzado con tooltip y navegación por teclado; histórico de sesión y exportación a CSV. |
| [TelemetriaWU Móvil](https://rafaumh2110.github.io/apps/telemetria/meteo/telemetriawumovil/) | Sexta app de la serie TelemetriaWU: panel con aspecto de app nativa de iOS, instalable en la pantalla de inicio, con condiciones actuales (máximo/mínimo del día con hora), gráficos de evolución a lo largo del día completo (temperatura/rocío, presión, humedad, viento/racha, dirección del viento, radiación solar e índice UV en una sola gráfica con doble eje Y, y tasa de lluvia junto con la lluvia acumulada en otra), histórico del día persistente en IndexedDB con relleno opcional vía el endpoint de histórico de Weather Underground, hoja de ajustes, compartir y exportación a CSV. |
| [TelemetriaWU iPad](https://rafaumh2110.github.io/apps/telemetria/meteo/telemetriawuipad/) | Séptima app de la serie TelemetriaWU: igual motor de datos que TelemetriaWU Móvil, con un diseño de dos paneles pensado para el ancho de un iPad (barra lateral persistente con navegación/ajustes/compartir/CSV y un área de contenido con tiles y gráficos en cuadrícula de varias columnas que se adapta sola, vía CSS grid, a cualquier modelo, orientación y Split View/Slide Over); como TelemetriaWU Móvil, combina radiación solar + índice UV y tasa de lluvia + lluvia acumulada en gráficas de doble eje Y. |
| [TeleMet](https://rafaumh2110.github.io/apps/telemetria/meteo/telemet/) | Basada en TelemetriaWU Monitor: mismo sondeo continuo con backoff automático, pero con tiempo límite configurable por petición (AbortController), flechas de tendencia (▲/▼/—) en cada tarjeta respecto a la lectura anterior, aviso de valor fuera de rango ampliado a las siete variables, modo oscuro automático y exportación a CSV con BOM UTF-8. |
| [TeleMet Pro](https://rafaumh2110.github.io/apps/telemetria/meteo/telemet/pro/) | Misma base que TeleMet, con un rediseño editorial completo (tipografía Bricolage Grotesque + Instrument Sans + JetBrains Mono, paleta de tipo "forja", tarjetas con icono y color por variable): luz de estado persistente en la cabecera y en una barra inferior fija, visibilidad de la API Key, ajustes avanzados plegables y un glosario emergente de términos (Freshness, tendencia, backoff, plausibilidad). Sus gráficas de evolución de 12 h muestran radiación solar + índice UV y tasa de lluvia + lluvia acumulada en una misma gráfica cada una, con doble eje Y (escala izquierda y derecha, leyenda con unidades y tooltip con ambos valores). |
| [TeleMet Mobile](https://rafaumh2110.github.io/apps/telemetria/meteo/telemetmobile/) | Misma base que TelemetriaWU Móvil (panel estilo app nativa instalable en la pantalla de inicio, con tiles de condiciones actuales y gráficos del día), con el mismo rediseño editorial de tipo "forja" que TeleMet Pro, una luz de estado persistente en la cabecera (en vivo/reintentando/error/pausado), umbral de "obsoleto" ahora funcional, tiempo límite de petición configurable, visibilidad de la API Key y exportación a CSV con BOM UTF-8. Los gráficos del día combinan radiación solar + índice UV y tasa de lluvia + lluvia acumulada en gráficas de doble eje Y. |
| [TeleMet iPad](https://rafaumh2110.github.io/apps/telemetria/meteo/telemetipad/) | Misma base que TelemetriaWU iPad (diseño de dos paneles: barra lateral con navegación/ajustes/compartir/CSV y cuadrícula de tiles y gráficos adaptable a cualquier modelo/orientación/Split View), con el mismo rediseño editorial de tipo "forja" que TeleMet Pro y TeleMet Mobile, luz de estado persistente en la barra lateral, umbral de "obsoleto" ahora funcional, tiempo límite de petición configurable, visibilidad de la API Key y exportación a CSV con BOM UTF-8. Los gráficos del día combinan radiación solar + índice UV y tasa de lluvia + lluvia acumulada en gráficas de doble eje Y. |
| [TeleMet Multi](https://rafaumh2110.github.io/apps/telemetria/meteo/telemet/multi/) | Basada en TeleMet Historial pero para **varias estaciones a la vez**, cada una con su Station ID, su API Key, su nombre y su color: sondeo independiente por estación (un fallo en una no detiene las demás), tarjetas de condiciones actuales, tabla comparativa con máximos/mínimos y diferencias respecto a una estación de referencia, extremos entre estaciones, mapa esquemático, gráficas de 12 h / 24 h / 7 días con todas las estaciones superpuestas (o todas las variables de una sola estación), resumen de 7 días, consulta de un día concreto, histórico persistente por estación en IndexedDB, sincronización con los JSON de TeleMet Colector multiestación, estimación de cuota por clave, importación/exportación de la configuración y CSV. |
| [TeleMet MultiStation](https://rafaumh2110.github.io/apps/telemetria/meteo/telemet/multistation/) | Versión en inglés de TeleMet Multi: misma app para seguir **varias estaciones a la vez** (sondeo independiente, tarjetas, comparativa, gráficas superpuestas, resumen de 7 días, día concreto, mapa y sincronización con TeleMet Collector), con interfaz, mensajes y comentarios en inglés, almacenamiento propio (`telemetmultistation_*`) y lectura de `history_<ID>.json` (acepta también los nombres `historial_*`). |
| [TeleHome (servicio)](https://github.com/RafaUMH2110/code/tree/main/telemetria/home/telehome-servicio) | **Servicio** y app de telemetría y control de enchufes Wi-Fi con medidor (Tuya, modo local y nube), con su propia interfaz web. Se instala en tu equipo o servidor; vive en el repo `code`. | Servicio |
| [TeleHome · Demostración](https://rafaumh2110.github.io/apps/telemetria/home/telehome/) | Versión **genérica** de TeleHome: la misma plantilla para varios tipos de dispositivo. En esta primera versión, enchufes Wi-Fi (potencia, tensión, corriente y energía), sensores de temperatura y humedad, luces regulables (brillo, blancos y color) y persianas; el catálogo lista además termostato y contador general como previstos. Contador adaptativo, agrupación por tipo o estancia, controles según el tipo, gráfica por magnitud (los tipos que miden lo mismo se dibujan juntos), una tabla de resumen por tipo y CSV. Se conecta a un servicio TeleHome del mismo servidor y, si encuentra un servicio anterior a la 0.5.0 (solo enchufes), un adaptador lo traduce al modelo genérico; sin servicio, funciona en **modo demostración** con siete dispositivos simulados guardados solo en el navegador. |

**Gráficas combinadas de doble eje (5 nov 2026).** En todas las apps de `telemetria/` que muestran estas variables (TeleMet Pro, Historial, Cal, Cal Vivo y la versión inglesa History; TeleMet Mobile/iPad y sus variantes Pro y Cal; TelemetriaWU Móvil e iPad), la radiación solar y el índice UV comparten gráfica (UV en el eje derecho), igual que la tasa de lluvia y la lluvia acumulada (acumulada en trazo discontinuo y eje derecho). Ambos ejes comparten rejilla, la leyenda indica unidades y eje de cada serie y el tooltip muestra los dos valores con su unidad. En las apps de la familia TeleMet Pro/Historial/Cal/Cal Vivo/History las mismas dos gráficas combinadas aparecen también en las de 7 días (y en la consulta de un día concreto de Historial). Las gráficas de 7 días de las apps móviles/iPad y las apps sin estas variables (TeleMet, versiones Lite, TelemetriaWU/Monitor/Histórico/MQTT/Gráficos) no cambian.

**Ventana de 12 h / 24 h (5 nov 2026).** TeleMet Historial y su versión inglesa TeleMet History incorporan, en el panel de evolución de horas, un selector 12 h / 24 h que cambia la ventana de todas las gráficas (eje X, umbral de huecos y mensajes se adaptan) y se recuerda en el navegador. Las 24 h se construyen con el histórico local (retención de 9 días) y con el JSON del colector, que ahora guarda 24 h por defecto (configurable con `duracion_horas`, `--horas` o `TELEMET_HORAS`).

**TeleMet Multi (6 nov 2026).** Nueva app `telemetria/meteo/telemet/multi/` para seguir varias estaciones a la vez. Lee el histórico de cada una desde `historial_<ID>.json` (TeleMet Colector multiestación), de modo que apuntando su carpeta de datos a `../historial/datos/` se completan las gráficas sin esperar a acumular lecturas en el navegador.

**TeleMet MultiStation (7 nov 2026).** Nueva app `telemetria/meteo/telemet/multistation/`: versión en inglés de TeleMet Multi (misma funcionalidad, interfaz y comentarios en inglés, formato de fechas y números en-GB). Usa su propio almacenamiento (`telemetmultistation_*`, IndexedDB `telemetmultistation_db`) para convivir con la versión española, y busca primero los archivos del colector en inglés (`data/history_<ID>.json`, `../telemethistory/data/`) y después los españoles. La documentación de TeleMet Collector apunta ahora a esta versión.

**TeleHome Enchufes Web (20 nov 2026).** Nueva app `telemetria/home/telehome-enchufes/`: interfaz web del servicio TeleHome Enchufes (repo `code`, `telemetria/home/telehome-enchufes`). Detecta el servicio por la ruta de la propia página o por una ruta del mismo servidor escrita en el pie (p. ej. `/rafa/telehome/enchufes/`; el servicio no admite otros orígenes) y, si no lo encuentra, entra en modo demostración con tres enchufes simulados (encender/apagar, añadir, histórico y exportación a CSV en el navegador). El almacenamiento de la demo es `localStorage` (`telehome_demo_v1`). Las funciones de la nube de Tuya y el descubrimiento de la red solo están disponibles con el servicio real.

**Portal: áreas Meteo y Hogar, navegación y fichas de altura fija (20 nov 2026).** Los dos portales (`appindex/` y `appindex/temas/`) muestran primero las **áreas** (Moda, Telemetría y, bajo ella, Meteo y Hogar, que el generador asigna por carpeta: `telemetria/meteo/` y `telemetria/home/`) y después el resto de categorías. Ambos llevan una barra *Inicio · Catálogo completo · Agrupado por tema* que conserva el filtro y la búsqueda (`#cat=…&q=…`), así que se puede ir y volver entre vistas o enlazar directamente a un área (p. ej. `appindex/temas/#cat=hogar`). En la vista por tema, Telemetría se divide en «Estación meteorológica» y «Hogar», las fichas tienen altura fija con barra de desplazamiento en la descripción y hay modo oscuro. La raíz del repo tiene una página de entrada (`index.html`). El workflow regenera y sube las dos versiones del portal, también al cambiar los scripts del generador.

**Portal: versiones y controles para plegar (20 nov 2026).** Los filtros de los dos portales tienen ahora tres grupos: **Áreas**, **Versiones** (Normales, Lite, Pro, ProMax y Para el aula; se combinan con el área o la categoría y quedan en la URL como `#v=pro`) y **Categorías**. Cada grupo se puede plegar, el panel de filtros se puede ocultar entero («Ocultar filtros») y cada sección (versión en el catálogo completo, tema en la vista por tema) se pliega con su flecha o con «Plegar todo»; estas preferencias se recuerdan en el navegador. Los contadores tienen en cuenta los demás filtros y las opciones sin resultados se desactivan. El título de la cabecera usa Plus Jakarta Sans.

**Pie de página común (20 nov 2026).** La página de entrada (`index.html`), el catálogo completo y la vista por tema comparten el mismo pie: enlaces a Inicio, Catálogo completo, Agrupado por tema, Versión anterior y GitHub (con la página actual marcada), autor con departamento, universidad y correo, y la línea «Generado con IA · Revisado por el autor · Última actualización». El generador (`render_footer_html` en `portal_render.py`) escribe los tres con la misma fecha. En `index.html`, el pie y las cifras del catálogo están entre marcadores `<!--HIAD:…-->` que rellena `generate_index.py`; no se editan a mano. La entrada tiene además accesos directos por versión (Normales, Lite, Pro, ProMax, Para el aula).

**TeleHome Enchufes · Demostración (20 nov 2026).** La antigua «TeleHome Enchufes Web» se llama ahora *TeleHome Enchufes · Demostración* (título, catálogo y página de entrada) y tiene la interfaz 0.3.1 del servicio, con la cabecera renovada. Ya no se lista en la página de entrada del servidor Linux, donde está la interfaz real.

**TeleHome (20 nov 2026).** Nueva app `telemetria/home/telehome/`: la versión genérica de TeleHome Enchufes, pensada para ir creciendo con más tipos de dispositivo. Todo el conocimiento sobre tipos vive en un catálogo al principio del fichero (`METRICS`, magnitudes comunes a todos los tipos, y `TYPES`, un tipo por entrada) y de ahí sale la interfaz: el formulario de alta, la fila del dispositivo, su control (interruptor, interruptor + nivel, subir/parar/bajar o solo lectura), las magnitudes de la gráfica, las columnas del resumen, la cifra del contador y el simulador de la demostración. Añadir un tipo es añadir una entrada. Las lecturas viajan con la misma forma para todos (`reading.values` con las claves de `METRICS`), el dispositivo lleva `type` y `room`, y las órdenes van a `api/devices/<id>/command` con `action` (`switch`, `level`, `position`, `stop`, `setpoint`). Si el servicio que responde es el antiguo TeleHome Enchufes, un adaptador traduce sus respuestas y manda las órdenes a `api/plugs/<id>/power`, así que los enchufes reales siguen funcionando sin tocar el servicio (los demás tipos quedan deshabilitados hasta actualizarlo; `api/state` indica en `types` los que admite). Almacenamiento de la demo: `localStorage`, clave `telehome_demo_v1`. Máximo 16 dispositivos.

**TeleHome: el servicio pasa a llamarse `telehome-servicio` (22 nov 2026).** El nombre «TeleHome Enchufes» queda obsoleto. En el repo `code`, el servicio vive ahora en `telemetria/home/telehome-servicio` (módulo Python `telehome`, antes `telehome_enchufes`; variable `TELEHOME_DIR`, antes `TELEHOME_ENCHUFES_DIR`) y habla con `api/health` → `"app": "TeleHome"`; las pruebas por línea de órdenes pasan a `telehome-pruebas`. Se elimina la demostración preliminar `telemetria/home/telehome-enchufes/` de este repo, sustituida por la app genérica `telemetria/home/telehome/` (demo en GitHub Pages), y las versiones antiguas para iPhone e iPad de `code`, sustituidas por `telehome-iphone/` y `telehome-ipad/`.

**TeleHome: soporte de luces (25 nov 2026).** Las bombillas de Smart Life (Tuya) ya se manejan como `luz`, no como enchufes: interruptor, brillo, blanco cálido↔frío, color y modo. La app genérica (`telemetria/home/telehome/`) y las de iPhone y iPad (`telehome-iphone`, `telehome-ipad`) añaden un botón de paleta en la fila de cada luz y un panel con esos controles; el panel ofrece solo lo que la bombilla sabe hacer (`caps`, que manda el servicio 0.10.0). Las programaciones admiten las órdenes `temp`, `color` y `mode`, y al editar un dispositivo se puede cambiar su tipo (para las bombillas que se importaron como enchufe; el servicio 0.10.0 las convierte además por su cuenta). Con un servicio anterior solo hay brillo. El modo demostración incluye una luz con todos los controles. Manual: apartado «Luces» de `MANUAL_TELEHOME.md`.

## Estructura del repositorio

```
apps/
├── appindex/          ← portal con el catálogo (GenImOd, GenPatMod, SearchLogMod...)
│   ├── index.html         portal general (todas las apps de la tabla de arriba)
│   └── moda/index.html     portal específico de moda (GenImOda, GenPatModa, GenOutFitS)
├── <nombre-app>/      ← una carpeta por app, cada una con su index.html
│   └── index.html
└── .github/workflows/ ← despliegue a GitHub Pages y regeneración del portal
```

Cada app vive en su propia carpeta en la raíz del repo, por lo que su
URL en GitHub Pages queda limpia:
`https://rafaumh2110.github.io/apps/<nombre-app>/`.

## Despliegue automático

- **GitHub Pages** (`deploy-artifacts-pages.yml`): cada `push` a `main`
  publica todo el repositorio en https://rafaumh2110.github.io/apps/.
- **Portal** (`sync-appindex-portal.yml`): cada `push` que modifique una
  carpeta de app regenera `appindex/index.html` (versión principal) y
  `appindex/temas/index.html` (versión alternativa, agrupada por tema) a
  partir de los metadatos (`data-app-title`, `data-app-description`,
  `data-categories`, `data-tags`) declarados en la etiqueta `<body>` de
  cada app, y hace commit del resultado automáticamente. No requiere
  ningún secreto:
  todo ocurre dentro de este mismo repositorio.

## Componentes de servidor

| Carpeta | Descripción |
|---|---|
| [`telemetria/meteo/telemetcolector/`](telemetria/meteo/telemetcolector/) | **TeleMet Colector**: programa Python que lee de forma continua la estación meteorológica, guarda un histórico de 24 h (configurable) en el servidor Linux y lo publica como JSON para que TeleMet Historial complete sus gráficas de evolución de 12 h y 24 h. Admite **varias estaciones, cada una con su API Key** (secciones `[estacion:ID]`, un hilo, una BD y un `historial_<ID>.json` por estación). Ver su README. |
| [`telemetria/meteo/telemetcollector/`](telemetria/meteo/telemetcollector/) | **TeleMet Collector** (English version of TeleMet Colector): Python program that continuously reads the weather station, keeps a 24 h (configurable) history on the Linux server and publishes it as JSON so that TeleMet History can complete its evolution charts. Supports **several stations, each with its own API Key** (`[station:ID]` sections, one thread, DB and `history_<ID>.json` per station). English app: [`telemetria/meteo/telemet/history/`](telemetria/meteo/telemet/history/). See its README. |

## Despliegue en un servidor propio (Apache)

Existe un paquete de scripts para instalar el portal `appindex/moda` y
las apps que enlaza en un servidor Linux (Debian) propio con Apache,
como alternativa o complemento a GitHub Pages. Pide ese paquete si lo
necesitas.

## Autor

Rafael Puerto — Departamento de Ingeniería de Sistemas y Automática.
Universidad Miguel Hernández de Elche (UMH),  Contacto: r.puerto@umh.es
