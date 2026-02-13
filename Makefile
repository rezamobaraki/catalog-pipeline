.PHONY: help run test lint update-requirements

export PYTHONPATH := $(CURDIR)

help:
	@echo "Commands:"
	@echo "  make run              - Run pipeline (stdout)"
	@echo "  make run OUT=file.json - Run pipeline (save to file)"
	@echo "  make test             - Run tests"
	@echo "  make lint             - Run ruff"
	@echo "  make update-requirements - Update requirements.txt"

run:
ifdef OUT
	uv run python src/main.py --pricat data/pricat.csv --mappings data/mappings.csv -o $(OUT)
else
	uv run python src/main.py --pricat data/pricat.csv --mappings data/mappings.csv
endif

test:
	uv run pytest tests/

lint:
	uv run ruff check src/ tests/

update-requirements:
	uv sync --upgrade
	uv export -o requirements.txt --no-hashes --no-dev
