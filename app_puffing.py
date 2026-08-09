import glob
import os
from datetime import datetime, time
import warnings
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

warnings.filterwarnings("ignore")

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="PP Analyzer (Puffing #1 & #2)", layout="wide"
)

st.title("🔥 PP Analyzer (Puffing Log Analysis)")
st.write(
    "Data analysis application for Puffing #1 and Puffing #2 trend logs, integrating Google Colab workflows."
)

# ---------------------------------------------------------
# COLUMN MAPPING DICTIONARIES
# ---------------------------------------------------------
column_mapping_PP1 = {
    "P2001": "CB Current",
    "C2006": "FRV Current",
    "TT2410": "FRV Front Temperature",
    "C2007": "BRV Current",
    "FT2000": "Flow Rate of Make up steam (LBs/HR)",
    "PD2302": "Strainer Differential Pressure",
    "PIC2000": "System Pressure",
    "FT2402": "Main (SH Outlet) Air Velocity",
    "TIC2000": "Main Temperature",
    "TT2000": "Main Temperature2",
    "TT2402": "Raw Material Input Temperature",
    "TT2406": "Cooler Rear Temperature",
    "TT2416": "Cooler Front Temperature",
    "TT2413": "S.H. Inlet Temperature (F)",
    "TIC2403": "S.H. Outlet Temperature (F)",
    "TT2423": "S.H. Upper Combustion",
    "T2412": "Temperature befor the Cyclon",
    "FT2506": "ByPass Flowrate",
    "FT2403": "SH Bypass Flowrate",
    "C2003": "Feed Rate",
    "TCV2403": "S.H. Output",
    "PT2103": "Seal Water Pressure (PSI)",
    "FT2103": "Seal Water Flow Rate (GPM)",
    "FT2101": "Bearling Cooling Water Flow Rate",
}

column_mapping_PP2 = {
    "EM2152": "CB Current",
    "EM25560.": "FRV Current",
    "EM25570": "BRV Current",
    "FT20530": "Flow Rate of Make up steam (LBs/HR)",
    "DPT2357": "Strainer Differential Pressure",
    "PT20510": "System Pressure",
    "PT2051.Out": "System Pressure PID OUTPUT",
    "PT2051.PV": "System Pressure PV",
    "PT2051.SP": "System Pressure SP",
    "FT24540": "Main (SH Outlet) Air Velocity",
    "TT2051.out": "Main Temperature PID OUT",
    "TT2051.PV": "Main Temperature PV",
    "TT2051.SP": "Main Temperature SP",
    "TT2454O.Out": "S.H. out Temperature (F) OUT",
    "TT2454O.PV": "S.H. out Temperature (F) PV",
    "TT2454O.SP": "S.H. out Temperature (F) SP",
    "TEMP_TE2454O0": "S.H. output Temperature (F)",
    "TEMP_TE2454I": "S.H. inlet Temperature (F)",
    "PT2152.0": "Mechanical Seal Water Pressure (PSI)",
    ".[Puffing2.Flow_Rate_FP6.]": "Mechanical Seal Water Flow Rate1 (GPM)",
    ".[Puffing2.Flow_Rate_FP7.]": "Mechanical Seal Water Flow Rate2 (GPM)",
    ".[Puffing2.FLOW_RATE_FP8.]": "CB Bearing Water Flow Rate (GPM)",
    "TE20510.": "Temperature befor the Cyclon",
    "TEMP_TE2455I0": "Temp Before Product Cooler",
    "TEMP_TE2455O0": "Temp After Product Cooler",
}

# ---------------------------------------------------------
# EVENT DEFINITIONS
# ---------------------------------------------------------
event_dates_for_PP1 = {
    "2025-08-11 05:00:00": "Exchange <br> Make up <br> Steam meter",
    "2025-08-18 05:00:00": "Exchange <br> Main Flow meter",
    "2025-08-25 22:00:00": "Stack",
    "2025-08-30 01:00:00": "Stack",
    "2025-08-30 08:30:00": "Stack",
    "2025-09-07 22:00:00": "Stack",
    "2025-09-08 10:00:00": "Bypass opening rate 45%",
    "2025-09-09 12:00:00": "Stack",
    "2025-09-10 12:00:00": "FRV交換",
    "2026-01-19 12:00:00": "GearBox Changed",
    "2026-07-03 12:30:00": "temporary power outage",
    "2026-07-03 12:00:00": "CB Broken and Exchange new one",
    "2026-07-05 16:00:00": "CB Bearing Water Line Solenoid Valve Change",
    "2026-08-08 10:40:00": "Seal Water Preassure Low",
}

event_dates_for_PP2 = {}

# ---------------------------------------------------------
# DATA PROCESSING HELPER FUNCTIONS
# ---------------------------------------------------------


def process_dataframe(df, column_mapping):
    """Clean, rename, parse timestamp, and numeric-convert the given DataFrame."""
    if df.empty:
        return df

    df = df.copy()

    # TimeStamp Parsing
    if "TimeStamp" in df.columns:
        df["TimeStamp"] = pd.to_datetime(
            df["TimeStamp"], errors="coerce", format="mixed"
        )
        df.dropna(subset=["TimeStamp"], inplace=True)

    # Column Renaming Logic
    rename_dict = {}
    for old_col in df.columns:
        for key, value in column_mapping.items():
            if key in old_col:
                rename_dict[old_col] = value
                break
    df.rename(columns=rename_dict, inplace=True)
    df = df.loc[:, ~df.columns.duplicated()]

    if "TimeStamp" in df.columns:
        df.drop_duplicates(subset=["TimeStamp"], inplace=True)
        df.sort_values("TimeStamp", inplace=True)

    df.replace("Null", 0, inplace=True)

    # Numeric conversion
    for col in df.columns:
        if col != "TimeStamp":
            try:
                df[col] = pd.to_numeric(df[col])
            except (TypeError, ValueError):
                continue

    return df.reset_index(drop=True)


def add_event_history_annotations(fig, plot_data, event_dates):
    """Add red dashed vertical lines and event annotations."""
    if plot_data.empty or "TimeStamp" not in plot_data.columns:
        return

    min_plot_date = plot_data["TimeStamp"].min()
    max_plot_date = plot_data["TimeStamp"].max()

    for date_str, text in event_dates.items():
        event_date = pd.to_datetime(date_str)
        if min_plot_date <= event_date <= max_plot_date:
            fig.add_shape(
                type="line",
                x0=event_date,
                y0=0,
                x1=event_date,
                y1=1,
                xref="x",
                yref="paper",
                line=dict(color="red", width=2, dash="dash"),
            )
            fig.add_annotation(
                x=event_date,
                y=1,
                xref="x",
                yref="paper",
                text=text,
                showarrow=False,
                yshift=10,
            )


# ---------------------------------------------------------
# SIDEBAR - DATA LOADING LOGIC
# ---------------------------------------------------------
st.sidebar.header("📁 Data Loading")

puffing_target = st.sidebar.radio(
    "Select Target Puffing Unit:", ["Puffing #1", "Puffing #2"]
)

uploaded_files = st.sidebar.file_uploader(
    f"Upload CSV files for {puffing_target} (Optional)",
    type=["csv"],
    accept_multiple_files=True,
)

raw_data = pd.DataFrame()

# 1. Uploaded files take priority
if uploaded_files:
    st.sidebar.success(f"Using uploaded CSV file(s) for {puffing_target}.")
    for file in uploaded_files:
        tmp = pd.read_csv(file, low_memory=False)
        raw_data = pd.concat([raw_data, tmp], axis=0)

# 2. Auto-load from GitHub Repository
else:
    if puffing_target == "Puffing #1":
        search_paths = glob.glob("data/Puffing#1/*.csv") + glob.glob("PP1/*.csv")
    else:
        search_paths = glob.glob("data/Puffing#2/*.csv") + glob.glob("PP2/*.csv")

    search_paths = sorted(list(set(search_paths)))

    if search_paths:
        st.sidebar.info(
            f"Automatically concatenated {len(search_paths)} CSV file(s) for {puffing_target} from repo."
        )
        for path in search_paths:
            tmp = pd.read_csv(path, low_memory=False)
            raw_data = pd.concat([raw_data, tmp], axis=0)
    else:
        st.info(
            f"👈 Please upload CSV file(s) or add files into `data/PP/PP1/` or `data/PP/PP2/` in your repository."
        )

# ---------------------------------------------------------
# MAIN ANALYSIS & PLOTTING
# ---------------------------------------------------------
if not raw_data.empty:
    if puffing_target == "Puffing #1":
        mapping = column_mapping_PP1
        event_dates = event_dates_for_PP1
    else:
        mapping = column_mapping_PP2
        event_dates = event_dates_for_PP2

    data = process_dataframe(raw_data, mapping)

    st.markdown("---")

    # Export Data Option in Sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("💾 Export Processed Data")
    csv_bytes = data.to_csv(index=False).encode("utf-8")
    st.sidebar.download_button(
        label=f"📥 Download Processed {puffing_target} CSV",
        data=csv_bytes,
        file_name=f"{puffing_target.replace(' #', '')}_processed_data.csv",
        mime="text/csv",
    )

    # Date Range Selector
    min_dt = data["TimeStamp"].min()
    max_dt = data["TimeStamp"].max()

    st.subheader("📅 Date & Time Filter")
    col_d1, col_t1, col_d2, col_t2 = st.columns(4)
    start_date = col_d1.date_input("Start Date", min_dt.date())
    start_time = col_t1.time_input("Start Time", time(0, 0))
    end_date = col_d2.date_input("End Date", max_dt.date())
    end_time = col_t2.time_input("End Time", time(23, 59))

    start_dt = pd.to_datetime(f"{start_date} {start_time}")
    end_dt = pd.to_datetime(f"{end_date} {end_time}")

    plot_data = data[
        (data["TimeStamp"] >= start_dt) & (data["TimeStamp"] <= end_dt)
    ]

    if plot_data.empty:
        st.warning("No data available in the selected date range.")
    else:
        # Navigation Tabs for Plot Options
        tab1, tab2, tab3 = st.tabs(
            [
                "📈 Single Tag Trend",
                "🔀 Multi-Tag Comparison",
                "📋 Raw Data Table",
            ]
        )

        # List of tags (excluding TimeStamp)
        available_tags = [
            col for col in plot_data.columns if col != "TimeStamp"
        ]

        # --- TAB 1: Single Tag Trend ---
        with tab1:
            st.subheader(f"Single Variable Analysis ({puffing_target})")
            selected_tag = st.selectbox(
                "Select Tag to Plot:", available_tags, index=0
            )

            fig1 = go.Figure()
            fig1.add_trace(
                go.Scatter(
                    x=plot_data["TimeStamp"],
                    y=plot_data[selected_tag],
                    mode="lines",
                    name=selected_tag,
                )
            )

            # Add Feed Rate overlay if PP1 and Feed Rate exists
            include_feed_rate = st.checkbox(
                "Overlay Feed Rate (if available)", value=False
            )
            if include_feed_rate and "Feed Rate" in plot_data.columns:
                fig1.add_trace(
                    go.Scatter(
                        x=plot_data["TimeStamp"],
                        y=plot_data["Feed Rate"],
                        mode="lines",
                        name="Feed Rate",
                    )
                )

            fig1.update_layout(
                title=dict(
                    text=f"{puffing_target} - {selected_tag} Over Time", x=0.5
                ),
                xaxis_title="Time",
                yaxis_title=selected_tag,
                xaxis_type="date",
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.2,
                    xanchor="center",
                    x=0.5,
                ),
                height=600,
            )

            add_event_history_annotations(fig1, plot_data, event_dates)
            st.plotly_chart(fig1, use_container_width=True)

        # --- TAB 2: Multi-Tag Comparison ---
        with tab2:
            st.subheader(f"Multi-Variable Comparison ({puffing_target})")

            col_tag1, col_tag2 = st.columns(2)
            tag1 = col_tag1.selectbox(
                "Select Primary Tag (Left Y-Axis):",
                available_tags,
                index=0,
                key="tag1",
            )
            tag2 = col_tag2.selectbox(
                "Select Secondary Tag (Right Y-Axis):",
                available_tags,
                index=min(1, len(available_tags) - 1),
                key="tag2",
            )

            use_sec_y = st.checkbox("Use Secondary Y-Axis", value=True)

            fig2 = make_subplots(specs=[[{"secondary_y": use_sec_y}]])
            fig2.add_trace(
                go.Scatter(
                    x=plot_data["TimeStamp"],
                    y=plot_data[tag1],
                    mode="lines",
                    name=tag1,
                ),
                secondary_y=False,
            )
            fig2.add_trace(
                go.Scatter(
                    x=plot_data["TimeStamp"],
                    y=plot_data[tag2],
                    mode="lines",
                    name=tag2,
                ),
                secondary_y=use_sec_y,
            )

            if "Feed Rate" in plot_data.columns:
                overlay_feed = st.checkbox(
                    "Include Feed Rate", value=False, key="feed_rate_tab2"
                )
                if overlay_feed:
                    fig2.add_trace(
                        go.Scatter(
                            x=plot_data["TimeStamp"],
                            y=plot_data["Feed Rate"],
                            mode="lines",
                            name="Feed Rate",
                        ),
                        secondary_y=False,
                    )

            fig2.update_layout(
                title=dict(
                    text=f"{puffing_target} - {tag1} vs {tag2} Over Time",
                    x=0.5,
                ),
                xaxis_title="Time",
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.2,
                    xanchor="center",
                    x=0.5,
                ),
                height=650,
            )

            if use_sec_y:
                fig2.update_yaxes(title_text=tag1, secondary_y=False)
                fig2.update_yaxes(title_text=tag2, secondary_y=True)

            add_event_history_annotations(fig2, plot_data, event_dates)
            st.plotly_chart(fig2, use_container_width=True)

        # --- TAB 3: Raw Data Table ---
        with tab3:
            st.subheader("📋 Processed Data Table")
            st.dataframe(plot_data, use_container_width=True)
