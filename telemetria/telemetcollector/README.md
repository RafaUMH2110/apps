# TeleMet Collector

A **Python** program (standard library only, no `pip install`) that runs continuously on the Linux server:

1. Reads your weather station every 5 minutes (configurable) through Weather Underground / Earth Network.
2. Stores the readings in a SQLite database.
3. Keeps only the last **24 hours** (sliding mode, the default; adjustable with `duration_hours`, `--hours` or `TELEMET_HOURS`); it can also wipe everything and start again once those hours are up (`mode = reset`).
4. After every reading it exports the history to a static JSON next to the **TeleMet History** app, which reads it when it opens and uses it to fill the gaps in its 12 h and 24 h evolution charts (even if the browser has been closed).

```
station ──► Weather Underground API ──► telemet_collector.py ──► SQLite (data/telemet.sqlite)
                                                │
                                                └──► history.json ──► Apache ──► TeleMet History (browser)
```

## Contents

| File | What for |
|---|---|
| `telemet_collector.py` | The program. |
| `config.example.ini` | Configuration template with every parameter commented. |
| `telemet-collector.service` | systemd unit so that it starts with the server and restarts if it fails. |
| `MANUAL.md` | Complete manual: installation, configuration, internals, data format and troubleshooting. |

## Installation on the server

Requirements: Python 3.8 or later and outbound Internet access to `api.weather.com`.

```bash
# 1. Service user and program folder
sudo useradd --system --home /opt/telemet-collector --shell /usr/sbin/nologin telemet
sudo mkdir -p /opt/telemet-collector/data      # must exist before starting the service (see ReadWritePaths in the .service)
sudo cp telemet_collector.py config.example.ini /opt/telemet-collector/
cd /opt/telemet-collector
sudo cp config.example.ini config.ini
sudo chown -R telemet:telemet /opt/telemet-collector
sudo chmod 600 config.ini

# 2. Folder where the JSON is published (next to the TeleMet History app)
sudo install -d -o telemet -g telemet -m 755 /var/www/htdocs/rafa/telemethistory/data

# 3. Edit config.ini: station_id, api_key and, if needed, json_path
sudo -u telemet nano /opt/telemet-collector/config.ini
```

### Test before putting it into service

```bash
cd /opt/telemet-collector
sudo -u telemet python3 telemet_collector.py --test      # one reading: prints it and exits (stores nothing)
sudo -u telemet python3 telemet_collector.py --once      # one reading: stores it and writes the JSON
sudo -u telemet python3 telemet_collector.py --status    # summary of what is stored
sudo -u telemet python3 telemet_collector.py --hours 48     # keep 48 h instead of the default 24 h
```

### Run it as a service

```bash
sudo cp telemet-collector.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now telemet-collector
journalctl -u telemet-collector -f                       # follow the log live
```

If you change paths or the user, adjust `User`, `WorkingDirectory`, `ExecStart` and `ReadWritePaths` in the `.service`.
After editing `config.ini`: `sudo systemctl restart telemet-collector`.

## Several stations

One collector can read **several stations, each with its own API Key**. Leave `[station]` empty and add one `[station:ID]` section per station:

```ini
[station:IELCHE12]
api_key = KEY1

[station:IALICA34]
api_key = KEY2
interval_s = 600         # optional: own pace
```

- Each station is read in its **own thread** (independent interval, retries and failures: a wrong key in one does not affect the others).
- Each one has its **own DB** (`telemet_<ID>.sqlite`) and its **own JSON** (`history_<ID>.json`, ID in upper case), in the folders of `db_path` and `json_path`. You can also use `{station_id}` in those paths or set `db_path` / `json_path` inside the station's section.
- The TeleMet History app reads `data/history_<ITS_STATION_ID>.json` first and, if it does not exist, `data/history.json`, so **a single copy of the app serves all the stations**.
- Secrets can go through the environment: `TELEMET_API_KEY_<ID>` (key of a section without `api_key`) or `TELEMET_STATIONS=ID1:KEY1,ID2:KEY2`.
- `--test`, `--once` and `--status` act on all the stations.
- A `config.ini` with a single station in `[station]` keeps working exactly as before (same DB and JSON names).

## Installing the TeleMet History app on the same server

Copy `telemetria/telemet/history/index.html` (and `apple-touch-icon.png`) to
`/var/www/htdocs/rafa/telemethistory/`. The app looks for the history at `data/history_<ID>.json` and, if it does not exist, at `data/history.json`,
**relative to its own page**, i.e. in `/var/www/htdocs/rafa/telemethistory/data/`,
which is exactly where the collector writes it with the default configuration. If you publish the app in
another folder, change `json_path` in `config.ini` (or `SERVER_HISTORY_URL` in the HTML) so that they match.

How it behaves in the app:

- When it opens (and when “Start” is pressed, and every 10 minutes while the tab is visible) it downloads the JSON and **adds** to the browser's local database the readings it is missing. It never deletes or modifies what the browser already had.
- The 12 h and 24 h charts (and the 7 day ones, which use the same database) are complete even if the app was closed.
- It is only used if the `stationId` in the JSON matches the Station ID entered in the app.
- If the file does not exist (for example, the GitHub Pages copy) the app works as always, with no errors.
- If the latest server reading is more than 15 minutes old, the app warns that the collector may be stopped.

The API Key does **not** appear in the JSON.

Optional (Apache with `mod_headers`): prevent the JSON from being cached.

```apache
<Directory /var/www/htdocs/rafa/telemethistory/data>
    <FilesMatch "\.json$">
        Header set Cache-Control "no-store"
    </FilesMatch>
</Directory>
```

## Main parameters (`config.ini`)

| Section | Parameter | Default | What it does |
|---|---|---|---|
| `station` | `station_id`, `api_key` | — | Your station and key. Also via the environment variables `TELEMET_STATION_ID` / `TELEMET_API_KEY`. |
| `station:ID` | `api_key`, `interval_s`, `db_path`, `json_path` | — | One section per station to use several (see “Several stations”). |
| `reading` | `interval_s` | 300 | Seconds between readings (minimum 5). |
| `reading` | `timeout_s` | 15 | Maximum time of each request. |
| `reading` | `backoff_base_s`, `backoff_max_s` | 2, 300 | Retries after a failure: 2, 4, 8… s up to the cap. |
| `cycle` | `duration_hours` | 24 | Hours of history that are kept (24 h serve the 12 h and the 24 h charts). Also via `--hours H` or the `TELEMET_HOURS` variable, which take precedence over the `.ini`. |
| `cycle` | `mode` | `sliding` | `sliding`: only readings older than `duration_hours` are discarded, so the last `duration_hours` are always complete. `reset`: when the cycle is up, everything is deleted and it starts from scratch. |
| `storage` | `db_path` | `./data/telemet.sqlite` | SQLite database. |
| `output` | `json_path` | `/var/www/htdocs/rafa/telemethistory/data/history.json` | JSON read by the app. |
| `output` | `decimals` | 2 | Decimals of the exported JSON. |
| `log` | `level`, `file` | `INFO`, empty | Log level and optional file with rotation. |

## Things to keep in mind

- **`sliding` mode (default):** the server always keeps the last `duration_hours` in full. With `mode = reset`, when those hours are up the history is left empty and fills again from scratch, so right afterwards a browser with no data of its own would see an almost empty chart.
- **The cycle survives restarts:** in `reset` mode, the start instant is stored in the database, so restarting the service or the server does not restart the cycle.
- **API call limit:** with `interval_s = 300` the collector makes 288 calls a day (with 60 it would be 1,440). If visitors of the app use the same key, they add their own. Check your key's limit before lowering the interval.
- **Repeated observations:** if the station has published nothing new, the API returns the same observation and the collector does not store it twice.
- **Changing station:** if you change `station_id`, the collector detects that the database belongs to another station and deletes it (with several stations, each DB keeps its own).
- **Key (401/403) or station (404) errors:** they are logged and the service keeps retrying every `backoff_max_s` seconds, in case it is a passing failure.
- The `config.ini` file contains your API Key: it is in `.gitignore` and must not be uploaded to GitHub.

## Troubleshooting

| Symptom | What to look at |
|---|---|
| `Could not write ...history.json` | The `json_path` folder does not exist or is not writable by the `telemet` user (and check `ReadWritePaths` in the `.service`). |
| The app does not show the “Server history” line | Open `https://your-server/.../data/history.json` in the browser: if it gives 404, the path does not match the app's. |
| “The server history belongs to another station” | The app's Station ID does not match the collector's (compared case-insensitively). |
| `HTTP 401` in the log | Wrong or expired API Key. |
