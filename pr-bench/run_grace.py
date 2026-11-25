#!/usr/bin/env python3
"""Grace's pull-request review on the selected pull requests, with an open-weight model on a local
OpenAI-compatible server (the `internal` provider a self-hosted customer uses).

Run from a Grace checkout, after fetch.sh:

    INTERNAL_BASE_URL=http://localhost:1234/v1 INTERNAL_CHAT_MODEL=qwen2.5-coder-7b-instruct-mlx \
      uv run --project engine python bench/cross-repo/pr-bench/run_grace.py

It is the same path as Grace's review of a change sent from an editor: the files the pull request
changes, plus their direct neighbours in the code index, read by the model; only findings on a
changed file are kept. Writes results/pr-bench/grace.json, one review per pull request, in the shape
the benchmark's scoring reads."""

from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE.parent / "work" / "pr-bench"
OUT = HERE.parent / "results" / "pr-bench"


def changed_paths(diff: str) -> list[str]:
    return sorted({m.group(1) for m in re.finditer(r"^\+\+\+ b/(.+)$", diff, re.M)})


def body(f: dict) -> str:
    title = f.get("plain_title") or ""
    return (f"{title}\n\n" if title else "") + str(f.get("rationale") or "")


def main() -> int:
    os.environ.setdefault("MODEL_PROVIDER", "internal")
    from grace.audit.pipeline import run_review
    from grace.impact.index import build_index
    from grace.impact.seeds import from_diff
    from grace.impact.traverse import traverse
    from grace.model_gateway import build_chat_gateway
    from grace.review.diff import is_reviewable_path

    gateway = build_chat_gateway(provider="internal")
    sel = json.loads((HERE / "selection.json").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    out_path = OUT / "grace.json"
    done = json.loads(out_path.read_text()) if out_path.exists() else {}
    only = os.environ.get("ONLY")
    for url in sel["prs"]:
        if only and only not in url:
            continue
        if url in done and not done[url].get("error") and not only:
            continue
        owner, repo, _pull, n = url.removeprefix("https://github.com/").split("/")
        pr_id = f"{owner}__{repo}__{n}"
        workdir = WORK / pr_id
        diff = (WORK / f"{pr_id}.diff").read_text(encoding="utf-8", errors="replace")
        changed = [p for p in changed_paths(diff) if is_reviewable_path(p) and (workdir / p).exists()]
        started = time.time()
        entry: dict = {"tool": "grace", "pr_url": url, "review_comments": []}
        try:
            index = build_index(str(workdir))
            near = traverse(index, from_diff(index, changed), depth=1)
            scope = sorted({*changed, *(s.path for s in (*near.certain, *near.possible))})
            findings, meta = asyncio.run(
                run_review(repo_path=str(workdir), changed_paths=changed, scope_paths=scope, gateway=gateway, diff=diff)
            )
            for f in findings:
                loc = str(f.get("location") or "")
                path, _, line = loc.partition(":")
                entry["review_comments"].append(
                    {
                        "path": path,
                        "line": int(n) if (n := line.split("-")[0].strip()).isdigit() else None,
                        "body": body(f),
                    }
                )
            entry["meta"] = {
                "files_changed": len(changed),
                "scope": len(scope),
                "seconds": round(time.time() - started),
                **{k: meta.get(k) for k in ("files_reviewed", "deep_read", "findings_before_scoping", "llm")},
            }
        except Exception as exc:  # noqa: BLE001 — a failed review is written, never skipped
            entry["error"] = f"{type(exc).__name__}: {exc}"
        done[url] = entry
        out_path.write_text(json.dumps(done, indent=1) + "\n", encoding="utf-8")
        took = round(time.time() - started)
        print(f"{pr_id}: {len(entry['review_comments'])} comment(s) {entry.get('error', '')} ({took} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
