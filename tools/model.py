#!/usr/bin/env python3
"""Baseline: the same open-weight model, asked directly, with what a pull-request reviewer sees.

Two variants:
  diff      the change's diff only (a single-repository review);
  diff+list the diff plus the names of the system's repositories (the model knows they exist,
            but cannot read them).

    API_BASE=http://localhost:1234/v1 MODEL=qwen2.5-coder-7b-instruct-mlx python3 tools/model.py diff

Writes results/raw/model-<variant>/<id>.md. Standard library only; any OpenAI-compatible server."""

import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
BUDGET = 60_000  # characters of diff: about 17k tokens, inside a 32k context with room to answer
HEADER_EXT = (".h", ".hh", ".hpp", ".hxx", ".inc")

PROMPT = """You are reviewing a pull request to the repository `{repo}`.
{context}
Here is the diff{cut}:

```diff
{diff}
```

Review this change. In particular: which code OUTSIDE this repository could this change break or
force to change? Name every other repository and file you can, and say why."""


def diff_of(repo: Path, base: str, head: str) -> tuple[str, bool]:
    """Headers first (they are what other repositories see), then the rest, within the budget."""
    names = subprocess.run(
        ["git", "-C", str(repo), "diff", "--name-only", base, head], capture_output=True, text=True, check=True
    ).stdout.split()
    names.sort(key=lambda n: (not n.endswith(HEADER_EXT), n))
    out, cut = "", False
    for n in names:
        d = subprocess.run(
            ["git", "-C", str(repo), "diff", base, head, "--", n], capture_output=True, text=True, errors="replace"
        ).stdout
        if len(out) + len(d) > BUDGET:
            cut = True
            continue
        out += d
    return out, cut


def ask(prompt: str) -> str:
    body = {
        "model": os.environ.get("MODEL", "qwen2.5-coder-7b-instruct-mlx"),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 1500,
    }
    req = urllib.request.Request(
        os.environ.get("API_BASE", "http://localhost:1234/v1").rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + os.environ.get("API_KEY", "local")},
    )
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]


def main() -> int:
    variant = sys.argv[1] if len(sys.argv) > 1 else "diff"
    if variant not in ("diff", "diff+list"):
        print("usage: model.py diff|diff+list", file=sys.stderr)
        return 2
    truth = json.loads((HERE / "truth.json").read_text())
    repos = [r["name"] for r in json.loads((HERE / "system.json").read_text())["repos"]]
    raw = HERE / "results" / "raw" / f"model-{variant}"
    raw.mkdir(parents=True, exist_ok=True)
    for ch in truth["changes"]:
        p = ch["producer"]
        diff, cut = diff_of(HERE / "work" / "repos" / p["repo"], p["parent"], p["commit"])
        context = ""
        if variant == "diff+list":
            others = ", ".join(r for r in repos if r != p["repo"])
            context = f"It is one of several repositories built together as one system. The others are: {others}.\n"
        prompt = PROMPT.format(
            repo=p["repo"], context=context, diff=diff, cut=" (cut to fit: some files are left out)" if cut else ""
        )
        (raw / f"{ch['id']}.md").write_text(ask(prompt), encoding="utf-8")
        print(f"{ch['id']}: done{' (diff cut)' if cut else ''}")
    (raw / "meta.json").write_text(
        json.dumps({"version": "prompt v1", "model": os.environ.get("MODEL", "qwen2.5-coder-7b-instruct-mlx")}) + "\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
