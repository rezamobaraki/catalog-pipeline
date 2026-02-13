.PHONY: help update-requirements run test

help:
	@echo "Available Commands:"
	@echo "  run                  - Run the main application"
	@echo "  update-requirements  - Update the requirements.txt file"
	@echo "  test                 - Run the tests"

update-requirements:
	uv sync --upgrade
	uv export -o requirements.txt --no-sources --no-hashes --no-dev --python 3.14

run:
	uv run python main.py

test:
	uv run pytest .
