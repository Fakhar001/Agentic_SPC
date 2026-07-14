"""Run the manuscript's 200,000-replication EWMA ARL analysis."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.arl_analysis import run_reference_arl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repetitions", type=int, default=200_000)
    parser.add_argument("--seed", type=int, default=20260627)
    parser.add_argument("--output", type=Path, default=Path("outputs/arl_results.csv"))
    args = parser.parse_args()
    table = run_reference_arl(args.output, repetitions=args.repetitions, seed=args.seed)
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
