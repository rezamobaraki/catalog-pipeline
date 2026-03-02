import argparse
import logging
import sys
from pathlib import Path

from src.exceptions import PricatError
from src.services import FileService, PipelineService
from src.utils import FieldCombiner

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


def main() -> int:
    parser = argparse.ArgumentParser(description="Transform CSV catalog to hierarchical JSON.")
    parser.add_argument("--input", "-i", required=True, type=Path, help="Input catalog CSV")
    parser.add_argument("--mappings", "-m", required=True, type=Path, help="Mappings CSV")
    parser.add_argument("--output", "-o", type=Path, help="Output JSON (default: stdout)")
    parser.add_argument(
        "--combine",
        action="append",
        metavar="FIELD1,FIELD2,...",
        help="Combine fields (e.g., --combine price_buy_net,currency)",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: {args.input} not found", file=sys.stderr)
        return 1
    if not args.mappings.exists():
        print(f"Error: {args.mappings} not found", file=sys.stderr)
        return 1

    try:
        # Parse field combinations
        combiner = None
        if args.combine:
            combiner = FieldCombiner([FieldCombiner.parse_spec(spec) for spec in args.combine])

        file_service = FileService()
        pipeline = PipelineService(file_service, combiner)
        catalog = pipeline.transform(args.input, args.mappings)

        if args.output:
            file_service.write_json(catalog, args.output)
            print(f"Wrote {args.output}")
        else:
            print(catalog.model_dump_json(indent=4))

        return 0

    except PricatError as e:
        logging.error("Pipeline error: %s", e)
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
