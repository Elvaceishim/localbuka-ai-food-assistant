from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


class RecommendationRequest(BaseModel):
    preferred_cuisines: list[str]
    price_range: str
    dietary_restrictions: list[str]
    likes_spicy: bool
    location: str


class RestaurantRecommendation(BaseModel):
    name: str
    cuisine: str
    score: int
    reasons: list[str]
    location: str
    rating: float
    popular_dishes: list[str]


class RecommendationResponse(BaseModel):
    recommendations: list[RestaurantRecommendation]