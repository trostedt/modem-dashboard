
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots

st.set_page_config(page_title="Modem Connectivity Dashboard", layout="wide")
st.title("📡 Modem Connectivity Dashboard")

uploaded_file = st.file_uploader("Upload CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    time_col = df.columns[0]

    # Extract modem IDs
    modem_ids = sorted(set(col.split(" - ")[0] for col in df.columns[1:]))

    tab1, tab2 = st.tabs(["📈 Single Modem Analysis", "📊 Multi-Modem Comparison"])

    with tab1:
        st.header("Single Modem View")

        selected_modem = st.selectbox("Select a modem", modem_ids)
        metric_options = ["Disconnect %", "Latency", "RSSI"]

        selected_metrics = st.multiselect(
            "Select metrics to display",
            metric_options,
            default=metric_options
        )

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        show_plot = False

        # Disconnect % → Primary Y
        if "Disconnect %" in selected_metrics:
            fig.add_trace(
                go.Scatter(
                    x=df[time_col],
                    y=df[f"{selected_modem} - Disconnect %"],
                    name="Disconnect %",
                    line=dict(color="green"), hovertemplate="Disconnect %%: %{y}<br>Time: %{x} min"
                ),
                secondary_y=False
            )
            show_plot = True

        # Latency and RSSI → Secondary Y
        if "Latency" in selected_metrics:
            fig.add_trace(
                go.Scatter(
                    x=df[time_col],
                    y=df[f"{selected_modem} - Latency"],
                    name="Latency (ms)",
                    line=dict(color="blue", dash="dash"), hovertemplate="Latency (ms): %{y:.1f}<br>Time: %{x} min"
                ),
                secondary_y=True
            )
            show_plot = True

        if "RSSI" in selected_metrics:
            fig.add_trace(
                go.Scatter(
                    x=df[time_col],
                    y=df[f"{selected_modem} - RSSI"],
                    name="RSSI (dBm)",
                    line=dict(color="red", dash="dot"), hovertemplate="RSSI (dBm): %{y:.1f}<br>Time: %{x} min"
                ),
                secondary_y=True
            )
            show_plot = True

        if show_plot:
            fig.update_layout(
                title=f"{selected_modem} - Selected Metrics Over Time",
                xaxis_title="Time (minutes)",
                height=500,
                margin=dict(l=40, r=40, t=40, b=40),
                legend=dict(x=0.01, y=0.99)
            )
            fig.update_yaxes(title_text="Disconnect %", secondary_y=False)
            fig.update_yaxes(title_text="Latency (ms) / RSSI (dBm)", secondary_y=True)
            fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please select at least one metric.")

    with tab2:
        st.header("Multi-Modem Comparison")

        selected_metric = st.selectbox("Select metric to compare", ["Disconnect %", "Latency", "RSSI"])
        selected_modems = st.multiselect("Select modems to compare", modem_ids, default=modem_ids)

        if selected_modems:
            value_cols = [f"{modem} - {selected_metric}" for modem in selected_modems]
            df_plot = df[[time_col] + value_cols]
            df_melted = df_plot.melt(id_vars=time_col, var_name="Modem", value_name="Value")

            fig = go.Figure()
            for modem in selected_modems:
                fig.add_trace(go.Scatter(
                    x=df[time_col],
                    y=df[f"{modem} - {selected_metric}"],
                    name=modem, hovertemplate="%{fullData.name}<br>Value: %{y}<br>Time: %{x} min"
                ))

            fig.update_layout(
                title=f"{selected_metric} Over Time",
                xaxis_title="Time (minutes)",
                yaxis_title=selected_metric,
                height=500
            )
            fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

            if selected_metric == "Disconnect %" and st.checkbox("Show Heatmap"):
                st.subheader("Disconnect % Heatmap")
                heatmap_data = df[value_cols].T
                fig2, ax = plt.subplots(figsize=(12, 5))
                sns.heatmap(heatmap_data, cmap="YlGnBu", vmin=0, vmax=100,
                            xticklabels=10, yticklabels=selected_modems, cbar_kws={'label': 'Disconnect %'})
                st.pyplot(fig2)
        else:
            st.warning("Please select at least one modem.")
else:
    st.info("Please upload a CSV file to get started.")
