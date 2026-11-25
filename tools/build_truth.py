#!/usr/bin/env python3
"""cases.txt → truth.json. Each line of cases.txt is one change, written by hand after reading both diffs:

    <producer repo> <commit> <kind> <symbols,comma,separated> | <consumer repo> <fix commit> <evidence> | ...

evidence: `direct` (the user's own fix, its message or timing ties it to the change), `release` (a
release of the user that swaps the old names for the new ones), `later` (the first later commit of
the user that removes a line of code using one of the names). This script only resolves full
commit ids and dates, and lists the SOURCE files the fix changed on a line that used those names."""

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
REPOS = HERE / "work" / "repos"
SOURCE = re.compile(r"\.(c|h|cc|cpp|cxx|hh|hpp|hxx|inc|cmake)$|(^|/)CMakeLists\.txt$")


def git(repo: str, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPOS / repo), *args], capture_output=True, text=True, errors="replace", check=True
    ).stdout.strip()


def info(repo: str, sha: str) -> dict:
    full = git(repo, "rev-parse", sha)
    return {
        "commit": full,
        "date": git(repo, "log", "-1", "--format=%cI", full),
        "subject": git(repo, "log", "-1", "--format=%s", full),
        "url": f"https://github.com/nasa/{repo}/commit/{full}",
    }


def main(argv: list[str]) -> int:
    """build_truth.py [CASES OUT PREFIX] — default: cases.txt truth.json C."""
    cases, out_name, prefix = (argv + ["cases.txt", "truth.json", "C"][len(argv) :])[:3]
    changes = []
    for i, line in enumerate((HERE / cases).read_text().splitlines()):
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split("|")]
        prepo, psha, kind, syms = parts[0].split()
        symbols = syms.split(",")
        p = info(prepo, psha)
        ch = {
            "id": f"{prefix}{i + 1:02d}",
            "producer": {"repo": prepo, **p, "parent": git(prepo, "rev-parse", p["commit"] + "^")},
            "kind": kind,
            "symbols": symbols,
            "cases": [],
        }
        rx = re.compile(r"(^|[^A-Za-z0-9_])(" + "|".join(map(re.escape, symbols)) + r")([^A-Za-z0-9_]|$)")
        for c in parts[1:]:
            crepo, csha, evidence = c.split()
            f = info(crepo, csha)
            diff = subprocess.run(
                ["git", "-C", str(REPOS / crepo), "show", "--format=", "-U0", f["commit"]],
                capture_output=True,
                text=True,
                errors="replace",
            ).stdout
            files, cur = set(), None
            for d in diff.splitlines():
                if d.startswith("--- "):
                    cur = d[6:] if d.startswith("--- a/") else None
                elif d.startswith("-") and cur and SOURCE.search(cur) and rx.search(d[1:]):
                    files.add(cur)
            ch["cases"].append(
                {
                    "id": f"{ch['id']}-{crepo}",
                    "consumer": crepo,
                    "fix_commit": f["commit"],
                    "fix_date": f["date"],
                    "fix_subject": f["subject"],
                    "url": f["url"],
                    "files": sorted(files),
                    "evidence": evidence,
                }
            )
        changes.append(ch)
    out = {"schema_version": 1, "system": "nasa-cfs", "changes": changes}
    (HERE / out_name).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{out_name}: {len(changes)} changes, {sum(len(c['cases']) for c in changes)} cases")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
