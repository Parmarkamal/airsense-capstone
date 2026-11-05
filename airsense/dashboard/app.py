"""
AirSense — Real-Time Air Quality & Environmental Intelligence Platform
File: dashboard/app.py
Weeks: 3 & 4 Deliverables

Views (Sidebar Navigable):
  1. 🏠 Live Telemetry: KPI Cards, CPCB Gauge, Pollutant Concentrations, 24h Trend
  2. 🗺️ India Air Quality Map: Interactive Folium Geographic Bubble Map with CPCB Pins
  3. 📊 EDA & Analytical Insights: Ranked League, PM2.5/PM10 Diagnostics, Diurnal Rhythm, Z-score Outliers
"""

from __future__ import annotations

import os
import sys
import types
from pathlib import Path
from datetime import datetime, timezone

# Windows runtime guard: prevent chromadb unused ONNX import crash
os.environ["ANONYMIZED_TELEMETRY"] = "False"
if "onnxruntime" not in sys.modules:
    try:
        import onnxruntime  # noqa: F401
    except Exception:
        sys.modules["onnxruntime"] = types.ModuleType("onnxruntime")

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
from streamlit_folium import st_folium

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

from common.config import load_settings
from consumer.db import create_db_engine
from dashboard.data_access import (
    get_latest_readings_all_cities,
    get_city_history,
    get_pipeline_stats,
    get_city_forecast,
    is_replay_mode_active,
    get_city_rolling_cpcb_aqi,
    get_provenance_badge,
)
from dashboard.components.gauges import (
    get_aqi_category,
    render_aqi_gauge,
    render_pollutants_bar,
    render_history_trend,
)
from dashboard.components.map_view import create_india_air_map
from dashboard.components.insights import (
    render_city_ranking_chart,
    render_diurnal_pattern_chart,
    render_pm_ratio_chart,
    detect_zscore_anomalies,
    render_wow_trend_chart,
    render_city_ranking_matrix,
    render_executive_scorecard,
    render_standards_comparison_chart,
)
from dashboard.components.forecast_view import (
    render_combined_forecast_chart,
    load_model_metadata,
    render_feature_importance_chart,
    render_benchmark_comparison_chart,
    get_benchmark_comparison_data,
)
from dashboard.components.ai_advisor_view import render_ai_advisor_view
from dashboard.components.health_view import render_pipeline_health_tab

# ── Page Configuration ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AirSense | Live Urban AQI Intelligence",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS for Modern Aesthetics ───────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, sans-serif;
    }

    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 1.5rem !important;
        max-width: 98% !important;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        color: #F8FAFC;
        padding: 12px 20px;
        border-radius: 10px;
        margin-bottom: 8px;
        box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.2);
    }
    
    .disclaimer-banner {
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        color: #92400E;
        padding: 6px 14px;
        border-radius: 6px;
        font-size: 11.5px;
        margin-bottom: 8px;
        line-height: 1.35;
    }

    .replay-banner {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        border: 2px solid #F59E0B;
        color: #78350F;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 12px;
        margin-bottom: 8px;
        font-weight: 600;
        text-align: center;
        box-shadow: 0 2px 6px rgba(245, 158, 11, 0.2);
    }

    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 8px 4px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
    }
    
    .badge {
        display: inline-block;
        padding: 2px 7px;
        border-radius: 9999px;
        font-size: 9.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .anomaly-card {
        background-color: #FFF1F2;
        border-left: 4px solid #E11D48;
        padding: 8px 12px;
        border-radius: 6px;
        margin-bottom: 8px;
        font-size: 12px;
        color: #881337;
    }
</style>
""", unsafe_allow_html=True)


# ── Database Connection Cache ──────────────────────────────────────────────────
@st.cache_resource
def get_engine():
    settings = load_settings()
    return create_db_engine(settings)


def main():
    try:
        engine = get_engine()
    except Exception as exc:
        st.error(f"⚠️ Cannot connect to TimescaleDB: {exc}")
        st.info("Make sure Docker container `airsense_timescaledb` is running on port 5433.")
        return

    # ── Sidebar Controls & Navigation ──────────────────────────────────────────
    with st.sidebar:
        st.title("🌬️ AirSense Controls")
        
        st.markdown("### 🧭 Select View")
        selected_view = st.radio(
            "Navigation Menu:",
            options=[
                "🏠 Live Telemetry",
                "🗺️ India Air Quality Map",
                "📈 Business Intelligence & Analytics",
                "🔮 48-Hour AQI Forecast",
                "🤖 AI Health Advisor",
                "🩺 Pipeline Health",
            ],
            index=0,
            label_visibility="collapsed",
        )
        
        st.markdown("---")
        
        # Auto-refresh setup
        auto_refresh = st.checkbox("Auto-refresh data", value=True)
        if auto_refresh:
            refresh_interval = st.selectbox(
                "Refresh rate",
                options=[30, 60, 120, 300],
                index=1,
                format_func=lambda s: f"{s} seconds",
            )
            if st_autorefresh is not None:
                st_autorefresh(interval=refresh_interval * 1000, key="airsense_autorefresh")
            st.caption(f"⏱️ Dashboard refreshes automatically every {refresh_interval}s")

        if st.button("🔄 Refresh Now", use_container_width=True):
            st.rerun()

        st.markdown("---")
        
        # Pipeline Health
        st.subheader("📡 Streaming Pipeline")
        stats = get_pipeline_stats(engine)
        st.metric("Total Events Ingested", f"{stats['total_readings']:,}")
        st.metric("Validation Errors", f"{stats['total_errors']}")
        
        if stats["latest_fetch"]:
            last_time = stats["latest_fetch"].strftime("%Y-%m-%d %H:%M:%S UTC")
            st.caption(f"Last Ingestion: **{last_time}**")
        else:
            st.caption("Awaiting first telemetry batch...")

        st.markdown("---")
        st.caption("🏗️ **Architecture:**")
        st.caption("• Broker: Apache Kafka `localhost:9092`")
        st.caption("• Storage: TimescaleDB `localhost:5433`")
        st.caption("• Standard: CPCB NAAQS (India)")

    # ── Main Header ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="main-header">
        <h2 style="margin:0; font-size: 22px; font-weight:800; letter-spacing: -0.02em;">
            🌬️ AirSense — Real-Time Environmental Intelligence
        </h2>
        <p style="margin:3px 0 0 0; color: #94A3B8; font-size: 12.5px;">
            MSc Business Intelligence & Analytics Capstone • Live Kafka Streaming & TimescaleDB Engine
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Medical & Advisory Disclaimer ──────────────────────────────────────────
    st.markdown("""
    <div class="disclaimer-banner">
        ⚠️ <b>Health Advisory Notice:</b> Air quality index readings and health guidelines are derived from official 
        CPCB NAAQS and WHO guidelines for educational and analytical purposes. This platform does not provide medical diagnoses.
    </div>
    """, unsafe_allow_html=True)

    # ── Fetch Live Data ────────────────────────────────────────────────────────
    df_latest = get_latest_readings_all_cities(engine)

    if df_latest.empty:
        st.warning("No data found in TimescaleDB. Please run `python ingestion/fetch_aqi.py` to ingest live records.")
        return

    # ── Phase 8: Replay Mode Detection Banner ───────────────────────────────────
    if is_replay_mode_active(df_latest):
        st.markdown("""
        <div class="replay-banner">
            📼 <b>REPLAY MODE ACTIVE:</b> Displaying simulated historical sensor stream
            (Offline Resilience Mode) — Internet/WAQI API unavailable.
        </div>
        """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # VIEW 1: LIVE TELEMETRY
    # ═══════════════════════════════════════════════════════════════════════════
    if selected_view == "🏠 Live Telemetry":
        st.markdown("<h4 style='margin-top:0; margin-bottom:8px;'>🏙️ Monitored Urban Hubs — Current Status</h4>", unsafe_allow_html=True)
        
        city_names = df_latest["city_display_name"].tolist()
        city_slugs = df_latest["city"].tolist()
        slug_map = dict(zip(city_names, city_slugs))

        cols = st.columns(len(df_latest))
        for idx, (_, row) in enumerate(df_latest.iterrows()):
            # Dual AQI display: show CPCB NAQI if computed, along with source indicator
            display_aqi = row.get("cpcb_aqi") if pd.notna(row.get("cpcb_aqi")) else row.get("aqi")
            category = get_aqi_category(display_aqi)
            freshness_label = row.get("freshness_label", "🟢 Live (<1h old)")
            freshness_color = row.get("freshness_color", "green")
            age_hours = row.get("data_age_hours")
            prov = get_provenance_badge(row)
            prom = row.get("prominent_pollutant") or "PM2.5"
            with cols[idx]:
                st.markdown(f"""
                <div class="kpi-card" style="border-top: 3px solid {prov.get('border_color', '#3B82F6')};">
                    <div style="font-weight:700; font-size:13px; color:#1E293B; margin-bottom:1px;">
                        {row['city_display_name']}
                    </div>
                    <div style="font-size:26px; font-weight:800; color:{category['color']}; margin:1px 0;">
                        {int(display_aqi) if pd.notna(display_aqi) else '--'}
                    </div>
                    <span class="badge" style="background-color:{category['bg_color']}; color:{category['text_color']};">
                        {category['label']}
                    </span>
                    <div style="margin-top:4px; font-size:10px; font-weight:600; color:#475569;">
                        Key: <b>{prom}</b>
                    </div>
                    <div style="margin-top:2px; font-size:9.5px; font-weight:600; color:{freshness_color};">
                        {freshness_label}
                    </div>
                    <div style="margin-top:2px; font-size:8.5px; color:#64748B; line-height:1.1;">
                        {prov['badge']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Deep-dive city selector
        col_sel, col_space = st.columns([1, 2])
        with col_sel:
            selected_display = st.selectbox(
                "Select City to Inspect:",
                options=city_names,
                index=0,
            )
        selected_slug = slug_map[selected_display]
        city_data = df_latest[df_latest["city"] == selected_slug].iloc[0]
        rolling_cpcb = get_city_rolling_cpcb_aqi(engine, selected_slug)
        prov_info = get_provenance_badge(city_data)

        # Dual AQI & Provenance Banner
        rolling_aqi_str = f"<b>{rolling_cpcb['aqi']}</b> ({rolling_cpcb['category']})" if rolling_cpcb.get("aqi") else "Averaging..."
        prom_str = rolling_cpcb.get("prominent_pollutant") or city_data.get("prominent_pollutant") or "PM2.5"
        st.markdown(f"""
        <div style="background:#1E293B; border-radius:8px; padding:8px 14px; margin-bottom:8px; border:1px solid #334155; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; font-size:12px; color:#F8FAFC;">
            <div>
                🏛️ <b style="color:#F8FAFC;">Official CPCB NAQI 24h Rolling Standard:</b> <span style="color:#38BDF8;">{rolling_aqi_str}</span> 
                &nbsp;|&nbsp; Prominent: <span style="background:#334155; color:#F8FAFC; padding:2px 6px; border-radius:4px; font-weight:600;">{prom_str}</span>
                <span style="font-size:11px; color:#94A3B8; margin-left:6px;">(Completeness: {rolling_cpcb.get('valid_hours', 24)}/24h)</span>
            </div>
            <div style="font-size:11px; color:#CBD5E1;">
                {prov_info['badge']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Gauge & Pollutants Breakdown
        c_left, c_right = st.columns([1, 1])

        with c_left:
            st.markdown(f"<h5 style='margin-bottom:2px;'>🎯 1-Hour Indicative AQI Gauge: {selected_display}</h5>", unsafe_allow_html=True)
            disp_gauge_aqi = city_data.get("cpcb_aqi") if pd.notna(city_data.get("cpcb_aqi")) else city_data["aqi"]
            gauge_fig = render_aqi_gauge(selected_display, disp_gauge_aqi)
            st.plotly_chart(gauge_fig, use_container_width=True, config={"displayModeBar": False})

            # Health recommendation card
            cat_obj = get_aqi_category(disp_gauge_aqi)
            st.markdown(f"""
            <div style="background-color:{cat_obj['bg_color']}; border-left: 4px solid {cat_obj['color']}; padding: 8px 12px; border-radius: 6px; margin-top: 4px;">
                <div style="font-weight:700; color:{cat_obj['text_color']}; font-size:12px; margin-bottom:2px;">
                    Health Advisory — {cat_obj['label']} Air Quality
                </div>
                <div style="color:{cat_obj['text_color']}; font-size:11.5px; line-height:1.4;">
                    {cat_obj['advisory']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c_right:
            st.markdown("<h5 style='margin-bottom:2px;'>🔬 Granular Pollutant Concentrations</h5>", unsafe_allow_html=True)
            bar_fig = render_pollutants_bar(city_data)
            st.plotly_chart(bar_fig, use_container_width=True, config={"displayModeBar": False})
            st.caption(f"📍 **Telemetry Provenance:** {prov_info['badge']} — {prov_info['tooltip']}. Calculation: {city_data.get('calculation_method', 'CPCB NAQI 2014')}.")

        # 24-Hour Trend Visualizer
        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)
        st.markdown(f"<h5 style='margin-bottom:2px;'>📈 24-Hour Temporal Trend — {selected_display}</h5>", unsafe_allow_html=True)
        history_df = get_city_history(engine, selected_slug, limit=48)
        trend_fig = render_history_trend(history_df, selected_display)
        st.plotly_chart(trend_fig, use_container_width=True, config={"displayModeBar": False})

        with st.expander(f"🔍 View Raw Telemetry Records for {selected_display}"):
            if not history_df.empty:
                st.dataframe(
                    history_df.style.format({
                        "aqi": "{:.1f}",
                        "pm25": "{:.1f}",
                        "pm10": "{:.1f}",
                        "no2": "{:.1f}",
                        "co": "{:.1f}",
                        "so2": "{:.1f}",
                        "o3": "{:.1f}",
                    }),
                    use_container_width=True,
                )
            else:
                st.info("No historical records logged yet.")

    # ═══════════════════════════════════════════════════════════════════════════
    # VIEW 2: INDIA AIR QUALITY MAP
    # ═══════════════════════════════════════════════════════════════════════════
    elif selected_view == "🗺️ India Air Quality Map":
        st.subheader("🗺️ Geographic Air Quality Index Across India")
        st.markdown(
            "Interactive geospatial visualization of monitored urban centers. "
            "Marker colors correspond to **CPCB NAAQS categories**; bubble sizes scale with AQI severity. "
            "**Click any city bubble** to view detailed pollutant metrics and health guidelines."
        )

        map_obj = create_india_air_map(df_latest)
        try:
            st_folium(map_obj, use_container_width=True, height=580, returned_objects=[])
        except Exception as e:
            import streamlit.components.v1 as components
            components.html(map_obj.get_root().render(), height=580)

        # Map Legend Bar
        st.markdown("""
        <div style="display: flex; justify-content: space-around; background: #F8FAFC; padding: 12px 16px; border-radius: 8px; border: 1px solid #E2E8F0; margin-top: 12px; font-size: 12px;">
            <span>🟢 <b>Good</b> (0-50)</span>
            <span>🍏 <b>Satisfactory</b> (51-100)</span>
            <span>🟠 <b>Moderate</b> (101-200)</span>
            <span>🔴 <b>Poor</b> (201-300)</span>
            <span>🟣 <b>Very Poor</b> (301-400)</span>
            <span>🟤 <b>Severe</b> (401-500)</span>
        </div>
        """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # VIEW 3: BUSINESS INTELLIGENCE & ANALYTICS
    # ═══════════════════════════════════════════════════════════════════════════
    elif selected_view == "📈 Business Intelligence & Analytics":
        st.subheader("📈 Business Intelligence & Executive Analytics")
        st.markdown(
            "Unified BI command center: executive scorecard, Week-over-Week trends, "
            "city pollution ranking matrix, and diagnostic analytics aligned with "
            "CPCB NAAQS and WHO 2021 air quality guidelines."
        )

        # Fetch extended history for all cities for WoW / matrix computations
        all_history = pd.DataFrame()
        for slug in df_latest["city"].tolist():
            city_hist = get_city_history(engine, slug, limit=336)  # ~14 days
            if not city_hist.empty:
                city_hist["city"] = slug
                all_history = pd.concat([all_history, city_hist], ignore_index=True)

        # ── Executive Scorecard Row ────────────────────────────────────────────
        scorecard = render_executive_scorecard(df_latest, all_history)
        if scorecard:
            sc_cols = st.columns(len(scorecard))
            for idx, kpi in enumerate(scorecard):
                with sc_cols[idx]:
                    st.metric(
                        kpi["label"],
                        kpi["value"],
                        kpi.get("delta"),
                        help=kpi.get("help", ""),
                    )

        st.markdown("---")

        # ── Week-over-Week Trend ───────────────────────────────────────────────
        city_names_bi = df_latest["city_display_name"].tolist()
        city_slugs_bi = df_latest["city"].tolist()
        slug_map_bi = dict(zip(city_names_bi, city_slugs_bi))

        sel_col, _ = st.columns([1, 2])
        with sel_col:
            wow_city = st.selectbox("Select city for WoW trend:", city_names_bi, index=0)

        wow_slug = slug_map_bi[wow_city]
        wow_history = all_history[all_history["city"] == wow_slug] if not all_history.empty else pd.DataFrame()
        st.plotly_chart(render_wow_trend_chart(wow_history, wow_city), use_container_width=True, config={"displayModeBar": False})

        st.markdown("---")

        # ── City Pollution Ranking Matrix ─────────────────────────────────────
        st.markdown("#### 🏆 City Pollution Ranking Matrix")
        st.markdown(
            "Sortable executive table ranking cities by AQI, peak pollution, "
            "PM2.5 concentration, combustion ratio, and WHO limit exceedance hours."
        )
        matrix = render_city_ranking_matrix(df_latest, all_history)
        if not matrix.empty:
            st.dataframe(matrix, use_container_width=True, hide_index=True)
        else:
            st.info("Insufficient data for ranking matrix.")

        st.markdown("---")

        # ── Existing Diagnostic Row 1: Ranking + PM Ratio ─────────────────────
        c1, c2 = st.columns([1, 1])
        with c1:
            st.plotly_chart(render_city_ranking_chart(df_latest), use_container_width=True, config={"displayModeBar": False})
            st.caption("Cities ranked from cleanest to highest air quality index.")

        with c2:
            st.plotly_chart(render_pm_ratio_chart(df_latest), use_container_width=True, config={"displayModeBar": False})
            st.caption("Diagnostic: ratios >0.6 indicate combustion smog; <0.4 indicate road/construction dust.")

        st.markdown("---")

        # ── Existing Diagnostic Row 2: Diurnal + Anomaly ───────────────────────
        c3, c4 = st.columns([1, 1])
        with c3:
            sample_city = df_latest.iloc[0]["city"]
            history_df = get_city_history(engine, sample_city, limit=48)
            st.plotly_chart(render_diurnal_pattern_chart(history_df), use_container_width=True, config={"displayModeBar": False})
            st.caption(f"Diurnal hourly pattern for {df_latest.iloc[0]['city_display_name']}.")

        with c4:
            st.markdown("#### ⚡ Statistical Spike & Anomaly Detection")
            st.markdown("Uses Z-Score standardization ($Z = \\frac{X - \\mu}{\\sigma}$) to detect sudden pollutant surges.")
            anomalies = detect_zscore_anomalies(df_latest)
            if anomalies:
                for a in anomalies:
                    st.markdown(f"""
                    <div class="anomaly-card">
                        <b>⚠️ {a['city']}</b>: AQI={a['aqi']:.0f} (Z-Score: +{a['z_score']})<br>
                        <span style="font-size: 11px;">Status: <b>{a['type']}</b> | Severity: <b>{a['severity']}</b></span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("✅ All urban stations are currently operating within ±1.5σ normal statistical distribution.")

        st.markdown("---")
        st.markdown("### 🔬 Multi-Standard Scientific Laboratory: Why Do AQI Numbers Differ?")
        st.markdown(
            "Users frequently observe conflicting air quality numbers when comparing Google, Apple Weather, "
            "IQAir, and Indian government CAAQMS monitors for the same city. This laboratory demonstrates "
            "the scientific mechanics of mathematical breakpoint divergence and atmospheric modeling."
        )

        lab_c1, lab_c2 = st.columns([1, 2])
        with lab_c1:
            st.markdown("#### 🧪 Test Concentration")
            sim_pm25 = st.slider(
                "Simulated PM2.5 Concentration (µg/m³):",
                min_value=5.0,
                max_value=350.0,
                value=35.0,
                step=5.0,
                help="Adjust PM2.5 to observe how Indian CPCB and US EPA mathematical interpolation diverged."
            )
            from common.cpcb_calculator import calculate_cpcb_subindex, calculate_us_epa_pm25_aqi
            cpcb_sim = calculate_cpcb_subindex("pm25", sim_pm25)
            us_sim, us_sim_cat, us_sim_color = calculate_us_epa_pm25_aqi(sim_pm25)
            cpcb_cat_sim = get_aqi_category(cpcb_sim)

            st.markdown(f"""
            <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:8px; padding:12px; margin-top:8px;">
                <div style="font-size:11px; font-weight:700; color:#64748B;">INDIAN CPCB NAQI (2014)</div>
                <div style="font-size:24px; font-weight:800; color:{cpcb_cat_sim['color']};">{cpcb_sim} <span style="font-size:13px;">({cpcb_cat_sim['label']})</span></div>
                <hr style="margin:8px 0; border:0; border-top:1px dashed #CBD5E1;">
                <div style="font-size:11px; font-weight:700; color:#64748B;">US EPA AQI (2024 REVISION)</div>
                <div style="font-size:24px; font-weight:800; color:{us_sim_color};">{us_sim} <span style="font-size:13px;">({us_sim_cat})</span></div>
                <hr style="margin:8px 0; border:0; border-top:1px dashed #CBD5E1;">
                <div style="font-size:11px; color:#475569;">WHO 2021 24h Threshold: <b>15 µg/m³</b> ({sim_pm25/15.0:.1f}x limit)</div>
            </div>
            """, unsafe_allow_html=True)

        with lab_c2:
            st.plotly_chart(render_standards_comparison_chart(sim_pm25), use_container_width=True, config={"displayModeBar": False})

        with st.expander("🎓 MSc Capstone Viva Defense: Four Scientific Reasons for Divergence"):
            st.markdown("""
            1. **Different Breakpoint Conventions**: India's CPCB 2014 scale was designed for higher baseline particulate concentrations in South Asia (PM2.5 Satisfactory up to 60 µg/m³). The US EPA 2024 standard enforces a stricter limit (PM2.5 Moderate ceiling tightened to 35.4 µg/m³).
            2. **Averaging Period Gate**: CPCB NAQI requires a 24-hour running arithmetic mean with $\ge 16$ valid hourly readings ($\ge 6$ hours for CO/O3). Instantaneous hourly readings shown on consumer apps do not reflect regulatory 24h compliance.
            3. **Sensor Station vs Grid Model**: Physical CAAQMS stations measure localized air at a single GPS coordinate. Global models (such as Open-Meteo's ECMWF CAMS IFS-AER) simulate regional atmospheric transport across a ~45 km grid cell.
            4. **Platform Discrepancies**: Google supports 70+ localized AQI systems; Apple utilizes BreezoMeter atmospheric algorithms; IQAir defaults to US EPA AQI. AirSense transparently presents both the official Indian regulatory CPCB NAQI and the 1-hour indicative index.
            """)

    # ═══════════════════════════════════════════════════════════════════════════
    # VIEW 4: 48-HOUR AQI FORECAST
    # ═══════════════════════════════════════════════════════════════════════════
    elif selected_view == "🔮 48-Hour AQI Forecast":
        st.subheader("🔮 Machine Learning 48-Hour AQI Forecasting")
        st.markdown(
            "Predictive environmental intelligence powered by a production **LightGBM Gradient Boosting** "
            "regressor trained on rolling autoregressive lags, temporal cycles, and walk-forward cross-validation."
        )

        # Model Metadata & Governance Banner
        meta = load_model_metadata()
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.metric("Model Architecture", "LightGBM Regressor", help="Gradient Boosted Decision Trees")
        with m_col2:
            st.metric("Mean RMSE", f"{meta.get('rmse', 7.61):.2f} AQI", help="Target < 30.0 AQI")
        with m_col3:
            st.metric("Mean MAE", f"{meta.get('mae', 5.77):.2f} AQI", help="Average absolute error")
        with m_col4:
            st.metric("R² Variance Explained", f"{meta.get('r2', 0.961):.3f}", help="96.1% variance captured")

        st.markdown("---")

        # City Selector
        city_names = df_latest["city_display_name"].tolist()
        city_slugs = df_latest["city"].tolist()
        slug_map = dict(zip(city_names, city_slugs))

        sel_col, _ = st.columns([1, 2])
        with sel_col:
            selected_city_name = st.selectbox("Select Target City for Forecast:", city_names, index=0)
        
        target_slug = slug_map[selected_city_name]

        # Fetch actuals and forecasts
        actual_df = get_city_history(engine, target_slug, limit=48)
        forecast_df = get_city_forecast(engine, target_slug)

        if not forecast_df.empty:
            current_aqi = actual_df["aqi"].iloc[0] if not actual_df.empty else forecast_df["predicted_aqi"].iloc[0]
            peak_val = forecast_df["predicted_aqi"].max()
            min_val = forecast_df["predicted_aqi"].min()
            delta_val = forecast_df["predicted_aqi"].iloc[-1] - current_aqi

            trend_status = "↗️ Deteriorating" if delta_val > 10 else ("↘️ Improving" if delta_val < -10 else "➡️ Stable")

            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            with kpi1:
                st.metric("Current AQI", f"{current_aqi:.0f}", help="Latest recorded telemetry")
            with kpi2:
                st.metric("48h Projected Peak", f"{peak_val:.0f}", help="Highest expected AQI over the next 48 hours")
            with kpi3:
                st.metric("48h Projected Min", f"{min_val:.0f}", help="Lowest expected AQI over the next 48 hours")
            with kpi4:
                st.metric("Expected Trajectory", trend_status, delta=f"{delta_val:+.1f} AQI")

            # Combined Chart
            fig = render_combined_forecast_chart(actual_df, forecast_df, selected_city_name)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            # Phase 7: Benchmark Comparison — LightGBM vs Naive Baselines
            st.markdown("---")
            st.markdown("#### 📊 Model Benchmark — LightGBM vs Naive Baselines")
            st.markdown(
                "The LightGBM champion model is benchmarked against two naive forecasting "
                "baselines. A defensible ML model must demonstrably outperform these trivial "
                "predictors to justify its deployment complexity."
            )
            bench_chart = render_benchmark_comparison_chart()
            st.plotly_chart(bench_chart, use_container_width=True, config={"displayModeBar": False})

            # Benchmark comparison table
            bench_data = get_benchmark_comparison_data()
            st.dataframe(
                pd.DataFrame(bench_data),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Model": st.column_config.TextColumn("Model", width="medium"),
                    "RMSE": st.column_config.NumberColumn("RMSE", format="%.2f"),
                    "MAE": st.column_config.NumberColumn("MAE", format="%.2f"),
                    "R²": st.column_config.NumberColumn("R²", format="%.3f"),
                },
            )

            # Phase 7: SHAP Feature Importance & Explainability
            st.markdown("---")
            st.markdown("#### 🔬 SHAP Feature Importance — Explainability")
            st.markdown(
                "SHAP (SHapley Additive exPlanations) values quantify each feature's "
                "contribution to individual predictions. The chart below shows the top 5 "
                "predictive drivers by mean absolute SHAP value, computed via LightGBM's "
                "built-in TreeSHAP algorithm."
            )
            shap_fig = render_feature_importance_chart()
            st.plotly_chart(shap_fig, use_container_width=True, config={"displayModeBar": False})

            # Data Expander Table
            with st.expander("📋 View Hourly Forecast Data Table & Health Advisory", expanded=False):
                fc_table = forecast_df.copy()
                fc_table["forecast_time"] = pd.to_datetime(fc_table["forecast_time"]).dt.strftime("%Y-%m-%d %H:%M UTC")
                fc_table["predicted_aqi"] = fc_table["predicted_aqi"].round(1)
                fc_table["cpcb_category"] = fc_table["predicted_aqi"].apply(lambda v: get_aqi_category(v)["label"])
                fc_table = fc_table.rename(columns={
                    "forecast_time": "Timestamp (UTC)",
                    "predicted_aqi": "Forecasted AQI",
                    "cpcb_category": "CPCB Category",
                    "model_version": "Model Version",
                })
                st.dataframe(
                    fc_table[["Timestamp (UTC)", "Forecasted AQI", "CPCB Category", "Model Version"]],
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.warning(f"No forecast records found for {selected_city_name}. Run `python ml/training/predict_forecast.py` to generate forecasts.")

            # Phase 7: Show benchmark & SHAP even without forecast data (uses model metadata)
            st.markdown("---")
            st.markdown("#### 📊 Model Benchmark — LightGBM vs Naive Baselines")
            st.plotly_chart(render_benchmark_comparison_chart(), use_container_width=True, config={"displayModeBar": False})
            st.dataframe(pd.DataFrame(get_benchmark_comparison_data()), use_container_width=True, hide_index=True)

            st.markdown("#### 🔬 SHAP Feature Importance — Explainability")
            st.plotly_chart(render_feature_importance_chart(), use_container_width=True, config={"displayModeBar": False})

    # ═══════════════════════════════════════════════════════════════════════════
    # VIEW 5: AI HEALTH ADVISOR (RAG + Ollama LLM)
    # ═══════════════════════════════════════════════════════════════════════════
    elif selected_view == "🤖 AI Health Advisor":
        render_ai_advisor_view(df_latest=df_latest)

    # ═══════════════════════════════════════════════════════════════════════════
    # VIEW 6: PIPELINE HEALTH (Phase 10 — Observability)
    # ═══════════════════════════════════════════════════════════════════════════
    elif selected_view == "🩺 Pipeline Health":
        render_pipeline_health_tab(engine=engine)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #94A3B8; font-size: 12px; padding: 20px 0;">
        AirSense Platform • MSc Business Intelligence & Analytics • Academic Capstone 2026<br>
        Telemetry sourced from <a href="https://waqi.info" target="_blank" style="color:#64748B;">WAQI Open Data</a> 
        and Central Pollution Control Board (CPCB).
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
