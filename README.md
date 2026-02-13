# Catalog Transformation Pipeline

Transforms flat CSV price catalogs into hierarchical JSON.

## Features

- Value mapping (single-field and composite)
- Attribute promotion to reduce redundancy
- Pydantic models for validation
- Dependency injection for testability

## Structure

```
src/
├── main.py                 # CLI entry point
├── domains/                # Domain models (Pydantic)
│   ├── variation.py
│   ├── article.py
│   └── catalog.py
├── services/               # Business logic
│   ├── file_service.py     # CSV/JSON I/O
│   ├── mapping_service.py  # Value transformations
│   └── pipeline_service.py # Main pipeline
└── utils/                  # Helper functions
    └── promotion.py        # Attribute promotion
```

## Install

```bash
# Using uv (recommended)
uv sync

# Using pip
pip install -r requirements.txt
```

## Usage

```bash
# Using uv
uv run python src/main.py --pricat data/pricat.csv --mappings data/mappings.csv

# Using pip
python src/main.py --pricat data/pricat.csv --mappings data/mappings.csv

# Save to file
python src/main.py --pricat data/pricat.csv --mappings data/mappings.csv -o output.json
```

## Makefile

```bash
make run       # Run pipeline
make test      # Run tests
make lint      # Run ruff
make help      # Show commands
```

## Dev

```bash
uv run pytest           # Run tests
uv run ruff check src   # Lint
```

See [docs/ARCHITECTURE.md](docs/TASK-1-ARCHITECTURE.md) for design details.
