"""
AirSense — Automated Core Unit Test Suite
File: tests/test_airsense_core.py
M.Sc. IT (Business Intelligence & Analytics) Capstone | Gujarat University

Tests the 4 critical analytical & engineering pillars:
1. CPCB breakpoint interpolation at exact boundary thresholds (PM2.5=60 -> AQI 100).
2. CPCB statutory minimum rules (3-pollutant rule and mandatory particulate presence).
3. Grounded AI safety guardrail sanitization (stripping clinical dosage hallucinations).
4. 2-Slider Prescriptive Policy Simulator dominant-pollutant bottleneck shift.
"""

from __future__ import annotations

import pytest
from common.cpcb_calculator import (
    calculate_cpcb_naqi,
    calculate_cpcb_subindex,
    get_cpcb_category,
)
from rag.health_advisor import sanitize_llm_output


def test_cpcb_exact_boundary():
    """
    Test 1: Verify exact linear interpolation at the CPCB Satisfactory ceiling.
    - PM2.5: 60 µg/m³ is the exact upper boundary of Satisfactory (Index 100)
    - PM10: 100 µg/m³ is the exact upper boundary of Satisfactory (Index 100)
    - NO2: 40 µg/m³ is the upper boundary of Good (Index 50)
    Expected overall NAQI: exactly 100, Satisfactory, is_valid=True.
    """
    readings = {"pm25": 60.0, "pm10": 100.0, "no2": 40.0}
    res = calculate_cpcb_naqi(readings)

    assert res["is_valid"] is True, "Calculation must satisfy CPCB 3-pollutant rule."
    assert res["aqi"] == 100, f"Expected AQI 100 at boundary, got {res['aqi']}."
    assert res["category"] == "Satisfactory", f"Expected Satisfactory, got {res['category']}."
    assert res["sub_indices"]["pm25"] == 100
    assert res["sub_indices"]["pm10"] == 100
    assert res["sub_indices"]["no2"] == 50


def test_cpcb_statutory_minimum_rules():
    """
    Test 2: Enforce CPCB statutory validity mandates:
    (a) At least 3 pollutants must be monitored.
    (b) At least one monitored pollutant MUST be PM2.5 or PM10.
    """
    # Case A: Only 2 pollutants present -> should fail minimum pollutant count
    case_two_polls = {"pm25": 55.0, "no2": 42.0}
    res_a = calculate_cpcb_naqi(case_two_polls)
    assert res_a["is_valid"] is False, "2 pollutants must not qualify as official regulatory CPCB NAQI."
    assert "CPCB requires >= 3 valid pollutants" in res_a["reason"]

    # Case B: 3 pollutants present, but NO particulate matter (PM2.5 / PM10)
    case_no_pm = {"no2": 45.0, "so2": 35.0, "co": 1.2}
    res_b = calculate_cpcb_naqi(case_no_pm)
    assert res_b["is_valid"] is False, "Missing PM must fail regulatory CPCB NAQI."
    assert "PM2.5 or PM10" in res_b["reason"]


def test_ai_advisor_guardrail_sanitization():
    """
    Test 3: Phase 6 Output Guardrail.
    Ensure that any hallucinated clinical medical dosages (e.g. '500 mg', '250mg', '10 ml')
    are stripped and replaced with safe physician advisory guidance.
    """
    hallucinated_text = (
        "For respiratory relief during high PM2.5 smog, take 500 mg paracetamol twice daily, "
        "or 250mg amoxicillin along with 10 ml cough syrup."
    )
    sanitized = sanitize_llm_output(hallucinated_text)

    # Must NOT contain forbidden clinical dosages
    assert "500 mg" not in sanitized
    assert "250mg" not in sanitized
    assert "10 ml" not in sanitized
    # Must contain the protective substitution token
    assert "[Medical dosage removed — consult a physician]" in sanitized


def test_two_slider_bottleneck_shift():
    """
    Test 4: Prescriptive Policy Simulator Bottleneck Physics.
    Verifies that when vehicular curbs lower PM2.5 below PM10 dust sub-index,
    the overall AQI bottlenecks at PM10, proving dynamic CPCB max() recalculation.
    """
    # Baseline: Heavy vehicular PM2.5 = 120 (sub-index ~300), Construction PM10 = 150 (sub-index ~133)
    base_pm25 = 120.0
    base_pm10 = 150.0
    base_no2 = 80.0

    sub_pm25_base = calculate_cpcb_subindex("pm25", base_pm25)
    sub_pm10_base = calculate_cpcb_subindex("pm10", base_pm10)
    assert sub_pm25_base > sub_pm10_base, "Baseline PM2.5 must be dominant."

    # Policy Intervention 1: 50% Vehicular Curb ONLY (dust_curb = 0%)
    veh_curb = 0.50
    dust_curb = 0.0

    sim_pm25 = base_pm25 * (1.0 - veh_curb)   # 60.0 µg/m³ -> subindex 100
    sim_pm10 = base_pm10 * (1.0 - dust_curb)  # 150.0 µg/m³ -> subindex 133
    sim_no2 = base_no2 * (1.0 - veh_curb)     # 40.0 µg/m³ -> subindex 50

    res_sim1 = calculate_cpcb_naqi({"pm25": sim_pm25, "pm10": sim_pm10, "no2": sim_no2})
    # PM2.5 is now 100, but PM10 is 134 -> AQI bottlenecks at 134
    assert res_sim1["aqi"] == 134
    assert res_sim1["prominent_pollutant"] == "PM10", "PM10 dust must become dominant bottleneck."

    # Policy Intervention 2: Also curb construction dust by 40%
    dust_curb_2 = 0.40
    sim_pm10_fixed = base_pm10 * (1.0 - dust_curb_2)  # 90.0 µg/m³ -> subindex 90

    res_sim2 = calculate_cpcb_naqi({"pm25": sim_pm25, "pm10": sim_pm10_fixed, "no2": sim_no2})
    # Both PM2.5 (100) and PM10 (90) curbed -> AQI drops to 100 (Satisfactory)
    assert res_sim2["aqi"] == 100
    assert res_sim2["category"] == "Satisfactory"
