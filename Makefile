.PHONY: help install test lint docs clean

help:                 ## Show this help
	@grep -Eh '^\S+:\s+.*##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "  make %-15s %s\n", $$1, $$2}'

install:              ## Install package with dev dependencies
	pip install -e ".[dev]"

test:                 ## Run all tests
	python -m pytest tests/ -v

lint:                 ## Run ruff linter
	python -m ruff check reporting/ tests/

docs:                 ## Build HTML documentation
	cd docs && python -m sphinx -b html source build

docs-clean:           ## Remove built documentation
	rm -rf docs/build/

clean:                ## Remove all build artifacts
	rm -rf docs/build/ reporting.egg-info/ .pytest_cache/ __pycache__/
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
