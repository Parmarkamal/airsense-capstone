"""
AirSense — Exploratory Data Analysis & Insights Visualizations
File: dashboard/components/insights.py
Week: 4 Deliverable

Features:
  1. Ranked Urban AQI Comparison (Cleanest to Most Polluted)
  2. Diurnal (Hourly) Air Quality Rhythm (Hour 0 to 23)
  3. Particulate Ratio Analysis (PM2.5 / PM10 Ratio Combustion vs Dust Diagnostic)
  4. Statistical Anomaly & Spike Detector (Z-score Analysis)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dashboard.components.gauges import get_aqi_category


def render_city_ranking_chart(df_latest: pd.DataFrame) -> go.Figure:
    """Render a ranked horizontal bar chart of monitored cities by AQI with clean outside labels."""
    if df_latest.empty:
        fig = go.Figure()
        fig.add_annotation(text="No city data available", showarrow=False)
        return fig

    # Sort cities by AQI ascending (Cleanest at top)
    df_sorted = df_latest.dropna(subset=["aqi"]).sort_values("aqi", ascending=True)

    colors = [get_aqi_category(val)["color"] for val in df_sorted["aqi"]]
    categories = [get_aqi_category(val)["label"] for val in df_sorted["aqi"]]
    max_val = df_sorted["aqi"].max() if not df_sorted.empty else 300

    fig = go.Figure(
        go.Bar(
            x=df_sorted["aqi"],
            y=df_sorted["city_display_name"],
            orientation="h",
            marker=dict(color=colors, cornerradius=6),
            text=[f" <b>{val:.0f}</b> ({cat})" for val, cat in zip(df_sorted["aqi"], categories)],
            textposition="outside",
            cliponaxis=False,
            textfont=dict(color="#1E293B", size=12, family="Inter, system-ui, sans-serif"),
            hovertemplate="<b>%{y}</b><br>AQI: <b>%{x:.0f}</b> (%{text})<extra></extra>",
        )
    )

    # Clean dotted benchmark threshold lines
    fig.add_vline(x=50, line_dash="dot", line_color="#10B981", line_width=1.5)
    fig.add_vline(x=100, line_dash="dot", line_color="#F59E0B", line_width=1.5)
    fig.add_vline(x=200, line_dash="dot", line_color="#EF4444", line_width=1.5)

    fig.update_layout(
        title=dict(
            text="<b>Urban Air Quality League</b> (Cleanest ➔ Most Polluted)",
            font=dict(size=15, color="#1E293B"),
            x=0,
            y=0.96,
        ),
        height=320,
        margin=dict(l=10, r=60, t=45, b=25),
        xaxis=dict(
            title="Air Quality Index (AQI)",
            range=[0, max_val * 1.32],
            showgrid=True,
            gridcolor="#E2E8F0",
        ),
        yaxis=dict(title="", automargin=True),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248, 250, 252, 0.6)",
        font={"family": "Inter, system-ui, sans-serif"},
    )
    return fig


def render_pm_ratio_chart(df_latest: pd.DataFrame) -> go.Figure:
    """
    Calculate and visualize the PM2.5 / PM10 ratio.
    - Ratio >= 0.6: Fine Combustion / Tailpipe / Smog dominance
    - Ratio <= 0.4: Mechanical / Construction / Road Dust dominance
    """
    df_valid = df_latest.dropna(subset=["pm25", "pm10"]).copy()
    df_valid = df_valid[df_valid["pm10"] > 0]

    if df_valid.empty:
        fig = go.Figure()
        fig.add_annotation(text="Granular PM metrics currently accumulating...", showarrow=False)
        fig.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)")
        return fig

    df_valid["pm_ratio"] = (df_valid["pm25"] / df_valid["pm10"]).clip(0, 1.0)
    max_ratio = df_valid["pm_ratio"].max() if not df_valid.empty else 1.0

    # Color by diagnosis
    colors = [
        "#EF4444" if r >= 0.6 else ("#F59E0B" if r >= 0.4 else "#3B82F6")
        for r in df_valid["pm_ratio"]
    ]

    fig = go.Figure(
        go.Bar(
            x=df_valid["city_display_name"],
            y=df_valid["pm_ratio"],
            marker=dict(color=colors, cornerradius=6),
            text=[f"<b>{r:.2f}</b>" for r in df_valid["pm_ratio"]],
            textposition="outside",
            cliponaxis=False,
            textfont=dict(color="#1E293B", size=12),
            hovertemplate="<b>%{x}</b><br>PM2.5/PM10 Ratio: <b>%{y:.2f}</b><extra></extra>",
        )
    )

    # Threshold indicator lines
    fig.add_hline(
        y=0.6,
        line_dash="dot",
        line_color="#DC2626",
        line_width=1.5,
    )
    fig.add_hline(
        y=0.4,
        line_dash="dot",
        line_color="#2563EB",
        line_width=1.5,
    )

    fig.update_layout(
        title=dict(
            text="<b>Particulate Diagnostic: PM2.5 / PM10 Ratio</b>",
            font=dict(size=15, color="#1E293B"),
            x=0,
            y=0.96,
        ),
        yaxis=dict(
            title="PM2.5 to PM10 Ratio",
            range=[0, max(1.15, max_ratio * 1.25)],
            showgrid=True,
            gridcolor="#E2E8F0",
        ),
        xaxis=dict(title=""),
        height=320,
        margin=dict(l=10, r=20, t=45, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248, 250, 252, 0.6)",
        font={"family": "Inter, system-ui, sans-serif"},
    )
    return fig


def render_diurnal_pattern_chart(history_df: pd.DataFrame) -> go.Figure:
    """
    Plot diurnal (hourly) pattern of air quality.
    Shows diurnal rhythm: morning traffic peak, afternoon solar dispersion, evening peak.
    """
    if history_df.empty or "time" not in history_df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="Accumulating hourly data from Kafka stream...",
            showarrow=False,
            font=dict(size=14, color="#64748B"),
        )
        fig.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)")
        return fig

    df_copy = history_df.copy()
    df_copy["hour"] = pd.to_datetime(df_copy["time"]).dt.hour

    hourly = df_copy.groupby("hour")["aqi"].agg(["mean", "min", "max"]).reset_index()

    fig = go.Figure()

    # Min-Max shaded envelope
    fig.add_trace(
        go.Scatter(
            x=list(hourly["hour"]) + list(hourly["hour"][::-1]),
            y=list(hourly["max"]) + list(hourly["min"][::-1]),
            fill="toself",
            fillcolor="rgba(59, 130, 246, 0.12)",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            showlegend=False,
            name="Range",
        )
    )

    # Average Diurnal Curve
    fig.add_trace(
        go.Scatter(
            x=hourly["hour"],
            y=hourly["mean"],
            mode="lines+markers",
            name="Hourly Mean AQI",
            line=dict(color="#2563EB", width=3, shape="spline"),
            marker=dict(size=8, color="#1E40AF"),
            hovertemplate="Hour %{x}:00<br>Average AQI: <b>%{y:.1f}</b><extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(
            text="<b>Diurnal (24-Hour) Pollution Rhythm</b>",
            font=dict(size=15, color="#1E293B"),
            x=0,
            y=0.96,
        ),
        xaxis=dict(
            title="Hour of the Day (00:00 - 23:00)",
            tickmode="linear",
            tick0=0,
            dtick=2,
            showgrid=True,
            gridcolor="#E2E8F0",
        ),
        yaxis=dict(title="Average AQI", showgrid=True, gridcolor="#E2E8F0"),
        height=320,
        margin=dict(l=10, r=20, t=45, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248, 250, 252, 0.6)",
        font={"family": "Inter, system-ui, sans-serif"},
    )
    return fig


def detect_zscore_anomalies(df_latest: pd.DataFrame) -> list[dict]:
    """
    Detect statistical outliers across cities using Z-score: Z = (X - μ) / σ.
    Flags readings that deviate significantly from current cross-city baseline.
    """
    anomalies = []
    valid_aqi = df_latest["aqi"].dropna()
    if len(valid_aqi) < 3:
        return anomalies

    mean_aqi = valid_aqi.mean()
    std_aqi = valid_aqi.std()

    if std_aqi == 0:
        return anomalies

    for _, row in df_latest.dropna(subset=["aqi"]).iterrows():
        z = (row["aqi"] - mean_aqi) / std_aqi
        if abs(z) >= 1.5:  # Sensitive spike threshold for 6 cities
            anomalies.append({
                "city": row["city_display_name"],
                "aqi": row["aqi"],
                "z_score": round(z, 2),
                "type": "Elevated Spike" if z > 0 else "Unusually Clean",
                "severity": "High" if abs(z) >= 2.0 else "Moderate",
            })
    return anomalies
