"""Contract tests for the public analytical summary."""

from __future__ import annotations

import csv
import unittest
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "processed" / "energy_usage_personal.csv"
REPORT_PATH = ROOT / "reports" / "analysis.md"
README_PATH = ROOT / "README.md"


class ReportAnalysisTests(unittest.TestCase):
    def test_summary_is_complete_bounded_and_derived_from_tracked_data(self) -> None:
        with CSV_PATH.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))

        annual_totals: dict[int, float] = defaultdict(float)
        seasonal_gas: dict[str, list[float]] = defaultdict(list)
        for row in rows:
            annual_totals[int(row["year"])] += float(row["total_usage"])
            seasonal_gas[row["season"]].append(float(row["gas_m3"]))

        report = REPORT_PATH.read_text(encoding="utf-8")
        summary = " ".join(
            line.strip()
            for line in report.splitlines()
            if line.strip() and not line.startswith("#")
        )

        self.assertLessEqual(len(summary), 200)
        self.assertNotIn("정리하세요", report)
        self.assertNotIn("추정 원인", report)
        self.assertEqual(len(rows), 120)
        self.assertEqual(len({(row["year"], row["month"]) for row in rows}), 120)

        growth = (annual_totals[2024] / annual_totals[2015] - 1) * 100
        winter_mean = sum(seasonal_gas["겨울"]) / len(seasonal_gas["겨울"])
        summer_mean = sum(seasonal_gas["여름"]) / len(seasonal_gas["여름"])

        self.assertIn(f"{annual_totals[2015] / 100_000_000:.1f}억", summary)
        self.assertIn(f"{annual_totals[2024] / 100_000_000:.1f}억", summary)
        self.assertIn(f"{growth:.1f}%", summary)
        self.assertIn(f"{winter_mean / 10_000:,.0f}만m³", summary)
        self.assertIn(f"{summer_mean / 10_000:,.0f}만m³", summary)
        self.assertIn(f"{winter_mean / summer_mean:.1f}배", summary)
        self.assertIn("월 집계 가스값 평균", summary)
        self.assertIn("절대 에너지량·원인으로 해석하지 않았다", summary)
        self.assertTrue(
            all(
                4_100_000_000 <= annual_totals[year] < 4_200_000_000
                for year in range(2022, 2025)
            )
        )

    def test_readme_preserves_official_source_and_license_attribution(self) -> None:
        readme = README_PATH.read_text(encoding="utf-8")

        self.assertIn(
            "https://data.seoul.go.kr/dataList/OA-15361/A/1/datasetView.do",
            readme,
        )
        self.assertIn("서울시 에코마일리지 에너지사용량 통계정보(회원유형별)", readme)
        self.assertIn("Seoul Metropolitan Government", readme)
        self.assertIn("https://www.kogl.or.kr/info/licenseType1.do", readme)
        self.assertIn("Type 1", readme)
        self.assertIn("No ownership of the Seoul source data is claimed", readme)
        self.assertIn("must not imply sponsorship", readme)
        self.assertIn("not a normalized energy measure", readme)
        self.assertIn("not a per-household average", readme)
        self.assertIn("it is not a software license", readme)
        self.assertIn("no separate open-source license", readme)


if __name__ == "__main__":
    unittest.main()
