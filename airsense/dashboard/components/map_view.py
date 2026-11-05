"""
AirSense — Interactive Folium Map View
File: dashboard/components/map_view.py
Week: 4 Deliverable

Renders an interactive geographic bubble map of India showing:
  - Real-time station locations with 100% free OpenStreetMap tiles (NO API keys required)
  - Permanent city name & AQI badges for instant non-tech recognition
  - Color-coded CPCB bubbles sized by pollution severity
  - Rich interactive click popups
"""

from __future__ import annotations

import folium
import pandas as pd
from dashboard.components.gauges import get_aqi_category


def create_india_air_map(df_latest: pd.DataFrame) -> folium.Map:
    """
    Generate an interactive Folium map centered on India with color-coded
    air quality bubbles for all monitored urban centers.
    Uses free, open tile providers that require NO API keys.
    """
    # Center geographically over India with appropriate initial zoom
    india_center = [21.5, 78.5]
    m = folium.Map(
        location=india_center,
        zoom_start=5,
        tiles="OpenStreetMap",  # 100% Free, NO API KEY, full city & state names visible
        control_scale=True,
    )

    if df_latest.empty:
        return m

    for _, row in df_latest.iterrows():
        lat = row.get("lat")
        lon = row.get("lon")
        if pd.isna(lat) or pd.isna(lon):
            continue

        aqi = row.get("aqi")
        city_name = row.get("city_display_name", row.get("city", "Unknown"))
        pm25 = row.get("pm25")
        pm10 = row.get("pm10")
        category = get_aqi_category(aqi)

        safe_aqi = int(aqi) if aqi is not None and not pd.isna(aqi) else "--"
        safe_pm25 = f"{float(pm25):.1f}" if pm25 is not None and not pd.isna(pm25) else "--"
        safe_pm10 = f"{float(pm10):.1f}" if pm10 is not None and not pd.isna(pm10) else "--"

        # Bubble radius scaled smoothly with AQI
        radius = 16
        if isinstance(safe_aqi, int):
            radius = max(14, min(28, int(safe_aqi / 14) + 12))

        # Permanent badge tooltip visible at all times (perfect for teachers & non-tech users)
        badge_html = f"""
        <div style="
            font-family: 'Segoe UI', Inter, sans-serif;
            font-weight: 700;
            font-size: 12px;
            background: #0F172A;
            color: #FFFFFF;
            padding: 3px 8px;
            border-radius: 6px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            white-space: nowrap;
            border-left: 4px solid {category['color']};
        ">
            {city_name}: <span style="color: {category['color']};">{safe_aqi} AQI</span>
        </div>
        """

        # Rich click popup
        popup_html = f"""
        <div style="font-family: 'Segoe UI', Inter, sans-serif; width: 220px; padding: 4px;">
            <div style="font-size: 16px; font-weight: 800; color: #0F172A; border-bottom: 2px solid {category['color']}; padding-bottom: 4px; margin-bottom: 8px;">
                📍 {city_name}
            </div>
            <div style="display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 8px;">
                <span style="font-size: 28px; font-weight: 800; color: {category['color']};">{safe_aqi}</span>
                <span style="font-size: 11px; font-weight: 700; background-color: {category['bg_color']}; color: {category['text_color']}; padding: 3px 8px; border-radius: 9999px;">
                    {category['label'].upper()}
                </span>
            </div>
            <div style="font-size: 12px; color: #334155; line-height: 1.6; background-color: #F8FAFC; padding: 8px 10px; border-radius: 8px; border: 1px solid #E2E8F0;">
                • <b>PM2.5:</b> {safe_pm25} µg/m³<br>
                • <b>PM10:</b> {safe_pm10} µg/m³<br>
                • <b>Source:</b> Ground-level WAQI/CPCB
            </div>
            <div style="font-size: 11px; color: {category['text_color']}; background: {category['bg_color']}; padding: 6px 8px; border-radius: 6px; margin-top: 8px; line-height: 1.4;">
                <b>Advisory:</b> {category['advisory']}
            </div>
        </div>
        """

        # Outer glowing halo
        folium.CircleMarker(
            location=[lat, lon],
            radius=radius + 6,
            color=category["color"],
            weight=1,
            fill=True,
            fill_color=category["color"],
            fill_opacity=0.20,
        ).add_to(m)

        # Core circle marker with permanent label
        marker = folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color="#FFFFFF",
            weight=2.5,
            fill=True,
            fill_color=category["color"],
            fill_opacity=0.90,
            popup=folium.Popup(popup_html, max_width=280),
        )
        
        # Add permanent tooltip so city name & AQI are visible immediately without clicking
        marker.add_child(
            folium.Tooltip(badge_html, permanent=True, direction="top", opacity=0.95)
        )
        marker.add_to(m)

    return m
