import json, urllib.request

SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]  # 直書きしない

with open("report.json", encoding="utf-8") as f:
  d = json.load(f)

r = d["test_results"]
total = len(r)
passed = sum(x["result"] == "pass" for x in r)
failed = sum(x["result"] == "fail" for x in r)

text = (
  f"{d['test_name']}\n"
  f"担当者: 齊藤僚太\n"
  f"合計: {total}  PASS: {passed}  FAIL: {failed}"
)

req = urllib.request.Request(
  WEBHOOK_URL,
  data=json.dumps({"text": text}, ensure_ascii=False).encode(),
  headers={"Content-Type": "application/json"}
)

urllib.request.urlopen(req)
