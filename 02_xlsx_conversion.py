import json
import openpyxl
from datetime import datetime 
from zoneinfo import ZoneInfo

# 入力・出力ファイル
print("jsonファイル出力中")

json_path = "report.json"

print("jsonファイル出力完了")

print("タイムスタンプ生成中")

#タイムゾーンを設定し、タイムスタンプを導入
ts = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y%m%d_%H%M%S")
excel_path = f"テスト実行結果_{ts}.xlsx"

print("タイムスタンプ生成完了")

with open(json_path, "r", encoding="utf-8") as f:
  data = json.load(f)

print("xslxファイル出力中")
# Excel作成
wb = openpyxl.Workbook()
sheet = wb.worksheets[0]
sheet.title = "テスト結果"

records = data["test_results"]

batch_run _url = data.get("batch_run_url", "")

header = ["test_case_name", "test_officer", "test_date", "result", "remark", "batch_run_url"]

sheet.append(header)

print("データ書き込み中")
# データ行
for record in records:
  row = [
    record.get("test_case_name", ""),
    record.get("test_officer", ""),
    record.get("test_date", ""),
    record.get("result", ""),
    record.get("remark", ""),
    batch_run_url,
  ]
  sheet.append(row)

print("データ書き込み完了")

# 保存
wb.save(excel_path)
wb.close()

print(f"ファイル名「{excel_path}」で保存しました")
print("xlsxファイル出力完了")
