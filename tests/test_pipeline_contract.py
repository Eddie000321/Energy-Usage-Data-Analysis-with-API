"""Network-free contract tests for the energy data pipeline."""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd


SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

import fetch_energy_data  # noqa: E402
import preprocess  # noqa: E402
import run_pipeline  # noqa: E402


def api_payload(*rows: dict[str, str]) -> dict:
    return {
        fetch_energy_data.DATASET: {
            "RESULT": {"CODE": "INFO-000", "MSG": "정상 처리되었습니다"},
            "list_total_count": len(rows),
            "row": list(rows),
        }
    }


def personal_row(month: str, electricity: str) -> dict[str, str]:
    return {
        "MM_TYPE": "개인",
        "YEAR": "2024",
        "MON": month,
        "EUS": electricity,
        "GUS": "20",
        "WUS": "3",
        "HUS": "2",
    }


class PipelineContractTests(unittest.TestCase):
    def test_fetch_month_returns_filtered_contract_without_network(self) -> None:
        individual = personal_row("01", "100")
        organization = {**personal_row("01", "900"), "MM_TYPE": "단체"}
        response = Mock()
        response.json.return_value = api_payload(individual, organization)

        with patch.object(
            fetch_energy_data.requests, "get", return_value=response
        ) as get:
            result = fetch_energy_data.fetch_month(2024, 1, api_key="test-key")

        get.assert_called_once_with(
            "http://openapi.seoul.go.kr:8088/test-key/json/"
            "energyUseDataSummaryInfo/1/1000/2024/01",
            timeout=30,
        )
        response.raise_for_status.assert_called_once_with()
        self.assertEqual(
            result,
            {
                fetch_energy_data.DATASET: {
                    "RESULT": {
                        "CODE": "INFO-000",
                        "MSG": "정상 처리되었습니다",
                    },
                    "list_total_count": 1,
                    "row": [individual],
                }
            },
        )

    def test_save_payload_is_idempotent(self) -> None:
        payload = api_payload(personal_row("01", "100"))

        with tempfile.TemporaryDirectory() as temporary_directory:
            raw_directory = Path(temporary_directory)
            with patch.object(fetch_energy_data, "RAW_DATA_DIR", raw_directory):
                fetch_energy_data.save_payload(2024, 1, payload)
                first_bytes = (raw_directory / "energy_2024_01.json").read_bytes()
                fetch_energy_data.save_payload(2024, 1, payload)
                second_bytes = (raw_directory / "energy_2024_01.json").read_bytes()

            self.assertEqual(first_bytes, second_bytes)
            self.assertEqual(
                json.loads(second_bytes.decode()),
                payload,
            )
            self.assertEqual(
                [path.name for path in raw_directory.iterdir()],
                ["energy_2024_01.json"],
            )

    def test_preprocess_rerun_keeps_csv_snapshot_and_schema(self) -> None:
        organization = {**personal_row("01", "900"), "MM_TYPE": "단체"}

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            raw_directory = root / "raw"
            processed_directory = root / "processed"
            raw_directory.mkdir()
            (raw_directory / "energy_2024_02.json").write_text(
                json.dumps(api_payload(personal_row("02", "200"))),
                encoding="utf-8",
            )
            (raw_directory / "energy_2024_01.json").write_text(
                json.dumps(api_payload(personal_row("01", "100"), organization)),
                encoding="utf-8",
            )

            with (
                patch.object(preprocess, "RAW_DATA_DIR", raw_directory),
                patch.object(preprocess, "PROCESSED_DATA_DIR", processed_directory),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                preprocess.main()
                output = processed_directory / "energy_usage_personal.csv"
                first_bytes = output.read_bytes()
                preprocess.main()
                second_bytes = output.read_bytes()

            self.assertEqual(first_bytes, second_bytes)
            frame = pd.read_csv(output)
            self.assertEqual(
                frame.columns.tolist(),
                [
                    "year",
                    "month",
                    "electricity_kwh",
                    "gas_m3",
                    "water_m3",
                    "district_heating",
                    "date",
                    "season",
                    "total_usage",
                ],
            )
            self.assertEqual(
                frame.to_dict(orient="records"),
                [
                    {
                        "year": 2024,
                        "month": 1,
                        "electricity_kwh": 100.0,
                        "gas_m3": 20.0,
                        "water_m3": 3.0,
                        "district_heating": 2.0,
                        "date": "2024-01-01",
                        "season": "겨울",
                        "total_usage": 125.0,
                    },
                    {
                        "year": 2024,
                        "month": 2,
                        "electricity_kwh": 200.0,
                        "gas_m3": 20.0,
                        "water_m3": 3.0,
                        "district_heating": 2.0,
                        "date": "2024-02-01",
                        "season": "겨울",
                        "total_usage": 225.0,
                    },
                ],
            )

    def test_pipeline_runs_each_stage_in_order(self) -> None:
        calls: list[str] = []

        with (
            patch.object(
                run_pipeline.fetch_energy_data,
                "main",
                side_effect=lambda: calls.append("fetch") or 0,
            ),
            patch.object(
                run_pipeline.preprocess,
                "main",
                side_effect=lambda: calls.append("preprocess"),
            ),
            patch.object(
                run_pipeline.visualize,
                "main",
                side_effect=lambda: calls.append("visualize"),
            ),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            result = run_pipeline.main()

        self.assertEqual(result, 0)
        self.assertEqual(calls, ["fetch", "preprocess", "visualize"])

    def test_pipeline_stops_when_fetch_fails(self) -> None:
        with (
            patch.object(run_pipeline.fetch_energy_data, "main", return_value=1),
            patch.object(run_pipeline.preprocess, "main") as preprocess_main,
            patch.object(run_pipeline.visualize, "main") as visualize_main,
        ):
            result = run_pipeline.main()

        self.assertEqual(result, 1)
        preprocess_main.assert_not_called()
        visualize_main.assert_not_called()


if __name__ == "__main__":
    unittest.main()
