#!/usr/bin/env python3
"""Track 3 score: for each change of tracks 1 and 2, did Grace's scan of the system as it was
BEFORE the change point at what then broke? Standard library only.

    python3 tools/score_debt.py     → results/debt/SCORES.md and scores.json

What "pointed at" means, at three levels, from the strictest:
- name:   an interface-debt finding names one of the change's broken names (`BaseMsg`, `microsecs`) or
          the type a broken member belongs to (`CFE_SB_TlmHdr_t`), in its symbol or its quoted line;
- header: an interface-debt finding is on a header that declared one of those names;
- scan:   a finding of the deterministic detectors names one of those names or types (a finding that
          only lists the header among other files does not count).
The headers and names come from the change itself (the truth's names, and the headers Grace's
change impact found them in), never from what the scan reported."""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
RAW = HERE / "results" / "debt" / "raw"
TRACKS = (
    ("truth.json", "results/raw/grace"),
    ("truth-fields.json", "results/fields/raw/grace"),
)


def word(name: str, text: str) -> bool:
    return (
        re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])", text)
        is not None
    )


def main() -> int:
    rows = []
    for truth_file, impact_dir in TRACKS:
        truth = json.loads((HERE / truth_file).read_text())
        for ch in truth["changes"]:
            raw = RAW / f"{ch['id']}.json"
            impact = HERE / impact_dir / f"{ch['id']}.json"
            if not raw.exists() or not impact.exists():
                continue
            scan = json.loads(raw.read_text())
            imp = json.loads(impact.read_text())
            names = set(ch["symbols"])
            headers = {
                h
                for s in imp.get("symbols", [])
                if s["name"] in names
                for h in s.get("headers", [])
            }
            names |= {
                t
                for s in imp.get("symbols", [])
                if s["name"] in names
                for t in s.get("of", [])
            }
            producer = ch["producer"]["repo"]
            debts = [d for d in scan["interface_debt"] if d["repo"] == producer]
            on_header = [d for d in debts if d["file"] in headers]
            on_name = [
                d
                for d in on_header
                if any(word(n, d["symbol"] + " " + d["quote"]) for n in names)
            ]
            det = [
                f
                for f in scan["findings"]
                if any(word(n, json.dumps(f)) for n in names)
            ]
            rows.append(
                {
                    "change": ch["id"],
                    "producer": producer,
                    "subject": ch["producer"]["subject"],
                    "names": sorted(names),
                    "headers": sorted(headers),
                    "scan": [f.get("title", f.get("kind")) for f in det][:3],
                    "header": [
                        f"{d['file']}:{d['line']} {d['symbol']}" for d in on_header
                    ][:3],
                    "name": [
                        {
                            "symbol": d["symbol"],
                            "line": d["line"],
                            "quote": d["quote"],
                            "why": d["why"],
                        }
                        for d in on_name
                    ][:2],
                    "interface_debts_in_producer": len(debts),
                    "headers_read": (scan["coverage"].get("interface_debt") or {}).get(
                        "reviewed"
                    ),
                }
            )
    n = len(rows)
    count = {k: sum(1 for r in rows if r[k]) for k in ("scan", "header", "name")}
    lines = [
        f"Did the scan of the system as it was before each change point at what then broke? ({n} changes)",
        "",
        "| Level | Changes where Grace pointed at it beforehand |",
        "|---|---|",
        f"| the deterministic detectors mention the header or a broken name | {count['scan']} of {n} |",
        f"| the model reports interface debt on the header | {count['header']} of {n} |",
        f"| the model names the very symbol or member that broke | {count['name']} of {n} |",
        "",
        "Per change:",
        "",
    ]
    for r in rows:
        lines.append(
            f"- **{r['change']}** {r['producer']}: {r['subject']} (broke: {', '.join(r['names'])}; "
            f"{r['interface_debts_in_producer']} interface debts reported in {r['producer']})"
        )
        lines.append(f"  - scan: {'; '.join(r['scan']) or 'nothing on it'}")
        lines.append(f"  - model on the header: {'; '.join(r['header']) or 'nothing'}")
        for d in r["name"]:
            lines.append(
                f"  - model on the name, line {d['line']}: `{d['quote']}` — {d['why']}"
            )
    md = "\n".join(lines) + "\n"
    out = HERE / "results" / "debt"
    (out / "SCORES.md").write_text(md, encoding="utf-8")
    (out / "scores.json").write_text(
        json.dumps({"counts": count, "changes": rows}, indent=1) + "\n",
        encoding="utf-8",
    )
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
