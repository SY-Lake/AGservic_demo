
import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import plotly.express as px  # グラフ描画用に追加
import re

def display_graph(st,df, customer, sample, item):
    """
    選択された条件に基づいてデータを加工し、グラフを描画する
    """
    st.subheader(f"📊 分析グラフ: {customer} / {sample}")
    
    if df.empty:
        st.warning("表示できるデータがありません。")
        return

    # --- データのクレンジング処理 ---
    plot_df = df.copy()
    
    # 1. 「結果」列のクレンジングと数値化
    plot_df['結果_数値'] = (
        plot_df['結果']
        .astype(str)
        .str.replace('未満', '', regex=False)
        .str.replace(r'\(.*$', '', regex=True)
        .str.strip()
    )
    plot_df['結果_数値'] = pd.to_numeric(plot_df['結果_数値'], errors='coerce')

    # 2. 「採取年月日」を日付型に変換（エラーはNaTになる）
    plot_df['採取年月日'] = pd.to_datetime(plot_df['採取年月日'], errors='coerce')
    
    # 3. 日付順に並び替え（グラフの線が正しくつながるように）
    plot_df = plot_df.sort_values('採取年月日')

    # --- グラフ描画 ---
    fig = px.line(
        plot_df, 
        x='採取年月日',  # X軸を指定
        y='結果_数値',
        title=f"{item} の推移",
        markers=True,
        labels={
            '結果_数値': f"{item} の計測値", 
            '採取年月日': '採取日'
        }
    )
    
    # X軸のフォーマット調整（日付を見やすくする）
    fig.update_xaxes(dtick="M1", tickformat="%Y/%m/%d")
    fig.update_layout(hovermode="x unified")
    
    #st.plotly_chart(fig, use_container_width=True)
    st.plotly_chart(fig, use_container_width=True,config={'displayModeBar': False})
    

    if plot_df['結果_数値'].isna().any():
        st.caption("※ 数値変換できないデータ、または日付不明なデータを除外して表示しています。")