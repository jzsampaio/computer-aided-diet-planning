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
    value: float


class MinMaxConstraint(BaseModel):
    min: float
    max: float


class MinConstraint(BaseModel):
    min: float


class MaxConstraint(BaseModel):
    max: float


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

    def as_array(self) -> List[float]:
        return [self.protein.value, self.carb.value, self.fat.value]


class DietConstraints(BaseModel):
    ingredients: List[IngredientConstraint]
    macros: MacroConstraint
