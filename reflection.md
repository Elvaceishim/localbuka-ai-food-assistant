# Reflection: Building LocalBuka AI Food Assistant

## Project Overview

LocalBuka AI Food Assistant is a restaurant recommendation system designed to help users discover restaurants in Lagos based on their preferences.

The project combines a rule-based recommendation engine with a Large Language Model (LLM) to produce personalised recommendations. Rather than relying on the LLM to determine which restaurants to recommend, the system first retrieves and ranks restaurants from a structured dataset before using the LLM to explain those recommendations in natural language.

My objective was not simply to connect an API to a chatbot. I wanted to build a system that balanced determinism and flexibility while exploring how traditional software engineering techniques can work alongside modern AI systems.

The application can be accessed through a command-line chat interface and through FastAPI endpoints exposed via Swagger UI for testing.

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

The recommendation engine retrieves and ranks restaurants while the language model explains those recommendations. Separating retrieval from generation became one of the most important design decisions in the project.

---

## Architectural Approach

LocalBuka uses a hybrid architecture that combines rule-based retrieval with LLM-powered response generation.

The recommendation engine itself is not a machine learning model. Restaurant ranking is performed using deterministic business rules and a weighted scoring system based on cuisine preferences, location, price range, dietary requirements, spice preferences, and restaurant ratings.

The LLM is responsible only for transforming retrieved recommendations into natural-language responses.

I deliberately separated retrieval from generation because language models are not reliable databases. Allowing the model to determine recommendations directly would increase the risk of hallucinated restaurants, inconsistent results, and ignored user constraints.

By grounding the model on retrieved restaurant data, I was able to maintain control over recommendation quality while still benefiting from the conversational capabilities of the LLM.

This design follows the same general principle used in Retrieval-Augmented Generation (RAG) systems. However, instead of using embeddings and vector search, the retrieval layer in this project is implemented using structured data and rule-based ranking logic.

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

The most significant debugging challenge involved API calls to OpenRouter.

A standalone test script successfully generated responses from GPT-4.1 Mini, but the same API call consistently failed inside the application with:

SSLV3_ALERT_BAD_RECORD_MAC

Because the API worked in isolation, I knew the issue was not the OpenRouter service itself. I isolated components, created smaller test scripts, compared successful and failed execution paths, and added logging around requests.

This allowed me to narrow the problem scope and eliminate the model, API provider, and network configuration as likely causes.

Eventually, I discovered stale Python cache files were contributing to inconsistent behaviour. Removing the project's **pycache** directories resolved the issue.

This experience reinforced the importance of isolating components and validating assumptions during debugging.

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

### Recommendation Filter

During testing, I discovered that my recommendation filter unintentionally excluded restaurants that matched dietary or price preferences when no cuisine preference was specified. The filtering logic relied too heavily on the overall score and implicitly favoured cuisine matches. I refactored the system so that eligibility and ranking became separate concerns: restaurants are included whenever they satisfy at least one user preference, while scores are used only for ranking. This improved recall without affecting recommendation quality.

---

## Risks and Guardrails

Although LocalBuka is a relatively small project, deploying a recommendation assistant in production introduces several risks.

### Hallucinated Recommendations

The most significant risk is the language model recommending restaurants that do not exist in the dataset or providing inaccurate information about restaurants.

To mitigate this risk, I adopted a retrieval-first architecture. Restaurants are retrieved from the dataset before being passed to the language model, and the model is explicitly instructed to use only the supplied restaurant context.

### Outdated Information

Restaurant information such as ratings, menus, operating hours, and locations can change over time.

In a production system, restaurant data should be regularly refreshed from trusted sources and versioned to ensure recommendations remain accurate.

### Inappropriate or Unsafe Responses

Large language models can occasionally generate responses that are irrelevant, misleading, or inappropriate.

To reduce this risk, I would implement moderation checks, stricter system prompts, output validation, and monitoring of user interactions to identify problematic responses.

### Poor Recommendation Quality

A user may receive recommendations that technically match their preferences but are not genuinely useful.

To address this, I would continuously monitor user engagement metrics, collect feedback, and use those signals to improve ranking logic and recommendation quality over time.

Overall, I believe combining deterministic retrieval with carefully constrained language generation provides a safer and more reliable user experience than relying entirely on an LLM.

---

## Managing LLM Costs

During development I used GPT-4.1 Mini through OpenRouter because it provided reliable responses and predictable behaviour.

If the application were deployed at scale, API cost management would become an important consideration.

Several approaches could help control costs:

- Use smaller and cheaper models for routine requests.
- Limit the amount of retrieved context sent to the model.
- Cache frequently requested recommendations.
- Avoid unnecessary model calls when deterministic logic can provide an answer.
- Monitor token usage and establish spending limits.
- Use retrieval and ranking logic to reduce the amount of reasoning required from the model.

The retrieval-first architecture already helps reduce costs because the recommendation engine performs most of the decision-making work. The language model is used primarily for explanation, which keeps prompts relatively small and predictable.

If usage increased significantly, I would evaluate whether some recommendation responses could be generated using templates rather than requiring an LLM call for every request.

---

## Evaluating Recommendation Quality

Building the recommendation system was only part of the challenge. If the application were deployed, I would also need a way to measure whether the recommendations were actually useful.

I would evaluate recommendation quality using both user behaviour and system metrics.

Examples include:

- Click-through rate on recommended restaurants
- Number of restaurant profile views after recommendations
- User ratings or feedback on recommendations
- Repeat usage rate
- Recommendation acceptance rate

I would also log recommendation inputs and outputs to identify situations where users consistently ignored recommendations.

For example, if users frequently searched for healthy restaurants in Lekki but rarely interacted with the returned results, that could indicate problems with the ranking logic, restaurant data, or preference extraction process.

Over time, these signals could be used to refine recommendation weights or transition to a machine-learning-based ranking model trained on real user interactions.

This reinforced an important lesson: a recommendation system should not only generate recommendations but also provide mechanisms for measuring whether those recommendations create value for users.

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

## Scaling Considerations

The current architecture is intentionally simple and appropriate for a small dataset and limited traffic.

If LocalBuka needed to support millions of users and a significantly larger restaurant catalogue, several architectural changes would be necessary.

The restaurant dataset would move from JSON files to a relational database such as PostgreSQL to support efficient querying, updates, and indexing.

Recommendation requests would be served through dedicated API services behind a load balancer to support higher traffic volumes.

Frequently requested recommendations could be cached to reduce latency and lower infrastructure costs.

The recommendation engine itself would likely evolve beyond manually defined rules. Rather than relying solely on weighted scoring, I would incorporate user interaction data such as clicks, views, favourites, and completed orders to build personalised ranking models.

Restaurant retrieval could also move toward embedding-based semantic search and vector database retrieval to support more complex natural-language queries.

User preferences would be stored persistently, allowing recommendations to adapt based on historical behaviour rather than a single request.

While the current implementation prioritises simplicity, transparency, and ease of debugging, a production-scale version would place greater emphasis on scalability, observability, personalisation, and operational reliability.

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
