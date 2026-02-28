import streamlit as st
import pandas as pd
import json
import os
import datetime
import x005_graph_make as x005
import x006_df_data_cleansing as x006
import x007_pdf_find_and_download as x007

# 実行ファイル(app.pyなど)と同じ場所を基準にする
BASE_DIR = os.path.dirname(__file__)
# Linux/Windows両対応のパス指定
USER_DB_PATH = os.path.join(BASE_DIR, 'xyz.iiddppww', 'pppaaassswd.json')

def load_user_db():
    # デバッグ用：ファイルが存在するかログに出力（Streamlit CloudのManage appで確認可能）
    if not os.path.exists(USER_DB_PATH):
        # st.error(f"File not found: {USER_DB_PATH}") # 動作確認時にコメントアウト解除
        return {"users": []}

    try:
        with open(USER_DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading JSON: {e}")
        return {"users": []}


def authenticate(user_id, password):
    db = load_user_db()
    input_id = user_id.strip()
    input_pw = password.strip()

    for user in db['users']:
        db_id = str(user['id']).strip()
        db_pw = str(user['pw']).strip()        
        if db_id == input_id and db_pw == input_pw:
            return user
    return None

# --- セッション状態の初期化 ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['user_info'] = None

def login():
    st.title("🔑 ログイン画面")
    user_id = st.text_input("ユーザーID")
    password = st.text_input("パスワード", type="password")
    
    if st.button("ログイン", use_container_width=True):
        user = authenticate(user_id, password)
        if user:
            st.session_state['logged_in'] = True
            st.session_state['user_info'] = user
            st.rerun()
        else:
            st.error("IDまたはパスワードが違います。")

def main_app():
    user_info = st.session_state['user_info']
    st.sidebar.write(f"👤 ようこそ、{user_info['name']} さん")
    
    if st.sidebar.button("ログアウト"):
        st.session_state['logged_in'] = False
        st.session_state['user_info'] = None
        st.rerun()

    st.header("📊 計量データ一覧")

    try:
        # 1. CSV読み込み
        df = pd.read_csv('分析結果出力.csv', encoding='utf-8')
        
        # 【修正】2. 会社コード関連の処理を廃止 (顧客名による制御へ移行)

        # 3. 採取年月日をdatetime型に変換
        if "採取年月日" in df.columns:
            df["採取年月日"] = pd.to_datetime(df["採取年月日"], errors='coerce')
        
        # 4. クレンジング処理
        df = x006.cleansing_data_001(df)

        # 【修正】5. 許可された「顧客名」によるフィルタリング
        # JSON内の customer_names キーを「許可された顧客名リスト」として扱う
        allowed_customers = user_info.get('customer_names', [])
        is_admin = (allowed_customers == "all") or (isinstance(allowed_customers, list) and "all" in allowed_customers)

        if not is_admin:
            if isinstance(allowed_customers, list):
                # リスト内の各顧客名を文字列として取得し、前方後方の空白を削除
                target_names = [str(n).strip() for n in allowed_customers]
                df = df[df["顧客名"].isin(target_names)]
            else:
                # 単一指定の場合
                df = df[df["顧客名"] == str(allowed_customers).strip()]

        if df.empty:
            st.warning("表示できるデータがありません。権限設定を確認してください。")
            return

        # 6. 指定された優先順位で表示ソート
        sort_columns = ["顧客名", "採取場所", "試料名", "項目", "採取年月日"]
        existing_sort_cols = [c for c in sort_columns if c in df.columns]
        df = df.sort_values(by=existing_sort_cols, ascending=True)

        # --- フィルタリング UI ---
        st.subheader("表示フィルター")
        
        # 【ポイント】権限で絞り込まれた後のdfから選択肢を生成するため、許可された顧客しか出ません
        customer_options = sorted(df["顧客名"].dropna().unique().astype(str).tolist())
        selected_customer = st.selectbox("1. 顧客名を選択", ["すべて"] + customer_options)
        df_filtered = df if selected_customer == "すべて" else df[df["顧客名"].astype(str) == selected_customer]

        # 2. 採取場所を選択
        location_options = sorted(df_filtered["採取場所"].dropna().unique().astype(str).tolist())
        selected_location = st.selectbox("2. 採取場所を選択", ["すべて"] + location_options)
        if selected_location != "すべて":
            df_filtered = df_filtered[df_filtered["採取場所"].astype(str) == selected_location]

        # 3. 試料名を選択
        sample_options = sorted(df_filtered["試料名"].dropna().unique().astype(str).tolist())
        selected_sample = st.selectbox("3. 試料名を選択", ["すべて"] + sample_options)
        if selected_sample != "すべて":
            df_filtered = df_filtered[df_filtered["試料名"].astype(str) == selected_sample]

        # 4. 項目を選択
        item_options = sorted(df_filtered["項目"].dropna().unique().astype(str).tolist())
        selected_item = st.selectbox("4. 項目を選択", ["すべて"] + item_options)

        # 5. 期間指定フィルター (任意指定)
        st.write("📅 採取年月日の範囲指定 (任意)")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("開始日 (FROM)", value=None)
        with col2:
            end_date = st.date_input("終了日 (TO)", value=None)

        # 日付条件の適用
        if start_date is not None:
            df_filtered = df_filtered[df_filtered["採取年月日"].dt.date >= start_date]
        if end_date is not None:
            df_filtered = df_filtered[df_filtered["採取年月日"].dt.date <= end_date]

        # --- グラフ表示およびPDFリンク表示判定 ---
        if selected_customer != "すべて" and selected_location != "すべて" and selected_sample != "すべて" and selected_item != "すべて":
            df_plot = df_filtered[df_filtered["項目"].astype(str) == selected_item]
            
            if st.button("📊 グラフとPDFを表示する", type="primary", use_container_width=True):
                if not df_plot.empty:
                    x005.display_graph(st, df_plot, selected_customer, selected_sample, selected_item)
                    
                    st.divider()
                    st.subheader("📄 関連資料")
                    x007.get_pdf_download_link(
                        st, 
                        selected_customer, 
                        selected_sample, 
                        start_date=start_date, 
                        end_date=end_date
                    )
                else:
                    st.warning("⚠️ 指定された期間内に該当するデータが存在しないため、グラフとPDFを表示できません。")

        st.divider()
        
        # 表示用に日付を整形
        df_display = df_filtered.copy()
        if "採取年月日" in df_display.columns:
            df_display["採取年月日"] = df_display["採取年月日"].dt.strftime('%Y-%m-%d').fillna("")
        
        st.dataframe(df_display, use_container_width=True)
        st.info(f"該当件数: {len(df_filtered)} 件")

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")

# --- メイン実行 ---
if st.session_state['logged_in']:
    main_app()
else:

    login()
