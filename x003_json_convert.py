import pandas as pd
import json

def convert_nested_json_to_df(json_input):
    """
    指定された列順序で、ネストしたJSONをDataFrameに変換する
    """
    # JSONデータの読み込み
    if isinstance(json_input, str):
        data = json.loads(json_input)
    else:
        data = json_input

    # リスト形式でない場合はリストに包む
    if not isinstance(data, list):
        data = [data]

    # 親情報のカラムリスト
    parent_columns = [
        "ファイル名", "シート名", "会社コード", "証明書番号", "顧客名",
        "試料名", "採取場所", "証明書発行日", "試料採取区分", 
        "試料受付日", "採取年月日", "分析種別"
    ]

    # 1. データを平坦化
    df = pd.json_normalize(
        data, 
        record_path=['分析結果'], 
        meta=parent_columns,
        errors='ignore'
    )

    # 2. 列の順番を指定（ご要望の順序 + 分析結果の3項目）
    ordered_columns = parent_columns + ["項目", "結果", "単位"]
    
    # 実際に存在する列のみを抽出（万が一JSONに存在しないキーがあってもエラーにならないように）
    df = df.reindex(columns=ordered_columns)

    # 3. 欠損値を「ー」で埋める
    df = df.fillna('ー')

    return df

def export_dataframe(df, file_name_base="分析結果出力"):
    """
    DataFrameをExcelとCSVで出力する
    """
    # 1. Excel出力 (推奨: 書式が崩れず日本語に強い)
    excel_file = f"{file_name_base}.xlsx"
    df.to_excel(excel_file, index=False)
    print(f"Excelファイルを保存しました: {excel_file}")

    # 2. CSV出力 (システム連携用: UTF-8 with BOMでExcel文字化けを防止)
    csv_file = f"{file_name_base}.csv"
    df.to_csv(csv_file, index=False, encoding='utf_8_sig')
    print(f"CSVファイルを保存しました: {csv_file}")


if __name__ == "__main__":
    # --- 実行・確認 ---
    # --- テストデータ ---
    json_data = [
        {
            "ファイル名": "F1-9.xlsx",
            "証明書番号": "125XII1111",
            "分析結果": [
                {"項目": "水素イオン濃度", "結果": "7.7(20℃)", "単位": "―"},
                {"項目": "化学的酸素要求量", "結果": "12", "単位": "mg/L"}
            ]
        },
        {
            "ファイル名": "F1-10.xlsx",
            "証明書番号": "125XII2222",
            "分析結果": [
                {"項目": "塩化物イオン", "結果": "6.8", "単位": "mg/L"},
                {"項目": "全窒素", "結果": "0.5"} # ここには「単位」がない例
            ]
        }
    ]

    df_result = convert_nested_json_to_df(json_data)
    # カラムの順番を確認
    print(df_result.columns.tolist())
    # データの表示
    print(df_result)