#!/usr/bin/env python3
"""Precision, recall and F1 per tool over the selected pull requests (micro-averaged, every golden
comment counted), for the local judge and, for the other tools, the benchmark's published judge on
the same pull requests: the gap between the two is the local judge's drift."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

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


def main(published: str, out_dir: str, *local_runs: str) -> int:
    from select_data import TOOLS

    prs = json.loads((HERE / "selection.json").read_text())["prs"]
    present = set(TOOLS) | {f.stem for f in Path(out_dir).glob("grace*.json")}
    runs = [{k: v for k, v in table(json.loads(Path(f).read_text()), prs).items() if k in present} for f in local_runs]
    pub = table(json.loads(Path(published).read_text()), prs)
    tools = sorted(set().union(*runs), key=lambda k: -sum(r[k]["f1"] for r in runs if k in r) / len(runs))

    def mean(k, key):
        vals = [r[k][key] for r in runs if k in r and r[k][key] is not None]
        return sum(vals) / len(vals) if vals else None

    lines = [
        f"Local judge, {len(runs)} run(s): mean (min to max of F1).",
        "",
        "| Tool | PRs | Precision | Recall | F1 (local judge) | F1 (published judge, same PRs) |",
        "|---|---|---|---|---|---|",
    ]
    for k in tools:
        f1s = [r[k]["f1"] for r in runs if k in r]
        spread = f" ({pct(min(f1s))} to {pct(max(f1s))})" if len(f1s) > 1 else ""
        p = pub.get(k)
        lines.append(
            f"| {k} | {runs[0][k]['prs']} | {pct(mean(k, 'precision'))} | {pct(mean(k, 'recall'))} | "
            f"{pct(mean(k, 'f1'))}{spread} | {pct(p['f1']) if p else 'not published'} |"
        )
    md = "\n".join(lines) + "\n"
    Path(out_dir, "SCORES.md").write_text(md)
    Path(out_dir, "scores.json").write_text(json.dumps({"local_judge_runs": runs, "published_judge": pub}, indent=1) + "\n")
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
