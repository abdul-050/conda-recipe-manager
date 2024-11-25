import json
import os
import sys

def parse_logs(log_dir):
    results = {
        "total_recipes": 0,
        "successful_conversions": 0,
        "successful_builds": 0,
        "failed_builds": 0,
        "failed_recipes": []
    }

    # Read logs
    with open(os.path.join(log_dir, "convert.log"), "r") as f:
        for line in f:
            if "Conversion successful" in line:
                results["successful_conversions"] += 1
            results["total_recipes"] += 1

    with open(os.path.join(log_dir, "build.log"), "r") as f:
        for line in f:
            if "Build succeeded" in line:
                results["successful_builds"] += 1
            elif "Build failed" in line:
                recipe = line.split(" ")[-1].strip()
                results["failed_recipes"].append(recipe)
                results["failed_builds"] += 1

    return results

def main(log_dir):
    results = parse_logs(log_dir)
    with open(os.path.join(log_dir, "final_report.json"), "w") as f:
        json.dump(results, f, indent=2)

    print("Final Report:")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: parse_full_build_logs.py <log_dir>")
        sys.exit(1)
    main(sys.argv[1])
