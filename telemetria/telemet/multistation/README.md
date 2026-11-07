# TeleMet MultiStation

Single-file web app (`index.html`) to follow **several Weather Underground weather stations at once**. It is the English version of TeleMet Multi and is built on TeleMet History, keeping its style and charts. It is fully independent from the Spanish version: it uses its own storage (`telemetmultistation_*` keys and the `telemetmultistation_db` IndexedDB), so both can live on the same site without interfering.

## What it does
- **Stations**: add, remove, enable, name and colour each station; own API Key or a shared one. Import/export the configuration as JSON. Changes are stored with the **Save configuration** button (it confirms with a message; unsaved changes are flagged, and they are saved automatically when you press Start).
- **Collapsible cards**: every card and every section (“Hide/Show” button) can be folded; the state is remembered in the browser.
- **Independent polling** per station with its own backoff; a 401/403/404 error only stops that station. Approximate quota estimate per key.
- **Now**: one card per station, comparison table (highest/lowest highlighted and difference from a reference), extremes between stations and a map with an OpenStreetMap background (Mercator projection, scale and north arrow).
- **Detail**: 12 variables with 24 h min/max and a sparkline.
- **Charts**: 12 h, 24 h or 7 days; *Compare stations* mode (all stations overlaid) or *One station* (all its variables); chips to show or hide stations and variables; tooltip with every station.
- **7-day summary** and **single-day lookup** (gaps are filled from the API history).
- **Data and server**: persistent history per station (IndexedDB, 9 days), synchronisation with the TeleMet Collector JSON files, gap filling from the API, CSV (24 h / 7 days / all) and deletion.

## Merging history with the first reading and filling 7 days
When the app loads, when you press **Start** and when you choose the **7 d** window, the app checks the last 7 days of every station (what is stored in the browser plus the collector’s data). If it finds gaps, it asks the API for the history of each affected day and adds only what is missing, so the chart lines are continuous.
- Today and yesterday: the last-24 h window is checked and any gap longer than 15 min is filled.
- Earlier days: days with large gaps (more than 90 min) are filled.
- Cost: up to 7 requests per station (the API returns one day per request). To save quota the same day is not repeated within 20 min (today and yesterday) or 12 h (earlier days).
- Requests are spaced 2.5 s apart (the API allows about 30 per minute and key) and the chart is redrawn after each day. If the API answers 429 (too many requests) or fails, a notice under the chart says so, the day is not marked as done and it is retried in 1 minute; the reason is kept in the section 07 log.
- Fallback: if the per-day query returns nothing for a day, the API’s 7-day hourly history (`observations/hourly/7day`, one request per station) is tried only for the days that are still empty.
- The **Complete 7 days from the API** button (section 05) launches it by hand ignoring the “already queried” marks, and below it (and below the chart) a report shows what the API answered for each station and day.
- If the API has no data for a stretch, the gap stays a gap: it is never joined with an invented straight line.

## Map with OpenStreetMap background
The map in the *Now* tab draws the stations over OpenStreetMap tiles, with scale, north indicator and attribution. It can be turned off with the “Background map (OpenStreetMap)” checkbox; without it a neutral grid is shown. Tiles are loaded from `tile.openstreetmap.org`, so the browser only contacts that service while the background is on.

## Interactive map with all the stations
“view on map” (Detail) and the links under the *Now* map open a new window with an OpenStreetMap map (Leaflet) showing **all the stations** with their colour, name and temperature; the chosen station is highlighted and its popup opens. The view fits all of them, and the legend lets you centre on each one. That window loads Leaflet from unpkg.com (with an integrity check) and the tiles from tile.openstreetmap.org. Stations appear once they have reported their position (after the first poll).

## Usage
Open `index.html` (or the version published on GitHub Pages), add each station (Station ID and API Key) and press **Start**. Data and keys are stored only in the browser.

## Integration with TeleMet Collector
With the multi-station collector, each station generates `history_<ID>.json`. In *Data and server* give the folder (default `data/`; use `../history/data/` if the collector writes next to TeleMet History). The app only **adds** missing readings; it never deletes local data. If the per-station file does not exist, the app also accepts the single `history.json` when its `stationId` matches (and, for compatibility, the Spanish `historial_<ID>.json` / `historial.json` names).

If there is no file in the given folder, the app also tries `../telemethistory/data/`, `../telemethistorial/datos/`, `../history/data/` and `../historial/datos/` (the usual TeleMet History/Historial folders next to this app). In the synchronisation table, hovering over “synchronised” shows the file that was read, and over “no file” where it was looked for.
