import csv
import json

from models import (
    MacroDistribution,
    DietConstraints,
)


def load_ingredients():
    fname = 'ingredients.csv'
    with open(fname, 'r') as fp:
        reader = csv.DictReader(fp)
        return {
            row['Item']: MacroDistribution(**row)
            for row in reader
        }


def load_constraints():
    fname = 'constraints.json'
    with open(fname, 'r') as fp:
        return DietConstraints(**json.load(fp))
