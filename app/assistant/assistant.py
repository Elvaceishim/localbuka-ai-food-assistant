from app.recommender.recommender import (
    recommend_restaurants
)

from app.assistant.llm_client import (
    generate_response
)


def extract_preferences(user_message):

    message = user_message.lower()

    preferences = {
        "preferred_cuisines": [],
        "price_range": "medium",
        "dietary_restrictions": [],
        "likes_spicy": False,
        "location": "",
    }

    # Cuisine detection
    if "nigerian" in message:
        preferences["preferred_cuisines"].append(
            "Nigerian"
        )

    if "italian" in message:
        preferences["preferred_cuisines"].append(
            "Italian"
        )

    if "healthy" in message:
        preferences["preferred_cuisines"].append(
            "Healthy"
        )

    # Price detection
    if any(
        word in message
        for word in [
            "cheap",
            "affordable",
            "budget"
        ]
    ):
        preferences["price_range"] = "low"

    if any(
        word in message
        for word in [
            "expensive",
            "premium",
            "luxury"
        ]
    ):
        preferences["price_range"] = "high"

    # Spice preference
    if "spicy" in message:
        preferences["likes_spicy"] = True

    # Dietary restriction detection
    dietary_keywords = [
        "vegetarian",
        "vegan",
        "halal",
        "gluten-free",
        "gluten free",
    ]

    for keyword in dietary_keywords:

        if keyword in message:

            normalized = keyword.replace(
                "gluten free", "gluten-free"
            )

            preferences["dietary_restrictions"].append(
                normalized
            )

    # Location detection
    locations = [
        "yaba",
        "lekki",
        "ikeja",
        "ikoyi",
        "ajah",
        "surulere",
        "victoria island"
    ]

    for location in locations:

        if location in message:

            preferences["location"] = (
                location.title()
            )

            break

    return preferences


def format_restaurant_context(recommendations):
    """
    Turn recommender output into a compact, LLM-friendly context block
    so the assistant only talks about restaurants that were actually
    retrieved (retrieval-first workflow, see PROJECT_PLAN.md).
    """

    if not recommendations:
        return "No matching restaurants were found for these preferences."

    lines = []

    for restaurant in recommendations:

        dishes = ", ".join(restaurant.get("popular_dishes", []))

        lines.append(
            f"- {restaurant['name']} | cuisine: {restaurant['cuisine']} "
            f"| location: {restaurant['location']} "
            f"| rating: {restaurant['rating']} "
            f"| popular dishes: {dishes} "
            f"| why it matches: {', '.join(restaurant['reasons']) or 'general match'}"
        )

    return "\n".join(lines)


def chat(user_message):

    preferences = extract_preferences(user_message)

    recommendations = recommend_restaurants(preferences)

    context = format_restaurant_context(recommendations)

    return generate_response(user_message, context=context)


if __name__ == "__main__":

    print(
        "\n🍽️ LocalBuka Food Assistant"
    )

    print(
        "Type 'exit' to quit.\n"
    )

    while True:

        user_input = input(
            "\nYou: "
        )

        if (
            user_input.lower()
            == "exit"
        ):
            break

        response = chat(
            user_input
        )

        print(
            "\nAssistant:"
        )

        print(response)