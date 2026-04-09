.PHONY: install run test lint clean

install:
	pip install -r requirements.txt

run:
	python3 git_hooks_manager.py list

test:
	python3 tests/test_hooks_manager.py

lint:
	python3 -m py_compile git_hooks_manager.py && echo "✅ Sintaxis OK"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
