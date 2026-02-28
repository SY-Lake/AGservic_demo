import glob
import os
import openpyxl as excel
import re
import time
import win32com.client

import x001_sheet_header_analytics as x001
import x004_pdf_convert as x004

# グローバル変数
path = os.getcwd()
folder_name = "001.data" 
folder_name2 = "002.pdf"

def main():
    print("[ S T A R T     P R O G R A M  ]")
    os.system('taskkill /f /im excel.exe /fi "status ne running" >nul 2>&1')
    time.sleep(2)

    # 1. ここでExcelアプリケーションを「一度だけ」起動
    excel_app = win32com.client.Dispatch("Excel.Application")
    excel_app.Visible = False
    excel_app.DisplayAlerts = False # アラート抑制

    try:
        xpath = os.path.join(path, folder_name, "**", "*.xlsx")
        allfiles = glob.glob(xpath, recursive=True)

        for file in allfiles:
            file_name = os.path.basename(file)
            print(f"ブック解析中: {file_name}")
            
            # openpyxlでシート構成を分析
            book = excel.load_workbook(file, read_only=True, data_only=True)
            
            for sheet in book.worksheets:
                if re.search("飲|浴", str(sheet.title)):
                    continue
                
                # ヘッダー分析
                data = x001.シートヘッダー分析json(sheet, file_name)
                
                # 保存パス生成
                # 【修正箇所】顧客名と試料名の間に採取場所を追加
                file_base_name = f"{data['会社コード']}_{data['証明書番号']}_{data['採取年月日']}_{data['顧客名']}_{data['採取場所']}_{data['試料名']}"
                
                # 正規表現での安全なファイル名生成
                safe_file_name = re.sub(r'[\\/:*?"<>|]', '_', file_base_name)
                output_pdf = os.path.join(path, folder_name2, safe_file_name + ".pdf")

                # 2. 起動済みの excel_app を渡してPDF化
                x004.excel_to_pdf(file, output_pdf, sheet.title, excel_app=excel_app)
                print(f"  -> PDF作成完了: {sheet.title}")

            book.close()

    finally:
        # 3. 全ファイル終わったら最後にExcelを終了
        excel_app.Quit()
        print("[ E N D       P R O G R A M  ]")

if __name__ == "__main__":
    main()