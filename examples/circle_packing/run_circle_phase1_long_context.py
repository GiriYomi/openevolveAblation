#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

from openevolve.api import run_evolution


def resolve_paths() -> tuple[str, str, str]:
    """
    Resolve default paths for initial program, evaluator, and default config.
    """
    here = Path(__file__).resolve().parent
    initial_program = str(here / "initial_program.py")
    evaluator = str(here / "evaluator.py")
    default_config = str(here / "config_phase_1_long_context.yaml")
    return initial_program, evaluator, default_config


def parse_args(default_config: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run OpenEvolve on the circle packing example using a YAML config."
    )
    parser.add_argument(
        "--config",
        "-c",
        default=default_config,
        help="Path to YAML config (default: config_phase_1.yaml).",
    )
    parser.add_argument(
        "--iterations",
        "-i",
        type=int,
        default=None,
        help="Override max iterations from config (optional).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=str(Path(__file__).resolve().parent / "openevolve_output_long_context"),
        help="Output directory (defaults to example's openevolve_output_long_context).",
    )
    parser.add_argument(
        "--keep-output",
        action="store_true",
        help="Keep temporary output directory (disables cleanup).",
    )
    return parser.parse_args()


def main() -> int:
    initial_program, evaluator, default_config = resolve_paths()
    args = parse_args(default_config)

    # Basic checks
    for path_label, path in [
        ("initial program", initial_program),
        ("evaluator", evaluator),
        ("config", args.config),
    ]:
        if not os.path.exists(path):
            print(f"Error: {path_label} not found at {path}", file=sys.stderr)
            return 1

    # Helpful hint if key is missing; not required but user-friendly.
    if not os.environ.get("OPENAI_API_KEY"):
        print(
            "Warning: OPENAI_API_KEY is not set. Set it for your chosen OpenAI-compatible provider.",
            file=sys.stderr,
        )

    # Run evolution via the library API.
    result = run_evolution(
        initial_program=initial_program,
        evaluator=evaluator,
        config=args.config,
        iterations=args.iterations,
        output_dir=args.output,
        cleanup=not args.keep_output,
    )

    print("\nEvolution complete.")
    print(f"Best score: {result.best_score:.6f}")
    if result.metrics:
        print("Best program metrics:")
        for k, v in result.metrics.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                try:
                    print(f"  {k}: {v:.6f}")
                except Exception:
                    print(f"  {k}: {v}")
            else:
                print(f"  {k}: {v}")

    if result.output_dir:
        print(f"\nArtifacts saved to: {result.output_dir}")
    else:
        # When cleanup=True, controller writes to example dir by default
        default_out = Path(initial_program).parent / "openevolve_output"
        print(f"\nArtifacts saved under: {default_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

