# Historial de cambios

Orden: más reciente primero. Sustituye a los párrafos fechados que había en el README.

## 2026-11-08 — Mantenimiento del repositorio

- Un único workflow (`portal-y-pages.yml`) regenera el portal y despliega Pages; el despliegue ya parte del portal actualizado y se genera también `appindex/temas/`.
- Pages deja de publicar `.github/` y los `.zip`.
- Eliminados los cuatro `appindex/icons/files*.zip` (los iconos ya estaban extraídos) y el workflow anidado `appindex/.github/`.
- Aplicados los cambios de los manuales del colector de la rama `telemet-multi-intervalo-y-enlaces` (8da4be8).
- El README deja de llevar el registro de cambios por fechas: pasa a este fichero.

## 2026-11-07 — TeleMet MultiStation

Nueva app `telemetria/telemet/multistation/`: versión en inglés de TeleMet Multi (misma funcionalidad, interfaz y comentarios en inglés, formato de fechas y números en-GB). Usa su propio almacenamiento (`telemetmultistation_*`, IndexedDB `telemetmultistation_db`) para convivir con la versión española, y busca primero los archivos del colector en inglés (`data/history_<ID>.json`, `../telemethistory/data/`) y después los españoles. La documentación de TeleMet Collector apunta ahora a esta versión.

## 2026-11-06 — TeleMet Multi

Nueva app `telemetria/telemet/multi/` para seguir varias estaciones a la vez. Lee el histórico de cada una desde `historial_<ID>.json` (TeleMet Colector multiestación), de modo que apuntando su carpeta de datos a `../historial/datos/` se completan las gráficas sin esperar a acumular lecturas en el navegador.

## 2026-11-05 — Gráficas combinadas de doble eje

En todas las apps de `telemetria/` que muestran estas variables (TeleMet Pro, Historial, Cal, Cal Vivo y la versión inglesa History; TeleMet Mobile/iPad y sus variantes Pro y Cal; TelemetriaWU Móvil e iPad), la radiación solar y el índice UV comparten gráfica (UV en el eje derecho), igual que la tasa de lluvia y la lluvia acumulada (acumulada en trazo discontinuo y eje derecho). Ambos ejes comparten rejilla, la leyenda indica unidades y eje de cada serie y el tooltip muestra los dos valores con su unidad. En las apps de la familia TeleMet Pro/Historial/Cal/Cal Vivo/History las mismas dos gráficas combinadas aparecen también en las de 7 días (y en la consulta de un día concreto de Historial). Las gráficas de 7 días de las apps móviles/iPad y las apps sin estas variables (TeleMet, versiones Lite, TelemetriaWU/Monitor/Histórico/MQTT/Gráficos) no cambian.

## 2026-11-05 — Ventana de 12 h / 24 h

TeleMet Historial y su versión inglesa TeleMet History incorporan, en el panel de evolución de horas, un selector 12 h / 24 h que cambia la ventana de todas las gráficas (eje X, umbral de huecos y mensajes se adaptan) y se recuerda en el navegador. Las 24 h se construyen con el histórico local (retención de 9 días) y con el JSON del colector, que ahora guarda 24 h por defecto (configurable con `duracion_horas`, `--horas` o `TELEMET_HORAS`).
