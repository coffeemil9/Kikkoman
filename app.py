from datetime import datetime, time
import warnings
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import t
import streamlit as st

warnings.filterwarnings("ignore")

# Page Configuration
st.set_page_config(page_title="Soft Water Analyzer", layout="wide")

st.title("📊 Soft Water Log Analysis App")
st.write(
    "A web application integrating Google Colab data analysis workflows. Upload CSV log files to perform analysis."
)

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------


# 1. 4-Row Detailed Process Trends Chart
def plot_process_trends(filtered_data, start_datetime, end_datetime):
    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        specs=[
            [{"secondary_y": True}],
            [{"secondary_y": True}],
            [{"secondary_y": True}],
            [{"secondary_y": True}],
        ],
    )

    # Row 1: FT0911 gpm and Softener Mode
    fig.add_trace(
        go.Scatter(
            x=filtered_data["Datetime"],
            y=filtered_data["FT0911 gpm"],
            name="FT0911 gpm",
            line=dict(color="blue"),
            legend="legend1",
        ),
        row=1,
        col=1,
        secondary_y=False,
    )
    for i, color in zip([1, 2, 3], ["blue", "red", "green"]):
        fig.add_trace(
            go.Scatter(
                x=filtered_data["Datetime"],
                y=filtered_data[f"Softner{i} Mode"],
                name=f"Softner{i} Mode",
                mode="lines",
                line=dict(color=color, dash="dot"),
                legend="legend1",
            ),
            row=1,
            col=1,
            secondary_y=True,
        )

    # Row 2: PT0911 psi and Softener Mode
    fig.add_trace(
        go.Scatter(
            x=filtered_data["Datetime"],
            y=filtered_data["PT0911 psi"],
            name="PT0911 psi",
            line=dict(color="cyan"),
            legend="legend2",
        ),
        row=2,
        col=1,
        secondary_y=False,
    )
    for i, color in zip([1, 2, 3], ["blue", "red", "green"]):
        fig.add_trace(
            go.Scatter(
                x=filtered_data["Datetime"],
                y=filtered_data[f"Softner{i} Mode"],
                name=f"Softner{i} Mode",
                mode="lines",
                line=dict(color=color, dash="dot"),
                showlegend=True,
                legend="legend2",
            ),
            row=2,
            col=1,
            secondary_y=True,
        )

    # Row 3: Tank Levels and Softener Mode
    for col_name, color in zip(
        ["V0910 Tank Level", "V0907 Tank Level", "V0909 Tank Level"],
        ["purple", "orange", "brown"],
    ):
        fig.add_trace(
            go.Scatter(
                x=filtered_data["Datetime"],
                y=filtered_data[col_name],
                name=col_name,
                mode="lines",
                line=dict(color=color),
                legend="legend3",
            ),
            row=3,
            col=1,
            secondary_y=False,
        )

    for i, color in zip([1, 2, 3], ["blue", "red", "green"]):
        fig.add_trace(
            go.Scatter(
                x=filtered_data["Datetime"],
                y=filtered_data[f"Softner{i} Mode"],
                name=f"Softner{i} Mode",
                mode="lines",
                line=dict(color=color, dash="dot"),
                showlegend=True,
                legend="legend3",
            ),
            row=3,
            col=1,
            secondary_y=True,
        )

    # Row 4: Softener Flow Rates and Softener Mode
    for i, color in zip([1, 2, 3], ["blue", "red", "green"]):
        fig.add_trace(
            go.Scatter(
                x=filtered_data["Datetime"],
                y=filtered_data[f"Softener{i} Flow Rate gpm"],
                name=f"Softener{i} Flow Rate (gpm)",
                mode="lines",
                line=dict(color=color),
                legend="legend4",
            ),
            row=4,
            col=1,
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=filtered_data["Datetime"],
                y=filtered_data[f"Softner{i} Mode"],
                name=f"Softner{i} Mode",
                mode="lines",
                line=dict(color=color, dash="dot"),
                showlegend=True,
                legend="legend4",
            ),
            row=4,
            col=1,
            secondary_y=True,
        )

    base_legend_style = dict(
        orientation="h",
        xanchor="center",
        x=0.5,
        bgcolor="rgba(255, 255, 255, 0.7)",
        bordercolor="gray",
        borderwidth=1,
    )

    fig.update_layout(
        title_text=f"Process Trends ({start_datetime.strftime('%Y-%m-%d %H:%M')} to {end_datetime.strftime('%Y-%m-%d %H:%M')})",
        title_x=0.5,
        hovermode="x unified",
        height=1000,
        legend1=dict(**base_legend_style, yanchor="top", y=0.78),
        legend2=dict(**base_legend_style, yanchor="top", y=0.51),
        legend3=dict(**base_legend_style, yanchor="top", y=0.24),
        legend4=dict(**base_legend_style, yanchor="top", y=-0.05),
    )

    mode_axis_config = dict(
        title_text="Softener Mode",
        tickvals=[1, 2, 4, 8, 16],
        ticktext=[
            "OFFLINE",
            "IN SERVICE",
            "IN REGEN",
            "REGEN COMP",
            "STANDBY",
        ],
        showgrid=False,
        mirror=True,
        linewidth=1,
        linecolor="black",
    )

    fig.update_yaxes(
        title_text="FT0911 (gpm)",
        row=1,
        col=1,
        secondary_y=False,
        showgrid=True,
    )
    fig.update_yaxes(secondary_y=True, row=1, col=1, **mode_axis_config)

    fig.update_yaxes(
        title_text="PT0911 (PSI)",
        row=2,
        col=1,
        secondary_y=False,
        showgrid=True,
    )
    fig.update_yaxes(secondary_y=True, row=2, col=1, **mode_axis_config)

    fig.update_yaxes(
        title_text="Tank Level (%)",
        row=3,
        col=1,
        secondary_y=False,
        showgrid=True,
    )
    fig.update_yaxes(secondary_y=True, row=3, col=1, **mode_axis_config)

    fig.update_yaxes(
        title_text="Softener Flow Rate (gpm)",
        row=4,
        col=1,
        secondary_y=False,
        showgrid=True,
    )
    fig.update_yaxes(secondary_y=True, row=4, col=1, **mode_axis_config)

    return fig


# 2. Prolonged Zero Flow Event Detection Function
def find_prolonged_zero_flow_events(
    df, softener_flow_col, softener_mode_col, min_duration_minutes
):
    df = df.sort_values(by="Datetime").reset_index(drop=True)
    is_zero_flow_in_service = (df[softener_mode_col] == 2) & (
        df[softener_flow_col] == 0
    )

    block_starts = is_zero_flow_in_service & (
        ~is_zero_flow_in_service.shift(1).fillna(False)
    )
    block_ids = block_starts.cumsum()

    events = []
    for block_id in block_ids.unique():
        if block_id == 0:
            continue
        current_block = df[is_zero_flow_in_service & (block_ids == block_id)]
        if not current_block.empty:
            duration = len(current_block)
            if duration >= min_duration_minutes:
                start_time = current_block["Datetime"].min()
                end_time = current_block["Datetime"].max()
                events.append(
                    {
                        "Start Time": start_time,
                        "End Time": end_time,
                        "Duration (minutes)": duration,
                    }
                )
    return events


# ---------------------------------------------------------
# MAIN APP FLOW
# ---------------------------------------------------------

# Sidebar: File Upload
st.sidebar.header("📁 Data Loading")
uploaded_files = st.sidebar.file_uploader(
    "Select Softener Log CSV files (Multiple files allowed)",
    type=["csv"],
    accept_multiple_files=True,
)

if uploaded_files:
    data = pd.DataFrame()
    for file in uploaded_files:
        tmp = pd.read_csv(file)
        data = pd.concat([data, tmp], axis=0)

    # Datetime Parsing and Sorting
    data["Datetime"] = pd.to_datetime(data["DATE"] + " " + data["TIME"])
    data.drop_duplicates(["Datetime"], inplace=True)
    data["Day of Week"] = data["Datetime"].dt.day_name()
    data["Hour"] = data["Datetime"].dt.hour
    data = data.sort_values(by="Datetime")

    # Flow Rate Calculation and Cleaning
    for i in [1, 2, 3]:
        total_col = f"Softner{i} total flow"
        mode_col = f"Softner{i} Mode"
        rate_col = f"Softener{i} Flow Rate gpm"

        data[rate_col] = (data[total_col] - data[total_col].shift(1)) * 100
        data.loc[data[mode_col] != 2, rate_col] = 0
        data.loc[(data[rate_col] < 0) | (data[rate_col] > 300), rate_col] = (
            np.nan
        )

        mean_in_service = data.loc[data[mode_col] == 2, rate_col].mean()
        data[rate_col].fillna(mean_in_service, inplace=True)

    # ---------------------------------------------------------
    # Navigation Tabs
    # ---------------------------------------------------------
    tab1, tab2, tab3 = st.tabs(
        [
            "📈 4-Row Trend Analysis",
            "🔍 Prolonged Zero Flow Events",
            "📊 Statistics & Distribution Analysis",
        ]
    )

    # --- TAB 1: 4-Row Process Trends ---
    with tab1:
        st.subheader("4-Row Detailed Process Trends")

        min_dt = data["Datetime"].min()
        max_dt = data["Datetime"].max()

        # Date & Time Selection UI
        col_d1, col_t1, col_d2, col_t2 = st.columns(4)
        start_date = col_d1.date_input("Start Date", min_dt.date())
        start_time = col_t1.time_input("Start Time", time(0, 0))
        end_date = col_d2.date_input("End Date", max_dt.date())
        end_time = col_t2.time_input("End Time", time(23, 59))

        start_dt = pd.to_datetime(f"{start_date} {start_time}")
        end_dt = pd.to_datetime(f"{end_date} {end_time}")

        filtered_df = data[
            (data["Datetime"] >= start_dt) & (data["Datetime"] <= end_dt)
        ]

        if not filtered_df.empty:
            fig_4row = plot_process_trends(filtered_df, start_dt, end_dt)
            st.plotly_chart(fig_4row, use_container_width=True)
        else:
            st.warning("No data available for the selected date and time range.")

    # --- TAB 2: Zero Flow Event Detection & Summary Chart ---
    with tab2:
        st.subheader("⚠️ Prolonged Zero Flow Events (In-Service Anomaly Detection)")
        st.write(
            "Extracts events where the Softener was 'IN SERVICE' but the measured flow rate was zero."
        )

        min_dur = st.number_input(
            "Minimum duration threshold (minutes)", min_value=1, value=30, step=5
        )

        # Detect Events for Softeners 1, 2, and 3
        softener1_events = find_prolonged_zero_flow_events(
            data, "Softener1 Flow Rate gpm", "Softner1 Mode", min_dur
        )
        softener2_events = find_prolonged_zero_flow_events(
            data, "Softener2 Flow Rate gpm", "Softner2 Mode", min_dur
        )
        softener3_events = find_prolonged_zero_flow_events(
            data, "Softener3 Flow Rate gpm", "Softner3 Mode", min_dur
        )

        # 1. Zero Flow Event Counts Summary
        st.subheader(
            f"📊 Summary: Number of prolonged zero flow events (>= {min_dur} minutes)"
        )

        zero_flow_counts = pd.DataFrame(
            {
                "Softener": ["Softener 1", "Softener 2", "Softener 3"],
                "Count of Prolonged Zero Flow Events": [
                    len(softener1_events),
                    len(softener2_events),
                    len(softener3_events),
                ],
            }
        )

        st.dataframe(zero_flow_counts, use_container_width=True)

        fig_counts = px.bar(
            zero_flow_counts,
            x="Softener",
            y="Count of Prolonged Zero Flow Events",
            title=f"Count of Prolonged Zero Flow Events (>= {min_dur} minutes) while IN SERVICE",
            labels={"Count of Prolonged Zero Flow Events": "Number of Events"},
            color="Softener",
            color_discrete_sequence=px.colors.qualitative.Plotly,
        )

        fig_counts.update_layout(title_x=0.5)
        fig_counts.update_traces(
            texttemplate="%{y}",
            textposition="outside",
            marker_line_color="black",
            marker_line_width=1,
        )

        st.plotly_chart(fig_counts, use_container_width=True)

        st.markdown("---")

        # 2. Detailed Event Log Tables per Softener
        st.subheader("📋 Detailed Event Logs")

        all_events_dict = {
            "Softener 1": softener1_events,
            "Softener 2": softener2_events,
            "Softener 3": softener3_events,
        }

        for name, events_list in all_events_dict.items():
            st.write(f"### 🔹 {name} Event List")
            if events_list:
                st.dataframe(pd.DataFrame(events_list), use_container_width=True)
            else:
                st.success(
                    f"{name}: No zero flow anomalies found matching the specified duration ({min_dur}+ mins)."
                )

    # --- TAB 3: Statistics and Distribution Plots ---
    with tab3:
        st.subheader("📊 FT0911 gpm & Moving Averages / Distribution Analysis")

        # Set DatetimeIndex for Rolling Calculations
        data_indexed = data.copy()
        data_indexed["Datetime"] = pd.to_datetime(data_indexed["Datetime"])
        data_indexed = data_indexed.set_index("Datetime").sort_index()

        # Moving Averages
        data["FT0911 gpm_MA_1H"] = (
            data_indexed["FT0911 gpm"].rolling(window="1h").mean().values
        )
        data["FT0911 gpm_MA_6H"] = (
            data_indexed["FT0911 gpm"].rolling(window="6h").mean().values
        )
        data["FT0911 gpm_MA_24H"] = (
            data_indexed["FT0911 gpm"].rolling(window="24h").mean().values
        )

        # FT0911 & PT0911 Moving Average Chart
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        fig_trend.add_trace(
            go.Scatter(
                x=data["Datetime"], y=data["FT0911 gpm"], name="FT0911 gpm"
            ),
            secondary_y=False,
        )
        fig_trend.add_trace(
            go.Scatter(
                x=data["Datetime"], y=data["PT0911 psi"], name="PT0911 psi"
            ),
            secondary_y=True,
        )

        fig_trend.add_trace(
            go.Scatter(
                x=data["Datetime"],
                y=data["FT0911 gpm_MA_1H"],
                name="1H MA",
                line=dict(dash="dot"),
            ),
            secondary_y=False,
        )
        fig_trend.add_trace(
            go.Scatter(
                x=data["Datetime"],
                y=data["FT0911 gpm_MA_6H"],
                name="6H MA",
                line=dict(dash="dash"),
            ),
            secondary_y=False,
        )
        fig_trend.add_trace(
            go.Scatter(
                x=data["Datetime"],
                y=data["FT0911 gpm_MA_24H"],
                name="24H MA",
                line=dict(dash="longdash"),
            ),
            secondary_y=False,
        )

        fig_trend.update_layout(
            title_text="FT0911 gpm & Moving Averages", title_x=0.5
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        # Standalone Tank Levels Chart
        st.subheader("🛢️ Tank Levels over Time")
        fig_tank = go.Figure()
        fig_tank.add_trace(
            go.Scatter(
                x=data["Datetime"],
                y=data["V0910 Tank Level"],
                name="V0910 Tank Level",
            )
        )
        fig_tank.add_trace(
            go.Scatter(
                x=data["Datetime"],
                y=data["V0909 Tank Level"],
                name="V0909 Tank Level",
            )
        )
        fig_tank.add_trace(
            go.Scatter(
                x=data["Datetime"],
                y=data["V0907 Tank Level"],
                name="V0907 Tank Level",
            )
        )
        fig_tank.update_layout(
            title_text="Tank Levels over Time",
            title_x=0.5,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
            ),
            yaxis_title="Tank Level",
        )
        st.plotly_chart(fig_tank, use_container_width=True)

        # Statistical Metrics
        mean_ft = data["FT0911 gpm"].mean()
        median_ft = data["FT0911 gpm"].median()
        std_dev_ft = data["FT0911 gpm"].std()
        n = len(data["FT0911 gpm"])
        t_score = t.ppf((1 + 0.95) / 2, n - 1)
        margin_of_error = t_score * (std_dev_ft / np.sqrt(n))

        ci_lower = mean_ft - margin_of_error
        ci_upper = mean_ft + margin_of_error

        c1, c2, c3 = st.columns(3)
        c1.metric("Mean FT0911 gpm", f"{mean_ft:.2f}")
        c2.metric("Median FT0911 gpm", f"{median_ft:.2f}")
        c3.metric("95% CI", f"({ci_lower:.2f}, {ci_upper:.2f})")

        # Histogram with Black Outlines
        fig_hist = px.histogram(
            data,
            x="FT0911 gpm",
            nbins=150,
            title="Distribution of FT0911 gpm",
        )
        fig_hist.add_vline(
            x=mean_ft,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {mean_ft:.2f}",
        )
        fig_hist.add_vline(
            x=median_ft,
            line_dash="dash",
            line_color="green",
            annotation_text=f"Median: {median_ft:.2f}",
        )
        fig_hist.add_vline(
            x=ci_lower,
            line_dash="dot",
            line_color="purple",
            annotation_text=f"95% CI Lower: {ci_lower:.2f}",
        )
        fig_hist.add_vline(
            x=ci_upper,
            line_dash="dot",
            line_color="purple",
            annotation_text=f"95% CI Upper: {ci_upper:.2f}",
        )

        fig_hist.update_traces(marker_line_color="black", marker_line_width=1)
        fig_hist.update_layout(title_x=0.5)

        st.plotly_chart(fig_hist, use_container_width=True)

        # Overall Violin Plot
        st.subheader("🎻 Overall Violin Plot of FT0911 gpm")
        fig_violin = px.violin(
            data,
            y="FT0911 gpm",
            box=True,
            points="all",
            title="Violin Plot of FT0911 gpm Distribution",
        )
        fig_violin.update_layout(title_x=0.5)
        st.plotly_chart(fig_violin, use_container_width=True)

        # Hourly Box Plot
        st.subheader("📦 Distribution of FT0911 gpm by Hour of Day (Box Plot)")
        fig_hourly_box = go.Figure()
        hourly_means = []
        hours = []

        for hour in range(24):
            hourly_data = data[data["Hour"] == hour]["FT0911 gpm"]
            if not hourly_data.empty:
                fig_hourly_box.add_trace(
                    go.Box(
                        y=hourly_data,
                        name=f"{hour}hr",
                        boxpoints="outliers",
                        line_width=1,
                    )
                )
                hourly_means.append(hourly_data.mean())
                hours.append(hour)

        fig_hourly_box.add_trace(
            go.Scatter(
                x=[f"{h}hr" for h in hours],
                y=hourly_means,
                mode="lines+markers+text",
                name="Hourly Mean",
                marker=dict(color="red", size=8),
                line=dict(color="red", width=2),
                text=[f"{m:.2f}" for m in hourly_means],
                textposition="top center",
            )
        )

        fig_hourly_box.update_layout(
            title="Distribution of FT0911 gpm by Hour of Day (Box Plot with Hourly Mean)",
            title_x=0.5,
            xaxis_title="Hour of Day",
            yaxis_title="FT0911 gpm",
            height=600,
            showlegend=True,
            hovermode="x unified",
        )
        st.plotly_chart(fig_hourly_box, use_container_width=True)

        # Hourly Violin Plot (Overall)
        st.subheader(
            "🎻 Density Distribution of FT0911 gpm by Hour of Day (Violin Plot)"
        )
        fig_hourly_violin = go.Figure()
        colors = px.colors.qualitative.Alphabet
        hourly_means_v = []
        hours_v = []

        for hour in range(24):
            hourly_data = data[data["Hour"] == hour]["FT0911 gpm"]

            if not hourly_data.empty:
                color_index = hour % len(colors)
                current_color = colors[color_index]

                fig_hourly_violin.add_trace(
                    go.Violin(
                        y=hourly_data,
                        name=f"{hour}hr",
                        box_visible=True,
                        meanline_visible=True,
                        points=False,
                        line_color="black",
                        line_width=1,
                        fillcolor=current_color,
                        opacity=0.6,
                        scalemode="count",
                    )
                )
                hourly_means_v.append(hourly_data.mean())
                hours_v.append(hour)

        fig_hourly_violin.add_trace(
            go.Scatter(
                x=[f"{h}hr" for h in hours_v],
                y=hourly_means_v,
                mode="lines+markers+text",
                name="Hourly Mean",
                marker=dict(color="red", size=8),
                line=dict(color="red", width=2),
                text=[f"{m:.2f}" for m in hourly_means_v],
                textposition="top center",
            )
        )

        fig_hourly_violin.update_layout(
            title="Density Distribution of FT0911 gpm by Hour of Day (Violin Plot with Hourly Mean)",
            title_x=0.5,
            xaxis_title="Hour of Day",
            yaxis_title="FT0911 gpm",
            height=700,
            violingap=0,
            violinmode="overlay",
            showlegend=True,
            xaxis=dict(tickmode="linear", tick0=0, dtick=1),
            hovermode="x unified",
        )
        st.plotly_chart(fig_hourly_violin, use_container_width=True)

        # Bar Chart by Day of Week with Standard Deviation Error Bars
        st.subheader("📅 Average FT0911 gpm by Day of Week")

        daily_stats_gpm = (
            data.groupby("Day of Week")["FT0911 gpm"]
            .agg(["mean", "std"])
            .reset_index()
        )
        daily_stats_gpm.rename(
            columns={"mean": "Mean FT0911 gpm", "std": "Std FT0911 gpm"},
            inplace=True,
        )

        day_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        daily_stats_gpm["Day of Week"] = pd.Categorical(
            daily_stats_gpm["Day of Week"], categories=day_order, ordered=True
        )
        daily_stats_gpm = daily_stats_gpm.sort_values("Day of Week")

        fig_day_bar = px.bar(
            daily_stats_gpm,
            x="Day of Week",
            y="Mean FT0911 gpm",
            error_y="Std FT0911 gpm",
            title="Average FT0911 gpm by Day of Week with Standard Deviation",
            labels={"Mean FT0911 gpm": "Average FT0911 gpm"},
            color="Day of Week",
            color_discrete_sequence=px.colors.qualitative.Plotly,
        )

        fig_day_bar.update_layout(
            title_x=0.5,
            yaxis_title="Average FT0911 gpm",
            xaxis_title="Day of Week",
        )

        fig_day_bar.update_traces(
            marker_line_color="black",
            marker_line_width=1,
            texttemplate="%{y:.2f}",
            textposition="outside",
        )

        st.plotly_chart(fig_day_bar, use_container_width=True)

        # Violin Plot by Hour for Each Day of Week
        st.subheader(
            "📅🎻 Density Distribution of FT0911 gpm by Hour for Each Day of Week"
        )

        unique_days = data["Day of Week"].unique()
        sorted_unique_days = [d for d in day_order if d in unique_days]

        selected_day = st.radio(
            "Select a day of the week:", sorted_unique_days, horizontal=True
        )

        if selected_day:
            day_data = data[data["Day of Week"] == selected_day]

            fig_day_hourly_v = go.Figure()
            colors_day = px.colors.qualitative.Alphabet

            hourly_means_d = []
            hours_d = []

            for hour in range(24):
                hourly_data = day_data[day_data["Hour"] == hour]["FT0911 gpm"]

                if not hourly_data.empty:
                    color_index = hour % len(colors_day)
                    current_color = colors_day[color_index]

                    fig_day_hourly_v.add_trace(
                        go.Violin(
                            y=hourly_data,
                            name=f"{hour}hr",
                            box_visible=True,
                            meanline_visible=True,
                            points=False,
                            line_color="black",
                            line_width=1,
                            fillcolor=current_color,
                            opacity=0.6,
                            scalemode="count",
                        )
                    )
                    hourly_means_d.append(hourly_data.mean())
                    hours_d.append(hour)

            if hours_d:
                fig_day_hourly_v.add_trace(
                    go.Scatter(
                        x=[f"{h}hr" for h in hours_d],
                        y=hourly_means_d,
                        mode="lines+markers+text",
                        name="Hourly Mean",
                        marker=dict(color="red", size=8),
                        line=dict(color="red", width=2),
                        text=[f"{m:.2f}" for m in hourly_means_d],
                        textposition="top center",
                    )
                )

            fig_day_hourly_v.update_layout(
                title=f"Density Distribution of FT0911 gpm by Hour on {selected_day} (Violin Plot with Hourly Mean)",
                title_x=0.5,
                xaxis_title="Hour of Day",
                yaxis_title="FT0911 gpm",
                height=700,
                violingap=0,
                violinmode="overlay",
                showlegend=True,
                xaxis=dict(tickmode="linear", tick0=0, dtick=1),
                hovermode="x unified",
            )

            st.plotly_chart(fig_day_hourly_v, use_container_width=True)

else:
    st.info("👈 Please upload Softener Log CSV file(s) using the sidebar.")
