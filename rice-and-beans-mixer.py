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
from tabulate import tabulate

def read_db():
    # TODO receive db-file as command line parameter
    db = 'carb-db.csv'
    with open(db, 'r') as fp:
        reader = csv.DictReader(fp)
        return {
            row['Item']: {
                'Protein': float(row['Protein']),
                'Carb': float(row['Carb']),
                'Fat': float(row['Fat']),
            }
            for row in reader
        }


def find_complement(ingredients, A, B, alpha, target_carb_per_meal):
    return (target_carb_per_meal - ingredients[A]['Carb'] * alpha) / ingredients[B]['Carb']


def list_mixing_coefficients(ingredients, A, B, target_carb_per_meal):
    return [
        (alpha, find_complement(ingredients, A, B, alpha, target_carb_per_meal))
        for alpha in [0.05 * i for i in range(60)]
    ]


def cost_function(carb_error, protein_error, fat_error, energy_error):
    return carb_error + protein_error + 2 * fat_error + 3 * energy_error


def evaluate_mix(ingredients, A, B, target_macros, alpha, beta):
    total_carb = round(ingredients[A]['Carb'] * alpha + ingredients[B]['Carb'] * beta, 2)
    total_protein = round(ingredients[A]['Protein'] * alpha + ingredients[B]['Protein'] * beta, 2)
    total_fat = round(ingredients[A]['Fat'] * alpha + ingredients[B]['Fat'] * beta, 2)

    carb_error = round(total_carb - target_macros['Carb'], 2)
    protein_error = round(total_protein - target_macros['Protein'], 2)
    fat_error = round(total_fat - target_macros['Fat'], 2)
    energy_error = 4*(carb_error + protein_error) + 9*fat_error

    cost = cost_function(carb_error, protein_error, fat_error, energy_error)

    return (total_carb, total_protein, total_fat, carb_error, protein_error, fat_error, energy_error, cost)


def find_optimum_mix(ingredients, A, B, target_macros):
    grid = {
        coeffs: evaluate_mix(ingredients, A, B, target_macros, *coeffs)
        for coeffs in list_mixing_coefficients(ingredients, A, B, target_macros['Carb'])
    }

    print("=" * 80)
    print(f"Analaysis for: {A}, {B}")

    header = [
        'Alpha',
        'Beta',
        'Total Carb',
        'Total Protein',
        'Total Fat',
        'Carb Error',
        'Protein Error',
        'Fat Error',
        'Energy Error',
        'Cost',
    ]

    rows = [
        [*k, *v]
        for k, v in grid.items()
    ]

    print(tabulate(rows, headers=header))

    abs_costs = [abs(cost) for *_, cost in grid.values()]
    min_abs_cost = min(abs_costs)
    argmin = [
        k
        for k, (*_, cost) in grid.items()
        if abs(cost) == min_abs_cost
    ][0]
    print(f"Optimal Mix: {argmin}")
    return argmin, grid[argmin]

ingredients = read_db()
# TODO receive macros as command line parameters
target_macros = {
    'Carb': 59.3 / 2,
    'Protein': 18.9 / 2,
    'Fat': 5 / 2,
}

# TODO refactor reporting code to a different file
header = [
    'Carb A',
    'Carb B',
    'Alpha',
    'Beta',
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
for A, B in itertools.combinations(ingredients.keys(), 2):
    optimum_mix, mix_metrics = find_optimum_mix(ingredients, A, B, target_macros)
    alpha, beta = optimum_mix
    if alpha > 0 and beta > 0:
        rows.append([A, B, *optimum_mix, *mix_metrics])
    else:
        print(f"{A} and {B} don't balance out!")

print(tabulate(rows, headers = header, showindex="always"))
