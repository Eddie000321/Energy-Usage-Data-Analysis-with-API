"""
Fetch monthly Seoul energy usage data via the public Open API.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests

BASE_URL = "http://openapi.seoul.go.kr:8088"
DATASET = "energyUseDataSummaryInfo"
START_YEAR = 2015
END_YEAR = 2024
ROW_START = 1
ROW_END = 1000
RAW_DATA_DIR = Path("data") / "raw"


def get_api_key() -> str:
    api_key = os.environ.get("SEOUL_OPEN_API_KEY")
    if not api_key:
        raise RuntimeError(
            "SEOUL_OPEN_API_KEY environment variable is required. "
            "Set it before running the fetch script."
        )
    return api_key


def build_request_url(year: int, month: int, api_key: str | None = None) -> str:
    api_key = api_key or get_api_key()
    return (
        f"{BASE_URL}/{api_key}/json/{DATASET}/{ROW_START}/{ROW_END}/{year}/{month:02d}"
    )


def validate_response(payload: dict) -> dict:
    section = payload.get(DATASET, {})
    if not section:
        raise ValueError("Unexpected response structure.")

    result = section.get("RESULT", {})
    if result.get("CODE") not in (None, "INFO-000"):
        raise ValueError(f"API error: {result.get('MSG', 'Unknown error')}")

    rows = section.get("row", [])
    if not rows:
        raise ValueError("Empty dataset returned.")

    return section


def extract_personal_rows(section: dict) -> list[dict]:
    personal_rows = [
        row for row in section.get("row", []) if row.get("MM_TYPE") == "개인"
    ]
    if not personal_rows:
        raise ValueError("개인 유형 데이터가 비어 있습니다.")
    return personal_rows


def fetch_month(year: int, month: int, api_key: str | None = None) -> dict:
    url = build_request_url(year, month, api_key)
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    payload = response.json()
    section = validate_response(payload)
    personal_rows = extract_personal_rows(section)
    return {
        DATASET: {
            "RESULT": section.get("RESULT"),
            "list_total_count": len(personal_rows),
            "row": personal_rows,
        }
    }


def save_payload(year: int, month: int, payload: dict) -> None:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RAW_DATA_DIR / f"energy_{year}_{month:02d}.json"
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))


def public_error_message(exc: Exception, api_key: str) -> str:
    """Return a useful failure message without exposing the path-based API key."""
    if isinstance(exc, requests.RequestException):
        return f"{type(exc).__name__}: request failed"
    return str(exc).replace(api_key, "[REDACTED]")


def main() -> int:
    try:
        api_key = get_api_key()
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1

    total_requests = 0
    failed_requests = 0
    for year in range(START_YEAR, END_YEAR + 1):
        for month in range(1, 13):
            try:
                print(f"요청 중: {year}-{month:02d} ...", end=" ")
                payload = fetch_month(year, month, api_key)
                save_payload(year, month, payload)
                total_requests += 1
                print("완료")
            except Exception as exc:
                failed_requests += 1
                print("실패")
                print(f"  ↳ {public_error_message(exc, api_key)}", file=sys.stderr)
            time.sleep(0.3)

    print(
        f"총 {total_requests}개의 월별 데이터를 저장했습니다. 실패: {failed_requests}개"
    )
    return 1 if failed_requests else 0


if __name__ == "__main__":
    sys.exit(main())
