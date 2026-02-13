.PHONY: help run test lint update-requirements

help:
	@echo "Commands:"
	@echo "  make run       - Run pipeline"
	@echo "  make test      - Run tests"
	@echo "  make lint      - Run ruff"
	@echo "  make update-requirements - Update requirements.txt"

run:
	uv run python src/main.py --pricat data/pricat.csv --mappings data/mappings.csv

test:
	uv run pytest tests/

lint:
	uv run ruff check src/ tests/

update-requirements:
	uv sync --upgrade
	uv export -o requirements.txt --no-hashes --no-dev
