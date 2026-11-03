# TeleMet Colector

Programa en **Python** (solo biblioteca estándar, sin `pip install`) que se ejecuta de forma continua en el servidor Linux:

1. Lee cada minuto (configurable) la estación meteorológica vía Weather Underground / Earth Network.
2. Guarda las lecturas en una base SQLite.
3. Pasadas **12 horas** borra los datos y empieza de nuevo.
4. Tras cada lectura exporta el histórico a un JSON estático junto a la app **TeleMet Historial**, que lo lee al abrirse y rellena con él los huecos de sus gráficas de evolución de 12 h (aunque el navegador haya estado cerrado).

```
estación ──► API Weather Underground ──► telemet_colector.py ──► SQLite (datos/telemet.sqlite)
                                                │
                                                └──► historial.json ──► Apache ──► TeleMet Historial (navegador)
```

## Contenido

| Fichero | Para qué |
|---|---|
| `telemet_colector.py` | El programa. |
| `config.example.ini` | Plantilla de configuración con todos los parámetros comentados. |
| `telemet-colector.service` | Unidad systemd para que arranque con el servidor y se reinicie si falla. |

## Instalación en el servidor

Requisitos: Python 3.8 o superior y salida a Internet hacia `api.weather.com`.

```bash
# 1. Usuario de servicio y carpeta del programa
sudo useradd --system --home /opt/telemet-colector --shell /usr/sbin/nologin telemet
sudo mkdir -p /opt/telemet-colector
sudo cp telemet_colector.py config.example.ini /opt/telemet-colector/
cd /opt/telemet-colector
sudo cp config.example.ini config.ini
sudo chown -R telemet:telemet /opt/telemet-colector
sudo chmod 600 config.ini

# 2. Carpeta donde se publica el JSON (junto a la app TeleMet Historial)
sudo install -d -o telemet -g telemet -m 755 /var/www/htdocs/rafa/telemethistorial/datos

# 3. Edita config.ini: station_id, api_key y, si hace falta, ruta_json
sudo -u telemet nano /opt/telemet-colector/config.ini
```

### Probar antes de dejarlo en servicio

```bash
cd /opt/telemet-colector
sudo -u telemet python3 telemet_colector.py --probar     # una lectura, la muestra y sale (no guarda nada)
sudo -u telemet python3 telemet_colector.py --una-vez    # una lectura, la guarda y escribe el JSON
sudo -u telemet python3 telemet_colector.py --estado     # resumen de lo guardado
```

### Dejarlo como servicio

```bash
sudo cp telemet-colector.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now telemet-colector
journalctl -u telemet-colector -f                        # ver el log en vivo
```

Si cambias rutas o el usuario, ajusta `User`, `WorkingDirectory`, `ExecStart` y `ReadWritePaths` en el `.service`.
Tras editar `config.ini`: `sudo systemctl restart telemet-colector`.

## Instalar la app TeleMet Historial en el mismo servidor

Copia `telemetria/telemet/historial/index.html` (y `apple-touch-icon.png`) a
`/var/www/htdocs/rafa/telemethistorial/`. La app busca el histórico en `datos/historial.json`
**relativo a su propia página**, es decir, en `/var/www/htdocs/rafa/telemethistorial/datos/historial.json`,
que es justo donde lo escribe el colector con la configuración por defecto. Si publicas la app en
otra carpeta, cambia `ruta_json` en `config.ini` (o `SERVIDOR_HISTORIAL_URL` en el HTML) para que coincidan.

Funcionamiento en la app:

- Al abrirla (y al pulsar «Iniciar», y cada 10 minutos con la pestaña visible) descarga el JSON y **añade** a la base local del navegador las lecturas que le faltan. Nunca borra ni modifica lo que el navegador ya tenía.
- Las gráficas de 12 h (y las de 7 días, que usan la misma base) quedan completas aunque la app haya estado cerrada.
- Solo se usa si el `stationId` del JSON coincide con el Station ID escrito en la app.
- Si el fichero no existe (por ejemplo, la copia de GitHub Pages) la app funciona como siempre, sin errores.
- Si la última lectura del servidor tiene más de 15 minutos, la app avisa de que el colector podría estar parado.

La API Key **no** aparece en el JSON.

Opcional (Apache con `mod_headers`): evitar que se cachee el JSON.

```apache
<Directory /var/www/htdocs/rafa/telemethistorial/datos>
    <FilesMatch "\.json$">
        Header set Cache-Control "no-store"
    </FilesMatch>
</Directory>
```

## Parámetros principales (`config.ini`)

| Sección | Parámetro | Por defecto | Qué hace |
|---|---|---|---|
| `estacion` | `station_id`, `api_key` | — | Tu estación y clave. También por variables de entorno `TELEMET_STATION_ID` / `TELEMET_API_KEY`. |
| `lectura` | `intervalo_s` | 60 | Segundos entre lecturas (mínimo 5). |
| `lectura` | `timeout_s` | 15 | Tiempo máximo de cada petición. |
| `lectura` | `backoff_base_s`, `backoff_max_s` | 2, 300 | Reintentos tras un fallo: 2, 4, 8… s hasta el tope. |
| `ciclo` | `duracion_horas` | 12 | Duración del ciclo. |
| `ciclo` | `modo` | `reinicio` | `reinicio`: al cumplirse el ciclo se borra todo y se empieza de cero. `deslizante`: solo se descartan las lecturas con más de `duracion_horas`. |
| `almacen` | `ruta_bd` | `./datos/telemet.sqlite` | Base de datos SQLite. |
| `salida` | `ruta_json` | `/var/www/htdocs/rafa/telemethistorial/datos/historial.json` | JSON que lee la app. |
| `salida` | `decimales` | 2 | Decimales del JSON exportado. |
| `log` | `nivel`, `fichero` | `INFO`, vacío | Nivel de log y fichero opcional con rotación. |

## Cosas a tener en cuenta

- **Modo `reinicio` (el pedido):** al cumplirse las 12 h el histórico del servidor queda vacío y vuelve a llenarse desde cero, así que justo después del reinicio un navegador sin datos propios verá la gráfica casi vacía. Con `modo = deslizante` el servidor conserva siempre las últimas 12 h completas; es un cambio de una línea.
- **El ciclo sobrevive a reinicios:** el instante de inicio se guarda en la base de datos, de modo que reiniciar el servicio o el servidor no reinicia el ciclo de 12 h.
- **Límite de llamadas de la API:** con `intervalo_s = 60` el colector hace 1.440 llamadas al día. Si los visitantes de la app usan la misma clave, suman las suyas. Comprueba el límite de tu clave y, si hace falta, sube el intervalo (con 120 s son 720 al día).
- **Observaciones repetidas:** si la estación no ha publicado nada nuevo, la API devuelve la misma observación y el colector no la guarda dos veces.
- **Cambio de estación:** si cambias `station_id`, el colector detecta que la base es de otra estación y la borra.
- **Errores de clave (401/403) o estación (404):** se registran en el log y el servicio sigue reintentando cada `backoff_max_s` segundos, por si fuera un fallo pasajero.
- El fichero `config.ini` contiene tu API Key: está en `.gitignore` y no debe subirse a GitHub.

## Resolución de problemas

| Síntoma | Qué mirar |
|---|---|
| `No se pudo escribir ...historial.json` | La carpeta de `ruta_json` no existe o no es escribible por el usuario `telemet` (y revisa `ReadWritePaths` en el `.service`). |
| La app no muestra la línea «Histórico del servidor» | Abre `https://tu-servidor/.../datos/historial.json` en el navegador: si da 404, la ruta no coincide con la de la app. |
| «El histórico del servidor es de otra estación» | El Station ID de la app no coincide con el del colector (se compara sin distinguir mayúsculas). |
| `HTTP 401` en el log | API Key incorrecta o caducada. |
