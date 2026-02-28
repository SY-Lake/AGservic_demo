import win32com.client
import os

def excel_to_pdf(excel_file_path, pdf_file_path, sheet_name=None, excel_app=None):
    # パスを絶対パスに変換
    excel_file_path = os.path.abspath(excel_file_path)
    pdf_file_path = os.path.abspath(pdf_file_path)

    # excel_appが渡されていない場合のみ新しく起動
    own_excel = False
    if excel_app is None:
        excel = win32com.client.Dispatch("Excel.Application")
        own_excel = True
    else:
        excel = excel_app

    wb = None
    try:
        # すでに同じブックが開いているかチェック（高速化のため）
        # ※簡易的な実装のため、基本は都度Open
        wb = excel.Workbooks.Open(excel_file_path)
        
        if sheet_name:
            ws = wb.Worksheets(sheet_name)
            # ページ設定（1ページに収める）
            ws.PageSetup.Zoom = False
            ws.PageSetup.FitToPagesWide = 1
            ws.PageSetup.FitToPagesTall = 1
            # 出力
            ws.ExportAsFixedFormat(0, pdf_file_path)
        else:
            for ws in wb.Worksheets:
                ws.PageSetup.Zoom = False
                ws.PageSetup.FitToPagesWide = 1
                ws.PageSetup.FitToPagesTall = 1
            wb.ExportAsFixedFormat(0, pdf_file_path)
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        if wb:
            wb.Close(False)
        # 自分で起動した場合のみQuitする
        if own_excel:
            excel.Quit()