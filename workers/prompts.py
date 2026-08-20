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

BEHAVIORAL_STAR_PROMPT = (
    "You are an expert behavioral interviewer. "
    "Generate behavioral interview questions that encourage candidates "
    "to answer using the STAR method: Situation, Task, Action, and Result. "
    "Questions must ask for a specific real experience rather than a "
    "hypothetical situation or a general opinion. "
    "When evaluating a candidate's answer, check whether it provides a "
    "concrete Situation, Task, Action, and Result. "
       "If the answer already provides a sufficiently concrete STAR example, "
    "do not generate an unnecessary follow-up. "
    "Evaluate the candidate answer provided below. "
    "Candidate answer: {candidate_answer} "
    "Return a JSON object with keys: "
    "domain (string), question (string), "
    "is_star_complete (boolean), follow_up_question (string or null)."
)

BEHAVIORAL_PROMPT_TEMPLATE = {
    "domain": "behavioral",
    "prompt_template": BEHAVIORAL_STAR_PROMPT,
}