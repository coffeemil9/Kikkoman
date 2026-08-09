from datetime import datetime, time
import glob
import os
import re
import warnings
import matplotlib.pyplot as plt
import numpy as np
import openpyxl
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import t
import seaborn as sns
import streamlit as st
import tqdm

warnings.filterwarnings("ignore")

# ページの設定
st.set_page_config(page_title="Water Usage Analyzer", layout="wide")

st.title("🌊 Water Usage Analyzer (Integrated Streamlit App)")
st.write(
    "Google Colabおよび自作モジュール (modules.py / WUS) のすべての分析機能を統合したアプリケーションです。"
)

# ---------------------------------------------------------
# HELPER FUNCTIONS & CLASSES (Integrated from modules.py)
# ---------------------------------------------------------


# --- Soft Water Analysis Functions ---
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

    # 1. FT0911 gpm & Softener Mode
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

    # 2. PT0911 psi & Softener Mode
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

    # 3. Tank Levels & Softener Mode
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

    # 4. Softener Flow Rates & Softener Mode
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


# --- WUS Class Functions (Integrated for Streamlit) ---
def process_filtration_room_df(data_rdfr, window_size):
    data_rdfr["year"] = (
        data_rdfr["Time"]
        .apply(lambda x: str(x).split("/")[2].split(" ")[0])
        .astype(int)
    )
    data_rdfr["month"] = (
        data_rdfr["Time"].apply(lambda x: str(x).split("/")[0]).astype(int)
    )
    data_rdfr["day"] = (
        data_rdfr["Time"].apply(lambda x: str(x).split("/")[1]).astype(int)
    )

    data_rdfr["Date"] = (
        data_rdfr["year"].astype(str)
        + "-"
        + data_rdfr["month"].astype(str)
        + "-"
        + data_rdfr["day"].astype(str)
    )
    data_rdfr["Date"] = pd.to_datetime(data_rdfr["Date"], errors="coerce")

    data_rdfr["time_str"] = data_rdfr["Time"].astype(str).str.split(" ").str[-1]
    data_rdfr["time"] = pd.to_datetime(
        data_rdfr["time_str"], format="%H:%M", errors="coerce"
    )

    data_rdfr.drop_duplicates(
        subset=["year", "month", "day", "time_str"], inplace=True
    )
    data_rdfr.sort_values(by=["year", "month", "day", "time_str"], inplace=True)

    # Interpolation
    if "Final Filtration 1.2 (Flow Rate)" in data_rdfr.columns:
        data_rdfr["Final Filtration 1.2 (Flow Rate)"] = data_rdfr[
            "Final Filtration 1.2 (Flow Rate)"
        ].replace(0, np.nan)
        rolling_avg = data_rdfr[
            "Final Filtration 1.2 (Flow Rate)"
        ].rolling(window=window_size, center=True, min_periods=5).mean()
        data_rdfr["Final Filtration 1.2 (Flow Rate)_interpolited"] = data_rdfr[
            "Final Filtration 1.2 (Flow Rate)"
        ].fillna(rolling_avg)

        rolling_sum = data_rdfr[
            "Final Filtration 1.2 (Flow Rate)"
        ].rolling(window=window_size, center=True, min_periods=5).sum()
        rolling_avg_no_self = (
            rolling_sum
            - data_rdfr["Final Filtration 1.2 (Flow Rate)_interpolited"]
        ) / (window_size - 1)
        data_rdfr[
            "Final Filtration 1.2 (Flow Rate)_interpolited_no_self"
        ] = data_rdfr[
            "Final Filtration 1.2 (Flow Rate)_interpolited"
        ].fillna(rolling_avg_no_self)

    return data_rdfr


def scatter_plot_wus(data, year_range, x_col, y_col):
    fig = go.Figure()
    for year in year_range:
        if "year" in data.columns:
            extract_data = data[data["year"] == year]
        else:
            extract_data = data
        fig.add_trace(
            go.Scatter(
                x=extract_data[x_col],
                y=extract_data[y_col],
                mode="markers",
                marker=dict(size=8, line=dict(width=0.5, color="black")),
                name=f"year : {year}",
                customdata=(
                    extract_data[["year", "month", "day"]]
                    if all(c in extract_data.columns for c in ["year", "month", "day"])
                    else None
                ),
                hovertemplate=(
                    "<b>Filter (X)</b>: %{x:,.0f}<br>"
                    + "<b>Flow Rate (Y)</b>: %{y:,.0f}<br><extra></extra>"
                ),
            )
        )

    fig.add_trace(
        go.Scatter(
            x=[0, 800000],
            y=[0, 800000],
            mode="lines",
            name="y=x Line",
            line=dict(color="red", dash="dash"),
            opacity=0.75,
            hoverinfo="skip",
        )
    )

    fig.update_layout(
        title="Scatter Plot of Flow Rate vs. Filter with y=x Reference",
        title_x=0.5,
        xaxis_title=f"{x_col}",
        yaxis_title=f"{y_col}",
        xaxis=dict(
            range=[0, 800000],
            showgrid=True,
            gridcolor="lightgrey",
            griddash="dot",
            tickformat=",.0f",
        ),
        yaxis=dict(
            range=[0, 800000],
            showgrid=True,
            gridcolor="lightgrey",
            griddash="dot",
            tickformat=",.0f",
        ),
        height=700,
        showlegend=True,
    )
    return fig


# ---------------------------------------------------------
# MAIN APP NAVIGATION
# ---------------------------------------------------------

st.sidebar.title("📌 モード選択")
app_mode = st.sidebar.radio(
    "分析機能を選択してください:",
    [
        "💧 Soft Water Analysis",
        "🏭 Filtration Room Analysis",
        "🔋 Well / CDA Water Usage",
        "📈 WUS Scatter & Year Trend Plot",
    ],
)

# =========================================================
# 1. SOFT WATER ANALYSIS
# =========================================================
if app_mode == "💧 Soft Water Analysis":
    st.header("💧 Soft Water Log Analysis")

    uploaded_files = st.sidebar.file_uploader(
        "SoftnerログCSVファイルを選択（複数可）",
        type=["csv"],
        accept_multiple_files=True,
        key="soft_water",
    )

    if uploaded_files:
        data = pd.DataFrame()
        for file in uploaded_files:
            tmp = pd.read_csv(file)
            data = pd.concat([data, tmp], axis=0)

        data["Datetime"] = pd.to_datetime(data["DATE"] + " " + data["TIME"])
        data.drop_duplicates(["Datetime"], inplace=True)
        data["Day of Week"] = data["Datetime"].dt.day_name()
        data = data.sort_values(by="Datetime")

        for i in [1, 2, 3]:
            total_col = f"Softner{i} total flow"
            mode_col = f"Softner{i} Mode"
            rate_col = f"Softener{i} Flow Rate gpm"

            data[rate_col] = (data[total_col] - data[total_col].shift(1)) * 100
            data.loc[data[mode_col] != 2, rate_col] = 0
            data.loc[
                (data[rate_col] < 0) | (data[rate_col] > 300), rate_col
            ] = np.nan

            mean_in_service = data.loc[data[mode_col] == 2, rate_col].mean()
            data[rate_col].fillna(mean_in_service, inplace=True)

        tab1, tab2, tab3 = st.tabs(
            [
                "📈 4段トレンド解析",
                "🔍 トラブル自動検知 (Zero Flow)",
                "📊 統計 & ヒストグラム/バイオリン",
            ]
        )

        with tab1:
            st.subheader("4-Row Detailed Process Trends")
            min_date = data["Datetime"].min().date()
            max_date = data["Datetime"].max().date()

            col_d1, col_d2 = st.columns(2)
            start_date = col_d1.date_input("開始日", min_date)
            end_date = col_d2.date_input("終了日", max_date)

            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1)

            filtered_df = data[
                (data["Datetime"] >= start_dt) & (data["Datetime"] < end_dt)
            ]

            if not filtered_df.empty:
                fig_4row = plot_process_trends(filtered_df, start_dt, end_dt)
                st.plotly_chart(fig_4row, use_container_width=True)

        with tab2:
            st.subheader("⚠️ Prolonged Zero Flow Events")
            min_dur = st.number_input(
                "判定する最小継続時間（分）", min_value=1, value=15, step=5
            )

            for i in [1, 2, 3]:
                events = find_prolonged_zero_flow_events(
                    data,
                    f"Softener{i} Flow Rate gpm",
                    f"Softner{i} Mode",
                    min_dur,
                )
                st.write(f"### 🔹 Softener #{i} 異常検知結果")
                if events:
                    st.dataframe(pd.DataFrame(events), use_container_width=True)
                else:
                    st.success(
                        f"Softener #{i}: {min_dur}分以上のゼロ流量異常はありません。"
                    )

        with tab3:
            st.subheader("📊 FT0911 gpm & 移動平均 / 分布解析")
            data_indexed = data.copy()
            data_indexed["Datetime"] = pd.to_datetime(data_indexed["Datetime"])
            data_indexed = data_indexed.set_index("Datetime").sort_index()

            data["FT0911 gpm_MA_1H"] = (
                data_indexed["FT0911 gpm"].rolling(window="1h").mean().values
            )
            data["FT0911 gpm_MA_6H"] = (
                data_indexed["FT0911 gpm"].rolling(window="6h").mean().values
            )
            data["FT0911 gpm_MA_24H"] = (
                data_indexed["FT0911 gpm"].rolling(window="24h").mean().values
            )

            fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
            fig_trend.add_trace(
                go.Scatter(
                    x=data["Datetime"],
                    y=data["FT0911 gpm"],
                    name="FT0911 gpm",
                ),
                secondary_y=False,
            )
            fig_trend.add_trace(
                go.Scatter(
                    x=data["Datetime"],
                    y=data["PT0911 psi"],
                    name="PT0911 psi",
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

            st.plotly_chart(fig_trend, use_container_width=True)

            mean_ft = data["FT0911 gpm"].mean()
            median_ft = data["FT0911 gpm"].median()
            std_dev_ft = data["FT0911 gpm"].std()
            n = len(data["FT0911 gpm"])
            t_score = t.ppf((1 + 0.95) / 2, n - 1)
            margin_of_error = t_score * (std_dev_ft / np.sqrt(n))

            c1, c2, c3 = st.columns(3)
            c1.metric("Mean FT0911 gpm", f"{mean_ft:.2f}")
            c2.metric("Median FT0911 gpm", f"{median_ft:.2f}")
            c3.metric(
                "95% CI",
                f"({mean_ft - margin_of_error:.2f}, {mean_ft + margin_of_error:.2f})",
            )

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
            fig_hist.update_traces(
                marker_line_color="black", marker_line_width=1
            )
            fig_hist.update_layout(title_x=0.5)
            st.plotly_chart(fig_hist, use_container_width=True)

            fig_violin = px.violin(
                data,
                y="FT0911 gpm",
                box=True,
                points="all",
                title="Violin Plot of FT0911 gpm Distribution",
            )
            fig_violin.update_layout(title_x=0.5)
            st.plotly_chart(fig_violin, use_container_width=True)

    else:
        st.info("👈 左側のサイドバーからSoftnerログCSVファイルをアップロードしてください。")

# =========================================================
# 2. FILTRATION ROOM ANALYSIS
# =========================================================
elif app_mode == "🏭 Filtration Room Analysis":
    st.header("🏭 Filtration Room Data Processing & Interpolation")

    uploaded_filt = st.sidebar.file_uploader(
        "Filtration Room CSVファイルを選択（複数可）",
        type=["csv"],
        accept_multiple_files=True,
        key="filt_room",
    )
    window_size = st.sidebar.number_input(
        "補間ウィンドウサイズ (window_size)", min_value=3, value=15, step=2
    )

    if uploaded_filt:
        df_filt = pd.DataFrame()
        for f in uploaded_filt:
            tmp = pd.read_csv(f)
            df_filt = pd.concat([df_filt, tmp], axis=0, ignore_index=True)

        processed_df = process_filtration_room_df(df_filt, window_size)

        st.subheader("📋 処理済みデータプレビュー")
        st.dataframe(processed_df.head(100), use_container_width=True)

        if "Final Filtration 1.2 (Flow Rate)" in processed_df.columns:
            st.subheader("📈 補間前後データの比較トレンド")
            fig_filt = go.Figure()
            fig_filt.add_trace(
                go.Scatter(
                    x=processed_df["Date"],
                    y=processed_df["Final Filtration 1.2 (Flow Rate)"],
                    name="Original Flow Rate",
                    mode="lines",
                )
            )
            fig_filt.add_trace(
                go.Scatter(
                    x=processed_df["Date"],
                    y=processed_df[
                        "Final Filtration 1.2 (Flow Rate)_interpolited"
                    ],
                    name="Interpolated Flow Rate",
                    mode="lines",
                    line=dict(dash="dot"),
                )
            )
            st.plotly_chart(fig_filt, use_container_width=True)
    else:
        st.info("👈 サイドバーからFiltration Room CSVファイルをアップロードしてください。")

# =========================================================
# 3. WELL / CDA WATER USAGE
# =========================================================
elif app_mode == "🔋 Well / CDA Water Usage":
    st.header("🔋 Well Water / CDA Usage Processing")

    uploaded_cda = st.sidebar.file_uploader(
        "Well Water Usage CSVを選択", type=["csv"], key="cda_file"
    )

    if uploaded_cda:
        df_cda = pd.read_csv(uploaded_cda)
        df_cda.dropna(inplace=True)
        df_cda.columns = df_cda.columns.str.strip()

        df_cda["year"] = (
            df_cda["Date"]
            .apply(lambda x: str(x).split("/")[2].split(" ")[-1])
            .astype(int)
        )
        df_cda["month"] = (
            df_cda["Date"].apply(lambda x: str(x).split("/")[0]).astype(int)
        )
        df_cda["day"] = (
            df_cda["Date"].apply(lambda x: str(x).split("/")[1]).astype(int)
        )
        df_cda["Formatted_Date"] = pd.to_datetime(
            df_cda["year"].astype(str)
            + "-"
            + df_cda["month"].astype(str)
            + "-"
            + df_cda["day"].astype(str),
            errors="coerce",
        )

        st.subheader("📋 成形済みCDA / Well Water データ")
        st.dataframe(df_cda, use_container_width=True)
    else:
        st.info("👈 サイドバーから Well Water Usage CSVをアップロードしてください。")

# =========================================================
# 4. WUS SCATTER & YEAR TREND PLOT
# =========================================================
elif app_mode == "📈 WUS Scatter & Year Trend Plot":
    st.header("📈 Scatter Plot (Flow Rate vs. Filter with y=x)")

    uploaded_scat = st.sidebar.file_uploader(
        "分析対象データ (CSV) を選択", type=["csv"], key="scatter_file"
    )

    if uploaded_scat:
        df_scat = pd.read_csv(uploaded_scat)

        num_cols = df_scat.select_dtypes(include=[np.number]).columns.tolist()

        if len(num_cols) >= 2:
            c_x, c_y = st.columns(2)
            x_col = c_x.selectbox("X軸カラム選択", num_cols, index=0)
            y_col = c_y.selectbox(
                "Y軸カラム選択",
                num_cols,
                index=1 if len(num_cols) > 1 else 0,
            )

            years = [2024, 2025, 2026]
            fig_scat = scatter_plot_wus(df_scat, years, x_col, y_col)
            st.plotly_chart(fig_scat, use_container_width=True)
        else:
            st.warning("数値データカラムが2つ以上必要です。")
    else:
        st.info("👈 分析用CSVファイルをアップロードしてください。")
