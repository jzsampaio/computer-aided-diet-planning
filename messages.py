
from typing import (
    List,
    Dict,
    Tuple,
    Optional,
)

from pydantic import BaseModel

from models import (
    IngredientConstraint,
    MacroDistribution,
)


class FindOptimalMixRequest(BaseModel):
    macros: List[List[float]]
    min_constraints: List[Optional[float]]
    max_constraints: List[Optional[float]]
    target_macros: List[float]
    mix_dim: int
    macros_dim: int


class OptimalMixResponse(BaseModel):
    optimal_mix: List[float]
    macros: List[float]
    square_error: float


class BestMixForEachCombinationRequest(BaseModel):
    ingredients: Dict[str, MacroDistribution]
    target_macros: MacroDistribution
    ingredient_constraints: List[IngredientConstraint]


class BestMixForEachCombinationResponse(BaseModel):
    mixes: List[Tuple[Tuple[str, ...], OptimalMixResponse]]