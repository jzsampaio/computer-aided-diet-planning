from typing import (
    List,
    Tuple,
    Optional,
)
import itertools

import numpy as np
from scipy.optimize import (
    Bounds,
    SR1,
    minimize,
)
from tabulate import tabulate

from config import (
    load_ingredients,
    load_constraints,
)
from models import (
    Constraint,
    EqualityConstraint,
    IngredientConstraint,
    MaxConstraint,
    MinConstraint,
    MinMaxConstraint,
)
from messages import (
    FindOptimalMixRequest,
    OptimalMixResponse,
    BestMixForEachCombinationRequest,
    BestMixForEachCombinationResponse,
)


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
    bounds = Bounds(
        np.array(request.min_constraints, dtype=np.float64),
        np.array(request.max_constraints, dtype=np.float64),
    )
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
    optimal_mix = [round(m, 4) for m in result.x.tolist()]
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


def _constraint_to_min_max(
        c: Constraint,
) -> Tuple[Optional[float], Optional[float]]:
    if isinstance(c, MinConstraint):
        return (c.min, np.inf)
    if isinstance(c, MaxConstraint):
        return (-np.inf, c.max)
    if isinstance(c, MinMaxConstraint):
        return (c.min, c.max)
    elif isinstance(c, EqualityConstraint):
        return (c.value, c.value)
    else:
        raise "Not implemented!"


DEFAULT_GENERAL_INGREDIENT_CONSTRAINT: Constraint = MinMaxConstraint(**{
    'min': 0.8,
    'max': 3.0
})


def _to_min_max_constraint_arrays(
    ingredient_constraints: List[IngredientConstraint],
    selection: Tuple[str, ...],
) -> Tuple[List[Optional[float]], List[Optional[float]]]:
    min_list = [None for _ in selection]
    max_list = [None for _ in selection]

    constraint_dict = {
        c.name: c.constraint
        for c in ingredient_constraints
    }

    general_constraint = constraint_dict.get('*', DEFAULT_GENERAL_INGREDIENT_CONSTRAINT)
    m, M = _constraint_to_min_max(general_constraint)
    min_list = [m for _ in selection]
    max_list = [M for _ in selection]

    for idx, ingredient in enumerate(selection):
        if ingredient not in constraint_dict:
            continue
        c = constraint_dict[ingredient]
        min_list[idx], max_list[idx] = _constraint_to_min_max(c)

    return min_list, max_list


def best_mix_for_each_combination(
    request: BestMixForEachCombinationRequest
) -> BestMixForEachCombinationResponse:
    ingredient_names = request.ingredients.keys()
    mixes = []
    for mix_dim in range(2, len(ingredient_names) + 1):
        for selection in itertools.combinations(ingredient_names, mix_dim):
            min_constraints, max_constraints = _to_min_max_constraint_arrays(request.ingredient_constraints, selection)
            find_optimal_request = FindOptimalMixRequest(
                macros=[request.ingredients[k].as_array() for k in selection],
                target_macros=request.target_macros.as_array(),
                mix_dim=mix_dim,
                macros_dim=len(request.target_macros.as_array()),
                min_constraints=min_constraints,
                max_constraints=max_constraints,
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
    constraints = load_constraints()
    ingredient_names = ingredients.keys()

    request = BestMixForEachCombinationRequest(
        ingredients=ingredients,
        target_macros=constraints.target_macros,
        ingredient_constraints=constraints.ingredient_constraints,
    )
    print(request.json(indent=2))
    response = best_mix_for_each_combination(request)

    report(response)
    report2(request, response)
