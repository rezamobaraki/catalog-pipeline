import argparse
import sys
from pathlib import Path

from services import FileService, PipelineService


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Transform a flat CSV catalog into hierarchical JSON."
    )
    parser.add_argument("--pricat", required=True, type=Path, help="Price catalog CSV")
    parser.add_argument("--mappings", required=True, type=Path, help="Mappings CSV")
    parser.add_argument("--output", "-o", type=Path, help="Output JSON (default: stdout)")
    parser.add_argument("--article-key", default="article_number", help="Article grouping key")
    args = parser.parse_args()

    if not args.pricat.exists():
        print(f"Error: {args.pricat} not found", file=sys.stderr)
        return 1
    if not args.mappings.exists():
        print(f"Error: {args.mappings} not found", file=sys.stderr)
        return 1

    # Dependency injection
    file_service = FileService()
    pipeline = PipelineService(file_service)

    catalog = pipeline.transform(args.pricat, args.mappings, args.article_key)

    if args.output:
        file_service.write_json(catalog, args.output)
        print(f"Wrote {args.output}")
    else:
        print(catalog.to_json())

    return 0


if __name__ == "__main__":
    sys.exit(main())
