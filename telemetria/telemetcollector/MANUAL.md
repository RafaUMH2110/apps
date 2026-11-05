# TeleMet Collector — Complete Manual

Manual for the installation, use, configuration and internals of **TeleMet Collector**, the Python program that keeps a history of the last 24 hours (configurable) of your weather station on the Linux server and makes it available to the **TeleMet History** app.

- **Code:** `RafaUMH2110/apps` → `telemetria/telemetcollector/`
- **Companion app:** `telemetria/telemet/history/index.html` (TeleMet History)
- **Program version:** 1.0 · **JSON format:** 1

---

## Table of contents

1. [What it is for](#1-what-it-is-for)
2. [Architecture and data flow](#2-architecture-and-data-flow)
3. [Requirements](#3-requirements)
4. [Package contents](#4-package-contents)
5. [Step-by-step installation](#5-step-by-step-installation)
6. [First run and tests](#6-first-run-and-tests)
7. [Running as a service (systemd)](#7-running-as-a-service-systemd)
8. [Installing and connecting the TeleMet History app](#8-installing-and-connecting-the-telemet-history-app)
9. [Configuration reference (`config.ini`)](#9-configuration-reference-configini)
10. [Command-line reference](#10-command-line-reference)
11. [How it works inside](#11-how-it-works-inside)
12. [Data format](#12-data-format)
13. [How the app side works](#13-how-the-app-side-works)
14. [Day-to-day operation: logs, status, backups, updating](#14-day-to-day-operation-logs-status-backups-updating)
15. [Security](#15-security)
16. [Troubleshooting](#16-troubleshooting)
17. [Frequently asked questions](#17-frequently-asked-questions)
18. [Uninstalling](#18-uninstalling)
19. [Appendix: examples](#19-appendix-examples)

---

## 1. What it is for

TeleMet History draws evolution charts of the last 12 or 24 hours (and of 7 days) from the readings that **the browser itself** has been saving while the app was open. If the app is closed, the browser is suspended (background tab, locked iPad…) or the app is opened from a new device, those charts have gaps.

TeleMet Collector solves that with a process that **never stops** on the server:

1. It queries the station at a regular interval (by default, **every 5 minutes**).
2. It stores every reading in a SQLite database.
3. It keeps only the **last 24 hours** (`sliding` mode, the default; the number of hours is configurable with `duration_hours`, `--hours` or `TELEMET_HOURS`) or, if you prefer, it **deletes everything once those hours are up** and starts again (`reset` mode).
4. After every reading it publishes the history in a `history.json` file served by Apache.
5. When the app opens, it reads that JSON and **adds to its local database the readings it is missing**, so that the 12 and 24 hour charts lose no information.

Everything is configurable from a single `config.ini` file.

---

## 2. Architecture and data flow

```
┌──────────────┐      HTTPS      ┌───────────────────────────┐
│  Station     │ ──────────────► │ Weather Underground /     │
│  Vevor       │                 │ Earth Network API (PWS)   │
└──────────────┘                 └─────────────┬─────────────┘
                                               │ GET .../observations/current
                                               ▼
                              ┌────────────────────────────────┐
                              │  telemet_collector.py (systemd)│
                              │   · reading every interval_s   │
                              │   · retries with backoff       │
                              │   · the duration_hours rule    │
                              └───────┬─────────────────┬──────┘
                                      │                 │
                       INSERT OR IGNORE                 │ atomic write
                                      ▼                 ▼
                       ┌────────────────────┐   ┌──────────────────────────────┐
                       │ SQLite             │   │ history.json                 │
                       │ data/telemet.sqlite│   │ (folder served by Apache)    │
                       └────────────────────┘   └──────────────┬───────────────┘
                                                               │ HTTP(S), same origin
                                                               ▼
                                              ┌────────────────────────────────┐
                                              │ Browser: TeleMet History       │
                                              │  · IndexedDB (local history)   │
                                              │  · additive merge with the JSON│
                                              │  · 12 h / 24 h / 7 d charts    │
                                              └────────────────────────────────┘
```

Key design points:

- **The collector and the app are independent.** The collector knows nothing about browsers; it only writes a file. The app works the same without a collector (just with what the browser records).
- **No new port and no proxy.** Apache serves the JSON like any other static file. There are no ports to open and no CORS to configure if the app and the JSON are in the same place.
- **No dependencies.** Python standard library only (`urllib`, `sqlite3`, `json`, `configparser`, `logging`…).
- **The API Key never leaves the server.** The JSON contains weather data and the Station ID, but not the key.

---

## 3. Requirements

| Requirement | Detail |
|---|---|
| System | Linux with systemd (the design was tested for Debian/Ubuntu with Apache; any distribution will do). |
| Python | 3.8 or later. No `pip` needed. Check with `python3 --version`. |
| Network | Outbound HTTPS (443) to `api.weather.com`. |
| Credentials | The **Station ID** and **API Key** of your station on Weather Underground / Earth Network. |
| Web server | Apache (or another) serving the folder where the app will live. On the example server: `/var/www/htdocs/rafa/`. |
| Permissions | `sudo` access to create the service user, the folders and the systemd unit. |

---

## 4. Package contents

```
telemetria/telemetcollector/
├── telemet_collector.py         ← the program
├── config.example.ini           ← commented configuration template
├── telemet-collector.service    ← systemd unit
├── README.md                    ← quick guide
├── MANUAL.md                    ← this manual
└── .gitignore                   ← keeps config.ini, data/ and logs out of GitHub
```

Plus the app that consumes the data:

```
telemetria/telemet/history/
├── index.html                   ← TeleMet History (already reads the JSON)
└── apple-touch-icon.png
```

---

## 5. Step-by-step installation

The commands assume a Debian/Ubuntu server. Replace the paths if you use others.

### 5.1. Get the files

From GitHub (on your computer or on the server):

```bash
git clone https://github.com/RafaUMH2110/apps.git
cd apps/telemetria/telemetcollector
```

or copy the `telemet-collector/` folder from the downloaded `.zip` to the server (for example with `scp -r`).

### 5.2. Create the service user and the program folder

A user with no shell and no password, dedicated only to this:

```bash
sudo useradd --system --home /opt/telemet-collector --shell /usr/sbin/nologin telemet
sudo mkdir -p /opt/telemet-collector/data
sudo cp telemet_collector.py config.example.ini /opt/telemet-collector/
sudo cp config.example.ini /opt/telemet-collector/config.ini
sudo chown -R telemet:telemet /opt/telemet-collector
sudo chmod 600 /opt/telemet-collector/config.ini
```

> **Important:** the folder `/opt/telemet-collector/data` must exist **before** the service starts. The systemd unit lists it in `ReadWritePaths` and, if it does not exist, systemd cannot set up the protected environment and the service fails at start-up (error `status=226/NAMESPACE`).

### 5.3. Create the folder where the JSON is published

It must be inside the folder served by Apache, next to the app, and writable by the `telemet` user:

```bash
sudo install -d -o telemet -g telemet -m 755 /var/www/htdocs/rafa/telemethistory/data
```

Apache only needs to **read**; the file is published with `644` permissions automatically.

### 5.4. Edit the configuration

```bash
sudo -u telemet nano /opt/telemet-collector/config.ini
```

At the very least, fill in:

```ini
[station]
station_id = YOUR_STATION_ID
api_key    = YOUR_API_KEY
```

And check `json_path` in the `[output]` section (it must point to the folder from step 5.3). The remaining parameters have sensible defaults; all of them are explained in [section 9](#9-configuration-reference-configini).

> Alternative to avoid leaving secrets in the `.ini`: use the environment variables `TELEMET_STATION_ID` and `TELEMET_API_KEY` (see [section 15](#15-security)).

---

## 6. First run and tests

Run these tests **before** installing the service, always as the `telemet` user so that permission problems show up:

```bash
cd /opt/telemet-collector
```

### 6.1. Test the connection to the station (stores nothing)

```bash
sudo -u telemet python3 telemet_collector.py --test
```

Expected output: the date of the observation and the values as JSON, for example:

```
Observation from 2026-11-03 21:19:12
{
  "temp_c": 18.4,
  "heat_index_c": 18.4,
  "dewpoint_c": 11.2,
  "humidity_pct": 62,
  "pressure_hpa": 1015.3,
  "wind_kmh": 7.2,
  "gust_kmh": 12.9,
  "wind_dir_deg": 204,
  "rainrate_mmh": 0.0,
  "rain_total_mm": 0.0,
  "solarradiation_wm2": 143.7,
  "uv_index": 1.0,
  "quality_code": 1
}
```

If it prints `ERROR: HTTP 401…` the key is wrong; if it prints `HTTP 404…`, the Station ID does not exist (see [section 16](#16-troubleshooting)).

### 6.2. Make a real reading and publish the JSON

```bash
sudo -u telemet python3 telemet_collector.py --once
ls -l /var/www/htdocs/rafa/telemethistory/data/
sudo -u telemet python3 telemet_collector.py --status
```

You should see `history.json` with `-rw-r--r--` permissions and, in `--status`, one stored reading.

### 6.3. Check that Apache serves it

From any computer:

```bash
curl -s https://YOUR-SERVER/PATH/telemethistory/data/history.json | head -c 400
```

(or open it in the browser). If you get a 404, the published path does not match `json_path` (see [section 8](#8-installing-and-connecting-the-telemet-history-app)).

### 6.4. Running in the foreground (optional)

```bash
sudo -u telemet python3 telemet_collector.py
```

You will see one log line per reading. Stop it with `Ctrl+C` (it closes the database cleanly).

---

## 7. Running as a service (systemd)

### 7.1. Installation

```bash
sudo cp /home/<your-user>/apps/telemetria/telemetcollector/telemet-collector.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now telemet-collector
```

### 7.2. Unit contents and what each line does

```ini
[Unit]
Description=TeleMet Collector (weather-station history)
# Start once the network is up
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=telemet
Group=telemet
WorkingDirectory=/opt/telemet-collector
ExecStart=/usr/bin/python3 /opt/telemet-collector/telemet_collector.py -c /opt/telemet-collector/config.ini
# If the process dies, it is relaunched after 10 s
Restart=always
RestartSec=10

# Hardening: read-only file system, no access to /home, private /tmp...
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
# ...except these two folders, which must exist before starting
ReadWritePaths=/opt/telemet-collector/data /var/www/htdocs/rafa/telemethistory/data

[Install]
# Start with the server
WantedBy=multi-user.target
```

> In `.service` files, comments must be on their own line (starting with `#`); systemd does not allow comments at the end of a setting line.

> If you change the user, the program paths or the JSON path, adjust `User`, `Group`, `WorkingDirectory`, `ExecStart` and `ReadWritePaths`. If you use a log `file` in `[log]`, also add its folder to `ReadWritePaths`.

### 7.3. Common commands

| Action | Command |
|---|---|
| Check status | `systemctl status telemet-collector` |
| Follow the log live | `journalctl -u telemet-collector -f` |
| See today's log | `journalctl -u telemet-collector --since today` |
| Restart after changing `config.ini` | `sudo systemctl restart telemet-collector` |
| Stop | `sudo systemctl stop telemet-collector` |
| Do not start with the server | `sudo systemctl disable telemet-collector` |

The program responds to `SIGTERM` (the one `systemctl stop` sends) and to `SIGINT`: it ends the current wait, closes the database and exits with code 0.

### 7.4. Alternative without a service: cron

If you prefer not to use systemd, you can schedule a one-off reading with `--once`:

```cron
*/5 * * * * telemet /usr/bin/python3 /opt/telemet-collector/telemet_collector.py -c /opt/telemet-collector/config.ini --once >> /var/log/telemet-collector.log 2>&1
```

It works the same (the `duration_hours` rule is applied on every run), but you lose the retries with backoff and the fixed rate of the loop. systemd is recommended.

### 7.5. Variant: secrets outside `config.ini`

```bash
sudo install -m 600 -o root -g root /dev/null /etc/telemet-collector.env
echo 'TELEMET_API_KEY=YOUR_API_KEY'       | sudo tee -a /etc/telemet-collector.env
echo 'TELEMET_STATION_ID=YOUR_STATION_ID' | sudo tee -a /etc/telemet-collector.env
```

and in the unit, inside `[Service]`:

```ini
EnvironmentFile=/etc/telemet-collector.env
```

Environment variables **take priority** over the values in `config.ini`.

---

## 8. Installing and connecting the TeleMet History app

### 8.1. Copy the app

Copy `index.html` and `apple-touch-icon.png` to the app folder on the server:

```bash
sudo mkdir -p /var/www/htdocs/rafa/telemethistory
sudo cp telemetria/telemet/history/{index.html,apple-touch-icon.png} /var/www/htdocs/rafa/telemethistory/
```

### 8.2. How the app and the JSON are linked

The app looks for the history at a path **relative to its own page**:

```js
const SERVER_HISTORY_URL = 'data/history.json';
```

So, if the app is at `…/telemethistory/index.html`, the JSON must be at `…/telemethistory/data/history.json`. That is exactly what the collector writes with the default configuration:

```
json_path = /var/www/htdocs/rafa/telemethistory/data/history.json
```

| If… | Do… |
|---|---|
| You publish the app in **another folder** | Change `json_path` in `config.ini` so that it ends in `<app-folder>/data/history.json`, and update `ReadWritePaths` in the unit. |
| You want the JSON **somewhere else** (another folder or domain) | Change the `SERVER_HISTORY_URL` constant in the HTML. If it is another origin, the server must send CORS headers (see 8.4). |

### 8.3. Preventing the JSON from being cached (optional)

The app already adds a `?t=<timestamp>` parameter to every request, so this is not usually needed. If you want to reinforce it in Apache (requires `mod_headers`):

```apache
<Directory /var/www/htdocs/rafa/telemethistory/data>
    <FilesMatch "\.json$">
        Header set Cache-Control "no-store"
    </FilesMatch>
</Directory>
```

Enabling compression of the JSON (`mod_deflate`, type `application/json`) reduces the transferred size, although with 144 readings it hardly matters (~45 KB).

### 8.4. Special cases

- **App and JSON on the same server and origin (the normal case):** nothing else to do.
- **App on HTTPS:** the JSON must also be served over HTTPS (it is automatically if the path is relative).
- **JSON on another origin:** add `Header set Access-Control-Allow-Origin "https://app-origin"` in Apache for that file.
- **Opening `index.html` straight from disk (`file://`):** the browser blocks reading the JSON; the app ignores it and works only with its local database.
- **SELinux (RHEL/Rocky/Alma):** if Apache cannot read the JSON, label the folder, e.g. `sudo chcon -R -t httpd_sys_content_t /var/www/.../data`.

### 8.5. Check that the app uses it

Open the app, enter (or leave saved) the Station ID and expand the **“Evolution over the last 12 hours”** panel (or 24, depending on the panel's 12 h / 24 h selector). Under the note you will see one of these lines (see [section 13.4](#134-messages-shown-by-the-app)).

---

## 9. Configuration reference (`config.ini`)

Standard INI format. Relative paths are resolved **relative to the folder of `config.ini`** (not relative to the directory the program is launched from). Comments start with `#`. If a parameter is missing, the default value in the table is used.

### 9.1. `[station]`

| Parameter | Default | Description |
|---|---|---|
| `station_id` | *(empty)* | Station identifier (e.g. `IELCHE12`). Required. If it differs from the one the database was using, **the old data is deleted** (see 11.7). |
| `api_key` | *(empty)* | Weather Underground / Earth Network API key. Required. |

Both can come from the environment variables `TELEMET_STATION_ID` and `TELEMET_API_KEY`, which prevail over the `.ini`. Likewise, `TELEMET_HOURS` overrides `duration_hours`.

### 9.2. `[reading]`

| Parameter | Default | Min. | Description |
|---|---|---|---|
| `base_url` | `https://api.weather.com/v2/pws/observations/current` | — | Current-observation endpoint. It would only need touching if the API changes (or for tests against a simulated server). |
| `interval_s` | `300` | 5 | Seconds between readings. |
| `timeout_s` | `15` | 1 | Maximum wait for each HTTP request. |
| `backoff_base_s` | `2` | 0.5 | Initial wait after a transient failure. The following ones double: base, 2·base, 4·base… |
| `backoff_max_s` | `300` | `backoff_base_s` | Cap on the wait after failures. It is also the retry interval after key/station errors (401/403/404). |

**Choosing `interval_s`.** Every reading is one API call:

| `interval_s` | Calls/day | Readings in 24 h | Approx. JSON size |
|---|---|---|---|
| 60 | 1,440 | 1,440 | ~460 KB |
| 120 | 720 | 720 | ~230 KB |
| **300 (default)** | **288** | **288** | **~90 KB** |
| 600 | 144 | 144 | ~45 KB |

The size is proportional to the hours kept (half with 12 h, double with 48 h).

Visitors of the app who use the same API Key consume additional calls (the app polls on its own every 60 s by default while it is running). Check your key's daily limit before lowering the interval much.

### 9.3. `[cycle]`

| Parameter | Default | Description |
|---|---|---|
| `duration_hours` | `24` | Hours of history that are kept. Decimals allowed (e.g. `0.5`). Must be > 0. 24 h are enough for the app's 12 h and 24 h charts. It can be overridden without touching the `.ini` with the `--hours H` option or the `TELEMET_HOURS` environment variable (precedence: `--hours` > `TELEMET_HOURS` > `.ini`). |
| `mode` | `sliding` | What happens when `duration_hours` is reached. See below. |

**`mode = sliding` (default).** On every round, readings older than `duration_hours` are deleted. The server always has the last `duration_hours` in full. It is the recommended mode: there is never a moment with an empty history.

**`mode = reset`.** Time is counted from the start of the cycle; when `now − start ≥ duration_hours`, **everything is deleted** and a new cycle opens. Right afterwards the server history is empty and fills up gradually; a browser with no data of its own would then see an almost empty chart until some time passes. The start instant is stored in the database, so restarting the service or the server does **not** restart the cycle.

### 9.4. `[storage]`

| Parameter | Default | Description |
|---|---|---|
| `db_path` | `./data/telemet.sqlite` | SQLite file. The folder is created if it does not exist (if the user has permission). `*.sqlite-wal` and `*.sqlite-shm` files are also created (WAL mode). |

### 9.5. `[output]`

| Parameter | Default | Description |
|---|---|---|
| `json_path` | `/var/www/htdocs/rafa/telemethistory/data/history.json` | Where the history is published. The **folder** must be writable by the service user (the atomic write creates a temporary file in it). |
| `decimals` | `2` | Decimals of the exported numeric values. The database keeps the full value; rounding only affects the JSON. |

### 9.6. `[log]`

| Parameter | Default | Description |
|---|---|---|
| `level` | `INFO` | `DEBUG`, `INFO`, `WARNING` or `ERROR`. |
| `file` | *(empty)* | If given, in addition to standard output it writes to that file with rotation (1 MB × 3 copies). Empty = standard output only, which under systemd goes to `journalctl`. |

### 9.7. Start-up validations

The program exits with a clear message if: `-c` points to a non-existent file; `duration_hours` ≤ 0; `mode` is neither `reset` nor `sliding`; or `station_id`/`api_key` are missing (in both `.ini` and environment). Numeric values below the minimum are raised to the minimum.

### 9.8. Applying changes

`config.ini` is read only at start-up: after editing it, run `sudo systemctl restart telemet-collector`.

---

## 10. Command-line reference

```
python3 telemet_collector.py [-c CONFIG_PATH] [--hours H] [--once | --test | --status]
```

| Option | Effect | Writes to DB / JSON |
|---|---|---|
| *(none)* | Continuous service: infinite loop until `SIGINT`/`SIGTERM`. | Yes |
| `-c`, `--config PATH` | Configuration file. If omitted, it uses `config.ini` next to the script **if it exists**; otherwise, only defaults and environment. | — |
| `--hours H` | Hours of history to keep (decimals allowed). Overrides `duration_hours` of the `.ini` and `TELEMET_HOURS`. | — |
| `--once` | One reading; stores it, exports the JSON and exits. | Yes |
| `--test` | One reading; prints it and exits. Exit code 1 if it fails. | **No** |
| `--status` | DB summary: path, station, number of readings with first/last instant, cycle start. Needs no credentials. | No |

`--once`, `--test` and `--status` are mutually exclusive.

Example of `--status`:

```
DB:            /opt/telemet-collector/data/telemet.sqlite
Station:       IELCHE12
Readings:      141  (from 2026-11-03 09:34:12 to 2026-11-03 21:19:12)
Cycle since:   2026-11-03 08:50:03
```

---

## 11. How it works inside

### 11.1. The main loop

```
start-up
  └─ load config, open SQLite, recover the cycle start
  └─ export an initial JSON (so the app finds the file right away)
  └─ repeat until SIGINT/SIGTERM:
        1. apply the duration_hours rule
        2. query the API
        3. store the reading (if it is new)
        4. export the JSON (if anything changed)
        5. wait (interval_s minus what the round took, minimum 1 s)
```

The wait is **fixed-rate**: the time of the request is subtracted, so with `interval_s = 300` the readings do not drift little by little.

### 11.2. The API request

A `GET` is made to the endpoint with these parameters (the key travels as a URL parameter, just as in the app):

```
stationId=<id>&format=json&numericPrecision=decimal&units=m&apiKey=<key>
```

`units=m` asks for metric units (°C, km/h, hPa, mm). The header `User-Agent: telemet-collector/1.0` is sent. If the response has no body (HTTP 204) or the `observations` list is empty, “The API returned no new observations” is logged and the normal interval is awaited.

### 11.3. Value extraction

The function `extract_values()` is a **faithful port** of the app's `extractValues()` (same fields, same fallbacks between field names and same formulas), so that a value stored on the server is identical to the one the browser would have stored. See [section 12.3](#123-fields-of-v-readings) for the mapping.

The **feels-like temperature** (`heat_index_c`) is computed locally, with no further API calls:

| Temperature | Method |
|---|---|
| ≥ 26.7 °C (≈ 80 °F) | NWS heat index (Rothfusz) using humidity; never below the real temperature. |
| ≤ 10 °C | Wind chill (Environment Canada) if the wind is > 4.8 km/h; never above the real temperature. |
| in between | The air temperature itself. |

It was checked against the app's JavaScript implementation with 880 combinations of temperature, humidity and wind: **0 discrepancies**.

### 11.4. Error handling

| Situation | Reaction |
|---|---|
| Network failure, timeout, HTTP 5xx/429/others, invalid JSON | **Transient.** Warning in the log and retry with exponential backoff: `backoff_base_s · 2^(n−1)` up to `backoff_max_s`. At the first success the counter goes back to 0. |
| HTTP 401 or 403 (invalid key or no permission) | **Fatal but not deadly.** Error in the log and a retry every `backoff_max_s`. The service does not go down, in case it is a passing failure. |
| HTTP 404 (non-existent station or endpoint) | Same as above. |
| Observation whose instant (`epoch`) is already stored | It is not stored twice and the JSON is not rewritten. |
| Unexpected exception in the code | Logged with a traceback and the loop continues after a backoff; the service does not die. |
| The JSON cannot be written | Error in the log (with the path and a hint about permissions) and reading/storing carries on. |

### 11.5. The `duration_hours` rule

It runs **at the beginning of every round**, before requesting the reading.

- **Sliding:** `DELETE … WHERE epoch_ms < now − duration`. If it deleted anything, the JSON is re-exported.
- **Reset:** if `now − cycle_start ≥ duration`, `DELETE` of all readings + `VACUUM`, new `cycle_start` = now (stored in the `meta` table) and re-export. Log message: “24 h cycle completed: N readings deleted and a new cycle begins.”

### 11.6. When the JSON is written

- Once at start-up (even if there are no readings yet, with `readings: []`).
- After every **new** reading stored.
- After any change made by the cycle rule (deletion of readings).
- After a network error, **only** if the cycle had just changed the content.

If the station stops publishing data, the JSON stops changing; the app detects it (see 13.4).

### 11.7. Changing station

At start-up, the `station_id` stored in the `meta` table is compared with the one in the configuration. If they differ, all readings are deleted and the cycle is restarted, so that data from two stations is never mixed.

### 11.8. Atomic writing of the JSON

1. A hidden temporary file (`.history-XXXX.tmp`) is created **in the same destination folder**.
2. The full content is written and it is given `0644` permissions.
3. It is renamed over `history.json` with `os.replace()` (an atomic operation within the same file system).

This way Apache never serves a half-written JSON. That is why the service user needs write permission on the **folder**, not just on the file. If anything fails, the temporary file is deleted.

### 11.9. The database

SQLite in WAL mode (more robust against power cuts):

```sql
CREATE TABLE readings (
  epoch_ms INTEGER PRIMARY KEY,   -- instant of the observation, ms since 1970 (UTC)
  vals     TEXT NOT NULL          -- JSON with the values (see section 12.3)
);
CREATE TABLE meta (
  k TEXT PRIMARY KEY,
  v TEXT NOT NULL                 -- station_id, cycle_start_ms
);
```

`epoch_ms` is the primary key, and rows are inserted with `INSERT OR IGNORE`: repeating an observation duplicates nothing. To inspect it by hand:

```bash
sudo -u telemet sqlite3 /opt/telemet-collector/data/telemet.sqlite \
  "SELECT datetime(epoch_ms/1000,'unixepoch','localtime'), json_extract(vals,'$.temp_c') FROM readings ORDER BY epoch_ms DESC LIMIT 10;"
```

(requires the `sqlite3` package; the program does not need it).

### 11.10. Orderly shutdown

`SIGTERM`/`SIGINT` set a flag; the loop's wait is interrupted, the database is closed and “Stopped.” is printed. If the signal arrives during an HTTP request, it waits for it to finish (at most `timeout_s`).

---

## 12. Data format

### 12.1. The `history.json` file

```json
{
  "format": 1,
  "stationId": "IELCHE12",
  "generatedMs": 1793737178059,
  "mode": "sliding",
  "durationMs": 43200000,
  "cycleStartMs": 1793737168054,
  "cycleEndMs": null,
  "intervalS": 300.0,
  "readings": [
    {
      "t": 1793737178000,
      "v": {
        "temp_c": 18.4,
        "heat_index_c": 18.4,
        "dewpoint_c": 11.2,
        "humidity_pct": 62,
        "pressure_hpa": 1015.3,
        "wind_kmh": 7.2,
        "gust_kmh": 12.9,
        "wind_dir_deg": 204,
        "rainrate_mmh": 0.0,
        "rain_total_mm": 0.0,
        "solarradiation_wm2": 143.7,
        "uv_index": 1.0,
        "quality_code": 1
      }
    }
  ]
}
```

### 12.2. Header

| Field | Meaning |
|---|---|
| `format` | Format version (currently `1`). The app **rejects** files with any other value. |
| `stationId` | Station the data belongs to. The app only uses it if it matches (case-insensitively) the Station ID entered in it. |
| `generatedMs` | Instant of the export (ms UTC). |
| `mode` | `sliding` or `reset`. |
| `durationMs` | Cycle duration in milliseconds (24 h = 86,400,000). |
| `cycleStartMs` | Start of the cycle stored in the DB. In sliding mode it is informative only. |
| `cycleEndMs` | Planned end of the cycle (only in `reset` mode; `null` in sliding). |
| `intervalS` | Configured reading interval; the app uses it to adjust the “collector stopped” warning. |
| `readings` | List sorted by `t` ascending. |

### 12.3. Fields of `v` (readings)

Each value can be `null` if the station did not report it.

| Field | Unit | Origin in the API response |
|---|---|---|
| `temp_c` | °C | `metric.temp` (or `metric.tempAvg`) |
| `heat_index_c` | °C | **Computed** (see 11.3) |
| `dewpoint_c` | °C | `dewpoint`, `metric.dewpt`, `metric.dewptAvg` or `metric.dewpoint` |
| `humidity_pct` | % | `humidity` (or `humidityAvg`) |
| `pressure_hpa` | hPa | `metric.pressure` (or the mean of `pressureMax`/`pressureMin`) |
| `wind_kmh` | km/h | `metric.windSpeed` (or `windspeedAvg`) |
| `gust_kmh` | km/h | `metric.windGust` (or `windgustAvg`) |
| `wind_dir_deg` | ° (0–360) | `winddir` / `windDir` / `winddirAvg` |
| `rainrate_mmh` | mm/h | `metric.precipRate` |
| `rain_total_mm` | mm | `metric.precipTotal` |
| `solarradiation_wm2` | W/m² | `solarRadiation` / `solarradiation` / `solarRadiationHigh` |
| `uv_index` | — | `uv` (or `uvHigh`) |
| `quality_code` | — | `qcStatus` / `qualityControlFlag`, or `"N/A"`. The value `1` means “verified” |

### 12.4. Time zones

All instants are **epoch in milliseconds (UTC)**. The time zone only comes into play when they are displayed: the collector's log uses the server's local time; the app uses the browser's.

---

## 13. How the app side works

Everything is in `telemetria/telemet/history/index.html`, in the “SERVER HISTORY (TeleMet Collector)” block.

### 13.1. Adjustable constants (in the HTML itself)

| Constant | Value | Description |
|---|---|---|
| `SERVER_HISTORY_URL` | `'data/history.json'` | Path of the JSON, relative to the page. |
| `SERVER_TIMEOUT_MS` | `15000` | Maximum time of the download. |
| `SERVER_SYNC_EVERY_MIN` | `10` | Every how many minutes it is queried again while the app is open. |
| `SERVER_MERGE_TOLERANCE_MS` | `30000` | A server reading within 30 s of a local one counts as the same one. |
| `SERVER_STALE_WARNING_MIN` | `15` | Minutes without new readings after which a warning is shown (a minimum; it is extended to 3 collector intervals if that is larger). |

### 13.2. When it syncs

1. **When the app opens**, without waiting for “Start” to be pressed (it uses the Station ID saved in the browser).
2. **When “Start” is pressed**, before the gap recovery with the Weather Underground API, which then only queries the days that are still incomplete and uses fewer calls.
3. **Every 10 minutes** while the tab is visible.
4. **When returning to the tab** (`visibilitychange` event), for example on unlocking the iPad.

If a sync is already in progress, the others are skipped.

### 13.3. How the data is merged (always additively)

1. It downloads the JSON (with `?t=<now>` to dodge caches).
2. It validates: `format === 1`, `readings` is a list, the `stationId` matches.
3. It reads from IndexedDB the local readings of that time range (±30 s).
4. For every server reading, it looks (binary search) for a local one within 30 s. If there is one, it discards it; if not, it marks it as new.
5. It inserts all the new ones in **a single transaction**.
6. If it added anything and the evolution panel is open, it redraws it.

Guarantees:

- It **never deletes or modifies** anything the browser already had.
- Server readings are **not compared with each other**, only with what was already local; this way very close server readings do not discard one another.
- If even the local database cannot be read (private mode, IndexedDB blocked…) nothing is inserted, so as not to risk duplicates.
- The server data goes into the **same database** used by the 7 day charts and the daily summary, so it completes them too (the browser purges at 9 days).

### 13.4. Messages shown by the app

In the “Evolution over the last 12 hours” panel (or 24):

| Situation | Message |
|---|---|
| Readings were added | “Server history: contributed N readings that were missing in this browser (latest server reading: HH:MM).” |
| Everything was already there | “Server history: queried, no reading was missing (latest server reading: HH:MM).” |
| The collector has not stored anything yet | “Server history: the collector has no stored readings yet.” |
| Latest reading too old | Appended: “Warning: the server has recorded nothing for more than N minutes; the collector may be stopped.” |
| Another station | “The server history belongs to another station (X)… it was not used.” |
| Invalid format or error while saving | “The server history could not be used…” |
| The file does not exist / no network | **Nothing is shown** and the app works as usual (the GitHub Pages case). |

### 13.5. What it does NOT do

- It does not use the server instead of the browser: the browser keeps recording its own readings every `pollInterval` (60 s by default).
- It does not offer more hours than the ones stored: the JSON only holds the server's window (`duration_hours`, 24 h by default). With a 24 h window in the app, the older half depends on what the browser has saved if `duration_hours` is below 24.
- It does not support several stations in the same JSON (see the FAQ).

---

## 14. Day-to-day operation: logs, status, backups, updating

### 14.1. Reading the log

```
2026-11-03 21:19:12 INFO TeleMet Collector 1.0 · station ITEST1 · every 300 s · cycle 24 h (sliding)
2026-11-03 21:19:12 INFO DB: /opt/telemet-collector/data/telemet.sqlite · JSON: /var/www/.../history.json
2026-11-03 21:19:12 INFO 21:19:12  T=18.4 °C  RH=62 %  wind=7.2 km/h  stored
2026-11-03 21:24:12 INFO 21:24:12  T=18.3 °C  RH=62 %  wind=6.8 km/h  stored
2026-11-03 21:29:12 WARNING Reading failed (HTTP 500); retry #1 in 2 s.
2026-11-03 21:29:15 INFO 21:24:12  T=18.3 °C  RH=62 %  wind=6.8 km/h  (repeated observation, not stored)
```

The time at the start of the data line is that of the station's **observation** (not the server's): if it matches the previous one, the station has not published anything new.

### 14.2. Quick health checks

```bash
systemctl is-active telemet-collector                 # active
sudo -u telemet python3 /opt/telemet-collector/telemet_collector.py -c /opt/telemet-collector/config.ini --status
ls -l --time-style=full-iso /var/www/htdocs/rafa/telemethistory/data/history.json   # recent date
```

### 14.3. Backups

They are not necessary: this is a few hours of reproducible, ephemeral data. Only `config.ini` (because of the key) is worth keeping somewhere safe.

### 14.4. Updating the program

```bash
cd ~/apps && git pull
sudo cp telemetria/telemetcollector/telemet_collector.py /opt/telemet-collector/
sudo chown telemet:telemet /opt/telemet-collector/telemet_collector.py
sudo systemctl restart telemet-collector
journalctl -u telemet-collector -n 20
```

If an update adds new parameters, compare `config.example.ini` with your `config.ini`: any missing parameters take their default value. Your `config.ini` is not overwritten.

### 14.5. Updating the app

```bash
sudo cp ~/apps/telemetria/telemet/history/index.html /var/www/htdocs/rafa/telemethistory/
```

Browsers will load the new version on reload (sometimes you have to force it with `Ctrl+Shift+R`).

### 14.6. Changing mode or interval

Edit `config.ini` and restart the service. Going from `reset` to `sliding` loses nothing; going from `sliding` to `reset`, the cycle counts from the `cycle_start` stored in the DB (the one from when it was first created), so it might reset right away. If you want a new cycle starting now, stop the service and delete `data/telemet.sqlite*` before starting it.

---

## 15. Security

- **API Key:** it is in `config.ini` with `600` permissions and owned by `telemet`. Do not upload it to GitHub (the `.gitignore` already excludes it). Alternative: environment variables with `EnvironmentFile` (section 7.5).
- **Exposure:** the published JSON does not contain the key, but it does contain weather data and the Station ID, accessible to anyone who knows the URL. If you do not want them to be public, protect the `data/` folder with Apache authentication (note that the app would then have to send it).
- **Least privilege:** the service runs as a user with no shell, with `NoNewPrivileges`, `ProtectSystem=strict`, `ProtectHome` and `PrivateTmp`; it can only write to `data/` and to the JSON folder.
- **Key in the API URL:** that is how the Weather Underground API is designed; the connection is HTTPS, but the key would show up in the logs of an intermediate proxy if there were one.
- **Network:** the program only makes outbound connections; it opens no port.

---

## 16. Troubleshooting

| Symptom | Probable cause | What to do |
|---|---|---|
| The service does not start; `status=226/NAMESPACE` | A `ReadWritePaths` folder does not exist (`/opt/telemet-collector/data` or the JSON one). | Create them (sections 5.2 and 5.3) and `systemctl restart`. |
| `ERROR: HTTP 401` / log “HTTP 401: invalid API Key” | Key mis-copied, expired or without permission for that Station ID. | Check `api_key` in `config.ini` (no spaces or quotes). It retries by itself every `backoff_max_s`. |
| `HTTP 404: Station ID not found` | Wrong Station ID (or with lowercase letters/spaces). | Fix `station_id`. |
| Repeated “Reading failed (network failure…)” | The server has no Internet access, DNS or firewall. | `curl -I https://api.weather.com`; check proxy/firewall. |
| “The API returned no new observations” | The station is offline or has no recent data. | Check the station and its Wi-Fi/Weather Underground connection. |
| “Could not write …history.json” | The folder does not exist or the `telemet` user cannot write to it (or it is missing from `ReadWritePaths`). | `ls -ld` the folder; `chown telemet:telemet`; check the unit. |
| `curl` to the JSON gives 404 | The Apache path does not match `json_path`. | Check `DocumentRoot`/alias and the real path of the file. |
| `curl` to the JSON gives 403 | Apache cannot read the folder (directory permissions or SELinux). | `chmod 755` on the intermediate folders; `chcon` if you use SELinux. |
| The app shows no “Server history” line | It cannot find/read the JSON (404, `file://`, another origin without CORS) or there is no Station ID. | Open the JSON URL in the browser; look at the console (F12 → Network). |
| The app says “another station (X)” | The Station ID in the app and the collector's do not match. | Enter in the app the same Station ID as in `config.ini`. |
| The app warns “the collector may be stopped” | The latest server reading is very old. | `systemctl status`, `journalctl`; check the station and the network. |
| Charts with broken stretches in the line | A gap > 90 min without readings (the app cuts the line from there). | Look at the collector's log for that interval. |
| The server history empties suddenly when `duration_hours` is up | You are in `mode = reset`. | Change to `mode = sliding` and restart the service. |
| `PermissionError` when opening the DB | The `data/` folder does not belong to `telemet`. | `sudo chown -R telemet:telemet /opt/telemet-collector`. |
| Log dates are shifted | The server's time zone differs from the expected one. | `timedatectl`; the data (epoch UTC) is correct anyway. |

For detailed debugging: set `level = DEBUG`, restart and watch `journalctl -u telemet-collector -f`.

---

## 17. Frequently asked questions

**What happens if the server restarts or there is a power cut?**
The service starts with the system (`enable`) and reopens the SQLite database. In sliding mode, on return it continues where it left off (the readings of the last `duration_hours` are kept; there will be a gap for the downtime). In reset mode, the cycle continues with its original start.

**Can I keep more (or fewer) than 24 hours?**
Yes: change `duration_hours` in the `.ini` (e.g. `48`), or use `--hours 48` / `TELEMET_HOURS=48` without touching the file. The app's 12 h and 24 h charts only need 24 h; with more hours, the server delivers extra data that stays in the browser's local database and feeds the 7 day charts. The JSON size grows proportionally. With fewer than 24 h, the 24 h chart will depend, in its older part, on what the browser has saved.

**Can I use an interval below 5 s?**
No: the minimum is 5 s, and the API does not update that fast; it would also eat up the daily quota.

**What if two readings arrive with the same instant?**
Only the first one is stored (primary key `epoch_ms`).

**Can several stations be monitored?**
Each collector instance serves one station. For several, create another folder with its own `config.ini`, another `db_path`, another `json_path` and another systemd unit (`telemet-collector-2.service`). The app, however, reads a single `data/history.json` relative to its page, so each station would need its own copy of the app in another folder (or change `SERVER_HISTORY_URL`).

**Why not a Python HTTP server of its own?**
A static file served by Apache is simpler and more robust: there is no other exposed process, no port, no mixed HTTP/HTTPS content problems, and it scales effortlessly.

**Does it work with the app copy on GitHub Pages?**
The app works, but without the server: since `data/history.json` does not exist on Pages, the read is ignored with no errors. To use the server history, the app must be hosted on the same server.

**Does the collector need someone to have the app open?**
No. It works 24 h a day; the app only reads what is already stored.

**Does it use much CPU, memory or disk?**
No: a few milliseconds of CPU every 5 minutes, a few MB of memory and tens of KB of disk.

**How do I test it without a real station?**
With `base_url` pointing to a simulated server that returns the same format as the API, and short durations/intervals (`interval_s = 5`, `duration_hours = 0.004`) to see the deletion within seconds.

---

## 18. Uninstalling

```bash
sudo systemctl disable --now telemet-collector
sudo rm /etc/systemd/system/telemet-collector.service
sudo systemctl daemon-reload
sudo rm -rf /opt/telemet-collector
sudo rm -f /var/www/htdocs/rafa/telemethistory/data/history.json
sudo userdel telemet
```

The app will keep working without the JSON.

---

## 19. Appendix: examples

### 19.1. Default `config.ini` (5 min, sliding, 24 h)

```ini
[station]
station_id = YOUR_STATION_ID
api_key    = YOUR_API_KEY

[reading]
base_url       = https://api.weather.com/v2/pws/observations/current
interval_s     = 300
timeout_s      = 15
backoff_base_s = 2
backoff_max_s  = 300

[cycle]
duration_hours = 24
mode = sliding

[storage]
db_path = ./data/telemet.sqlite

[output]
json_path = /var/www/htdocs/rafa/telemethistory/data/history.json
decimals = 2

[log]
level = INFO
file  =
```

### 19.2. High resolution (one reading per minute)

```ini
[reading]
interval_s = 60
```

(1,440 calls per day; ~460 KB of JSON).

### 19.3. Full wipe every 12 h (“reset” behaviour)

```ini
[cycle]
duration_hours = 12
mode = reset
```

### 19.4. Keep 48 h

```ini
[cycle]
duration_hours = 48
mode = sliding
```

Or without touching the file: `python3 telemet_collector.py --hours 48` (or `TELEMET_HOURS=48`).

### 19.5. Complete installation in one block (to copy and paste)

```bash
# From the apps/telemetria/telemetcollector folder of the cloned repository
sudo useradd --system --home /opt/telemet-collector --shell /usr/sbin/nologin telemet
sudo mkdir -p /opt/telemet-collector/data
sudo cp telemet_collector.py /opt/telemet-collector/
sudo cp config.example.ini /opt/telemet-collector/config.ini
sudo chown -R telemet:telemet /opt/telemet-collector
sudo chmod 600 /opt/telemet-collector/config.ini
sudo install -d -o telemet -g telemet -m 755 /var/www/htdocs/rafa/telemethistory/data

sudo -u telemet nano /opt/telemet-collector/config.ini        # station_id and api_key
sudo -u telemet python3 /opt/telemet-collector/telemet_collector.py -c /opt/telemet-collector/config.ini --test
sudo -u telemet python3 /opt/telemet-collector/telemet_collector.py -c /opt/telemet-collector/config.ini --once

sudo cp telemet-collector.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now telemet-collector
journalctl -u telemet-collector -f
```

---

*Author: Rafael Puerto (r.puerto@umh.es) · Department of Systems Engineering and Automation · Miguel Hernández University of Elche.*
