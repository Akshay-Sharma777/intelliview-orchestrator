QUALITY_EVALUATION_PROMPT = (
    "You are an expert technical interviewer. Evaluate this candidate answer. "
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