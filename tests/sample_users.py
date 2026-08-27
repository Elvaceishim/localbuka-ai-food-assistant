from app.recommender.recommender import (
    recommend_restaurants
)


student_user = {
    "preferred_cuisines": ["Nigerian"],
    "price_range": "low",
    "dietary_restrictions": [],
    "likes_spicy": True,
    "location": "Yaba"
}

healthy_user = {
    "preferred_cuisines": ["Healthy"],
    "price_range": "medium",
    "dietary_restrictions": ["vegetarian"],
    "likes_spicy": False,
    "location": "Lekki"
}

date_night_user = {
    "preferred_cuisines": ["Italian"],
    "price_range": "high",
    "dietary_restrictions": [],
    "likes_spicy": False,
    "location": "Victoria Island"
}


print("\n=== Student User ===")
for restaurant in recommend_restaurants(student_user):
    print(restaurant)

print("\n=== Healthy User ===")
for restaurant in recommend_restaurants(healthy_user):
    print(restaurant)

print("\n=== Date Night User ===")
for restaurant in recommend_restaurants(date_night_user):
    print(restaurant)