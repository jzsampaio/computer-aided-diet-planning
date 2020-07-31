import numpy as np
from typing import List, Union
from pydantic import BaseModel

class MacroDistribution:
    def __init__(self, protein, carb, fat):
        self.protein = protein
        self.carb = carb
        self.fat = fat

    def macro_array(self) -> List[float]:
        return [self.protein, self.carb, self.fat]

    @staticmethod
    def from_dict(row) -> 'MacroDistribution':
        return MacroDistribution(row['Protein'], row['Carb'], row['Fat'])


class EqualityConstraint(BaseModel):
    value: int


class MinMaxConstraint(BaseModel):
    min: int
    max: int


class MinConstraint(BaseModel):
    min: int


class MaxConstraint(BaseModel):
    max: int


Constraint = Union[
    EqualityConstraint,
    MinMaxConstraint,
    MaxConstraint,
    MinConstraint,
]


class IngredientConstraint(BaseModel):
    name: str
    constraint: Constraint


class MacroConstraint(BaseModel):
    protein: EqualityConstraint
    carb: EqualityConstraint
    fat: EqualityConstraint


class DietConstraints(BaseModel):
    ingredients: List[IngredientConstraint]
    macros: MacroConstraint


o = {
    "ingredients": [
        {
        "name": "Frango",
        "constraint": {
            "value": 180
            }
        },
        {
        "name": "*",
        "constraint": {
            "min": 90
            }
        }
    ],
    "macros": {
        "protein": {
            "value": 90
        },
        "carb": {
            "value": 90
        },
        "fat": {
            "value": 90
        },
    }
}

x = DietConstraints(**o)
print(x.dict())
