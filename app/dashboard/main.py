from datetime import datetime
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from app.dashboard.services.dashboard_service import DashboardService
from app.dashboard.services.chart_service import ChartService
import pandas as pd
from app.dashboard.services.hashrate_formatter import HashrateFormatter
from app.dashboard.services.uptime_dashboard_service import UptimeDashboardService
from app.dashboard.services.uptime_chart_service import UptimeChartService
from app.dashboard.services.app_state import AppState

AppState.init()

def text_color(val):
    if val == "ok":
        return "color: #2e7d32; font-weight: 500"
    elif val == "low":
        return "color: #f9a825; font-weight: 500"
    elif val == "off":
        return "color: #c62828; font-weight: 600"
    return ""

def highlight_rank(val):
    if val == 1:
        return "background-color: #d4edda"
    elif val <= 3:
        return "background-color: #fff3cd"
    return ""
# ==========================================================
# CONFIG (must be first Streamlit command)
# ==========================================================
st.set_page_config(
    page_title="Miner Monitor",
    page_icon="⛏️",
    layout="wide"
)
st.sidebar.markdown("---")
st.sidebar.subheader("Selected Worker")

current = AppState.get_worker()

if current:
    st.sidebar.success(current)
else:
    st.sidebar.warning("No worker selected")
    
# Auto refresh every 30 seconds
st_autorefresh(interval=30 * 1000, key="data_refresh")

# ==========================================================
# SERVICE
# ==========================================================
service = DashboardService()
uptime_service = UptimeDashboardService()
chart_service = ChartService()
stats = service.get_current_statistics()
incidents = service.get_open_incidents()
Uptime_chart_service = UptimeChartService()
workers = service.get_live_workers()

# ==========================================================
# HEADER
# ==========================================================
st.title("⛏️ Braiins Pool Dashboard")

st.caption(
    f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

# ==========================================================
# SYSTEM STATUS
# ==========================================================
st.subheader("System Status")

col1, col2, col3 = st.columns(3)
col1.metric("API Status", "🟢 Online")
col2.metric("Monitor", "Running")
col3.metric("Dashboard", "Active")

# ==========================================================
# INCIDENT SUMMARY
# ==========================================================
st.subheader("Incident Summary")

critical = stats.get("critical", 0)
warning = stats.get("warning", 0)
offline = stats.get("offline", 0)

c1, c2, c3 = st.columns(3)
c1.metric("Critical", critical)
c2.metric("Warning", warning)
c3.metric("Offline", offline)

# ==========================================================
# FARM KPIs
# ==========================================================
st.subheader("Farm KPIs")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Hashrate",
    HashrateFormatter.format_farm_hashrate(
        stats["hashrate"]
    )
)

c2.metric(
    "Availability",
    f"{stats['availability']:.1f}%"
)

c3.metric(
    "Workers",
    stats["workers"]
)

c4.metric(
    "Open Incidents",
    incidents
)

# ==========================================================
# FARM HEALTH
# ==========================================================
st.subheader("Farm Health")

a, b, c = st.columns(3)

a.success(f"Healthy\n\n{stats['online']}")
b.error(f"Offline\n\n{stats['offline']}")
c.warning(f"Low Hashrate\n\n{stats['low']}")

# ==========================================================
# INCIDENT TABLE
# ==========================================================
st.subheader("Open Incidents")

incident_df = service.get_incident_list()

if incident_df.empty:
    st.success("No open incidents.")
else:
    st.dataframe(incident_df, use_container_width=True)

# ==========================================================
# TRENDS
# ==========================================================
st.subheader("📈 Farm Hashrate Trend (5 min)")

trend = chart_service.get_farm_hashrate_trend()

st.line_chart(
    trend.set_index("timestamp")
)
# ==========================================================
# WORKERS
# ==========================================================

st.subheader("Workers Status")

workers = service.get_live_workers()

workers = workers.rename(columns={
    "Worker": "worker",
    "Status": "state"
})
workers = workers.sort_values(by="state")
styled_workers = workers.style.map(text_color, subset=["state"])

st.dataframe(
    styled_workers,
    use_container_width=True
)


st.subheader("Worker Uptime (Last 30 Days)")
uptime_df = uptime_service.get_uptime_table()

st.dataframe(
    uptime_df,
    use_container_width=True
)

st.subheader("🏆 Worker Reliability Leaderboard")
ranking_df = uptime_service.get_worker_ranking()
st.dataframe(
    ranking_df,
    use_container_width=True,
    hide_index=True
)

st.subheader("📈 Farm Uptime Trend (7 Days)")

trend = Uptime_chart_service.get_farm_trend(7)
st.line_chart(
    trend,
    x="time",
    y="healthy_workers"
)

st.subheader("📊 Worker Uptime Comparison")
worker_cmp = Uptime_chart_service.get_worker_comparison(7)
st.bar_chart(
    worker_cmp,
    x="worker",
    y="uptime"
)

st.subheader("⚠️ Farm State Distribution")
dist = Uptime_chart_service.get_state_distribution()