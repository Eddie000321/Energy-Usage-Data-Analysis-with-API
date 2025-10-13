"""
Configuration helpers for the Seoul energy usage data pipeline.
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

BASE_URL = "http://openapi.seoul.go.kr:8088"
DATASET = "energyUseDataSummaryInfo"
API_KEY = os.getenv("SEOUL_OPEN_API_KEY", "YOUR_API_KEY_HERE")

# Data collection window
START_YEAR = 2015
END_YEAR = 2024
START_MONTH = 1
END_MONTH = 12

# API pagination bounds (first, last index)
ROW_START = 1
ROW_END = 5

# File system locations
RAW_DATA_DIR = os.path.join("data", "raw")
PROCESSED_DATA_DIR = os.path.join("data", "processed")
FIGURES_DIR = os.path.join("reports", "figures")
