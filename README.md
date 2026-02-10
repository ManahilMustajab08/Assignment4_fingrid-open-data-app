# Fingrid data (Python Application)

**Project name:** Fingrid data  

Open data from the **Fingrid Open Data API** is fetched and presented as a **readable table** in the terminal and/or as a **matplotlib chart**. (Course reference project stores data in a database and visualizes with Grafana; this assignment uses table + chart instead.)

**The API key and other information are obtained from [developer-data.fingrid.fi](https://developer-data.fingrid.fi).**

**Course context (Carbon awareness – Coding example):** COMP.SE.221 Sustainable Software Engineering. Fingrid is Finland’s transmission system operator. This project uses the [Fingrid Open Data API](https://data.fingrid.fi). For the course example (API → database → Grafana), see [github.com/miksa007/Sustainable2025_ex](https://github.com/miksa007/Sustainable2025_ex). This repo includes **`get_datasets.py`** (list all dataset metadata → `datasets_info.txt`) and **`wind.py`** (dataset metadata + optional wind time-series plot).

## What the application does

- **Fetches** time-series data from Fingrid’s public API for a **user-defined variable** (e.g. consumption, production, wind, nuclear) and **time range**.
- **Displays** the data:
  - as a **table** in the command line (default), or
  - as a **visualization** (matplotlib), optionally saving the plot to a file.
- **Handles errors** such as missing API key, network failures, and API rate limits.
- **Structure**: modular layout with a small “service” layer (API client, data service, formatters) suitable for extension (e.g. microservice-style separation later).

## API key – how to obtain and configure

**The API key and other information are obtained from [developer-data.fingrid.fi](https://developer-data.fingrid.fi).**

1. **Register** at [Fingrid Open Data](https://data.fingrid.fi) (free, valid email required).
2. Open the **Developer portal** ([developer-data.fingrid.fi](https://developer-data.fingrid.fi)) from the control panel and **subscribe** to **“Open Data starter”**.
3. In your **profile** on the developer portal, create/copy your **API key**.
4. **Configure** the key in your environment:

   ```bash
   export FINGRID_API_KEY="your-api-key-here"
   ```

   The app also accepts `API_KEY` (as in the course examples) or `FINGRID_OPENDATA_API_KEY`.

   **Security:** Do not commit the API key to version control. Use environment variables or a local `.env` (and add `.env` to `.gitignore` if you use one).

## Installation and run

### Prerequisites

- Python 3.10+ (or 3.8+; type hints use `str | None` which is 3.10+; for 3.8/3.9 you can change to `Optional[str]`).
- For **chart** output: install matplotlib (see below).

### Install dependencies

From the project root (`fingrid_open_data_app/`):

```bash
cd fingrid_open_data_app
pip install -r requirements.txt
```

- **Table only:** You can run without installing anything (stdlib only).  
- **Charts:** `pip install -r requirements.txt` (installs `matplotlib`).

### Run the application

From the `fingrid_open_data_app` directory:

```bash
# Ensure API key is set
export FINGRID_API_KEY="your-key"

# Default: consumption, last 2 days, table output
python main.py

# Custom variable and time range, table only
python main.py --variable wind --start 2024-01-01 --end 2024-01-03

# Last 7 days, table + chart saved to file
python main.py --variable production --days 7 --chart --output production.png

# List available variables (names and dataset IDs)
python main.py --list-variables
```

**Options (summary):**

| Option | Short | Description |
|--------|--------|-------------|
| `--variable` | `-v` | Variable name or dataset ID (default: `consumption`) |
| `--start` | | Start time (e.g. `2024-01-01` or `2024-01-01T00:00`) |
| `--end` | | End time (default: now) |
| `--days` | `-d` | Number of days of data if start/end not set (default: 2) |
| `--table` | `-t` | Print table (default: on unless `--chart-only`) |
| `--chart` | `-c` | Generate matplotlib chart |
| `--chart-only` | | Only chart, no table |
| `--output` | `-o` | Save chart to file (implies `--chart`) |
| `--list-variables` | | List variables and exit |
| `--max-rows` | | Max rows in table before truncation (default: 50) |

## Example run and expected output

### 1. List variables

```bash
python main.py --list-variables
```

**Expected (excerpt):**

```
Available variables (use name or ID):

  chp: dataset ID 201
  consumption: dataset ID 193
  district_heating: dataset ID 371
  hydro: dataset ID 191
  nuclear: dataset ID 188
  production: dataset ID 192
  wind: dataset ID 181
  ...
```

### 2. Table: consumption, last 2 days

```bash
export FINGRID_API_KEY="your-key"
python main.py
```

**Expected (conceptually):**

```
--- Consumption ---

  Start time (UTC)        End time (UTC)          Value
  --------------------------------  --------------------------------  ------------
  2024-02-08 00:00:00     2024-02-08 01:00:00        8923.00
  2024-02-08 01:00:00     2024-02-08 02:00:00        8512.00
  ...
  Total points: 48
```

(Exact values and length depend on the API and time range.)

### 3. Chart only, save to file

```bash
python main.py --variable wind --days 5 --chart-only --output wind.png
```

**Expected:** No table; a message like `Chart saved to: .../fingrid_open_data_app/wind.png` and the file `wind.png` in the current directory.

### 4. Error: missing API key

```bash
unset FINGRID_API_KEY
python main.py
```

**Expected:**

```
Error: No API key found. The API key and other information are obtained from https://developer-data.fingrid.fi ...

The API key and other information are obtained from developer-data.fingrid.fi
  1. Go to https://developer-data.fingrid.fi (or data.fingrid.fi → Developer portal).
  ...
```

### 5. Error: unknown variable

```bash
python main.py --variable unknown_var
```

**Expected:** Error message plus the list of available variables.

## Project structure

```
fingrid_open_data_app/
├── main.py              # CLI entry point
├── get_datasets.py      # Optional: fetch all dataset metadata from API → datasets_info.txt
├── wind.py              # Course-style: fetch dataset metadata (+ optional wind time-series plot)
├── config.py             # API base URL, API key from env
├── datasets.py           # Curated catalog (subset); full list from API in datasets_info.txt
├── api_client.py         # HTTP client, pagination, error handling
├── services/
│   ├── __init__.py
│   └── data_service.py   # Fetch + process API data
├── formatters/
│   ├── __init__.py
│   ├── table_formatter.py  # CLI table
│   └── chart_formatter.py  # Matplotlib chart
├── requirements.txt
└── README.md
```

## Fetching dataset metadata (optional)

The script **`get_datasets.py`** does what the course example does: it calls the Fingrid **dataset metadata** endpoint (`/api/datasets/{id}`) for IDs 1–250 and saves `id` and English name to **`datasets_info.txt`**. Useful to discover or update available datasets. Same idea as in [Sustainable2025_ex/get_datasets.py](https://github.com/miksa007/Sustainable2025_ex).

```bash
export FINGRID_API_KEY='your_key'
python get_datasets.py
```

Accepts `FINGRID_API_KEY`, `API_KEY`, or `FINGRID_OPENDATA_API_KEY`. Uses a 2-second delay between requests to respect the API rate limit.

The **full list** of datasets (id + name) from the API looks like the JSON you see in the course: an array of `{"id": 1, "name": "Automatic Frequency Restoration Reserve, capacity, up"}, ...`. After running `get_datasets.py`, that list is in **`datasets_info.txt`**. The app’s **`datasets.py`** uses a **curated subset** of those IDs for the main CLI; you can extend it from `datasets_info.txt` if you like.

### Wind example (course-style: `wind.py`)

**`wind.py`** mirrors the course [wind.py](https://github.com/miksa007/Sustainable2025_ex): it fetches **metadata** for one dataset from `GET /api/datasets/75` (Wind power, 15-min) and prints the JSON. Optionally, with `--data`, it also fetches **time-series** for the last 24 hours and saves a plot to `wind_plot.png`.

```bash
export FINGRID_API_KEY='your_key'
python wind.py              # metadata only (like course wind.py)
python wind.py --data       # metadata + fetch series and plot
```

## Error handling

- **Missing API key:** Clear message and instructions to obtain and set the key.
- **Network errors:** Timeouts and connection failures caught and reported.
- **Rate limit (429):** Message to wait (Fingrid: 10 requests/minute).
- **Invalid variable:** Suggests using `--list-variables` and lists options.
- **Invalid API response:** JSON and structure checks with clear error messages.

## License and data source

- **Data:** [Fingrid Open Data](https://data.fingrid.fi), typically under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Check the portal for each dataset.
- **Code:** Use and adapt as needed for your assignment/course; keep attribution.

## Documentation (learning diary / PDF)

For the assignment, you can export this README (or a shortened “User guide” section) to PDF and submit it as the documentation part of your learning diary. Include (as per course instructions):

- **Project name:** Fingrid data  
- What the application does (open data from Fingrid API fetched and displayed as table/chart)  
- **The API key and other information are obtained from developer-data.fingrid.fi** — how to obtain and configure the API key  
- How to install and run  
- At least one example run and expected output (e.g. table + error example)
