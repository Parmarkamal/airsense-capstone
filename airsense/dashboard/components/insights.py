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


# ── Phase 9: Business Intelligence & Executive Analytics ──────────────────────

WHO_PM25_24H_LIMIT = 15.0  # WHO 2021 Global Air Quality Guidelines (µg/m³)


def compute_wow_change(history_df: pd.DataFrame) -> float | None:
    """
    Compute Week-over-Week (WoW) percentage change in 7-day rolling average AQI.

    Returns the % change between the most recent 7-day average and the prior
    7-day average. Returns None if insufficient data (<14 days).
    """
    if history_df.empty or "aqi" not in history_df.columns:
        return None

    df = history_df.copy()
    df["time"] = pd.to_datetime(df["time"], utc=True)
    df = df.dropna(subset=["aqi"]).sort_values("time")

    if len(df) < 14:
        return None

    # Daily average AQI
    df["date"] = df["time"].dt.date
    daily_avg = df.groupby("date")["aqi"].mean().sort_index()

    if len(daily_avg) < 14:
        return None

    # Current week = last 7 days, Prior week = 7 days before that
    current_week = daily_avg.tail(7).mean()
    prior_week = daily_avg.iloc[-14:-7].mean()

    if prior_week == 0:
        return None

    return round(((current_week - prior_week) / prior_week) * 100, 1)


def render_wow_trend_chart(history_df: pd.DataFrame, city_name: str) -> go.Figure:
    """
    Render a Week-over-Week AQI trend chart showing the 7-day rolling average.

    The chart displays the rolling 7-day mean AQI over time, with the WoW %
    change annotated prominently. This is a key executive KPI for demonstrating
    whether air quality is improving or deteriorating week-over-week.
    """
    if history_df.empty or "aqi" not in history_df.columns:
        fig = go.Figure()
        fig.add_annotation(text="Insufficient historical data for WoW trend", showarrow=False)
        fig.update_layout(height=320, paper_bgcolor="rgba(0,0,0,0)")
        return fig

    df = history_df.copy()
    df["time"] = pd.to_datetime(df["time"], utc=True)
    df = df.dropna(subset=["aqi"]).sort_values("time")

    # Compute daily averages
    df["date"] = df["time"].dt.date
    daily_avg = df.groupby("date")["aqi"].mean().reset_index()
    daily_avg["date"] = pd.to_datetime(daily_avg["date"])
    daily_avg["rolling_7d"] = daily_avg["aqi"].rolling(7, min_periods=1).mean()

    # WoW % change
    wow_pct = compute_wow_change(history_df)

    fig = go.Figure()

    # 7-day rolling average
    fig.add_trace(
        go.Scatter(
            x=daily_avg["date"],
            y=daily_avg["rolling_7d"],
            mode="lines+markers",
            name="7-Day Rolling Avg AQI",
            line=dict(color="#2563EB", width=3),
            marker=dict(size=5, color="#1D4ED8"),
            hovertemplate="%{x|%b %d}<br>7-Day Avg: <b>%{y:.1f}</b><extra></extra>",
        )
    )

    # WoW annotation
    if wow_pct is not None:
        arrow = "↗" if wow_pct > 0 else ("↘" if wow_pct < 0 else "➡")
        color = "#DC2626" if wow_pct > 0 else ("#16A34A" if wow_pct < 0 else "#64748B")
        fig.add_annotation(
            text=f"<b>WoW: {arrow} {abs(wow_pct):.1f}%</b>",
            xref="paper", x=0.98, yref="paper", y=0.95,
            showarrow=False,
            font=dict(size=14, color=color, family="Inter, system-ui, sans-serif"),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor=color,
            borderwidth=1,
            borderpad=4,
        )

    fig.update_layout(
        title=dict(
            text=f"<b>Week-over-Week AQI Trend — {city_name}</b>",
            font=dict(size=15, color="#1E293B"),
            x=0, y=0.96,
        ),
        xaxis=dict(title="", showgrid=True, gridcolor="#E2E8F0"),
        yaxis=dict(title="7-Day Rolling Avg AQI", showgrid=True, gridcolor="#E2E8F0"),
        height=320,
        margin=dict(l=10, r=20, t=45, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248, 250, 252, 0.6)",
        font={"family": "Inter, system-ui, sans-serif"},
        hovermode="x unified",
    )
    return fig


def render_city_ranking_matrix(
    df_latest: pd.DataFrame,
    history_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build an executive city pollution ranking matrix.

    Returns a sortable DataFrame with columns:
      City, Current AQI, CPCB Category, Peak Daily AQI, Avg PM2.5,
      Combustion Ratio, WHO Exceedance Hours, WoW % Change

    WHO 24h PM2.5 limit = 15 µg/m³ (WHO 2021 Global Air Quality Guidelines).
    """
    if df_latest.empty:
        return pd.DataFrame()

    rows = []
    for _, city_row in df_latest.iterrows():
        city = city_row.get("city", "")
        city_name = city_row.get("city_display_name", city)
        current_aqi = city_row.get("aqi")
        category = get_aqi_category(current_aqi)["label"] if pd.notna(current_aqi) else "N/A"

        # Peak daily AQI from history
        peak_aqi = current_aqi if pd.notna(current_aqi) else 0
        avg_pm25 = city_row.get("pm25")

        # Compute from history if available
        city_history = history_df[history_df["city"] == city] if not history_df.empty and "city" in history_df.columns else pd.DataFrame()
        if not city_history.empty:
            city_history = city_history.copy()
            city_history["time"] = pd.to_datetime(city_history["time"], utc=True)
            city_history["date"] = city_history["time"].dt.date
            daily_max = city_history.groupby("date")["aqi"].max()
            if not daily_max.empty:
                peak_aqi = float(daily_max.max())
            pm25_vals = city_history["pm25"].dropna()
            if not pm25_vals.empty:
                avg_pm25 = float(pm25_vals.mean())

        # Combustion ratio
        pm25 = city_row.get("pm25")
        pm10 = city_row.get("pm10")
        combustion_ratio = round(float(pm25) / float(pm10), 2) if pd.notna(pm25) and pd.notna(pm10) and float(pm10) > 0 else None

        # WHO exceedance hours (PM2.5 > 15 µg/m³)
        who_exceed = 0
        if not city_history.empty and "pm25" in city_history.columns:
            who_exceed = int((city_history["pm25"].dropna() > WHO_PM25_24H_LIMIT).sum())

        # WoW % change
        wow_pct = compute_wow_change(city_history) if not city_history.empty else None

        rows.append({
            "City": city_name,
            "Current AQI": round(float(current_aqi)) if pd.notna(current_aqi) else None,
            "CPCB Category": category,
            "Peak Daily AQI": round(peak_aqi) if peak_aqi else None,
            "Avg PM2.5 (µg/m³)": round(float(avg_pm25), 1) if avg_pm25 is not None else None,
            "Combustion Ratio": combustion_ratio,
            "WHO Exceedance Hours": who_exceed,
            "WoW % Change": wow_pct,
        })

    matrix = pd.DataFrame(rows)
    # Sort by Current AQI descending (most polluted first)
    if "Current AQI" in matrix.columns and not matrix["Current AQI"].isna().all():
        matrix = matrix.sort_values("Current AQI", ascending=False).reset_index(drop=True)
    return matrix


def render_executive_scorecard(
    df_latest: pd.DataFrame,
    history_df: pd.DataFrame,
) -> list[dict]:
    """
    Compute executive KPI scorecard metrics for the BI dashboard.

    Returns a list of KPI dicts, each with 'label', 'value', 'delta', and 'help'
    keys suitable for st.metric() rendering.
    """
    if df_latest.empty:
        return []

    valid_aqi = df_latest.dropna(subset=["aqi"])
    if valid_aqi.empty:
        return []

    fleet_avg = round(float(valid_aqi["aqi"].mean()), 0)
    most_polluted = valid_aqi.loc[valid_aqi["aqi"].idxmax()]
    cleanest = valid_aqi.loc[valid_aqi["aqi"].idxmin()]

    # Combustion ratio average
    ratio_vals = []
    for _, row in valid_aqi.iterrows():
        pm25, pm10 = row.get("pm25"), row.get("pm10")
        if pd.notna(pm25) and pd.notna(pm10) and float(pm10) > 0:
            ratio_vals.append(float(pm25) / float(pm10))
    avg_ratio = round(sum(ratio_vals) / len(ratio_vals), 2) if ratio_vals else None

    # Total WHO exceedance hours
    who_exceed = 0
    if not history_df.empty and "pm25" in history_df.columns:
        who_exceed = int((history_df["pm25"].dropna() > WHO_PM25_24H_LIMIT).sum())

    # Fleet WoW
    fleet_wow = compute_wow_change(history_df) if not history_df.empty else None

    return [
        {
            "label": "Fleet Avg AQI",
            "value": f"{fleet_avg:.0f}",
            "delta": f"{fleet_wow:+.1f}% WoW" if fleet_wow is not None else None,
            "help": "Average AQI across all monitored cities",
        },
        {
            "label": "Most Polluted",
            "value": f"{most_polluted.get('city_display_name', most_polluted.get('city', 'Unknown')).title()}",
            "delta": f"{most_polluted['aqi']:.0f} AQI",
            "help": "City with highest current AQI",
        },
        {
            "label": "Cleanest City",
            "value": f"{cleanest.get('city_display_name', cleanest.get('city', 'Unknown')).title()}",
            "delta": f"{cleanest['aqi']:.0f} AQI",
            "help": "City with lowest current AQI",
        },
        {
            "label": "Avg Combustion Ratio",
            "value": f"{avg_ratio:.2f}" if avg_ratio is not None else "N/A",
            "delta": "Combustion" if avg_ratio and avg_ratio >= 0.6 else ("Dust" if avg_ratio and avg_ratio <= 0.4 else "Mixed"),
            "help": "PM2.5/PM10 ratio: >0.6 combustion, <0.4 dust",
        },
        {
            "label": "WHO Exceedance Hours",
            "value": f"{who_exceed}",
            "delta": f"> {WHO_PM25_24H_LIMIT:.0f} µg/m³" if who_exceed > 0 else "Within limits",
            "help": f"Hours where PM2.5 exceeds WHO limit ({WHO_PM25_24H_LIMIT:.0f} µg/m³)",
        },
    ]
