#!/usr/bin/env python3
import argparse, glob, json, os, re
from collections import defaultdict
from datetime import datetime

GAP_MIN = 10
CC_EDITS = {"Edit", "Write", "NotebookEdit"}
OMP_EDITS = {"edit", "write"}
NOISE = re.compile(r"^\s*(<(system-reminder|system-notice|command-|local-command|task-notification)|\[Request interrupted|Caveat:)")
ICONS = re.compile("[-\U000f0000-\U000ffffd]")


def text_of(content):
    if isinstance(content, str):
        return content
    return " ".join(b.get("text", "") for b in content if b.get("type") == "text")


def local(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone()


def lines(path):
    for line in open(path, errors="replace"):
        try:
            yield json.loads(line)
        except ValueError:
            continue


def claude_code(path, titles):
    sid = os.path.basename(path)[:-6]
    for d in lines(path):
        if d.get("type") == "ai-title":
            titles[sid] = d.get("aiTitle") or d.get("title") or titles.get(sid, "")
        if d.get("type") not in ("user", "assistant") or d.get("isSidechain") or not d.get("timestamp"):
            continue
        c, role = d["message"].get("content"), d["type"]
        edits = sum(1 for b in c if b.get("type") == "tool_use" and b.get("name") in CC_EDITS) if role == "assistant" and isinstance(c, list) else 0
        prompt = text_of(c).strip() if role == "user" and not d.get("isMeta") else ""
        yield "cc", sid, d["timestamp"], d.get("cwd", ""), d.get("gitBranch", ""), edits, prompt


def omp(path, titles):
    sid, cwd = os.path.basename(path)[:-6].split("_")[-1], ""
    for d in lines(path):
        t = d.get("type")
        if t == "session":
            cwd = d.get("cwd", "")
        elif t in ("title", "title_change") and d.get("title"):
            titles[sid] = ICONS.sub("", d["title"]).strip()
        elif t == "message" and d.get("timestamp"):
            m = d["message"]
            c, role = m.get("content"), m.get("role")
            edits = sum(1 for b in c if b.get("type") == "toolCall" and b.get("name") in OMP_EDITS) if role == "assistant" and isinstance(c, list) else 0
            prompt = text_of(c).strip() if role == "user" else ""
            yield "omp", sid, d["timestamp"], cwd, "", edits, prompt


SOURCES = [
    (claude_code, "~/.claude/projects/*/*.jsonl"),
    (omp, "~/.omp/agent/sessions/*/*.jsonl"),
]


def main():
    ap = argparse.ArgumentParser(description="Digest of Claude Code and omp sessions per day")
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

    titles = {}
    days = defaultdict(lambda: defaultdict(lambda: {"src": "", "ev": [], "prompts": [], "edits": 0, "cwd": "", "branch": ""}))
    for parse, pattern in SOURCES:
        for f in glob.glob(os.path.expanduser(pattern)):
            if os.path.getmtime(f) < floor:
                continue
            for src, sid, ts, cwd, branch, edits, prompt in parse(f, titles):
                if not a.all and not (cwd == root or cwd.startswith(root + os.sep)):
                    continue
                t = local(ts)
                if not start <= t.date() <= end:
                    continue
                s = days[t.date()][sid]
                s["src"], s["cwd"], s["branch"] = src, cwd, branch or s["branch"]
                s["ev"].append(t)
                s["edits"] += edits
                if prompt and not NOISE.match(prompt):
                    s["prompts"].append(re.sub(r"\s+", " ", prompt)[:200])

    for day in sorted(days):
        print(f"\n## {day} ({day.strftime('%A')})")
        for sid, s in sorted(days[day].items(), key=lambda kv: min(kv[1]["ev"])):
            ev = sorted(s["ev"])
            active = sum(min((b - x).total_seconds(), GAP_MIN * 60) for x, b in zip(ev, ev[1:])) / 60
            branch = f" | branch={s['branch']}" if s["branch"] else ""
            print(f"- {s['src']} {sid[:8]} | {ev[0]:%H:%M}-{ev[-1]:%H:%M} | active~{active:.0f}min | prompts={len(s['prompts'])} | edits={s['edits']}{branch}")
            if a.all:
                print(f"  cwd: {s['cwd']}")
            if titles.get(sid):
                print(f"  title: {titles[sid]}")
            for p in s["prompts"][: a.prompts]:
                print(f"  > {p}")
            if len(s["prompts"]) > a.prompts:
                print(f"  ... +{len(s['prompts']) - a.prompts} more prompts")


if __name__ == "__main__":
    main()
