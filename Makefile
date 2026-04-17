.PHONY: install dev run test lint clean

PY ?= python3

install:
	pip install -e .

dev:
	pip install -e .[dev]

run:
	$(PY) -m hookman list

test:
	$(PY) -m pytest tests/ -v

lint:
	$(PY) -m py_compile hookman/*.py hookman/commands/*.py hookman/hooks/*.py \
		hookman.py git_hooks_manager.py && echo "Syntax OK"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
