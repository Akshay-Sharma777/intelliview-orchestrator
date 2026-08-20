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


DATA_SCIENCE_PROMPTS = [
    {
        "domain": "data-science",
        "difficulty": "easy",
        "prompt_template": (
            "You are an expert Data Science interviewer. "
            "Generate one easy-level statistics interview question for a beginner. "
            "Focus on fundamental concepts such as mean, median, mode, variance, "
            "standard deviation, probability, or basic distributions. "
            "The question must be clear, technically accurate, relevant to Data Science, "
            "and non-repetitive."
        ),
    },
    {
        "domain": "data-science",
        "difficulty": "easy",
        "prompt_template": (
            "You are an expert Machine Learning interviewer. "
            "Generate one easy-level Machine Learning interview question. "
            "Focus on fundamental concepts such as supervised learning, "
            "unsupervised learning, training data, testing data, features, labels, "
            "or basic model evaluation. "
            "The question should be suitable for a beginner and must be "
            "clear, technically accurate, and non-repetitive."
        ),
    },
    {
        "domain": "data-science",
        "difficulty": "easy",
        "prompt_template": (
            "You are a Data Science interviewer. "
            "Generate one easy-level question about data preprocessing. "
            "Focus on practical fundamentals such as missing values, duplicate data, "
            "categorical encoding, scaling, or basic data cleaning. "
            "The question should test understanding rather than memorization "
            "and must be clear, relevant, and non-repetitive."
        ),
    },
    {
        "domain": "data-science",
        "difficulty": "medium",
        "prompt_template": (
            "You are an experienced Machine Learning interviewer. "
            "Generate one medium-level Machine Learning question involving "
            "model selection, feature engineering, overfitting, cross-validation, "
            "or evaluation metrics. "
            "Require the candidate to explain their reasoning or apply the concept "
            "to a practical situation. "
            "The question must be technically accurate, relevant, and non-repetitive."
        ),
    },
    {
        "domain": "data-science",
        "difficulty": "medium",
        "prompt_template": (
            "You are an experienced Data Science interviewer. "
            "Generate one medium-level statistics question that requires "
            "interpretation or practical application. "
            "Focus on topics such as hypothesis testing, confidence intervals, "
            "correlation, probability distributions, sampling, or statistical significance. "
            "The question should require reasoning and must be clear, relevant, "
            "technically accurate, and non-repetitive."
        ),
    },
    {
        "domain": "data-science",
        "difficulty": "medium",
        "prompt_template": (
            "You are a Data Science interviewer. "
            "Generate one medium-level practical Machine Learning scenario. "
            "Ask the candidate to determine an appropriate approach for a problem "
            "involving data preprocessing, class imbalance, model evaluation, "
            "feature selection, or model improvement. "
            "The question should test practical decision-making and must be "
            "technically accurate and non-repetitive."
        ),
    },
    {
        "domain": "data-science",
        "difficulty": "hard",
        "prompt_template": (
            "You are a senior Machine Learning interviewer. "
            "Generate one hard-level Machine Learning question that tests "
            "advanced reasoning and trade-offs. "
            "Focus on topics such as model bias and variance, imbalanced datasets, "
            "model interpretability, optimization, scalability, data leakage, "
            "or production model failures. "
            "The question should require a detailed technical explanation "
            "and must be challenging, relevant, and non-repetitive."
        ),
    },
    {
        "domain": "data-science",
        "difficulty": "hard",
        "prompt_template": (
            "You are a senior Data Science interviewer. "
            "Generate one hard-level statistics question involving advanced "
            "statistical reasoning, assumptions, uncertainty, experimentation, "
            "causal reasoning, or statistical inference. "
            "The question should require the candidate to analyze a situation, "
            "identify assumptions, and justify their approach. "
            "Ensure the question is technically accurate, challenging, "
            "and non-repetitive."
        ),
    },
    {
        "domain": "data-science",
        "difficulty": "hard",
        "prompt_template": (
            "You are a senior Data Science interviewer. "
            "Generate one hard-level real-world Data Science case-study question. "
            "Present a realistic business problem with incomplete or ambiguous "
            "information. Require the candidate to reason about data collection, "
            "preprocessing, feature engineering, model selection, evaluation, "
            "business metrics, and trade-offs. "
            "The question must be realistic, challenging, technically relevant, "
            "and non-repetitive."
        ),
    },
    {
        "domain": "data-science",
        "difficulty": "hard",
        "prompt_template": (
            "You are a senior Machine Learning interviewer. "
            "Generate one hard-level production Machine Learning case-study question. "
            "The scenario should involve challenges such as model drift, "
            "data distribution changes, latency, scalability, monitoring, "
            "retraining, or unreliable predictions. "
            "Require the candidate to propose a solution and explain the trade-offs. "
            "The question must test advanced problem-solving and be "
            "technically accurate and non-repetitive."
        ),
    },
]
