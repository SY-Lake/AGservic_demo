import pandas as pd
import streamlit as st
import plotly.express as px
import re

# ==========================================
# 1. データ前処理用の関数
# ==========================================
def cleansing_data_001(df):

    new_df = df.copy()

    # --- 試料名のカッコ除去（全角・半角両対応） ---
    if "試料名" in new_df.columns:
        # 正規表現の説明:
        # [(\（]  : 半角または全角の開始カッコ
        # .*?     : 任意の文字列（最短一致）
        # [)\）]  : 半角または全角の終了カッコ
        new_df["試料名"] = (
            new_df["試料名"]
            .astype(str)
            .str.replace(r"[(\（].*?[)\）]", "", regex=True)
            .str.strip()
        )
    
    # --- 採取年月日の日付型変換 ---
    if "採取年月日" in new_df.columns:
        new_df["採取年月日"] = pd.to_datetime(new_df["採取年月日"], errors='coerce')
    
    return new_df