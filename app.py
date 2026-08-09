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

        # ★ 凡例を下部に水平配置するための設定を追加
        fig_trend.update_layout(
            title_text="FT0911 gpm & Moving Averages",
            title_x=0.5,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.2,
                xanchor="center",
                x=0.5,
            ),
        )
        st.plotly_chart(fig_trend, use_container_width=True)
