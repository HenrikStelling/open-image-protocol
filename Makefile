.PHONY: setup examples test validate
setup:
	uv venv .venv && uv pip install --python .venv/bin/python -e ".[dev]" && chflags nohidden $$(.venv/bin/python -c "import site;print(site.getsitepackages()[0])")/*.pth
examples:
	.venv/bin/python scripts/make_examples.py
test:
	.venv/bin/python -m pytest -q
validate:
	for p in spec/examples/*.oip; do .venv/bin/python -m oip.cli validate $$p; done
