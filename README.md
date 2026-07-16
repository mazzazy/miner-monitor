# ⛏️ Miner Monitor Dashboard

A real-time mining farm monitoring system built with Streamlit.

## Features

- Live worker monitoring (Braiins API)
- Hashrate tracking (5m / 60m / 24h)
- Incident tracking system
- Uptime analytics engine
- Worker drill-down dashboard
- Interactive Plotly charts with downtime visualization

## Architecture

- Streamlit UI (dashboard)
- Python monitoring engine (monitor.py)
- API integration layer (Braiins API)
- Incident + uptime engine
- Local storage (JSON + CSV)

## Run locally

```bash
pip install -r requirements.txt
streamlit run app/dashboard/main.py