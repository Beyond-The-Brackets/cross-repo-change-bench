#!/usr/bin/env python3
"""Cross-repository change bench: setup, snapshots, answer extraction and scoring.

Standard library only, so anyone can check a number without installing a tool.

    python3 bench.py setup [--from DIR]   clone the system's repositories into work/repos
    python3 bench.py snapshot             recompute snapshots.json (needs work/repos)
    python3 bench.py answers TOOL         raw outputs in results/raw/TOOL → results/TOOL.json
    python3 bench.py score                every results/*.json → results/SCORES.md + scores.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
WORK = HERE / "work" / "repos"
RESULTS = HERE / "results"
# A track = a ground truth with its own snapshots and results. `main`: names removed from headers;
# `fields`: struct members removed while the type stays (what the first version of Grace missed).
TRACKS = {
    "main": {"truth": "truth.json", "snapshots": "snapshots.json", "results": "results"},
    "fields": {"truth": "truth-fields.json", "snapshots": "snapshots-fields.json", "results": "results/fields"},
}
TRACK = TRACKS[os.environ.get("TRACK", "main")]


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def git(repo: Path, *args: str) -> str:
    res = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, errors="replace")
    if res.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed in {repo}: {res.stderr.strip()}")
    return res.stdout.strip()


# --- setup and snapshots ---------------------------------------------------------------------------


def setup(source: str | None) -> None:
    system = load("system.json")
    WORK.mkdir(parents=True, exist_ok=True)
    for r in system["repos"]:
        dest = WORK / r["name"]
        if dest.exists():
            print(f"{r['name']}: already there")
            continue
        src = str(Path(source) / r["name"]) if source else r["url"]
        subprocess.run(["git", "clone", "--quiet", "--no-checkout", src, str(dest)], check=True)
        print(f"{r['name']}: cloned from {src}")


def snapshot_of(change: dict, repos: list[str]) -> dict[str, str]:
    """The system as the producer's author saw it: the producer at the parent of its change; every
    other repository at its last commit on the branch before the change, or before its own fix
    for this change if that came first (some users adapted in advance)."""
    p = change["producer"]
    branch = load("system.json")["branch"]
    out = {p["repo"]: p["parent"]}
    for name in repos:
        if name == p["repo"]:
            continue
        dates = [p["date"]] + [c["fix_date"] for c in change["cases"] if c["consumer"] == name]
        cut = min(datetime.fromisoformat(d) for d in dates)  # dates, not strings: offsets differ
        before = (cut - timedelta(seconds=1)).isoformat()
        sha = git(WORK / name, "rev-list", "-1", "--first-parent", f"--before={before}", f"origin/{branch}")
        if sha:
            out[name] = sha
    return out


def snapshot() -> None:
    repos = [r["name"] for r in load("system.json")["repos"]]
    truth = load(TRACK["truth"])
    snaps = {ch["id"]: snapshot_of(ch, repos) for ch in truth["changes"]}
    (HERE / TRACK["snapshots"]).write_text(json.dumps(snaps, indent=1) + "\n", encoding="utf-8")
    print(f"{TRACK['snapshots']}: {len(snaps)} changes, {sum(len(v) for v in snaps.values())} repository states")


# --- answers --------------------------------------------------------------------------------------

_PATH = re.compile(r"[A-Za-z0-9_./-]+\.(?:c|h|cc|cpp|hpp|cmake|txt)\b")


def mentioned_repos(text: str, repos: list[str], producer: str) -> list[str]:
    """Repository names a review names. Names of three letters or fewer must match their case
    exactly (`CF`, `DS`): lower-case `cf` or `ds` are ordinary words. Longer names match whole words
    in any case."""
    out = []
    for r in repos:
        if r == producer:
            continue
        flags = 0 if len(r) <= 3 else re.I
        # `README.MD` or `x.CS` are file names, not repositories: a dot next to the name rules it out
        if re.search(rf"(?<![A-Za-z0-9_.]){re.escape(r)}(?![A-Za-z0-9_]|\.[A-Za-z])", text, flags):
            out.append(r)
    return out


def text_answers(tool: str, results: Path) -> dict:
    repos = [r["name"] for r in load("system.json")["repos"]]
    meta_path = results / "raw" / tool / "meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    changes = {}
    for ch in load(TRACK["truth"])["changes"]:
        f = results / "raw" / tool / f"{ch['id']}.md"
        text = f.read_text(encoding="utf-8", errors="replace") if f.exists() else ""
        changes[ch["id"]] = {
            "answered": f.exists(),
            "repos": mentioned_repos(text, repos, ch["producer"]["repo"]),
            "files": sorted({m.group(0) for m in _PATH.finditer(text)}),
        }
    return {"tool": tool, **meta, "changes": changes}


def grace_answers(results: Path, tool: str = "grace") -> dict:
    raw = results / "raw" / tool
    meta = json.loads((raw / "meta.json").read_text()) if (raw / "meta.json").exists() else {}
    changes = {}
    for ch in load(TRACK["truth"])["changes"]:
        f = raw / f"{ch['id']}.json"
        if not f.exists():
            changes[ch["id"]] = {"answered": False, "repos": [], "files": []}
            continue
        r = json.loads(f.read_text())
        code = [c for c in r.get("consumers", []) if any(not x["comment_only"] for x in c["files"])]
        changes[ch["id"]] = {
            "answered": not r.get("error"),
            "repos": [c["repo"] for c in code],
            "files": [f"{c['repo']}:{x['path']}" for c in code for x in c["files"] if not x["comment_only"]],
            "breaks": [c["repo"] for c in code if c["breaks"]],
        }
    return {"tool": tool, **meta, "changes": changes}


def answers(tool: str, results: Path) -> None:
    out = grace_answers(results, tool) if tool.startswith("grace") else text_answers(tool, results)
    (results / f"{tool}.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(f"{(results / tool).relative_to(HERE)}.json written")


# --- score ----------------------------------------------------------------------------------------


def _file_hit(truth_path: str, consumer: str, named: list[str]) -> bool:
    """A structured answer (`repo:path`) names a file by its path: the same path, or a suffix of it
    on a `/` boundary. A free-text review names a file by its name, which is weaker: two files of a
    repository can share a name, so the per-change detail shows both."""
    base = PurePosixPath(truth_path).name
    for n in named:
        repo, sep, path = n.partition(":")
        if sep:
            if repo == consumer and (path == truth_path or truth_path.endswith("/" + path)):
                return True
        elif PurePosixPath(n).name == base:
            return True
    return False


def adjudication(results: Path) -> dict:
    """`adjudication.json`: decisions made by hand on free-text reviews, published so they can be
    disputed. Per tool and change: `not_a_repository` (a short name used as an ordinary word, e.g.
    "CS" for checksum) and `warns_elsewhere` (the review says code outside the repository may break,
    without naming it)."""
    f = results / "adjudication.json"
    return json.loads(f.read_text()) if f.exists() else {}


def score_tool(ans: dict, truth: dict, results: Path = RESULTS) -> dict:
    adj = adjudication(results).get(ans["tool"], {})
    warned = 0
    cases = hits = file_total = file_hits = 0
    by_evidence: dict[str, list[int]] = {}
    named = confirmed = 0
    per_change = {}
    for ch in truth["changes"]:
        a = ans["changes"].get(ch["id"], {"repos": [], "files": []})
        users = {c["consumer"] for c in ch["cases"]}
        decided = adj.get(ch["id"], {})
        got = (set(a["repos"]) | set(decided.get("also_names", []))) - set(decided.get("not_a_repository", []))
        warned += bool(got) or bool(decided.get("warns_elsewhere"))
        named += len(got)
        confirmed += len(got & users)
        found = []
        for c in ch["cases"]:
            hit = c["consumer"] in got
            cases += 1
            hits += hit
            by_evidence.setdefault(c["evidence"], [0, 0])
            by_evidence[c["evidence"]][0] += hit
            by_evidence[c["evidence"]][1] += 1
            for f in c["files"]:
                file_total += 1
                file_hits += hit and _file_hit(f, c["consumer"], a["files"])
            if hit:
                found.append(c["consumer"])
        per_change[ch["id"]] = {
            "found": sorted(found),
            "missed": sorted(users - got),
            "unconfirmed": sorted(got - users),
        }
    return {
        "tool": ans["tool"],
        "model": ans.get("model"),
        "version": ans.get("version"),
        "cases": cases,
        "users_named": hits,
        "recall": hits / cases if cases else None,
        "recall_by_evidence": {k: {"named": v[0], "cases": v[1]} for k, v in sorted(by_evidence.items())},
        "files": file_total,
        "files_named": file_hits,
        "file_recall": file_hits / file_total if file_total else None,
        "repos_named": named,
        "repos_confirmed": confirmed,
        "precision_lower_bound": confirmed / named if named else None,
        "changes_warned": warned,
        "changes": per_change,
    }


def pct(x: float | None) -> str:
    return "n/a" if x is None else f"{100 * x:.0f} %"


def score(results: Path) -> None:
    truth = load(TRACK["truth"])
    rows = []
    for f in sorted(results.glob("*.json")):
        if f.name in ("scores.json", "adjudication.json"):
            continue
        ans = json.loads(f.read_text())
        rows.append(score_tool(ans, truth, results))
        if any("breaks" in c for c in ans["changes"].values()):
            # A structured answer that separates "breaks" from "to check": scored both ways, since the
            # truth lists repositories that broke, not those that will have to migrate later.
            strict = {k: {**c, "repos": c.get("breaks", [])} for k, c in ans["changes"].items()}
            rows.append(score_tool({**ans, "tool": ans["tool"] + " (breaks only)", "changes": strict}, truth, results))
    rows.sort(key=lambda r: -(r["recall"] or 0))
    (results / "scores.json").write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
    lines = [
        f"| Tool | Model | Users named (of {rows[0]['cases'] if rows else 0}) | Recall | Files named "
        "| Repositories named | Confirmed | Precision (lower bound) | Changes with a warning (of "
        f"{len(truth['changes'])}) |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['tool']} | {r['model'] or 'none'} | {r['users_named']} | {pct(r['recall'])} | "
            f"{r['files_named']} of {r['files']} ({pct(r['file_recall'])}) | {r['repos_named']} | "
            f"{r['repos_confirmed']} | {pct(r['precision_lower_bound'])} | {r['changes_warned']} |"
        )
    lines += [
        "",
        "Recall by kind of evidence:",
        "",
        "| Tool | " + " | ".join(sorted(rows[0]["recall_by_evidence"])) + " |",
    ]
    lines.append("|---|" + "---|" * len(rows[0]["recall_by_evidence"]))
    for r in rows:
        cells = [f"{v['named']} of {v['cases']}" for _k, v in sorted(r["recall_by_evidence"].items())]
        lines.append(f"| {r['tool']} | " + " | ".join(cells) + " |")
    lines += ["", "Per change (users named / missed):", ""]
    for ch in truth["changes"]:
        p = ch["producer"]
        lines.append(f"- **{ch['id']}** {p['repo']} `{p['commit'][:10]}` {p['subject']}")
        for r in rows:
            c = r["changes"][ch["id"]]
            lines.append(
                f"  - {r['tool']}: named {', '.join(c['found']) or 'none'}"
                + (f"; missed {', '.join(c['missed'])}" if c["missed"] else "")
                + (f"; not confirmed {', '.join(c['unconfirmed'])}" if c["unconfirmed"] else "")
            )
    out = "\n".join(lines) + "\n"
    (results / "SCORES.md").write_text(out, encoding="utf-8")
    print(out)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("setup")
    s.add_argument("--from", dest="source", help="clone from local mirrors in DIR instead of GitHub")
    sub.add_parser("snapshot")
    a = sub.add_parser("answers")
    a.add_argument("tool")
    a.add_argument("--dir", default=TRACK["results"], help="results folder (default: the track's)")
    sc = sub.add_parser("score")
    sc.add_argument("--dir", default=TRACK["results"], help="results folder (default: the track's)")
    args = p.parse_args(argv)
    if args.cmd == "setup":
        setup(args.source)
    elif args.cmd == "snapshot":
        snapshot()
    elif args.cmd == "answers":
        answers(args.tool, HERE / args.dir)
    else:
        score(HERE / args.dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
