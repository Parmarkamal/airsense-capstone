"""Unit tests for official CPCB NAQI 2014 Calculator."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common.cpcb_calculator import (
    calculate_cpcb_subindex,
    calculate_cpcb_naqi,
    convert_co_ug_to_mg,
    get_cpcb_category,
    check_data_completeness,
)


def test_pm25_subindex_interpolation():
    """Verify PM2.5 sub-index against official CPCB 2014 breakpoints."""
    # Good: 0-30 -> 0-50
    assert calculate_cpcb_subindex("pm25", 15.0) == 25
    # Satisfactory: 31-60 -> 51-100 (51 + (49/29)*4 = 57.76 -> 58)
    assert calculate_cpcb_subindex("pm25", 35.0) == 58
    # Moderate: 61-90 -> 101-200 (101 + (99/29)*14 = 148.79 -> 149)
    assert calculate_cpcb_subindex("pm25", 75.0) == 149
    # Poor: 91-120 -> 201-300 (201 + (99/29)*19 = 265.86 -> 266)
    assert calculate_cpcb_subindex("pm25", 110.0) == 266
    # Very Poor: 121-250 -> 301-400 (301 + (99/129)*79 = 361.63 -> 362)
    assert calculate_cpcb_subindex("pm25", 200.0) == 362
    # Severe: 251-400 -> 401-500 (401 + (99/149)*49 = 433.56 -> 434)
    assert calculate_cpcb_subindex("pm25", 300.0) == 434
    # Beyond 400: Capped at 500
    assert calculate_cpcb_subindex("pm25", 450.0) == 500


def test_pm10_subindex_interpolation():
    """Verify PM10 sub-index against official breakpoints."""
    assert calculate_cpcb_subindex("pm10", 25.0) == 25
    assert calculate_cpcb_subindex("pm10", 75.0) == 75
    assert calculate_cpcb_subindex("pm10", 175.0) == 150
    assert calculate_cpcb_subindex("pm10", 300.0) == 250
    assert calculate_cpcb_subindex("pm10", 600.0) == 500


def test_co_unit_conversion_and_subindex():
    """Verify CO conversion from µg/m³ to mg/m³ and correct sub-index calculation."""
    # 211 µg/m³ is typical Open-Meteo Ahmedabad reading -> 0.211 mg/m³
    mg = convert_co_ug_to_mg(211.0)
    assert mg == 0.211
    # 0.211 mg/m³ in Good bracket (0-1.0 mg/m³ -> 0-50): 0 + 50*0.211 = 10.55 -> 11
    sub = calculate_cpcb_subindex("co", mg)
    assert sub == 11

    # In Satisfactory bracket: 1.5 mg/m³ (1.1-2.0 -> 51-100)
    # 51 + (49 / 0.9) * 0.4 = 51 + 21.77 = 72.77 -> 73
    assert calculate_cpcb_subindex("co", 1.5) == 73


def test_invalid_and_edge_inputs():
    """Ensure negative, None, and unknown pollutants return None safely."""
    assert calculate_cpcb_subindex("pm25", -5.0) is None
    assert calculate_cpcb_subindex("pm25", None) is None
    assert calculate_cpcb_subindex("unknown_pollutant", 50.0) is None
    assert convert_co_ug_to_mg(-100.0) is None
    assert convert_co_ug_to_mg(None) is None


def test_cpcb_category_mapping():
    """Verify categories and color mapping."""
    cat, color = get_cpcb_category(25)
    assert cat == "Good"
    assert color == "#00E400"

    cat, color = get_cpcb_category(75)
    assert cat == "Satisfactory"
    assert color == "#92D050"

    cat, color = get_cpcb_category(150)
    assert cat == "Moderate"

    cat, color = get_cpcb_category(250)
    assert cat == "Poor"

    cat, color = get_cpcb_category(350)
    assert cat == "Very Poor"

    cat, color = get_cpcb_category(450)
    assert cat == "Severe"

    cat, _ = get_cpcb_category(None)
    assert cat == "Unknown"


def test_data_completeness_criteria():
    """Verify 24h (min 16) and 8h (min 6) completeness rules."""
    # 16 valid out of 24
    hours_24_valid = [50.0] * 16 + [None] * 8
    is_valid, mean = check_data_completeness(hours_24_valid, min_required=16)
    assert is_valid is True
    assert mean == 50.0

    # 15 valid out of 24 (insufficient)
    hours_24_invalid = [50.0] * 15 + [None] * 9
    is_valid, mean = check_data_completeness(hours_24_invalid, min_required=16)
    assert is_valid is False
    assert mean is None

    # 8h window with 6 valid
    hours_8_valid = [1.5] * 6 + [None] * 2
    is_valid, mean = check_data_completeness(hours_8_valid, min_required=6)
    assert is_valid is True
    assert mean == 1.5


def test_overall_naqi_calculation_valid():
    """Verify NAQI when >= 3 pollutants and PM is present."""
    pollutants = {
        "pm25": 75.0,   # subindex = 149
        "pm10": 80.0,   # subindex = 80
        "no2": 30.0,    # subindex = 38
        "co": 0.5,      # subindex = 25
    }
    result = calculate_cpcb_naqi(pollutants)
    assert result["is_valid"] is True
    assert result["aqi"] == 149
    assert result["prominent_pollutant"] == "PM2.5"
    assert result["category"] == "Moderate"
    assert result["sub_indices"]["pm25"] == 149


def test_overall_naqi_insufficient_pollutants():
    """Verify NAQI fails when fewer than 3 pollutants are present."""
    pollutants = {
        "pm25": 75.0,
        "pm10": 80.0,
    }
    result = calculate_cpcb_naqi(pollutants)
    assert result["is_valid"] is False
    assert "CPCB requires >= 3 valid pollutants" in result["reason"]


def test_overall_naqi_missing_particulate_matter():
    """Verify NAQI fails when NO2, SO2, CO are present but PM2.5/PM10 are missing."""
    pollutants = {
        "no2": 50.0,
        "so2": 30.0,
        "co": 1.2,
    }
    result = calculate_cpcb_naqi(pollutants)
    assert result["is_valid"] is False
    assert "Missing Particulate Matter" in result["category"]
