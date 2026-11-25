#!/usr/bin/env python3
"""Run Grace's change impact (`grace system impact`) on every change, each on its own snapshot.

GRACE is the command that runs Grace's engine (default `grace`; from a Grace checkout:
`GRACE="uv run --project engine grace"`). Writes results/raw/grace/<id>.json."""

import json
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from bench import TRACK  # noqa: E402

RAW = HERE / TRACK["results"] / "raw" / "grace"


def main() -> int:
    grace = shlex.split(os.environ.get("GRACE", "grace"))
    truth = json.loads((HERE / TRACK["truth"]).read_text())
    snaps = json.loads((HERE / TRACK["snapshots"]).read_text())
    RAW.mkdir(parents=True, exist_ok=True)
    for ch in truth["changes"]:
        p = ch["producer"]
        lines = ["repos:"]
        for name, sha in sorted(snaps[ch["id"]].items()):
            lines += [f"  - name: {name}", f"    path: {HERE / 'work' / 'repos' / name}", f"    ref: {sha}"]
        with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as f:
            f.write("\n".join(lines) + "\n")
        out = RAW / f"{ch['id']}.json"
        cmd = [
            *grace,
            "system",
            "impact",
            f.name,
            "--repo",
            p["repo"],
            "--base",
            p["parent"],
            "--head",
            p["commit"],
            "--json",
            str(out),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        os.unlink(f.name)
        print(f"{ch['id']}: {res.stdout.splitlines()[0] if res.stdout else res.stderr.strip()[:200]}")
    version = os.environ.get("GRACE_VERSION", "")
    (RAW / "meta.json").write_text(json.dumps({"version": version, "model": None}) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
