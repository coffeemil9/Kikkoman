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
st.set_page_config(page_title="Softener Log Analysis App", layout="wide")

st.title("📊 Softener Log Data Analysis App")
st.write(
    "Google Colab & 自作モジュール（WUS）の分析機能を統合したWebアプリケーションです。"
)

# ---------------------------------------------------------
# HELPER FUNCTIONS (From Modules)
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

    # --- 1つ目のグラフ: FT0911 gpm and Softener Mode ---
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

    # --- 2つ目のグラフ: PT0911 psi and Softener Mode ---
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

    # --- 3つ目のグラフ: Tank Levels and Softener Mode ---
    fig.add_trace(
        go.Scatter(
            x=filtered_data["Datetime"],
            y=filtered_data["V0910 Tank Level"],
            name="V0910 Tank Level",
            mode="lines",
            line=dict(color="purple"),
            legend="legend3",
        ),
        row=3,
        col=1,
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=filtered_data["Datetime"],
            y=filtered_data["V0907 Tank Level"],
            name="V0907 Tank Level",
            mode="lines",
            line=dict(color="orange"),
            legend="legend3",
        ),
        row=3,
        col=1,
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=filtered_data["Datetime"],
            y=filtered_data["V0909 Tank Level"],
            name="V0909 Tank Level",
            mode="lines",
            line=dict(color="brown"),
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

    # --- 4つ目のグラフ: Softener Flow Rates and Softener Mode ---
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
    # タブで画面表示を切り替え
    # ---------------------------------------------------------
    tab1, tab2, tab3 = st.tabs(
        ["📈 4段トレンド解析", "🔍 トラブル自動検知 (Zero Flow)", "📊 統計 & ヒストグラム"]
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

    # --- TAB 3: 統計 ＆ ヒストグラム ---
    with tab3:
        st.subheader("📊 FT0911 gpm & 移動平均 / 分布解析")

        # 【エラー修正箇所】Datetimeを正しくDatetimeIndexとして設定
        data_indexed = data.copy()
        data_indexed["Datetime"] = pd.to_datetime(data_indexed["Datetime"])
        data_indexed = data_indexed.set_index("Datetime").sort_index()

        # 移動平均の安全な計算
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

        st.plotly_chart(fig_hist, use_container_width=True)

else:
    st.info("👈 左側のサイドバーからCSVファイルをアップロードしてください。")
