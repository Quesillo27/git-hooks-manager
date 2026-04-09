.PHONY: install run test lint

install:
	@echo "No hay dependencias externas — solo Python stdlib"
	@python --version

run:
	python git_hooks_manager.py list

test:
	python -m pytest tests/ -v 2>/dev/null || python tests/test_smoke.py

lint:
	python -m py_compile git_hooks_manager.py && echo "Syntax OK"
