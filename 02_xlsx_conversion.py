import json
import openpyxl

# 入力・出力ファイル
json_path = "report.json"
excel_path = "テスト実行結果_20251128_150000.xlsx"

with open(json_path, "r", encoding="utf-8") as f:
  data = json.load(f)

# Excel作成
wb = openpyxl.Workbook()
sheet = wb.worksheets[0]
sheet.title = "テスト結果"

records = data["test_results"]

header = ["test_case_name", "test_officer", "test_date", "result"]
if any("remark" in r for r in records):
  header.append("remark")


# データ行
for record in data["test_results"]:
  row = [record.get(key, "") for key in header]
  sheet.append(row)

# 保存
wb.save(excel_path)
wb.close()