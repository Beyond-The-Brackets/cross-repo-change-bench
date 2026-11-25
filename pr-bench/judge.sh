#!/bin/bash
# pr-bench/judge.sh — score Grace and the comparison tools with the benchmark's OWN pipeline
# (extract → dedup → judge), its judge pointed at a local open-weight model.
# Needs: the benchmark checked out at selection.json's commit in work/pr-bench/martian (git clone
# https://github.com/withmartian/code-review-benchmark), uv, results/pr-bench/grace.json.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
M=$HERE/../work/pr-bench/martian/offline
OUT=$HERE/../results/pr-bench
export MARTIAN_BASE_URL=${API_BASE:-https://ai-gateway.vercel.sh/v1} MARTIAN_API_KEY=${API_KEY:-local} MARTIAN_MODEL=${MODEL:-alibaba/qwen3-coder-30b-a3b}
python3 "$HERE/select_data.py" "$M/results/benchmark_data.json" "$OUT" "$M/results/benchmark_data.subset.json"
cd "$M"
[ -f results/benchmark_data.full.json ] || cp results/benchmark_data.json results/benchmark_data.full.json
cp results/benchmark_data.subset.json results/benchmark_data.json
uv sync -q
# ONLY_TOOL=grace re-scores one tool (after a new run of it) and keeps the others' judgements.
D=results/$(python3 -c "import os,re;print(re.sub(r'[^A-Za-z0-9._-]','_',os.environ['MARTIAN_MODEL']))")
# RUNS=3 judges three times from scratch: on five pull requests one judgement of the same reviews
# moves by ten points of F1 or more, so the published figure is the mean, with the range.
# ONLY_TOOL="grace-a grace-b" judges only those tools and merges them into the existing run files,
# keeping the other tools' judgements (a new Grace run does not re-bill every comparison tool).
for run in $(seq 1 "${RUNS:-1}"); do
  if [ -n "${ONLY_TOOL:-}" ]; then
    for t in $ONLY_TOOL; do
      uv run python -m code_review_benchmark.step2_extract_comments --tool "$t" --force
      uv run python -m code_review_benchmark.step2_5_dedup_candidates
      uv run python -m code_review_benchmark.step3_judge_comments --tool "$t" --force
    done
    python3 - "$D/evaluations.json" "$OUT/evaluations.local-judge.run$run.json" $ONLY_TOOL <<'PY'
import json, sys
from pathlib import Path
new, dest, tools = json.loads(Path(sys.argv[1]).read_text()), Path(sys.argv[2]), sys.argv[3:]
old = json.loads(dest.read_text()) if dest.exists() else {}
for url, by_tool in new.items():
    for t in tools:
        if t in by_tool:
            old.setdefault(url, {})[t] = by_tool[t]
dest.write_text(json.dumps(old, indent=1))
PY
  else
    uv run python -m code_review_benchmark.step2_extract_comments ${RUNS:+--force}
    uv run python -m code_review_benchmark.step2_5_dedup_candidates
    uv run python -m code_review_benchmark.step3_judge_comments ${RUNS:+--force}
    cp "$D/evaluations.json" "$OUT/evaluations.local-judge.run$run.json"
  fi
done
python3 "$HERE/summarize.py" results/openai_gpt-5.2/evaluations.json "$OUT" "$OUT"/evaluations.local-judge.run*.json
