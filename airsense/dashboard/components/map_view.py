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
from dashboard.data_access import calculate_data_freshness


def create_india_air_map(df_latest: pd.DataFrame) -> folium.Map:
    """
    Generate an interactive Folium map centered on India with color-coded
    air quality bubbles for all monitored urban centers.
    Uses CartoDB dark_matter tiles for sleek dark aesthetics.
    """
    # Center geographically over India with appropriate initial zoom
    india_center = [21.5, 78.5]
    m = folium.Map(
        location=india_center,
        zoom_start=5,
        tiles="CartoDB dark_matter",
        control_scale=True,
    )

    if df_latest.empty:
        return m

    for _, row in df_latest.iterrows():
        lat = row.get("lat")
        lon = row.get("lon")
        if pd.isna(lat) or pd.isna(lon):
            continue

        cpcb = row.get("cpcb_aqi")
        aqi = cpcb if (pd.notna(cpcb) and cpcb is not None) else row.get("aqi")
        city_name = row.get("city_display_name", row.get("city", "Unknown"))
        pm25 = row.get("pm25")
        pm10 = row.get("pm10")
        prom = row.get("prominent_pollutant") or "PM2.5"
        category = get_aqi_category(aqi)
        source = row.get("data_source", "WAQI")

        if "freshness_label" in row.index and pd.notna(row.get("freshness_label")):
            freshness_label = str(row["freshness_label"])
        else:
            _, freshness_label, _ = calculate_data_freshness(row.get("time"))

        safe_aqi = int(aqi) if aqi is not None and not pd.isna(aqi) else "--"
        safe_pm25 = f"{float(pm25):.1f}" if pm25 is not None and not pd.isna(pm25) else "--"
        safe_pm10 = f"{float(pm10):.1f}" if pm10 is not None and not pd.isna(pm10) else "--"

        # Bubble radius scaled smoothly with AQI
        radius = 16
        if isinstance(safe_aqi, int):
            radius = max(14, min(28, int(safe_aqi / 14) + 12))

        # Rich dark-styled click popup
        popup_html = f"""
        <div style="font-family: 'Segoe UI', Inter, sans-serif; width: 230px; padding: 6px; background: #0F172A; color: #F8FAFC; border-radius: 8px;">
            <div style="font-size: 15px; font-weight: 800; color: #F8FAFC; border-bottom: 2px solid {category['color']}; padding-bottom: 4px; margin-bottom: 8px;">
                📍 {city_name}
            </div>
            <div style="display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 8px;">
                <span style="font-size: 26px; font-weight: 800; color: {category['color']};">{safe_aqi} <span style="font-size:12px;color:#94A3B8;">AQI</span></span>
                <span style="font-size: 11px; font-weight: 700; background: {category['color']}22; color: {category['color']}; border: 1px solid {category['color']}66; padding: 2px 8px; border-radius: 9999px;">
                    {category['label'].upper()}
                </span>
            </div>
            <div style="font-size: 11.5px; color: #CBD5E1; line-height: 1.6; background: rgba(30,41,59,0.7); padding: 8px 10px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.06);">
                • <b>Key Pollutant:</b> {prom}<br>
                • <b>PM2.5:</b> {safe_pm25} µg/m³<br>
                • <b>PM10:</b> {safe_pm10} µg/m³<br>
                • <b>Source:</b> {source}<br>
                • <b>Freshness:</b> {freshness_label}
            </div>
            <div style="font-size: 11px; color: #E2E8F0; background: rgba(15,23,42,0.85); border-left: 3px solid {category['color']}; padding: 6px 8px; border-radius: 4px; margin-top: 8px; line-height: 1.4;">
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

        # Core circle marker
        marker = folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color="#FFFFFF",
            weight=2.0,
            fill=True,
            fill_color=category["color"],
            fill_opacity=0.90,
            popup=folium.Popup(popup_html, max_width=270),
        )
        
        # Hover tooltip (non-permanent to avoid overlapping clutter)
        marker.add_child(
            folium.Tooltip(f"<b>{city_name}</b>: {safe_aqi} AQI ({category['label']})", sticky=True)
        )
        marker.add_to(m)

    return m
