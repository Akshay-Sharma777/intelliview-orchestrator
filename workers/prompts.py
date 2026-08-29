"""
Prompt templates for the automated interview preparation platform.

This module contains prompt definitions only.
It intentionally does not contain LLM clients, API wrappers, or
prompt-execution logic.
"""

# ---------------------------------------------------------------------------
# Evaluation Prompts
# ---------------------------------------------------------------------------

QUALITY_EVALUATION_PROMPT = (
    "You are an expert technical interviewer. "
    "Evaluate this candidate answer. "
    "Return a JSON object with keys: overall_quality_score (0-100), "
    "relevance (0-1), completeness (0-1), clarity (0-1), feedback (string)."
)

TECHNICAL_ACCURACY_PROMPT = (
    "You are a technical interviewer evaluating a candidate's answer. "
    "Return a JSON object with keys: accuracy_score (0-100), "
    "correct_concepts_count (int), incorrect_concepts_count (int), "
    "knowledge_gaps (list of strings)."
)

COMMUNICATION_EVALUATION_PROMPT = (
    "Evaluate the candidate's communication quality. "
    "Return a JSON object with keys: clarity_score (0-100), "
    "professionalism (0-100), confidence_level (0-1), "
    "pace_appropriateness (0-1)."
)


# ---------------------------------------------------------------------------
# Junior System Design Prompt Templates
# ---------------------------------------------------------------------------

JUNIOR_SYSTEM_DESIGN_SCALABILITY_PROMPT = (
    "Generate one junior-level system-design interview question focused "
    "on foundational scalability. The question should ask the candidate "
    "to reason about a simple application starting with a single server "
    "and explain when and why it should move toward a multi-tier or "
    "multi-server architecture. Include basic load balancing and "
    "horizontal scaling considerations. Keep the expected architecture "
    "simple and avoid advanced distributed-system concepts."
)

JUNIOR_SYSTEM_DESIGN_DATA_PROMPT = (
    "Generate one junior-level system-design interview question focused "
    "on basic data-storage decisions. The scenario should require the "
    "candidate to choose between a relational database and a NoSQL "
    "database and explain the reasoning behind the choice. The question "
    "may also involve a basic caching layer using Redis or Memcached. "
    "Keep the scale and requirements realistic for a junior engineer "
    "and avoid advanced consistency models, distributed transactions, "
    "or multi-region database architectures."
)

JUNIOR_SYSTEM_DESIGN_API_PROMPT = (
    "Generate one junior-level system-design interview question focused "
    "on designing and protecting a simple API. The question should test "
    "fundamental API rate limiting, basic load balancing, caching, and "
    "request-handling concepts. The candidate should explain where these "
    "components fit in the architecture and what problems they solve. "
    "Keep the problem bounded and avoid advanced event-driven systems, "
    "distributed transactions, multi-region replication, or complex "
    "failure-handling strategies."
)


# ---------------------------------------------------------------------------
# Senior System Design Prompt Templates
# ---------------------------------------------------------------------------

SENIOR_SYSTEM_DESIGN_DISTRIBUTED_PROMPT = (
    "Generate one senior-level system-design interview question involving "
    "a large-scale distributed system. The question must require the "
    "candidate to analyze architectural trade-offs involving throughput, "
    "latency, availability, consistency, and partition tolerance. Include "
    "a scenario where CAP theorem considerations and failure-domain "
    "isolation matter. The candidate should justify trade-offs rather "
    "than simply name technologies."
)

SENIOR_SYSTEM_DESIGN_MULTIREGION_PROMPT = (
    "Generate one senior-level system-design interview question involving "
    "a globally distributed, multi-region system. Require the candidate "
    "to reason about cross-region replication, consistency models, "
    "regional failures, asynchronous processing, event-driven "
    "backpressure, and recovery behavior. Include competing latency, "
    "availability, correctness, and operational-cost requirements. "
    "The question should require the candidate to clarify ambiguous "
    "business requirements before finalizing the architecture."
)

SENIOR_SYSTEM_DESIGN_TRANSACTIONS_PROMPT = (
    "Generate one senior-level system-design interview question involving "
    "multiple services that must coordinate state changes reliably at "
    "large scale. Require discussion of distributed transactions, "
    "idempotency, retries, partial failures, consistency guarantees, "
    "failure-domain isolation, and asynchronous event processing. "
    "Introduce ambiguous or competing business constraints such as "
    "cost versus latency or consistency versus availability. The "
    "candidate should identify assumptions, discuss alternatives, and "
    "justify the final architecture based on explicit trade-offs."
)


# ---------------------------------------------------------------------------
# System Design Prompt Registry
# ---------------------------------------------------------------------------

SYSTEM_DESIGN_PROMPT_CONFIGS = [
    {
        "domain": "system-design",
        "seniority": "junior",
        "prompt_template": JUNIOR_SYSTEM_DESIGN_SCALABILITY_PROMPT,
    },
    {
        "domain": "system-design",
        "seniority": "junior",
        "prompt_template": JUNIOR_SYSTEM_DESIGN_DATA_PROMPT,
    },
    {
        "domain": "system-design",
        "seniority": "junior",
        "prompt_template": JUNIOR_SYSTEM_DESIGN_API_PROMPT,
    },
    {
        "domain": "system-design",
        "seniority": "senior",
        "prompt_template": SENIOR_SYSTEM_DESIGN_DISTRIBUTED_PROMPT,
    },
    {
        "domain": "system-design",
        "seniority": "senior",
        "prompt_template": SENIOR_SYSTEM_DESIGN_MULTIREGION_PROMPT,
    },
    {
        "domain": "system-design",
        "seniority": "senior",
        "prompt_template": SENIOR_SYSTEM_DESIGN_TRANSACTIONS_PROMPT,
    },
]
PRODUCT_MANAGEMENT_PROMPTS = [
    {
        "domain": "product",
        "prompt_template": (
            "A food-delivery app can build only two of these four features this quarter: "
            "faster checkout, restaurant loyalty rewards, scheduled delivery, and a "
            "personalized home feed. Prioritize the features and explain your decision. "
            "Consider user impact, business value, strategic alignment, engineering effort, "
            "and trade-offs."
        ),
        "rubric_hint": (
            "Evaluate whether the candidate clearly defines the product goal and target "
            "users, establishes prioritization criteria, compares impact against effort, "
            "makes an explicit ranking, explains trade-offs, and states key assumptions."
        ),
    },
    {
        "domain": "product",
        "prompt_template": (
            "A ride-sharing app has budget to improve only one of three areas: reducing "
            "driver cancellation, improving rider pickup accuracy, or adding a loyalty "
            "program. As the product manager, prioritize one initiative and explain how "
            "you would decide between the options."
        ),
        "rubric_hint": (
            "Evaluate problem framing, identification of affected users, prioritization "
            "criteria, expected customer and business impact, effort or feasibility "
            "considerations, trade-off reasoning, and clarity of the final recommendation."
        ),
    },
    {
        "domain": "product",
        "prompt_template": (
            "You are the product manager for a music streaming app. Monthly active users "
            "are stable, but 30-day retention has fallen from 40% to 30%. Identify the "
            "metrics you would examine to diagnose the decline and explain how each metric "
            "would help you find the underlying problem."
        ),
        "rubric_hint": (
            "Evaluate whether the candidate distinguishes the north-star metric from "
            "diagnostic metrics, considers retention cohorts and segments, identifies "
            "activation and engagement metrics, proposes meaningful breakdowns, and "
            "connects metric changes to actionable hypotheses."
        ),
    },
    {
        "domain": "product",
        "prompt_template": (
            "A mobile payments product has increased new-user sign-ups by 25%, but the "
            "percentage of users completing their first payment has decreased. As the "
            "product manager, define the key metrics and funnel stages you would analyze "
            "to understand what is happening and decide what to improve first."
        ),
        "rubric_hint": (
            "Evaluate funnel understanding, metric selection, conversion analysis, "
            "segmentation, identification of possible drop-off points, prioritization "
            "of investigation areas, and the ability to turn metrics into product actions."
        ),
    },
    {
        "domain": "product",
        "prompt_template": (
            "Estimate the number of food-delivery orders placed in a large Indian city "
            "on an average day. State your assumptions, build a simple estimation model, "
            "calculate the estimate step by step, and explain which assumptions have the "
            "largest effect on the result."
        ),
        "rubric_hint": (
            "Evaluate whether the candidate defines the scope, uses reasonable and "
            "explicit assumptions, breaks the estimate into logical components, performs "
            "consistent calculations, checks the result for plausibility, and identifies "
            "the assumptions most sensitive to the final estimate."
        ),
    },
]

SDE_PROMPT_TEMPLATES = [
    {
        "domain": "sde",
        "difficulty": "easy",
        "prompt_template": (
            "Role: Act as an experienced Software Engineering interviewer. "
            "Context: Generate one technical SDE interview question for a candidate "
            "at an easy difficulty level. Focus on fundamental programming, "
            "object-oriented programming, basic data structures, databases, "
            "debugging, or core software engineering concepts. "
            "Constraints: The question must be clear, practical, and suitable for "
            "an entry-level SDE interview. Vary the topic and question style across "
            "generations. Do not repeat or closely rephrase previously generated "
            "questions. Do not provide the answer or explanation. Return only the "
            "interview question."
        ),
    },
    {
        "domain": "sde",
        "difficulty": "medium",
        "prompt_template": (
            "Role: Act as an experienced Software Engineering interviewer. "
            "Context: Generate one technical SDE interview question for a candidate "
            "at a medium difficulty level. Focus on algorithms, data structures, "
            "database design, SQL, REST APIs, concurrency, testing, debugging, "
            "or practical software engineering problem-solving. "
            "Constraints: The question should require reasoning or application of "
            "technical concepts rather than simple recall. Vary the topic, scenario, "
            "and problem style across generations. Do not repeat or closely rephrase "
            "previously generated questions. Do not provide the answer or explanation. "
            "Return only the interview question."
        ),
    },
    {
        "domain": "sde",
        "difficulty": "hard",
        "prompt_template": (
            "Role: Act as a senior Software Engineering interviewer conducting an "
            "advanced SDE interview. Context: Generate one challenging technical "
            "question involving system design, distributed systems, scalability, "
            "performance optimization, fault tolerance, concurrency, data-intensive "
            "systems, or advanced software architecture. "
            "Constraints: The question must require multi-step technical reasoning "
            "and should reflect real-world engineering challenges. Vary the system, "
            "constraints, and problem scenario across generations. Do not repeat or "
            "closely rephrase previously generated questions. Avoid questions that "
            "can be answered with simple definitions. Do not provide the answer or "
            "explanation. Return only the interview question."
        ),
    },
]
