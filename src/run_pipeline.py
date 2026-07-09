"""
Run the full Seoul energy usage pipeline end to end.
"""

from __future__ import annotations

import sys

import fetch_energy_data
import preprocess
import visualize


def main() -> int:
    result = fetch_energy_data.main()
    if result != 0:
        return result

    preprocess.main()
    visualize.main()
    print("전체 파이프라인 실행이 완료되었습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
