"""
Transform raw JSON payloads into an analysis-ready DataFrame.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import pandas as pd
from io import StringIO

DATASET = "energyUseDataSummaryInfo"
RAW_DATA_DIR = Path("data") / "raw"
PROCESSED_DATA_DIR = Path("data") / "processed"


def load_raw_files(directory: Path) -> Iterable[dict]:
    for path in sorted(directory.glob("energy_*.json")):
        with path.open(encoding="utf-8") as handle:
            yield json.load(handle)


def parse_records(payload: dict) -> list[dict]:
    rows = payload.get(DATASET, {}).get("row", [])
    return [
        {
            "year": int(row["YEAR"]),
            "month": int(row["MON"]),
            "electricity_kwh": float(row["EUS"]),
            "gas_m3": float(row["GUS"]),
            "water_m3": float(row["WUS"]),
            "district_heating": float(row["HUS"]),
        }
        for row in rows
        if row.get("MM_TYPE") == "개인"
    ]


def determine_season(month: int) -> str:
    if month in (3, 4, 5):
        return "봄"
    if month in (6, 7, 8):
        return "여름"
    if month in (9, 10, 11):
        return "가을"
    return "겨울"


def print_problem_2_1(df: pd.DataFrame) -> None:
    """Problem 2-1: show DataFrame structure and preview."""
    print(
        "문제 2-1. 수집한 JSON 데이터를 pandas DataFrame으로 변환하고 기본 정보를 출력하시오."
    )
    print("[결과]")
    info_buffer = StringIO()
    df.info(buf=info_buffer)
    print(info_buffer.getvalue().strip())
    print("\nDataFrame 앞부분(5행):")
    print(df.head())


def add_problem_2_2_columns(df: pd.DataFrame) -> None:
    """Problem 2-2: derive year/season columns (and helper totals) from the date."""
    df["date"] = pd.to_datetime(dict(year=df["year"], month=df["month"], day=1))
    df["year"] = df["date"].dt.year  # emphasize derivation from the date column
    df["season"] = df["date"].dt.month.apply(determine_season)
    df["total_usage"] = (
        df["electricity_kwh"] + df["gas_m3"] + df["water_m3"] + df["district_heating"]
    )


def print_problem_2_2(df: pd.DataFrame) -> None:
    """Problem 2-2: display the new columns and their distribution."""
    print(
        "\n문제 2-2. 날짜 컬럼을 활용하여 연도(year)와 계절(season) 컬럼을 추가한 결과를 확인하시오."
    )
    print("[결과]")
    print(df.loc[:, ["date", "year", "month", "season"]].head())
    print("\n계절별 건수:")
    print(df["season"].value_counts().sort_index())


def main() -> None:
    raw_dir = RAW_DATA_DIR
    if not raw_dir.exists():
        raise FileNotFoundError(
            "원본 데이터가 존재하지 않습니다. 먼저 fetch 스크립트를 실행하세요."
        )

    records: list[dict] = []
    for payload in load_raw_files(raw_dir):
        records.extend(parse_records(payload))

    if not records:
        raise ValueError("전처리할 개인 유형 데이터가 비어 있습니다.")

    df = pd.DataFrame(records)
    print_problem_2_1(df)

    add_problem_2_2_columns(df)
    print_problem_2_2(df)

    output_path = PROCESSED_DATA_DIR / "energy_usage_personal.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n저장 완료: {output_path}")


if __name__ == "__main__":
    main()
