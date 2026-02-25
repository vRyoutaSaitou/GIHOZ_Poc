import argparse
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import requests


def to_jst_date(iso_z: str) -> str:
  if not iso_z:
    return ""
  # 例： 2026-02-25T02:06:19Z
  dt = datetime.fromisoformat(iso_z.replace("Z", "+00:00"))
  dt_jst = dt.astimezone(ZoneInfo("Asia/Tokyo"))
  return dt_jst.strftime("%Y/%m/%d")


def to_jst_name(iso_z: str) -> str:
  if not iso_z:
    return "テスト実行結果"
  dt = datetime.fromisoformat(iso_z.replace("Z", "+00:00"))
  dt_jst = dt.astimezone(ZoneInfo("Asia/Tokyo"))
  return dt_jst.strftime("テスト実行結果_%Y%m%d_%H%M%S")

def status_to_result(status: str) -> str:
  # MagicPod: succeeded/failed/canceld/running
  if status == "succeeded":
    return "pass"
    return "fail"

def get_batch_run(org: str, project: str, token: str, batch_run_number: int, *, errors: bool = False, note: bool = False) -> dict:
  url = f"https://app.magicpod.com/api/v1.0/{org}/{project}/batch-run/{batch_run_number}"
  headers = {
    "accept": "application/json",
    "Authorization":  f"Token {token}",
  }

  params = {}
  if errors:
    params["errors"] = "true"
  if note:
    params["note"] = "true"
  
  r = requests.get(url, headers=headers, timeout=60)
  r.raise_for_status()
  return r.json()

def build_batch_run_url(org: str, project: str, batch_run_number: int) -> str:
  tepl = os.environ.get("MAGICPOD_BATCHRUN_URL_TEMPLATE", "")
  if not tepl:
    return ""
    return tmpl.format(org=org, project=project, batch_run_number=batch_run_number)

def main():
  ap = argparse.ArgumentParser()
  ap.add_argument("--org", required=True)
  ap.add_argument("--project", required=True)
  ap.add_argument("--token", required=True)
  ap.add_argument("--batch-run-number",type=int, required=True)
  ap.add_argument("--out", default="report.json")

  ap.add_argument("--test-officer", default="")
  ap.add_argument("--errors", action="store_true")
  ap.add_argument("--note", action="store_true")

  args = ap.parse_args()

  data = get_batch_run(
    args.org, args.project, args.token, args.batch_run_number,
    errors=args.errors, note=args.note
   )

  status = data.get("status")
  test_admin = data.get("executed_by", "")
  test_name = to_jst_name(data.get("started_at", ""))
  test_id = f"magicpod_batch_run_{data.get('batch_run_number')}"

  officer_default = args.test_officer if args.test_officer else test_admin

  batch_run_url = build_batch_run_url(
    args.org,
    args.project,
    data.get("batch_run_number")
  )

  #処理失敗時
  test_results = []
  details = (data.get("test_cases") or {}).get("details") or []

  for d in details:
    for res in (d.get("results") or []):
      tc = res.get("test_case") or {}
      tc_name = tc.get("name") or ""
      tc_number = tc.get("number")

      if tc_number is not None:
        tc_name = f"{tc_name} (#{tc_number})"

      result_value = status_to_result(res.get("status", ""))

      item = {
        "test_case_name": tc_name,
        "test_officer": officer_default,
        "test_date": to_jst_date(res.get("finished_at") or res.get("started_at") or ""),
        "result": result_value,
      }

      #失敗時固定remark
      if result_value == "fail":
        item["remark"] = "failed"

      test_results.append(item)

  report = {
    "test_name": test_name,
    "test_id": test_id,
    "test_admin": test_admin,
    "status": status,
    "batch_run_number": data.get("batch_run_number"),
    "batch_run_url": batch_run_url,
    "test_results": test_results,
  }

  with open(args.out, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
  main()
