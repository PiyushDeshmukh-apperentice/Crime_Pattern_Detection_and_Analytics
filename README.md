# Crime Pattern Detection & Analytics (DAA_PBL)

A small toolkit and demo for detecting and analyzing crime / FIR (First Information Report) patterns.
It includes tools to generate synthetic FIR data, perform fast substring searches using the KMP algorithm,
format unstructured descriptions (example integration with Gemma API), and a Streamlit dashboard for visualization.

This repository is intended as a research/demo playground and not for production use with real sensitive data.

## Highlights

- Fast pattern matching (KMP) to filter FIR records by keyword/phrase.
- Synthetic dataset generator to create realistic-looking FIR records for testing and demos.
- Example integration with an external text-formatting API (Gemma) to convert unstructured descriptions to a structured form.
- Streamlit-based dashboard (`app.py`) to explore filtered records with maps, charts, KPIs and word clouds.

## Requirements

- Python 3.8 or newer
- Recommended: create and use a virtual environment
- System packages (on Debian/Ubuntu) if you plan to use SQLite or compile extensions:

```bash
sudo apt update
sudo apt install -y sqlite3 libsqlite3-dev
```

- Install Python dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Note: `requirements.txt` in this repo contains the main Python packages used by the project (pandas, streamlit, plotly, wordcloud, etc.).
If you run into installation errors, check for missing system libraries (for example for `wordcloud` or `pillow`).

## Key files

- `KMP.py` — Command-line script implementing KMP-based substring search and `filter_csv_by_pattern()`; reads a CSV and writes `filtered_fir.csv`.
- `kmp.py` — Small examples / alternate KMP implementations used during development.
- `generate_data.py` — Generates a synthetic FIR dataset (`synthetic_fir.csv`) and an SQLite DB for testing.
- `Formatting.py` — Example script showing how to call the Gemma API (requires `GEMMA_API_KEY` in a `.env` file) to structure FIR text.
- `app.py` — Streamlit dashboard that uses the filtered CSV to show KPIs, maps, charts and word clouds.
- `synthetic_fir.csv`, `synthetic_fir1.csv` — Example synthetic datasets included in the repo.
- `filtered_fir.csv` — Output file produced by `KMP.py` (created after running pattern filtering).
- `requirements.txt` — Python dependencies used by the project.

## Quickstart / Usage

1) Generate synthetic data (optional)

```bash
python3 generate_data.py
# The script prompts for number of records. It writes `synthetic_fir.csv` and a small SQLite DB.
```

2) Run KMP pattern matching (command-line)

```bash
python3 KMP.py
# Enter a search pattern when prompted (case-insensitive). The script will write `filtered_fir.csv`.
```

Programmatic usage (from Python):

```py
from KMP import filter_csv_by_pattern
filter_csv_by_pattern('synthetic_fir1.csv', 'filtered_fir.csv', 'burglary')
```

3) Run the Streamlit dashboard

```bash
streamlit run app.py
```

The dashboard allows you to run KMP filtering from the UI, or load an existing `filtered_fir.csv` for exploration.

4) Text formatting with Gemma API (optional)

1. Create a `.env` file in the repo root with your API key:

```
GEMMA_API_KEY=your_api_key_here
```

2. Run the formatting script (it reads `synthetic_fir.csv` by default and writes `output_gemma.csv`):

```bash
python3 Formatting.py
```

Notes:
- The Gemma API example is illustrative. You will incur network calls and must follow the API provider's terms and rate limits.
- Keep API keys out of version control (use `.env`, environment variables, or secret management).

## Examples

- Search for "robbery": run `python3 KMP.py` and type `robbery` when prompted. Check `filtered_fir.csv` for results.
- Generate 500 test records: `python3 generate_data.py` -> when prompted, enter `500`.
- Launch the dashboard and use the sidebar to filter divisions/stations and date ranges.

## Troubleshooting

- If `pip install -r requirements.txt` fails, inspect the error for missing system libraries and install the corresponding dev packages (for example `libjpeg-dev`, `build-essential`, `python3-dev`).
- If the Streamlit app errors with missing columns, run KMP first to create `filtered_fir.csv` or open one of the provided synthetic CSV files.
- If `Formatting.py` fails due to missing `GEMMA_API_KEY`, create a `.env` file or export the env var: `export GEMMA_API_KEY=...`.

## Contributing

Contributions, bug reports and improvements are welcome. Please open an issue or submit a pull request with a short description of the change.

If you add new dependencies, update `requirements.txt` and include brief instructions for any system-level packages needed.

## License

This project is provided under the MIT License. See the `LICENSE` file for details (or add one if needed).

## Contact

Maintainer: Repository owner

For questions about usage or to report issues, please open an issue on the repository.
