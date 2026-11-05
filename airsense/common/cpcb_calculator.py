"""Official CPCB National Air Quality Index (NAQI 2014) Calculator.

Implements the breakpoint interpolation formula, pollutant sub-indices,
averaging period requirements, and data completeness criteria established
in the CPCB NAQI Final Report (2014) by the Central Pollution Control Board
and IIT Kanpur.

Scientific Reference:
    CPCB (2014). National Air Quality Index. Central Pollution Control Board,
    Ministry of Environment, Forest & Climate Change, Government of India.
"""

from __future__ import annotations

import math
from typing import Any, Final

# CPCB NAQI Breakpoint Table: (B_LO, B_HI, I_LO, I_HI)
# Units:
#   PM2.5, PM10, NO2, SO2, O3 (8h): µg/m³
#   CO (8h): mg/m³
CPCB_BREAKPOINTS: Final[dict[str, list[tuple[float, float, int, int]]]] = {
    "pm25": [
        (0.0, 30.0, 0, 50),
        (31.0, 60.0, 51, 100),
        (61.0, 90.0, 101, 200),
        (91.0, 120.0, 201, 300),
        (121.0, 250.0, 301, 400),
        (251.0, 400.0, 401, 500),
    ],
    "pm10": [
        (0.0, 50.0, 0, 50),
        (51.0, 100.0, 51, 100),
        (101.0, 250.0, 101, 200),
        (251.0, 350.0, 201, 300),
        (351.0, 430.0, 301, 400),
        (431.0, 500.0, 401, 500),
    ],
    "no2": [
        (0.0, 40.0, 0, 50),
        (41.0, 80.0, 51, 100),
        (81.0, 180.0, 101, 200),
        (181.0, 280.0, 201, 300),
        (281.0, 400.0, 301, 400),
        (401.0, 500.0, 401, 500),
    ],
    "so2": [
        (0.0, 40.0, 0, 50),
        (41.0, 80.0, 51, 100),
        (81.0, 380.0, 101, 200),
        (381.0, 800.0, 201, 300),
        (801.0, 1600.0, 301, 400),
        (1601.0, 2000.0, 401, 500),
    ],
    "co": [  # Concentration must be in mg/m³
        (0.0, 1.0, 0, 50),
        (1.1, 2.0, 51, 100),
        (2.1, 10.0, 101, 200),
        (10.1, 17.0, 201, 300),
        (17.1, 34.0, 301, 400),
        (34.1, 50.0, 401, 500),
    ],
    "o3": [  # 8-hour average, µg/m³
        (0.0, 50.0, 0, 50),
        (51.0, 100.0, 51, 100),
        (101.0, 168.0, 101, 200),
        (169.0, 208.0, 201, 300),
        (209.0, 748.0, 301, 400),
        (749.0, 1000.0, 401, 500),
    ],
}

# Standard CPCB Categories and associated color palette
CPCB_CATEGORIES: Final[list[tuple[int, int, str, str]]] = [
    (0, 50, "Good", "#00E400"),
    (51, 100, "Satisfactory", "#92D050"),
    (101, 200, "Moderate", "#FFFF00"),
    (201, 300, "Poor", "#FF7E00"),
    (301, 400, "Very Poor", "#FF0000"),
    (401, 500, "Severe", "#7E0023"),
]

POLLUTANT_DISPLAY_NAMES: Final[dict[str, str]] = {
    "pm25": "PM2.5",
    "pm10": "PM10",
    "no2": "NO2",
    "so2": "SO2",
    "co": "CO",
    "o3": "Ozone",
}


def convert_co_ug_to_mg(co_ug: float | None) -> float | None:
    """Convert CO concentration from µg/m³ (Open-Meteo output) to mg/m³ (CPCB standard).

    Returns None if input is None or negative.
    """
    if co_ug is None or math.isnan(co_ug) or co_ug < 0:
        return None
    return round(co_ug / 1000.0, 4)


def get_cpcb_category(aqi: int | float | None) -> tuple[str, str]:
    """Return CPCB Category name and UI hex color code for a given AQI value.

    Returns ('Unknown', '#6B7280') if AQI is None or negative.
    """
    if aqi is None or aqi < 0:
        return ("Unknown", "#6B7280")
    
    val = round(aqi)
    for low, high, cat, color in CPCB_CATEGORIES:
        if low <= val <= high:
            return (cat, color)
    if val > 500:
        return ("Severe", "#7E0023")
    return ("Unknown", "#6B7280")


def calculate_cpcb_subindex(pollutant: str, concentration: float | None) -> int | None:
    """Calculate the CPCB NAQI sub-index for a specific pollutant using linear interpolation.

    Formula:
        I_p = I_LO + [(I_HI - I_LO) / (B_HI - B_LO)] * (C_p - B_LO)

    Args:
        pollutant: Key matching 'pm25', 'pm10', 'no2', 'so2', 'co', or 'o3'.
        concentration: Pollutant concentration (CO in mg/m³, others in µg/m³).

    Returns:
        Integer sub-index (0 to 500, capped at 500 for extreme values), or None if invalid.
    """
    if concentration is None or math.isnan(concentration) or concentration < 0:
        return None

    key = pollutant.lower().replace(".", "").replace("-", "")
    breakpoints = CPCB_BREAKPOINTS.get(key)
    if not breakpoints:
        return None

    # Handle concentrations beyond the maximum breakpoint ceiling
    max_b_hi = breakpoints[-1][1]
    if concentration >= max_b_hi:
        return 500

    for b_lo, b_hi, i_lo, i_hi in breakpoints:
        if b_lo <= concentration <= b_hi:
            sub = i_lo + ((i_hi - i_lo) / (b_hi - b_lo)) * (concentration - b_lo)
            return round(sub)

    # Edge cases between discrete breakpoint steps (e.g., 30.1 - 30.9)
    # Assign to the corresponding upper segment to avoid dead bands
    for idx in range(len(breakpoints) - 1):
        curr_b_hi = breakpoints[idx][1]
        next_b_lo = breakpoints[idx + 1][0]
        if curr_b_hi < concentration < next_b_lo:
            b_lo, b_hi, i_lo, i_hi = breakpoints[idx + 1]
            sub = i_lo + ((i_hi - i_lo) / (b_hi - b_lo)) * (concentration - b_lo)
            return round(sub)

    return None


def calculate_cpcb_naqi(
    pollutants: dict[str, float | None],
    is_indicative: bool = False,
) -> dict[str, Any]:
    """Calculate the overall CPCB National AQI from pollutant concentrations.

    According to official CPCB NAQI guidelines:
    1. At least three pollutants must have valid data.
    2. At least one of the valid pollutants must be PM2.5 or PM10.
    3. The overall AQI is the maximum of the individual sub-indices.
    4. The pollutant responsible for the maximum sub-index is the 'prominent pollutant'.

    Args:
        pollutants: Dictionary mapping pollutant key ('pm25', 'pm10', 'no2', 'so2', 'co', 'o3')
                    to concentration. (CO must be in mg/m³).
        is_indicative: If True, indicates 1-hour or instantaneous snapshot rather than 24h average.

    Returns:
        Dictionary containing:
            - aqi: Overall AQI (int) or None if requirements are not met.
            - category: String category name (e.g., 'Satisfactory') or 'Insufficient Data'.
            - color: Hex color code for UI rendering.
            - prominent_pollutant: String (e.g., 'PM2.5') or None.
            - sub_indices: Dict of computed sub-indices for valid pollutants.
            - is_valid: Boolean indicating whether CPCB minimum data criteria are satisfied.
            - calculation_type: '24h_regulatory' or '1h_indicative'.
            - reason: Diagnostic string when validity criteria fail.
    """
    sub_indices: dict[str, int] = {}
    for poll_key, conc in pollutants.items():
        norm_key = poll_key.lower().replace(".", "").replace("-", "")
        sub = calculate_cpcb_subindex(norm_key, conc)
        if sub is not None:
            sub_indices[norm_key] = sub

    has_pm = ("pm25" in sub_indices) or ("pm10" in sub_indices)
    valid_count = len(sub_indices)
    calc_type = "1h_indicative" if is_indicative else "24h_regulatory"

    if valid_count < 3:
        # If insufficient pollutants for full CPCB NAQI
        # We still return the maximum observed subindex if PM is present as indicative, but flag validity
        prominent = max(sub_indices, key=sub_indices.get) if sub_indices else None
        prom_display = POLLUTANT_DISPLAY_NAMES.get(prominent, prominent) if prominent else None
        return {
            "aqi": max(sub_indices.values()) if sub_indices else None,
            "category": "Insufficient Pollutants",
            "color": "#6B7280",
            "prominent_pollutant": prom_display,
            "sub_indices": sub_indices,
            "is_valid": False,
            "calculation_type": calc_type,
            "reason": f"CPCB requires >= 3 valid pollutants with PM. Found {valid_count} valid.",
        }

    if not has_pm:
        prominent = max(sub_indices, key=sub_indices.get)
        prom_display = POLLUTANT_DISPLAY_NAMES.get(prominent, prominent)
        return {
            "aqi": max(sub_indices.values()),
            "category": "Missing Particulate Matter",
            "color": "#6B7280",
            "prominent_pollutant": prom_display,
            "sub_indices": sub_indices,
            "is_valid": False,
            "calculation_type": calc_type,
            "reason": "CPCB NAQI requires at least PM2.5 or PM10 among valid pollutants.",
        }

    # Criteria satisfied
    max_pollutant = max(sub_indices, key=sub_indices.get)
    max_aqi = sub_indices[max_pollutant]
    cat_name, cat_color = get_cpcb_category(max_aqi)

    return {
        "aqi": max_aqi,
        "category": cat_name,
        "color": cat_color,
        "prominent_pollutant": POLLUTANT_DISPLAY_NAMES.get(max_pollutant, max_pollutant.upper()),
        "sub_indices": sub_indices,
        "is_valid": True,
        "calculation_type": calc_type,
        "reason": None,
    }


def check_data_completeness(
    values: list[float | None],
    min_required: int = 16,
) -> tuple[bool, float | None]:
    """Verify CPCB data completeness requirement for rolling averages.

    For 24-hour rolling averages (PM2.5, PM10, NO2, SO2): minimum 16 valid hours required.
    For 8-hour rolling averages (CO, O3): minimum 6 valid hours required.

    Args:
        values: Sequence of hourly measurements in chronological window.
        min_required: Minimum number of non-null, positive values needed.

    Returns:
        Tuple of (is_complete, arithmetic_mean). If incomplete, returns (False, None).
    """
    valid_vals = [v for v in values if v is not None and not math.isnan(v) and v >= 0]
    if len(valid_vals) < min_required:
        return (False, None)
    return (True, round(sum(valid_vals) / len(valid_vals), 2))
