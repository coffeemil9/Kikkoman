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
    'C2003' : 'Feed Rate (Hz) C2003',
    'P2001' : 'CB Current (AMP) P2001',
    'C2006': 'FRV Current (AMP) C2006',
    'C2007': 'BRV Current (AMP) C2007',

    'TT2410': 'FRV Inlet Steam Temp (F) TT2410',
    # Make Up Steam
    'FT2000': 'Make Up Steam Flow Rate (LBs/HR) FT2000',
    'PCV2000': 'Make Up Steam Control (%) PCV2000',
    'PIC2000': 'Make Up Steam Pressure (PSI) PIC2000',
    'PD2302': 'Strainer Differential Pressure (mmH20) PD2302',

    'FT2402': 'Main System Steam Velocity (FT/SEC) FT2402',
    'PT2000': 'Main System Steam Pressure (PSI) PT2000',
    'TIC2000': 'Main System Steam Control Temp (F) TIC200',
    'TT2000': 'Main System Steam Temp (F) TT2000',
    'TT2402': 'Pre-Heater Temp (F) TT2402',

    # Souper Heater
    'TT2413': 'S.H. Inlet Temp (F) TT2413',
    'TIC2403': 'S.H. Outlet Control Temp (F) TIC2403',
    'TT2403': 'S.H. Outlet Temp (F) TT2403',
    'TT2423': 'S.H. Combustion Temp (F) TT2423',
    'TCV2403' : 'S.H. Control Output (%) TCV2403',
    'PT2403' : 'S.H Fuel Gas Feed Pressure (PSI) PT2403',
    'FT2506': 'ByPass Steam Flowrate (LBs/Hr) FT2506', 
    'FT2403': 'Bypass Before S.H. Steam Flowrate (LBs/Hr) FT2403',
    'TT2412' : 'Inlet temp for Cyclon (F) TT2412',
    
    # Cooler 
    'TT2406': 'Cooler Outlet Temp (F) TT2406',
    'TT2416': 'Cooler Inlet Temp (F) TT2416',
    'TT2404': 'Cooler Inlet Cylclon Air Temp (F) TT2404',
    'TT2405': 'Puffed Soy Transfer Air Temp (F) TT2405',
    # Seal Water
    'PT2103': 'CB Seal Water Pressure (PSI) PT2103',
    'FT2103': 'CB Seal Water Flow Rate Driven Side (GPM) FT2103',
    'FT2113': 'CB Seal Water Flow Rate Non-Driven Side (GPM) FT2113',
    'TT1_2006': 'CB Seal Water Temp Driven Side (F)? TT1_2006', # Adam 調査必要
    'TT2_2006': 'CB Seal Water Temp Non-Driven Side (F)? TT1_2006', # Adam 調査必要
    'TT3_2006': 'CB Bearling Cooling Water Temp (F)? TT1_2006', # Adam 調査必要

    'FT2101': 'CB Bearling Cooling Water Flow Rate (GPM) FT2101',

    'PT2205': 'CB Seal Water Back Up Tank Air Pressure (PSI) PT2205',


}

column_mapping_PP2 = {
    'EM2152': 'CB Current (AMP) EM2152',
    'EM25560.': 'FRV Current (AMP) EM25560.',
    'EM25570': 'BRV Current (AMP) EM25570',
    
    # Make Up Steam
    'FT20530': 'Make Up Steam Flow Rate (LBs/HR) FT20530',
    'DPT2357': 'Strainer Differential Pressure DPT2357',

    # Main System Steam
    'PT20510': 'Main System Pressure (PSI) PT20510',
    'PT2051.Out': 'Main System Pressure PID Control (%) PT2051.Out',
    'PT2051.PV': 'Main System Pressure PV (PSI) PT2051.PV',
    'PT2051.SP': 'Main System Pressure SP (PSI) PT2051.SP',

    'FT24540': 'Main System Steam Velocity FT24540',

    'TT2051.out': 'Main System Temp Control (%) TT2051.out',
    'TT2051.PV': 'Main System Temp PV (F) TT2051.PV',
    'TT2051.SP': 'Main System Temp SP (F) TT2051.SP',

    # Super Heater
    'TT2454O.Out': 'S.H. Outlet Control (%) TT2454O.Out',
    'TT2454O.PV': 'S.H. Outlet Temp PV (F) TT2454O.PV',
    'TT2454O.SP': 'S.H. Outlet Temp SP (F) TT2454O.SP',
    'TEMP_TE2454O0': 'S.H. Outlet Temp (F) TEMP_TE2454O0',
    'TEMP_TE2454I': 'S.H. Inlet Temp (F) TEMP_TE2454I',

    'TE20510.': 'Inlet Temp for Cyclone (F) TE20510.',

    # Cooler
    'TEMP_TE2455I0': 'Cooler Inlet Temp (F) TEMP_TE2455I0',
    'TEMP_TE2455O0': 'Cooler Outlet Temp (F) TEMP_TE2455O0',

    # Seal Water
    'PT2152.0': 'CB Seal Water Pressure (PSI) PT2152.0',
    '.[Puffing2.Flow_Rate_FP6.]': 'CB Seal Water Flow Rate Driven Side (GPM) .[Puffing2.Flow_Rate_FP6.]',
    '.[Puffing2.Flow_Rate_FP7.]': 'CB Seal Water Flow Rate Non-Driven Side (GPM) .[Puffing2.Flow_Rate_FP7.]',
    '.[Puffing2.FLOW_RATE_FP8.]': 'CB Bearing Cooling Water Flow Rate (GPM) .[Puffing2.FLOW_RATE_FP8.]',
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

event_dates_for_PP2={
    '2025-11-14 08:00:00': "PP2 Bug <br> Filtter <br> Issue and Solved ",
    '2025-11-11 08:00:00': "Something <br> Wrong <BR> With Pressure",
    '2026-02-01 08:00:00': "PP2 Puffing Exhaust <br> Something Wrong",
    '2026-02-18 07:00:00': "PP2 GearBox Changed <br> PP2 Mechanical Seal <br> Replacements <br> Super Heater <br> PM Conducted",
    '2026-03-19 13:00:00': "PP2 Changed BRV", # この時のBRVのポケットには、多くの原料が詰まっていた。サイドパッキン、グランドパッキンの調整方法が不均一だった。
    '2026-03-31 14:00:00': "PP2 Make UP Steam Control Fix",
    '2026-04-27 7:00:00': "PP2 Changed BRV <br> Due to High Current of BRV",
    '2026-07-03 12:30:00': "temporary power outage",
    '2026-07-08 16:00:00': "Start to process soy",
    '2026-07-17 08:00:00': "Seal Water Pump Exchange",
    '2026-07-17 13:00:00': "Seal Water Pressure Sensore Exchange",

}

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


def get_event_dataframe(event_dates_dict):
    """Convert event dates dictionary into a clean Pandas DataFrame for table display."""
    events_list = []
    for date_str, desc in event_dates_dict.items():
        clean_desc = (
            desc.replace("<br>", " ").replace("<BR>", " ").replace("  ", " ")
        )
        events_list.append(
            {
                "Event Date & Time": pd.to_datetime(date_str),
                "Event Description": clean_desc,
            }
        )
    df_events = pd.DataFrame(events_list)
    if not df_events.empty:
        df_events = df_events.sort_values(
            "Event Date & Time"
        ).reset_index(drop=True)
    return df_events


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

# 2. Auto-load from GitHub Repository (Updated Paths to data/Puffing#1 & data/Puffing#2)
else:
    if puffing_target == "Puffing #1":
        search_dir = "data/Puffing#1"
        fallback_dirs = ["data/PP/PP1", "PP1"]
    else:
        search_dir = "data/Puffing#2"
        fallback_dirs = ["data/PP/PP2", "PP2"]

    search_paths = []
    
    # Direct directory scan for exact folder name matching
    if os.path.exists(search_dir):
        for fname in os.listdir(search_dir):
            if fname.endswith(".csv"):
                search_paths.append(os.path.join(search_dir, fname))
                
    for fb in fallback_dirs:
        if os.path.exists(fb):
            for fname in os.listdir(fb):
                if fname.endswith(".csv"):
                    search_paths.append(os.path.join(fb, fname))

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
            f"👈 Please upload CSV file(s) or add files into `data/Puffing#1/` or `data/Puffing#2/` in your repository."
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
        # Navigation Tabs
        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "📈 Single Tag Trend",
                "🔀 Multi-Tag Comparison",
                "📅 Maintenance & Event Logs",
                "📋 Raw Data Table",
            ]
        )

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

        # --- TAB 3: Maintenance & Event Logs ---
        with tab3:
            st.subheader(f"📅 Registered Event History ({puffing_target})")
            st.write(
                "List of maintenance events, equipment exchanges, and operational issues for the selected unit."
            )

            df_events = get_event_dataframe(event_dates)

            if not df_events.empty:
                filtered_events = df_events[
                    (df_events["Event Date & Time"] >= start_dt)
                    & (df_events["Event Date & Time"] <= end_dt)
                ]

                st.markdown(
                    f"**Events within selected Date Filter ({start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}):**"
                )
                if not filtered_events.empty:
                    st.dataframe(filtered_events, use_container_width=True)
                else:
                    st.info(
                        "No registered events fall within the current date filter range."
                    )

                st.markdown("---")
                st.markdown(
                    f"**All Registered Events for {puffing_target}:**"
                )
                st.dataframe(df_events, use_container_width=True)
            else:
                st.info(f"No events registered for {puffing_target}.")

        # --- TAB 4: Raw Data Table ---
        with tab4:
            st.subheader("📋 Processed Data Table")
            st.dataframe(plot_data, use_container_width=True)
