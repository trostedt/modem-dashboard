
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

# Config
st.set_page_config(page_title="Modem Connectivity Dashboard", layout="wide")
st.title("📡 Modem Connectivity Dashboard")

# Upload CSV
uploaded_file = st.file_uploader("Upload CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    time_col = df.columns[0]
    modem_cols = df.columns[1:]

    # Simulated extra metrics (add latency and RSSI if not present)
    if "LatencyMs" not in df.columns:
        df["LatencyMs"] = np.abs((df.index % 15) * 20 + 100 + np.random.normal(0, 10, size=len(df)))
    if "RSSIdBm" not in df.columns:
        df["RSSIdBm"] = -60 + 20 * np.sin(df.index / 10) + np.random.normal(0, 5, size=len(df))

    tab1, tab2 = st.tabs(["📈 Single Modem Analysis", "📊 Multi-Modem Comparison"])

    with tab1:
        st.header("Single Modem View")

        selected_modem = st.selectbox("Select a modem", modem_cols)
        available_metrics = {
            "Disconnect %": selected_modem,
            "Latency (ms)": "LatencyMs",
            "RSSI (dBm)": "RSSIdBm"
        }

        selected_metrics = st.multiselect(
            "Select metrics to display",
            list(available_metrics.keys()),
            default=list(available_metrics.keys())
        )

        if selected_metrics:
            plot_cols = [available_metrics[m] for m in selected_metrics]
            df_plot = df[[time_col] + plot_cols]
            df_melted = df_plot.melt(id_vars=time_col, var_name="Metric", value_name="Value")

            fig = px.line(df_melted, x=time_col, y="Value", color="Metric",
                          title=f"{selected_modem} - Selected Metrics Over Time")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please select at least one metric.")

    with tab2:
        st.header("Multi-Modem Comparison")

        metric_option = st.selectbox("Select metric to compare", ["Disconnect %", "Latency (ms)", "RSSI (dBm)"])
        metric_map = {
            "Disconnect %": modem_cols,
            "Latency (ms)": "LatencyMs",
            "RSSI (dBm)": "RSSIdBm"
        }

        if metric_option == "Disconnect %":
            selected_modems = st.multiselect("Select modems to compare", modem_cols, default=list(modem_cols))
            if selected_modems:
                df_melted = df.melt(id_vars=time_col, value_vars=selected_modems,
                                    var_name="Modem", value_name="Value")
                fig_multi = px.line(df_melted, x=time_col, y="Value", color="Modem",
                                    title="Disconnect % Over Time")
                fig_multi.update_yaxes(range=[0, 100])
                st.plotly_chart(fig_multi, use_container_width=True)

                if st.checkbox("Show Heatmap"):
                    st.subheader("Disconnect % Heatmap")
                    heatmap_data = df[selected_modems].T
                    fig2, ax = plt.subplots(figsize=(12, 5))
                    sns.heatmap(heatmap_data, cmap="YlGnBu", vmin=0, vmax=100,
                                xticklabels=10, yticklabels=selected_modems, cbar_kws={'label': 'Disconnect %'})
                    st.pyplot(fig2)
            else:
                st.warning("Please select at least one modem.")
        else:
            metric_col = metric_map[metric_option]
            st.info(f"Showing '{metric_option}' across all modems.")
            df_metric = pd.DataFrame({
                "Time": df[time_col],
                "Metric": df[metric_col]
            })
            fig = px.line(df_metric, x="Time", y="Metric", title=f"{metric_option} Over Time")
            st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Please upload a CSV file to get started.")
