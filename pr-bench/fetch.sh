#!/bin/bash
# pr-bench/fetch.sh — for each selected pull request: its diff (GitHub's public .diff) and its head,
# checked out in work/pr-bench/<owner>__<repo>__<n>. Read-only: nothing is pushed or posted.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
W=$HERE/../work/pr-bench
mkdir -p "$W"
for url in $(python3 -c "import json;print(' '.join(json.load(open('$HERE/selection.json'))['prs']))"); do
  path=${url#https://github.com/}; owner=${path%%/*}; rest=${path#*/}; repo=${rest%%/*}; n=${url##*/}
  id="${owner}__${repo}__${n}"; d=$W/$id
  [ -f "$d.diff" ] || curl -sSfL "$url.diff" -o "$d.diff"
  if [ ! -d "$d" ]; then
    git init -q "$d"
    git -C "$d" fetch -q --depth 1 "https://github.com/$owner/$repo.git" "pull/$n/head"
    git -C "$d" -c advice.detachedHead=false checkout -q FETCH_HEAD
  fi
  echo "$id $(git -C "$d" rev-parse HEAD) $(du -sh "$d" | cut -f1)"
done
