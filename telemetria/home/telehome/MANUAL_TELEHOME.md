# TeleHome · Manual técnico

**Autor:** Rafael Puerto · Departamento de Ingeniería de Sistemas y Automática · Universidad Miguel Hernández de Elche · r.puerto@umh.es
*Generado con IA · Revisado por el autor*

Referencia completa de **TeleHome**: la app web, el servicio que la alimenta, el protocolo que hablan entre
los dos, los niveles de acceso y el despliegue. Para instalarlo paso a paso está la
[guía de instalación](INSTALACION.md); este manual explica **cómo funciona y por qué**, y sirve de referencia
cuando haya que tocar algo.

Versión del servicio documentada: **0.13.0**. Cada apartado indica desde qué versión existe lo que describe.

---

## Índice

1. [Panorama](#1-panorama)
2. [Arquitectura](#2-arquitectura)
3. [Piezas y dónde vive cada una](#3-piezas-y-dónde-vive-cada-una)
4. [El catálogo de tipos](#4-el-catálogo-de-tipos)
5. [Modelo de datos](#5-modelo-de-datos)
6. [Protocolo: la API del servicio](#6-protocolo-la-api-del-servicio)
7. [Seguridad y niveles de acceso](#7-seguridad-y-niveles-de-acceso)
8. [Conexión: cómo la app encuentra el servicio](#8-conexión-cómo-la-app-encuentra-el-servicio)
9. [La interfaz de la app genérica](#9-la-interfaz-de-la-app-genérica)
10. [Las versiones de iPhone y iPad](#10-las-versiones-de-iphone-y-ipad)
11. [Modo demostración](#11-modo-demostración)
12. [Exportar e importar la configuración](#12-exportar-e-importar-la-configuración)
13. [Almacenamiento](#13-almacenamiento)
14. [Línea de órdenes](#14-línea-de-órdenes)
15. [Despliegue](#15-despliegue)
16. [Programaciones](#16-programaciones)
17. [Añadir un tipo de dispositivo nuevo](#17-añadir-un-tipo-de-dispositivo-nuevo)
18. [Desarrollo y pruebas](#18-desarrollo-y-pruebas)
19. [Solución de problemas](#19-solución-de-problemas)
20. [Límites conocidos](#20-límites-conocidos)
21. [Referencia rápida](#21-referencia-rápida)

---

## 1. Panorama

TeleHome monitoriza y maneja los dispositivos conectados de una vivienda desde el navegador. Nació como
**TeleHome Enchufes**, que solo sabía de enchufes Wi-Fi Tuya, y se generalizó: hoy una misma plantilla sirve
para enchufes, sensores de temperatura y humedad, luces regulables y persianas, y admitir un tipo nuevo es
añadir una entrada a un catálogo.

Qué hace:

- **Lee** los dispositivos cada pocos segundos y guarda el histórico en SQLite.
- **Manda órdenes**: encender y apagar, regular el brillo, subir y bajar persianas.
- **Presenta** los valores del momento, un histórico por magnitud, un resumen por tipo y exportación a CSV.
- **Separa quién puede hacer qué** en tres niveles: mirar, manejar y configurar.

- **Programa** encendidos y apagados por hora, amanecer o anochecer (apartado 16).

Qué **no** hace: no es un sistema de automatización completo. No hay escenas, ni reglas encadenadas, ni avisos, ni
condiciones que dependan de otro dispositivo. No habla con asistentes de voz ni con HomeKit.

---

## 2. Arquitectura

```
┌──────────────────────┐        HTTP (JSON)         ┌─────────────────────────┐      Wi-Fi local
│  App TeleHome        │ ─────────────────────────► │  Servicio TeleHome      │ ───────────────────► Enchufes,
│  (una página HTML)   │ ◄───────────────────────── │  (Python, systemd)      │ ◄─────────────────── sensores…
│  navegador           │   /rafa/telehome/api/…     │  127.0.0.1:8765         │
└──────────────────────┘                            │                         │      HTTPS
          ▲                                         │  SQLite + config.json   │ ───────────────────► Nube de
          │ HTML estático                           └─────────────────────────┘ ◄─────────────────── Tuya
┌─────────┴────────────┐                                        ▲
│  Apache              │────────── proxy inverso ───────────────┘
│  /var/www/htdocs     │           <Location /rafa/telehome/>
└──────────────────────┘
```

Tres piezas, cada una con una responsabilidad:

**La app** es un único `index.html` sin dependencias externas: HTML, CSS y JavaScript en el mismo fichero, sin
`fetch` a nada que no sea el servicio. Se puede abrir desde cualquier sitio que la sirva. No guarda datos de
dispositivos: todo lo pide al servicio en cada ciclo.

**El servicio** es un programa Python que corre como servicio de systemd, escucha en `127.0.0.1:8765`, sondea
los dispositivos, guarda las lecturas y expone la API. Es el único que conoce las credenciales.

**Apache** sirve la app como fichero estático y hace de proxy inverso hacia el servicio bajo una misma ruta,
`/rafa/telehome/`. Que la app y la API salgan del mismo origen es lo que evita tener que tocar CORS.

### Por qué el servicio escucha solo en localhost

El servicio no está pensado para exponerse a la red. Escucha en `127.0.0.1` y es Apache quien decide quién
llega hasta él. Así la autenticación, el registro de accesos y, donde lo haya, el HTTPS son los de Apache, que
es software hecho para eso. El servicio añade por su cuenta varias comprobaciones (apartado 7) por si alguien
lo publica directamente.

---

## 3. Piezas y dónde vive cada una

| Pieza | Repo | Ruta |
|---|---|---|
| App genérica (web) | `apps` | `telemetria/home/telehome/index.html` |
| App para iPhone | `apps` | `telemetria/home/telehome-iphone/` |
| App para iPad | `apps` | `telemetria/home/telehome-ipad/` |
| Servicio (Python) | `code` | `telemetria/home/telehome-servicio/` |
| Interfaz que sirve el servicio | `code` | `telemetria/home/telehome-servicio/telehome/static/index.html` |
| Instaladores | `code` | `scripts/instalar-todo/` |

Dentro del paquete Python:

| Módulo | Qué hace |
|---|---|
| `cli.py` | Línea de órdenes y arranque del servicio |
| `server.py` | Servidor HTTP, rutas, sesiones y niveles |
| `config.py` | `config.json`: validación, opciones, contraseñas, exportar e importar |
| `monitor.py` | Hilo de sondeo: lee los dispositivos y manda órdenes |
| `devices.py` | Diálogo con los dispositivos (modo local, TinyTuya) y descubrimiento en red |
| `cloud.py` | Diálogo con la nube de Tuya y recuento de llamadas |
| `store.py` | SQLite: lecturas, histórico, resumen, CSV, retención |
| `scheduler.py` | Hilo de programaciones: decide qué toca y lo dispara |
| `sun.py` | Amanecer y anochecer (algoritmo del NOAA), sin dependencias |
| `static/index.html` | La interfaz que el propio servicio sirve en `/` |

> **Nota sobre los nombres.** El servicio se llama `telehome` (unidad de systemd, `/opt/telehome`,
> `/var/lib/telehome`, orden `telehome`). En el repo `code`, la carpeta es `telehome-servicio` y el módulo
> Python `telehome`. Hasta la 0.9.0 la carpeta y el módulo se llamaban `telehome-enchufes` / `telehome_enchufes`
> y `api/health` devolvía `"app": "TeleHome Enchufes"`; ahora devuelve `"app": "TeleHome"`.

---

## 4. El catálogo de tipos

Es la pieza central del diseño de la app genérica. Está en el **primer bloque `<script>`** de `index.html` y
define dos objetos: `TELEHOME_METRICS` (las magnitudes) y `TELEHOME_TYPES` (los tipos de dispositivo).
De cada entrada de `TYPES` salen, sin escribir ni una línea de interfaz:

- el selector y el formulario de alta,
- la fila del dispositivo: valor grande, barra y valores secundarios,
- su control: interruptor, nivel, posición o solo lectura,
- las magnitudes que ofrece la gráfica,
- las columnas del resumen,
- el simulador del modo demostración.

### Magnitudes (`METRICS`)

| Clave | Etiqueta | Unidad | Decimales | Empieza en cero |
|---|---|---|---|---|
| `p` | Potencia | W | 1 | Sí |
| `v` | Tensión | V | 1 | No |
| `i` | Corriente | A | 3 | Sí |
| `t` | Temperatura | °C | 1 | No |
| `h` | Humedad | % | 0 | Sí |
| `br` | Brillo | % | 0 | Sí |
| `pos` | Apertura | % | 0 | Sí |

«Empieza en cero» decide si el eje vertical arranca en 0 (potencia) o se ajusta al rango de los datos
(temperatura). Dos tipos que midan la misma clave se dibujan juntos en la gráfica.

### Tipos

| Clave | Etiqueta | Mide | Control | Órdenes |
|---|---|---|---|---|
| `enchufe` | Enchufe | `p`, `v`, `i` | interruptor | `switch` |
| `sensor-th` | Sensor T/H | `t`, `h` | ninguno | — |
| `luz` | Luz | `br` | nivel + panel de luz | `switch`, `level`, `temp`, `color`, `mode` |
| `persiana` | Persiana | `pos` | posición | `position`, `stop` |
| `termostato` | Termostato | `t` | consigna | *previsto* |
| `contador` | Contador general | `p` | ninguno | *previsto* |

Los marcados como previstos llevan la propiedad `soon` y aparecen en el catálogo de la app, pero no se pueden
dar de alta.

### Campos de una entrada de `TYPES`

| Campo | Para qué |
|---|---|
| `label`, `plural`, `desc` | Nombres que ve el usuario |
| `icon` | La `d` de un `<path>` SVG de 24×24 |
| `metrics` | Magnitudes que mide, en orden |
| `primary` | La que se muestra en grande en la fila |
| `meta` | Las que acompañan en la línea secundaria |
| `bar` | La que dibuja la barra de nivel (opcional) |
| `control` | `switch`, `level`, `position`, `setpoint` o `none` |
| `actions` | Órdenes que acepta; el servicio las valida por su cuenta |
| `accum` | Magnitud acumulada del día (`energy_today_kwh` en el enchufe) |
| `hi` | Cifra destacada del grupo: `sum`, `avg` o `count` |
| `summary` | Columnas de la tabla de resumen |
| `note` | Aclaración al pie de su tabla |
| `fields` | Campos del formulario de alta |
| `state` | Estado inicial en el simulador |
| `sim` | Función que inventa lecturas en modo demostración |

### Luces

Una luz (`luz`) lleva en su lectura `state: {on, br, temp, mode, color:{h,s,v}, hex}` y `values: {br}` (0 si está
apagada). Todo viaja en las mismas unidades, sean cuales sean las de la bombilla: brillo y blanco de 0 a 100
(blanco: 0 cálido, 100 frío), color con `h` de 0 a 360 y `s`, `v` de 0 a 100. El servicio convierte a la escala de Tuya.

Cada dispositivo de luz trae además `caps` (`mode`, `level`, `temp`, `color`): lo que **esa** bombilla sabe hacer, deducido
de los códigos que devuelve. La app lo usa para decidir qué controles ofrece: una bombilla solo blanca no enseña el
selector de color. Si el servicio no manda `caps` (anterior a la 0.10.0) solo se ofrece el brillo.

En la fila de una luz hay, junto al interruptor y el deslizador de brillo, un botón de **paleta** (si la luz admite
blanco o color). Abre el **panel de luz**: interruptor, brillo, selector *Blanco / Color* (si admite ambos), el
deslizador cálido↔frío con tres blancos rápidos, o bien el tono y la intensidad del color con ocho colores rápidos.
Cada cambio se manda al soltar el deslizador, y el panel se repinta con lo que el servicio responde. En modo color el
brillo es el valor `v` del color: bajar el brillo oscurece el color, no cambia otro código. Las apps de iPhone y de iPad
tienen el mismo panel como hoja inferior.

En una programación, la acción de una luz puede ser `switch`, `level`, `temp`, `color` o `mode`. Las opciones del
formulario dependen del dispositivo elegido y de sus `caps`. «Cálido al 30 % a las 21:00» son dos programaciones
(`temp` 10 y `level` 30), porque cada una lleva una sola orden.

**Una bombilla importada como enchufe.** Las versiones de TeleHome anteriores a la 0.10.0 daban de alta toda bombilla de
Smart Life como *enchufe*. El servicio 0.10.0 se da cuenta (el dispositivo responde con códigos de luz), la convierte a
`luz` por sí solo y conserva nombre, estancia, Device ID y clave. También puede hacerse a mano: *Ajustes → Dispositivos
→ Editar → Tipo*; al cambiar el tipo se ponen los códigos por defecto de ese tipo. Al importar desde la nube, el tipo
sale de la categoría de Tuya (`dj`, `dd`, `xdd`, `fwd`, `dc`, `tgq` → luz).

**Más allá de lo básico.** Escenas guardadas, grupos, transiciones, temporizadores y parámetros por bombilla (servicio 0.11.0) no están en esta app: viven en la versión avanzada, [TeleHome Pro](../telehome-pro/README.md).

### Columnas del resumen

Cada entrada de `summary` tiene `key`, `label` y opcionalmente `unit`, `dec`, `pct`, `bar` y `total`. La clave
puede ser directa (`energy_kwh`, `availability`, `on_ratio`) o referirse al bloque de magnitudes con la forma
`m.<magnitud>.<agregado>`, donde el agregado es `avg`, `min`, `max` o `range`. Con `total: "sum"` la columna
lleva fila de totales.

---

## 5. Modelo de datos

### La lectura

Es el contrato entre el servicio y la app. El servicio solo tiene que devolver, por cada dispositivo:

```json
{
  "ts": 1795359880.71,
  "online": true,
  "error": null,
  "state":  { "on": true },
  "values": { "p": 28.3, "v": 230.3, "i": 0.123 }
}
```

- `ts`: instante de la lectura, en **segundos** epoch (no milisegundos).
- `online`: si se pudo hablar con el dispositivo.
- `error`: texto del fallo, o `null`.
- `state`: lo que se puede mandar cambiar (`on`, `br`, `pos`). En una luz, además `temp`, `mode`, `color` y `hex`
  (ver «Luces» más abajo).
- `values`: lo que se mide, con las claves de `METRICS`.

Los campos planos antiguos (`on`, `power_w`, `voltage_v`, `current_a`) se siguen enviando para que las apps
anteriores funcionen.

### El dispositivo

```json
{
  "id": "nevera", "name": "Nevera", "room": "Cocina", "type": "enchufe",
  "slot": 0, "mode": "local",
  "reading": { … },
  "accum": { "energy_today_kwh": 0.183 },
  "energy_today_kwh": 0.183,

  "dev_id": "bf1234…", "ip": "Auto", "version": "3.3", "has_key": true,
  "dp_switch": 1, "dp_power": 19, "code_power": "cur_power", "scale_power": 10
}
```

`room` es el nombre de la estancia, no un identificador: es lo que enlaza el dispositivo con la lista de
`rooms` del estado, y por eso renombrar una estancia reescribe el campo en todos los suyos.

`id` es el identificador interno, derivado del nombre. `slot` fija el color de la serie (0-6) y no cambia
aunque se borren otros dispositivos. **Los campos del segundo bloque solo se envían a un administrador**
(apartado 7). La *Local Key* no sale nunca por la API: solo `has_key`.

### El punto del histórico

```json
{ "t": 1795359880, "p": 28.3, "v": 230.3, "i": 0.123, "on": 1, "online": 1 }
```

`t` es el **instante**, agregado en cubos cuya anchura sale de dividir el intervalo pedido entre el número de
puntos; dentro de cada cubo los valores son medias.

> **Cuidado con la clave `t`.** En este formato plano `t` significa tiempo, y en `METRICS` significa
> temperatura. Mientras el servicio solo sirva enchufes no hay choque, pero cuando admita sensores tendrá que
> incluir también un objeto `values` en cada punto. Las apps ya lo contemplan: leen el valor de `values`
> cuando viene, y nunca interpretan la `t` plana como temperatura.

### El resumen

Por dispositivo e intervalo:

```json
{
  "energy_kwh": 1.0174, "avg_w": 443.4, "max_w": 611.2, "samples": 8640,
  "availability": 1.0, "on_ratio": 0.83, "v_max": 233.0, "v_min": 227.0,
  "m": { "p": {"avg": 443.4, "min": 0.0, "max": 611.2},
         "v": {"avg": 230.1, "min": 227.0, "max": 233.0},
         "i": {"avg": 1.93,  "min": 0.0,  "max": 2.66} }
}
```

`availability` y `on_ratio` son fracciones de 0 a 1; la app las muestra como porcentaje. La energía se integra
por trapecios sobre la potencia medida, ignorando los huecos de más de 120 s para que un corte no invente
consumo.

### La base de datos

SQLite, una tabla de lecturas y otra con el recuento diario de llamadas a la nube:

```sql
CREATE TABLE readings (
    ts INTEGER NOT NULL, plug TEXT NOT NULL, online INTEGER NOT NULL,
    on_ INTEGER, power REAL, voltage REAL, current REAL);
CREATE TABLE api_calls (day TEXT PRIMARY KEY, n INTEGER NOT NULL);
```

El esquema todavía habla de `plug` y de las tres magnitudes del enchufe: es la parte que falta por generalizar
(apartado 20). La retención se aplica al vuelo según `retention_days`.

### El CSV

Una fila por lectura, con cabecera:

```
fecha_hora_utc,epoch,enchufe,en_linea,encendido,potencia_w,tension_v,corriente_a
2026-11-22T15:08:31Z,1795359511,nevera,1,1,88.4,228.4,0.387
```

La fecha va en UTC para que no dependa de la zona horaria de quien lo abra; `epoch` está al lado para
ordenar y calcular sin ambigüedad.

---

## 6. Protocolo: la API del servicio

Todo cuelga de `api/` bajo la ruta donde esté publicado el servicio. Las respuestas son JSON salvo el CSV y la
página de la interfaz.

### Reglas generales

- **Lectura** (`GET`) y **escritura** (el resto) se tratan distinto: lo que cambia algo exige la cabecera
  `X-TeleHome: 1`, comprueba el `Origin` y necesita el nivel adecuado.
- **Cabeceras de la app**: `X-TeleHome: 1` siempre; `X-TeleHome-Admin: <token>` cuando hay sesión;
  `Authorization: Basic` cuando el servicio tiene contraseña.
- **Errores**: `{"error": "texto en español"}` con el código HTTP correspondiente. Un 403 por nivel
  insuficiente añade `"admin_required": true` y `"nivel_necesario": "user"` o `"admin"`.

| Código | Cuándo |
|---|---|
| 400 | Datos no válidos (lo lanza `ConfigError`) |
| 401 | Falta la contraseña del servicio |
| 403 | Host u origen no permitido, o nivel insuficiente |
| 404 | Ruta o dispositivo inexistente |
| 409 | Ya hay una búsqueda en curso |
| 502 | Error hablando con el dispositivo o con la nube |
| 500 | Error interno (se registra con traza) |

### Lectura

| Ruta | Devuelve |
|---|---|
| `GET /` | La interfaz del servicio, con su `Content-Security-Policy` |
| `GET api/health` | `{app, version, ok, api:"telehome", types, admin_required, user_required}` |
| `GET api/state` | Estado completo (abajo) |
| `GET api/history?dev=<id\|all>&range=<s>&points=<n>` | `{from, to, series:{<id>:[punto…]}}` |
| `GET api/summary?range=<s>` | `{from, to, devices:{…}, plugs:{…}}` |
| `GET api/export.csv?dev=<id>&range=<s>` | CSV con `Content-Disposition: attachment` |

`points` va de 50 a 2000 (400 por omisión); `range` se recorta al máximo que permita la retención.
`dev` es el nombre genérico y `plug` el de las apps anteriores: valen los dos.

`api/health` es lo que usa la app para reconocer el servicio: le basta `api: "telehome"`.

**`api/state`** devuelve:

```json
{
  "app": "TeleHome", "version": "0.9.0", "api": "telehome",
  "types": ["enchufe"], "max_devices": 7, "server_time": 1795359880.7,
  "simulate": false, "features": ["estancias", …], "limits": { "max_rooms": 24, … },
  "rooms": [ { "id": "cocina", "name": "Cocina", "devices": 2 } ],
  "admin":  { "required": true, "active": false },
  "sesion": { "nivel": "user", "admin_required": true, "user_required": true, "puede_mandar": true },
  "options": { … }, "regions": { … },
  "cloud": { "configured": false, "calls": 0, "today": 0, "yesterday": 0,
             "month": 0, "last30": 0, "by_day": [{"day":"2026-11-22","n":0}] },
  "devices": [ … ]
}
```

`types` dice qué tipos sabe leer **este** servicio: la app deshabilita en el alta los que no estén.
`sesion` existe desde 0.8.0; `admin` se mantiene para las apps anteriores.

`features` y `rooms` existen desde 0.13.0. `features` es la lista de lo que admite el servicio y es como la app
decide qué enseñar: sin `"estancias"` no ofrece gestionarlas y se limita a listar las que ya usen los
dispositivos. `rooms` va en el orden elegido por el usuario, y cada entrada trae cuántos dispositivos tiene.

### Dispositivos

| Ruta | Para qué | Nivel |
|---|---|---|
| `POST api/devices/<id>/command` | Orden genérica `{"action":…,"value":…}` | usuario |
| `POST api/plugs/<id>/power` | `{"on": true\|false}` (compatibilidad) | usuario |
| `POST api/devices` | Alta | admin |
| `PUT api/devices/<id>` | Modificación | admin |
| `DELETE api/devices/<id>?keep_history=1` | Baja | admin |
| `POST api/devices/import` | `{"devices":[…],"mode":"local"\|"nube"}` | admin |
| `POST api/discover` | Busca por UDP en la red local | admin |

Órdenes de `command`: `switch` (booleano), `level` (0-100), `position` (0-100) y `stop` (sin valor) y, solo para
luces (servicio 0.10.0 o posterior), `temp` (0 cálido … 100 frío), `color` (`"#rrggbb"` o `{h,s,v}`) y `mode`
(`white` o `colour`). `level`, `temp` y `color` encienden la luz; `mode` no. El servicio comprueba que el tipo las
admita y devuelve 400 si no. Para una luz la respuesta trae su estado completo (`state`).

### Estancias

Desde 0.13.0. Una estancia es un nombre con un orden; el vínculo con el dispositivo es su campo `room`, por
nombre y no por identificador.

| Ruta | Para qué | Nivel |
|---|---|---|
| `POST api/rooms` | Alta: `{"name": "Cocina"}` | admin |
| `PUT api/rooms/<id>` | Renombrar: `{"name": "Sala de estar"}` | admin |
| `DELETE api/rooms/<id>` | Baja | admin |
| `PUT api/rooms` | Reordenar: `{"ids": ["salon", "cocina", …]}` | admin |

Renombrar cambia el nombre **en todos los dispositivos de esa estancia**, en la misma operación; la respuesta
dice a cuántos ha afectado. Borrar deja sus dispositivos con `room` vacío y **no borra ninguno**. Los nombres
se normalizan (espacios de sobra fuera, 24 caracteres como mucho) y no se repiten, sin distinguir mayúsculas.
Una estancia escrita a mano al dar de alta un dispositivo se añade sola a la lista.

### Opciones, nube y contraseñas

| Ruta | Para qué | Nivel |
|---|---|---|
| `PUT api/options` | `poll_interval`, `cloud_poll_interval`, `retention_days` | admin |
| `PUT api/password` | Contraseña del servicio (0.7.1) | admin |
| `PUT api/admin/password` | Contraseña de administrador (0.7.0) | admin |
| `PUT api/user-password` | Contraseña de usuario de confianza (0.8.0) | admin |
| `PUT api/cloud` | Credenciales de Tuya | admin |
| `POST api/cloud/test` | Prueba la conexión | admin |
| `POST api/cloud/devices` | Lista los dispositivos de la cuenta | admin |
| `POST api/cloud/import` | `{"dev_ids":[…]}` | admin |

Las tres contraseñas aceptan `{"password": "…"}` o `{"quitar": true}`, y exigen un mínimo de 8 caracteres.

### Sesión

| Ruta | Para qué |
|---|---|
| `POST api/login` | `{"password":…}` → `{nivel, token, expires_in}` (0.8.0) |
| `POST api/logout` | Cierra la sesión del token enviado |
| `POST api/admin/login` | Igual, pero solo acepta la de administrador (compatibilidad) |
| `POST api/admin/logout` | Alias de `logout` |

### Configuración completa

| Ruta | Para qué | Nivel |
|---|---|---|
| `POST api/config/export` | Descarga toda la configuración; admite `{"ruta": "/rafa/telehome/"}` | admin |
| `POST api/config/import` | `{"config": {…}, "modo": "reemplazar"\|"añadir"}` | admin |

La exportación va por `POST`, y no por `GET`, justamente para que exija `X-TeleHome` y ninguna otra web pueda
pedirla con un simple enlace.

---

## 7. Seguridad y niveles de acceso

Hay cuatro barreras independientes. Conviene no confundirlas, porque resuelven cosas distintas.

### 7.1. Contraseña del servicio: quién entra

Es autenticación HTTP Basic sobre **todo** el servicio, incluida la lectura. Sin ella no se ve nada. El
usuario da igual; solo cuenta la contraseña. Se guarda con PBKDF2-SHA256 y 200 000 iteraciones, así que **no
se puede recuperar**: solo sustituir.

```bash
sudo telehome password            # poner o cambiar
sudo telehome password --quitar
```

Desde 0.7.1 también se cambia desde *Ajustes → Opciones → Contraseña del servicio*, siendo administrador.

### 7.2. Niveles: quién puede qué

Dos contraseñas más, independientes de la anterior, reparten permisos entre quienes ya han entrado:

| Con qué entras | Ve los datos | Maneja los dispositivos | Configura y cambia contraseñas |
|---|---|---|---|
| Nada | Sí | No | No |
| Contraseña de usuario (0.8.0) | Sí | Sí | No |
| Contraseña de administrador (0.7.0) | Sí | Sí | Sí |

```bash
sudo telehome admin-password
sudo telehome user-password
```

**Si no hay ninguna de las dos puestas, el servicio está abierto**: cualquiera que llegue puede configurarlo
todo. Es el comportamiento de siempre, y el que tiene sentido en una instalación local.

Quien no es administrador recibe una vista recortada de `api/state`: sin `dev_id`, `ip`, `version`,
`has_key`, ni los campos `dp_*`, `code_*` y `scale_*`; sin credenciales de la nube y con el recuento de
llamadas a cero. No es solo que la interfaz lo oculte: el servicio no lo manda.

**Las sesiones** son un token aleatorio de 32 bytes que la app envía en `X-TeleHome-Admin`. Duran 12 horas,
hay como mucho 50 a la vez (se descartan las más antiguas) y viven en `sessionStorage`, así que se pierden al
cerrar la pestaña. Los tokens llevan una huella de las dos contraseñas: **cambiar cualquiera de ellas
invalida todas las sesiones abiertas**, salvo la del administrador que hace el cambio, que recibe un token
nuevo en la respuesta.

> Poner contraseña de usuario sin poner la de administrador deja la configuración accesible solo desde la
> línea de órdenes. La orden lo avisa.

### 7.3. Host y origen: contra el DNS rebinding y el CSRF

- **Lista de hosts.** Si el servicio escucha en loopback, solo acepta peticiones cuyo `Host` sea
  `localhost`, `127.0.0.1`, `::1` o uno de los `--allow-host`. Protege del *DNS rebinding*: una web
  malintencionada que resuelva su nombre a 127.0.0.1 no puede hablar con el servicio.
- **Cabecera `X-TeleHome`.** Toda escritura la exige. Un formulario HTML de otra web no puede ponerla.
- **Comprobación de `Origin`.** En las escrituras, si viene `Origin` y no es el mismo host ni uno autorizado,
  se rechaza con 403.

Al reinstalar hay que **repetir todas las opciones**: el instalador reescribe la unidad de systemd con lo que
se le pase, así que un `--allow-host` que se olvide desaparece.

### 7.4. CORS: usar la API desde otra web

Solo para los orígenes de `--allow-origin`. Para ellos el servicio responde al *preflight* `OPTIONS` con
`Access-Control-Allow-Origin`, `-Credentials`, `-Methods`, `-Headers` (incluidas `X-TeleHome`,
`X-TeleHome-Admin` y `Authorization`) y `Access-Control-Allow-Private-Network`.

```bash
telehome serve --allow-origin https://rafaumh2110.github.io
```

Dos avisos: una página servida por **https** no puede llamar a un servicio **http**, porque el navegador lo
bloquea como contenido mixto; y la app manda `credentials: "include"` cuando la base es absoluta, para que
viajen la contraseña del servicio y las cookies.

### 7.5. Qué no sale nunca por la API

La *Local Key* de los dispositivos, el *Access Secret* de Tuya y las tres contraseñas (guardadas como hash).
`config.json` se escribe con permisos 600 y de forma atómica, mediante fichero temporal y `os.replace`.

---

## 8. Conexión: cómo la app encuentra el servicio

La app genérica admite tres modos y los recuerda en el navegador:

1. **Servicio real**, por una ruta del mismo servidor (`/rafa/telehome/`) o por una URL completa
   (`http://127.0.0.1:8765/`), que exige `--allow-origin`.
2. **Servicio heredado** (anterior a la 0.5.0, que se anunciaba como «TeleHome Enchufes»), mediante un adaptador que traduce el protocolo antiguo. Solo se ven
   enchufes, y la app lo avisa en un cartel.
3. **Demostración** (apartado 11).

Al arrancar prueba la ruta guardada y, si no, la ruta de la propia página. El sondeo es un `GET api/health`
con un límite de 2,5 s; si responde con `api: "telehome"` o `app: "TeleHome"` usa el protocolo genérico, y si
responde `app: "TeleHome Enchufes"` sin más (servicio heredado), el adaptador.

Cuando el sondeo falla, el cartel del pie dice **por qué**, que es lo que suele ahorrar la depuración:

| Respuesta | Qué significa |
|---|---|
| 401 | El servicio tiene contraseña; se escribe en el campo del pie |
| 403 | El servicio rechaza la petición: revisar `--allow-host` y `--allow-origin` |
| 404 | La ruta no existe en el servidor: falta el proxy de Apache |
| 502/503/504 | Apache no alcanza el servicio: ¿está arrancado? |
| No es JSON | La ruta responde, pero no es un servicio TeleHome |
| Sin respuesta | No se pudo conectar, o tardó más de 2,5 s |

El campo **Contraseña** del pie guarda la del servicio para esta pestaña, o para el navegador si se marca
«Recordar». Con ella puesta la app la manda en cada petición, incluida la descarga del CSV, que pasa a
hacerse por `fetch` en vez de por navegación.

**Ciclos de actualización:** el estado cada 3 s y el histórico cada 15 s, siempre que la pestaña esté visible.
Al volver a ella se refresca de inmediato.

---

## 9. La interfaz de la app genérica

### Cabecera

Título, distintivo de modo (Demostración, Simulación, Solo enchufes), distintivo de nivel (Solo lectura o
Usuario), estado de la conexión con la hora de la **última actualización del servidor** —la lectura más
reciente, no el momento de la consulta—, el botón **Entrar** cuando el servicio pide contraseña y el botón
**Ajustes y dispositivos**.

### Resumen de cabecera

Una cifra destacada por tipo presente, según su campo `hi`: potencia total, temperatura media, luces
encendidas, apertura media. Para los enchufes hay además un contador de energía del día.

### Dispositivos

Agrupados por tipo, por estancia o sin agrupar. Cada fila lleva nombre, estado, valores secundarios,
minigráfica, valor principal y su control. Pulsando una fila se filtra el histórico a ese dispositivo.

Agrupando por tipo o por estancia, la **cabecera del grupo también se pulsa** y filtra la gráfica y el resumen
a todos sus dispositivos. La selección activa (`S.sel`) es por eso de tres clases: `"all"`, el identificador de
un dispositivo, o `"grp:<tipo|estancia>:<clave>"`; el predicado `enSel(d)` es el único sitio que las distingue,
y de él tiran la gráfica, el resumen y el menú del CSV. Si nada de la selección mide la magnitud que está
puesta, se cambia a la del primero que mida algo. Al cambiar de agrupación la selección de grupo se descarta,
porque ese grupo ya no existe en la vista nueva.

Botones en la cabecera de la sección: **Actualizar**, que pide al servicio leer ya todos los dispositivos, y
**Ocultar gráficas**, que esconde solo las minigráficas. Dentro de la ficha del histórico, **Ocultar gráfica**,
que la pliega.

**Por qué existe «Actualizar».** Para no gastar la cuota gratuita de Tuya, el servicio lee la nube cada 300 s
(*Ajustes → Opciones*). Si enciendes, apagas o cambias un dispositivo con otra app, TeleHome no lo ve hasta la
siguiente lectura. Pulsa **Actualizar** y el servidor vuelve a leer todos al momento (una sola llamada a Tuya
para todos los de la nube). Puedes pulsarlo aunque solo estés mirando, sin contraseña. Si lo pulsas dos veces
seguidas, la segunda dentro de 5 s no hace nada y te dice cuánto esperar. Requiere un servicio 0.9.4 o posterior;
con uno anterior el botón solo recarga lo que el servicio ya tenía.

### Histórico

Cabecera con el título, **Exportar CSV** y el botón de plegar. Debajo, intervalo (1 h, 6 h, 24 h, 7 días,
30 días), magnitud y escala (por dispositivo o común), esta última a la derecha y etiquetada. Después la
leyenda, con **Mostrar todos** cuando hay series ocultas, la gráfica y una ayuda plegable.

La gráfica dibuja una magnitud a la vez con todos los dispositivos que la miden. Con varios y escala «por
dispositivo» pinta un panel por cada uno, con su propia escala vertical: así se compara la **forma** de las
curvas, no su altura. El cursor funciona con ratón, con el dedo y con las flechas del teclado.

Si se ha elegido un dispositivo, **Exportar CSV** lo descarga directamente; si están todos, abre un menú para
elegir cuál.

### Resumen

Una tabla por tipo con las columnas que declara su catálogo, y fila de totales donde tiene sentido.

### Ajustes y dispositivos

| Pestaña | Contenido |
|---|---|
| Dispositivos | Alta, edición, borrado y reordenación con ▲▼ |
| Estancias | Alta, renombrado, borrado y orden de las estancias (servicio 0.13.0) |
| Tipos | Catálogo, con lo que mide cada tipo y cuántos hay |
| Nube de Tuya | Credenciales, prueba, listado e importación |
| Buscar e importar | Búsqueda por UDP e importación del `devices.json` de TinyTuya |
| Opciones | Intervalos, retención, llamadas a la API y las contraseñas de servicio y de usuario |
| Compartir | Exportar e importar la configuración completa |

Sin ser administrador la hoja se abre igual, pero todos los campos están bloqueados y un aviso lo explica. El
orden de los dispositivos se guarda por navegador y se refleja en la página principal y en la leyenda.

---

## 10. Las versiones de iPhone y iPad

Dos apps aparte, también de una sola página, pensadas para el dedo y para añadirse a la pantalla de inicio.
**Solo consultan y manejan**: las altas, la nube y las contraseñas siguen en la interfaz completa.

- **iPhone**: una columna con cuatro pestañas abajo (Dispositivos, Gráfica, Resumen, Ajustes), interruptores
  de 44 pt y confirmación antes de apagar algo que está encendido.
- **iPad**: vista dividida, con los dispositivos a la izquierda y la gráfica o el resumen a la derecha. En
  pantallas estrechas pasa a una columna.

Buscan la API en este orden: la URL puesta a mano en Ajustes, `/rafa/telehome/api/`, `api/` relativa y la ruta
antigua `/rafa/telehome/enchufes/api/`. Respetan los tres niveles y muestran el distintivo correspondiente. El
intervalo de refresco es configurable (3, 5, 10 o 30 s).

Las dos comparten núcleo: catálogo, cliente de la API, sesión y gráfica son el mismo código, así que **una
corrección en una hay que llevarla a la otra**.

---

## 11. Modo demostración

Solo en la versión web del repo `apps`. Simula siete dispositivos de los cuatro tipos y los guarda en
`localStorage`, de modo que los cambios persisten entre recargas y no salen del navegador. El simulador de
cada tipo es su función `sim`, que combina una curva diaria, una cíclica y algo de ruido con una semilla
derivada del identificador: el mismo dispositivo dibuja siempre la misma curva.

La energía se integra sobre la potencia simulada, igual que hace el servicio. Las operaciones que no tienen
sentido sin servicio real (nube, búsqueda en red, exportación de configuración) avisan en vez de fallar.

La demostración también implementa `api/rooms`, de modo que las estancias se pueden crear, renombrar, borrar y
ordenar sin servicio real, con los mismos avisos y las mismas comprobaciones.

«Reiniciar demo» borra los datos guardados y vuelve a los siete iniciales.

---

## 12. Exportar e importar la configuración

Sirve para que otra persona tenga los mismos dispositivos sin configurar nada. Disponible desde 0.6.0 en
*Ajustes → Compartir* y en la línea de órdenes.

**Qué lleva el fichero:** los dispositivos con su *Local Key*, el Access ID y el Access Secret de Tuya, los
intervalos, la retención, la región y, si se indica, la ruta del servicio.
**Qué no lleva:** ninguna de las tres contraseñas.

```json
{
  "format": "telehome-config", "version": 1,
  "exported_at": "2026-11-22T14:20:42+0100",
  "aviso": "Este fichero contiene credenciales de Tuya y las Local Key…",
  "servicio": { "ruta": "/rafa/telehome/" },
  "options": { "poll_interval": 10, "cloud_region": "eu", "cloud_api_key": "…", "cloud_api_secret": "…" },
  "devices": [ … ]
}
```

Al importar hay dos modos. **Reemplazar** deja los dispositivos del fichero, conservando el identificador y
el histórico de los que ya existían con el mismo Device ID. **Añadir** solo suma los que falten.

Todo se valida **antes** de tocar nada, así que un fichero defectuoso no deja la configuración a medias; los
dispositivos inválidos se omiten indicando el motivo y se respeta el máximo de 7. Las credenciales vacías no
borran las que ya tuviera quien importa. Si el fichero trae la ruta del servicio y la app aún no está
conectada, se conecta ahí antes de importar.

El fichero se crea con permisos 600 y contiene credenciales: hay que tratarlo como una contraseña.

---

## 13. Almacenamiento

### En el servidor

| Qué | Dónde |
|---|---|
| Servicio Linux | `/var/lib/telehome/` |
| Linux, ejecución manual | `~/.telehome/` |
| macOS | `~/Library/Application Support/telehome/` |
| Simulación | subcarpeta `simulacion/` de la anterior |

Dentro: `config.json` (permisos 600) y `telemetria.sqlite3`. Si solo existe la carpeta con el nombre antiguo
`telehome-enchufes`, se sigue usando. La variable `TELEHOME_DIR` y la opción `--data-dir` la cambian.

> El modo simulación usa **otra** carpeta de configuración. Para ponerle contraseña a un servicio arrancado
> con `--simulate` hay que apuntar a esa subcarpeta con `--data-dir`.

### En el navegador

App genérica, en `localStorage`:

| Clave | Guarda |
|---|---|
| `telehome_conn` | Ruta del servicio, o `demo-only` |
| `telehome_auth` | Contraseña del servicio, si se marcó «Recordar» |
| `telehome_range`, `telehome_scale` | Intervalo y escala del histórico |
| `telehome_orden` | Orden de los dispositivos |
| `telehome_sin_graficas`, `telehome_sin_historico` | Qué está oculto |
| `telehome_demo_v1` | Los dispositivos de la demostración |
| `telehome_demo_v1_rooms` | Las estancias de la demostración |

En `sessionStorage`: `telehome_admin` (el token de sesión) y, si no se marcó «Recordar», también la
contraseña del servicio.

Las apps de iPhone y iPad usan el prefijo `telehome.`: `telehome.api`, `telehome.range`, `telehome.poll` y
`telehome.admin`.

---

## 14. Línea de órdenes

`telehome …` en el servicio Linux; `python3 -m telehome …` dentro del entorno virtual.

Opciones generales: `--version`, `-v/--verbose`, `--data-dir CARPETA`.

| Orden | Para qué |
|---|---|
| `serve` | Arranca el servicio (es la orden por omisión) |
| `scan [--time N]` | Busca dispositivos Tuya en la red local |
| `probe <dispositivo>` | Muestra los DPS crudos y el mapa de datos actual |
| `import <fichero> [--nube]` | Importa el `devices.json` de TinyTuya |
| `list` | Lista los dispositivos configurados |
| `cloud-setup --access-id … [--region eu] [--secret-env VAR] [--keep-secret]` | Credenciales de Tuya |
| `cloud-list` | Dispositivos de la cuenta enlazada |
| `cloud-import [ids…] [--todos]` | Alta en modo nube |
| `password [--quitar] [--password-env VAR]` | Contraseña del servicio |
| `admin-password [--quitar] [--password-env VAR]` | Contraseña de administrador |
| `user-password [--quitar] [--password-env VAR]` | Contraseña de usuario de confianza |
| `export-config [-o FICHERO] [--ruta /ruta/]` | Exporta la configuración |
| `import-config <fichero> [--anadir]` | Importa una configuración |

Opciones de `serve`:

| Opción | Por omisión | Para qué |
|---|---|---|
| `--host` | `127.0.0.1` | Interfaz donde escucha |
| `--port` | `8765` | Puerto |
| `--no-browser` | — | No abrir el navegador (obligatorio como servicio) |
| `--simulate N` | — | N enchufes simulados, sin hardware |
| `--allow-host NOMBRE` | — | Host adicional permitido; repetible |
| `--allow-origin ORIGEN` | — | Origen web autorizado (CORS); repetible |

`--password-env` y `--secret-env` leen el secreto de una variable de entorno, para no dejarlo en el historial
del intérprete de órdenes.

---

## 15. Despliegue

El despliegue completo lo hacen los scripts de `code/scripts/instalar-todo/`, uno por servidor
(`instalar-todo.sh`, `instalar-todo-isa.sh`, `instalar-todo-lorca.sh`). Cada pasada clona los repos, copia el
contenido al *webroot*, regenera el portal y, con `--telehome`, instala o actualiza el servicio y su proxy.
**Las opciones del servicio hay que repetirlas en cada pasada**, porque la unidad se reescribe.

El proxy que dejan en `/etc/apache2/conf-available/telehome.conf` es:

```apache
<Location "/rafa/telehome/">
    ProxyPreserveHost On
    ProxyPass "http://127.0.0.1:8765/"
    ProxyPassReverse "http://127.0.0.1:8765/"
</Location>
```

`ProxyPreserveHost On` es lo que hace que al servicio le llegue el nombre real del servidor, que es el que
compara contra su lista de hosts; sin ella habría que permitir `127.0.0.1` y se perdería la protección.

La app también se publica en GitHub Pages desde el repo `apps`, mediante el flujo
`deploy-artifacts-pages.yml`. Desde ahí no puede hablar con un servicio **http** (contenido mixto), así que
en Pages solo tiene sentido la demostración.

> Al desplegar desde Actions, usar `workflow_dispatch` y no «Re-run»: volver a ejecutar un flujo ya ejecutado
> produce el error «Multiple artifacts named github-pages».

---

## 16. Programaciones

Desde 0.9.0 el servicio puede encender, apagar o regular un dispositivo por su cuenta. Las evalúa un hilo propio
cada 20 s, así que funcionan con la app cerrada; lo único que tiene que estar en marcha es el servicio.

### Cómo se define una

```json
{
  "id": "luz-al-anochecer",
  "name": "Luz al anochecer",
  "enabled": true,
  "device": "luz-salon",
  "action": "switch", "value": true,
  "when": { "kind": "sunset", "offset": -15 },
  "days": [1, 2, 3, 4, 5],
  "condition": { "metric": "p", "op": "<", "value": 5, "for": 600 },
  "skip_if_manual": true,
  "last_fire": 1795359880.0, "last_result": "ejecutada"
}
```

| Campo | Qué significa |
|---|---|
| `action`, `value` | La orden: `switch` (booleano), `level`, `position` y `temp` (0-100), `color` (`#rrggbb`), `mode` (`white`/`colour`) o `stop` (sin valor) |
| `when.kind` | `clock` con `time` en `HH:MM`, o `sunrise`/`sunset` con `offset` en minutos (±720) |
| `days` | Días en formato ISO: 1 lunes … 7 domingo. **Lista vacía: se ejecuta una sola vez** |
| `condition` | Opcional. `metric`, `op` (`<`, `<=`, `>`, `>=`), `value` y `for` en segundos |
| `skip_if_manual` | No hacerlo si has manejado el aparato a mano desde la vez anterior |
| `last_fire`, `last_result` | Los escribe el servicio: cuándo se evaluó y qué pasó |
| `created`, `once` | Los calcula el servicio: cuándo se creó y si es de un solo uso |

Máximo **32** programaciones. Los identificadores se derivan del nombre.

### Cuándo dispara

El hilo mira el reloj cada 20 s y busca, para cada programación activa, el instante que le tocaba hoy o ayer:

- **`clock`** usa la hora local del servidor, con su horario de verano.
- **`sunrise` y `sunset`** calculan el orto y el ocaso de ese día con `sun.py`, que implementa el algoritmo del
  NOAA sin dependencias, a partir de `lat` y `lon` de las opciones (Elche por omisión; se cambian en la pestaña o
  con `PUT api/place`). Si ese día el Sol no sale ni se pone, la programación no toca.

Dispara si ese instante ya pasó, **hace menos de una hora**, es posterior a su `last_fire` y posterior a
`created`. La ventana de una hora es deliberada: si el servicio estuvo parado toda la noche, al arrancar por la
mañana no se ejecuta de golpe todo lo que tocaba de madrugada. Lo de `created` evita la otra sorpresa: crear a
las 07:30 una programación de las 07:00 no la dispara en el acto, sino al día siguiente.

### Una sola vez

Si no se marca ningún día, la programación vale para **cualquier** día y se gasta en la primera evaluación: se
ejecuta en el próximo momento que llegue y queda desactivada, con el resultado anotado. Se gasta aunque se salte
por la condición o por el mando manual, porque «una sola vez» significa una sola evaluación, no un reintento
indefinido. Para repetirla basta con volver a activarla.

### Condición

Se comprueba al disparar, contra la última lectura del dispositivo. Con `for` mayor que cero se exige además que
se haya mantenido durante ese tiempo, y eso se mira en el histórico: si no hay datos en esa ventana, **no se
ejecuta**, porque es más prudente no hacer nada que actuar a ciegas.

El caso que motiva esto es apagar la lavadora al terminar: «apagar si la potencia lleva 10 minutos por debajo de
5 W». Las magnitudes disponibles son `p`, `v` e `i` (enchufes) y `br` (brillo de las luces), que es lo que guarda el almacén.

### «No me pises»

Con `skip_if_manual`, antes de actuar se mira si alguien dio una orden **a mano** a ese dispositivo después de la
vez anterior en que esta programación se disparó (o en las últimas 24 h si nunca lo hizo). Si es así, se salta y
lo anota. Las órdenes que manda el propio programador no cuentan como manuales, de modo que una programación
nunca se salta a sí misma.

### Resultados

Cada evaluación deja un texto en `last_result`, que la app muestra bajo cada programación: `ejecutada`,
`saltada: lo manejaste a mano después de la vez anterior`, `saltada: no se cumple la condición (p < 5, vale 29.5)`,
`saltada: no hay histórico para comprobar la condición`, `saltada: el dispositivo ya no existe` o `error: …`.
También se registran en el diario del servicio.

### Dónde se gestionan

En **Ajustes → Programaciones** de la app completa: alta, edición, activar y desactivar, **Probar** (que la
dispara al momento, saltándose el reloj pero no la condición) y el lugar para el amanecer. En iPhone y iPad se
ven y se activan o desactivan, pero no se editan. Por línea de órdenes, `telehome schedules`.

En el formulario, los días se marcan uno a uno o de golpe: la casilla **Todos los días** (queda a medias si hay algunos marcados) y los atajos **Lunes a viernes** y **Fin de semana**. Desmarcar todo deja la programación «una sola vez», y el formulario lo avisa.

Solo un **administrador** las ve y las toca: a quien no lo es, `api/state` le manda la lista vacía.

Se incluyen al exportar la configuración, junto con el lugar. Al importar se descartan las que apunten a un
dispositivo que no venga en el fichero.

---

## 17. Añadir un tipo de dispositivo nuevo

Dos mitades, y se pueden hacer por separado.

**En la app** basta con añadir una entrada a `TELEHOME_TYPES`, en el primer bloque `<script>`: etiquetas,
icono, magnitudes, control, columnas del resumen, campos de alta y, si se quiere que salga en la
demostración, un `sim`. No hay que tocar la interfaz. Si la magnitud es nueva, se añade antes a
`TELEHOME_METRICS`.

**En el servicio** hay más trabajo: añadir el tipo a `DEVICE_TYPES`, enseñar a `devices.py` a leerlo y a
mandarle órdenes, extender `monitor.py` y generalizar `store.py`, que hoy guarda tres columnas fijas. Mientras
el servicio no lo declare en `api/health`, la app lo muestra en el catálogo pero no deja darlo de alta.

---

## 18. Desarrollo y pruebas

El servicio trae una batería con `pytest`: 67 pruebas que cubren configuración, almacén, servidor, niveles de
acceso, nube y línea de órdenes.

```bash
cd telemetria/home/telehome-servicio
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt pytest
python3 -m pytest -q
```

Para probar sin hardware:

```bash
python3 -m telehome serve --simulate 3 --no-browser     # servicio simulado en :8765
```

Las apps de iPhone y iPad traen un `servir.py` que sirve la carpeta y reenvía `/rafa/telehome/*` al servicio,
imitando a Apache, para poder probarlas sin tocar el servidor.

Al editar cualquiera de las apps hay que actualizar la fecha de **Última modificación** del pie.

---

## 19. Solución de problemas

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| «No hay servicio TeleHome en esa ruta» | El cartel dice el motivo | Seguir lo que indique (ver 8) |
| 401 repetidos en el registro de Apache | El servicio tiene contraseña | Escribirla en el campo del pie |
| «Host no permitido» (403) | Falta `--allow-host` con el nombre que usas | Reinstalar repitiendo **todas** las opciones |
| 404 en `/rafa/telehome/api/health` | Falta el proxy o `a2enconf`/recarga | Revisar `telehome.conf` y `a2enmod proxy proxy_http` |
| 502 | El servicio está parado | `systemctl status telehome` |
| Un dispositivo cambiado con otra app tarda en verse | El servicio lee la nube cada 300 s | Pulsa **Actualizar** en *Dispositivos* (servicio 0.9.4 o posterior) |
| La app no se actualiza tras publicar | Caché del navegador, o falta `instalar-todo` | Ctrl+Mayús+R; en el servidor, reinstalar |
| Una bombilla aparece como enchufe, sin brillo ni color | Se dio de alta con una versión anterior a la 0.10.0 | Actualiza el servicio (`instalar-todo-lorca.sh --telehome`): la convierte sola. O *Editar* → Tipo → Luz |
| Una luz no muestra el selector de color | La bombilla no devuelve códigos de color (es solo blanca) o el servicio es anterior a la 0.10.0 | Mirar `caps` en `GET api/state`; actualizar el servicio |
| Un dispositivo «sin conexión» | Tuya admite una sola conexión TCP | Cerrar la app del móvil |
| Cambios que no se aplican | Otro proceso editó `config.json` | El servicio lo recarga solo al detectar el cambio |
| `journalctl` vacío | El usuario no está en `adm` ni `systemd-journal` | Usarlo con `sudo` |
| «No se pudo conectar con la nube de Tuya…» | El servidor no llega a `openapi.tuyaeu.com`: sin DNS, sin salida por el 443, proxy o certificado | El propio mensaje dice cuál de los cuatro; el texto técnico está plegado en «Detalle técnico» y entero en `journalctl -u telehome` |

Registros útiles: `sudo journalctl -u telehome -f`, `/var/log/apache2/access.log` (el código de respuesta de
cada petición) y `/var/log/apache2/error.log`.

---

## 20. Límites conocidos

- **Máximo 7 dispositivos**, sumando los dos modos.
- **Intervalos**: local mínimo 5 s (los medidores Tuya no admiten más), nube mínimo 60 s (cupo de la cuenta
  gratuita), máximo 3600 s en ambos.
- **El servicio solo sabe leer enchufes.** Los demás tipos existen en la app y en el protocolo, pero aún no en
  el servicio.
- **El almacén guarda tres columnas fijas** (potencia, tensión, corriente). Generalizarlo es el paso previo a
  admitir sensores de verdad.
- **El punto del histórico usa `t` para el tiempo**, que choca con la clave de temperatura; hará falta añadir
  `values` cuando haya sensores (ver 5).
- **Un solo dispositivo por Device ID**, y los dispositivos Tuya suelen admitir **una sola conexión TCP**.
- **Sin HTTPS propio**: el cifrado, si lo hay, lo pone Apache. En un servidor sin HTTPS las contraseñas viajan
  en claro por la red.
- **Las programaciones son simples**: una orden, a una hora o al orto/ocaso, con una sola condición sobre una
  magnitud del propio dispositivo. No hay escenas, encadenamientos, avisos ni condiciones cruzadas entre aparatos.
- **La condición solo mira potencia, tensión y corriente**, porque es lo único que guarda el almacén.

---

## 21. Referencia rápida

```bash
# Servicio
sudo systemctl {status,restart} telehome
sudo journalctl -u telehome -f
systemctl cat telehome | grep ExecStart          # con qué opciones arrancó

# Contraseñas
sudo telehome password          # entrar al servicio
sudo telehome admin-password    # configurar
sudo telehome user-password     # manejar los dispositivos

# Configuración
sudo telehome list
sudo telehome export-config -o config.json --ruta /rafa/telehome/
sudo telehome import-config config.json [--anadir]

# Comprobaciones
curl -s http://127.0.0.1:8765/api/health
curl -s http://SERVIDOR/rafa/telehome/api/health
```

| Quiero… | Dónde |
|---|---|
| Instalarlo paso a paso | [INSTALACION.md](INSTALACION.md) |
| Añadir un tipo | Apartado 17 |
| Saber qué devuelve una ruta | Apartado 6 |
| Entender los permisos | Apartado 7 |
| Dar acceso a otra persona | Apartados 7.2 y 12 |
| Depurar una conexión | Apartados 8 y 19 |
| Explicárselo a quien solo lo va a usar | [Manual de usuario de TeleHome Pro](../telehome-pro/manual/) |

---

*Última modificación: 2026-11-25 22:25*
