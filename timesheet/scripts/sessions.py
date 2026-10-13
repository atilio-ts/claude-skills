#!/usr/bin/env python3
import argparse, glob, json, os, re
from collections import defaultdict
from datetime import datetime, timedelta

GAP_MIN = 10
EDIT_TOOLS = {"Edit", "Write", "NotebookEdit"}
NOISE = re.compile(r"^\s*(<(system-reminder|command-|local-command|task-notification)|\[Request interrupted|Caveat:)")


def text_of(content):
    if isinstance(content, str):
        return content
    return " ".join(b.get("text", "") for b in content if b.get("type") == "text")


def local(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone()


def main():
    ap = argparse.ArgumentParser(description="Digest of Claude Code sessions per day")
    ap.add_argument("--from", dest="start", required=True)
    ap.add_argument("--to", dest="end")
    ap.add_argument("--cwd", default=os.getcwd())
    ap.add_argument("--all", action="store_true", help="include sessions from every directory")
    ap.add_argument("--prompts", type=int, default=12)
    a = ap.parse_args()

    start = datetime.fromisoformat(a.start).date()
    end = datetime.fromisoformat(a.end or a.start).date()
    root = os.path.realpath(a.cwd)
    floor = datetime.combine(start, datetime.min.time()).timestamp()

    days = defaultdict(lambda: defaultdict(lambda: {"ev": [], "prompts": [], "edits": 0, "title": "", "cwd": "", "branch": ""}))
    for f in glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")):
        if os.path.getmtime(f) < floor:
            continue
        sid = os.path.basename(f)[:-6]
        for line in open(f, errors="replace"):
            try:
                d = json.loads(line)
            except ValueError:
                continue
            if d.get("type") == "ai-title":
                for day in days.values():
                    if sid in day:
                        day[sid]["title"] = d.get("aiTitle") or d.get("title") or day[sid]["title"]
                continue
            ts, cwd = d.get("timestamp"), d.get("cwd", "")
            if d.get("type") not in ("user", "assistant") or not ts or d.get("isSidechain"):
                continue
            if not a.all and not (cwd == root or cwd.startswith(root + os.sep)):
                continue
            t = local(ts)
            if not start <= t.date() <= end:
                continue
            s = days[t.date()][sid]
            s["ev"].append(t)
            s["cwd"], s["branch"] = cwd, d.get("gitBranch") or s["branch"]
            c = d["message"].get("content")
            if d["type"] == "assistant" and isinstance(c, list):
                s["edits"] += sum(1 for b in c if b.get("type") == "tool_use" and b.get("name") in EDIT_TOOLS)
            elif d["type"] == "user" and not d.get("isMeta"):
                txt = text_of(c).strip()
                if txt and not NOISE.match(txt):
                    s["prompts"].append(re.sub(r"\s+", " ", txt)[:200])

    for day in sorted(days):
        print(f"\n## {day} ({day.strftime('%A')})")
        for sid, s in sorted(days[day].items(), key=lambda kv: min(kv[1]["ev"])):
            ev = sorted(s["ev"])
            active = sum(min((b - x).total_seconds(), GAP_MIN * 60) for x, b in zip(ev, ev[1:])) / 60
            print(f"- session {sid[:8]} | {ev[0]:%H:%M}-{ev[-1]:%H:%M} | active~{active:.0f}min | prompts={len(s['prompts'])} | edits={s['edits']} | branch={s['branch']}")
            if a.all:
                print(f"  cwd: {s['cwd']}")
            if s["title"]:
                print(f"  title: {s['title']}")
            for p in s["prompts"][: a.prompts]:
                print(f"  > {p}")
            if len(s["prompts"]) > a.prompts:
                print(f"  ... +{len(s['prompts']) - a.prompts} more prompts")


if __name__ == "__main__":
    main()
