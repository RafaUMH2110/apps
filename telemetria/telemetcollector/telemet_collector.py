#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TeleMet Collector — continuous weather-station polling and a 24 h (configurable)
history kept on the Linux server.

What it does
------------
1. Every `interval_s` seconds it queries the Weather Underground
   (Earth Network) API for your personal station (the "current" endpoint).
2. It stores every reading in a local SQLite database (Python standard
   library only: nothing to install with pip).
3. With `mode = sliding` (the default) it keeps discarding readings older
   than `duration_hours` (24 by default), so it always holds the last 24 h
   (enough for the app's 12 h and 24 h charts). The hours can be changed in
   config.ini, with the --hours option or with the TELEMET_HOURS environment
   variable.
   With `mode = reset`, once `duration_hours` have elapsed since the start
   of the cycle it DELETES all the data and starts a new cycle.
4. After every reading it exports the history to a static JSON file inside
   the folder served by Apache, next to the TeleMet History app. The app
   reads it when it opens and uses it to fill the gaps in its 12 and 24 hour
   evolution charts.

All the important parameters are in `config.ini` (see
`config.example.ini`) and the two secrets can be given through
environment variables: TELEMET_STATION_ID and TELEMET_API_KEY.

Usage
-----
    python3 telemet_collector.py                 # continuous service
    python3 telemet_collector.py -c /path/config.ini
    python3 telemet_collector.py --hours 48       # keep 48 h instead of the default 24 h
    python3 telemet_collector.py --once          # one reading: store it, export and exit
    python3 telemet_collector.py --test          # one reading: print it and exit (stores nothing)
    python3 telemet_collector.py --status        # summary of what is stored in the DB
"""

import argparse
import configparser
import json
import logging
import logging.handlers
import math
import os
import signal
import sqlite3
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

VERSION = "1.0"
JSON_FORMAT = 1  # version of the exported JSON format (the app checks it)

log = logging.getLogger("telemet_collector")

# ----------------------------------------------------------------------
# DEFAULT VALUES (all of them can be changed in config.ini)
# ----------------------------------------------------------------------
DEFAULTS = {
    "station": {
        "station_id": "",
        "api_key": "",
    },
    "reading": {
        "base_url": "https://api.weather.com/v2/pws/observations/current",
        "interval_s": "300",       # seconds between queries
        "timeout_s": "15",         # time limit of each request
        "backoff_base_s": "2",     # retry after a failure: base * 2^n ...
        "backoff_max_s": "300",    # ... capped at this value
    },
    "cycle": {
        "duration_hours": "24",   # hours of history (24 = enough for the 12 h and 24 h charts)
        # sliding -> only readings older than `duration_hours` are deleted
        # reset   -> when the hours are up, ALL data is deleted and it starts from scratch
        "mode": "sliding",
    },
    "storage": {
        "db_path": "./data/telemet.sqlite",
    },
    "output": {
        "json_path": "/var/www/htdocs/rafa/telemethistory/data/history.json",
        "decimals": "2",
    },
    "log": {
        "level": "INFO",
        "file": "",                # empty = standard output only (journald under systemd)
    },
}


# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------
class Config:
    def __init__(self, ini_path, hours=None):
        cp = configparser.ConfigParser(interpolation=None)
        cp.read_dict(DEFAULTS)
        if ini_path:
            if not os.path.isfile(ini_path):
                raise SystemExit("Configuration file not found: %s" % ini_path)
            cp.read(ini_path, encoding="utf-8")
        self.base_dir = os.path.dirname(os.path.abspath(ini_path)) if ini_path else os.getcwd()

        # The secrets may come from the environment (they take priority over the .ini).
        self.station_id = (os.environ.get("TELEMET_STATION_ID") or cp.get("station", "station_id")).strip()
        self.api_key = (os.environ.get("TELEMET_API_KEY") or cp.get("station", "api_key")).strip()

        self.base_url = cp.get("reading", "base_url").strip()
        self.interval_s = max(5.0, cp.getfloat("reading", "interval_s"))
        self.timeout_s = max(1.0, cp.getfloat("reading", "timeout_s"))
        self.backoff_base_s = max(0.5, cp.getfloat("reading", "backoff_base_s"))
        self.backoff_max_s = max(self.backoff_base_s, cp.getfloat("reading", "backoff_max_s"))

        # Hours of history: --hours (command line) > TELEMET_HOURS (environment) > config.ini.
        hours_value = hours if hours is not None else (os.environ.get("TELEMET_HOURS") or "").strip() or None
        try:
            self.duration_h = float(hours_value) if hours_value is not None else cp.getfloat("cycle", "duration_hours")
        except ValueError:
            raise SystemExit("The hours of history (--hours / TELEMET_HOURS / [cycle] duration_hours) must be a number.")
        if self.duration_h <= 0:
            raise SystemExit("The hours of history (duration_hours) must be > 0")
        self.mode = cp.get("cycle", "mode").strip().lower()
        if self.mode not in ("reset", "sliding"):
            raise SystemExit("[cycle] mode must be 'reset' or 'sliding'")

        self.db_path = self._path(cp.get("storage", "db_path"))
        self.json_path = self._path(cp.get("output", "json_path"))
        self.decimals = max(0, cp.getint("output", "decimals"))

        self.log_level = cp.get("log", "level").strip().upper()
        self.log_file = cp.get("log", "file").strip()
        if self.log_file:
            self.log_file = self._path(self.log_file)

    def _path(self, path):
        path = os.path.expanduser(path.strip())
        return path if os.path.isabs(path) else os.path.normpath(os.path.join(self.base_dir, path))

    @property
    def duration_ms(self):
        return int(self.duration_h * 3600 * 1000)


# ----------------------------------------------------------------------
# VALUE EXTRACTION (same logic as the app's extractValues(), so that what
# is stored here is identical to what the browser stores)
# ----------------------------------------------------------------------
def _first_defined(*vals):
    for v in vals:
        if v is not None:
            return v
    return None


def _finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def heat_index_c(t_c, rh):
    t_f = t_c * 9 / 5 + 32
    if t_f < 80 or rh is None or not _finite(rh):
        return t_c
    hi = (-42.379 + 2.04901523 * t_f + 10.14333127 * rh - 0.22475541 * t_f * rh
          - 0.00683783 * t_f * t_f - 0.05481717 * rh * rh + 0.00122874 * t_f * t_f * rh
          + 0.00085282 * t_f * rh * rh - 0.00000199 * t_f * t_f * rh * rh)
    if rh < 13 and 80 <= t_f <= 112:
        hi -= ((13 - rh) / 4) * math.sqrt((17 - abs(t_f - 95)) / 17)
    elif rh > 85 and 80 <= t_f <= 87:
        hi += ((rh - 85) / 10) * ((87 - t_f) / 5)
    return max((hi - 32) * 5 / 9, t_c)


def wind_chill_c(t_c, wind_kmh):
    if wind_kmh is None or not _finite(wind_kmh) or wind_kmh <= 4.8:
        return t_c
    v = wind_kmh ** 0.16
    wc = 13.12 + 0.6215 * t_c - 11.37 * v + 0.3965 * t_c * v
    return min(wc, t_c)


def feels_like_c(t_c, rh, wind_kmh):
    if t_c is None or not _finite(t_c):
        return None
    if t_c >= 26.7:
        return heat_index_c(t_c, rh)
    if t_c <= 10:
        return wind_chill_c(t_c, wind_kmh)
    return t_c


def extract_values(obs):
    metric = obs.get("metric") or {}
    temp_c = _first_defined(metric.get("temp"), metric.get("tempAvg"))
    hum = _first_defined(obs.get("humidity"), obs.get("humidityAvg"))
    wind = _first_defined(metric.get("windSpeed"), metric.get("windspeedAvg"))
    p_max, p_min = metric.get("pressureMax"), metric.get("pressureMin")
    if _finite(p_max) and _finite(p_min):
        hist_pressure = (p_max + p_min) / 2
    else:
        hist_pressure = _first_defined(p_max, p_min)
    return {
        "temp_c": temp_c,
        "heat_index_c": feels_like_c(temp_c, hum, wind),
        "dewpoint_c": _first_defined(obs.get("dewpoint"), metric.get("dewpt"),
                                     metric.get("dewptAvg"), metric.get("dewpoint")),
        "humidity_pct": hum,
        "pressure_hpa": _first_defined(metric.get("pressure"), hist_pressure),
        "wind_kmh": wind,
        "gust_kmh": _first_defined(metric.get("windGust"), metric.get("windgustAvg")),
        "wind_dir_deg": _first_defined(obs.get("winddir"), obs.get("windDir"), obs.get("winddirAvg")),
        "rainrate_mmh": metric.get("precipRate"),
        "rain_total_mm": metric.get("precipTotal"),
        "solarradiation_wm2": _first_defined(obs.get("solarRadiation"), obs.get("solarradiation"),
                                             obs.get("solarRadiationHigh")),
        "uv_index": _first_defined(obs.get("uv"), obs.get("uvHigh")),
        "quality_code": _first_defined(obs.get("qcStatus"), obs.get("qualityControlFlag"), "N/A"),
    }


# ----------------------------------------------------------------------
# SQLITE STORE
# ----------------------------------------------------------------------
class Store:
    def __init__(self, path):
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        self.db = sqlite3.connect(path, timeout=30)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("CREATE TABLE IF NOT EXISTS readings ("
                        "epoch_ms INTEGER PRIMARY KEY, vals TEXT NOT NULL)")
        self.db.execute("CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT NOT NULL)")
        self.db.commit()

    def meta(self, key, default=None):
        row = self.db.execute("SELECT v FROM meta WHERE k=?", (key,)).fetchone()
        return row[0] if row else default

    def set_meta(self, key, value):
        self.db.execute("INSERT INTO meta(k, v) VALUES(?, ?) "
                        "ON CONFLICT(k) DO UPDATE SET v=excluded.v", (key, str(value)))
        self.db.commit()

    def add(self, epoch_ms, vals):
        """True if the reading was new (the station sometimes repeats the same observation)."""
        cur = self.db.execute("INSERT OR IGNORE INTO readings(epoch_ms, vals) VALUES(?, ?)",
                              (int(epoch_ms), json.dumps(vals, separators=(",", ":"))))
        self.db.commit()
        return cur.rowcount > 0

    def delete_all(self):
        self.db.execute("DELETE FROM readings")
        self.db.commit()
        self.db.execute("VACUUM")

    def delete_older_than(self, limit_ms):
        cur = self.db.execute("DELETE FROM readings WHERE epoch_ms < ?", (int(limit_ms),))
        self.db.commit()
        return cur.rowcount

    def all(self):
        return [(e, json.loads(v)) for e, v in
                self.db.execute("SELECT epoch_ms, vals FROM readings ORDER BY epoch_ms")]

    def summary(self):
        n, mn, mx = self.db.execute("SELECT COUNT(*), MIN(epoch_ms), MAX(epoch_ms) FROM readings").fetchone()
        return n, mn, mx

    def close(self):
        self.db.close()


# ----------------------------------------------------------------------
# JSON EXPORT (what the app reads)
# ----------------------------------------------------------------------
def _round_values(vals, decimals):
    out = {}
    for k, v in vals.items():
        out[k] = round(v, decimals) if isinstance(v, float) else v
    return out


def export_json(cfg, store, cycle_start_ms):
    readings = [{"t": e, "v": _round_values(v, cfg.decimals)} for e, v in store.all()]
    doc = {
        "format": JSON_FORMAT,
        "stationId": cfg.station_id,
        "generatedMs": int(time.time() * 1000),
        "mode": cfg.mode,
        "durationMs": cfg.duration_ms,
        "cycleStartMs": cycle_start_ms,
        "cycleEndMs": cycle_start_ms + cfg.duration_ms if cfg.mode == "reset" else None,
        "intervalS": cfg.interval_s,
        "readings": readings,
    }
    folder = os.path.dirname(cfg.json_path) or "."
    os.makedirs(folder, exist_ok=True)
    # Atomic write: Apache never serves a half-written JSON.
    fd, tmp = tempfile.mkstemp(prefix=".history-", suffix=".tmp", dir=folder)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(doc, f, separators=(",", ":"), ensure_ascii=False)
        os.chmod(tmp, 0o644)  # readable by the Apache user (www-data / apache)
        os.replace(tmp, cfg.json_path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ----------------------------------------------------------------------
# API REQUEST
# ----------------------------------------------------------------------
class FatalError(Exception):
    """An error that quick retries will not fix (invalid key, non-existent station)."""


class TransientError(Exception):
    pass


def build_url(cfg):
    params = {"stationId": cfg.station_id, "format": "json", "numericPrecision": "decimal",
              "units": "m", "apiKey": cfg.api_key}
    return cfg.base_url + "?" + urllib.parse.urlencode(params)


def fetch(cfg):
    """Return (epoch_ms, vals) of the latest observation, or None if the API returns none."""
    req = urllib.request.Request(build_url(cfg), headers={"User-Agent": "telemet-collector/" + VERSION})
    try:
        with urllib.request.urlopen(req, timeout=cfg.timeout_s) as resp:
            body = resp.read()
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            raise FatalError("HTTP %d: invalid API Key or no permission" % e.code)
        if e.code == 404:
            raise FatalError("HTTP 404: Station ID not found or endpoint obsolete")
        raise TransientError("HTTP %d" % e.code)
    except (urllib.error.URLError, OSError) as e:
        raise TransientError("network failure: %s" % getattr(e, "reason", e))
    if not body:  # the API answers 204 with no body when there is no data
        return None
    try:
        data = json.loads(body.decode("utf-8"))
    except ValueError:
        raise TransientError("response is not valid JSON")
    obs_list = data.get("observations") or []
    if not obs_list:
        return None
    obs = obs_list[0]
    epoch = obs.get("epoch")
    epoch_ms = int(epoch * 1000) if epoch else int(time.time() * 1000)
    return epoch_ms, extract_values(obs)


# ----------------------------------------------------------------------
# MAIN LOOP
# ----------------------------------------------------------------------
class Collector:
    def __init__(self, cfg):
        self.cfg = cfg
        self.store = Store(cfg.db_path)
        self.stop = threading.Event()
        self.consecutive_failures = 0
        self.cycle_start_ms = self._load_cycle()

    # -- the `duration_hours` cycle (24 h by default) ------------------
    def _load_cycle(self):
        now = int(time.time() * 1000)
        db_station = self.store.meta("station_id")
        if db_station is not None and db_station != self.cfg.station_id:
            log.warning("The DB belonged to station %s and station %s is now in use: old data is deleted.",
                        db_station, self.cfg.station_id)
            self.store.delete_all()
            self.store.set_meta("cycle_start_ms", now)
        self.store.set_meta("station_id", self.cfg.station_id)
        start = self.store.meta("cycle_start_ms")
        if start is None:
            start = now
            self.store.set_meta("cycle_start_ms", start)
        return int(start)

    def apply_cycle(self):
        """Apply the `duration_hours` rule. Return True if the DB content has changed."""
        now = int(time.time() * 1000)
        if self.cfg.mode == "reset":
            if now - self.cycle_start_ms >= self.cfg.duration_ms:
                n = self.store.summary()[0]
                self.store.delete_all()
                self.cycle_start_ms = now
                self.store.set_meta("cycle_start_ms", now)
                log.info("%.4g h cycle completed: %d readings deleted and a new cycle begins.",
                         self.cfg.duration_h, n)
                return True
        else:
            deleted = self.store.delete_older_than(now - self.cfg.duration_ms)
            if deleted:
                log.debug("Discarded %d readings older than %.4g h.", deleted, self.cfg.duration_h)
                return True
        return False

    # -- one round -------------------------------------------------------
    def one_round(self):
        """Make one query. Return the seconds to wait until the next one."""
        changed = self.apply_cycle()
        try:
            res = fetch(self.cfg)
        except FatalError as e:
            self.consecutive_failures += 1
            log.error("%s. Will retry every %.0f s; fix config.ini if it is not a passing failure.",
                      e, self.cfg.backoff_max_s)
            self._export_if(changed)
            return self.cfg.backoff_max_s
        except TransientError as e:
            self.consecutive_failures += 1
            wait = min(self.cfg.backoff_base_s * (2 ** (self.consecutive_failures - 1)), self.cfg.backoff_max_s)
            log.warning("Reading failed (%s); retry #%d in %.0f s.", e, self.consecutive_failures, wait)
            self._export_if(changed)
            return wait

        self.consecutive_failures = 0
        if res is None:
            log.info("The API returned no new observations.")
            self._export_if(changed)
            return self.cfg.interval_s
        epoch_ms, vals = res
        is_new = self.store.add(epoch_ms, vals)
        t = vals.get("temp_c")
        log.info("%s  T=%s °C  RH=%s %%  wind=%s km/h  %s",
                 time.strftime("%H:%M:%S", time.localtime(epoch_ms / 1000)),
                 t, vals.get("humidity_pct"), vals.get("wind_kmh"),
                 "stored" if is_new else "(repeated observation, not stored)")
        self._export_if(changed or is_new)
        return self.cfg.interval_s

    def _export_if(self, needed):
        if not needed:
            return
        try:
            export_json(self.cfg, self.store, self.cycle_start_ms)
        except OSError as e:
            log.error("Could not write %s: %s (does the folder exist and does the service user have permissions?)",
                      self.cfg.json_path, e)

    def run(self):
        log.info("TeleMet Collector %s · station %s · every %.0f s · cycle %.4g h (%s)",
                 VERSION, self.cfg.station_id, self.cfg.interval_s, self.cfg.duration_h, self.cfg.mode)
        log.info("DB: %s · JSON: %s", self.cfg.db_path, self.cfg.json_path)
        # Initial JSON: this way the app finds the file even if the first reading is slow.
        self._export_if(True)
        while not self.stop.is_set():
            started = time.monotonic()
            try:
                wait = self.one_round()
            except Exception:  # an unexpected failure must not bring the service down
                log.exception("Unexpected error in the reading round")
                self.consecutive_failures += 1
                wait = min(self.cfg.backoff_base_s * (2 ** min(self.consecutive_failures, 10)), self.cfg.backoff_max_s)
            # Fixed-rate interval: the time the request took is subtracted.
            remaining = max(1.0, wait - (time.monotonic() - started))
            self.stop.wait(remaining)
        self.store.close()
        log.info("Stopped.")


# ----------------------------------------------------------------------
# STARTUP
# ----------------------------------------------------------------------
def setup_logging(cfg):
    log.setLevel(getattr(logging, cfg.log_level, logging.INFO))
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")
    handlers = [logging.StreamHandler(sys.stdout)]
    if cfg.log_file:
        os.makedirs(os.path.dirname(cfg.log_file) or ".", exist_ok=True)
        handlers.append(logging.handlers.RotatingFileHandler(cfg.log_file, maxBytes=1_000_000, backupCount=3,
                                                             encoding="utf-8"))
    for h in handlers:
        h.setFormatter(fmt)
        log.addHandler(h)


def main(argv=None):
    ap = argparse.ArgumentParser(description="TeleMet Collector: weather-station history (24 h by default) on the server.")
    ap.add_argument("-c", "--config", default=None,
                    help="path of config.ini (by default, config.ini next to the script if it exists)")
    ap.add_argument("--hours", type=float, default=None, metavar="H",
                    help="hours of history to keep (overrides duration_hours in config.ini and TELEMET_HOURS; default 24)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--once", action="store_true", help="make one reading, store it, export the JSON and exit")
    g.add_argument("--test", action="store_true", help="make one reading and print it, storing nothing")
    g.add_argument("--status", action="store_true", help="show a summary of what is stored in the DB")
    args = ap.parse_args(argv)

    ini_path = args.config
    if ini_path is None:
        candidate = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
        ini_path = candidate if os.path.isfile(candidate) else None
    cfg = Config(ini_path, args.hours)
    setup_logging(cfg)

    if args.status:
        s = Store(cfg.db_path)
        n, mn, mx = s.summary()
        f = lambda ms: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ms / 1000)) if ms else "—"
        print("DB:            %s" % cfg.db_path)
        print("Station:       %s" % s.meta("station_id", "—"))
        print("Readings:      %d  (from %s to %s)" % (n, f(mn), f(mx)))
        start = s.meta("cycle_start_ms")
        print("Cycle since:   %s" % (f(int(start)) if start else "—"))
        s.close()
        return 0

    if not cfg.station_id or not cfg.api_key:
        raise SystemExit("station_id and/or api_key missing (in config.ini or in TELEMET_STATION_ID / TELEMET_API_KEY).")

    if args.test:
        try:
            res = fetch(cfg)
        except (FatalError, TransientError) as e:
            print("ERROR: %s" % e)
            return 1
        if res is None:
            print("The API returned no observations.")
            return 1
        epoch_ms, vals = res
        print("Observation from %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(epoch_ms / 1000)))
        print(json.dumps(vals, indent=2, ensure_ascii=False))
        return 0

    col = Collector(cfg)
    if args.once:
        col.one_round()
        col._export_if(True)
        col.store.close()
        return 0

    def _stop(signum, _frame):
        log.info("Signal %d received: stopping…", signum)
        col.stop.set()
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    col.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
