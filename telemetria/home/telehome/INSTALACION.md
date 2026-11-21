# TeleHome · Guía de instalación, configuración y ejecución

**Autor:** Rafa · Departamento de Ingeniería de Sistemas y Automática · Universidad Miguel Hernández de Elche · r.puerto@umh.es
*Generado con IA · Revisado por el autor*

Versión de la app: primera versión genérica · Versión del servicio: TeleHome Enchufes 0.5.2 (protocolo genérico; servicio «telehome») · Fecha: 21/11/2026

---

## 1. Qué es TeleHome y cómo se relaciona con TeleHome Enchufes

**TeleHome** es una app web de un solo archivo HTML (HTML + CSS + JavaScript, sin librerías externas) que muestra y controla **varios tipos de dispositivos** domésticos. Deriva de TeleHome-enchufes y mantiene su funcionalidad, pero su estructura es genérica: cada tipo de dispositivo se describe en un catálogo declarativo y la interfaz se construye a partir de él.

**TeleHome Enchufes** es el **servicio Python** que habla con los dispositivos reales (enchufes Wi-Fi Tuya, p. ej. Energeeks EG-EW008MC / EG-EW009MC) y guarda el histórico en SQLite. Desde la versión 0.5.0 incorpora el **protocolo genérico de TeleHome**.

```
navegador ──▶ index.html (TeleHome) ──HTTP──▶ telehome_enchufes (Python) ──TCP 6668──────────▶ enchufes (modo local, misma LAN)
                                                    │                    └──HTTPS (API Tuya)──▶ nube de Tuya ◀── enchufes (modo nube)
                                                    └── SQLite (telemetría)
```

### Tipos de dispositivo del catálogo

| Tipo | Estado | Magnitudes |
|---|---|---|
| Enchufe | Funcional | potencia, tensión, corriente, interruptor |
| Sensor T/H | Funcional | temperatura, humedad |
| Luz | Funcional | interruptor, nivel (brillo) |
| Persiana | Funcional | posición, subir/bajar/parar |
| Termostato | Previsto (`soon`) | — |
| Contador | Previsto (`soon`) | — |

> Hoy el **servicio** solo gestiona enchufes (`DEVICE_TYPES = ("enchufe",)`). Los demás tipos funcionan completos en el **modo demostración** de la app y se activarán en el servicio a medida que se añadan.

### Modos de conexión de la app

| Modo | Qué hace | Cuándo usarlo |
|---|---|---|
| **Servicio TeleHome** (genérico) | Detecta `api/health` con `"api":"telehome"` | Servicio 0.5.0 o superior |
| **TeleHome Enchufes (heredado)** | Adaptador que traduce respuestas y órdenes | Servicio anterior a 0.5.0, sin actualizar |
| **Demostración** | 7 dispositivos simulados en el navegador (`localStorage`, clave `telehome_demo_v1`, máx. 16) | Probar sin hardware ni servicio |

---

## 2. Requisitos

- **Python 3.9 o superior** (solo para el servicio). En macOS: `xcode-select --install` o `brew install python`.
- **git** (para clonar el código).
- Dependencia Python: `tinytuya>=1.13` (la instalan los scripts de instalación).
- Un navegador moderno para la app.
- Para modo local: enchufes en la misma red que el servicio, con *Device ID* y *Local Key*.
- Para modo nube: cuenta en [iot.tuya.com](https://iot.tuya.com) y enchufes emparejados en **Smart Life** o **Tuya Smart**.

---

## 3. Obtener el código

La app y el servicio están en repositorios distintos:

| Pieza | Repositorio | Ruta |
|---|---|---|
| App TeleHome (HTML) | `RafaUMH2110/apps` | `telemetria/home/telehome/index.html` (+ `README.md`) |
| Servicio TeleHome Enchufes | `RafaUMH2110/code` | `telemetria/home/telehome-enchufes/` |

Clonado ligero del servicio (solo la carpeta necesaria):

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/RafaUMH2110/code.git
cd code && git sparse-checkout set telemetria/home/telehome-enchufes
cd telemetria/home/telehome-enchufes
```

### 3.1. Aplicar el parche del protocolo genérico (0.5.0)

Si en `RafaUMH2110/code` el servicio aún está en una versión anterior a 0.5.0, aplica el parche `telehome-enchufes-protocolo-generico-0.5.0.patch` desde la raíz del repositorio clonado:

```bash
cd code                                   # raíz del repositorio
git apply --check /ruta/telehome-enchufes-protocolo-generico-0.5.0.patch   # comprobar (no cambia nada)
git apply /ruta/telehome-enchufes-protocolo-generico-0.5.0.patch           # aplicar
git status                                # ver los archivos modificados
```

Para subirlo al repositorio:

```bash
git checkout -b telehome-protocolo-generico
git add telemetria/home/telehome-enchufes
git commit -m "TeleHome Enchufes 0.5.0: protocolo genérico (tipos, órdenes, resumen por magnitud)"
git push -u origin telehome-protocolo-generico   # o directamente a main, según prefieras
```

Cambios del parche: `__init__.py` (versión 0.5.0), `config.py` (campos `type` y `room`), `monitor.py` (`command`, `actions_for`, `state` ampliado), `store.py` (resumen por magnitud `m` y `on_ratio`), `server.py` (rutas genéricas), `README.md` y 3 tests nuevos (33 en total).

---

## 4. Instalar el servicio

> Desde la 0.5.2 el servicio Linux se llama **`telehome`** (antes `telehome-enchufes`): unidad systemd, orden, `/opt/telehome` y `/var/lib/telehome`. Si ya lo tenías instalado, vuelve a ejecutar el instalador: migra solo el nombre anterior y conserva los datos. La carpeta del código y el módulo Python siguen llamándose `telehome-enchufes` / `telehome_enchufes`.

### 4.1. macOS

```bash
cd telemetria/home/telehome-enchufes
./macos/instalar-macos.sh              # crea .venv e instala dependencias
./macos/instalar-macos.sh --launchd    # opcional: arranca al iniciar sesión (LaunchAgent)
```

- La primera vez macOS pedirá permiso de **Red local** para Python: **hay que permitirlo**. Si usas el LaunchAgent, ejecuta antes la app una vez desde el Terminal para ver ese aviso.
- Datos: `~/Library/Application Support/telehome/`.

### 4.2. Linux (p. ej. una VM de Azure)

```bash
cd telemetria/home/telehome-enchufes
sudo ./linux/instalar-linux.sh
```

Crea un usuario de servicio, el entorno virtual, la unidad systemd `telehome` (con `ProtectSystem=strict`) y la orden `telehome`. Código en `/opt/telehome`, datos en `/var/lib/telehome/`. Si ya tenías el servicio con el nombre anterior (`telehome-enchufes`, hasta la 0.5.1), vuelve a ejecutar el instalador: lo migra solo, sin perder datos.

Opciones del instalador:

| Opción | Efecto |
|---|---|
| `--puerto N` | Puerto distinto de 8765 |
| `--host DIR` | Dirección de escucha (por defecto `127.0.0.1`) |
| `--allow-host NOMBRE` | Admite ese nombre de host (necesario tras proxy inverso) |
| `--allow-origin ORIGEN` | Autoriza a una web externa (CORS), p. ej. `https://rafaumh2110.github.io` |
| `--quitar` | Desinstala el servicio |

Gestión del servicio:

```bash
sudo systemctl status telehome
sudo systemctl restart telehome
sudo journalctl -u telehome -f
```

Los cambios hechos con la orden `telehome ...` (alta de dispositivos, contraseña, etc.) se aplican al momento, sin reiniciar.

### 4.3. Acceso remoto al servicio

**Opción A · Túnel SSH (recomendada, no abre puertos):**

```bash
ssh -L 8765:127.0.0.1:8765 usuario@tu-vm
# y abre http://127.0.0.1:8765/
```

**Opción B · Apache con HTTPS (subruta):**

```apache
ProxyPass        /enchufes/ http://127.0.0.1:8765/
ProxyPassReverse /enchufes/ http://127.0.0.1:8765/
```

Instala con `--allow-host tu-dominio` y **pon contraseña** (`sudo telehome password`). No uses `--host 0.0.0.0` sin contraseña.

---

### 4.4. Todo en lorca.umh.es (sin HTTPS): `instalar-todo-lorca.sh`

El instalador `scripts/instalar-todo/instalar-todo-lorca.sh` del repo `code` clona los repos, despliega las apps en Apache, **regenera el portal** (`/rafa/`) e instala el servicio `telehome` con su proxy. Es idempotente: se repite para actualizar.

```bash
cd ~/RafaUMH2110/code && git pull
cd scripts/instalar-todo
./instalar-todo-lorca.sh          # usa la selección de repos guardada; --telehome / --sin-telehome lo controlan
```

Resultado:
- Servicio: proxy en `http://lorca.umh.es/rafa/telehome/` (interfaz propia de TeleHome Enchufes).
- App TeleHome: `http://lorca.umh.es/rafa/apps/telemetria/home/telehome/`. En *Servicio TeleHome* escribe `/rafa/telehome/` y pulsa Conectar (mismo origen: no hace falta CORS).
- Si el portal no muestra las apps nuevas, es que no se ha vuelto a ejecutar el instalador.

Sin HTTPS la contraseña viaja sin cifrar: pon contraseña (`sudo telehome password`) y limita el acceso a la red.

## 5. Ejecutar el servicio

| Caso | Orden |
|---|---|
| macOS, doble clic | `macos/iniciar-telehome-enchufes.command` (abre el navegador en <http://127.0.0.1:8765/>) |
| Línea de órdenes (venv) | `.venv/bin/python -m telehome_enchufes serve` |
| Linux (servicio) | `sudo systemctl start telehome` |
| **Sin hardware (simulado)** | `.venv/bin/python -m telehome_enchufes serve --simulate 4` |

Opciones de `serve`: `--host`, `--port` (por defecto 8765), `--no-browser`, `--simulate N`, `--allow-host NOMBRE`, `--allow-origin ORIGEN`, `--data-dir RUTA`. También se puede fijar la carpeta de datos con la variable `TELEHOME_ENCHUFES_DIR`.

El modo `--simulate` usa una carpeta de datos aparte, así que no mezcla datos de prueba con los reales.

---

## 6. Dar de alta los dispositivos (enchufes)

Cada enchufe puede leerse en **modo local** o en **modo nube**. Máximo **7 enchufes** en total.

### 6.1. Modo local (misma red)

Necesitas: **Device ID**, **Local Key**, IP (o `Auto`) y versión del protocolo (3.3 o 3.4).

1. Empareja el enchufe con Smart Life / Tuya Smart (o Energeeks 3.0).
2. Obtén la Local Key con el asistente de TinyTuya (requiere cuenta gratuita de desarrollador en iot.tuya.com con tu app vinculada):
   ```bash
   .venv/bin/python -m tinytuya wizard
   ```
   Genera `devices.json`. La clave cambia si borras el enchufe de la app o lo restableces.
3. Impórtalos:
   - Interfaz: **Ajustes → Importar devices.json**, o
   - Terminal: `python -m telehome_enchufes import devices.json`
4. También puedes añadirlos a mano, y buscar IP/Device ID con **Buscar en la red** (`python -m telehome_enchufes scan`).

Con IP `Auto` el servicio localiza el enchufe por su Device ID y se adapta si el router cambia la IP. Lo ideal es reservar una IP fija en el router.

**Mapa de datos (DPS) por defecto:** interruptor `1`, corriente `18` (mA), potencia `19` (÷10 → W), tensión `20` (÷10 → V). No verificado con un EG-EW008MC real: si las lecturas salen mal, mira los DPS crudos con `python -m telehome_enchufes probe <nombre>` y ajústalos en *Ajustes → Avanzado* del enchufe.

### 6.2. Modo nube (API de Tuya)

Sirve cuando el servicio no está en la misma red que los enchufes (p. ej. en una VM de Azure).

1. Los enchufes deben estar en **Smart Life** o **Tuya Smart**. Con la app de marca **Energeeks 3.0** el enlace con Tuya normalmente **no funciona**: restablece cada enchufe y empareja en Smart Life.
2. En [iot.tuya.com](https://iot.tuya.com) → *Cloud → Create Cloud Project* (tipo **Smart Home**, centro de datos **Central Europe**). Suscribe **IoT Core** y **Authorization** (plan de prueba gratuito) y **autoriza el proyecto** (*Cloud Services → IoT Core → View Details → Authorized Projects → Add Authorization*).
3. En el proyecto: *Devices → Link Tuya App Account → Add App Account*; escanea el QR desde la pestaña «Yo» de Smart Life.
4. **Para poder encender/apagar:** en esa lista, columna *Device Permission* → *Change* → **Controllable** (con *Read* solo se lee y Tuya responde «No permissions…»).
5. Copia **Access ID** y **Access Secret** (pestaña *Overview*) en *Ajustes → Nube de Tuya* y pulsa *Ver dispositivos de la nube*; o por terminal:
   ```bash
   telehome cloud-setup --region eu --access-id TU_ACCESS_ID
   telehome cloud-list
   telehome cloud-import            # todos, o: cloud-import id1 id2 ...
   ```

Notas:

- El plan gratuito de IoT Core **caduca al mes**: renuévalo en la consola de Tuya (*Extend trial period*). Si caduca, los enchufes salen «sin conexión» con el error de la API.
- El cupo de llamadas es limitado: se lee todo con 1-2 llamadas por ciclo (por defecto cada **300 s**, mínimo 60 s). *Ajustes → Opciones* muestra la estimación mensual y, desde la 0.5.1, las llamadas reales por día (se guardan en la base de datos del servicio) para contrastarlas con *Cloud → Usage (API Statistics)* en iot.tuya.com. Los créditos de la portada de la consola son de Cobuilder (IA) y no cuentan estas llamadas.
- Códigos de datos por defecto: `switch_1`, `cur_power` (÷10 → W), `cur_voltage` (÷10 → V), `cur_current` (mA); ajustables por enchufe en *Avanzado*.
- Los dispositivos virtuales de la consola (Device ID `vdevo…`) solo sirven para pruebas: no dan potencia/tensión/corriente y rechazan órdenes (error 28841105).
- Al importar desde la nube se guarda también la Local Key, por lo que luego puedes pasar el enchufe a modo local.

### 6.3. Límites y buenas prácticas

- Máximo **7 enchufes** (suma de ambos modos).
- Los dispositivos Tuya suelen admitir **una sola conexión TCP**: cierra la app del móvil mientras uses TeleHome.
- Intervalo local: 10 s por defecto, **mínimo 5 s**. Nube: 300 s por defecto, mínimo 60 s.
- Si un enchufe se cae se reintenta con espera creciente (hasta 60 s) y se marca «sin conexión».
- Histórico: 30 días por defecto (configurable). Al eliminar un enchufe se borra su histórico.

---

## 7. Usar la app TeleHome

### 7.1. Abrirla

- **Modo demostración** (sin nada instalado): abre `index.html` (desde el repo `apps`, GitHub Pages, o el archivo local). Si no encuentra servicio, arranca en demostración.
- **Con el servicio local:** abre <http://127.0.0.1:8765/> (el servicio también sirve la interfaz de TeleHome Enchufes).
- **Servicio en otra dirección u origen (p. ej. app en GitHub Pages y servicio en tu máquina):** en *Ajustes → Servicio TeleHome* escribe la dirección completa, p. ej. `http://127.0.0.1:8765/`. El servicio debe autorizar el origen de la web con `--allow-origin` (ver 7.1.1). Sin eso el navegador bloquea la conexión.
- **App y servicio bajo el mismo servidor (Apache de `isa.umh.es`):** copia `index.html` a `/var/www/htdocs/rafa/telehome/`, define un proxy en la misma web (`ProxyPass /rafa/telehome-api/ http://127.0.0.1:8765/`), instala con `--allow-host isa.umh.es` y escribe en el campo la ruta `/rafa/telehome-api/` (no hace falta `--allow-origin`).
- Con el campo **vacío** usa el servicio que sirve esa misma página.

> Antes de conectar, la app consulta `api/health` en esa dirección (2,5 s de espera). Si no hay servicio TeleHome o TeleHome Enchufes, sigue en demostración.

#### 7.1.1. Autorizar una web externa: `--allow-origin` (servicio 0.5.0 con este cambio)

```bash
# macOS / manual
.venv/bin/python -m telehome_enchufes serve --allow-origin https://rafaumh2110.github.io
# Linux (servicio systemd)
sudo ./linux/instalar-linux.sh --allow-origin https://rafaumh2110.github.io
```

- Es el **origen** (esquema + dominio, sin ruta ni barra final). Repetible. Si no se indica, el servicio no admite ningún otro origen (comportamiento por defecto, el más seguro).
- Solo ese origen puede leer y escribir en la API; el servicio responde a su *preflight* (`OPTIONS`) y rechaza los demás. Siguen exigiéndose `Host` válido, cabecera `X-TeleHome` y la contraseña si la hay.
- Desde una web HTTPS (GitHub Pages), el navegador solo permite conectar sin avisos con `http://127.0.0.1` / `localhost`. Para un servicio en otra máquina hace falta HTTPS (proxy).
- Autorizar un origen equivale a confiar en esa web: cualquier página publicada allí podrá controlar tus dispositivos mientras tengas el navegador abierto. Usa contraseña y no autorices dominios que no controles.

### 7.2. Qué muestra

- **Contador superior (hero):** magnitud principal agregada (suma, media o recuento según el tipo).
- **Grupos por tipo/habitación:** lista de dispositivos con indicador de carga/estado, minigráfica y control (interruptor, regulador de nivel, botones de persiana…).
- **Gráfica:** 1 h a 30 días, con valores al pasar el ratón o el dedo. Dos tipos que miden la misma magnitud comparten gráfica. Con varios dispositivos se dibuja una mini-gráfica por dispositivo, cada una con su escala vertical, para que uno de 1.800 W no aplaste a los de 4 W; el selector «Escala» (Por dispositivo / Común) vuelve a una sola gráfica con escala compartida y la elección se recuerda en el navegador.
- **Tabla resumen** con medias, mínimos y máximos por magnitud, energía y disponibilidad.
- **Ajustes:** conexión, dispositivos (añadir, editar, eliminar), nube de Tuya, buscar/importar, opciones. Modo oscuro automático.

### 7.3. Añadir un dispositivo

*Ajustes → Dispositivos → Añadir*: elige el **tipo** (Enchufe, Sensor T/H, Luz, Persiana…); el formulario se genera con los campos de ese tipo (nombre, habitación, identificadores de Tuya, DPS/códigos). Los tipos marcados «próximamente» aparecen deshabilitados.

### 7.4. Añadir un tipo nuevo al catálogo (para evolucionar la app)

En `index.html`, bloque del catálogo (`TELEHOME_TYPES`, con magnitudes compartidas en `TELEHOME_METRICS`), añade una entrada con: `label`, `plural`, `icon`, `metrics`, `primary`, `meta`, `bar`, `control`, `actions`, `hi` (kind `sum|avg|count` y `main`), `summary` (columnas), `accum`, `fields`, `state`, `sim` (simulador demo) y `note`. Márcalo con `soon: true` hasta que el servicio lo soporte. No hace falta tocar el resto de la interfaz. Después actualiza el pie «Última modificación».

En el servicio: añade el tipo a `DEVICE_TYPES` (`config.py`) y sus acciones a `ACTIONS` (`monitor.py`).

---

## 8. API del servicio (protocolo genérico)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `api/health` | Estado y versión; incluye `"api":"telehome"` y `"types":[…]` |
| GET | `api/state` | Lectura actual de todos los dispositivos (`state`, `values`, `accum`) |
| GET | `api/summary?…` | Resumen por dispositivo (`devices`, alias `plugs`; `m` por magnitud, `on_ratio`) |
| GET | `api/history?dev=<id>…` | Histórico (`dev=` es alias de `plug=`) |
| POST | `api/devices/<id>/command` | `{action:"switch"\|"level"\|"position"\|"stop"\|"setpoint", value}` |
| POST | `api/plugs/<id>/power` | Alias heredado para encender/apagar enchufes |

Modelo de lectura: `{ts, online, error, state:{…}, values:{p,v,i,t,h,br,pos}}`. Las operaciones de escritura exigen la cabecera `X-TeleHome` y un `Origin` propio.

---

## 9. Órdenes de la línea de comandos

(`telehome …` en el servicio Linux, o `python -m telehome_enchufes …` en el venv.)

| Orden | Descripción |
|---|---|
| `serve` | Arranca el servicio (`--host`, `--port`, `--no-browser`, `--simulate N`, `--allow-host`, `--data-dir`) |
| `scan` | Busca enchufes en la red local |
| `probe <enchufe>` | Muestra los DPS/datos crudos de un enchufe |
| `import <devices.json> [--nube]` | Importa dispositivos desde TinyTuya |
| `list` | Lista los dispositivos configurados |
| `cloud-setup --region eu --access-id …` | Guarda credenciales de la nube de Tuya |
| `cloud-list` | Lista los dispositivos de la nube |
| `cloud-import [ids…]` | Importa dispositivos de la nube |
| `password [--quitar]` | Pone, cambia o quita la contraseña |

---

## 10. Datos y seguridad

- Datos en `~/Library/Application Support/telehome/` (macOS), `~/.telehome/` (Linux, usuario) o `/var/lib/telehome/` (servicio Linux): `config.json` (permisos 600) y `telemetria.sqlite3`.
- Las *Local Keys*, el *Access Secret* y la contraseña (PBKDF2) **nunca** salen por la API ni se suben al repositorio (`.gitignore`).
- El servicio escucha en `127.0.0.1`, rechaza `Host` ajenos (anti DNS rebinding) y exige `X-TeleHome` + `Origin` propio en escrituras (anti CSRF).
- Contraseña opcional (HTTP Basic, cualquier usuario): `telehome password`. Por HTTP sin cifrar solo tiene sentido tras túnel SSH o proxy HTTPS.
- Haz copia de seguridad de `config.json` y `telemetria.sqlite3` si el histórico te importa.

---

## 11. Solución de problemas

| Síntoma | Causa probable / solución |
|---|---|
| La app arranca en demostración | No encuentra el servicio: comprueba que está en marcha (`curl http://127.0.0.1:8765/api/health`) y la dirección en *Ajustes → Conexión* |
| Enchufe «sin conexión» (local) | IP cambiada (usa `Auto` o reserva IP), Local Key obsoleta (regenerar con `tinytuya wizard`), app del móvil abierta (una sola conexión TCP), aviso de Red local no permitido en macOS |
| Lecturas absurdas (W, V, mA) | DPS distintos: usa `probe <enchufe>` y ajusta en *Avanzado* |
| Nube: «No permissions. This project is not authorized…» | Falta *Controllable* en *Device Permission* o la autorización de IoT Core/Authorization (ver 6.2) |
| Nube: sin conexión con error de API | Caducó el plan de prueba de IoT Core: renovar en iot.tuya.com |
| Nube: error 28841105 | Dispositivo virtual `vdevo…`: no admite órdenes, quitarlo |
| Error 403 / «Host no permitido» tras proxy | Reinstalar o ejecutar con `--allow-host tu-dominio` |
| `python3 -m pytest` → `No module named pytest` | pytest solo es necesario para desarrollar; ver apartado 12 |
| No conecta desde GitHub Pages o con una URL completa | Arranca el servicio con `--allow-origin https://rafaumh2110.github.io` (sin barra final) y escribe la dirección completa; revisa la consola del navegador (CORS) |

---

## 12. Desarrollo y pruebas

```bash
cd telemetria/home/telehome-enchufes
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt pytest
.venv/bin/python -m pytest -q          # 38 tests
```

pytest **no** es necesario para ejecutar el servicio, solo para las pruebas.

Para publicar la app en la web: sube `index.html` a `RafaUMH2110/apps` (carpeta `telemetria/home/telehome/`) y regenera el portal (`.github/scripts/generate_index.py`, necesita `GITHUB_REPOSITORY=RafaUMH2110/apps`; los workflows `deploy-artifacts-pages.yml` y `sync-appindex-portal.yml` lo hacen en cada push). Para Apache de `isa.umh.es`, copia el archivo a `/var/www/htdocs/rafa/`.

---

## 13. Resumen de arranque rápido

1. **Probar sin nada:** abre `index.html` → modo demostración.
2. **Probar el servicio sin hardware:** instala (apartado 4) y ejecuta `serve --simulate 4`.
3. **Uso real:** instala, da de alta los enchufes (local o nube), arranca el servicio, abre <http://127.0.0.1:8765/> o conecta la app TeleHome al servicio.
