import json
from pathlib import Path


DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "restaurants.json"
)


def load_restaurants():
    """Load restaurant data from JSON file."""
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_score(user_preferences, restaurant):
    """
    Calculate recommendation score and provide reasons.
    Returns:
        tuple: (score, reasons)
    """

    score = 0
    reasons = []

    # Cuisine Match (35 points)
    preferred_cuisines = user_preferences.get(
        "preferred_cuisines", []
    )

    if restaurant["cuisine"] in preferred_cuisines:
        score += 35
        reasons.append("Cuisine match")

    # Price Match (25 points)
    if (
        restaurant["price_range"]
        == user_preferences.get("price_range")
    ):
        score += 25
        reasons.append("Price match")

    # Dietary Restrictions (20 points)
    user_restrictions = set(
        user_preferences.get(
            "dietary_restrictions", []
        )
    )

    restaurant_options = set(
        restaurant.get(
            "dietary_options", []
        )
    )

    if user_restrictions.issubset(
        restaurant_options
    ):
        score += 20

        if user_restrictions:
            reasons.append(
                "Dietary requirements satisfied"
            )

    # Spice Preference (10 points)
    if (
        user_preferences.get("likes_spicy")
        and restaurant["spice_level"] == "high"
    ):
        score += 10
        reasons.append(
            "Spicy food preference match"
        )

    # Location Match (5 points)
    if (
        restaurant["location"]
        == user_preferences.get("location")
    ):
        score += 5
        reasons.append("Location match")

    # Rating Bonus (0-5 points)
    rating_bonus = round(
        restaurant["rating"]
    )

    score += rating_bonus

    return score, reasons


def recommend_restaurants(
    user_preferences,
    top_n=5
):
    """
    Return top restaurant recommendations.
    """

    restaurants = load_restaurants()

    recommendations = []

    for restaurant in restaurants:

        score, reasons = calculate_score(
            user_preferences,
            restaurant
        )

        # Include any restaurant with at least one concrete match
        # (cuisine, price, dietary, spice, or location). Previously
        # this required a cuisine match or score >= 60, which silently
        # dropped every result for dietary-only or price-only queries
        # (e.g. "show me vegetarian restaurants") since those criteria
        # alone can't reach 60 points without also matching cuisine.
        if reasons:
            recommendations.append(
                {
                    "name": restaurant["name"],
                    "cuisine": restaurant["cuisine"],
                    "score": score,
                    "reasons": reasons,
                    "location": restaurant["location"],
                    "rating": restaurant["rating"],
                    "popular_dishes": restaurant[
                        "popular_dishes"
                    ],
                }
            )

    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    return recommendations[:top_n]