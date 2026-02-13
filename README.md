# Catalog Transformation Pipeline

Transforms flat CSV price catalogs into hierarchical JSON.

## Features

- Mapping engine for value normalization (single-field and composite)
- Attribute promotion to reduce redundancy
- Pydantic models for validation
- Full test coverage

## Structure

```
src/
├── models.py      # Catalog, Article, Variation
├── mapping.py     # Value mapping logic
├── pipeline.py    # Transformation and promotion
├── reader.py      # CSV parsing
├── writer.py      # JSON output
└── main.py        # CLI
```

## Install

```bash
pip install -r requirements.txt
# or
uv sync
```

## Usage

```bash
python src/main.py --pricat data/pricat.csv --mappings data/mappings.csv

# Save to file
python src/main.py --pricat data/pricat.csv --mappings data/mappings.csv -o output.json
```

### Using Makefile

```bash
make run                  # Run the application
make test                 # Run tests
make update-requirements  # Update requirements.txt
make help                 # Show all commands
```

## Dev

```bash
pytest              # Run tests
ruff check src tests  # Lint
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

