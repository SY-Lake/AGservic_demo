def シートボディ解析json(sheet, start_keyword="計量の対象", end_keyword="以下余白"):
    """
    C列をスキャンし、開始キーワードの次の行から終了キーワードの前まで、
    C列(項目名)・D列(結果)・E列(単位)をセットで取得する
    """
    analysis_results = []
    is_reading = False
    
    # 1行目から最大行までループ
    for row in range(1, sheet.max_row + 1):
        # C列（項目名）を取得
        cell_c = sheet.cell(row=row, column=3).value
        
        # 終了判定：セルが空でない場合のみチェック（「以下余白」を探す）
        if cell_c is not None:
            cell_str = str(cell_c)
            if end_keyword in cell_str:
                break

        # 読み込みフラグが立っている場合の処理
        if is_reading:
            # セルがNone（空）であっても、行として存在していれば読み取る
            item_name = str(cell_c).strip() if cell_c is not None else ""
            
            # 項目名が空でない場合のみリストに追加（空行を飛ばす）
            if item_name:
                # 列S (19列目) : 結果
                # 列W (23列目) : 単位
                # ※結合セルの場合、左端のセルに値が入っています
                cell_s = sheet.cell(row=row, column=19).value
                cell_w = sheet.cell(row=row, column=23).value                
                analysis_results.append({
                    "項目": item_name,
                    "結果": str(cell_s).strip() if cell_s is not None else "",
                    "単位": str(cell_w).strip() if cell_w is not None else ""
                })
            
        # 開始判定：開始キーワードが見つかったら、次のループから読み込み開始
        if cell_c is not None and start_keyword in str(cell_c):
            is_reading = True
            
    return analysis_results


def test():
    print("test")

if __name__ == "__main__":
   test() 