from typing import (
    List,
    Union,
    Tuple,
)

from pydantic import BaseModel


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


MacroList = Tuple[float, float, float]


class MacroConstraint(BaseModel):
    protein: EqualityConstraint
    carb: EqualityConstraint
    fat: EqualityConstraint

    def as_array(self) -> MacroList:
        return [self.protein.value, self.carb.value, self.fat.value]


class MacroDistribution(BaseModel):
    protein: float
    carb: float
    fat: float

    def as_array(self) -> MacroList:
        return [self.protein, self.carb, self.fat]


class DietConstraints(BaseModel):
    ingredient_constraints: List[IngredientConstraint]
    target_macros: MacroDistribution
