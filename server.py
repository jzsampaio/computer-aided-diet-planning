from fastapi import FastAPI

from messages import (
    BestMixForEachCombinationRequest,
    BestMixForEachCombinationResponse,
)

from macro_balancer import best_mix_for_each_combination

app = FastAPI()


@app.post("/balance-meal")
async def root(request: BestMixForEachCombinationRequest) -> BestMixForEachCombinationResponse:
    return best_mix_for_each_combination(request)
