# TeleMet Multi

App web de un solo archivo (`index.html`) para seguir **varias estaciones meteorológicas de Weather Underground a la vez**. Parte de TeleMet Historial y mantiene su estilo y sus gráficas.

## Qué hace
- **Estaciones**: alta, baja, activación, nombre y color de cada una; clave API propia o común. Importar/exportar la configuración en JSON.
- **Sondeo independiente** por estación con backoff propio; un error 401/403/404 solo detiene a esa estación. Estimación de cuota por clave (orientativa).
- **Ahora**: tarjeta por estación, tabla comparativa (máximo/mínimo resaltados y diferencia respecto a una referencia), extremos entre estaciones y mapa con fondo de OpenStreetMap (proyección Mercator, escala y norte).
- **Detalle**: 12 variables con mín/máx de 24 h y minigráfico.
- **Gráficas**: 12 h, 24 h o 7 días; modo *Comparar* (todas las estaciones superpuestas) o *Una estación* (todas sus variables); chips para mostrar u ocultar estaciones y variables; tooltip con todas las estaciones.
- **Resumen de 7 días** y **consulta de un día concreto** (completa los huecos con el histórico de la API).
- **Datos y servidor**: histórico persistente por estación (IndexedDB, 9 días), sincronización con los JSON de TeleMet Colector, relleno de huecos desde la API, CSV (24 h / 7 días / todo) y borrado.

## Unión del histórico con la primera lectura y relleno de 7 días
Al cargar la app, al pulsar **Iniciar** y al elegir la ventana **7 d**, la app revisa los últimos 7 días de cada estación (lo guardado en el navegador más lo del colector). Si encuentra huecos, pide a la API el histórico de cada día afectado y añade solo lo que falta, para que las líneas de la gráfica sean continuas.
- Hoy y ayer: se mira la ventana de las últimas 24 h y se rellena todo hueco de más de 15 min.
- Días anteriores: se rellenan los días con huecos grandes (más de 90 min).
- Coste: hasta 7 peticiones por estación (la API entrega un día por petición). Para ahorrar cuota no se repite el mismo día en 20 min (hoy y ayer) ni en 12 h (días anteriores).
- Si la API no tiene datos para un tramo, el hueco se queda como hueco: nunca se une con una recta inventada.

## Mapa con fondo OpenStreetMap
El mapa de la pestaña *Ahora* dibuja las estaciones sobre teselas de OpenStreetMap, con escala, indicador de norte y atribución. Se puede desactivar con la casilla «Mapa de fondo (OpenStreetMap)»; sin fondo se muestra una cuadrícula neutra. Las teselas se cargan desde `tile.openstreetmap.org`, de modo que el navegador contacta con ese servicio solo mientras el fondo está activado.

## Uso
Abrir `index.html` (o la versión publicada en GitHub Pages), añadir cada estación (Station ID y API Key) y pulsar **Iniciar**. Los datos y las claves se guardan solo en el navegador.

## Integración con TeleMet Colector
Con el colector multiestación, cada estación genera `historial_<ID>.json` (o `history_<ID>.json`). Indica en *Datos y servidor* la carpeta (por defecto `datos/`; usa `../historial/datos/` si el colector escribe junto a TeleMet Historial). La app solo **añade** lecturas que faltan; nunca borra lo local.

Si en la carpeta indicada no hay archivo, la app prueba también `../telemethistorial/datos/`, `../telemethistory/data/`, `../historial/datos/` y `../history/data/` (las carpetas habituales de TeleMet Historial/History junto a esta app). En la tabla de sincronización, al pasar el ratón por «sincronizado» se ve el archivo leído y, por «sin archivo», dónde se ha buscado.
