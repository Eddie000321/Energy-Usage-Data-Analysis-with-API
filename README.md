# Energy Usage Data Analysis with Seoul Open API

This project automates the collection, transformation, and visualization of Seoul Eco-Mileage energy usage statistics for the 개인 (household) category from January 2015 through December 2024. The annual line chart includes the student ID suffix `2212` in its title as required by the assignment brief.

![Annual Total Energy Usage](reports/figures/annual_total_energy_2212.png)
<sub>Annual electricity+gas+water+district heating totals with student ID suffix `2212` in the title.</sub>

![Seasonal Gas Usage](reports/figures/seasonal_gas_usage.png)
<sub>Average household gas consumption by season with value labels.</sub>

## Project Layout
- `src/fetch_energy_data.py` — calls the Open API for each month and stores the raw JSON
- `src/preprocess.py` — converts JSON responses into a pandas DataFrame and prepares analysis-ready columns
- `src/visualize.py` — produces the annual total usage line chart and the seasonal gas usage bar chart
- `data/raw/` — raw API responses (JSON)
- `data/processed/` — processed datasets (CSV)
- `reports/figures/` — generated charts (PNG)
- `reports/analysis.md` — template for the 200-character analytical summary
- `docs/engineering_case_study.md` — design decisions, verification evidence, limits, and lessons learned
- `requirements.txt` — Python dependencies

## Setup
1. Install Python 3.9 or later.
2. (Optional) create and activate a virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set your Seoul Open API key as an environment variable:
   ```bash
   export SEOUL_OPEN_API_KEY="your_api_key_here"
   ```
   The application reads the process environment directly; it does not automatically load `.env` files. If you keep a local `.env` as a reference, export its value in your shell and never commit it.

## Usage
1. **Collect data**
   ```bash
   python src/fetch_energy_data.py
   ```
   Saves one JSON file per month under `data/raw/`.

2. **Preprocess data**
   ```bash
   python src/preprocess.py
   ```
   Prints the assignment-specific outputs for Problems 2-1 and 2-2 and writes `data/processed/energy_usage_personal.csv`.

3. **Generate charts**
   ```bash
   python src/visualize.py
   ```
   Exports:
   - `reports/figures/annual_total_energy_2212.png`
   - `reports/figures/seasonal_gas_usage.png`

4. **Write the analysis**
   Update `reports/analysis.md` with a sub-200-character interpretation of the trends.

> **Shortcut:** 환경 설정이 끝났다면 전체 파이프라인은
> `python src/run_pipeline.py`

## Verification

The network-free suite checks response validation, category filtering, deterministic snapshot writes, idempotent CSV generation, ordered orchestration, and fail-closed behavior without using a live API key:

```bash
python -m unittest discover -s tests -v
```

See the [engineering case study](docs/engineering_case_study.md) for the problem, design decision, verification evidence, known limits, and lessons learned. Private API-registration screenshots and raw credentials are intentionally excluded from the public repository.
