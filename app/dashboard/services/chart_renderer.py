import pandas as pd
import plotly.graph_objects as go
from datetime import datetime


class ChartRenderer:

    @staticmethod
    def plot_hashrate_with_incident_bands(df, incident, title, column):

        fig = go.Figure()

        # -----------------------
        # 1. Hashrate line
        # -----------------------
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df[column],
                mode="lines",
                name="Hashrate"
            )
        )

        # -----------------------
        # 2. Incident time bands
        # -----------------------
        if incident:

            state = str(
                incident.get("state", "")).lower()
            start = incident.get("first_seen")
            # If no start time, skip shading
            if start:
                # If still open → extend to now
                end = incident.get(
                "resolved_at")

                if not end:
                    end = datetime.now()
                # Choose color
                if state == "off":
                    color = "rgba(255,0,0,0.25)"  # red
                elif state == "low":
                    color = "rgba(255,165,0,0.20)"  # orange
                else:
                    color = "rgba(0,255,0,0.15)"   # green 
                
                fig.add_vrect(
                    x0=start,
                    x1=end,
                    fillcolor=color,
                    opacity=0.4,
                    layer="below",
                    line_width=0,
                    annotation_text=state.upper(),
                    annotation_position="top left"
                )             



        # -----------------------
        # 3. Layout
        # -----------------------
        fig.update_layout(
            title=title,
            xaxis_title="Time",
            yaxis_title="TH/s",
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h"),
            hovermode="x unified"
        )

        return fig