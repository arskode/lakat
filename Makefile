.PHONY: lint
lint:
	black --check --diff lakat
	flake8 lakat
	mypy lakat
	isort --check-only --df lakat

.PHONY: format
format:
	isort lakat
	black lakat

.PHONY: install-deps
install-deps:
	python -m pip install -r requirements.txt

.PHONY: install-deps-dev
install-deps-dev:
	python -m pip install -r requirements-dev.txt	

.PHONY: install
install: install-deps
	playwright install chromium

.PHONY: install-dev
install-dev: install-deps-dev
	playwright install chromium

.PHONY: run
run:
	python -m lakat
