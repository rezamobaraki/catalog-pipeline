# Architecture

## Problem

Transform flat CSV catalog into hierarchical JSON (Catalog > Article > Variation).

## Data Flow

```mermaid
sequenceDiagram
    participant CSV as pricat.csv
    participant FS as FileService
    participant MS as MappingService
    participant PS as PipelineService
    participant JSON as Output

    CSV->>FS: read_csv()
    FS->>PS: rows
    loop Per row
        PS->>MS: apply(row)
        MS-->>PS: transformed
    end
    PS->>PS: group_by_article()
    PS->>PS: promote_attributes()
    PS->>FS: write_json()
    FS->>JSON: catalog.json
```

## Class Diagram

```mermaid
classDiagram
    class FileService {
        +read_csv(path) Iterator
        +write_json(catalog, path)
    }
    
    class MappingService {
        +load(path)
        +apply(row) dict
    }
    
    class PipelineService {
        -file_service: FileService
        +transform(pricat, mappings) Catalog
    }
    
    class Catalog {
        +attributes: dict
        +articles: list
        +to_json() str
    }
    
    class Article {
        +article_id: str
        +attributes: dict
        +variations: list
    }
    
    class Variation {
        +ean: str
        +attributes: dict
    }
    
    PipelineService --> FileService
    PipelineService --> MappingService
    Catalog "1" *-- "*" Article
    Article "1" *-- "*" Variation
```

## Services

**FileService**: Handles CSV reading and JSON writing.

**MappingService**: Loads mappings and transforms field values.
- Single: `(field, value) → (dest_field, dest_value)`
- Composite: `((f1, f2), (v1, v2)) → (dest_field, dest_value)`

**PipelineService**: Orchestrates the transformation.

## Attribute Promotion

For each group of children:
1. Find attributes where all have identical values
2. Move to parent, remove from children

Never promotes: `ean`, `article_id`, `article_number`

## Processing

- **Stream**: CSV reading, row mapping
- **Batch**: Grouping, promotion (needs all siblings)

Dataset fits in memory.

## Edge Cases

- Empty values filtered
- Prices vary by material → stay at variation level
- Composite mappings use `|` delimiter
