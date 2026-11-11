#!/usr/bin/env python3
import argparse, json, os, re, sys, urllib.error, urllib.parse, urllib.request
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

CONFIG = os.path.expanduser("~/.clockify-cli.yaml")
API = "https://api.clockify.me/api/v1"
PAGE = 200


def config():
    try:
        text = open(CONFIG, encoding="utf-8").read()
    except OSError:
        sys.exit(f"cannot read {CONFIG}")

    def field(pattern):
        m = re.search(pattern, text, re.M)
        return m.group(1).strip().strip("\"'") if m else None

    cfg = {
        "token": field(r"^token:\s*(.+)$"),
        "workspace": field(r"^workspace:\s*(.+)$"),
        "user": field(r"^user:\s*\n\s+id:\s*(.+)$"),
        "tz": field(r"^time-zone:\s*(.+)$"),
    }
    missing = [k for k in ("token", "workspace", "user") if not cfg[k]]
    if missing:
        sys.exit(f"missing in {CONFIG}: {', '.join(missing)}")
    cfg["tz"] = None if cfg["tz"] in (None, "Local") else ZoneInfo(cfg["tz"])
    return cfg


def pages(cfg, path, **params):
    page = 1
    while True:
        query = urllib.parse.urlencode({**params, "page-size": PAGE, "page": page})
        req = urllib.request.Request(f"{API}/workspaces/{cfg['workspace']}/{path}?{query}", headers={"X-Api-Key": cfg["token"]})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                batch = json.load(r)
        except urllib.error.HTTPError as e:
            sys.exit(f"Clockify API error {e.code} ({path.split('/')[-1]})")
        except urllib.error.URLError as e:
            sys.exit(f"Clockify API unreachable: {e.reason}")
        yield from batch
        if len(batch) < PAGE:
            return
        page += 1


def utc(day, tz):
    return datetime.combine(day, time.min, tz).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def local(ts, tz):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(tz)


def catalog(cfg):
    print("## Active projects")
    for p in pages(cfg, "projects", archived="false"):
        if p.get("public") or any(m.get("userId") == cfg["user"] for m in p.get("memberships", [])):
            print(f"- {p['name']} | billable={str(p.get('billable')).lower()}")
    print("\n## Active tags")
    for t in pages(cfg, "tags", archived="false"):
        print(f"- {t['name']}")


def main():
    ap = argparse.ArgumentParser(description="Clockify time entries per day (read-only)")
    ap.add_argument("--from", dest="start")
    ap.add_argument("--to", dest="end")
    ap.add_argument("--catalog", action="store_true", help="list active projects and tags")
    a = ap.parse_args()
    cfg = config()

    if a.catalog:
        catalog(cfg)
        return
    if not a.start:
        ap.error("--from is required unless --catalog is used")

    start = date.fromisoformat(a.start)
    end = date.fromisoformat(a.end) if a.end else start
    entries = pages(cfg, f"user/{cfg['user']}/time-entries", hydrated="true",
                    start=utc(start, cfg["tz"]), end=utc(end + timedelta(days=1), cfg["tz"]))

    days = defaultdict(list)
    for e in entries:
        days[local(e["timeInterval"]["start"], cfg["tz"]).date()].append(e)

    if not days:
        print(f"No entries between {start} and {end}")
    for day in sorted(days):
        print(f"\n## {day} ({day.strftime('%A')})")
        total = 0
        for e in sorted(days[day], key=lambda x: x["timeInterval"]["start"]):
            s = local(e["timeInterval"]["start"], cfg["tz"])
            if e["timeInterval"]["end"]:
                f = local(e["timeInterval"]["end"], cfg["tz"])
                hours = (f - s).total_seconds() / 3600
                total += hours
                window = f"{s:%H:%M}-{f:%H:%M} | {hours:.2f}h"
            else:
                window = f"{s:%H:%M}-running"
            project = (e.get("project") or {}).get("name", "-")
            tags = "[" + ", ".join(t["name"] for t in e.get("tags") or []) + "]"
            billable = "billable" if e.get("billable") else "non-billable"
            print(f"- {window} | {project} | {tags} | {billable} | {e.get('description') or ''}")
        print(f"  total {total:.2f}h")


if __name__ == "__main__":
    main()
