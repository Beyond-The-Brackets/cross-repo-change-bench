#!/bin/bash
# tools/pr_agent.sh <change id> — Qodo PR-Agent's `review`, local git provider, local model.
# Needs `pr-agent` (pip install pr-agent==0.50.0; PR_AGENT_PYTHON points at its Python).
# The change is replayed in a throw-away clone: main = the parent, feature = the change.
# Nothing is sent to GitHub. Writes results/raw/pr-agent/<id>.md.
set -euo pipefail
HERE=$(cd "$(dirname "$0")/.." && pwd)
ID=$1
TRUTH=$(cd "$HERE" && python3 -c "from bench import TRACK; print(TRACK['truth'])")
RES=$(cd "$HERE" && python3 -c "from bench import TRACK; print(TRACK['results'])")
read -r REPO PARENT COMMIT < <(python3 -c "
import json,sys
for c in json.load(open('$HERE/$TRUTH'))['changes']:
    if c['id']=='$ID': p=c['producer']; print(p['repo'], p['parent'], p['commit'])")
W=$HERE/work/pr-agent/$ID
rm -rf "$W"; git clone -q --no-checkout "$HERE/work/repos/$REPO" "$W"
cd "$W"
git -c advice.detachedHead=false checkout -q -B main "$PARENT"
git checkout -q -B feature "$COMMIT"
export CONFIG__GIT_PROVIDER=local CONFIG__MODEL="openai/${MODEL:-qwen2.5-coder-7b-instruct-mlx}" CONFIG__FALLBACK_MODELS='[]' \
  CONFIG__CUSTOM_MODEL_MAX_TOKENS=${MAX_TOKENS:-24000} CONFIG__AI_TIMEOUT=900 OPENAI__API_BASE=${API_BASE:-http://localhost:1234/v1} OPENAI__KEY=${API_KEY:-local}
mkdir -p "$HERE/$RES/raw/pr-agent"
"${PR_AGENT_PYTHON:-python3}" -m pr_agent.cli --pr_url main review > "$HERE/work/pr-agent/$ID.log" 2>&1 || true
if [ -f review.md ]; then cp review.md "$HERE/$RES/raw/pr-agent/$ID.md"; else rm -f "$HERE/$RES/raw/pr-agent/$ID.md"; fi
printf '{"version": "pr-agent 0.50.0", "model": "%s"}\n' "${MODEL:-qwen2.5-coder-7b-instruct-mlx}" > "$HERE/$RES/raw/pr-agent/meta.json"
