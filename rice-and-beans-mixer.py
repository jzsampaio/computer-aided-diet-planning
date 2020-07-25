"""
Usage:
    python rice-and-beans-mixer.py

The tool will try a full grid search on possible combinations of 2 carb
options.

Inputs:
    - Database of carb options
    - Target macro nutrients to be ingested in a meal

Output:
    - List of possible carb combinations

Motivation:

Say you have a balanced diet, but next week you decide to take 100 calories out
of it, and you also started taking Omega 3 pills (which include 1.5g fat). How
should you fix your carb options in order to take that into account? How do you
do that while considering the impact on protein and fat that whole-food carb
always produce? This tool provides an automated way of solving this problem.

Why Rice and Beans Mixer?

In Brazil it is very common to eat rice and beans on every-day meal. For a
Brazilian such as I, mixing 2 carb options is really a way to say "finding
alternatives to rice and beans". Deep down, what I'm really looking for is for
food combination that will help me achieve my fitness results, while still I'm
eating what my family taught me to eat (something that looks like rice with
something that looks like beans).
"""
import csv
import itertools
import json
from tabulate import tabulate

from grid_search_optimization import find_optimum_mix
from config import load_ingredients, load_target_macros


ingredients = load_ingredients()
target_macros = load_target_macros()

# TODO refactor reporting code to a different file
header = [
    'Carb A',
    'Carb B',
    'Carb C',
    'Alpha',
    'Beta',
    'Gama',
    'Total Carb',
    'Total Protein',
    'Total Fat',
    'Carb Error',
    'Protein Error',
    'Fat Error',
    'Energy Error',
    'Cost',
]
rows = []
for t in itertools.combinations(ingredients.keys(), 3):
    optimum_mix, mix_metrics = find_optimum_mix(ingredients, t, target_macros)
    rows.append([*t, *optimum_mix, *mix_metrics])

print("Target Macros")
print(json.dumps(target_macros, indent=2, sort=True))
print(tabulate(rows, headers = header, showindex="always"))
