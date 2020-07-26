import numpy as np
from scipy.optimize import minimize
from scipy.optimize import Bounds
from scipy.optimize import SR1
from scipy.optimize import LinearConstraint

import itertools
from config import load_ingredients, load_target_macros
from models import MacroDistribution

w = np.array([4, 4, 9], dtype=np.float64)
def build_cost_function(
    macros,
    target_macros,
    mix_dim,
    macros_dim,
):
    def f(x):
        return sum(
            w[m] * (target_macros[m] - sum(x[i] * macros[i][m] for i in range(mix_dim))) ** 2
            for m in range(macros_dim)
        )
    return f


def evaluate_mix(macros, mix, mix_dim, macros_dim):
    return [
        sum(macros[i][m] * mix[i] for i in range(mix_dim))
        for m in range(macros_dim)
    ]

def optimize(ingredients, selection, target_macros):
    macros = [ingredients[k].v for k in selection]
    mix_dim=len(selection)
    macros_dim = target_macros.v.shape[0]
    f = build_cost_function(
        macros,
        target_macros.v,
        mix_dim=mix_dim,
        macros_dim=macros_dim,
    )

    bounds = Bounds(np.full(mix_dim, 0.9), np.full(mix_dim, 3.0))
    initial_guess = np.full(mix_dim, 1.0)
    result = minimize(
        f,
        initial_guess,
        method='trust-constr',
        jac="2-point",
        hess=SR1(),
        options={'verbose': 0},
        bounds=bounds
    )
    optimal_mix = [round(result.x[i] * 100, 2) for i in range(mix_dim)]
    return optimal_mix, result, macros, mix_dim, macros_dim


ingredients = load_ingredients()
target_macros = load_target_macros()
ingredient_names = ingredients.keys()

options = [
    (t, *optimize(ingredients, t, target_macros))
    for k in range(2, len(ingredient_names) + 1)
    for t in itertools.combinations(ingredients.keys(), k)
]

options.sort(
    key=lambda x: x[2].fun,
)


rows = []
for o in options:
    ingredients, mix, result, ingredient_macros, mix_dim, macros_dim = o
    rows.append([
        ", ".join([f'{mix[i]}g {ingredients[i]}' for i in range(mix_dim)]),
        *evaluate_mix(ingredient_macros, result.x, mix_dim, macros_dim),
        result.fun,
    ])
from tabulate import tabulate
print(tabulate(rows, headers=["Options", "g Protein", "g Carb", "g Fat", "sqr error"], showindex="always"))
