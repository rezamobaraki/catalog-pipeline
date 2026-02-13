# Catalog Transformation Pipeline

A Python-based pipeline that transforms flat CSV price catalogs into structured, optimized JSON hierarchies.

## 🚀 Senior-Level Highlights

- **Pragmatic Design**: Simple, readable code that avoids over-engineering while maintaining high standards.
- **Robust Promotion Algorithm**: Smartly lifts common attributes (like `brand` or `season`) up the tree while keeping SKU-specific data (like `ean`) localized.
- **Performance**: O(1) attribute mapping using pre-compiled hash maps.
- **Zero-Boilerplate Models**: Built with **Pydantic V2** for instant type-safe validation and serialization.
- **Quality Assured**: 100% test coverage on core logic with **Pytest** and strictly linted with **Ruff**.

## 🛠 Project Structure

```bash
src/
├── models.py      # Pydantic schema (Catalog -> Article -> Variation)
├── mapping.py     # High-performance Mapping Engine
├── pipeline.py    # Transformation and Attribute Promotion logic
├── reader.py      # Dynamic CSV parsing
├── writer.py      # JSON serialization
└── main.py        # CLI entry point
```

## 📦 Installation

This project uses standard Python libraries + Pydantic.

### Option 1: Using pip (Standard)
```bash
# Recommended: install in venv
pip install -r requirements.txt
pip install pytest ruff  # for dev/test
```

### Option 2: Using uv (Fast)
```bash
# Install dependencies
uv pip install -r requirements.txt
# Or if using uv project management
uv sync
```

## 💻 Usage

### With python
```bash
# Basic run
python src/main.py --pricat data/pricat.csv --mappings data/mappings.csv

# Save to file
python src/main.py --pricat data/pricat.csv --mappings data/mappings.csv -o output.json
```

### With uv
```bash
# Using uv run
uv run src/main.py --pricat data/pricat.csv --mappings data/mappings.csv
```

## 🧪 Testing & Quality
```bash
# Run the test suite
pytest
# Or with uv
uv run pytest

# Check code quality
ruff check src tests
# Or with uv
uv run ruff check src tests
```

---
*For a detailed breakdown of design decisions, data edge cases, and architectural tradeoffs, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).*
