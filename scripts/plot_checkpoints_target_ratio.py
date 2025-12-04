#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt


CHECKPOINT_STEPS = [i for i in range(10, 101, 10)]
CHECKPOINT_DIR_PATTERN = "checkpoint_{}"
BEST_INFO_FILENAME = "best_program_info.json"


def load_target_ratio_for_checkpoint(checkpoints_root: Path, step: int) -> Optional[float]:
    """
    Load target_ratio from checkpoints_root/checkpoint_{step}/best_program_info.json
    Return None if the checkpoint folder or file is missing, or the key is absent.
    """
    checkpoint_dir = checkpoints_root / CHECKPOINT_DIR_PATTERN.format(step)
    info_path = checkpoint_dir / BEST_INFO_FILENAME
    if not info_path.is_file():
        return None
    try:
        with info_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return None
    value = data.get("target_ratio")
    if isinstance(value, (int, float)):
        return float(value)
    # Try nested common patterns if structure differs
    # e.g., {"metrics": {"target_ratio": x}}
    if isinstance(data.get("metrics"), dict):
        nested = data["metrics"].get("target_ratio")
        if isinstance(nested, (int, float)):
            return float(nested)
    return None


def collect_series(checkpoints_root: Path) -> Tuple[List[int], List[Optional[float]]]:
    """
    For a given checkpoints directory, collect x (steps) and y (target_ratio or None) lists.
    """
    x_values: List[int] = CHECKPOINT_STEPS
    y_values: List[Optional[float]] = []
    for step in CHECKPOINT_STEPS:
        y_values.append(load_target_ratio_for_checkpoint(checkpoints_root, step))
    return x_values, y_values


def plot_series(series_list: List[Tuple[str, List[int], List[Optional[float]]]], title: Optional[str], output: Optional[Path]) -> None:
    plt.figure(figsize=(10, 6), dpi=140)

    for label, x_values, y_values in series_list:
        # Convert None to NaN so matplotlib breaks the line on missing points
        y_plot = [float("nan") if v is None else float(v) for v in y_values]
        plt.plot(x_values, y_plot, marker="o", linewidth=2, markersize=5, label=label)
        # Annotate points with values (skip missing)
        for x, y in zip(x_values, y_values):
            if y is None:
                continue
            plt.text(x, float(y), f"{float(y):.3f}", ha="center", va="bottom", fontsize=8, alpha=0.9)

    plt.xlabel("Checkpoint", fontsize=12)
    plt.ylabel("target_ratio", fontsize=12)
    plt.xticks(CHECKPOINT_STEPS)
    plt.grid(True, linestyle="--", alpha=0.4)
    if title:
        plt.title(title, fontsize=13)
    plt.legend()
    plt.tight_layout()

    # Print numbers to console as a compact table
    for label, x_values, y_values in series_list:
        print(f"\n{label}")
        for x, y in zip(x_values, y_values):
            if y is None:
                print(f"  {x}: -")
            else:
                print(f"  {x}: {float(y):.6f}")

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output)
        print(f"Saved plot to: {output}")
    else:
        plt.show()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot target_ratio vs checkpoint across exactly three checkpoints directories."
    )
    parser.add_argument(
        "--dirs",
        nargs=3,
        default=["/Users/girigiri_yomi/Udel_Proj/openevolveAblation/examples/circle_packing/openevolve_output_phase1/checkpoints", 
        "/Users/girigiri_yomi/Udel_Proj/openevolveAblation/examples/circle_packing/openevolve_output_long_context_t8d8/checkpoints", 
        "/Users/girigiri_yomi/Udel_Proj/openevolveAblation/examples/circle_packing/openevolve_output_long_context_t16d16/checkpoints"],
        help="Exactly three checkpoints directories (each containing subfolders like checkpoint_10 ... checkpoint_100).",
    )
    parser.add_argument(
        "--names",
        nargs="*",
        default=["Phase 1", "T8D8", "T16D16"],
        help="Optional custom names for each input directory, in the same order. If fewer are provided, remaining will be auto-named.",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Optional plot title.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output image path (e.g., /path/to/plot.png). If omitted, the plot is shown interactively.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dirs = args.dirs

    labels: List[str] = []
    if args.names and len(args.names) > 0:
        for i in range(3):
            if i < len(args.names) and args.names[i]:
                labels.append(args.names[i])
            else:
                labels.append(Path(input_dirs[i]).name)
    else:
        labels = [Path(d).name for d in input_dirs]

    series_list: List[Tuple[str, List[int], List[Optional[float]]]] = []
    for dir_path, label in zip(input_dirs, labels):
        root = Path(dir_path).expanduser().resolve()
        x_values, y_values = collect_series(root)
        series_list.append((label, x_values, y_values))

    output_path = Path(args.output).expanduser().resolve() if args.output else None
    plot_series(series_list, args.title, output_path)


if __name__ == "__main__":
    main()


