import csv
import json

from models import MacroDistribution

def _print_file(fname):
    with open(fname, 'r') as fin:
        print(fin.read())

def load_ingredients():
    fname = 'carb-db.csv'
    _print_file(fname)
    with open(fname, 'r') as fp:
        reader = csv.DictReader(fp)
        return {
            row['Item']: MacroDistribution.from_dict(row)
            for row in reader
        }

def load_target_macros():
    fname = 'target-macros.json'
    _print_file(fname)
    with open(fname, 'r') as fp:
        return MacroDistribution.from_dict(json.load(fp))
