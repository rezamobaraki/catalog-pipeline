.PHONY: help run test lint update-requirements

export PYTHONPATH := $(CURDIR)

BASE_CMD    := uv run python src/main.py --input data/pricat.csv --mappings data/mappings.csv
OUT_FLAG    := $(if $(OUT),-o $(OUT))
COMBINE_FLAGS := $(foreach c,$(COMBINE),--combine $(c))

help:
	@echo "Usage:"
	@echo "  make run                                    - Run pipeline (stdout)"
	@echo "  make run OUT=file.json                      - Run pipeline (save to file)"
	@echo "  make run COMBINE=price_buy_net,currency     - Run with field combining"
	@echo "  make test                                   - Run tests"
	@echo "  make lint                                   - Run ruff"
	@echo "  make update-requirements                    - Update requirements.txt"

run:
	$(BASE_CMD) $(OUT_FLAG) $(COMBINE_FLAGS)

test:
	uv run pytest tests/

lint:
	uv run ruff check src/ tests/

update-requirements:
	uv sync --upgrade
	uv export -o requirements.txt --no-hashes --no-dev
