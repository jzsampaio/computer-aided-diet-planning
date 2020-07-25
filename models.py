import numpy as np

class MacroDistribution:
    def __init__(self, protein, carb, fat):
        self.protein = protein
        self.carb = carb
        self.Fat = fat
        self.v = np.array([protein, carb, fat], dtype=np.float64)

    @staticmethod
    def from_dict(row) -> 'MacroDistribution':
        return MacroDistribution(row['Protein'], row['Carb'], row['Fat'])
