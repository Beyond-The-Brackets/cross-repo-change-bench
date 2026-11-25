# Every published number comes from `make score`, which reads only the files in results/.
# The other targets regenerate those files: they need the repositories (make setup), and the tool.

PYTHON ?= python3
GRACE ?= grace
# The published run: Qwen3-Coder 30B-A3B (open weights, Apache 2.0) through an OpenAI-compatible
# endpoint. API_KEY comes from the environment. A local server works the same way (LM Studio, vLLM).
API_BASE ?= https://ai-gateway.vercel.sh/v1
MODEL ?= alibaba/qwen3-coder-30b-a3b
MAX_TOKENS ?= 100000
CHANGES := $(shell $(PYTHON) -c "import json;print(' '.join(c['id'] for c in json.load(open('truth.json'))['changes']))")

.PHONY: score setup truth snapshot grace pr-agent model all

score:
	$(PYTHON) bench.py score
	TRACK=fields $(PYTHON) bench.py score
	$(PYTHON) bench.py score --dir results/qwen2.5-coder-7b

setup:
	$(PYTHON) bench.py setup

truth: setup
	$(PYTHON) tools/build_truth.py
	$(PYTHON) tools/build_truth.py cases-fields.txt truth-fields.json F

snapshot: setup
	$(PYTHON) bench.py snapshot
	TRACK=fields $(PYTHON) bench.py snapshot

grace: setup
	GRACE="$(GRACE)" $(PYTHON) tools/grace.py && $(PYTHON) bench.py answers grace

pr-agent: setup
	for id in $(CHANGES); do API_BASE=$(API_BASE) MODEL=$(MODEL) MAX_TOKENS=$(MAX_TOKENS) tools/pr_agent.sh $$id; done
	$(PYTHON) bench.py answers pr-agent

model: setup
	API_BASE=$(API_BASE) MODEL=$(MODEL) $(PYTHON) tools/model.py diff && $(PYTHON) bench.py answers model-diff
	API_BASE=$(API_BASE) MODEL=$(MODEL) $(PYTHON) tools/model.py diff+list && $(PYTHON) bench.py answers model-diff+list

all: grace pr-agent model score
