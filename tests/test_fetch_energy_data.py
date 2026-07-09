"""Network-free tests for the Seoul energy data fetch stage."""

from __future__ import annotations

import io
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

import fetch_energy_data  # noqa: E402


class FetchEnergyDataTests(unittest.TestCase):
    def test_main_fails_before_network_when_api_key_is_missing(self) -> None:
        stderr = io.StringIO()

        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(fetch_energy_data, "fetch_month") as fetch_month,
            patch("sys.stderr", stderr),
        ):
            result = fetch_energy_data.main()

        self.assertEqual(result, 1)
        fetch_month.assert_not_called()
        self.assertIn("SEOUL_OPEN_API_KEY", stderr.getvalue())

    def test_build_request_url_uses_explicit_key_and_zero_padded_month(self) -> None:
        url = fetch_energy_data.build_request_url(2024, 3, api_key="test-key")

        self.assertEqual(
            url,
            "http://openapi.seoul.go.kr:8088/test-key/json/"
            "energyUseDataSummaryInfo/1/1000/2024/03",
        )

    def test_valid_response_keeps_only_personal_rows(self) -> None:
        personal_row = {"MM_TYPE": "개인", "YEAR": "2024", "MON": "01"}
        payload = {
            fetch_energy_data.DATASET: {
                "RESULT": {"CODE": "INFO-000", "MSG": "정상 처리되었습니다"},
                "row": [
                    personal_row,
                    {"MM_TYPE": "단체", "YEAR": "2024", "MON": "01"},
                ],
            }
        }

        section = fetch_energy_data.validate_response(payload)
        rows = fetch_energy_data.extract_personal_rows(section)

        self.assertEqual(rows, [personal_row])

    def test_main_fails_closed_and_redacts_key_after_request_errors(self) -> None:
        api_key = "live-looking-test-key"
        stdout = io.StringIO()
        stderr = io.StringIO()

        with (
            patch.dict(os.environ, {"SEOUL_OPEN_API_KEY": api_key}, clear=True),
            patch.object(fetch_energy_data, "START_YEAR", 2024),
            patch.object(fetch_energy_data, "END_YEAR", 2024),
            patch.object(
                fetch_energy_data,
                "fetch_month",
                side_effect=RuntimeError(f"request failed for /{api_key}/json"),
            ) as fetch_month,
            patch.object(fetch_energy_data.time, "sleep"),
            patch("sys.stdout", stdout),
            patch("sys.stderr", stderr),
        ):
            result = fetch_energy_data.main()

        self.assertEqual(result, 1)
        self.assertEqual(fetch_month.call_count, 12)
        self.assertIn("실패: 12개", stdout.getvalue())
        self.assertIn("[REDACTED]", stderr.getvalue())
        self.assertNotIn(api_key, stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
