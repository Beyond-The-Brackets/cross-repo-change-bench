#!/usr/bin/env python3
"""Precision, recall and F1 per tool over the selected pull requests (micro-averaged, every golden
comment counted), for the local judge and, for the other tools, the benchmark's published judge on
the same pull requests: the gap between the two is the local judge's drift."""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def table(evals: dict, prs: list[str]) -> dict:
    out: dict[str, dict] = {}
    for url in prs:
        for tool, v in (evals.get(url) or {}).items():
            if v.get("skipped"):
                continue
            t = out.setdefault(tool, {"tp": 0, "fp": 0, "golden": 0, "prs": 0})
            t["tp"] += v["tp"]
            t["fp"] += v["fp"]
            t["golden"] += v["total_golden"]
            t["prs"] += 1
    for t in out.values():
        p = t["tp"] / (t["tp"] + t["fp"]) if t["tp"] + t["fp"] else None
        r = t["tp"] / t["golden"] if t["golden"] else None
        t.update(precision=p, recall=r, f1=(2 * p * r / (p + r)) if p and r else 0.0)
    return out


def pct(x):
    return "n/a" if x is None else f"{100 * x:.0f} %"


def main(local: str, published: str, out_dir: str) -> int:
    prs = json.loads((HERE / "selection.json").read_text())["prs"]
    loc = table(json.loads(Path(local).read_text()), prs)
    pub = table(json.loads(Path(published).read_text()), prs)
    rows = sorted(loc, key=lambda k: -loc[k]["f1"])
    lines = [
        "| Tool | PRs | Precision | Recall | F1 (local judge) | F1 (published judge, same PRs) |",
        "|---|---|---|---|---|---|",
    ]
    for k in rows:
        t = loc[k]
        p = pub.get(k)
        lines.append(
            f"| {k} | {t['prs']} | {pct(t['precision'])} | {pct(t['recall'])} | {pct(t['f1'])} | "
            f"{pct(p['f1']) if p else 'not published'} |"
        )
    md = "\n".join(lines) + "\n"
    Path(out_dir, "SCORES.md").write_text(md)
    Path(out_dir, "scores.json").write_text(json.dumps({"local_judge": loc, "published_judge": pub}, indent=1) + "\n")
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
