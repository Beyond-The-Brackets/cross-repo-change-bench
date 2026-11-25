#!/usr/bin/env python3
"""The benchmark's data, cut to the selected pull requests and the comparison tools, plus Grace's reviews."""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = ["coderabbit", "greptile", "copilot", "bugbot", "claude-code", "qodo"]  # the best known, as published


def main(full: str, grace_dir: str, out: str) -> int:
    data = json.loads(Path(full).read_text())
    if "benchmark_data.full" not in full and Path(full).with_name("benchmark_data.full.json").exists():
        data = json.loads(Path(full).with_name("benchmark_data.full.json").read_text())
    # Every Grace run in results/pr-bench (grace.json, grace-<model>.json), one tool each.
    runs = {f.stem: json.loads(f.read_text()) for f in sorted(Path(grace_dir).glob("grace*.json"))}
    sel = json.loads((HERE / "selection.json").read_text())["prs"]
    keep = {}
    for url in sel:
        e = dict(data[url])
        e["reviews"] = [r for r in e["reviews"] if r["tool"] in TOOLS]
        for tool, ours in runs.items():
            g = ours.get(url)
            if g and not g.get("error"):
                e["reviews"].append({"tool": tool, "pr_url": url, "review_comments": g["review_comments"]})
        keep[url] = e
    Path(out).write_text(json.dumps(keep, indent=1))
    print(f"{len(keep)} pull requests, tools: {sorted({r['tool'] for e in keep.values() for r in e['reviews']})}")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
