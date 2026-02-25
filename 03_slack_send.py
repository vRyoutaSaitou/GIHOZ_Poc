import os, json, urllib.request

WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")
if not WEBHOOK_URL:
  raise RuntimeError("SLACK_WEBHOOK_URL is not set")

reporter = os.environ.get("TEST_REPORTER") or "unknown"

try:
  with open("report.json", encoding="utf-8") as f:
  d = json.load(f)
except FileNotFoundError:
  raise RuntimeError("report.json not found")
except json.JSONDecodeError as e:
  raise RuntimeError(f"report.json is invalid JSON: {e}")

if "test_results" not in d:
  raise RuntimeError("report.json does not contain 'test_results'")

r = d["test_results"]
total = len(r)
passed = sum(x["result"] == "pass" for x in r)
failed = sum(x["result"] == "fail" for x in r)

test_name = d.get("test_name", "unknown_test")

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
try:
  with urllib.request.urlopen(req, timeout=30) as resp:
  resp.read()
except urllib.error.HTTPError as e:
  body = e.read().decode("utf-8", errors="replace")
  raise RuntimeError(f"Slack webhook HTTPError: {e.code} {e.reason} body={body}")
except urllib.error.URLError as e:
  raise RuntimeError(f"Slack webhook URLError: {e.reason}")
