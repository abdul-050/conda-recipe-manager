import sys
import json

# Check for input arguments
if len(sys.argv) != 2:
    print("Usage: python summary.py <log_file>")
    sys.exit(1)

log_file = sys.argv[1]

# Initialize counters
total_recipes = 0
failed_recipes = 0
passed_recipes = 0
failed_list = []

# Parse the log file
try:
    with open(log_file, "r") as f:
        logs = json.load(f)  # Parse the JSON content
        
        # Extract statistics
        if "statistics" in logs:
            stats = logs["statistics"]
            total_recipes += stats.get("total_recipes_processed", 0)
            failed_recipes += stats.get("total_errors", 0)
            passed_recipes = total_recipes - failed_recipes

        # Extract failed recipes
        if "recipes_with_build_error_code" in logs:
            failed_list.extend(logs["recipes_with_build_error_code"])

except FileNotFoundError:
    print(f"Error: File '{log_file}' not found.")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Error: Failed to parse JSON from '{log_file}'.")
    sys.exit(1)

# Print summary
print(f"Total Recipes: {total_recipes}")
print(f"Passed Recipes: {passed_recipes}")
print(f"Failed Recipes: {failed_recipes}")
if failed_list:
    print("Failed Recipes:")
    for recipe in failed_list:
        print(f"- {recipe}")
