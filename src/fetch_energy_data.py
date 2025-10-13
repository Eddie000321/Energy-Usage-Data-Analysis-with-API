"""
Fetch monthly Seoul energy usage data via the public Open API.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import requests

import config


def build_request_url(year: int, month: int) -> str:
    return (
        f"{config.BASE_URL}/{config.API_KEY}/json/"
        f"{config.DATASET}/{config.ROW_START}/{config.ROW_END}/{year}/{month:02d}"
    )


def validate_response(payload: dict) -> dict:
    section = payload.get(config.DATASET, {})
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


def fetch_month(year: int, month: int) -> dict:
    url = build_request_url(year, month)
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    payload = response.json()
    section = validate_response(payload)
    personal_rows = extract_personal_rows(section)
    return {
        config.DATASET: {
            "RESULT": section.get("RESULT"),
            "list_total_count": len(personal_rows),
            "row": personal_rows,
        }
    }


def save_payload(year: int, month: int, payload: dict) -> None:
    output_path = Path(config.RAW_DATA_DIR) / f"energy_{year}_{month:02d}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    if not config.API_KEY or config.API_KEY == "YOUR_API_KEY_HERE":
        print("환경 변수 SEOUL_OPEN_API_KEY 가 설정되지 않았습니다.", file=sys.stderr)
        return 1

    total_requests = 0
    for year in range(config.START_YEAR, config.END_YEAR + 1):
        for month in range(config.START_MONTH, config.END_MONTH + 1):
            try:
                print(f"요청 중: {year}-{month:02d} ...", end=" ")
                payload = fetch_month(year, month)
                save_payload(year, month, payload)
                total_requests += 1
                print("완료")
            except Exception as exc:
                print("실패")
                print(f"  ↳ {exc}", file=sys.stderr)
            time.sleep(0.3)

    print(f"총 {total_requests}개의 월별 데이터를 저장했습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
