import argparse
import subprocess
import sys

import requests


def list_batch_runs(org: str, project: str, token: str, *, count: int = 20) -> dict:
  url = f"https://app.magicpod.com/api/v1.0/{org}/{project}/batch-runs/"
  headers = {
    "accept": "application/json",
    "Authorization": f"Token {token}",
  }
  params = {"count": count}

  r=requests.get(url, headers=headers, params=params, timeout=60)
  r.raise_for_status()
  return r.json

def pick_latest_batch_run_number(list_json: dict) -> int:
  runs = list_json.get("batch_runs") or []

#フィルタ固定（要件：main&PoC演習_Chrome）
  runs = [x for x in runs if x.get("branch_name") == "main"]
  runs = [x for x in runs if x.get("test_setting_name") == "PoC演習_Chrome"]

  rums = [x.get("batch_run_number") for x in runs if isinstance(x.get("batch_run_number"), int)]
  if not rums:
    return None

  return max(nums)

def main():
  ap = argparse.ArgumentParser()
  ap.add_argument("--org", required=True)
  ap.add_argument("--project", required=True)
  ap.add_argument("--token", required=True)

  ap.add_argument("--count", type=int, default=20)

  #01_magicpod_report.pyに渡す引数
  ap.add_argument("--out", default="report.json")
  ap.add_argument("--errors", action="store_true")
  ap.add_argument("--note", action="store_true")
  ap.add_argument("--test-officer", default="")

  args = ap.parse_args()

  lst = list_batch_runs(args.org, args.project, args.token, count=args.count)
  latest = pick_latest_batch_run_number(lst)

  print("Filter: branch_name=main, test_setting_name=PoC演習_Chrome", fluch=True)
  print("Picked latest batch_run_number:", latest, flush=True)

  if latest is None:
    raise RuntimeError("latest batch_run_number not found (try increasing --count or check filter conditions)")

  cmd =[
    sys.executable, "01_magicpod_report.py",
    "--org", args.org,
    "--project", args.project,
    "--token", args.token,
    "--batch-run-number", str(latest),
    "--out", args.out,
  ]
  if args.errors:
    cmd.append("--errors")
  if args.note:
    cmd.append("--note")
  if args.test_officer:
    cmd.extend(["--test-officer", args.test_officer])

  subprocess.run(cmd, check=True)

if __name__ == "__main__":
  main()
