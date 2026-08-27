# Reflection: Building LocalBuka AI Food Assistant

## Project Overview

LocalBuka AI Food Assistant is a restaurant recommendation system designed to help users discover restaurants in Lagos based on their preferences.

The project combines a rule-based recommendation engine with a Large Language Model (LLM) to produce personalised recommendations. Rather than relying on the LLM to determine which restaurants to recommend, the system first retrieves and ranks restaurants from a structured dataset before using the LLM to explain those recommendations in natural language.

My objective was not simply to connect an API to a chatbot. I wanted to build a system that balanced determinism and flexibility while exploring how traditional software engineering techniques can work alongside modern AI systems.

---

## Problem Definition

A user looking for a restaurant often has multiple constraints:

- Preferred cuisine
- Budget
- Location
- Dietary requirements
- Spice tolerance

A language model alone can generate restaurant suggestions, but there is no guarantee those recommendations will exist in the available dataset.

I therefore approached the problem as two separate tasks:

1. Finding the best restaurant matches.
2. Explaining those matches conversationally.

Separating retrieval from generation became the foundation of the system architecture.

---

## System Architecture

The final workflow follows a retrieval-first approach:

```text
User Query
    |
    v
Preference Extraction
    |
    v
Recommendation Engine
    |
    v
Restaurant Ranking
    |
    v
Context Builder
    |
    v
GPT-4.1 Mini (OpenRouter)
    |
    v
Natural Language Recommendation
```

The recommendation engine is responsible for finding restaurants.

The language model is responsible for explaining them.

This separation of responsibilities became one of the most important design decisions in the project.

---

## What I Built

The system consists of four major components.

### 1. Restaurant Dataset

I created a structured restaurant dataset stored in JSON format.

Each restaurant contains:

- Name
- Cuisine
- Location
- Price range
- Rating
- Spice level
- Dietary options
- Popular dishes

This dataset serves as the application's source of truth.

---

### 2. Recommendation Engine

The recommendation engine evaluates restaurants against user preferences and assigns a weighted score.

The scoring system considers:

| Factor               | Weight |
| -------------------- | ------ |
| Cuisine Match        | 35     |
| Price Match          | 25     |
| Dietary Requirements | 20     |
| Spice Preference     | 10     |
| Location Match       | 5      |
| Rating Bonus         | 0–5    |

Restaurants are ranked based on their total score and returned in descending order.

The engine also generates human-readable reasons explaining why each restaurant was selected.

For example:

```text
Cuisine match
Price match
Location match
```

This information is later passed to the language model.

---

### 3. Conversational Assistant

The assistant accepts natural-language requests such as:

> Recommend a healthy restaurant in Lekki.

The assistant performs lightweight preference extraction by identifying signals within the user's message.

Examples include:

- Cuisine preferences
- Budget preferences
- Location references
- Spice preferences

These extracted preferences are then supplied to the recommendation engine.

---

### 4. LLM Integration

The application integrates GPT-4.1 Mini through OpenRouter.

Rather than asking the model to determine recommendations itself, retrieved restaurants are converted into structured context.

Example:

```text
- Green Bowl | cuisine: Healthy | location: Lekki | rating: 4.8
- Fresh Roots | cuisine: Healthy | location: Victoria Island | rating: 4.7
```

The language model receives both:

- The original user request
- The retrieved restaurant context

Its role is limited to generating a natural-language explanation of the retrieved recommendations.

---

## Engineering Decisions and Tradeoffs

The most interesting part of the project was not the implementation itself but the decisions made during development.

### Why Not Let the LLM Recommend Restaurants Directly?

My initial instinct was to send user queries directly to the model and allow it to recommend restaurants.

While this would have reduced implementation effort, it created a reliability problem.

The model could:

- Recommend restaurants that do not exist
- Ignore important constraints
- Produce inconsistent results

For a recommendation system, correctness was more important than creativity.

I therefore chose a rule-based recommendation engine for retrieval and ranking while reserving the language model for explanation.

This decision improved transparency and made debugging significantly easier.

---

### Why Use Weighted Scoring?

I considered several approaches to ranking restaurants.

For a dataset of this size, introducing machine learning would have added complexity without providing meaningful benefits.

A weighted scoring system offered several advantages:

- Easy to understand
- Easy to debug
- Predictable behaviour
- Transparent recommendation logic

The tradeoff is that the system relies on manually chosen weights.

While less sophisticated than a learned ranking model, it was appropriate for the project's scope.

---

### Why JSON Instead of a Database?

I considered storing restaurant information in a database.

However, the dataset was small, static, and used only for experimentation.

Using JSON reduced development overhead and allowed me to focus on recommendation logic rather than database administration.

If the system needed to support:

- Frequent updates
- User-generated content
- Thousands of restaurants

I would migrate the data layer to PostgreSQL.

---

### Why Retrieval Before Generation?

This became the most important architectural decision in the project.

Allowing the language model to generate recommendations freely would have increased flexibility but also increased hallucination risk.

Retrieving restaurants first reduced flexibility but significantly improved reliability.

Given the purpose of the application, reliability was the more valuable property.

This tradeoff mirrors the same reasoning behind Retrieval-Augmented Generation (RAG) systems used in production AI applications.

---

## Challenges Encountered

### OpenRouter Rate Limits

While integrating OpenRouter, several free models repeatedly returned HTTP 429 errors.

This interrupted development and made testing unreliable.

Rather than continuing to fight rate limits, I switched to GPT-4.1 Mini and used paid credits for development.

This highlighted a practical lesson:

Building AI applications often involves dealing with infrastructure constraints rather than model logic alone.

---

### SSL/TLS Errors

One of the most frustrating problems occurred when API calls succeeded in isolated test scripts but failed inside the application.

The error appeared as:

```text
SSLV3_ALERT_BAD_RECORD_MAC
```

Because the issue appeared inconsistent, debugging was difficult.

I isolated the problem by:

1. Creating smaller test scripts
2. Testing the API independently
3. Comparing successful and failed execution paths

Eventually I discovered stale Python cache files were contributing to inconsistent behaviour.

Removing the project's `__pycache__` directories resolved the issue.

This reinforced the importance of isolating components and validating assumptions during debugging.

---

### Prompt Grounding

Early versions of the assistant relied too heavily on the language model.

Although responses sounded natural, they were not always grounded in retrieved data.

To improve reliability, I introduced:

- Structured context generation
- A stronger system prompt
- Retrieval-first architecture

This significantly reduced the risk of hallucinated recommendations.

---

### Recoommendation Filter

During testing, I discovered that my recommendation filter unintentionally excluded restaurants that matched dietary or price preferences when no cuisine preference was specified. The filtering logic relied too heavily on the overall score and implicitly favoured cuisine matches. I refactored the system so that eligibility and ranking became separate concerns: restaurants are included whenever they satisfy at least one user preference, while scores are used only for ranking. This improved recall without affecting recommendation quality.

---

## What I Learned

Several lessons emerged from the project.

### LLMs Are Not Databases

Language models are excellent at generating language but should not be treated as reliable sources of structured information.

Retrieval mechanisms remain necessary whenever correctness matters.

---

### Retrieval Improves Reliability

The quality of responses improved noticeably once recommendations were grounded in retrieved restaurant data.

The language model became more focused and significantly more consistent.

---

### AI Engineering Is More Than Prompting

Before building the project, it was tempting to view AI applications primarily as prompts wrapped around models.

In practice, most development effort was spent on:

- Data structures
- Ranking logic
- API integration
- Error handling
- Debugging
- System design

The language model was only one component of a larger system.

---

### Simplicity Has Value

Several times during development I considered more complex solutions.

Examples included:

- Machine-learning-based ranking
- Database integration
- Semantic search

In many cases, simpler solutions were sufficient.

The project reinforced the idea that complexity should be introduced only when it solves a real problem.

---

## What I Would Improve Next

If I continued developing LocalBuka, I would focus on retrieval rather than upgrading the language model.

The current system works well for straightforward queries but relies heavily on keyword matching.

For example:

> I want somewhere affordable around Lekki with healthy options and good grilled chicken.

Handling these types of requests effectively would benefit from semantic retrieval rather than simple keyword extraction.

Future improvements would include:

- Embedding-based search
- Vector database retrieval
- User preference memory
- Personalised recommendations
- Restaurant reviews and sentiment analysis
- Automated evaluation metrics
- Docker deployment
- Comprehensive unit and integration testing

These additions would move the application closer to a production-grade recommendation system.

---

## Final Thoughts

The most valuable lesson from this project was learning that effective AI systems are rarely powered by a language model alone.

The strongest results came from combining:

- Structured data
- Deterministic business logic
- Retrieval mechanisms
- Language generation

LocalBuka demonstrated how traditional software engineering and AI engineering complement each other.

More importantly, it changed how I think about building AI applications. Rather than asking, "What can the model do?" I began asking, "What responsibilities should belong to the model, and what responsibilities should belong to the system around it?"

That shift in thinking was the most important outcome of the project.
