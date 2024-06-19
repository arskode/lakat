.PHONY: lint
lint:
	ruff check lakat

.PHONY: format
format:
	ruff check --fix && ruff format lakat

.PHONY: install-deps
install-deps:
	python -m pip install -r requirements-dev.txt	

.PHONY: install
install: install-deps
	playwright install chromium

.PHONY: run
run:
	python -m lakat
