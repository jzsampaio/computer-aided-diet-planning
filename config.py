import csv
import json

from models import MacroDistribution, DietConstraints

def _print_file(fname):
    with open(fname, 'r') as fin:
        print(fin.read())

def load_ingredients():
    fname = 'ingredients.csv'
    _print_file(fname)
    with open(fname, 'r') as fp:
        reader = csv.DictReader(fp)
        return {
            row['Item']: MacroDistribution.from_dict(row)
            for row in reader
        }

def load_constraints():
    fname = 'constraints.json'
    _print_file(fname)
    with open(fname, 'r') as fp:
        return DietConstraints(**json.load(fp))
