import os, json, urllib.request

WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

reporter = os.environ.get("TEST_REPORTER") or "unknown"

with open("report.json", encoding="utf-8") as f:
  d = json.load(f)

r = d["test_results"]
total = len(r)
passed = sum(x["result"] == "pass" for x in r)
failed = sum(x["result"] == "fail" for x in r)

text = (
  f"{d['test_name']}\n"
  f"担当者: {reporter}\n"
  f"合計: {total}  PASS: {passed}  FAIL: {failed}"
)

req = urllib.request.Request(
  WEBHOOK_URL,
  data=json.dumps({"text": text}, ensure_ascii=False).encode(),
  headers={"Content-Type": "application/json"}
)

urllib.request.urlopen(req)
