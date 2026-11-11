"""
AirSense — UI Components & Visualizations
File: dashboard/components/gauges.py
Week: 3

Renders:
  - CPCB-compliant AQI Gauges (Plotly Indicator)
  - 24-Hour Trend Line Charts with Area Glow
  - Multi-pollutant Breakdown Charts (PM2.5, PM10, NO2, CO, SO2, O3)
  - Color-coded Category Badges & Health Advisories
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
import pandas as pd
import plotly.graph_objects as go

IST = timezone(timedelta(hours=5, minutes=30))


# CPCB NAAQS AQI Classification Bands & Palette
AQI_LEVELS = [
    {
        "min": 0,
        "max": 50,
        "label": "Good",
        "color": "#10B981",       # Emerald Green
        "bg_color": "#D1FAE5",
        "text_color": "#065F46",
        "advisory": "Air quality is satisfactory and poses little or no health risk. Enjoy outdoor activities.",
    },
    {
        "min": 51,
        "max": 100,
        "label": "Satisfactory",
        "color": "#84CC16",       # Lime Green
        "bg_color": "#ECFCCB",
        "text_color": "#365314",
        "advisory": "Air quality is acceptable. Sensitive individuals may experience minor breathing discomfort.",
    },
    {
        "min": 101,
        "max": 200,
        "label": "Moderate",
        "color": "#F59E0B",       # Amber / Orange
        "bg_color": "#FEF3C7",
        "text_color": "#92400E",
        "advisory": "Breathing discomfort to people with lung disease, asthma, and heart conditions. Limit prolonged exertion.",
    },
    {
        "min": 201,
        "max": 300,
        "label": "Poor",
        "color": "#EF4444",       # Red
        "bg_color": "#FEE2E2",
        "text_color": "#991B1B",
        "advisory": "Breathing discomfort to most people on prolonged exposure. Wear N95 masks outdoors.",
    },
    {
        "min": 301,
        "max": 400,
        "label": "Very Poor",
        "color": "#8B5CF6",       # Purple
        "bg_color": "#EDE9FE",
        "text_color": "#5B21B6",
        "advisory": "Respiratory illness on prolonged exposure. Sensitive groups should remain indoors.",
    },
    {
        "min": 401,
        "max": 500,
        "label": "Severe",
        "color": "#7F1D1D",       # Deep Maroon
        "bg_color": "#FEE2E2",
        "text_color": "#450A0A",
        "advisory": "Affects healthy people and seriously impacts those with existing disease. Avoid all outdoor physical activity.",
    },
]


def get_aqi_category(aqi_val: float | None) -> dict[str, Any]:
    """Return category details, colors, and health guidelines for a given AQI."""
    if aqi_val is None or pd.isna(aqi_val):
        return {
            "label": "No Data",
            "color": "#9CA3AF",
            "bg_color": "#F3F4F6",
            "text_color": "#374151",
            "advisory": "Monitoring data currently unavailable for this station.",
        }

    val = float(aqi_val)
    for band in AQI_LEVELS:
        if band["min"] <= val <= band["max"]:
            return band

    if val > 500:
        return AQI_LEVELS[-1]

    return AQI_LEVELS[0]


def render_aqi_gauge(city_name: str, aqi_val: float | None) -> go.Figure:
    """Create a sleek, modern Plotly semicircular gauge meter."""
    category = get_aqi_category(aqi_val)
    safe_val = float(aqi_val) if aqi_val is not None and not pd.isna(aqi_val) else 0.0

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=safe_val,
            domain={"x": [0, 1], "y": [0, 1]},
            title={
                "text": f"<b>{city_name}</b><br><span style='font-size:14px;color:{category['color']}'>{category['label'].upper()}</span>",
                "font": {"size": 20, "color": "#1E293B"},
            },
            number={
                "font": {"size": 42, "color": category["color"], "family": "Inter, sans-serif"},
                "suffix": " AQI",
            },
            gauge={
                "axis": {"range": [0, 500], "tickwidth": 1, "tickcolor": "#94A3B8", "dtick": 100},
                "bar": {"color": category["color"], "thickness": 0.3},
                "bgcolor": "rgba(241, 245, 249, 0.6)",
                "borderwidth": 1,
                "bordercolor": "#E2E8F0",
                "steps": [
                    {"range": [0, 50], "color": "rgba(16, 185, 129, 0.15)"},
                    {"range": [50, 100], "color": "rgba(132, 204, 22, 0.15)"},
                    {"range": [100, 200], "color": "rgba(245, 158, 11, 0.15)"},
                    {"range": [200, 300], "color": "rgba(239, 68, 68, 0.15)"},
                    {"range": [300, 400], "color": "rgba(139, 92, 246, 0.15)"},
                    {"range": [400, 500], "color": "rgba(127, 29, 29, 0.2)"},
                ],
                "threshold": {
                    "line": {"color": "#DC2626", "width": 3},
                    "thickness": 0.8,
                    "value": 200,  # Alert threshold
                },
            },
        )
    )

    fig.update_layout(
        height=205,
        margin=dict(l=15, r=15, t=35, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, system-ui, sans-serif"},
    )
    return fig


def render_pollutants_bar(row: pd.Series) -> go.Figure:
    """Render a horizontal bar breakdown of individual pollutants."""
    co_val = row.get("co")
    if co_val is not None and not pd.isna(co_val) and co_val > 50.0:
        co_val = round(co_val / 1000.0, 3)

    pollutants = {
        "PM2.5 (µg/m³)": row.get("pm25"),
        "PM10 (µg/m³)": row.get("pm10"),
        "NO2 (µg/m³)": row.get("no2"),
        "CO (mg/m³)": co_val,
        "SO2 (µg/m³)": row.get("so2"),
        "O3 (µg/m³)": row.get("o3"),
    }

    labels = []
    values = []
    colors = []

    for name, val in pollutants.items():
        if val is not None and not pd.isna(val):
            labels.append(name)
            values.append(float(val))
            # Dynamic color accent
            if "PM2.5" in name:
                colors.append("#EF4444" if float(val) > 60 else "#10B981")
            elif "PM10" in name:
                colors.append("#F59E0B" if float(val) > 100 else "#10B981")
            else:
                colors.append("#3B82F6")

    if not labels:
        # Placeholder if all are None
        labels = ["No granular metrics"]
        values = [0]
        colors = ["#94A3B8"]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker=dict(color=colors, cornerradius=4),
            text=[f"{v:.1f}" if v > 0 else "-" for v in values],
            textposition="auto",
        )
    )

    fig.update_layout(
        height=205,
        margin=dict(l=10, r=20, t=15, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248, 250, 252, 0.6)",
        xaxis=dict(title="", showgrid=True, gridcolor="#E2E8F0"),
        yaxis=dict(title="", automargin=True),
        font={"family": "Inter, system-ui, sans-serif", "size": 11},
    )
    return fig


def render_history_trend(history_df: pd.DataFrame, city_name: str) -> go.Figure:
    """Plot an interactive 24-hour historical line chart with area fill in Indian Standard Time (IST)."""
    if history_df.empty or "time" not in history_df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="Accumulating time-series data... (runs hourly via pipeline)",
            showarrow=False,
            font=dict(size=14, color="#64748B"),
        )
        fig.update_layout(height=270, paper_bgcolor="rgba(0,0,0,0)")
        return fig

    # Focus strictly on the contiguous 24-hour window relative to the latest reading
    df = history_df.copy()
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values(by="time")
    latest_time = df["time"].iloc[-1]
    df = df[df["time"] >= (latest_time - pd.Timedelta(hours=28))].reset_index(drop=True)

    # Convert timestamps to Indian Standard Time (IST, UTC+5:30) for local display
    df["time_ist"] = df["time"].apply(
        lambda t: t.astimezone(IST) if pd.notna(t) and getattr(t, "tzinfo", None) is not None else (t + pd.Timedelta(hours=5, minutes=30))
    )

    fig = go.Figure()

    # CPCB AQI Line
    fig.add_trace(
        go.Scatter(
            x=df["time_ist"],
            y=df["aqi"],
            mode="lines+markers",
            name="CPCB NAQI",
            line=dict(color="#3B82F6", width=2.5, shape="spline"),
            marker=dict(size=6, color="#1D4ED8", symbol="circle"),
            fill="tozeroy",
            fillcolor="rgba(59, 130, 246, 0.08)",
            connectgaps=False,
            hovertemplate="<b>%{x|%b %d, %I:%M %p} IST</b><br>CPCB NAQI: <b>%{y:.0f}</b><extra></extra>",
        )
    )

    # Optional PM2.5 trace if available
    if "pm25" in df.columns and df["pm25"].notna().any():
        fig.add_trace(
            go.Scatter(
                x=df["time_ist"],
                y=df["pm25"],
                mode="lines",
                name="PM2.5 (µg/m³)",
                line=dict(color="#EF4444", width=1.5, dash="dot"),
                connectgaps=False,
                hovertemplate="PM2.5: <b>%{y:.1f} µg/m³</b><extra></extra>",
            )
        )

    # CPCB Guideline Reference lines
    fig.add_hline(y=50, line_dash="dash", line_color="#10B981", annotation_text="Good (50)", annotation_position="top right")
    fig.add_hline(y=100, line_dash="dash", line_color="#F59E0B", annotation_text="Moderate (100)", annotation_position="top right")
    fig.add_hline(y=200, line_dash="dash", line_color="#EF4444", annotation_text="Poor (200)", annotation_position="top right")

    fig.update_layout(
        title=dict(
            text=f"<b>24-Hour Air Quality Profile (IST) — {city_name}</b>",
            font=dict(size=14, color="#1E293B"),
        ),
        height=270,
        margin=dict(l=15, r=15, t=35, b=15),
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248, 250, 252, 0.6)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(
            title=dict(text="Time (Indian Standard Time — IST)", font=dict(size=11, color="#64748B")),
            showgrid=True,
            gridcolor="#E2E8F0",
            tickformat="%I:%M %p",
        ),
        yaxis=dict(title="Index Value (CPCB NAQI)", showgrid=True, gridcolor="#E2E8F0", zeroline=False),
        font={"family": "Inter, system-ui, sans-serif"},
    )
    return fig
