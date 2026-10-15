# apps

Herramientas de IA para la Docencia (HIAD) — colección de apps web de
un solo archivo HTML (sin backend propio) para la generación de
imágenes y patrones de moda, la investigación de logística de
empresas del sector y el apoyo a la evaluación académica. Cada app
llama directamente, desde el navegador, a las APIs de Anthropic Claude,
OpenAI, Google Gemini y/o fal.ai con la clave que introduce la propia
persona que la usa.

**Portal con el catálogo completo:** https://rafaumh2110.github.io/apps/appindex/

## Apps

| App | Descripción |
|---|---|
| [ConSultar](https://rafaumh2110.github.io/apps/consultar/) | Mejora automáticamente tu consulta y la envía a Claude para obtener una respuesta completa en Markdown, exportable a Word o PDF. |
| [DetectIApdf](https://rafaumh2110.github.io/apps/detectiapdf/) | Analiza hasta 3 documentos PDF y genera un informe forense de indicios de uso de IA en su redacción, con exportación a PDF; pensada para profesorado universitario. |
| [DetectIApdfOne](https://rafaumh2110.github.io/apps/detectiapdfone/) | Versión de un único documento de DetectIApdf. |
| [DetectIApdfLite](https://rafaumh2110.github.io/apps/detectiapdflite/) | Versión ligera de DetectIApdfOne: prompt reducido, menos tokens y menor coste en documentos extensos. |
| [GenImOd](https://rafaumh2110.github.io/apps/genimod/) | Genera imágenes de moda con IA: mejora la idea con Claude, OpenAI o Gemini y crea la imagen final con FLUX (fal.ai). Versión completa, con proveedor, modelos y parámetros configurables. |
| [GenImOda](https://rafaumh2110.github.io/apps/genimoda/) | Versión de GenImOd para el aula, con opción de omitir la mejora del prompt y modelos/parámetros limitados por el profesor. |
| [GenImOd — alumnos](https://rafaumh2110.github.io/apps/genimod-alumnos/) | Otra versión de GenImOd para el aula, con modelos y parámetros limitados y fijados por el profesor. |
| [GenOutFit](https://rafaumh2110.github.io/apps/genoutfit/) | A partir de la foto de una prenda, genera un outfit completo a juego (prompts + imágenes), con un número de piezas configurable. |
| [GenOutFitFace](https://rafaumh2110.github.io/apps/genoutfitface/) | Como GenOutFit, añadiendo la foto de una persona para generar la imagen del modelo conservando su rostro real (FLUX Kontext). |
| [GenOutFitFaceM](https://rafaumh2110.github.io/apps/genoutfitfacem/) | Como GenOutFitFace, permitiendo subir hasta dos prendas y elegir complementos (gafas, collares, bolsos, zapatos...). |
| [GenOutFitS](https://rafaumh2110.github.io/apps/genoutfits/) | Versión para alumnos de GenOutFit, con catálogo de modelos y parámetros limitados por el profesor. |
| [GenPatMod](https://rafaumh2110.github.io/apps/genpatmod/) | Genera patrones de corte de moda en SVG a partir de una idea y los exporta a PDF A4, con revisión del plan de piezas e historial local. |
| [GenPatModa](https://rafaumh2110.github.io/apps/genpatmoda/) | Versión para alumnos de GenPatMod, con catálogo de modelos y tokens limitados por el profesor. |
| [SearchLogMod](https://rafaumh2110.github.io/apps/searchlogmod/) | Consulta asistida por IA sobre métodos y logística de empresas de la industria de la moda, con estimación de coste y exportación a Markdown/texto/Word. |
| [SearchLogModCB](https://rafaumh2110.github.io/apps/searchlogmodcb/) | Versión de SearchLogMod con caché de resultados, caché de prompts de Anthropic y modo por lotes (cola propia o Batch API). |
| [TelemetriaWU](https://rafaumh2110.github.io/apps/telemetriawu/) | Consulta bajo demanda los datos de una estación meteorológica personal (Vevor YT60234 u otra compatible) dada de alta en Weather Underground / Earth Network, directamente desde el navegador. Primera app de una serie que irá incorporando sondeo continuo, histórico persistente y otras funcionalidades. |
| [TelemetriaWU Monitor](https://rafaumh2110.github.io/apps/telemetriawumonitor/) | Segunda app de la serie TelemetriaWU: sondeo continuo con backoff automático ante errores, lecturas en tarjetas gráficas con minigráficos en tiempo real, histórico de sesión y exportación a CSV. |
| [TelemetriaWU Histórico](https://rafaumh2110.github.io/apps/telemetriawuhistorico/) | Tercera app de la serie TelemetriaWU: igual que TelemetriaWU Monitor, pero con histórico PERSISTENTE guardado en IndexedDB (sobrevive a recargar la página), con retención configurable, purga automática y exportación a CSV de todo el histórico guardado. |
| [TelemetriaWU MQTT](https://rafaumh2110.github.io/apps/telemetriawumqtt/) | Cuarta app de la serie TelemetriaWU: igual que TelemetriaWU Histórico, añadiendo publicación de cada lectura en un topic MQTT sobre WebSocket (broker, topic, usuario/contraseña, QoS y retain configurables), con estado de conexión, contadores y registro de actividad independientes del sondeo. |
| [TelemetriaWU Gráficos](https://rafaumh2110.github.io/apps/telemetriawugraficos/) | Quinta app de la serie TelemetriaWU, a partir de TelemetriaWU Monitor: sustituye los minigráficos por gráficos de líneas a tamaño completo que muestran la evolución de cada parámetro (temperatura y punto de rocío, viento y racha, humedad, presión, lluvia), con leyenda, cursor cruzado con tooltip y navegación por teclado; histórico de sesión y exportación a CSV. |
| [TelemetriaWU Móvil](https://rafaumh2110.github.io/apps/telemetriawumovil/) | Sexta app de la serie TelemetriaWU: panel con aspecto de app nativa de iOS, instalable en la pantalla de inicio, con condiciones actuales (máximo/mínimo del día con hora), gráficos de evolución a lo largo del día completo (temperatura/rocío, presión, humedad, viento/racha, dirección del viento, lluvia), histórico del día persistente en IndexedDB con relleno opcional vía el endpoint de histórico de Weather Underground, hoja de ajustes, compartir y exportación a CSV. |
| [TelemetriaWU iPad](https://rafaumh2110.github.io/apps/telemetriawuipad/) | Séptima app de la serie TelemetriaWU: igual motor de datos que TelemetriaWU Móvil, con un diseño de dos paneles pensado para el ancho de un iPad (barra lateral persistente con navegación/ajustes/compartir/CSV y un área de contenido con tiles y gráficos en cuadrícula de varias columnas que se adapta sola, vía CSS grid, a cualquier modelo, orientación y Split View/Slide Over). |

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
  carpeta de app regenera `appindex/index.html` a partir de los
  metadatos (`data-app-title`, `data-app-description`, `data-categories`,
  `data-tags`) declarados en la etiqueta `<body>` de cada app, y hace
  commit del resultado automáticamente. No requiere ningún secreto:
  todo ocurre dentro de este mismo repositorio.

## Despliegue en un servidor propio (Apache)

Existe un paquete de scripts para instalar el portal `appindex/moda` y
las apps que enlaza en un servidor Linux (Debian) propio con Apache,
como alternativa o complemento a GitHub Pages. Pide ese paquete si lo
necesitas.

## Autor

Rafael Puerto — Departamento de Ingeniería de Sistemas y Automática. Universidad Miguel Hernández de Elche (UMH),  Contacto: r.puerto@umh.es
