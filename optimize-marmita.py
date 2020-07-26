from typing import List, Dict, Tuple

import numpy as np
from scipy.optimize import minimize
from scipy.optimize import Bounds
from scipy.optimize import SR1
from scipy.optimize import LinearConstraint
from pydantic import BaseModel
from tabulate import tabulate

import itertools
from config import load_ingredients, load_target_macros
from models import MacroDistribution

class FindOptimalMixRequest(BaseModel):
    macros: List[List[float]]
    target_macros: List[float]
    mix_dim: int
    macros_dim: int


class OptimalMixResponse(BaseModel):
    optimal_mix: List[float]
    macros: List[float]
    square_error: float


MACRO_WEIGHTS = np.array([4, 4, 9], dtype=np.float64)
def _build_cost_function(
    macros,
    target_macros,
    mix_dim,
    macros_dim,
):
    def f(x):
        return sum(
            MACRO_WEIGHTS[m] * (target_macros[m] - sum(x[i] * macros[i][m] for i in range(mix_dim))) ** 2
            for m in range(macros_dim)
        )
    return f


def _evaluate_mix(macros, mix, mix_dim, macros_dim) -> List[float]:
    return [
        sum(macros[i][m] * mix[i] for i in range(mix_dim))
        for m in range(macros_dim)
    ]


def find_optimal_mix(request: FindOptimalMixRequest) -> OptimalMixResponse:
    f = _build_cost_function(
        request.macros,
        request.target_macros,
        mix_dim=request.mix_dim,
        macros_dim=request.macros_dim,
    )
    bounds = Bounds(np.full(request.mix_dim, 0.9), np.full(request.mix_dim, 3.0))
    initial_guess = np.full(request.mix_dim, 1.0)
    result = minimize(
        f,
        initial_guess,
        method='trust-constr',
        jac="2-point",
        hess=SR1(),
        options={'verbose': 0},
        bounds=bounds
    )
    optimal_mix=[round(m, 4) for m in result.x.tolist()]
    achieved_macros = _evaluate_mix(
        request.macros,
        mix=optimal_mix,
        mix_dim=request.mix_dim,
        macros_dim=request.macros_dim,
    )
    return OptimalMixResponse(
        optimal_mix=optimal_mix,
        macros=achieved_macros,
        square_error=result.fun.astype(float),
    )


class BestMixForEachCombinationRequest(BaseModel):
    ingredients: Dict[str, List[float]]
    target_macros: List[float]


class BestMixForEachCombinationResponse(BaseModel):
    mixes: List[Tuple[Tuple[str, ...], OptimalMixResponse]]


def best_mix_for_each_combination(
        request: BestMixForEachCombinationRequest
) -> BestMixForEachCombinationResponse:
    ingredient_names = request.ingredients.keys()
    mixes = []
    for mix_dim in range(2, len(ingredient_names) + 1):
        for selection in itertools.combinations(ingredient_names, mix_dim):
            find_optimal_request = FindOptimalMixRequest(
                macros=[request.ingredients[k] for k in selection],
                target_macros=request.target_macros,
                mix_dim=mix_dim,
                macros_dim = len(request.target_macros),
            )
            mixes.append(
                (selection, find_optimal_mix(find_optimal_request))
            )

    mixes.sort(
        key=lambda x: x[1].square_error,
    )

    return BestMixForEachCombinationResponse(
        mixes=mixes
    )


def report(response: BestMixForEachCombinationResponse):
    rows = []
    for ingredients, optimal_mix in response.mixes:
        rows.append([
            ", ".join(
                f'{round(100 * component, 2)}g {ingredient_name}'
                for component, ingredient_name in zip(optimal_mix.optimal_mix, ingredients)
            ),
            *optimal_mix.macros,
            optimal_mix.square_error,
        ])
    print(tabulate(rows, headers=["Options", "g Protein", "g Carb", "g Fat", "sqr error"], showindex="always"))


def report2(
    request: BestMixForEachCombinationRequest,
    response: BestMixForEachCombinationResponse,
):
    rows = []
    ingredient_names = sorted(list(request.ingredients.keys()))

    def new_row():
        return ["" for _ in range(len(ingredient_names))]

    for ingredients, optimal_mix in response.mixes:
        row = new_row()
        for v, n in zip(optimal_mix.optimal_mix, ingredients):
            row[ingredient_names.index(n)] = f'{round(v * 100, 2)}g'
        rows.append([*row, *optimal_mix.macros, optimal_mix.square_error])

    headers = [
        *ingredient_names,
        'g Protein',
        'g Carb',
        'g Fat',
        'sqr error',
    ]
    print(tabulate(rows, headers=headers, showindex="always"))


if __name__ == "__main__":
    ingredients = load_ingredients()
    target_macros = load_target_macros()
    ingredient_names = ingredients.keys()

    request = BestMixForEachCombinationRequest(
        ingredients={k: v.macro_array() for k, v in ingredients.items()},
        target_macros=target_macros.macro_array()
    )
    response = best_mix_for_each_combination(request)

    report(response)
    report2(request, response)
