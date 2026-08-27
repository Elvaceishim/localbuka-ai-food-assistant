from fastapi import FastAPI, HTTPException

from app.api.models import (
    ChatRequest,
    ChatResponse,
    RecommendationRequest,
    RecommendationResponse,
)

from app.assistant.assistant import chat
from app.recommender.recommender import (
    recommend_restaurants
)

app = FastAPI(
    title="LocalBuka AI Assistant"
)


@app.post(
    "/recommendations",
    response_model=RecommendationResponse
)
def recommendations(
    preferences: RecommendationRequest
):

    results = recommend_restaurants(
        preferences.model_dump()
    )

    return {
        "recommendations": results
    }


@app.post("/chat", response_model=ChatResponse)
def assistant_chat(
    payload: ChatRequest
):

    try:
        response = chat(
            payload.message
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

    return {
        "response": response
    }


@app.get("/health")
def health():

    return {
        "status": "ok"
    }

