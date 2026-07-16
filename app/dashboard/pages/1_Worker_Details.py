import streamlit as st

from app.dashboard.services.dashboard_service import DashboardService
from app.dashboard.services.worker_details_service import WorkerDetailsService
from app.dashboard.services.app_state import AppState
from app.dashboard.services.worker_chart_service import WorkerChartService
import plotly.graph_objects as go
from app.dashboard.services.chart_renderer import ChartRenderer

AppState.init()

service = WorkerDetailsService()
chart_service = WorkerChartService()

workers = service.dashboard.get_live_workers()
worker_list = sorted(workers["Worker"])

renderer = ChartRenderer()

def plot_hashrate(df, title, column):
    
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df[column],
            mode="lines",
            name=column
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title="TH/s",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return fig

# initialize if empty
if AppState.get_worker() is None:
    AppState.set_worker(worker_list[0])

selected = st.selectbox(
    "Select Worker",
    worker_list,
    index=worker_list.index(AppState.get_worker())
)
AppState.set_worker(selected)
worker_name = AppState.get_worker()

worker = service.get_worker(selected)
uptime = service.get_uptime(selected)
reliability = service.get_reliability(uptime)
last_share = service.format_last_share(
    worker["Last Share"]
)
incident = service.get_current_incident(selected)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Status",
    worker["Status"]
)

c2.metric(
    "Current 5m",
    f"{worker['5m TH/s']:.2f} TH/s"
)

c3.metric(
    "Uptime",
    f"{uptime:.2f}%"
)

c4.metric(
    "Last Share",
    last_share
)

st.subheader("Hashrate")

h1, h2, h3 = st.columns(3)

h1.metric(
    "5m",
    f"{worker['5m TH/s']:.2f} TH/s"
)

h2.metric(
    "60m",
    f"{worker['60m TH/s']:.2f} TH/s"
)

h3.metric(
    "24h",
    f"{worker['24h TH/s']:.2f} TH/s"
)

left, right = st.columns(2)

with left:
    st.subheader("Reliability")
    st.success(reliability)

with right:
    st.subheader("Current Incident")

    if incident:
        st.error(
            f"{incident['severity']} - {incident['state']}"
        )
    else:
        st.success("No active incident")

# st.subheader("📊 Hashrate Trend")
# chart_df = chart_service.get_worker_chart_data(worker_name)
# if chart_df.empty:
#     st.warning("No chart data available")
# else:
#     st.line_chart(
#         chart_df[[
#             "hashrate_5m",
#             "hashrate_60m",
#             "hashrate_24h"
#         ]]
#     )

st.subheader("📊 Hashrate History")

chart5 = chart_service.get_5m_chart(worker_name)

st.markdown("### 5 Minute Hashrate")

if chart5.empty:
    st.info("No data available.")
else:
    fig5 = renderer.plot_hashrate_with_incident_bands(
    chart5,
    incident,
    "5 Minute Hashrate",
    "hashrate_5m"
    )

    st.plotly_chart(fig5, use_container_width=True)

chart60 = chart_service.get_60m_chart(worker_name)

st.markdown("### 60 Minute Hashrate")

if chart60.empty:
    st.info("No data available.")
else:
    
    fig60 = renderer.plot_hashrate_with_incident_bands(
    chart60,
    incident,
    "60 Minute Hashrate",
    "hashrate_60m"
)
    st.plotly_chart(fig60, use_container_width=True)

chart24 = chart_service.get_24h_chart(worker_name)

st.markdown("### 24 Hour Hashrate")

if chart24.empty:
    st.info("No data available.")
else:
    fig24 = renderer.plot_hashrate_with_incident_bands(
    chart24,
    incident,
    "24 Hour Hashrate",
    "hashrate_24h"
)

    st.plotly_chart(fig24, use_container_width=True)