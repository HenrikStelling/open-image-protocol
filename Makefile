.PHONY: setup setup-all examples examples-check test validate
PY ?= .venv/bin/python

setup:            ## core package + dev tools (tests, examples, Kaggle downloader)
	uv venv .venv && uv pip install --python .venv/bin/python -e ".[dev]" && chflags nohidden $$(.venv/bin/python -c "import site;print(site.getsitepackages()[0])")/*.pth 2>/dev/null || true

setup-all:        ## also the anatomy adapter (torch, torchxrayvision) and the benchmark extras
	uv pip install --python .venv/bin/python -e ".[all]"

examples:         ## rebuild spec/examples/*.oip and data/samples/*.dcm (deterministic: SOURCE_DATE_EPOCH is set by the script)
	$(PY) scripts/make_examples.py

examples-check:   ## rebuild the examples and fail if any committed file changed (CI)
	$(PY) scripts/make_examples.py >/dev/null && git diff --exit-code --stat -- spec/examples data/samples

test:             ## phantom tests (tests/) and benchmark unit tests (bench/test_*.py)
	$(PY) -m pytest -q

validate:         ## schema + package rules on every example package
	for p in spec/examples/*.oip; do $(PY) -m oip.cli validate $$p; done
