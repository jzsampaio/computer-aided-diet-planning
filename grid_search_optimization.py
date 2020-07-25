from tabulate import tabulate

def list_mixing_coefficients(t):
    dim = len(t)
    if dim == 2:
        return [
            (a, b)
            for a in [0.1 * i for i in range(20)]
            for b in [0.1 * i for i in range(20)]
        ]
    elif dim == 3:
        return [
            (a, b, c)
            for a in [0.1 * i for i in range(20)]
            for b in [0.1 * i for i in range(20)]
            for c in [0.1 * i for i in range(20)]
        ]

def cost_function(carb_error, protein_error, fat_error, energy_error):
    return abs(carb_error) + abs(protein_error) +  abs(fat_error) + abs(energy_error)


def sum_macro(ingredients, macro, t, coeffs):
    return round(sum(coeffs[i] * ingredients[t[i]][macro] for i in range(len(t))))


def evaluate_mix(ingredients, t, target_macros, coeffs):
    total_carb = sum_macro(ingredients, 'Carb', t, coeffs)
    total_protein = sum_macro(ingredients, 'Protein', t, coeffs)
    total_fat = sum_macro(ingredients, 'Fat', t, coeffs)

    carb_error = round(total_carb - target_macros['Carb'], 2)
    protein_error = round(total_protein - target_macros['Protein'], 2)
    fat_error = round(total_fat - target_macros['Fat'], 2)
    energy_error = 4*(carb_error + protein_error) + 9*fat_error

    cost = cost_function(carb_error, protein_error, fat_error, energy_error)

    return (total_carb, total_protein, total_fat, carb_error, protein_error, fat_error, energy_error, cost)


def find_optimum_mix(ingredients, t, target_macros):
    grid = {
        coeffs: evaluate_mix(ingredients, t, target_macros, coeffs)
        for coeffs in list_mixing_coefficients(t)
    }

    print("=" * 80)
    print(f"Analaysis for: {t}")

    header = [
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
