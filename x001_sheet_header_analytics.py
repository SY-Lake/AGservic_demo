import glob
import os
import openpyxl as excel
import re
import datetime
import json

def シートヘッダー分析json(sheet,file_name):
    print("[ シ ー ト 分 析 開 始  ]" + " : " + file_name)
    print(f"    シート名: {sheet}  _データ分析対象")
    """
    シートから情報を取得し、Pythonの辞書形式で返す
    (JSON文字列にする一歩手前の状態)
    """
    result_data = {
        "ファイル名": file_name,
        "シート名": sheet.title
    }

    target_items = [
        {"label": "証明書番号",     "cells": ["AH2", "AJ2", "AL2"], "is_date": False},
        {"label": "証明書発行日",   "cells": ["AH5"],               "is_date": True},
        {"label": "顧客名",         "cells": ["D7"],                "is_date": False},
        {"label": "分析種別",       "cells": ["J9"],                "is_date": False},
        {"label": "試料採取区分",   "cells": ["J10"],               "is_date": False},
        {"label": "試料受付日",     "cells": ["J12"],               "is_date": True},
        {"label": "採取年月日",     "cells": ["J13"],               "is_date": True},
        {"label": "採取場所",       "cells": ["J15"],               "is_date": False},
        {"label": "試料名",         "cells": ["J17"],               "is_date": False},
        {"label": "会社コード",     "cells": ["AK50","AL50","AL51"],"is_date": False},
    ]

    for item in target_items:
        label = item["label"]
        values = []
        for cell in item["cells"]:
            val = sheet[cell].value
            if item["is_date"]:
                # 前に作った format_excel_date を使用
                val = format_excel_date(val)
            values.append(str(val) if val is not None else "")
        
        result_data[label] = "".join(values)

    return result_data

# --- 新しく追加する「連結・保存用」関数 ---
def save_to_json(data_list, output_filename="result.json"):
    """
    リスト化されたデータをまとめて一つのJSONファイルとして保存する
    """
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)
    print(f"ファイルを保存しました: {output_filename}")

def format_excel_date(value):
    # 1. 文字列として入ってきた場合 (例: "2026-01-05 00:00:00")
    if isinstance(value, str):
        try:
            # スペースで区切って日付部分だけ取得
            return value.split(' ')[0]
        except Exception:
            return value

    # 2. 数値（シリアル値）として入ってきた場合 (例: 46027)
    elif isinstance(value, (int, float)):
        # Excelのシリアル値は1899年12月30日を基準とする
        serial_date = datetime.datetime(1899, 12, 30) + datetime.timedelta(days=value)
        return serial_date.strftime('%Y-%m-%d')

    # 3. すでにdatetimeオブジェクトの場合
    elif isinstance(value, datetime.datetime):
        return value.strftime('%Y-%m-%d')

    return str(value)


def test():
    print("test")

if __name__ == "__main__":
   test() 