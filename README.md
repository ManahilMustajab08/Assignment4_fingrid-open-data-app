# Fingrid data

**Project name:** Fingrid data

This app pulls electricity data from the Fingrid Open Data API and shows it either as a table in the terminal or as a chart (matplotlib). The course reference project pushes data into a database and uses Grafana; here we stick to table + chart.

You need an API key to talk to the API. The API key and other information are obtained from [developer-data.fingrid.fi](https://developer-data.fingrid.fi).

Course: COMP.SE.221 Sustainable Software Engineering (Carbon awareness – coding example). Same API as in [Sustainable2025_ex](https://github.com/miksa007/Sustainable2025_ex). This repo also has `get_datasets.py` (dumps all dataset metadata to a file) and `wind.py` (dataset metadata + optional wind time-series plot), in the same spirit as the course examples.

---

## What it does

You pick a variable (e.g. consumption, wind, nuclear) and a time range. The app fetches that series from Fingrid and either prints a table (default) or draws a chart. It handles missing API key, network issues, and rate limits. The code is split into an API client, a small service layer, and formatters (table/chart), so you can extend or swap parts without touching everything.

---

## API key

The API key and other information are obtained from [developer-data.fingrid.fi](https://developer-data.fingrid.fi).

1. Register at [data.fingrid.fi](https://data.fingrid.fi) (free, email only).
2. In the control panel, open the Developer portal ([developer-data.fingrid.fi](https://developer-data.fingrid.fi)), subscribe to “Open Data starter”.
3. In your profile, copy your API key.
4. Set it in your environment:

   ```bash
   export FINGRID_API_KEY="your-api-key-here"
   ```

   You can also use `API_KEY` (like in the course scripts) or `FINGRID_OPENDATA_API_KEY`. Don’t put the key in the repo — use env vars or a local `.env` and keep `.env` in `.gitignore`.

---

## Install and run

Python 3.8+ is enough. For charts you’ll need matplotlib; for table-only you don’t need any extra packages.

```bash
cd fingrid_open_data_app
pip install -r requirements.txt
```

Then:

```bash
export FINGRID_API_KEY="your-key"
python main.py
```

That prints consumption for the last 2 days as a table. Some other examples:

```bash
python main.py --variable wind --start 2024-01-01 --end 2024-01-03
python main.py --variable production --days 7 --chart --output production.png
python main.py --list-variables
```

**Options:**

| Option | Short | Meaning |
|--------|------|--------|
| `--variable` | `-v` | Which series (default: consumption) |
| `--start` / `--end` | | Time range (e.g. `2024-01-01`, `2024-01-01T00:00`) |
| `--days` | `-d` | Last N days if you don’t set start/end (default: 2) |
| `--table` | `-t` | Print table (default on) |
| `--chart` | `-c` | Draw chart |
| `--chart-only` | | Only chart, no table |
| `--output` | `-o` | Save chart to file |
| `--list-variables` | | Print variable names and IDs, then exit |
| `--max-rows` | | Cap table rows (default 50) |

---

## Example run and output

**List variables:**

```bash
python main.py --list-variables
```

You get something like:

```
Available variables (use name or ID):

  chp: dataset ID 201
  consumption: dataset ID 193
  hydro: dataset ID 191
  nuclear: dataset ID 188
  production: dataset ID 192
  wind: dataset ID 181
  ...
```

**Table (default):**

```bash
export FINGRID_API_KEY="your-key"
python main.py
```

Example output:

```
--- Consumption ---

  Start time (UTC)        End time (UTC)          Value
  --------------------------------  --------------------------------  ------------
  2024-02-08 00:00:00     2024-02-08 01:00:00        8923.00
  2024-02-08 01:00:00     2024-02-08 02:00:00        8512.00
  ...
  Total points: 48
```

Numbers and length depend on the API and the range you ask for.

**Chart to file:**

```bash
python main.py --variable wind --days 5 --chart-only --output wind.png
```

You get a message like `Chart saved to: .../wind.png` and the file in the current directory.

**Missing API key:**

If you run without setting the key, the app prints an error and tells you to get the key from developer-data.fingrid.fi and set `FINGRID_API_KEY`.

**Unknown variable:**

If you pass a variable name that doesn’t exist, you get an error and the list of valid variables.

---

## Project layout

```
fingrid_open_data_app/
├── main.py                 # entry point
├── get_datasets.py         # optional: fetch all dataset metadata → datasets_info.txt
├── wind.py                 # course-style: dataset metadata + optional wind plot
├── config.py               # API base URL, API key from env
├── datasets.py             # variable name ↔ dataset ID (curated subset)
├── api_client.py           # HTTP, pagination, errors
├── services/
│   └── data_service.py     # fetch + process
├── formatters/
│   ├── table_formatter.py
│   └── chart_formatter.py
├── requirements.txt
└── README.md
```

---

## Extra scripts

**get_datasets.py** — Hits the metadata endpoint for dataset IDs 1–250 and writes id + English name to `datasets_info.txt`. Same idea as the course [get_datasets.py](https://github.com/miksa007/Sustainable2025_ex). Run with `FINGRID_API_KEY` or `API_KEY` set; it waits 2 seconds between requests so the API doesn’t throttle you.

**wind.py** — Fetches metadata for dataset 75 (wind, 15-min) and prints the JSON, like the course wind.py. With `--data` it also fetches the last 24 hours of that series and saves a plot to `wind_plot.png`.

```bash
python wind.py
python wind.py --data
```

The main app’s variable list in `datasets.py` is a subset of what the API offers. The full list (after running `get_datasets.py`) lives in `datasets_info.txt`.

---

## Errors

- No API key → message + instructions (developer-data.fingrid.fi).
- Network / timeout → error message.
- Rate limit (429) → “wait a bit” (Fingrid allows 10 req/min).
- Unknown variable → error + list of variables.
- Bad API response → caught and reported.

---

## Data and license

Data from [Fingrid Open Data](https://data.fingrid.fi), usually CC BY 4.0 (check each dataset). Code: use and adapt, keep attribution.

---

## For the learning diary (PDF)

When you turn this in, export the README (or a short “how to use” section) to PDF. Make sure it includes:

- Project name: Fingrid data
- What the app does (fetches Fingrid open data, shows table/chart)
- That the API key and other information are obtained from developer-data.fingrid.fi, plus how to get and set the key
- How to install and run
- At least one example run and what output to expect
