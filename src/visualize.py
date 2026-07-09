"""
Generate charts from the processed Seoul energy usage dataset.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd

FIGURES_DIR = Path("reports") / "figures"
PROCESSED_DATA_DIR = Path("data") / "processed"

PREFERRED_FONTS = [
    "AppleGothic",
    "Malgun Gothic",
    "NanumGothic",
    "NanumBarunGothic",
    "NanumSquareOTF",
    "Noto Sans CJK KR",
    "DejaVu Sans",
]


def configure_font() -> None:
    available_fonts = {font.name for font in font_manager.fontManager.ttflist}
    for name in PREFERRED_FONTS:
        if name in available_fonts:
            plt.rcParams["font.family"] = name
            break
    else:  # No preferred font found
        print("경고: 한글 폰트를 찾을 수 없어 기본 글꼴을 사용합니다.")
    plt.rcParams["axes.unicode_minus"] = False


def load_processed_data() -> pd.DataFrame:
    path = PROCESSED_DATA_DIR / "energy_usage_personal.csv"
    if not path.exists():
        raise FileNotFoundError(
            "전처리된 CSV를 찾을 수 없습니다. preprocess 스크립트를 먼저 실행하세요."
        )
    return pd.read_csv(path, parse_dates=["date"])


def plot_annual_total(df: pd.DataFrame) -> None:
    annual = df.groupby("year", as_index=False)["total_usage"].sum()

    plt.figure(figsize=(10, 6))
    plt.plot(annual["year"], annual["total_usage"], marker="o")
    plt.title("연도별 과제용 단순 합계 변화 - 2212")
    plt.xlabel("연도")
    plt.ylabel("서로 다른 원 단위 수치의 단순 합계")
    plt.grid(True, linestyle="--", alpha=0.5)

    output = FIGURES_DIR / "annual_total_energy_2212.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output, dpi=150)
    plt.close()


def plot_seasonal_gas(df: pd.DataFrame) -> None:
    season_order = ["봄", "여름", "가을", "겨울"]
    seasonal = df.groupby("season")["gas_m3"].mean().reindex(season_order)

    plt.figure(figsize=(8, 6))
    bars = plt.bar(seasonal.index, seasonal.values, color="#4C72B0")
    plt.title("개인 유형의 계절별 월 집계 가스값 평균")
    plt.xlabel("계절")
    plt.ylabel("원자료 가스값 평균 (㎥)")

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height:,.0f}",
            ha="center",
            va="bottom",
        )

    output = FIGURES_DIR / "seasonal_gas_usage.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output, dpi=150)
    plt.close()


def main() -> None:
    configure_font()
    df = load_processed_data()
    plot_annual_total(df)
    plot_seasonal_gas(df)
    print("그래프 생성 완료:", FIGURES_DIR)


if __name__ == "__main__":
    main()
