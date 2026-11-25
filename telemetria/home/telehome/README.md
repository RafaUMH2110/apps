# TeleHome · Demostración

**Autor:** Rafa · Departamento de Ingeniería de Sistemas y Automática · Universidad Miguel Hernández de Elche · r.puerto@umh.es
*Generado con IA · Revisado por el autor*

App de telemetría del hogar en un solo fichero (`index.html`), **genérica**: la misma plantilla sirve para varios tipos de dispositivo, no solo para enchufes. Es la versión general de TeleHome y habla con su [servicio](https://github.com/RafaUMH2110/code/tree/main/telemetria/home/telehome-servicio) y está pensada para ir creciendo: cada tipo nuevo se declara en un catálogo y la interfaz sale de ahí.

En esta primera versión ya funcionan cuatro tipos: **enchufes** Wi-Fi (potencia, tensión, corriente y energía), **sensores de temperatura y humedad**, **luces regulables** y **persianas**. En el catálogo aparecen además, marcados como previstos, **termostato** y **contador general**.

## Documentación

| Documento | Para qué |
|---|---|
| [MANUAL_TELEHOME.md](MANUAL_TELEHOME.md) | Manual técnico: arquitectura, catálogo, API, niveles de acceso, despliegue y referencia |
| [INSTALACION.md](INSTALACION.md) | Instalar, configurar y poner en marcha, paso a paso |

## Estructura

El fichero tiene tres bloques de código, en este orden:

| Bloque | Qué es | Depende de |
|---|---|---|
| 1 · Catálogo | `TELEHOME_METRICS` (magnitudes) y `TELEHOME_TYPES` (tipos de dispositivo) | nada |
| 2 · Conexión | servicio real, adaptador del servicio heredado y motor de demostración | catálogo |
| 3 · Interfaz | contador, lista, controles, gráfica, resumen y ajustes | catálogo |

El bloque 2 solo hace falta en esta versión web: la página que sirva el propio servicio puede llevar solo los bloques 1 y 3 y hablar directamente con su API.

### Magnitudes comunes

`TELEHOME_METRICS` es una tabla común a todos los tipos (`p`, `v`, `i`, `t`, `h`, `br`, `pos`), con etiqueta, unidad, decimales y si el eje debe empezar en cero. Al ser comunes, **dos tipos que midan lo mismo se dibujan en la misma gráfica**: un sensor y un termostato comparten «Temperatura». Con la escala «Por dispositivo» (la de por defecto cuando hay varios) cada uno tiene su mini-gráfica con escala propia; «Común» las junta en una sola.

### Modelo de datos

Cada lectura, venga del servicio o de la demostración, tiene la misma forma:

```json
{ "ts": 1763645000, "online": true, "error": null,
  "state":  { "on": true },
  "values": { "p": 517.7, "v": 227.9, "i": 2.271 } }
```

Y cada dispositivo añade su tipo, su estancia y, si el tipo lo declara, un acumulado:

```json
{ "id": "lavadora", "type": "enchufe", "name": "Lavadora", "room": "Cocina",
  "slot": 1, "mode": "local", "reading": { }, "accum": { "energy_today_kwh": 6.23 } }
```

El histórico es `series[<id>] = [{ t, <magnitud>: valor, … }]`, con las claves de `METRICS`; el resumen es `devices[<id>] = { samples, availability, energy_kwh?, on_ratio?, m: { <magnitud>: { avg, min, max } } }`.

### Cómo se presentan los datos

- **Contador adaptativo**: el bloque grande es el del tipo que declara `hi.main` (los enchufes: potencia total, reparto por dispositivo y contador de energía del día). Los demás grupos aparecen como cifras destacadas al lado (temperatura media, luces encendidas, apertura media). Si no hay enchufes, el bloque grande pasa a ser el primer grupo que haya, así que la cabecera siempre dice algo útil.
- **Lista agrupada** por tipo (por omisión), por estancia o sin agrupar. Cada grupo lleva su propio total en la cabecera.
- **Fila de dispositivo**: estado, magnitud principal en grande con barra opcional, minigráfica de esa magnitud, magnitudes secundarias, acumulado y su control.
- **Controles** según el tipo: interruptor, interruptor + nivel, subir/parar/bajar, o «solo lectura».
- **Gráfica**: una magnitud a la vez, con los dispositivos que la miden; al elegir un dispositivo de otro tipo, la magnitud cambia a la principal de ese tipo.
- **Resumen**: una tabla por tipo, con las columnas que declara cada uno.

## Añadir un tipo de dispositivo

Una entrada en `TYPES` y nada más; no hay que tocar la interfaz:

```js
humedad_suelo: {
  label: "Sensor de suelo", plural: "Sensores de suelo", desc: "Humedad del sustrato",
  icon: "M12 3v18M6 9l6-6 6 6",            // trazo sobre una caja de 24×24
  metrics: ["h"], primary: "h", meta: [], bar: "h",
  control: "none", actions: [],
  hi: { kind: "avg", metric: "h", label: "Humedad del suelo" },
  summary: [ { key: "m.h.avg", label: "Media", unit: "%", dec: 0 },
             { key: "availability", label: "Disponibilidad", pct: true } ],
  fields: tuya([ dp("hum", "humedad", 3), code("hum", "humedad", "humidity_value"), scale("hum", "humedad", 1) ]),
  state: {},
  sim(d, t, st, H) { return { h: 40 + 10 * Math.sin(t / 4000 + H.seed(d.id)) }; },
},
```

Claves: `metrics` (de `METRICS`) y `primary`; `meta` y `bar` para la fila; `control` (`switch`, `level`, `position`, `setpoint`, `none`) y `actions`; `hi` para el contador (`sum`, `avg` o `count`, y `main: true` si debe llevar el bloque grande); `summary` con claves `m.<magnitud>.<avg|min|max|range>`, `energy_kwh`, `on_ratio` o `availability`; `accum` para un acumulado del día; `fields` para el formulario de alta (`only: "local"|"nube"` y `adv: true` para el apartado avanzado); `state` y `sim` solo para la demostración. Si un tipo lleva `soon`, aparece en el catálogo como previsto y no se puede dar de alta.

En el servicio, el tipo nuevo solo tiene que leer sus DPS o códigos y devolver las magnitudes en `reading.values`.

## Estancias

Al añadir o editar un dispositivo, la **estancia** se elige en un desplegable con las que ya existen, o se crea una nueva en el momento («＋ Nueva estancia…»). Con el servicio 0.13.0 la lista y su orden vienen de él (`api/state` → `rooms`) y la agrupación «Por estancia» los respeta; con un servicio anterior, el desplegable se arma con las estancias que ya usen los dispositivos. Definir, renombrar, borrar y ordenar estancias se hace en [TeleHome Pro](../telehome-pro/README.md).

## Modos de funcionamiento

| Modo | Cuándo | Qué hace |
|---|---|---|
| **Servicio TeleHome** | La página la sirve el propio servicio, o escribes en el pie su ruta en el mismo servidor (p. ej. `/rafa/telehome/`). Se reconoce porque `api/health` responde `"api": "telehome"` (o `"app": "TeleHome"`) | Todos los tipos que el servicio declare en `types`, con dispositivos reales |
| **Servicio anterior a la 0.5.0** (solo enchufes) | `api/health` responde `TeleHome Enchufes` **sin** `"api": "telehome"` (versiones hasta la 0.4.0) | Un adaptador traduce sus respuestas al modelo genérico: se ven y se controlan los enchufes reales, y los demás tipos quedan deshabilitados hasta actualizar el servicio. Desde la 0.5.0 el servicio habla el protocolo genérico y el adaptador ya no interviene |
| **Demostración** | No se encuentra ningún servicio (p. ej. en GitHub Pages) | Siete dispositivos simulados de los cuatro tipos; se pueden controlar, añadir y exportar a CSV. Los datos se guardan solo en el navegador (`localStorage`, clave `telehome_demo_v1`; «Reiniciar demo» los borra) |

Notas:

- La conexión solo admite rutas del **mismo servidor** (empiezan por `/`): el servicio rechaza otros orígenes.
- La nube de Tuya y la búsqueda en la red local necesitan el servicio real; en la demostración devuelven un aviso. Al importar desde la búsqueda, el tipo lo eliges tú: la difusión UDP no lo dice.
- Máximo 16 dispositivos.

## API del servicio

```
GET    api/health                      → { app: "TeleHome", version }
GET    api/state                       → opciones, tipos admitidos y dispositivos con su lectura
GET    api/history?dev=all&range=&points=
GET    api/summary?range=
GET    api/export.csv?dev=<id>&range=
POST   api/devices                     → alta (incluye type)
PUT    api/devices/<id>                → cambios
DELETE api/devices/<id>
POST   api/devices/<id>/command        → { action: "switch"|"level"|"position"|"stop"|"setpoint", value }
PUT    api/options · PUT api/cloud · POST api/cloud/test · POST api/cloud/devices
POST   api/cloud/import · POST api/discover · POST api/devices/import
```

`api/state` devuelve `types` con los tipos que admite el servicio: la app deshabilita en el alta los que no estén. Se mantiene `api/plugs/<id>/power` como alias de `command` con `action: "switch"`, y `plug=` como alias de `dev=`.

## Icono

El icono de la familia TeleHome (app genérica, iPhone, iPad y la interfaz del servicio) es una casa blanca con una línea de pulso (telemetría) sobre fondo azul. Fuente única: [`favicon.svg`](favicon.svg), con [`favicon.ico`](favicon.ico) (16, 32 y 48 px) y [`apple-touch-icon.png`](apple-touch-icon.png) (180 px, a sangre: iOS aplica su propio redondeo). Cada página lleva el SVG incrustado en `<link rel="icon">`, de modo que sigue siendo un solo fichero; la interfaz del servicio (repo `code`) incrusta también el PNG de iOS. Si cambias el icono, actualiza los cuatro HTML y los `apple-touch-icon.png` de `telehome-iphone/` y `telehome-ipad/`.
