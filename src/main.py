import argparse
import sys
from pathlib import Path

from src.services import FileService, PipelineService


def main() -> int:
    parser = argparse.ArgumentParser(description="Transform CSV catalog to hierarchical JSON.")
    parser.add_argument("--input", "-i", required=True, type=Path, help="Input catalog CSV")
    parser.add_argument("--mappings", "-m", required=True, type=Path, help="Mappings CSV")
    parser.add_argument("--output", "-o", type=Path, help="Output JSON (default: stdout)")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: {args.input} not found", file=sys.stderr)
        return 1
    if not args.mappings.exists():
        print(f"Error: {args.mappings} not found", file=sys.stderr)
        return 1

    file_service = FileService()
    pipeline = PipelineService(file_service)
    catalog = pipeline.transform(args.input, args.mappings)

    if args.output:
        file_service.write_json(catalog, args.output)
        print(f"Wrote {args.output}")
    else:
        print(catalog.to_json())

    return 0


if __name__ == "__main__":
    sys.exit(main())
