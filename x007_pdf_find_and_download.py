import streamlit as st
import pandas as pd
import glob 
import os
import re
import datetime

def get_pdf_download_link(st, customer, sample, start_date=None, end_date=None):
    pdf_dir = "002.pdf"
    # ファイル名に顧客名と試料名の両方が含まれるPDFを検索
    search_pattern = os.path.join(pdf_dir, f"*{customer}*{sample}*.pdf")
    matched_files = glob.glob(search_pattern)
    
    if not matched_files:
        st.warning(f"該当するPDF証明書が見つかりません。")
        return

    # --- 日付による絞り込みロジック ---
    filtered_files = []
    for file_path in matched_files:
        file_name = os.path.basename(file_path)
        
        # 正規表現で日付(YYYY-MM-DD)を抽出
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_name)
        
        if date_match:
            try:
                # ファイル名から取得した日付をdate型に変換
                file_date = datetime.datetime.strptime(date_match.group(1), '%Y-%m-%d').date()
                
                # 範囲指定がある場合、範囲外ならスキップ
                if start_date and file_date < start_date:
                    continue
                if end_date and file_date > end_date:
                    continue
            except ValueError:
                # 日付の形式が不正な場合は除外せずに進める（念のため）
                pass
        
        filtered_files.append(file_path)

    # 絞り込み後の結果確認
    if not filtered_files:
        st.warning(f"指定された期間に該当するPDF証明書がありません。")
        return

    st.write(f"📄 計量証明書ダウンロード ({len(filtered_files)}件) ")
    
    # 1ファイルごとにボタンを作成
    for file_path in filtered_files:
        file_name = os.path.basename(file_path)
        
        with open(file_path, "rb") as f:
            st.download_button(
                label=f"📥 {file_name} ",
                data=f.read(),
                file_name=file_name,
                mime="application/pdf",
                key=file_name, # ファイル名をキーにして一意にする
                use_container_width=True
            )