# Energy Usage Data Analysis with Seoul Open API

This project automates the collection, transformation, and visualization of Seoul Eco-Mileage energy usage statistics for the 개인 (household) category from January 2015 through December 2024. The annual line chart includes the student ID suffix `2212` in its title as required by the assignment brief.

![Annual assignment helper sum](reports/figures/annual_total_energy_2212.png)
<sub>Annual assignment helper: the source electricity, gas, water, and district-heating values are added without unit conversion. This is a trend aid, not a normalized energy measure.</sub>

![Seasonal Gas Usage](reports/figures/seasonal_gas_usage.png)
<sub>Mean of the monthly aggregate gas values for the `개인` category, grouped by season. This is not a per-household average.</sub>

## Data Source & License

This project uses the Seoul Open Data Plaza dataset [서울시 에코마일리지 에너지사용량 통계정보(회원유형별)](https://data.seoul.go.kr/dataList/OA-15361/A/1/datasetView.do), API service `energyUseDataSummaryInfo`. The publisher and copyright holder is the Seoul Metropolitan Government (서울특별시). This project filters the official aggregate records to the `개인` member category; the tracked CSV, charts, and analysis are derived outputs. No ownership of the Seoul source data is claimed.

The official dataset page designates the source as [Korea Open Government License (공공누리) Type 1 — Source Indication](https://www.kogl.or.kr/info/licenseType1.do). Type 1 permits commercial and non-commercial reuse and modification, provided the source/copyright holder is attributed. Online reuse should preserve a link to the official dataset and must not imply sponsorship or a special relationship with the Seoul Metropolitan Government. Reusers of this repository's derived data or visuals should retain this attribution.

> Source data: Seoul Metropolitan Government, “서울시 에코마일리지 에너지사용량 통계정보(회원유형별),” Seoul Open Data Plaza, KOGL Type 1.

The KOGL notice above describes the Seoul source data's reuse terms; it is not a software license for this repository's code. This repository currently provides no separate open-source license for the code.

## Project Layout
- `src/fetch_energy_data.py` — calls the Open API for each month and stores the raw JSON
- `src/preprocess.py` — converts JSON responses into a pandas DataFrame and prepares analysis-ready columns
- `src/visualize.py` — produces the annual total usage line chart and the seasonal gas usage bar chart
- `data/raw/` — raw API responses (JSON)
- `data/processed/` — processed datasets (CSV)
- `reports/figures/` — generated charts (PNG)
- `reports/analysis.md` — verified, evidence-limited summary of the tracked 120-month dataset
- `docs/engineering_case_study.md` — design decisions, verification evidence, limits, and lessons learned
- `requirements.txt` — Python dependencies

## Setup
1. Install Python 3.11 or later. CI currently verifies Python 3.13.
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

4. **Review the analysis**
   Read the completed sub-200-character summary in `reports/analysis.md`. Its headline values are recomputed from the tracked CSV by the test suite.

> **Shortcut:** 환경 설정이 끝났다면 전체 파이프라인은
> `python src/run_pipeline.py`

## Verification

The network-free suite checks response validation, category filtering, deterministic snapshot writes, idempotent CSV generation, analytical-summary claims, source attribution, ordered orchestration, and fail-closed behavior without using a live API key. CI also runs Ruff, compilation, dependency consistency, and a dependency vulnerability audit:

```bash
python -m unittest discover -s tests -v
```

See the [engineering case study](docs/engineering_case_study.md) for the problem, design decision, verification evidence, known limits, and lessons learned. Private API-registration screenshots and raw credentials are intentionally excluded from the public repository.
