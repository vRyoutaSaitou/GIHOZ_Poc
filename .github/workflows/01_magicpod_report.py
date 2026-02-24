import argparse
import json
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import requests


def to_jst_date(iso_z: str) -> str:
  if not iso_z:
    return ""
  # 例： 2026-02-17T02:06:19Z
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

def post_batch_run(org: str, project: str, token: str, payload: dict) -> dict:
  url = f"https://app.magicpod.com/api/v1.0/{org}/{project}/batch-run/"
  headers = {
    "accept": "application/json",
    "Authorization":  f"Token {token}",
    "Content-Type": "application/json",
  }
  r = requests.post(url, headers=headers, json=payload, timeout=60)
  r.raise_for_status()
  return r.json()

def get_batch_run(org: str, project: str, token: str, batch_run_number: int) -> dict:
  url = f"https://app.magicpod.com/api/v1.0/{org}/{project}/batch-run/{batch_run_number}/"
  headers = {
    "accept": "application/json",
    "Authorization": f"Token {token}",
  }
  r = requests.get(url, headers=headers, timeout=60)
  r.raise_for_status()
  return r.json()

def main():
  ap = argparse.ArgumentParser()
  ap.add_argument("--org", required=True)
  ap.add_argument("--project", required=True)
  ap.add_argument("--token", required=True)
  ap.add_argument("--out", default="report.json")

  ap.add_argument("--environment", default="magic_pod")
  ap.add_argument("--test-case-numbers", default="") #magicpodのテストケース番号
  ap.add_argument("--os", required=True)
  ap.add_argument("--device-type", required=True)
  ap.add_argument("--version", required=True)
  ap.add_argument("--model", required=True)
  ap.add_argument("--app-type", required=True)
  ap.add_argument("--app-file-number", required=True)

  ap.add_argument("--test-officer", default="")
  ap.add_argument("--poll-interval", type=int, default=10)
  ap.add_argument("--timeout-seconds", type=int, default=1800)

  args = ap.parse_args()

  payload = {
    "environment": args.environment,
    "os": args.os,
    "device_type": args.device_type,
    "version": args.version,
    "model": args.model,
    "app_type": args.app_type,
    "app_file_number": args.app_file_number,
  }

  if args.test_case_numbers:
    payload["test_case_numbers"] = args.test_case_numbers

  #POST新規実行
  started = post_batch_run(args.org, args.project, args.token, payload)
  batch_run_number = started["batch_run_number"]

  #完了待ち
  deadline = time.time() + args.timeout_seconds
  while True:
    data = get_batch_run(args.org, args.project, args.token, batch_run_number)
    status = data.get("status")

    if status in ("succeeded", "failed", "canceled"):
      break

    if time.time() > deadline:
      raise RuntimeError(
      f"Timeout waiting batch-run {batch_run_number}. last_status={status}"
      )

    time.sleep(args.poll_interval)

  test_admin = data.get("executed_by", "")
  test_name = to_jst_name(data.get("started_at", ""))
  test_id = f"magicpod_batch_run_{data.get('batch_run_number')}"

  officer_default = args.test_officer if args.test_officer else test_admin

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
    "test_results": test_results,
  }

  with open(args.out, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
  main()