import numpy as np
from typing import List

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
