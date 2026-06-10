"""
Title hierarchies, skill taxonomy, company classifications, and location tiers.
Derived from deep reading of the Redrob JD for Senior AI Engineer — Founding Team.
"""

# ============================================================================
# Title -> JD fit score
# Based on how well the current_title maps to "Senior AI Engineer" role
# ============================================================================
TITLE_SCORES = {
    # Perfect matches
    "Senior AI Engineer": 1.00,
    "Lead AI Engineer": 0.98,
    "AI Engineer": 0.96,
    "Staff Machine Learning Engineer": 0.95,
    "Senior Machine Learning Engineer": 0.95,
    # Strong ML/AI titles
    "Machine Learning Engineer": 0.92,
    "Senior Applied Scientist": 0.92,
    "Applied ML Engineer": 0.90,
    "ML Engineer": 0.90,
    "Senior NLP Engineer": 0.90,
    "NLP Engineer": 0.88,
    "Search Engineer": 0.88,
    "Recommendation Systems Engineer": 0.88,
    # Good AI-adjacent
    "AI Research Engineer": 0.85,
    "AI Specialist": 0.83,
    "Senior Data Scientist": 0.82,
    "Data Scientist": 0.78,
    "Computer Vision Engineer": 0.72,  # JD says CV-only is mild penalty
    # Tech but not ML-specific
    "Senior Software Engineer (ML)": 0.75,
    "Junior ML Engineer": 0.70,
    "Senior Software Engineer": 0.55,
    "Senior Data Engineer": 0.55,
    "Data Engineer": 0.48,
    "Analytics Engineer": 0.45,
    "Backend Engineer": 0.42,
    "Software Engineer": 0.40,
    "Full Stack Developer": 0.35,
    "Data Analyst": 0.35,
    # Adjacent tech
    "Cloud Engineer": 0.28,
    "DevOps Engineer": 0.25,
    "Java Developer": 0.22,
    ".NET Developer": 0.20,
    "Frontend Engineer": 0.15,
    "Mobile Developer": 0.12,
    "QA Engineer": 0.10,
    # Non-technical (should mostly be filtered at Stage 1)
    "Project Manager": 0.05,
    "Business Analyst": 0.05,
    "Marketing Manager": 0.03,
    "HR Manager": 0.02,
    "Accountant": 0.01,
    "Sales Executive": 0.01,
    "Customer Support": 0.01,
    "Content Writer": 0.01,
    "Graphic Designer": 0.01,
    "Civil Engineer": 0.01,
    "Mechanical Engineer": 0.01,
    "Operations Manager": 0.02,
}

# Titles that are clearly non-technical for coarse filtering
NON_TECHNICAL_TITLES = {
    "HR Manager", "Accountant", "Sales Executive", "Customer Support",
    "Content Writer", "Graphic Designer", "Civil Engineer",
    "Mechanical Engineer", "Operations Manager", "Marketing Manager",
}

# Titles that could pass if they have ML work in descriptions
MAYBE_TECHNICAL_TITLES = {
    "Project Manager", "Business Analyst",
}

# ============================================================================
# Skill Taxonomy — 3 tiers based on JD requirements
# ============================================================================

# Tier 1: Must-have skills from JD
TIER1_SKILLS = {
    # Embeddings & retrieval
    "Sentence Transformers", "Embeddings", "Vector Representations",
    "Semantic Search", "Information Retrieval", "BM25", "TF-IDF",
    # Vector databases
    "FAISS", "Pinecone", "Qdrant", "Milvus", "Weaviate", "Chroma",
    "pgvector", "OpenSearch", "Elasticsearch",
    # Core ML/DL
    "PyTorch", "TensorFlow", "Deep Learning", "Machine Learning",
    "Neural Networks",
    # Python
    "Python",
    # RAG / LLM integration
    "RAG", "Retrieval Augmented Generation", "LlamaIndex", "LangChain",
    "Large Language Models", "LLMs", "Transformers",
    # NLP
    "Natural Language Processing", "NLP", "Text Mining",
    "Named Entity Recognition", "Text Classification",
}

# Tier 2: Strong signal skills
TIER2_SKILLS = {
    # Fine-tuning
    "Fine-tuning", "LoRA", "QLoRA", "PEFT", "Model Fine-tuning",
    # Learning to rank
    "Learning to Rank", "XGBoost", "LightGBM", "Ranking Systems",
    "NDCG", "Ranking Algorithms",
    # MLOps
    "MLOps", "MLflow", "Kubeflow", "Model Deployment", "Model Serving",
    "TensorFlow Serving", "TorchServe", "Triton",
    # Search
    "Search Systems", "Hybrid Search", "Query Understanding",
    "Search Ranking",
    # Recommendation systems
    "Recommendation Systems", "Collaborative Filtering",
    "Content-based Filtering",
    # General ML tools
    "scikit-learn", "Hugging Face", "spaCy", "NLTK",
    "Pandas", "NumPy", "Jupyter",
}

# Tier 3: Nice-to-have
TIER3_SKILLS = {
    # Distributed systems
    "Kubernetes", "Docker", "Apache Spark", "Kafka",
    "Distributed Systems", "Microservices",
    # Data engineering
    "Apache Airflow", "dbt", "Snowflake", "BigQuery",
    "Data Pipelines", "ETL",
    # Cloud
    "AWS", "GCP", "Azure", "SageMaker",
    # Other ML
    "Computer Vision", "Reinforcement Learning", "Statistical Modeling",
    "Feature Engineering", "A/B Testing", "Causal Inference",
    # Programming
    "Go", "Rust", "Java", "Scala", "SQL", "Git",
}

# Normalized lookup: lowercase -> tier
SKILL_TIER_LOOKUP = {}
for skill in TIER1_SKILLS:
    SKILL_TIER_LOOKUP[skill.lower()] = 1
for skill in TIER2_SKILLS:
    SKILL_TIER_LOOKUP[skill.lower()] = 2
for skill in TIER3_SKILLS:
    SKILL_TIER_LOOKUP[skill.lower()] = 3

# Common abbreviations / alternate names -> canonical name (lowercase)
SKILL_ALIASES = {
    "ml": "machine learning",
    "dl": "deep learning",
    "ai": "machine learning",
    "artificial intelligence": "machine learning",
    "nlp": "natural language processing",
    "ir": "information retrieval",
    "llm": "large language models",
    "genai": "large language models",
    "gen ai": "large language models",
    "generative ai": "large language models",
    "bert": "transformers",
    "gpt": "large language models",
    "openai": "large language models",
    "claude": "large language models",
    "gemini": "large language models",
    "huggingface": "hugging face",
    "hf transformers": "hugging face",
    "sklearn": "scikit-learn",
    "sk-learn": "scikit-learn",
    "tf": "tensorflow",
    "keras": "tensorflow",
    "torch": "pytorch",
    "elastic search": "elasticsearch",
    "elastic": "elasticsearch",
    "open search": "opensearch",
    "vector db": "faiss",
    "vector database": "faiss",
    "vector search": "semantic search",
    "similarity search": "semantic search",
    "ann": "faiss",
    "approximate nearest neighbor": "faiss",
    "k8s": "kubernetes",
    "aws sagemaker": "sagemaker",
    "amazon sagemaker": "sagemaker",
    "rag pipeline": "rag",
    "retrieval augmented generation": "rag",
    "langchain": "langchain",
    "llamaindex": "llamaindex",
    "sentence-transformers": "sentence transformers",
    "sbert": "sentence transformers",
}

# ============================================================================
# Company classifications
# ============================================================================

CONSULTING_COMPANIES = {
    "tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini",
    "hcl", "hcl technologies", "tech mahindra", "mphasis", "mindtree",
    "deloitte", "ey", "ernst & young", "kpmg", "pwc",
    "pricewaterhousecoopers", "ltimindtree", "l&t infotech",
    "hexaware", "birlasoft", "cyient", "zensar", "persistent systems",
    "niit technologies", "coforge", "mastek",
}

PRODUCT_COMPANIES = {
    # Indian product companies
    "flipkart", "zomato", "razorpay", "cred", "swiggy", "meesho",
    "groww", "zerodha", "paytm", "phonepe", "ola", "myntra",
    "freshworks", "zoho", "sharechat", "dream11", "unacademy",
    "byju's", "byjus", "udaan", "lenskart", "nykaa", "dunzo",
    "jupiter", "slice", "smallcase", "cleartax", "browserstack",
    "postman", "hasura", "chargebee", "druva",
    # Global tech
    "google", "meta", "facebook", "amazon", "apple", "microsoft",
    "netflix", "linkedin", "twitter", "x", "uber", "airbnb",
    "spotify", "stripe", "databricks", "snowflake", "openai",
    "anthropic", "deepmind", "nvidia", "intel", "adobe", "salesforce",
    "oracle", "ibm", "samsung", "atlassian", "github", "gitlab",
    "confluent", "elastic", "mongodb", "redis labs", "pinecone",
    # Fictional companies in dataset that signal product work
    "pied piper", "hooli", "stark industries", "wayne enterprises",
    "initech", "globex", "acme corp", "dunder mifflin",
    # Indian AI-native companies observed in dataset
    "sarvam ai", "sarvam", "mad street den", "niramai", "haptik",
    "yellow.ai", "yellowai", "genpact ai", "krutrim", "ola krutrim",
    "vernacular.ai", "observe.ai", "uniphore", "arya.ai", "artivatic",
    "darwinbox", "leadsquared", "capillary technologies",
    "sigmoid", "fractal analytics", "mu sigma", "absolutdata",
    "latentview analytics", "bridgei2i", "tiger analytics",
    "thoughtworks",  # Product-oriented consulting
}

# ============================================================================
# Location tiers
# ============================================================================

LOCATION_TIER1_INDIA = {
    "pune", "noida",  # JD preferred
}

LOCATION_TIER2_INDIA = {
    "bangalore", "bengaluru", "mumbai", "delhi", "new delhi",
    "hyderabad", "secunderabad", "chennai", "kolkata", "gurgaon", "gurugram",
    "ghaziabad", "faridabad", "greater noida",
    # Strong tech presence cities in dataset
    "vizag", "visakhapatnam", "trivandrum", "thiruvananthapuram",
    "kochi", "cochin", "pune",  # Pune also here (already tier1 for exact match)
}

LOCATION_TIER3_INDIA = {
    "ahmedabad", "jaipur", "lucknow", "kochi", "cochin",
    "trivandrum", "thiruvananthapuram", "chandigarh", "indore",
    "bhopal", "nagpur", "coimbatore", "vadodara", "surat",
    "visakhapatnam", "bhubaneswar", "dehradun", "mysore", "mysuru",
    "mangalore", "mangaluru", "patna", "ranchi", "guwahati",
    "raipur", "agra", "varanasi", "kanpur", "allahabad", "prayagraj",
    "madurai", "tiruchirappalli", "trichy", "salem", "erode",
    "jodhpur", "udaipur", "kota",
}

# ============================================================================
# Education field relevance
# ============================================================================

EDUCATION_FIELDS_HIGH = {
    "computer science", "cs", "artificial intelligence", "ai",
    "machine learning", "data science", "information technology", "it",
    "mathematics", "statistics", "applied mathematics",
    "computational linguistics", "natural language processing",
}

EDUCATION_FIELDS_MEDIUM = {
    "electrical engineering", "electronics", "ece",
    "electronics and communication", "information systems",
    "software engineering", "computational science",
    "operations research", "physics", "applied physics",
}

EDUCATION_FIELDS_LOW = {
    "mechanical engineering", "civil engineering", "chemical engineering",
    "biotechnology", "commerce", "business administration", "mba",
    "arts", "humanities", "management",
}

# ============================================================================
# Career description keywords for trajectory analysis
# ============================================================================

# Production ML evidence (high signal)
PRODUCTION_ML_KEYWORDS = {
    "production", "deployed", "shipped", "serving", "inference",
    "model serving", "a/b test", "a/b testing", "latency",
    "throughput", "real-time", "realtime", "real time",
    "batch processing", "monitoring", "pipeline", "mlops",
    "model deployment", "model monitoring", "feature store",
    "training pipeline", "inference pipeline", "online serving",
    "offline evaluation", "online evaluation", "canary deployment",
    "blue-green", "shadow mode", "model registry",
    # Additional production signals
    "end-to-end", "end to end", "scaled", "scale",
    "millions of", "billion", "users", "requests per second",
    "qps", "p99", "p95", "percentile", "sla", "slo",
    "reliability", "uptime", "on-call", "oncall", "incident",
    "data drift", "concept drift", "retraining", "feedback loop",
    "recruiter engagement", "click-through", "conversion rate",
    "precision", "recall", "ndcg", "mrr", "map@",
}

# ML/AI domain keywords (medium signal)
ML_DOMAIN_KEYWORDS = {
    "machine learning", "deep learning", "neural network",
    "embeddings", "transformer", "bert", "gpt", "llm",
    "natural language processing", "nlp", "information retrieval",
    "search ranking", "recommendation", "retrieval",
    "vector search", "semantic search", "similarity",
    "classification", "regression", "clustering",
    "fine-tuning", "fine tuning", "training", "model",
    "algorithm", "feature engineering", "hyperparameter",
    "cross-validation", "loss function", "gradient",
    "backpropagation", "attention mechanism", "tokenization",
    "rag", "retrieval augmented", "prompt engineering",
    "embedding drift", "index refresh",
}

# Anti-pattern keywords (consulting/generic work)
CONSULTING_KEYWORDS = {
    "client project", "stakeholder management", "advisory",
    "consulting engagement", "requirement gathering",
    "business requirement", "client deliverable",
    "offshore", "onshore", "delivery manager",
}
