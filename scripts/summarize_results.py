import sys
import re

log_file = sys.argv[1]

total_recipes = 0
failed_recipes = 0
passed_recipes = 0
failed_list = []

with open(log_file, "r") as f:
    for line in f:
        if "total_recipes_processed" in line:
            match = re.search(r'"total_recipes_processed": (\d+)', line)
            if match:
                total_recipes += int(match.group(1))
        elif "Error:" in line:
            recipe_match = re.search(r"Recipe: (\S+)", line)
            if recipe_match:
                failed_list.append(recipe_match.group(1))
                failed_recipes += 1

passed_recipes = total_recipes - failed_recipes

# Print summary
print(f"Total Recipes: {total_recipes}")
print(f"Passed Recipes: {passed_recipes}")
print(f"Failed Recipes: {failed_recipes}")
if failed_list:
    print("Failed Recipes:")
    for recipe in failed_list:
        print(f"- {recipe}")
