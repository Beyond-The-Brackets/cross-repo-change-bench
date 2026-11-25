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
python3 "$HERE/select_data.py" "$M/results/benchmark_data.json" "$OUT/grace.json" "$M/results/benchmark_data.subset.json"
cd "$M"
[ -f results/benchmark_data.full.json ] || cp results/benchmark_data.json results/benchmark_data.full.json
cp results/benchmark_data.subset.json results/benchmark_data.json
uv sync -q
uv run python -m code_review_benchmark.step2_extract_comments
uv run python -m code_review_benchmark.step2_5_dedup_candidates
uv run python -m code_review_benchmark.step3_judge_comments
D=results/$(python3 -c "import os,re;print(re.sub(r'[^A-Za-z0-9._-]','_',os.environ['MARTIAN_MODEL']))")
cp "$D/evaluations.json" "$OUT/evaluations.local-judge.json"
python3 "$HERE/summarize.py" "$OUT/evaluations.local-judge.json" results/openai_gpt-5.2/evaluations.json "$OUT"
