#!/usr/bin/env python3
"""
:Description: Given a directory of CI logs, parse and organize the JSON output for easier consumption, focusing on full builds only.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Final, cast, no_type_check

BasicJsonType = dict[str, dict[str, int | str] | str]

@no_type_check
def aggregate_stats(stats: list[dict[str, int | float]]) -> dict[str, int | float]:
    """
    Aggregates statistics across multiple logs. Percentages are averaged, and all other numeric values are summed.

    :param stats: List of statistics dictionaries.
    :returns: Aggregated statistics dictionary.
    """
    accumulated_stats: dict[str, int | float] = {}
    total_tests: Final[int] = len(stats)
    percent_keys: set[str] = set()

    for tbl in stats:
        stats_key = "stats" if "stats" in tbl else "statistics"
        for key, value in tbl[stats_key].items():
            if not isinstance(value, (int, float)):
                continue
            if key.startswith("percent_"):
                percent_keys.add(key)
            accumulated_stats.setdefault(key, 0)
            accumulated_stats[key] += value

    for key in percent_keys:
        accumulated_stats[key] = round(accumulated_stats[key] / total_tests, 2)

    # Add total counts dynamically
    accumulated_stats["total_recipe_files"] = total_tests
    accumulated_stats["total_recipes_processed"] = total_tests

    return accumulated_stats


@no_type_check
def generate_summary(full_build_results: list[BasicJsonType]) -> BasicJsonType:
    """
    Summarizes the full build results.

    :param full_build_results: List of parsed JSON for full build logs.
    :returns: Summary JSON object.
    """
    fields_to_pull: Final[list[str]] = [
        "percent_errors",
        "percent_success",
    ]
    test_data: dict[str, dict[str, str | int]] = {}

    for result in full_build_results:
        test = Path(result["info"]["directory"]).name
        test_data.setdefault(test, {})
        test_data[test].setdefault("test_count", 0)
        test_data[test]["test_count"] += 1

        stats_key = "stats" if "stats" in result else "statistics"
        for field in fields_to_pull:
            if field in result[stats_key]:
                test_data[test].setdefault("full_build", {})
                test_data[test]["full_build"][field] = result[stats_key][field]

    return {
        "all_stages": {
            "full_build": aggregate_stats(full_build_results),
        },
        "test_summaries": dict(sorted(test_data.items())),
    }


def read_logs(log_dir: Path) -> list[BasicJsonType]:
    """
    Reads log files and parses JSON results.

    :param log_dir: Directory containing log files.
    :returns: List of parsed JSON results for full build logs.
    """
    full_build_results: list[BasicJsonType] = []
    seen_recipes = set()  # Track unique recipes to avoid duplicates

    for file in log_dir.iterdir():
        if file.is_dir() or file.name == ".DS_Store":
            continue
        content = file.read_text(encoding="utf-8")
        try:
            data = json.loads(content)
            if "info" in data and "command_name" in data["info"]:
                recipe_name = Path(data["info"]["directory"]).name
                if recipe_name not in seen_recipes:
                    full_build_results.append(data)
                    seen_recipes.add(recipe_name)  # Avoid duplicates
        except json.JSONDecodeError:
            print(f"Error parsing JSON from file: {file}", file=sys.stderr)
    return full_build_results


def main() -> None:
    """
    Main execution point of the script.
    """
    parser = argparse.ArgumentParser(
        description="Extracts JSON results from CI logs for full build testing."
    )
    parser.add_argument("dir", type=Path, help="Directory containing log files to parse.")  # type: ignore[misc]
    args = parser.parse_args()

    log_dir: Final[Path] = args.dir

    # Process logs for full build results
    full_build_results = read_logs(log_dir)

    # Generate final summary
    final_results = {
        "summary": cast(BasicJsonType, generate_summary(full_build_results)),
    }

    print(json.dumps(final_results, indent=2))


if __name__ == "__main__":
    main()
