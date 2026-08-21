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


MARKETING_SALES_PROMPTS = [
    {
        "domain": "marketing-sales",
        "prompt_template": (
            "You are an expert marketing and sales interviewer. "
            "Generate one realistic sales pitch interview question. "
            "Give the candidate a specific product, target customer, and selling situation "
            "and ask them to explain how they would pitch the product. "
            "The question should test customer understanding, value proposition, "
            "persuasion, and objection handling. "
            "Make the scenario realistic and avoid generic interview questions."
        ),
    },
    {
        "domain": "marketing-sales",
        "prompt_template": (
            "You are an expert marketing interviewer. "
            "Generate one campaign case-study interview question involving an "
            "underperforming marketing campaign. "
            "Provide realistic information such as the target audience, campaign goal, "
            "and performance issue, then ask the candidate how they would diagnose "
            "the problem and improve the campaign. "
            "Test analytical thinking, audience segmentation, channel selection, "
            "and campaign optimization. "
            "Avoid generic questions."
        ),
    },
    {
        "domain": "marketing-sales",
        "prompt_template": (
            "You are an expert sales interviewer. "
            "Generate one realistic customer-objection scenario. "
            "Present a customer who is interested in a product but raises a specific "
            "objection such as price, competitor preference, lack of trust, or unclear ROI. "
            "Ask the candidate how they would respond and move the conversation toward "
            "a successful sale. "
            "Test consultative selling, active listening, and objection handling. "
            "Avoid generic questions."
        ),
    },
    {
        "domain": "marketing-sales",
        "prompt_template": (
            "You are an expert growth marketing interviewer. "
            "Generate one lead-conversion case study in which a company receives "
            "many leads but has a low conversion rate. "
            "Ask the candidate to identify possible causes and propose a strategy "
            "to improve conversion. "
            "The question should test funnel analysis, customer journey understanding, "
            "experimentation, and marketing-sales alignment. "
            "Make the scenario practical and non-generic."
        ),
    },
    {
        "domain": "marketing-sales",
        "prompt_template": (
            "You are a senior marketing and sales interviewer. "
            "Generate one go-to-market case-study question for launching a new product "
            "in a competitive market. "
            "Ask the candidate to explain how they would identify the target market, "
            "position the product, choose acquisition channels, define pricing, "
            "and measure launch success. "
            "The scenario should require strategic reasoning and realistic trade-offs "
            "rather than a generic marketing plan."
        ),
    },
]
