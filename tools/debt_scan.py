#!/usr/bin/env python3
"""Track 3: did the debt show BEFORE it broke? Grace's system scan on cFS as it was just before each
change of tracks 1 and 2, with a model reading the most used interfaces.

Run from a Grace checkout (it imports Grace's engine), with an OpenAI-compatible endpoint:

    API_BASE=https://ai-gateway.vercel.sh/v1 API_KEY=... MODEL=alibaba/qwen3.8-27b \
      uv run --project engine python bench/cross-repo/tools/debt_scan.py [ID ...]

Writes results/debt/raw/<id>.json: the scan's findings (the deterministic detectors) and the
interface debt the model reported, with the coverage of both."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx

# tools/grace.py would shadow Grace's own `grace` package: this folder is not on the import path.
sys.path = [
    p for p in sys.path if Path(p or ".").resolve() != Path(__file__).resolve().parent
]

HERE = Path(__file__).resolve().parent.parent
RAW = HERE / "results" / "debt" / "raw"


def reader(messages: list[dict]) -> str | None:
    for attempt in range(2):
        try:
            r = httpx.post(
                os.environ["API_BASE"].rstrip("/") + "/chat/completions",
                json={
                    "model": os.environ["MODEL"],
                    "temperature": 0,
                    "messages": messages,
                },
                headers={"Authorization": "Bearer " + os.environ.get("API_KEY", "")},
                timeout=900,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except Exception as exc:  # noqa: BLE001 — counted by the scan as a model failure
            print(
                f"  model call failed ({type(exc).__name__}), attempt {attempt + 1}",
                file=sys.stderr,
            )
            time.sleep(5)
    return None


def changes() -> list[tuple[str, dict, dict]]:
    out = []
    for truth_file, snaps_file in (
        ("truth.json", "snapshots.json"),
        ("truth-fields.json", "snapshots-fields.json"),
    ):
        truth = json.loads((HERE / truth_file).read_text())
        snaps = json.loads((HERE / snaps_file).read_text())
        out += [(ch["id"], ch, snaps[ch["id"]]) for ch in truth["changes"]]
    return out


def main(ids: list[str]) -> int:
    from grace.system.cli import scan_specs
    from grace.system.models import RepoSpec

    RAW.mkdir(parents=True, exist_ok=True)
    for cid, ch, snap in changes():
        if ids and cid not in ids:
            continue
        out = RAW / f"{cid}.json"
        if out.exists() and not ids:
            continue
        specs = [
            RepoSpec(name=n, path=str(HERE / "work" / "repos" / n), ref=sha)
            for n, sha in sorted(snap.items())
        ]
        started = time.time()
        rep = scan_specs(
            specs,
            blame=False,
            commit_labeller=None,
            capability_reader=None,
            interface_reader=reader,
            today=datetime.fromisoformat(ch["producer"]["date"]).date(),
        )
        keep = {
            "change": cid,
            "snapshot": {r["name"]: r["sha"] for r in rep["snapshot"]["repos"]},
            "findings": rep["findings"],
            "interface_debt": rep["interface_debt"],
            "coverage": {
                k: rep["coverage"].get(k) for k in ("interface_debt", "architecture")
            },
            "architecture": {
                k: rep["architecture"].get(k)
                for k in ("unstable_interfaces", "hubs", "cycles")
            },
        }
        out.write_text(json.dumps(keep, indent=1, default=str) + "\n", encoding="utf-8")
        cov = rep["coverage"]["interface_debt"]
        print(
            f"{cid}: {len(rep['findings'])} findings, {len(rep['interface_debt'])} interface debts "
            f"({cov.get('reviewed')} headers read, {cov.get('quotes_rejected')} quotes rejected) "
            f"in {time.time() - started:.0f}s",
            flush=True,
        )
    import grace

    commit = subprocess.run(
        ["git", "-C", str(Path(grace.__file__).parent), "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
    ).stdout.strip()
    (RAW / "meta.json").write_text(
        json.dumps({"model": os.environ.get("MODEL"), "grace_commit": commit}) + "\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
