#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

from openevolve.api import run_evolution
from openevolve.config import Config


def default_paths() -> tuple[str, str, str]:
    """
    Resolve defaults:
    - initial program: best program from phase 1
    - evaluator: circle packing evaluator
    - config: phase 2 YAML
    """
    here = Path(__file__).resolve().parent
    initial_program = str(here / "openevolve_output_phase1" / "best" / "best_program.py")
    evaluator = str(here / "evaluator.py")  
    config = str(here / "config_phase_2.yaml")
    return initial_program, evaluator, config


def parse_args(default_initial: str, default_evaluator: str, default_config: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run OpenEvolve phase 2 using the best program from phase 1 as the initial program."
    )
    parser.add_argument(
        "--initial",
        "-p",
        default=default_initial,
        help="Path to initial program (defaults to openevolve_output_phase1/best/best_program.py).",
    )
    parser.add_argument(
        "--evaluator",
        "-e",
        default=default_evaluator,
        help="Path to evaluator (defaults to examples/circle_packing/evaluator.py).",
    )
    parser.add_argument(
        "--config",
        "-c",
        default=default_config,
        help="Path to phase 2 YAML config (defaults to config_phase_2.yaml).",
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
        default=str(Path(__file__).resolve().parent / "openevolve_output"),
        help="Output directory (defaults to example's openevolve_output).",
    )
    parser.add_argument(
        "--keep-output",
        action="store_true",
        help="Keep temporary output directory (disables cleanup).",
    )
    return parser.parse_args()


def main() -> int:
    default_initial, default_evaluator, default_config = default_paths()
    args = parse_args(default_initial, default_evaluator, default_config)

    # Validate paths
    for label, path in [
        ("initial program", args.initial),
        ("evaluator", args.evaluator),
        ("config", args.config),
    ]:
        if not os.path.exists(path):
            print(f"Error: {label} not found at {path}", file=sys.stderr)
            return 1

    # Warn if no API key present
    if not (os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENROUTER_API_KEY")):
        print(
            "Warning: Neither OPENAI_API_KEY nor OPENROUTER_API_KEY is set.",
            file=sys.stderr,
        )

    # Load YAML, inject API key, and run phase 2
    config_obj = Config.from_yaml(args.config)

    # Prefer OPENROUTER_API_KEY when using OpenRouter. Fallback to OPENAI_API_KEY.
    api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if api_key:
        config_obj.llm.api_key = api_key
        config_obj.llm.update_model_params({"api_key": api_key}, overwrite=True)
    else:
        if (config_obj.llm.api_base or "").startswith("https://openrouter.ai"):
            print(
                "Error: No API key found for OpenRouter. Set OPENROUTER_API_KEY or OPENAI_API_KEY.",
                file=sys.stderr,
            )
            return 1

    result = run_evolution(
        initial_program=args.initial,
        evaluator=args.evaluator,
        config=config_obj,
        iterations=args.iterations,
        output_dir=args.output,
        cleanup=not args.keep_output,
    )

    print("\nPhase 2 evolution complete.")
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
        default_out = Path(__file__).resolve().parent / "openevolve_output"
        print(f"\nArtifacts saved under: {default_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

