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

# ページの設定
st.set_page_config(page_title="Soft Water Analyzer", layout="wide")

st.title("📊 Soft Water Log Analysis App")
st.write(
    "Google Colabの分析処理を統合したWebアプリケーションです。CSVファイルをアップロードして分析を実行します。"
)

# ---------------------------------------------------------
# HELPER FUNCTIONS (From modules.py - Soft Water Only)
# ---------------------------------------------------------


# 1. 4段連動プロセスTrendグラフを描画する関数
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


# 2. IN SERVICE（稼働中）にもかかわらず、流量が0のトラブル期間を検知する関数
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

# サイドバー: ファイルアップロード
st.sidebar.header("📁 データ読み込み")
uploaded_files = st.sidebar.file_uploader(
    "SoftnerログCSVファイルを選択（複数可）", type=["csv"], accept_multiple_files=True
)

if uploaded_files:
    data = pd.DataFrame()
    for file in uploaded_files:
        tmp = pd.read_csv(file)
        data = pd.concat([data, tmp], axis=0)

    # Datetimeの確実な型変換とソート
    data["Datetime"] = pd.to_datetime(data["DATE"] + " " + data["TIME"])
    data.drop_duplicates(["Datetime"], inplace=True)
    data["Day of Week"] = data["Datetime"].dt.day_name()
    data["Hour"] = data["Datetime"].dt.hour  # 時間帯（0〜23）を取得
    data = data.sort_values(by="Datetime")

    # Flow Rate クレンジング・補正処理
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
    # タブ切り替え（Soft Water分析専用）
    # ---------------------------------------------------------
    tab1, tab2, tab3 = st.tabs(
        ["📈 4段トレンド解析", "🔍 トラブル自動検知 (Zero Flow)", "📊 統計 & 各種分布解析"]
    )

    # --- TAB 1: 4段連動グラフ ---
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
        else:
            st.warning("選択した日付範囲にデータが存在しません。")

    # --- TAB 2: トラブル自動検知 (Zero Flow) ---
    with tab2:
        st.subheader("⚠️ Prolonged Zero Flow Events (In-Service 異常検知)")
        st.write(
            "Softenerが 'IN SERVICE'（稼働中）であるにもかかわらず、流量が0になっているイベントを抽出します。"
        )

        min_dur = st.number_input(
            "判定する最小継続時間（分）", min_value=1, value=15, step=5
        )

        for i in [1, 2, 3]:
            flow_c = f"Softener{i} Flow Rate gpm"
            mode_c = f"Softner{i} Mode"

            events = find_prolonged_zero_flow_events(
                data, flow_c, mode_c, min_dur
            )

            st.write(f"### 🔹 Softener #{i} 異常検知結果")
            if events:
                events_df = pd.DataFrame(events)
                st.dataframe(events_df, use_container_width=True)
            else:
                st.success(
                    f"Softener #{i}: 指定された条件（{min_dur}分以上）に該当するゼロ流量異常は見つかりませんでした。"
                )

    # --- TAB 3: 統計 ＆ 各種分布解析 ---
    with tab3:
        st.subheader("📊 FT0911 gpm & 移動平均 / 分布解析")

        # DatetimeIndexの設定
        data_indexed = data.copy()
        data_indexed["Datetime"] = pd.to_datetime(data_indexed["Datetime"])
        data_indexed = data_indexed.set_index("Datetime").sort_index()

        # 移動平均の計算
        data["FT0911 gpm_MA_1H"] = (
            data_indexed["FT0911 gpm"].rolling(window="1h").mean().values
        )
        data["FT0911 gpm_MA_6H"] = (
            data_indexed["FT0911 gpm"].rolling(window="6h").mean().values
        )
        data["FT0911 gpm_MA_24H"] = (
            data_indexed["FT0911 gpm"].rolling(window="24h").mean().values
        )

        # 移動平均付きトレンド
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

        # 【今回追加箇所】Tank Levels over Time 単体グラフ
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

        # 統計量計算
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

        # ヒストグラム（黒い枠線付き）
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

        # 全体バイオリンプロット
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

        # 時間帯別 箱ひげ図
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

        # 時間帯別 バイオリンプロット（全体）
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

        # 曜日別 平均FT0911 gpm（標準偏差エラーバー付き）
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

        # 曜日ごとの時間帯別バイオリンプロット
        st.subheader(
            "📅🎻 Density Distribution of FT0911 gpm by Hour for Each Day of Week"
        )

        unique_days = data["Day of Week"].unique()
        sorted_unique_days = [d for d in day_order if d in unique_days]

        selected_day = st.radio(
            "表示する曜日を選択してください:", sorted_unique_days, horizontal=True
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
    st.info("👈 左側のサイドバーからSoftnerログCSVファイルをアップロードしてください。")
