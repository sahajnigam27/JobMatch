from flask import Flask, render_template, request, session
from pypdf import PdfReader
from datetime import datetime
import sqlite3
import json
import re
import uuid
import os


# ============================================================
# APP CONFIG
# ============================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "JOBMATCH_SECRET_KEY",
    "jobmatch-development-secret-key"
)

DB_NAME = "jobmatch.db"


# ============================================================
# TEMPLATE FILTER
# ============================================================

@app.template_filter("from_json")
def from_json(value):
    try:
        return json.loads(value)
    except Exception:
        return []


# ============================================================
# TECHNICAL SKILL DATABASE
# ============================================================
#
# IMPORTANT:
#
# These are technical skills only.
#
# Professional capabilities are modeled separately from technical skills so they
# can be scored with lower weights and transparent evidence rather than treated as
# interchangeable technical keywords.
#
# ============================================================

SKILLS = {

    # --------------------------------------------------------
    # PROGRAMMING LANGUAGES
    # --------------------------------------------------------

    "Python": {
        "aliases": [
            "python",
            "python 3",
            "python3"
        ],
        "category": "Programming",
        "weight": 5
    },

    "Java": {
        "aliases": [
            "java"
        ],
        "category": "Programming",
        "weight": 5
    },

    "C++": {
        "aliases": [
            "c++",
            "cpp"
        ],
        "category": "Programming",
        "weight": 4
    },

    "C": {
        "aliases": [
            "c programming",
            "c language"
        ],
        "category": "Programming",
        "weight": 4
    },

    "C#": {
        "aliases": [
            "c#",
            "c sharp",
            "csharp"
        ],
        "category": "Programming",
        "weight": 4
    },

    "JavaScript": {
        "aliases": [
            "javascript",
            "java script"
        ],
        "category": "Programming",
        "weight": 3
    },

    "TypeScript": {
        "aliases": [
            "typescript"
        ],
        "category": "Programming",
        "weight": 3
    },

    "Go": {
        "aliases": [
            "golang",
            "go language"
        ],
        "category": "Programming",
        "weight": 4
    },

    "Rust": {
        "aliases": [
            "rust language"
        ],
        "category": "Programming",
        "weight": 4
    },

    "Kotlin": {
        "aliases": [
            "kotlin"
        ],
        "category": "Programming",
        "weight": 4
    },

    "Swift": {
        "aliases": [
            "swift"
        ],
        "category": "Programming",
        "weight": 3
    },

    "PHP": {
        "aliases": [
            "php"
        ],
        "category": "Programming",
        "weight": 3
    },

    "Ruby": {
        "aliases": [
            "ruby"
        ],
        "category": "Programming",
        "weight": 3
    },

    # --------------------------------------------------------
    # WEB
    # --------------------------------------------------------

    "HTML": {
        "aliases": [
            "html",
            "html5"
        ],
        "category": "Web",
        "weight": 1
    },

    "CSS": {
        "aliases": [
            "css",
            "css3"
        ],
        "category": "Web",
        "weight": 1
    },

    "React": {
        "aliases": [
            "react",
            "reactjs",
            "react.js"
        ],
        "category": "Web",
        "weight": 4
    },

    "Angular": {
        "aliases": [
            "angular",
            "angularjs"
        ],
        "category": "Web",
        "weight": 4
    },

    "Vue": {
        "aliases": [
            "vue",
            "vuejs",
            "vue.js"
        ],
        "category": "Web",
        "weight": 3
    },

    "Node.js": {
        "aliases": [
            "node.js",
            "nodejs",
            "node js"
        ],
        "category": "Backend",
        "weight": 4
    },

    "Express.js": {
        "aliases": [
            "express.js",
            "expressjs",
            "express"
        ],
        "category": "Backend",
        "weight": 4
    },

    "Flask": {
        "aliases": [
            "flask"
        ],
        "category": "Backend",
        "weight": 4
    },

    "Django": {
        "aliases": [
            "django"
        ],
        "category": "Backend",
        "weight": 4
    },

    "FastAPI": {
        "aliases": [
            "fastapi",
            "fast api"
        ],
        "category": "Backend",
        "weight": 4
    },

    "Spring Boot": {
        "aliases": [
            "spring boot",
            "springboot"
        ],
        "category": "Backend",
        "weight": 4
    },

    "ASP.NET": {
        "aliases": [
            "asp.net",
            "asp net",
            "aspnet"
        ],
        "category": "Backend",
        "weight": 4
    },

    "REST API": {
        "aliases": [
            "rest api",
            "rest apis",
            "restful api",
            "restful apis",
            "restful services",
            "rest services"
        ],
        "category": "Backend",
        "weight": 5
    },

    "GraphQL": {
        "aliases": [
            "graphql"
        ],
        "category": "Backend",
        "weight": 3
    },

    "Microservices": {
        "aliases": [
            "microservices",
            "microservice architecture",
            "microservice architecture"
        ],
        "category": "Architecture",
        "weight": 4
    },

    "Web Services": {
        "aliases": [
            "web services",
            "web service"
        ],
        "category": "Backend",
        "weight": 3
    },

    # --------------------------------------------------------
    # DATABASES
    # --------------------------------------------------------

    "SQL": {
        "aliases": [
            "sql",
            "sql queries",
            "structured query language"
        ],
        "category": "Database",
        "weight": 5
    },

    "MySQL": {
        "aliases": [
            "mysql"
        ],
        "category": "Database",
        "weight": 3
    },

    "PostgreSQL": {
        "aliases": [
            "postgresql",
            "postgres"
        ],
        "category": "Database",
        "weight": 3
    },

    "MongoDB": {
        "aliases": [
            "mongodb",
            "mongo db"
        ],
        "category": "Database",
        "weight": 3
    },

    "SQLite": {
        "aliases": [
            "sqlite"
        ],
        "category": "Database",
        "weight": 2
    },

    "Oracle": {
        "aliases": [
            "oracle database",
            "oracle db",
            "oracle sql"
        ],
        "category": "Database",
        "weight": 3
    },

    "PostgreSQL": {
        "aliases": [
            "postgresql",
            "postgres"
        ],
        "category": "Database",
        "weight": 3
    },

    "Redis": {
        "aliases": [
            "redis"
        ],
        "category": "Database",
        "weight": 3
    },

    "DynamoDB": {
        "aliases": [
            "dynamodb",
            "dynamo db"
        ],
        "category": "Database",
        "weight": 3
    },

    "Firebase": {
        "aliases": [
            "firebase"
        ],
        "category": "Database",
        "weight": 2
    },

    "Elasticsearch": {
        "aliases": [
            "elasticsearch"
        ],
        "category": "Database",
        "weight": 3
    },

    "ORM": {
        "aliases": [
            "orm",
            "object relational mapping",
            "object-relational mapping"
        ],
        "category": "Database",
        "weight": 2
    },

    # --------------------------------------------------------
    # DATA
    # --------------------------------------------------------

    "Pandas": {
        "aliases": [
            "pandas"
        ],
        "category": "Data",
        "weight": 3
    },

    "NumPy": {
        "aliases": [
            "numpy"
        ],
        "category": "Data",
        "weight": 2
    },

    "Scikit-learn": {
        "aliases": [
            "scikit-learn",
            "scikit learn",
            "sklearn"
        ],
        "category": "Machine Learning",
        "weight": 4
    },

    "Apache Spark": {
        "aliases": [
            "apache spark",
            "spark"
        ],
        "category": "Data Engineering",
        "weight": 4
    },

    "PySpark": {
        "aliases": [
            "pyspark"
        ],
        "category": "Data Engineering",
        "weight": 4
    },

    "Kafka": {
        "aliases": [
            "kafka",
            "apache kafka"
        ],
        "category": "Data Engineering",
        "weight": 4
    },

    "Airflow": {
        "aliases": [
            "airflow",
            "apache airflow"
        ],
        "category": "Data Engineering",
        "weight": 4
    },

    "Databricks": {
        "aliases": [
            "databricks"
        ],
        "category": "Data Engineering",
        "weight": 4
    },

    "ETL": {
        "aliases": [
            "etl",
            "extract transform load",
            "extract, transform, load"
        ],
        "category": "Data Engineering",
        "weight": 4
    },

    "Data Engineering": {
        "aliases": [
            "data engineering",
            "data engineer"
        ],
        "category": "Data Engineering",
        "weight": 5
    },

    "Data Warehousing": {
        "aliases": [
            "data warehousing",
            "data warehouse",
            "data warehouses"
        ],
        "category": "Data Engineering",
        "weight": 4
    },

    "Data Modeling": {
        "aliases": [
            "data modeling",
            "data modelling"
        ],
        "category": "Data Engineering",
        "weight": 4
    },

    "Data Pipelines": {
        "aliases": [
            "data pipelines",
            "data pipeline",
            "pipeline development"
        ],
        "category": "Data Engineering",
        "weight": 4
    },

    "BigQuery": {
        "aliases": [
            "bigquery",
            "big query"
        ],
        "category": "Data Engineering",
        "weight": 4
    },

    "Snowflake": {
        "aliases": [
            "snowflake"
        ],
        "category": "Data Engineering",
        "weight": 4
    },

    "Power BI": {
        "aliases": [
            "power bi",
            "powerbi"
        ],
        "category": "Data Analytics",
        "weight": 3
    },

    "Tableau": {
        "aliases": [
            "tableau"
        ],
        "category": "Data Analytics",
        "weight": 3
    },

    "Excel": {
        "aliases": [
            "microsoft excel",
            "ms excel"
        ],
        "category": "Data Analytics",
        "weight": 2
    },

    # --------------------------------------------------------
    # MACHINE LEARNING / AI
    # --------------------------------------------------------

    "Machine Learning": {
        "aliases": [
            "machine learning",
            "machine-learning"
        ],
        "category": "Machine Learning",
        "weight": 5
    },

    "Deep Learning": {
        "aliases": [
            "deep learning",
            "deep-learning"
        ],
        "category": "Machine Learning",
        "weight": 4
    },

    "NLP": {
        "aliases": [
            "natural language processing",
            "nlp"
        ],
        "category": "Machine Learning",
        "weight": 4
    },

    "Computer Vision": {
        "aliases": [
            "computer vision"
        ],
        "category": "Machine Learning",
        "weight": 4
    },

    "TensorFlow": {
        "aliases": [
            "tensorflow"
        ],
        "category": "Machine Learning",
        "weight": 4
    },

    "PyTorch": {
        "aliases": [
            "pytorch"
        ],
        "category": "Machine Learning",
        "weight": 4
    },

    "Keras": {
        "aliases": [
            "keras"
        ],
        "category": "Machine Learning",
        "weight": 3
    },

    "XGBoost": {
        "aliases": [
            "xgboost"
        ],
        "category": "Machine Learning",
        "weight": 3
    },

    "Generative AI": {
        "aliases": [
            "generative ai",
            "generative artificial intelligence",
            "gen ai",
            "genai"
        ],
        "category": "AI",
        "weight": 4
    },

    "LLM": {
        "aliases": [
            "llm",
            "large language model",
            "large language models"
        ],
        "category": "AI",
        "weight": 4
    },

    "Prompt Engineering": {
        "aliases": [
            "prompt engineering",
            "prompt design"
        ],
        "category": "AI",
        "weight": 2
    },

    "RAG": {
        "aliases": [
            "retrieval augmented generation",
            "retrieval-augmented generation"
        ],
        "category": "AI",
        "weight": 4
    },

    "LangChain": {
        "aliases": [
            "langchain"
        ],
        "category": "AI",
        "weight": 3
    },

    "Hugging Face": {
        "aliases": [
            "hugging face",
            "huggingface"
        ],
        "category": "AI",
        "weight": 3
    },

    "Transformers": {
        "aliases": [
            "transformers",
            "transformer models"
        ],
        "category": "AI",
        "weight": 3
    },

    # --------------------------------------------------------
    # CORE COMPUTER SCIENCE
    # --------------------------------------------------------

    "Data Structures": {
        "aliases": [
            "data structures",
            "data structure"
        ],
        "category": "Core CS",
        "weight": 4
    },

    "Algorithms": {
        "aliases": [
            "algorithms",
            "algorithm"
        ],
        "category": "Core CS",
        "weight": 4
    },

    "OOP": {
        "aliases": [
            "oop",
            "object oriented programming",
            "object-oriented programming"
        ],
        "category": "Core CS",
        "weight": 4
    },

    "DBMS": {
        "aliases": [
            "dbms",
            "database management system",
            "database management systems"
        ],
        "category": "Core CS",
        "weight": 3
    },

    "Operating Systems": {
        "aliases": [
            "operating systems",
            "operating system"
        ],
        "category": "Core CS",
        "weight": 3
    },

    "Computer Networks": {
        "aliases": [
            "computer networks",
            "computer networking",
            "networking concepts"
        ],
        "category": "Core CS",
        "weight": 3
    },

    "Software Engineering": {
        "aliases": [
            "software engineering"
        ],
        "category": "Core CS",
        "weight": 3
    },

    "SDLC": {
        "aliases": [
            "sdlc",
            "software development life cycle"
        ],
        "category": "Core CS",
        "weight": 3
    },

    "Debugging": {
        "aliases": [
            "debugging",
            "debug applications",
            "debug code"
        ],
        "category": "Core CS",
        "weight": 4
    },

    "Testing": {
        "aliases": [
            "software testing",
            "testing",
            "unit testing",
            "test cases"
        ],
        "category": "Testing",
        "weight": 3
    },

    "Unit Testing": {
        "aliases": [
            "unit testing",
            "unit tests"
        ],
        "category": "Testing",
        "weight": 3
    },

    "Integration Testing": {
        "aliases": [
            "integration testing",
            "integration tests"
        ],
        "category": "Testing",
        "weight": 3
    },

    "Code Review": {
        "aliases": [
            "code review",
            "code reviews",
            "reviewing code"
        ],
        "category": "Engineering",
        "weight": 3
    },

    "System Design": {
        "aliases": [
            "system design",
            "systems design"
        ],
        "category": "Architecture",
        "weight": 5
    },

    "Software Architecture": {
        "aliases": [
            "software architecture"
        ],
        "category": "Architecture",
        "weight": 5
    },

    "Design Patterns": {
        "aliases": [
            "design patterns",
            "design pattern"
        ],
        "category": "Architecture",
        "weight": 4
    },

    "Distributed Systems": {
        "aliases": [
            "distributed systems",
            "distributed system"
        ],
        "category": "Architecture",
        "weight": 5
    },

    "Scalability": {
        "aliases": [
            "scalability",
            "scalable systems",
            "scalable applications"
        ],
        "category": "Architecture",
        "weight": 4
    },

    # --------------------------------------------------------
    # CLOUD / DEVOPS
    # --------------------------------------------------------

    "AWS": {
        "aliases": [
            "aws",
            "amazon web services"
        ],
        "category": "Cloud",
        "weight": 5
    },

    "Azure": {
        "aliases": [
            "microsoft azure",
            "azure"
        ],
        "category": "Cloud",
        "weight": 5
    },

    "GCP": {
        "aliases": [
            "gcp",
            "google cloud",
            "google cloud platform"
        ],
        "category": "Cloud",
        "weight": 5
    },

    "Cloud Computing": {
        "aliases": [
            "cloud computing",
            "cloud technologies",
            "cloud platform",
            "cloud platforms"
        ],
        "category": "Cloud",
        "weight": 4
    },

    "Docker": {
        "aliases": [
            "docker",
            "containerization",
            "docker containers"
        ],
        "category": "DevOps",
        "weight": 4
    },

    "Kubernetes": {
        "aliases": [
            "kubernetes",
            "k8s"
        ],
        "category": "DevOps",
        "weight": 4
    },

    "Terraform": {
        "aliases": [
            "terraform"
        ],
        "category": "DevOps",
        "weight": 3
    },

    "Jenkins": {
        "aliases": [
            "jenkins"
        ],
        "category": "DevOps",
        "weight": 3
    },

    "CI/CD": {
        "aliases": [
            "ci/cd",
            "cicd",
            "continuous integration",
            "continuous delivery",
            "continuous deployment"
        ],
        "category": "DevOps",
        "weight": 3
    },

    "Linux": {
        "aliases": [
            "linux",
            "unix"
        ],
        "category": "Infrastructure",
        "weight": 3
    },

    "Networking": {
        "aliases": [
            "networking",
            "network infrastructure"
        ],
        "category": "Infrastructure",
        "weight": 3
    },

    "VPC": {
        "aliases": [
            "vpc",
            "virtual private cloud"
        ],
        "category": "Cloud",
        "weight": 3
    },

    "Ansible": {
        "aliases": [
            "ansible"
        ],
        "category": "DevOps",
        "weight": 3
    },

    # --------------------------------------------------------
    # DEVELOPMENT TOOLS
    # --------------------------------------------------------

    "Git": {
        "aliases": [
            "git",
            "version control"
        ],
        "category": "Tools",
        "weight": 2
    },

    "GitHub": {
        "aliases": [
            "github"
        ],
        "category": "Tools",
        "weight": 1
    },

    "GitLab": {
        "aliases": [
            "gitlab"
        ],
        "category": "Tools",
        "weight": 1
    },

    "pytest": {
        "aliases": [
            "pytest",
            "py test"
        ],
        "category": "Testing",
        "weight": 3
    },

    "Jira": {
        "aliases": [
            "jira"
        ],
        "category": "Tools",
        "weight": 1
    },

    "Postman": {
        "aliases": [
            "postman"
        ],
        "category": "Tools",
        "weight": 2
    }
}


# ============================================================
# RELATED SKILL GROUPS
# ============================================================
#
# Partial credit is allowed only for genuinely related
# technologies.
#
# Example:
#
# Flask -> Django / FastAPI
#
# should NOT equal:
#
# Flask -> Java
#
# ============================================================

RELATED_SKILLS = {

    "Python": {
        "Python"
    },

    "Flask": {
        "Flask",
        "Django",
        "FastAPI"
    },

    "Django": {
        "Django",
        "Flask",
        "FastAPI"
    },

    "FastAPI": {
        "FastAPI",
        "Flask",
        "Django"
    },

    "REST API": {
        "REST API",
        "GraphQL",
        "Web Services"
    },

    "SQL": {
        "SQL",
        "MySQL",
        "PostgreSQL",
        "Oracle"
    },

    "Database": {
        "SQL",
        "MySQL",
        "PostgreSQL",
        "MongoDB",
        "SQLite",
        "Oracle"
    },

    "Machine Learning": {
        "Machine Learning",
        "Scikit-learn",
        "XGBoost",
        "TensorFlow",
        "PyTorch"
    },

    "Deep Learning": {
        "Deep Learning",
        "TensorFlow",
        "PyTorch",
        "Keras"
    },

    "NLP": {
        "NLP",
        "Transformers",
        "BERT",
        "LLM"
    },

    "LLM": {
        "LLM",
        "Generative AI",
        "RAG",
        "LangChain",
        "Hugging Face"
    },

    "Cloud Computing": {
        "Cloud Computing",
        "AWS",
        "Azure",
        "GCP"
    },

    "AWS": {
        "AWS",
        "Cloud Computing"
    },

    "Azure": {
        "Azure",
        "Cloud Computing"
    },

    "GCP": {
        "GCP",
        "Cloud Computing"
    },

    "Docker": {
        "Docker",
        "Kubernetes"
    },

    "Data Engineering": {
        "Data Engineering",
        "ETL",
        "Data Pipelines",
        "Apache Spark",
        "PySpark",
        "Airflow",
        "Kafka"
    },

    "ETL": {
        "ETL",
        "Data Engineering",
        "Data Pipelines",
        "Airflow"
    },

    "Data Pipelines": {
        "Data Pipelines",
        "ETL",
        "Airflow",
        "Apache Spark",
        "PySpark"
    }
}


# ============================================================
# TEXT UTILITIES
# ============================================================

def normalize_text(text):
    if not text:
        return ""

    text = text.replace("\u2013", "-")
    text = text.replace("\u2014", "-")
    text = text.replace("\u2212", "-")
    text = text.replace("\u00a0", " ")

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()


def normalize_search(text):
    return normalize_text(text).lower()


def alias_pattern(alias):

    alias = alias.lower().strip()

    escaped = re.escape(alias)

    return (
        rf"(?<![a-zA-Z0-9])"
        rf"{escaped}"
        rf"(?![a-zA-Z0-9])"
    )


def contains_alias(text, aliases):

    text = normalize_search(text)

    for alias in aliases:

        if re.search(
            alias_pattern(alias),
            text
        ):
            return True

    return False


# ============================================================
# EXTRACT SKILLS FROM TEXT
# ============================================================

def extract_skills(text):

    found = []

    for skill, data in SKILLS.items():

        if contains_alias(
            text,
            data["aliases"]
        ):
            found.append(skill)

    return found


# ============================================================
# SECTION DETECTION
# ============================================================

def technical_context(text, position):

    start = max(
        0,
        position - 900
    )

    end = min(
        len(text),
        position + 900
    )

    return text[start:end].lower()


def importance_from_context(context):

    core_words = [
        "required",
        "must have",
        "must-have",
        "mandatory",
        "essential",
        "technical skills",
        "required skills",
        "core skills",
        "key skills",
        "qualifications",
        "experience with",
        "proficiency in",
        "strong knowledge",
        "hands-on experience",
        "hands on experience",
        "should have"
    ]

    preferred_words = [
        "preferred",
        "nice to have",
        "nice-to-have",
        "bonus",
        "plus",
        "good to have",
        "desirable",
        "preferred qualification"
    ]

    if any(
        word in context
        for word in core_words
    ):
        return "Core"

    if any(
        word in context
        for word in preferred_words
    ):
        return "Supporting"

    return "Supporting"


# ============================================================
# EXTRACT JD REQUIREMENTS
# ============================================================

def extract_requirements(job_description):

    text = normalize_text(
        job_description
    )

    if not text:
        return []

    lower = text.lower()

    requirements = {}

    for skill, data in SKILLS.items():

        positions = []

        for alias in data["aliases"]:

            match = re.search(
                alias_pattern(alias),
                lower
            )

            if match:
                positions.append(
                    match.start()
                )

        if not positions:
            continue

        position = min(
            positions
        )

        context = technical_context(
            lower,
            position
        )

        tier = importance_from_context(
            context
        )

        # Technologies that are normally core technical
        # requirements for engineering jobs.
        if skill in {
            "Python",
            "Java",
            "C++",
            "C",
            "C#",
            "JavaScript",
            "TypeScript",
            "SQL",
            "REST API",
            "Backend Development",
            "Software Development",
            "Data Engineering",
            "ETL",
            "Data Pipelines",
            "Machine Learning",
            "Deep Learning",
            "NLP",
            "Data Structures",
            "Algorithms",
            "OOP",
            "DBMS",
            "Operating Systems",
            "Computer Networks",
            "Debugging",
            "Testing",
            "System Design",
            "Software Architecture",
            "AWS",
            "Azure",
            "GCP",
            "Docker",
            "Kubernetes"
        }:
            tier = "Core"

        requirements[skill] = {
            "skill": skill,
            "category": data["category"],
            "tier": tier,
            "weight": data["weight"],
            "position": position
        }

    # --------------------------------------------------------
    # Additional technical phrases
    # --------------------------------------------------------

    phrase_map = {

        "API Development": [
            r"\bapi development\b"
        ],

        "System Architecture": [
            r"\bsystem architecture\b"
        ],

        "Distributed Systems": [
            r"\bdistributed systems?\b"
        ],

        "Cloud Native": [
            r"\bcloud[- ]native\b"
        ],

        "Performance Optimization": [
            r"\bperformance optimization\b",
            r"\bperformance tuning\b"
        ],

        "Containerization": [
            r"\bcontainerization\b",
            r"\bcontainerized applications?\b"
        ],

        "Automated Testing": [
            r"\bautomated testing\b"
        ],

        "Production Systems": [
            r"\bproduction systems?\b"
        ]
    }

    for skill, patterns in phrase_map.items():

        position = None

        for pattern in patterns:

            match = re.search(
                pattern,
                lower
            )

            if match:
                position = match.start()
                break

        if position is None:
            continue

        if skill in requirements:
            continue

        context = technical_context(
            lower,
            position
        )

        requirements[skill] = {
            "skill": skill,
            "category": "Technical Concept",
            "tier": importance_from_context(
                context
            ),
            "weight": 3,
            "position": position
        }

    result = list(
        requirements.values()
    )

    # Core first, then supporting.
    result.sort(
        key=lambda x: (
            0 if x["tier"] == "Core" else 1,
            -x["weight"],
            x["position"]
        )
    )

    # Supporting requirements count less.
    for item in result:

        if item["tier"] == "Core":
            item["effective_weight"] = float(
                item["weight"]
            )

        else:
            item["effective_weight"] = round(
                item["weight"] * 0.45,
                2
            )

    return result


# ============================================================
# RESUME PROJECT EXTRACTION
# ============================================================

def split_resume_sections(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    sections = {
        "projects": "",
        "experience": "",
        "skills": "",
        "education": "",
        "other": ""
    }

    current = "other"

    for line in lines:

        lower = line.lower()

        if re.match(
            r"^(projects?|personal projects?|academic projects?)$",
            lower
        ):
            current = "projects"
            continue

        if re.match(
            r"^(experience|work experience|internship|internships|professional experience)$",
            lower
        ):
            current = "experience"
            continue

        if re.match(
            r"^(technical skills|skills|core skills)$",
            lower
        ):
            current = "skills"
            continue

        if re.match(
            r"^(education|academic background)$",
            lower
        ):
            current = "education"
            continue

        sections[current] += line + "\n"

    return sections


# ============================================================
# FIND SKILLS IN PROJECTS
# ============================================================

def project_skill_evidence(
    resume_text,
    skill
):

    sections = split_resume_sections(
        resume_text
    )

    project_text = sections["projects"]

    if not project_text.strip():
        return False

    data = SKILLS.get(skill)

    if not data:
        return False

    return contains_alias(
        project_text,
        data["aliases"]
    )


# ============================================================
# FIND SKILLS IN EXPERIENCE
# ============================================================

def experience_skill_evidence(
    resume_text,
    skill
):

    sections = split_resume_sections(
        resume_text
    )

    experience_text = sections["experience"]

    if not experience_text.strip():
        return False

    data = SKILLS.get(skill)

    if not data:
        return False

    return contains_alias(
        experience_text,
        data["aliases"]
    )


# ============================================================
# RESUME EVIDENCE ENGINE
# ============================================================
#
# Evidence hierarchy:
#
# Project + skill       = 1.00
# Experience + skill    = 1.00
# Skills section        = 0.80
# General resume text   = 0.65
# Related technology    = 0.40
# No evidence           = 0
#
# This prevents simply writing a skill in a resume from
# being treated the same as actually demonstrating it.
# ============================================================

def resume_evidence(
    requirement,
    resume_text
):

    skill = requirement["skill"]

    normalized_resume = normalize_search(
        resume_text
    )

    resume_skills = extract_skills(
        resume_text
    )

    # --------------------------------------------------------
    # Direct skill detection
    # --------------------------------------------------------

    direct = skill in resume_skills

    project_match = project_skill_evidence(
        resume_text,
        skill
    )

    experience_match = experience_skill_evidence(
        resume_text,
        skill
    )

    sections = split_resume_sections(
        resume_text
    )

    skills_section_match = False

    if sections["skills"]:

        data = SKILLS.get(skill)

        if data:

            skills_section_match = contains_alias(
                sections["skills"],
                data["aliases"]
            )

    # --------------------------------------------------------
    # Strong evidence
    # --------------------------------------------------------

    if project_match:

        return {
            "score": 1.0,
            "level": "Strong",
            "evidence": (
                f"{skill} is demonstrated in a project."
            )
        }

    if experience_match:

        return {
            "score": 1.0,
            "level": "Strong",
            "evidence": (
                f"{skill} is demonstrated in technical experience."
            )
        }

    # --------------------------------------------------------
    # Skills section only
    # --------------------------------------------------------

    if skills_section_match:

        return {
            "score": 0.80,
            "level": "Demonstrated",
            "evidence": (
                f"{skill} is listed as a technical skill."
            )
        }

    # --------------------------------------------------------
    # General resume evidence
    # --------------------------------------------------------

    if direct:

        return {
            "score": 0.65,
            "level": "Mentioned",
            "evidence": (
                f"{skill} appears in the resume."
            )
        }

    # --------------------------------------------------------
    # Related technology
    # --------------------------------------------------------

    related = RELATED_SKILLS.get(
        skill,
        set()
    )

    for resume_skill in resume_skills:

        if resume_skill in related:

            return {
                "score": 0.40,
                "level": "Related",
                "evidence": (
                    f"{resume_skill} provides related "
                    f"technical evidence for {skill}."
                )
            }

    # --------------------------------------------------------
    # No evidence
    # --------------------------------------------------------

    return {
        "score": 0.0,
        "level": "Missing",
        "evidence": ""
    }


# ============================================================
# SCORE REQUIREMENTS
# ============================================================

def score_requirements(
    resume_text,
    requirements
):

    matched = []
    partial = []
    missing = []

    resume_skills = extract_skills(
        resume_text
    )

    total_weight = 0.0
    achieved_weight = 0.0

    core_total = 0.0
    core_achieved = 0.0

    supporting_total = 0.0
    supporting_achieved = 0.0

    for requirement in requirements:

        evidence = resume_evidence(
            requirement,
            resume_text
        )

        score = evidence["score"]

        weight = requirement[
            "effective_weight"
        ]

        contribution = (
            weight * score
        )

        total_weight += weight
        achieved_weight += contribution

        item = {
            **requirement,
            "match_score": score,
            "match_level": evidence["level"],
            "evidence": evidence["evidence"]
        }

        if requirement["tier"] == "Core":

            core_total += weight
            core_achieved += contribution

        else:

            supporting_total += weight
            supporting_achieved += contribution

        if score >= 0.80:

            matched.append(item)

        elif score > 0:

            partial.append(item)

        else:

            missing.append(item)

    # --------------------------------------------------------
    # Scores
    # --------------------------------------------------------

    core_score = (
        core_achieved / core_total * 100
        if core_total
        else 0
    )

    supporting_score = (
        supporting_achieved /
        supporting_total *
        100
        if supporting_total
        else 0
    )

    # Technical core dominates.
    if core_total and supporting_total:

        final_score = (
            core_score * 0.85
            +
            supporting_score * 0.15
        )

    elif core_total:

        final_score = core_score

    else:

        final_score = supporting_score

    coverage = (
        (
            len(matched)
            +
            len(partial) * 0.5
        )
        /
        len(requirements)
        * 100
        if requirements
        else 0
    )

    return {
        "resume_skills": resume_skills,

        "matched": matched,

        "partial": partial,

        "missing": missing,

        "match_percentage": round(
            final_score,
            2
        ),

        "skill_coverage": round(
            coverage,
            2
        ),

        "matched_weight": round(
            achieved_weight,
            2
        ),

        "total_weight": round(
            total_weight,
            2
        ),

        "core_score": round(
            core_score,
            2
        ),

        "supporting_score": round(
            supporting_score,
            2
        )
    }


# ============================================================
# PROJECT ALIGNMENT
# ============================================================

def calculate_project_alignment(
    resume_text,
    requirements
):

    sections = split_resume_sections(
        resume_text
    )

    project_text = sections[
        "projects"
    ]

    if not project_text.strip():
        return []

    output = []

    for requirement in requirements:

        skill = requirement["skill"]

        if project_skill_evidence(
            resume_text,
            skill
        ):

            output.append({
                "skill": skill,
                "category": requirement["category"],
                "evidence": (
                    f"Project work demonstrates {skill}."
                )
            })

    return output


# ============================================================
# SKILLS ALREADY LEARNED
# ============================================================

def learned_skills(
    resume_text,
    requirements
):

    learned = []

    for requirement in requirements:

        evidence = resume_evidence(
            requirement,
            resume_text
        )

        if evidence["score"] >= 0.65:

            learned.append({
                "skill": requirement["skill"],
                "category": requirement["category"],
                "level": evidence["level"],
                "evidence": evidence["evidence"]
            })

    return learned


# ============================================================
# SKILLS TO LEARN
# ============================================================

def skills_to_learn(
    missing,
    partial
):

    output = []

    # Missing core skills first.
    for item in missing:

        if item["tier"] == "Core":

            output.append({
                "skill": item["skill"],
                "category": item["category"],
                "priority": "High",
                "reason": (
                    "Core technical requirement "
                    "not demonstrated in the resume."
                )
            })

    # Partial core skills.
    for item in partial:

        if item["tier"] == "Core":

            output.append({
                "skill": item["skill"],
                "category": item["category"],
                "priority": "High",
                "reason": (
                    "Related evidence exists, but the "
                    "required technology is not strongly demonstrated."
                )
            })

    # Supporting missing skills.
    for item in missing:

        if item["tier"] == "Supporting":

            output.append({
                "skill": item["skill"],
                "category": item["category"],
                "priority": "Medium",
                "reason": (
                    "Useful supporting technical requirement "
                    "that is not currently demonstrated."
                )
            })

    return output


# ============================================================
# RECOMMENDATIONS
# ============================================================

def build_recommendations(
    missing,
    partial
):

    recommendations = []

    for item in missing:

        if item["tier"] == "Core":

            recommendations.append({
                "skill": item["skill"],
                "priority": "High",
                "category": item["category"],
                "reason": (
                    "This is a core technical requirement "
                    "and no supporting evidence was found."
                )
            })

    for item in partial:

        if item["tier"] == "Core":

            recommendations.append({
                "skill": item["skill"],
                "priority": "High",
                "category": item["category"],
                "reason": (
                    "You have related technical evidence, "
                    "but stronger hands-on evidence is needed."
                )
            })

    for item in missing:

        if item["tier"] == "Supporting":

            recommendations.append({
                "skill": item["skill"],
                "priority": "Medium",
                "category": item["category"],
                "reason": (
                    "This would improve technical compatibility "
                    "but is less important than core requirements."
                )
            })

    return recommendations


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze_resume(
    resume_text,
    job_description
):

    if not resume_text.strip():

        return None, (
            "Resume text could not be extracted."
        )

    if not job_description.strip():

        return None, (
            "Job description text could not be extracted."
        )

    requirements = extract_requirements(
        job_description
    )

    if not requirements:

        return None, (
            "No technical requirements could be "
            "identified in this job description."
        )

    scoring = score_requirements(
        resume_text,
        requirements
    )

    matched = scoring[
        "matched"
    ]

    partial = scoring[
        "partial"
    ]

    missing = scoring[
        "missing"
    ]

    learned = learned_skills(
        resume_text,
        requirements
    )

    learn = skills_to_learn(
        missing,
        partial
    )

    recommendations = build_recommendations(
        missing,
        partial
    )

    projects = calculate_project_alignment(
        resume_text,
        requirements
    )

    # --------------------------------------------------------
    # Result object
    # --------------------------------------------------------

    result = {

        "resume_skills":
            scoring["resume_skills"],

        "job_skills":
            [
                item["skill"]
                for item in requirements
            ],

        "matched_skills":
            [
                item["skill"]
                for item in matched
            ],

        "partial_skills":
            [
                item["skill"]
                for item in partial
            ],

        "missing_skills":
            [
                item["skill"]
                for item in missing
            ],

        "match_percentage":
            scoring["match_percentage"],

        "skill_coverage":
            scoring["skill_coverage"],

        "matched_weight":
            scoring["matched_weight"],

        "total_weight":
            scoring["total_weight"],

        "core_score":
            scoring["core_score"],

        "supporting_score":
            scoring["supporting_score"],

        "recommendations":
            recommendations,

        "skills_to_learn":
            learn,

        "learned_skills":
            learned,

        "project_alignment":
            projects,

        "skill_weights":
            {
                item["skill"]:
                    item["weight"]
                for item in requirements
            },

        "requirement_details":
            requirements,

        "matched_details":
            matched,

        "partial_details":
            partial,

        "missing_details":
            missing
    }

    return result, None


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_pdf_text(
    pdf_file
):

    reader = PdfReader(
        pdf_file
    )

    pages = []

    for page in reader.pages:

        try:
            text = page.extract_text()

        except Exception:
            text = ""

        if text:
            pages.append(text)

    return "\n".join(
        pages
    ).strip()


# ============================================================
# JOB ROLE DETECTION
# ============================================================

def clean_line(line):

    line = line.replace(
        "\u2013",
        "-"
    )

    line = line.replace(
        "\u2014",
        "-"
    )

    return re.sub(
        r"\s+",
        " ",
        line
    ).strip()


def detect_job_roles(text):

    lines = [
        clean_line(line)
        for line in text.splitlines()
        if clean_line(line)
    ]

    patterns = [

        r"^(intern|junior|senior|associate|trainee|graduate)\s+.+",

        r"^software\s+(engineer|developer)",

        r"^application\s+(engineer|developer)",

        r"^data\s+(engineer|developer|analyst|scientist)",

        r"^machine\s+learning\s+(engineer|scientist)",

        r"^platform\s+engineer",

        r"^backend\s+(engineer|developer)",

        r"^frontend\s+(engineer|developer)",

        r"^full[- ]stack\s+(engineer|developer)",

        r"^devops\s+engineer",

        r"^cloud\s+engineer",

        r"^business\s+analyst",

        r"^system\s+engineer",

        r"^qa\s+engineer",

        r"^test\s+engineer"
    ]

    headings = []

    for index, line in enumerate(lines):

        if len(line) > 150:
            continue

        lower = line.lower()

        for pattern in patterns:

            if re.match(
                pattern,
                lower
            ):

                headings.append(
                    (
                        index,
                        line
                    )
                )

                break

    # Remove duplicates.
    unique = []

    seen = set()

    for index, title in headings:

        key = title.lower()

        if key not in seen:

            seen.add(key)

            unique.append(
                (
                    index,
                    title
                )
            )

    # Only treat as multi-role if there are at
    # least two genuine headings.
    if len(unique) < 2:
        return []

    roles = []

    for i, (start, title) in enumerate(unique):

        if i + 1 < len(unique):

            end = unique[
                i + 1
            ][0]

        else:

            end = len(lines)

        role_text = "\n".join(
            lines[start:end]
        )

        roles.append({
            "title": title,
            "text": role_text
        })

    return roles


# ============================================================
# FILE INPUT
# ============================================================

def read_resume():

    resume_file = request.files.get(
        "resume_file"
    )

    resume_text = request.form.get(
        "resume",
        ""
    ).strip()

    if (
        resume_file
        and resume_file.filename
    ):

        if not resume_file.filename.lower().endswith(
            ".pdf"
        ):

            return None, (
                "Resume file must be a PDF."
            )

        try:

            resume_text = extract_pdf_text(
                resume_file
            )

        except Exception as exc:

            return None, (
                f"Could not read resume PDF: {exc}"
            )

    return resume_text, None


def read_job_description():

    job_file = request.files.get(
        "job_file"
    )

    job_text = request.form.get(
        "job_description",
        ""
    ).strip()

    if (
        job_file
        and job_file.filename
    ):

        if not job_file.filename.lower().endswith(
            ".pdf"
        ):

            return None, (
                "Job description file must be a PDF."
            )

        try:

            job_text = extract_pdf_text(
                job_file
            )

        except Exception as exc:

            return None, (
                f"Could not read job description PDF: {exc}"
            )

    return job_text, None


# ============================================================
# DATABASE
# ============================================================

def get_db():

    connection = sqlite3.connect(
        DB_NAME
    )

    connection.row_factory = (
        sqlite3.Row
    )

    return connection


def init_db():

    connection = get_db()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            resume_skills TEXT,

            job_skills TEXT,

            matched_skills TEXT,

            missing_skills TEXT,

            match_percentage REAL,

            skill_coverage REAL,

            matched_weight REAL,

            total_weight REAL,

            created_at TEXT,

            requirement_details TEXT,

            core_score REAL,

            supporting_score REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS active_analyses (

            id TEXT PRIMARY KEY,

            resume_text TEXT NOT NULL,

            job_description TEXT NOT NULL,

            roles_json TEXT NOT NULL,

            created_at TEXT NOT NULL
        )
    """)

    connection.commit()

    connection.close()


# ============================================================
# SAVE ANALYSIS
# ============================================================

def save_analysis(result):

    connection = get_db()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO analyses (

            resume_skills,
            job_skills,
            matched_skills,
            missing_skills,
            match_percentage,
            skill_coverage,
            matched_weight,
            total_weight,
            created_at,
            requirement_details,
            core_score,
            supporting_score

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        json.dumps(
            result["resume_skills"]
        ),

        json.dumps(
            result["job_skills"]
        ),

        json.dumps(
            result["matched_skills"]
        ),

        json.dumps(
            result["missing_skills"]
        ),

        result[
            "match_percentage"
        ],

        result[
            "skill_coverage"
        ],

        result[
            "matched_weight"
        ],

        result[
            "total_weight"
        ],

        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        json.dumps(
            result[
                "requirement_details"
            ]
        ),

        result[
            "core_score"
        ],

        result[
            "supporting_score"
        ]
    ))

    analysis_id = (
        cursor.lastrowid
    )

    connection.commit()

    connection.close()

    return analysis_id


# ============================================================
# ACTIVE MULTI-ROLE ANALYSIS
# ============================================================

def save_active_analysis(
    resume_text,
    job_description,
    roles
):

    analysis_id = str(
        uuid.uuid4()
    )

    connection = get_db()

    connection.execute("""
        INSERT INTO active_analyses (

            id,
            resume_text,
            job_description,
            roles_json,
            created_at

        )

        VALUES (?, ?, ?, ?, ?)
    """, (

        analysis_id,

        resume_text,

        job_description,

        json.dumps(
            roles
        ),

        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    connection.commit()

    connection.close()

    return analysis_id


def get_active_analysis(
    analysis_id
):

    if not analysis_id:
        return None

    connection = get_db()

    row = connection.execute(
        """
        SELECT *
        FROM active_analyses
        WHERE id = ?
        """,
        (
            analysis_id,
        )
    ).fetchone()

    connection.close()

    if not row:
        return None

    return {

        "resume_text":
            row["resume_text"],

        "job_description":
            row["job_description"],

        "roles":
            json.loads(
                row["roles_json"]
            )
    }


def delete_active_analysis(
    analysis_id
):

    if not analysis_id:
        return

    connection = get_db()

    connection.execute(
        """
        DELETE FROM active_analyses
        WHERE id = ?
        """,
        (
            analysis_id,
        )
    )

    connection.commit()

    connection.close()


# ============================================================
# RENDER HOME
# ============================================================

def render_home(
    result=None,
    error=None,
    roles=None,
    selected_role=None
):

    return render_template(
        "index.html",

        result=result,

        error=error,

        roles=roles or [],

        selected_role=selected_role
    )


# ============================================================
# MAIN ROUTE
# ============================================================

@app.route(
    "/",
    methods=[
        "GET",
        "POST"
    ]
)
def index():

    selected_role = request.form.get(
        "selected_role"
    )

    # --------------------------------------------------------
    # SELECTED ROLE
    # --------------------------------------------------------

    if (
        request.method == "POST"
        and selected_role
    ):

        active = get_active_analysis(
            session.get(
                "analysis_id"
            )
        )

        if not active:

            session.pop(
                "analysis_id",
                None
            )

            return render_home(
                error=(
                    "Your analysis session expired. "
                    "Please upload the resume and JD again."
                )
            )

        selected_job = None

        for role in active["roles"]:

            if (
                role["title"]
                == selected_role
            ):

                selected_job = (
                    role["text"]
                )

                break

        if not selected_job:

            return render_home(
                error=(
                    "The selected job role "
                    "could not be found."
                ),

                roles=active["roles"],

                selected_role=selected_role
            )

        result, error = analyze_resume(
            active["resume_text"],
            selected_job
        )

        if error:

            return render_home(
                error=error,
                roles=active["roles"],
                selected_role=selected_role
            )

        save_analysis(
            result
        )

        delete_active_analysis(
            session.get(
                "analysis_id"
            )
        )

        session.pop(
            "analysis_id",
            None
        )

        return render_home(
            result=result,
            roles=active["roles"],
            selected_role=selected_role
        )

    # --------------------------------------------------------
    # NEW ANALYSIS
    # --------------------------------------------------------

    if request.method == "POST":

        resume_text, error = (
            read_resume()
        )

        if error:

            return render_home(
                error=error
            )

        job_description, error = (
            read_job_description()
        )

        if error:

            return render_home(
                error=error
            )

        if not resume_text:

            return render_home(
                error=(
                    "Please upload your resume "
                    "PDF or paste your resume."
                )
            )

        if not job_description:

            return render_home(
                error=(
                    "Please upload the job "
                    "description PDF or paste it."
                )
            )

        # ----------------------------------------------------
        # Detect multiple roles.
        # ----------------------------------------------------

        roles = detect_job_roles(
            job_description
        )

        if len(roles) > 1:

            analysis_id = save_active_analysis(
                resume_text,
                job_description,
                roles
            )

            session[
                "analysis_id"
            ] = analysis_id

            return render_home(
                roles=roles
            )

        # ----------------------------------------------------
        # Single role.
        # ----------------------------------------------------

        result, error = analyze_resume(
            resume_text,
            job_description
        )

        if error:

            return render_home(
                error=error
            )

        save_analysis(
            result
        )

        return render_home(
            result=result
        )

    return render_home()


# ============================================================
# HISTORY
# ============================================================

@app.route(
    "/history"
)
def history():

    connection = get_db()

    analyses = connection.execute(
        """
        SELECT *
        FROM analyses
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "history.html",
        analyses=analyses
    )


# ============================================================
# HISTORY DETAILS
# ============================================================

@app.route(
    "/history/<int:analysis_id>"
)
def history_detail(
    analysis_id
):

    connection = get_db()

    row = connection.execute(
        """
        SELECT *
        FROM analyses
        WHERE id = ?
        """,
        (
            analysis_id,
        )
    ).fetchone()

    connection.close()

    if not row:

        return render_template(
            "details.html",
            result=None,
            error="Analysis not found."
        ), 404

    try:

        requirement_details = (
            json.loads(
                row["requirement_details"]
            )
            if row["requirement_details"]
            else []
        )

    except Exception:

        requirement_details = []

    result = {

        "id":
            row["id"],

        "resume_skills":
            json.loads(
                row["resume_skills"]
            ),

        "job_skills":
            json.loads(
                row["job_skills"]
            ),

        "matched_skills":
            json.loads(
                row["matched_skills"]
            ),

        "missing_skills":
            json.loads(
                row["missing_skills"]
            ),

        "match_percentage":
            row["match_percentage"],

        "skill_coverage":
            row["skill_coverage"],

        "matched_weight":
            row["matched_weight"],

        "total_weight":
            row["total_weight"],

        "created_at":
            row["created_at"],

        "core_score":
            row["core_score"],

        "supporting_score":
            row["supporting_score"],

        "requirement_details":
            requirement_details,

        "skill_weights":
            {
                item["skill"]:
                    item["weight"]
                for item in requirement_details
            },

        "recommendations":
            build_recommendations(
                [
                    item
                    for item in requirement_details
                    if item.get(
                        "match_score",
                        0
                    ) == 0
                ],
                [
                    item
                    for item in requirement_details
                    if (
                        0
                        <
                        item.get(
                            "match_score",
                            0
                        )
                        <
                        0.80
                    )
                ]
            ),

        "matched_details":
            [
                item
                for item in requirement_details
                if item.get(
                    "match_score",
                    0
                ) >= 0.80
            ],

        "partial_details":
            [
                item
                for item in requirement_details
                if (
                    0
                    <
                    item.get(
                        "match_score",
                        0
                    )
                    <
                    0.80
                )
            ],

        "missing_details":
            [
                item
                for item in requirement_details
                if item.get(
                    "match_score",
                    0
                ) == 0
            ]
    }

    return render_template(
        "details.html",
        result=result,
        error=None
    )


# ============================================================
# FINAL EVIDENCE-BASED JOB FIT ENGINE
# ============================================================
# 1. Structured JD requirement extraction
# 2. Section-aware resume evidence
# 3. Explicit skill relationships
# 4. Deterministic semantic/context matching
# 5. Weighted fit scoring by dimension
# 6. Evidence-based gap analysis
# 7. Actionable recommendations
# 8. Potential fit + confidence
# 9. UI-compatible result fields
# 10. Robust role/database compatibility
# ============================================================

from difflib import SequenceMatcher


PREFERRED_MARKERS = [
    "preferred", "preferably", "nice to have", "nice-to-have",
    "good to have", "good-to-have", "plus", "bonus", "desirable",
    "advantage", "would be a plus", "added advantage", "optional",
]

CORE_MARKERS = [
    "required", "must", "mandatory", "essential", "should have",
    "strong knowledge", "strong understanding", "proficiency",
    "proficient", "experience with", "hands-on", "hands on",
    "knowledge of", "understanding of", "ability to", "responsible for",
    "possess", "demonstrate", "should demonstrate", "should possess",
]

VIRTUAL_SKILLS = {
    "Backend Development": {"category": "Backend", "weight": 4, "aliases": ["backend development", "backend engineering", "server side development"]},
    "Software Development": {"category": "Software Engineering", "weight": 4, "aliases": ["software development", "software engineering"]},
    "Problem Solving": {"category": "Core CS", "weight": 4, "aliases": ["problem solving", "problem-solving", "problem solving skills"]},
    "Cloud Native": {"category": "Cloud", "weight": 4, "aliases": ["cloud native", "cloud-native"]},
    "API Development": {"category": "Backend", "weight": 4, "aliases": ["api development", "api design"]},
    "Production Systems": {"category": "Software Engineering", "weight": 3, "aliases": ["production systems", "production system", "production environments"]},
    "Performance Optimization": {"category": "Software Engineering", "weight": 3, "aliases": ["performance optimization", "performance tuning", "performance improvement"]},
    "Data Quality": {"category": "Data Engineering", "weight": 3, "aliases": ["data quality"]},
    "Agentic Thinking": {"category": "AI/ML", "weight": 3, "aliases": ["agentic thinking", "agentic ai", "ai agents"]},
    "Programming": {"category": "Programming", "weight": 4, "aliases": ["programming", "programming skills", "strong programming skills"]},
    "Code Review": {"category": "Software Engineering", "weight": 3, "aliases": ["code review", "code reviews", "review code", "review complex code"]},
    "Deployment": {"category": "Software Engineering", "weight": 3, "aliases": ["deployment", "deploy", "deploying"]},
    "Configuration Management": {"category": "Software Engineering", "weight": 3, "aliases": ["configuration management"]},
    "System Architecture": {"category": "Software Engineering", "weight": 3, "aliases": ["system architecture", "software architecture", "architecture background"]},
    "System Design": {"category": "Software Engineering", "weight": 3, "aliases": ["system design", "software design", "architecture and design"]},
    "Initiative": {"category": "Professional", "weight": 2, "aliases": ["initiative", "take initiative"]},
    "Independent Work": {"category": "Professional", "weight": 2, "aliases": ["work independently", "independently"]},
    "Leadership": {"category": "Professional", "weight": 2, "aliases": ["leadership", "leadership capability", "leadership skills"]},
    "Ownership": {"category": "Professional", "weight": 2, "aliases": ["ownership", "accountability"]},
    "Business Acumen": {"category": "Professional", "weight": 2, "aliases": ["business sense", "business acumen"]},
    "Interpersonal Skills": {"category": "Professional", "weight": 2, "aliases": ["interpersonal skills", "interpersonal"]},
    "Emerging Technologies": {"category": "Technology", "weight": 2, "aliases": ["emerging technologies", "new and emerging technologies"]},
}

CONCEPT_PATTERNS = {
    "SDLC": [r"\bsdlc\b", r"software development life cycle", r"software development lifecycle"],
    "Testing": [r"\btesting\b", r"unit testing", r"integration testing", r"software testing", r"quality assurance", r"\bqa\b"],
    "Debugging": [r"\bdebugging\b", r"\bdebug\b", r"troubleshooting", r"troubleshoot"],
    "Problem Solving": [r"problem[- ]solving", r"problem solving skills"],
    "Analytical Thinking": [r"analytical thinking", r"analytical skills", r"analytical ability"],
    "Communication": [r"clear communication", r"communication skills?", r"verbal communication", r"written communication", r"\bcommunication\b"],
    "Collaboration": [r"teamwork", r"team work", r"collaboration", r"collaborative"],
    "Documentation": [r"documentation", r"technical documentation", r"document requirements"],
    "Continuous Learning": [r"continuous learning", r"continuous improvement", r"learning mindset"],
    "Adaptability": [r"adaptability", r"adaptable", r"flexibility"],
    "Time Management": [r"time management", r"manage time"],
    "Stakeholder Management": [r"stakeholder management", r"stakeholder communication", r"stakeholders"],
    "Requirement Gathering": [r"requirement gathering", r"gather requirements", r"requirements gathering"],
    "Process Analysis": [r"process analysis", r"analyze processes", r"process improvement"],
    "Functional Documentation": [r"functional documentation", r"functional specification", r"functional specifications"],
    "User Acceptance Testing": [r"user acceptance testing", r"\buat\b"],
    "Customer Focus": [r"customer-centric", r"customer centric", r"customer focus", r"customer focused"],
    "Performance Optimization": [r"performance optimization", r"performance tuning", r"optimize performance", r"performance improvement"],
    "Security": [r"security", r"secure software", r"application security"],
    "Programming": [r"programming skills?", r"strong programming", r"proficiency in programming", r"programming ability"],
    "Software Development": [r"software development", r"developing .* software", r"develops? .*modules?", r"develops?, modifies", r"software engineering"],
    "Code Review": [r"code reviews?", r"review complex code", r"review .* code bases?"],
    "Deployment": [r"deployment", r"deploy(?:ment|ing)?"],
    "Configuration Management": [r"configuration management"],
    "System Architecture": [r"system architecture", r"software architecture", r"architecture background", r"architecture and design"],
    "System Design": [r"system design", r"software design", r"architecture and design"],
    "Initiative": [r"take initiative", r"initiative"],
    "Independent Work": [r"work independently", r"independently"],
    "Leadership": [r"leadership", r"leadership capability", r"leadership skills"],
    "Ownership": [r"ownership", r"accountability", r"own(?:ership)? and accountability"],
    "Business Acumen": [r"business sense", r"business acumen"],
    "Interpersonal Skills": [r"interpersonal skills?", r"interpersonal"],
    "Emerging Technologies": [r"emerging technologies", r"new and emerging technologies"],
}

PROFESSIONAL_CONCEPTS = {
    "Communication", "Collaboration", "Continuous Learning", "Adaptability",
    "Time Management", "Stakeholder Management", "Customer Focus",
    "Initiative", "Independent Work", "Leadership", "Ownership",
    "Business Acumen", "Interpersonal Skills"
}

RESPONSIBILITY_CONCEPTS = {
    "SDLC", "Testing", "Debugging", "Performance Optimization", "Documentation",
    "Requirement Gathering", "Process Analysis", "Functional Documentation",
    "User Acceptance Testing", "Programming", "Software Development", "Code Review",
    "Deployment", "Configuration Management", "System Architecture", "System Design",
    "Emerging Technologies"
}

# Explicit edges are directional: the left side is the JD requirement and
# the right side is resume evidence. They never mean that two skills are equal.
SKILL_RELATIONSHIPS = {
    "Testing": {
        "pytest": 1.00,
        "Testing": 1.00,
    },
    "Problem Solving": {
        "Data Structures": 0.65,
        "Algorithms": 0.65,
        "Debugging": 0.75,
    },
    "Backend Development": {
        "Flask": 0.90,
        "Django": 0.90,
        "FastAPI": 0.90,
        "REST API": 0.85,
        "API Development": 0.85,
    },
    "API Development": {
        "REST API": 0.90,
        "Flask": 0.75,
        "Django": 0.75,
        "FastAPI": 0.90,
    },
    "Database": {
        "SQL": 0.90,
        "MySQL": 0.90,
        "PostgreSQL": 0.90,
        "SQLite": 0.85,
        "MongoDB": 0.75,
        "ORM": 0.70,
    },
    "Data Engineering": {
        "SQL": 0.45,
        "ETL": 0.90,
        "Data Pipelines": 0.90,
        "Data Warehousing": 0.90,
        "Data Modeling": 0.85,
        "Data Processing": 0.70,
    },
    "Machine Learning": {
        "Scikit-learn": 0.90,
        "Pandas": 0.55,
        "NumPy": 0.55,
    },
    "Cloud Computing": {
        "AWS": 0.90,
        "Azure": 0.90,
        "GCP": 0.90,
    },
    "Cloud Native": {
        "Docker": 0.65,
        "Kubernetes": 0.75,
    },
    "Software Development": {
        "Python": 0.35,
        "Java": 0.35,
        "C++": 0.35,
        "Git": 0.35,
        "Testing": 0.70,
        "Debugging": 0.70,
        "SDLC": 0.85,
        "Backend Development": 0.90,
    },
    "Programming": {
        "Python": 0.95,
        "Java": 0.95,
        "C++": 0.95,
        "JavaScript": 0.90,
    },
    "Software Development": {
        "Backend Development": 0.90,
        "Python": 0.55,
        "Django": 0.80,
        "Flask": 0.80,
        "REST API": 0.75,
        "Git": 0.35,
    },
    "Code Review": {
        "Code Review": 1.00,
        "Git": 0.25,
    },
    "Deployment": {
        "Docker": 0.55,
        "DevOps": 0.60,
        "AWS": 0.55,
        "Azure": 0.55,
        "GCP": 0.55,
    },
    "System Architecture": {
        "System Design": 0.65,
        "Backend Development": 0.35,
    },
    "System Design": {
        "System Architecture": 0.70,
        "Backend Development": 0.30,
    },
    "Initiative": {},
    "Independent Work": {},
    "Leadership": {},
    "Ownership": {},
    "Business Acumen": {},
    "Interpersonal Skills": {
        "Communication": 0.60,
        "Collaboration": 0.60,
    },
    "Emerging Technologies": {
        "Machine Learning": 0.55,
        "Python": 0.25,
    },
    "Debugging": {
        "Testing": 0.50,
        "pytest": 0.60,
    },
    "Data Modeling": {
        "Data Warehousing": 0.70,
        "Star Schema": 0.85,
        "Snowflake Schema": 0.85,
        "Fact and Dimension Tables": 0.90,
    },
    "Performance Optimization": {
        "System Design": 0.35,
        "System Architecture": 0.35,
        "Production Systems": 0.35,
    },
}

CANONICAL_ALIASES = {
    "unit testing": "Testing",
    "integration testing": "Testing",
    "automated testing": "Testing",
    "software testing": "Testing",
    "troubleshooting": "Debugging",
    "problem-solving": "Problem Solving",
    "problem solving": "Problem Solving",
    "teamwork": "Collaboration",
    "team work": "Collaboration",
    "software development life cycle": "SDLC",
    "software development lifecycle": "SDLC",
}


def _all_skill_data():
    data = dict(SKILLS)
    for name, value in VIRTUAL_SKILLS.items():
        data.setdefault(name, value)
    return data


def _skill_aliases(skill):
    data = _all_skill_data().get(skill, {})
    aliases = list(data.get("aliases", []))
    aliases.append(skill)
    return aliases


def _canonical_skill(name):
    return CANONICAL_ALIASES.get(name.lower().strip(), name)


def _improved_split_resume_sections(text):
    sections = {
        "summary": "", "projects": "", "experience": "", "skills": "",
        "education": "", "certifications": "", "achievements": "", "other": ""
    }
    current = "other"
    lines = [x.strip() for x in (text or "").splitlines() if x.strip()]
    section_patterns = [
        ("summary", r"^(summary|profile|professional summary|objective)$"),
        ("projects", r"^(projects?|personal projects?|academic projects?)$"),
        ("experience", r"^(experience|work experience|internship|internships|professional experience)$"),
        ("skills", r"^(technical skills|skills|core skills)$"),
        ("education", r"^(education|academic background)$"),
        ("certifications", r"^(certifications?|certificates?|certifications & virtual experience)$"),
        ("achievements", r"^(achievements?|activities?|extracurriculars?|leadership)$"),
    ]
    for line in lines:
        lower = line.lower()
        found = False
        for name, pattern in section_patterns:
            if re.match(pattern, lower):
                current = name
                found = True
                break
        if not found:
            sections[current] += line + "\n"
    return sections


def _text_has(text, patterns):
    lower = normalize_search(text)
    return any(re.search(p, lower) for p in patterns)


def _direct_skill(text, skill):
    if not text:
        return False
    data = _all_skill_data().get(skill)
    if not data:
        return _text_has(text, CONCEPT_PATTERNS.get(skill, []))
    return contains_alias(text, data.get("aliases", [])) or _text_has(text, CONCEPT_PATTERNS.get(skill, []))


def _resume_skill_set(text):
    found = set(extract_skills(text))
    # Include virtual/canonical concepts too. These are not merely keywords;
    # they let the evidence engine reason over broader capabilities such as
    # Backend Development when the resume explicitly states them.
    for skill, data in _all_skill_data().items():
        if contains_alias(text, data.get("aliases", [])):
            found.add(skill)
    for skill, patterns in CONCEPT_PATTERNS.items():
        if _text_has(text, patterns):
            found.add(skill)
    return {_canonical_skill(x) for x in found}


def _contextual_evidence(section_text, skill):
    lower = normalize_search(section_text)
    rules = {
        "Software Development": [
            r"developed application", r"built application", r"developed .*software",
            r"software development", r"backend services", r"application features"
        ],
        "Testing": [r"pytest", r"unit tests?", r"integration tests?", r"wrote .*tests?", r"test automation"],
        "Debugging": [r"debug", r"troubleshoot", r"troubleshooting"],
        "Problem Solving": [r"problem[- ]solving", r"solved", r"troubleshoot", r"debug"],
        "Machine Learning": [r"machine learning", r"scikit-learn", r"ml model", r"trained .*model"],
        "Data Structures": [r"data structures?", r"data structures? & algorithms?", r"dsa"],
        "Algorithms": [r"algorithms?", r"data structures? & algorithms?", r"dsa"],
        "OOP": [r"object[- ]oriented programming", r"\boop\b"],
        "API Development": [r"restful? api", r"rest api", r"api development", r"backend services"],
        "Backend Development": [r"backend development", r"backend services", r"server[- ]side"],
        "Collaboration": [r"team stand[- ]ups?", r"code reviews?", r"teamwork", r"collaboration"],
        "Documentation": [r"documentation", r"documented"],
        "Performance Optimization": [r"performance optimization", r"performance tuning", r"optimi[sz]ed performance"],
    }
    for pattern in rules.get(skill, []):
        if re.search(pattern, lower):
            return True
    return False


def _relationship_evidence(requirement_skill, resume_skills):
    relation_map = SKILL_RELATIONSHIPS.get(requirement_skill, {})
    best = None
    for raw in resume_skills:
        skill = _canonical_skill(raw)
        strength = relation_map.get(skill)
        if strength is None:
            related = RELATED_SKILLS.get(requirement_skill, set()) if 'RELATED_SKILLS' in globals() else set()
            if skill in related:
                strength = 0.40
        if strength is not None and (best is None or strength > best["strength"]):
            best = {"skill": skill, "strength": float(strength)}
    return best


def resume_evidence(requirement, resume_text):
    skill = requirement.get("skill", "")
    sections = _improved_split_resume_sections(resume_text)
    experience = sections["experience"]
    projects = sections["projects"]
    skills = sections["skills"]
    certifications = sections["certifications"]
    education = sections["education"]
    all_text = resume_text or ""
    resume_skills = _resume_skill_set(all_text)

    # Direct professional/internship evidence.
    if _direct_skill(experience, skill) or _contextual_evidence(experience, skill):
        return {"score": 1.00, "level": "Strong", "source": "Professional Experience", "evidence": f"{skill} is directly demonstrated in professional/internship experience."}

    # Direct project evidence.
    if _direct_skill(projects, skill) or _contextual_evidence(projects, skill):
        return {"score": 0.90, "level": "Strong", "source": "Project", "evidence": f"{skill} is directly demonstrated in project work."}

    # Some concepts have legitimate indirect evidence in professional work.
    relationship = _relationship_evidence(skill, resume_skills)
    if relationship and skill in {"Testing", "Software Development", "Backend Development", "API Development"}:
        # pytest -> Testing and Django/Flask/REST -> backend/API are strong evidence
        # when they are actually in the internship/project context.
        rel_skill = relationship["skill"]
        if _direct_skill(experience, rel_skill) or _contextual_evidence(experience, rel_skill) or _direct_skill(projects, rel_skill):
            score = min(0.95, max(0.80, relationship["strength"]))
            return {"score": score, "level": "Strong", "source": "Related Professional Evidence", "evidence": f"{rel_skill} provides strong practical evidence for {skill}.", "related_skill": rel_skill}

    # Explicit skills list. Do not call this professional experience.
    if _direct_skill(skills, skill):
        return {"score": 0.68, "level": "Demonstrated", "source": "Skills Section", "evidence": f"{skill} is explicitly listed in the technical skills section."}

    # Skills-section conceptual equivalents such as DSA -> Problem Solving.
    if skill == "Problem Solving":
        if _direct_skill(skills, "Data Structures") or _direct_skill(skills, "Algorithms"):
            return {"score": 0.62, "level": "Related", "source": "Core CS Skills", "evidence": "Data Structures/Algorithms provide related evidence for problem solving, but problem solving is not directly demonstrated."}
    if skill in {"Data Structures", "Algorithms"} and _text_has(skills, [r"data structures?\s*(?:&|and)\s*algorithms?", r"\bdsa\b"]):
        return {"score": 0.68, "level": "Demonstrated", "source": "Skills Section", "evidence": f"{skill} is explicitly represented by the DSA entry in the technical skills section."}

    # Machine Learning can be explicitly listed in skills; education alone is weaker.
    if skill == "Machine Learning" and _text_has(skills, [r"machine learning", r"scikit-learn"]):
        return {"score": 0.68, "level": "Demonstrated", "source": "Skills Section", "evidence": "Machine Learning is explicitly listed in the technical skills section."}

    if _direct_skill(certifications, skill):
        return {"score": 0.45, "level": "Certified", "source": "Certification", "evidence": f"{skill} is supported by a certification or virtual-experience entry."}

    if skill in resume_skills or _direct_skill(all_text, skill):
        return {"score": 0.30, "level": "Mentioned", "source": "Resume Mention", "evidence": f"{skill} is mentioned in the resume, but stronger evidence was not found."}

    if skill == "Problem Solving":
        relationship = _relationship_evidence(skill, resume_skills)
        if relationship:
            score = min(0.65, max(0.45, relationship["strength"] * 0.85))
            return {"score": round(score, 2), "level": "Related", "source": "Related Core Skill", "evidence": f"{relationship['skill']} provides related evidence for {skill}; the capability itself is not directly demonstrated.", "related_skill": relationship["skill"]}

    if relationship:
        score = min(0.65, max(0.35, relationship["strength"] * 0.70))
        return {"score": round(score, 2), "level": "Related", "source": "Related Technology", "evidence": f"{relationship['skill']} provides related evidence for {skill}; the required skill itself is not directly demonstrated.", "related_skill": relationship["skill"]}

    # Conservative textual similarity. It can never create a strong match.
    target = normalize_search(skill)
    best_ratio = 0.0
    best_skill = None
    for resume_skill in resume_skills:
        ratio = SequenceMatcher(None, target, normalize_search(resume_skill)).ratio()
        if ratio > best_ratio:
            best_ratio, best_skill = ratio, resume_skill
    if best_ratio >= 0.88 and best_skill:
        return {"score": 0.25, "level": "Semantic Similarity", "source": "Similar Skill", "evidence": f"{best_skill} is textually similar to {skill}, but this is weak evidence and should be verified.", "related_skill": best_skill}

    return {"score": 0.0, "level": "No Evidence", "source": "No Evidence", "evidence": ""}


def _jd_lines(text):
    return [clean_line(x) for x in (text or "").splitlines() if clean_line(x)]


def _is_metadata_line(line):
    lower = (line or "").lower().strip()
    # Cohort/program identifiers such as spark_<init> are metadata, not technology requirements.
    if re.match(r"^cohort\s*:", lower) or re.search(r"\b(?:alpha|dev|spark)_<[^>]+>", lower):
        return True
    prefixes = (
        "job title:", "jobtitle:", "location:", "locations:", "stipend:",
        "salary:", "package:", "ctc:", "department:", "role:", "designation:",
        "employment type:", "job type:", "experience:", "qualification:",
        "qualifications:", "eligibility:", "education:", "batch:", "apply:",
        "apply at:", "ref:", "reference:"
    )
    if lower.startswith(prefixes):
        return True
    return lower in {
        "about the company", "about us", "benefits", "job details", "job description",
        "job summary", "requirements", "required skills", "key skills", "technical skills",
        "technical requirements", "responsibilities", "qualifications", "preferred qualifications",
        "preferred skills", "eligibility criteria"
    }


def detect_jd_section(line):
    lower = (line or "").lower().strip().rstrip(":")
    # Explicit headings in real-world JDs should control interpretation.
    if lower in {
        "what will differentiate you", "what differentiates you",
        "what will set you apart", "differentiators"
    }:
        return "Differentiators"
    if lower in {"what we value", "values", "our values"}:
        return "Values"
    if lower in {"your role", "role", "responsibilities", "responsibility",
                 "what you'll do", "what you will do", "role and responsibilities",
                 "your responsibilities"}:
        return "Responsibilities"
    if lower in {"your profile", "candidate profile", "what we're looking for",
                 "what we are looking for", "key competencies"}:
        return "Professional"
    if lower.startswith("eligible streams") or lower.startswith("eligibility"):
        return "Qualifications"
    if any(x in lower for x in [
        "why this is the launchpad", "benefits", "what you get", "what we offer",
        "what you will love about working here", "about the company", "about capgemini",
        "disclaimer", "make it real"
    ]):
        return "Company Context"
    if any(x in lower for x in ["required skills", "key skills", "technical skills", "technical requirements", "skills required", "core skills"]):
        return "Technical Skills"
    if any(x in lower for x in ["preferred skills", "preferred qualifications", "nice to have", "nice-to-have", "good to have", "good-to-have"]):
        return "Preferred Skills"
    if any(x in lower for x in ["qualification", "eligibility", "education"]):
        return "Qualifications"
    if any(x in lower for x in ["about the role", "job description", "job summary", "role overview"]):
        return "Job Description"
    return None


def clean_requirement_name(skill):
    replacements = {
        "Software Development Life Cycle": "SDLC",
        "Software Development Lifecycle": "SDLC",
        "Unit Testing": "Testing",
        "Integration Testing": "Testing",
        "Automated Testing": "Testing",
        "Troubleshooting": "Debugging",
        "Problem-Solving": "Problem Solving",
        "Problem-Solving Skills": "Problem Solving",
        "Team Work": "Collaboration",
        "Teamwork": "Collaboration",
        "Fact and Dimension Tables": "Fact and Dimension Modeling",
        "Problem-Solving": "Problem Solving",
        "Interpersonal Skill": "Interpersonal Skills",
    }
    return replacements.get(skill, skill)


def _requirement_kind(skill, section):
    if skill in PROFESSIONAL_CONCEPTS:
        return "Professional"
    if skill in _all_skill_data() or skill in CONCEPT_PATTERNS:
        return "Technical"
    if section == "Responsibilities":
        return "Responsibility"
    return "Conceptual"


def _tier_for_line(line, section, skill):
    lower = (line or "").lower()
    if section in {"Company Context", "Differentiators", "Values"}:
        return "Supporting"
    if any(marker in lower for marker in PREFERRED_MARKERS) or section == "Preferred Skills":
        return "Supporting"
    if section == "Qualifications":
        return "Core" if any(marker in lower for marker in CORE_MARKERS) else "Supporting"
    if skill in PROFESSIONAL_CONCEPTS:
        return "Core" if section == "Professional" and any(marker in lower for marker in CORE_MARKERS) else ("Supporting" if section in {"Professional", "Values"} else "Core")
    if section == "Differentiators":
        return "Supporting"
    if skill in _all_skill_data() or skill in CONCEPT_PATTERNS:
        return "Core"
    if any(marker in lower for marker in CORE_MARKERS):
        return "Core"
    return "Supporting"


def _req_weight(skill, kind, tier):
    data = _all_skill_data().get(skill, {})
    base = float(data.get("weight", 3))
    if kind == "Professional":
        base = min(base, 2.0)
    if tier == "Supporting":
        base = min(base, 3.0)
    return base


def _extract_concepts(line):
    lower = normalize_search(line)
    result = []
    for name, patterns in CONCEPT_PATTERNS.items():
        if any(re.search(p, lower) for p in patterns):
            result.append(name)
    return result


def extract_requirements(job_description):
    lines = _jd_lines(job_description)
    if not lines:
        return []

    requirements = {}
    # Most JDs begin with employer/program context before the actual role sections.
    # Treat that opening block as context so marketing language is not mistaken for requirements.
    section = "Company Context"
    skill_data = _all_skill_data()

    def add(skill, line, position, current_section, forced_type=None):
        skill = clean_requirement_name(skill)
        kind = forced_type or _requirement_kind(skill, current_section)
        tier = _tier_for_line(line, current_section, skill)
        weight = _req_weight(skill, kind, tier)
        key = skill.lower().strip()
        candidate = {
            "skill": skill,
            "category": skill_data.get(skill, {}).get("category", "Professional" if kind == "Professional" else "Technical Concept"),
            "tier": tier,
            "importance": tier,
            "weight": weight,
            "effective_weight": weight if tier == "Core" else round(weight * 0.45, 2),
            "type": kind,
            "dimension": (
                "Responsibility" if current_section == "Responsibilities"
                else ("Professional" if kind == "Professional" or current_section in {"Professional", "Values"}
                      else ("Differentiator" if current_section == "Differentiators" else "Technical"))
            ),
            "section": current_section,
            "source_section": current_section,
            "jd_evidence": clean_line(line),
            "position": position,
        }
        old = requirements.get(key)
        if old is None:
            requirements[key] = candidate
            return
        if old["tier"] != "Core" and tier == "Core":
            old["tier"] = old["importance"] = "Core"
        if weight > old["weight"]:
            old["weight"] = weight
        old["effective_weight"] = old["weight"] if old["tier"] == "Core" else round(old["weight"] * 0.45, 2)
        # Prefer a requirement-specific technical/responsibility line over generic evidence.
        if current_section != "General" and old.get("source_section") == "General":
            old["section"] = old["source_section"] = current_section
            old["jd_evidence"] = clean_line(line)
        if old.get("type") == "Professional" and kind == "Technical":
            old["type"] = "Technical"

    for idx, line in enumerate(lines):
        detected = detect_jd_section(line)
        if detected:
            section = detected
            continue
        if _is_metadata_line(line) or section == "Company Context":
            continue

        for skill, data in skill_data.items():
            if contains_alias(line, data.get("aliases", [])):
                add(skill, line, idx, section)

        for concept in _extract_concepts(line):
            kind = "Professional" if concept in PROFESSIONAL_CONCEPTS else None
            add(concept, line, idx, section, kind)

    # Phrase-level requirements frequently split by PDF extraction.
    whole = normalize_search(job_description)
    phrase_rules = {
        "API Development": [r"\bapi development\b", r"\bapi design\b"],
        "System Architecture": [r"\bsystem architecture\b", r"\bsoftware architecture\b"],
        "Distributed Systems": [r"\bdistributed systems?\b"],
        "Cloud Native": [r"\bcloud[- ]native\b"],
        "Containerization": [r"\bcontainerization\b", r"\bcontainerized applications?\b"],
        "Production Systems": [r"\bproduction systems?\b", r"\bproduction environments?\b"],
        "Data Warehousing": [r"\bdata warehousing\b", r"\bdata warehouse\b"],
        "Data Modeling": [r"\bdata modeling\b", r"\bdata modelling\b"],
        "Data Pipelines": [r"\bdata pipelines?\b"],
        "Data Quality": [r"\bdata quality\b"],
        "Fact and Dimension Modeling": [r"\bfact and dimension\b", r"\bfact tables?\b", r"\bdimension tables?\b"],
        "ETL": [r"\betl\b", r"extract[, ]+transform[, ]+load"],
        "API Development": [r"\bbuilding apis?\b", r"\bbuild apis?\b", r"\brestful? apis?\b"],
        "Scalability": [r"\bscalability\b", r"\bscalable\b"],
        "Design Patterns": [r"\bdesign patterns?\b"],
        "Agentic Thinking": [r"\bagentic thinking\b", r"\bagentic ai\b", r"\bai agents?\b"],
        "Security": [r"\bsecurity\b", r"\bapplication security\b"],
        "Data Structures": [r"\bdata structures?\b"],
        "Algorithms": [r"\balgorithms?\b"],
    }
    for skill, patterns in phrase_rules.items():
        for pattern in patterns:
            match = re.search(pattern, whole)
            if match:
                evidence_line = skill
                for idx, line in enumerate(lines):
                    if re.search(pattern, normalize_search(line)):
                        evidence_line = line
                        break
                add(skill, evidence_line, match.start(), "Technical Skills")
                break

    result = list(requirements.values())
    result.sort(key=lambda x: (0 if x["tier"] == "Core" else 1, 0 if x["type"] == "Technical" else 1, -float(x["effective_weight"]), x.get("position", 999999)))
    return result


def assess_eligibility(resume_text, jd_text):
    resume = normalize_search(resume_text)
    jd = normalize_search(jd_text)
    checks = []

    def add(criterion, status, evidence):
        checks.append({"criterion": criterion, "status": status, "evidence": evidence})

    if re.search(r"b\.?\s*tech|b\.?\s*e\.?|bachelor", jd):
        if re.search(r"b\.?\s*tech|b\.?\s*e\.?|bachelor", resume):
            add("Required degree", "Pass", "A bachelor's-level engineering degree is present.")
        else:
            add("Required degree", "No Evidence", "The required degree is not visible in the resume text.")

    if re.search(r"computer science|cse|cs/it|information technology", jd):
        if re.search(r"computer science|cse|information technology|computer engineering", resume):
            add("Relevant CS/IT background", "Pass", "Computer Science/related background is present.")
        else:
            add("Relevant CS/IT background", "No Evidence", "Relevant CS/IT background was not found.")

    if re.search(r"\b(?:minimum|at least|above|>=)\s*\d+(?:\.\d+)?\s*%", jd):
        if re.search(r"\b\d{2}(?:\.\d+)?\s*%", resume):
            add("Academic percentage", "Review", "The JD contains a percentage threshold and the resume contains a percentage; manual comparison is required.")
        else:
            add("Academic percentage", "No Evidence", "The JD contains a percentage threshold but the resume does not provide marks.")

    if "no diploma" in jd or "without diploma" in jd:
        add("No diploma restriction", "Review", "This criterion should be verified from the candidate's academic record; absence from the resume is not proof.")

    hard = [x for x in checks if x["status"] in {"Pass", "Fail"}]
    fails = sum(x["status"] == "Fail" for x in checks)
    passes = sum(x["status"] == "Pass" for x in checks)
    unknown = sum(x["status"] in {"No Evidence", "Review"} for x in checks)
    if fails:
        status = "Not Eligible"
    elif hard and passes == len(hard) and unknown == 0:
        status = "Eligible"
    elif passes and not fails:
        status = "Likely Eligible"
    else:
        status = "Needs Verification"
    return {"status": status, "checks": checks, "verified_count": passes, "unknown_count": unknown, "failed_count": fails}


def _dimension_score(items):
    if not items:
        return None
    total = sum(float(x.get("effective_weight", x.get("weight", 1))) for x in items)
    achieved = sum(float(x.get("effective_weight", x.get("weight", 1))) * float(x.get("match_score", 0)) for x in items)
    return round(achieved / total * 100, 2) if total else 0.0


def score_requirements(resume_text, requirements):
    matched, partial, missing = [], [], []
    resume_skills = sorted(_resume_skill_set(resume_text))
    for requirement in requirements:
        evidence = resume_evidence(requirement, resume_text)
        score = float(evidence.get("score", 0))
        weight = float(requirement.get("effective_weight", requirement.get("weight", 1)))
        item = {
            **requirement,
            "match_score": round(score, 2),
            "match_level": evidence.get("level", "No Evidence"),
            "evidence": evidence.get("evidence", ""),
            "evidence_source": evidence.get("source", "No Evidence"),
            "related_skill": evidence.get("related_skill", ""),
            "weighted_contribution": round(weight * score, 2),
        }
        if score >= 0.80:
            matched.append(item)
        elif score > 0:
            partial.append(item)
        else:
            missing.append(item)

    details = matched + partial + missing
    # Technical fit measures technical capabilities wherever the JD states them.
    # Responsibility fit separately measures requirements expressed as duties.
    # This deliberately allows the same technical requirement to inform both
    # capability and responsibility without pretending the two dimensions are identical.
    technical = [x for x in details if x.get("type") == "Technical"]
    responsibility = [x for x in details if x.get("dimension") == "Responsibility"]
    professional = [x for x in details if x.get("dimension") == "Professional"]

    # Technical score intentionally excludes soft/professional criteria.
    technical_score = _dimension_score(technical)
    responsibility_score = _dimension_score(responsibility)
    professional_score = _dimension_score(professional)

    dimensions = []
    if technical_score is not None:
        dimensions.append((technical_score, 0.70))
    if responsibility_score is not None:
        dimensions.append((responsibility_score, 0.20))
    if professional_score is not None:
        dimensions.append((professional_score, 0.10))
    if dimensions:
        divisor = sum(w for _, w in dimensions)
        final_score = sum(score * weight for score, weight in dimensions) / divisor
    else:
        final_score = 0.0

    coverage = ((len(matched) + 0.5 * len(partial)) / len(requirements) * 100) if requirements else 0.0

    core_items = [x for x in details if x.get("tier") == "Core"]
    supporting_items = [x for x in details if x.get("tier") == "Supporting"]
    core_score = _dimension_score(core_items) or 0.0
    supporting_score = _dimension_score(supporting_items) or 0.0

    return {
        "resume_skills": resume_skills,
        "matched": matched,
        "partial": partial,
        "missing": missing,
        "match_percentage": round(max(0.0, min(100.0, final_score)), 2),
        "skill_coverage": round(coverage, 2),
        "matched_weight": round(sum(x.get("weighted_contribution", 0) for x in details), 2),
        "total_weight": round(sum(float(x.get("effective_weight", x.get("weight", 1))) for x in details), 2),
        "core_score": round(core_score, 2),
        "supporting_score": round(supporting_score, 2),
        "technical_fit": technical_score or 0.0,
        "responsibility_fit": responsibility_score or 0.0,
        "professional_fit": professional_score or 0.0,
    }


def _gap_reason(item):
    score = float(item.get("match_score", 0))
    skill = item.get("skill", "this requirement")
    if score == 0:
        return f"No evidence found in the resume for {skill}. This does not prove the candidate lacks it; the resume simply does not demonstrate it."
    if item.get("match_level") == "Related":
        return f"Related evidence was found, but {skill} is not directly demonstrated."
    if item.get("match_level") == "Demonstrated":
        return f"{skill} is listed or represented in the resume, but stronger hands-on evidence would improve the fit."
    return f"{skill} has some evidence, but the evidence is not strong enough for a full match."


def build_recommendations(missing, partial):
    output = []
    for item in missing + partial:
        skill = item.get("skill")
        if not skill:
            continue
        tier = item.get("tier", "Supporting")
        if item.get("match_score", 0) == 0:
            action = f"Add direct evidence for {skill}: a project, internship task, certification, or measurable implementation. Do not add it as a keyword unless you can substantiate it."
        else:
            action = f"Strengthen the resume evidence for {skill} with a concrete implementation, project bullet, test result, or internship responsibility."
        output.append({
            "skill": skill,
            "priority": "High" if tier == "Core" else "Medium",
            "category": item.get("category", ""),
            "reason": _gap_reason(item),
            "action": action,
        })
    output.sort(key=lambda x: (0 if x["priority"] == "High" else 1, x["skill"]))
    return output


def skills_to_learn(missing, partial):
    output, seen = [], set()
    for item in missing + partial:
        skill = item.get("skill")
        if not skill or skill in seen:
            continue
        seen.add(skill)
        output.append({
            "skill": skill,
            "category": item.get("category", ""),
            "priority": "High" if item.get("tier") == "Core" else "Medium",
            "reason": _gap_reason(item),
        })
    return output


def calculate_project_alignment(resume_text, requirements):
    projects = _improved_split_resume_sections(resume_text).get("projects", "")
    if not projects.strip():
        return []
    output = []
    for req in requirements:
        skill = req.get("skill")
        if _direct_skill(projects, skill) or _contextual_evidence(projects, skill):
            output.append({"skill": skill, "category": req.get("category", ""), "evidence": f"Project work demonstrates {skill}."})
    return output


def learned_skills(resume_text, requirements):
    output = []
    for req in requirements:
        evidence = resume_evidence(req, resume_text)
        if evidence.get("score", 0) >= 0.60:
            output.append({"skill": req.get("skill"), "category": req.get("category", ""), "level": evidence.get("level"), "evidence": evidence.get("evidence", "")})
    return output


def calculate_potential_fit(requirements, current_score, result_details=None):
    if not requirements:
        return round(current_score, 2)
    # Potential fit is the score after resolving evidence gaps, not a hiring probability.
    # If all missing/partial requirements are strongly evidenced, the mathematical ceiling is 100.
    # We also expose the number of gaps separately so the UI can explain the distance.
    return 100.0


def confidence_label(score):
    if score >= 80:
        return "High"
    if score >= 60:
        return "Medium"
    return "Low"


def fit_band(score):
    if score >= 80:
        return "Strong Fit"
    if score >= 65:
        return "Good Fit"
    if score >= 50:
        return "Moderate Fit"
    if score >= 35:
        return "Weak Fit"
    return "Low Fit"


def calculate_confidence(resume_text, jd_text, requirements, details):
    if not requirements:
        return 0.0
    sections = _improved_split_resume_sections(resume_text)
    structured_resume = sum(bool(sections.get(k, "").strip()) for k in ["experience", "projects", "skills", "education"]) / 4
    jd_evidence = sum(bool(x.get("jd_evidence")) for x in requirements) / len(requirements)
    direct_evidence = sum(float(x.get("match_score", 0)) >= 0.8 for x in details) / len(details) if details else 0
    semantic_only = sum(x.get("match_level") == "Semantic Similarity" for x in details) / len(details) if details else 0
    # Confidence measures analysis quality, not candidate quality.
    score = 50 + 20 * structured_resume + 15 * jd_evidence + 15 * direct_evidence - 20 * semantic_only
    return round(max(0.0, min(100.0, score)), 2)


def _why_not_100(details):
    gaps = [x for x in details if float(x.get("match_score", 0)) < 1.0]
    gaps.sort(key=lambda x: (0 if x.get("tier") == "Core" else 1, -float(x.get("effective_weight", x.get("weight", 1)))))
    return [{
        "skill": x.get("skill"),
        "tier": x.get("tier"),
        "type": x.get("type"),
        "reason": _gap_reason(x),
        "weight": x.get("effective_weight", x.get("weight", 1)),
    } for x in gaps[:10]]


def analyze_resume(resume_text, job_description):
    if not (resume_text or "").strip():
        return None, "Resume text could not be extracted."
    if not (job_description or "").strip():
        return None, "Job description text could not be extracted."

    requirements = extract_requirements(job_description)
    if not requirements:
        return None, "No meaningful requirements could be identified in this job description."

    scoring = score_requirements(resume_text, requirements)
    details = scoring["matched"] + scoring["partial"] + scoring["missing"]
    details.sort(key=lambda x: (0 if x.get("tier") == "Core" else 1, 0 if x.get("type") == "Technical" else 1, -float(x.get("effective_weight", 0))))

    matched = scoring["matched"]
    partial = scoring["partial"]
    missing = scoring["missing"]
    technical_details = [x for x in details if x.get("type") == "Technical"]
    technical_missing = [x for x in technical_details if x.get("match_score", 0) == 0]
    technical_partial = [x for x in technical_details if 0 < x.get("match_score", 0) < 0.8]
    technical_matched = [x for x in technical_details if x.get("match_score", 0) >= 0.8]
    responsibility_details = [x for x in details if x.get("dimension") == "Responsibility"]
    professional_details = [x for x in details if x.get("dimension") == "Professional"]

    eligibility = assess_eligibility(resume_text, job_description)
    confidence = calculate_confidence(resume_text, job_description, requirements, details)
    recommendations = build_recommendations(technical_missing + [x for x in responsibility_details if x.get("match_score", 0) == 0], technical_partial + [x for x in responsibility_details if 0 < x.get("match_score", 0) < 0.8])
    learn = skills_to_learn(technical_missing, technical_partial)
    projects = calculate_project_alignment(resume_text, requirements)
    learned = learned_skills(resume_text, requirements)

    why_not = _why_not_100(details)
    strongest_gaps = [x for x in why_not if x.get("match_score", 0) != 1.0]
    # Explicitly state the reason for the score, rather than a generic sentence.
    if technical_missing:
        top = [x.get("skill") for x in technical_missing[:5]]
        why_summary = "The score is below 100% because the resume does not directly demonstrate: " + ", ".join(top) + "."
    elif technical_partial:
        top = [x.get("skill") for x in technical_partial[:5]]
        why_summary = "The score is below 100% because some technical requirements have only partial or related evidence: " + ", ".join(top) + "."
    else:
        why_summary = "The resume directly covers the detected technical requirements; remaining differences are mainly responsibility or professional-evidence strength."

    result = {
        "resume_skills": scoring["resume_skills"],
        "job_skills": [x["skill"] for x in requirements],
        "matched_skills": [x["skill"] for x in technical_matched],
        "partial_skills": [x["skill"] for x in technical_partial],
        "missing_skills": [x["skill"] for x in technical_missing],
        "match_percentage": scoring["match_percentage"],
        "skill_coverage": scoring["skill_coverage"],
        "matched_weight": scoring["matched_weight"],
        "total_weight": scoring["total_weight"],
        "core_score": scoring["core_score"],
        "supporting_score": scoring["supporting_score"],
        "technical_fit": scoring["technical_fit"],
        "responsibility_fit": scoring["responsibility_fit"],
        "professional_fit": scoring["professional_fit"],
        "fit_band": fit_band(scoring["match_percentage"]),
        "confidence": confidence,
        "confidence_label": confidence_label(confidence),
        "potential_fit": calculate_potential_fit(requirements, scoring["match_percentage"], details),
        "eligibility": eligibility,
        "recommendations": recommendations,
        "skills_to_learn": learn,
        "learned_skills": learned,
        "project_alignment": projects,
        "skill_weights": {x["skill"]: x.get("weight", 0) for x in requirements},
        "requirement_details": details,
        "matched_details": matched,
        "partial_details": partial,
        "missing_details": missing,
        "technical_details": technical_details,
        "responsibility_details": responsibility_details,
        "professional_details": professional_details,
        "strong_matches": technical_matched[:15],
        "partial_matches": technical_partial[:15],
        "no_evidence_gaps": technical_missing[:15],
        "why_not_100": why_not,
        "why_not_100_summary": why_summary,
        "analysis_version": "10-step-evidence-engine-v2",
    }
    return result, None


# ============================================================
# ROLE DETECTION
# ============================================================

def detect_job_roles(text):
    lines = [clean_line(x) for x in (text or "").splitlines() if clean_line(x)]
    roles = []
    for i, line in enumerate(lines):
        m = re.match(r"^job\s*title\s*:\s*(.+)$", line, flags=re.I)
        if m:
            title = clean_line(m.group(1))
            if title:
                roles.append({"title": title, "line_index": i})

    role_patterns = [
        r"(?:intern|junior|senior|associate|trainee|graduate)?\s*[-:]?\s*software\s+(?:engineer|developer)",
        r"(?:intern|junior|senior|associate|trainee|graduate)?\s*[-:]?\s*application\s+(?:engineer|developer)",
        r"(?:intern|junior|senior|associate|trainee|graduate)?\s*[-:]?\s*data\s+(?:engineer|developer|analyst|scientist)",
        r"(?:intern|junior|senior|associate|trainee|graduate)?\s*[-:]?\s*machine\s+learning\s+(?:engineer|scientist)",
        r"(?:intern|junior|senior|associate|trainee|graduate)?\s*[-:]?\s*platform\s+engineer",
        r"(?:intern|junior|senior|associate|trainee|graduate)?\s*[-:]?\s*backend\s+(?:engineer|developer)",
        r"(?:intern|junior|senior|associate|trainee|graduate)?\s*[-:]?\s*frontend\s+(?:engineer|developer)",
        r"(?:intern|junior|senior|associate|trainee|graduate)?\s*[-:]?\s*full[- ]stack\s+(?:engineer|developer)",
        r"(?:intern|junior|senior|associate|trainee|graduate)?\s*[-:]?\s*devops\s+engineer",
        r"(?:intern|junior|senior|associate|trainee|graduate)?\s*[-:]?\s*cloud\s+engineer",
        r"(?:intern|junior|senior|associate|trainee|graduate)?\s*[-:]?\s*business\s+analyst",
        r"(?:intern|junior|senior|associate|trainee|graduate)?\s*[-:]?\s*system\s+engineer",
        r"(?:intern|junior|senior|associate|trainee|graduate)?\s*[-:]?\s*qa\s+engineer",
        r"(?:intern|junior|senior|associate|trainee|graduate)?\s*[-:]?\s*test\s+engineer",
    ]
    # If the document contains explicit Job Title fields, trust those and
    # ignore generic role-like rows elsewhere in eligibility tables.
    if not roles:
        role_scan = enumerate(lines)
    else:
        role_scan = []
    for i, line in role_scan:
        if len(line) > 180:
            continue
        for pattern in role_patterns:
            if re.match(r"^\s*" + pattern + r"(?:\s+.*)?$", line, flags=re.I):
                roles.append({"title": line, "line_index": i})
                break

    unique, seen = [], set()
    for role in roles:
        key = normalize_search(role["title"])
        if key and key not in seen:
            seen.add(key)
            unique.append(role)
    if len(unique) < 2:
        return []

    output = []
    for i, role in enumerate(unique):
        start = role["line_index"]
        end = unique[i + 1]["line_index"] if i + 1 < len(unique) else len(lines)
        output.append({"title": role["title"], "text": "\n".join(lines[start:end])})
    return output

# ============================================================
# DATABASE COMPATIBILITY
# ============================================================

_original_init_db_final = init_db
_original_save_analysis_final = save_analysis


def init_db():
    _original_init_db_final()
    connection = get_db()
    for statement in [
        "ALTER TABLE analyses ADD COLUMN result_json TEXT",
        "ALTER TABLE analyses ADD COLUMN role TEXT",
        "ALTER TABLE analyses ADD COLUMN resume_name TEXT",
        "ALTER TABLE analyses ADD COLUMN job_name TEXT",
    ]:
        try:
            connection.execute(statement)
        except sqlite3.OperationalError:
            pass
    connection.commit()
    connection.close()


def save_analysis(result, role=None, resume_name=None, job_name=None):
    # Write through the original schema first so existing history remains compatible.
    analysis_id = _original_save_analysis_final(result)
    connection = get_db()
    try:
        connection.execute("UPDATE analyses SET result_json = ?, role = ?, resume_name = ?, job_name = ? WHERE id = ?", (json.dumps(result), role, resume_name, job_name, analysis_id))
        connection.commit()
    except sqlite3.OperationalError:
        pass
    connection.close()
    return analysis_id


def engine_diagnostics():
    return {
        "skill_database": bool(SKILLS),
        "relationship_graph": bool(SKILL_RELATIONSHIPS),
        "effective_weight": True,
        "pdf_reader": PdfReader is not None,
        "database": True,
        "analysis_version": "10-step-evidence-engine-v2",
    }



# ============================================================
# HYBRID AI ENGINE
# ============================================================
# The deterministic engine remains the scoring authority. The optional AI
# layer evaluates semantic evidence and can improve the evidence classification
# without allowing the model to invent skills or directly choose the final fit.
# ============================================================

try:
    from ai_engine import analyze_with_ai
except Exception:
    analyze_with_ai = None


def _hybrid_evidence_score(deterministic_score, ai_item):
    """Combine deterministic evidence with AI evidence conservatively."""
    d = max(0.0, min(1.0, float(deterministic_score or 0)))
    if not ai_item:
        return d

    a = max(0.0, min(1.0, float(ai_item.get("evidence_strength", 0) or 0)))
    confidence = max(0.0, min(1.0, float(ai_item.get("confidence", 0) or 0)))
    relationship = ai_item.get("relationship", "no_evidence")

    # Deterministic direct evidence is never downgraded by the AI layer.
    if d >= 0.80:
        return round(max(d, (0.75 * a) + (0.25 * d)), 4)

    # AI cannot create a strong match from a weak/no-confidence judgment.
    if relationship == "no_evidence" or confidence < 0.45:
        return d

    if d > 0:
        return round(max(d, (0.65 * a) + (0.35 * d)), 4)

    # For previously unseen semantic matches, require substantial AI evidence.
    if a >= 0.80 and confidence >= 0.70:
        return round(a * 0.90, 4)

    if a >= 0.55 and confidence >= 0.60:
        return round(a * 0.75, 4)

    return d


def _recompute_hybrid_scoring(details):
    """Calculate the final score from enriched evidence, not from AI opinion."""
    matched = []
    partial = []
    missing = []

    core_total = core_achieved = 0.0
    supporting_total = supporting_achieved = 0.0
    technical_total = technical_achieved = 0.0
    responsibility_total = responsibility_achieved = 0.0
    professional_total = professional_achieved = 0.0

    for item in details:
        weight = float(item.get("effective_weight", item.get("weight", 1)) or 1)
        score = max(0.0, min(1.0, float(item.get("match_score", 0) or 0)))
        contribution = weight * score

        if item.get("tier") == "Core":
            core_total += weight
            core_achieved += contribution
        else:
            supporting_total += weight
            supporting_achieved += contribution

        dimension = item.get("dimension") or item.get("type")
        item_type = item.get("type")
        # A technical requirement can live inside a role-responsibility section.
        # Keep the two concepts separate: type answers "what kind of requirement?"
        # while dimension answers "where in the JD did it appear?".
        if item_type == "Technical" or dimension == "Technical":
            technical_total += weight
            technical_achieved += contribution
        if dimension == "Responsibility":
            responsibility_total += weight
            responsibility_achieved += contribution
        if item_type == "Professional" or dimension == "Professional":
            professional_total += weight
            professional_achieved += contribution

        if score >= 0.80:
            item["match_level"] = item.get("match_level") or "Strong"
            matched.append(item)
        elif score > 0:
            item["match_level"] = item.get("match_level") or "Related"
            partial.append(item)
        else:
            item["match_level"] = "Missing"
            missing.append(item)

    core_score = (core_achieved / core_total * 100) if core_total else 0.0
    supporting_score = (supporting_achieved / supporting_total * 100) if supporting_total else 0.0

    if core_total and supporting_total:
        final_score = core_score * 0.85 + supporting_score * 0.15
    elif core_total:
        final_score = core_score
    else:
        final_score = supporting_score

    technical_fit = (technical_achieved / technical_total * 100) if technical_total else 0.0
    responsibility_fit = (responsibility_achieved / responsibility_total * 100) if responsibility_total else 0.0
    professional_fit = (professional_achieved / professional_total * 100) if professional_total else 0.0

    coverage = (
        (len(matched) + len(partial) * 0.5) / len(details) * 100
        if details else 0.0
    )

    return {
        "matched": matched,
        "partial": partial,
        "missing": missing,
        "match_percentage": round(final_score, 2),
        "skill_coverage": round(coverage, 2),
        "matched_weight": round(core_achieved + supporting_achieved, 2),
        "total_weight": round(core_total + supporting_total, 2),
        "core_score": round(core_score, 2),
        "supporting_score": round(supporting_score, 2),
        "technical_fit": round(technical_fit, 2),
        "responsibility_fit": round(responsibility_fit, 2),
        "professional_fit": round(professional_fit, 2),
    }


def _ai_enabled():
    return (
        os.environ.get("JOBMATCH_AI_ENABLED", "1") != "0"
        and bool(os.environ.get("OPENAI_API_KEY"))
        and analyze_with_ai is not None
    )


def analyze_resume(resume_text, job_description):
    if not (resume_text or "").strip():
        return None, "Resume text could not be extracted."
    if not (job_description or "").strip():
        return None, "Job description text could not be extracted."

    requirements = extract_requirements(job_description)
    if not requirements:
        return None, "No meaningful requirements could be identified in this job description."

    # --------------------------------------------------------
    # Deterministic baseline
    # --------------------------------------------------------
    baseline = score_requirements(resume_text, requirements)
    details = baseline["matched"] + baseline["partial"] + baseline["missing"]
    details.sort(
        key=lambda x: (
            0 if x.get("tier") == "Core" else 1,
            0 if x.get("type") == "Technical" else 1,
            -float(x.get("effective_weight", x.get("weight", 0))),
        )
    )

    ai_result = {
        "enabled": False,
        "analyses": [],
        "summary": {},
    }

    # --------------------------------------------------------
    # AI semantic evidence layer
    # --------------------------------------------------------
    if _ai_enabled():
        try:
            ai_result = analyze_with_ai(requirements, resume_text)
        except Exception as exc:
            ai_result = {
                "enabled": False,
                "analyses": [],
                "summary": {},
                "error": str(exc),
            }

    ai_map = {
        int(item.get("requirement_index")): item
        for item in ai_result.get("analyses", [])
        if isinstance(item, dict) and str(item.get("requirement_index", "")).isdigit()
    }

    requirement_by_skill = {
        req.get("skill"): i
        for i, req in enumerate(requirements)
    }

    # Match AI judgments back to requirement details by requirement index.
    for detail in details:
        idx = requirement_by_skill.get(detail.get("skill"))
        ai_item = ai_map.get(idx)
        deterministic_score = float(detail.get("match_score", 0) or 0)
        final_evidence = _hybrid_evidence_score(deterministic_score, ai_item)

        if ai_item:
            detail["deterministic_score"] = round(deterministic_score, 4)
            detail["ai_score"] = round(float(ai_item.get("evidence_strength", 0) or 0), 4)
            detail["ai_confidence"] = round(float(ai_item.get("confidence", 0) or 0), 4)
            detail["ai_relationship"] = ai_item.get("relationship", "no_evidence")
            detail["ai_evidence"] = ai_item.get("evidence_text", "")
            detail["ai_evidence_section"] = ai_item.get("evidence_section", "")
            detail["ai_reason"] = ai_item.get("reason", "")

            # AI is allowed to improve interpretation, not to invent resume text.
            if final_evidence > deterministic_score:
                detail["evidence"] = ai_item.get("reason") or detail.get("evidence", "")

            detail["match_score"] = final_evidence
            if ai_item.get("relationship") == "direct" and final_evidence >= 0.80:
                detail["match_level"] = "Strong"
            elif ai_item.get("relationship") in {"strong_related", "weak_related"} and final_evidence > 0:
                detail["match_level"] = "Related"
            elif final_evidence > 0:
                detail["match_level"] = "Mentioned"
            else:
                detail["match_level"] = "Missing"

    hybrid = _recompute_hybrid_scoring(details)
    matched = hybrid["matched"]
    partial = hybrid["partial"]
    missing = hybrid["missing"]

    technical_details = [x for x in details if x.get("type") == "Technical"]
    technical_missing = [x for x in technical_details if x.get("match_score", 0) == 0]
    technical_partial = [x for x in technical_details if 0 < x.get("match_score", 0) < 0.8]
    technical_matched = [x for x in technical_details if x.get("match_score", 0) >= 0.8]
    responsibility_details = [x for x in details if x.get("dimension") == "Responsibility" or x.get("type") == "Responsibility"]
    professional_details = [x for x in details if x.get("dimension") == "Professional" or x.get("type") == "Professional"]

    eligibility = assess_eligibility(resume_text, job_description)
    confidence = calculate_confidence(resume_text, job_description, requirements, details)

    # AI evidence quality contributes to confidence, but never overrides the
    # deterministic confidence calculation.
    if ai_result.get("enabled") and ai_result.get("analyses"):
        ai_confidences = [
            float(x.get("confidence", 0) or 0)
            for x in ai_result["analyses"]
        ]
        if ai_confidences:
            ai_conf = sum(ai_confidences) / len(ai_confidences) * 100
            confidence = round((float(confidence) * 0.55) + (ai_conf * 0.45), 2)

    recommendations = build_recommendations(
        [x for x in missing if x.get("type") in {"Technical", "Responsibility"}],
        [x for x in partial if x.get("type") in {"Technical", "Responsibility"}],
    )
    learn = skills_to_learn(technical_missing, technical_partial)
    projects = calculate_project_alignment(resume_text, requirements)
    learned = learned_skills(resume_text, requirements)

    why_not = _why_not_100(details)
    if technical_missing:
        top = [x.get("skill") for x in technical_missing[:6]]
        why_summary = "The score is below 100% because the resume provides no evidence for: " + ", ".join(top) + "."
    elif technical_partial:
        top = [x.get("skill") for x in technical_partial[:6]]
        why_summary = "The score is below 100% because these requirements have only partial or related evidence: " + ", ".join(top) + "."
    else:
        why_summary = "The detected technical requirements are strongly covered; remaining differences are mainly responsibility/professional evidence strength."

    # Build a clean list of AI evidence records for the UI/debugging layer.
    ai_evidence = []
    for item in details:
        if "ai_score" in item:
            ai_evidence.append({
                "skill": item.get("skill"),
                "score": item.get("ai_score", 0),
                "confidence": item.get("ai_confidence", 0),
                "relationship": item.get("ai_relationship", "no_evidence"),
                "evidence": item.get("ai_evidence", ""),
                "section": item.get("ai_evidence_section", ""),
                "reason": item.get("ai_reason", ""),
            })

    result = {
        "resume_skills": baseline.get("resume_skills", []),
        "job_skills": [x["skill"] for x in requirements],
        "matched_skills": [x["skill"] for x in technical_matched],
        "partial_skills": [x["skill"] for x in technical_partial],
        "missing_skills": [x["skill"] for x in technical_missing],
        "match_percentage": hybrid["match_percentage"],
        "skill_coverage": hybrid["skill_coverage"],
        "matched_weight": hybrid["matched_weight"],
        "total_weight": hybrid["total_weight"],
        "core_score": hybrid["core_score"],
        "supporting_score": hybrid["supporting_score"],
        "technical_fit": hybrid["technical_fit"],
        "responsibility_fit": hybrid["responsibility_fit"],
        "professional_fit": hybrid["professional_fit"],
        "fit_band": fit_band(hybrid["match_percentage"]),
        "confidence": confidence,
        "confidence_label": confidence_label(confidence),
        "potential_fit": calculate_potential_fit(requirements, hybrid["match_percentage"], details),
        "eligibility": eligibility,
        "recommendations": recommendations,
        "skills_to_learn": learn,
        "learned_skills": learned,
        "project_alignment": projects,
        "skill_weights": {x["skill"]: x.get("weight", 0) for x in requirements},
        "requirement_details": details,
        "matched_details": matched,
        "partial_details": partial,
        "missing_details": missing,
        "technical_details": technical_details,
        "responsibility_details": responsibility_details,
        "professional_details": professional_details,
        "strong_matches": technical_matched[:15],
        "partial_matches": technical_partial[:15],
        "no_evidence_gaps": technical_missing[:15],
        "why_not_100": why_not,
        "why_not_100_summary": why_summary,
        "ai_enabled": bool(ai_result.get("enabled")),
        "ai_model": ai_result.get("model", ""),
        "ai_summary": ai_result.get("summary", {}),
        "ai_evidence": ai_evidence,
        "ai_error": ai_result.get("error", ""),
        "analysis_version": "hybrid-ai-evidence-engine-v1",
    }
    return result, None


def engine_diagnostics():
    return {
        "skill_database": bool(SKILLS),
        "relationship_graph": bool(SKILL_RELATIONSHIPS),
        "effective_weight": True,
        "pdf_reader": PdfReader is not None,
        "database": True,
        "ai_engine": analyze_with_ai is not None,
        "ai_enabled": _ai_enabled(),
        "ai_model": os.environ.get("JOBMATCH_AI_MODEL", "gpt-5.4-mini"),
        "embedding_model": os.environ.get("JOBMATCH_EMBEDDING_MODEL", "text-embedding-3-small"),
        "analysis_version": "hybrid-ai-evidence-engine-v1",
    }


# ============================================================
# AI-FIRST ANALYSIS (v3)
# ============================================================
# The AI interprets the entire JD + resume. The deterministic layer below only
# converts the AI's structured judgments into stable arithmetic/UI fields.
# ============================================================

try:
    from ai_engine import analyze_documents
except Exception:
    analyze_documents = None


def _ai_score_value(item):
    """Normalize AI evidence into a stable 0..1 scoring value."""
    try:
        value = max(0.0, min(1.0, float(item.get("evidence_strength", 0) or 0)))
    except Exception:
        value = 0.0
    assessment = item.get("assessment", "missing")
    if assessment == "missing" or assessment == "not_applicable":
        return 0.0
    if assessment == "strong":
        return max(0.80, value)
    if assessment == "partial":
        return min(0.79, max(0.25, value))
    return value


def _ai_requirement_weight(item):
    """Importance weight. This is arithmetic only; the AI decides importance."""
    importance = item.get("importance", "supporting")
    category = item.get("category", "technical")
    if importance == "mandatory":
        base = 1.0
    elif importance == "supporting":
        base = 0.40
    else:  # bonus / differentiator
        base = 0.20
    if category == "responsibility":
        base *= 0.95
    elif category == "professional":
        base *= 0.75
    elif category == "differentiator":
        base *= 0.60
    return round(base, 3)


def _ai_category_scores(details):
    categories = ["technical", "responsibility", "professional", "differentiator"]
    scores = {}
    for category in categories:
        rows = [x for x in details if x.get("ai_category") == category and x.get("scoring_relevance") == "score"]
        if not rows:
            scores[category] = None
            continue
        total = sum(float(x.get("category_weight", 1.0)) for x in rows)
        achieved = sum(float(x.get("category_weight", 1.0)) * float(x.get("match_score", 0.0)) for x in rows)
        scores[category] = round((achieved / total) * 100, 2) if total else 0.0
    return scores


def _ai_overall_score(category_scores):
    """Weighted overall fit; missing categories are redistributed, never scored as zero."""
    configured = {
        "technical": 0.55,
        "responsibility": 0.25,
        "professional": 0.15,
        "differentiator": 0.05,
    }
    present = [(k, v) for k, v in category_scores.items() if v is not None]
    if not present:
        return 0.0
    total_share = sum(configured[k] for k, _ in present)
    return round(sum(configured[k] * float(v) for k, v in present) / total_share, 2)


def _make_ai_detail(req):
    category = req.get("category", "technical")
    importance = req.get("importance", "supporting")
    tier = "Core" if importance == "mandatory" else ("Supporting" if importance == "supporting" else "Bonus")
    score = _ai_score_value(req)
    weight = _ai_requirement_weight(req)
    category_weight = 1.0 if importance == "mandatory" else (0.55 if importance == "supporting" else 0.30)
    detail = {
        "skill": req.get("name", "").strip(),
        "category": req.get("name", "").strip(),
        "tier": tier,
        "importance": importance,
        "weight": weight,
        "effective_weight": weight,
        "type": {
            "technical": "Technical",
            "responsibility": "Responsibility",
            "professional": "Professional",
            "differentiator": "Differentiator",
            "eligibility": "Eligibility",
        }.get(category, "Technical"),
        "dimension": {
            "technical": "Technical",
            "responsibility": "Responsibility",
            "professional": "Professional",
            "differentiator": "Differentiator",
            "eligibility": "Eligibility",
        }.get(category, "Technical"),
        "section": req.get("source_section", ""),
        "source_section": req.get("source_section", ""),
        "jd_evidence": req.get("jd_text", ""),
        "position": 0,
        "match_score": round(score, 4),
        "match_level": (
            "Strong" if req.get("assessment") == "strong" else
            "Related" if req.get("assessment") == "partial" else
            "Missing" if req.get("assessment") == "missing" else
            "Not Applicable"
        ),
        "evidence": req.get("reason", ""),
        "evidence_source": req.get("evidence_section", "") or "Not evidenced",
        "related_skill": "",
        "weighted_contribution": round(weight * score, 4),
        "ai_score": round(score, 4),
        "ai_confidence": round(float(req.get("confidence", 0) or 0), 4),
        "ai_relationship": req.get("relationship", "none"),
        "ai_evidence": req.get("evidence_text", ""),
        "ai_evidence_section": req.get("evidence_section", ""),
        "ai_reason": req.get("reason", ""),
        "ai_category": category,
        "scoring_relevance": req.get("scoring_relevance", "score"),
        "category_weight": category_weight,
    }
    return detail


def _ai_recommendations(details):
    output = []
    for item in details:
        if item.get("scoring_relevance") != "score":
            continue
        score = float(item.get("match_score", 0) or 0)
        if score >= 0.8:
            continue
        if item.get("tier") == "Core":
            priority = "High"
        elif item.get("tier") == "Supporting":
            priority = "Medium"
        else:
            priority = "Low"
        output.append({
            "skill": item.get("skill"),
            "priority": priority,
            "category": item.get("type"),
            "reason": item.get("ai_reason") or "No direct evidence was found in the resume."
        })
    return output


def _ai_why_not_100(details):
    gaps = [x for x in details if x.get("scoring_relevance") == "score" and float(x.get("match_score", 0) or 0) < 1.0]
    gaps.sort(key=lambda x: (-float(x.get("effective_weight", 0)), float(x.get("match_score", 0))))
    return [{
        "skill": x.get("skill"),
        "tier": x.get("tier"),
        "type": x.get("type"),
        "reason": x.get("ai_reason") or "The requirement is not fully evidenced.",
        "weight": x.get("effective_weight", 0),
    } for x in gaps[:12]]


def analyze_resume(resume_text, job_description):
    if not (resume_text or "").strip():
        return None, "Resume text could not be extracted."
    if not (job_description or "").strip():
        return None, "Job description text could not be extracted."

    if analyze_documents is None or not os.environ.get("OPENAI_API_KEY") or os.environ.get("JOBMATCH_AI_ENABLED", "1") == "0":
        # Safe fallback for offline use. The normal product path is AI-first.
        requirements = extract_requirements(job_description)
        if not requirements:
            return None, "No meaningful requirements could be identified in this job description."
        scoring = score_requirements(resume_text, requirements)
        details = scoring["matched"] + scoring["partial"] + scoring["missing"]
        return {
            "resume_skills": scoring.get("resume_skills", []),
            "job_skills": [x.get("skill") for x in requirements],
            "matched_skills": [x.get("skill") for x in scoring["matched"]],
            "partial_skills": [x.get("skill") for x in scoring["partial"]],
            "missing_skills": [x.get("skill") for x in scoring["missing"]],
            "match_percentage": scoring.get("match_percentage", 0),
            "skill_coverage": scoring.get("skill_coverage", 0),
            "matched_weight": scoring.get("matched_weight", 0),
            "total_weight": scoring.get("total_weight", 0),
            "core_score": scoring.get("core_score", 0),
            "supporting_score": scoring.get("supporting_score", 0),
            "technical_fit": scoring.get("technical_fit", 0),
            "responsibility_fit": scoring.get("responsibility_fit", 0),
            "professional_fit": scoring.get("professional_fit", 0),
            "fit_band": fit_band(scoring.get("match_percentage", 0)),
            "confidence": calculate_confidence(resume_text, job_description, requirements, details),
            "confidence_label": "Fallback",
            "potential_fit": 100.0,
            "eligibility": assess_eligibility(resume_text, job_description),
            "recommendations": build_recommendations(scoring["missing"], scoring["partial"]),
            "skills_to_learn": skills_to_learn(scoring["missing"], scoring["partial"]),
            "learned_skills": learned_skills(resume_text, requirements),
            "project_alignment": calculate_project_alignment(resume_text, requirements),
            "skill_weights": {x["skill"]: x.get("weight", 0) for x in requirements},
            "requirement_details": details,
            "matched_details": scoring["matched"],
            "partial_details": scoring["partial"],
            "missing_details": scoring["missing"],
            "technical_details": [x for x in details if x.get("type") == "Technical"],
            "responsibility_details": [x for x in details if x.get("dimension") == "Responsibility"],
            "professional_details": [x for x in details if x.get("dimension") == "Professional"],
            "strong_matches": scoring["matched"][:15],
            "partial_matches": scoring["partial"][:15],
            "no_evidence_gaps": scoring["missing"][:15],
            "why_not_100": _why_not_100(details),
            "why_not_100_summary": "AI-first analysis is disabled; showing the deterministic fallback.",
            "ai_enabled": False,
            "ai_model": "",
            "ai_summary": {},
            "ai_evidence": [],
            "ai_error": "AI engine disabled or unavailable.",
            "analysis_version": "ai-first-jobmatch-v3-fallback",
        }, None

    ai = analyze_documents(resume_text, job_description)
    if not ai.get("enabled"):
        return None, "AI analysis failed: " + str(ai.get("error", "Unknown AI error"))

    details = [_make_ai_detail(req) for req in ai.get("requirements", []) if req.get("scoring_relevance") != "ignore" and req.get("category") != "eligibility"]
    details = [x for x in details if x.get("skill")]

    # Stable order: mandatory first, then supporting, then bonus; within each,
    # keep the AI's document order.
    importance_order = {"Core": 0, "Supporting": 1, "Bonus": 2}
    for idx, item in enumerate(details):
        item["position"] = idx
    details.sort(key=lambda x: (importance_order.get(x.get("tier"), 3), x.get("position", 0)))

    category_scores = _ai_category_scores(details)
    overall = _ai_overall_score(category_scores)

    scored = [x for x in details if x.get("scoring_relevance") == "score"]
    matched = [x for x in scored if x.get("match_score", 0) >= 0.8]
    partial = [x for x in scored if 0 < x.get("match_score", 0) < 0.8]
    missing = [x for x in scored if x.get("match_score", 0) == 0]
    technical_details = [x for x in details if x.get("ai_category") == "technical" and x.get("scoring_relevance") == "score"]
    responsibility_details = [x for x in details if x.get("ai_category") == "responsibility" and x.get("scoring_relevance") == "score"]
    professional_details = [x for x in details if x.get("ai_category") == "professional" and x.get("scoring_relevance") == "score"]
    differentiator_details = [x for x in details if x.get("ai_category") == "differentiator" and x.get("scoring_relevance") == "score"]

    ai_conf = float(ai.get("analysis_confidence", 0) or 0) * 100
    evidence_conf = (sum(float(x.get("ai_confidence", 0) or 0) for x in scored) / len(scored) * 100) if scored else 0
    confidence = round((ai_conf * 0.65) + (evidence_conf * 0.35), 2) if scored else round(ai_conf, 2)

    eligibility_rows = ai.get("eligibility_checks", [])
    hard_fails = [x for x in eligibility_rows if x.get("status") == "fail"]
    unknowns = [x for x in eligibility_rows if x.get("status") == "unknown"]
    if hard_fails:
        eligibility_status = "Not Eligible"
    elif unknowns:
        eligibility_status = "Needs Verification"
    elif eligibility_rows:
        eligibility_status = "Eligible"
    else:
        eligibility_status = "Not Specified"
    eligibility = {
        "status": eligibility_status,
        "checks": eligibility_rows,
        "verified_count": sum(x.get("status") == "pass" for x in eligibility_rows),
        "unknown_count": len(unknowns),
        "failed_count": len(hard_fails),
    }

    recommendations = _ai_recommendations(details)
    learn = [
        {
            "skill": x.get("skill"),
            "category": x.get("type"),
            "priority": "High" if x.get("tier") == "Core" else ("Medium" if x.get("tier") == "Supporting" else "Low"),
            "reason": x.get("ai_reason") or "Not fully demonstrated in the resume."
        }
        for x in missing + partial
        if x.get("ai_category") in {"technical", "responsibility"}
    ][:15]

    resume_skills = sorted(_resume_skill_set(resume_text))
    ai_evidence = [
        {
            "skill": x.get("skill"),
            "score": x.get("ai_score", 0),
            "confidence": x.get("ai_confidence", 0),
            "relationship": x.get("ai_relationship", "none"),
            "evidence": x.get("ai_evidence", ""),
            "section": x.get("ai_evidence_section", ""),
            "reason": x.get("ai_reason", ""),
        }
        for x in details
    ]

    matched_weight = round(sum(float(x.get("effective_weight", 0)) * float(x.get("match_score", 0)) for x in scored), 2)
    total_weight = round(sum(float(x.get("effective_weight", 0)) for x in scored), 2)
    coverage = round(((len(matched) + 0.5 * len(partial)) / len(scored) * 100), 2) if scored else 0.0

    why = _ai_why_not_100(details)
    why_summary = ai.get("overall_reason", "The fit is based on the evidence identified in the resume against the meaningful job criteria.")

    return {
        "resume_skills": resume_skills,
        "job_skills": [x.get("skill") for x in details],
        "matched_skills": [x.get("skill") for x in technical_details if x.get("match_score", 0) >= 0.8],
        "partial_skills": [x.get("skill") for x in technical_details if 0 < x.get("match_score", 0) < 0.8],
        "missing_skills": [x.get("skill") for x in technical_details if x.get("match_score", 0) == 0],
        "match_percentage": overall,
        "skill_coverage": coverage,
        "matched_weight": matched_weight,
        "total_weight": total_weight,
        "core_score": round(sum(x.get("match_score", 0) for x in scored if x.get("tier") == "Core") / max(1, sum(1 for x in scored if x.get("tier") == "Core")) * 100, 2) if any(x.get("tier") == "Core" for x in scored) else 0.0,
        "supporting_score": round(sum(x.get("match_score", 0) for x in scored if x.get("tier") != "Core") / max(1, sum(1 for x in scored if x.get("tier") != "Core")) * 100, 2) if any(x.get("tier") != "Core" for x in scored) else 0.0,
        "technical_fit": category_scores.get("technical") or 0.0,
        "responsibility_fit": category_scores.get("responsibility") or 0.0,
        "professional_fit": category_scores.get("professional") or 0.0,
        "differentiator_fit": category_scores.get("differentiator"),
        "fit_band": fit_band(overall),
        "confidence": confidence,
        "confidence_label": confidence_label(confidence),
        "potential_fit": 100.0,
        "eligibility": eligibility,
        "recommendations": recommendations,
        "skills_to_learn": learn,
        "learned_skills": [x for x in matched + partial if x.get("ai_category") == "technical"][:20],
        "project_alignment": [
            {"skill": x.get("skill"), "category": x.get("category"), "evidence": x.get("ai_evidence")}
            for x in matched + partial
            if x.get("ai_evidence_section", "").lower() == "projects"
        ],
        "skill_weights": {x.get("skill"): x.get("weight", 0) for x in details},
        "requirement_details": details,
        "matched_details": matched,
        "partial_details": partial,
        "missing_details": missing,
        "technical_details": technical_details,
        "responsibility_details": responsibility_details,
        "professional_details": professional_details,
        "differentiator_details": differentiator_details,
        "strong_matches": [x for x in technical_details if x.get("match_score", 0) >= 0.8][:15],
        "partial_matches": [x for x in technical_details if 0 < x.get("match_score", 0) < 0.8][:15],
        "no_evidence_gaps": [x for x in technical_details if x.get("match_score", 0) == 0][:15],
        "why_not_100": why,
        "why_not_100_summary": why_summary,
        "ai_enabled": True,
        "ai_model": ai.get("model", ""),
        "ai_summary": {
            "role_title": ai.get("role_title", ""),
            "role_summary": ai.get("role_summary", ""),
            "major_strengths": ai.get("major_strengths", []),
            "major_gaps": ai.get("major_gaps", []),
            "cautions": ai.get("cautions", []),
            "document_quality": ai.get("document_quality", {}),
            "analysis_confidence": ai.get("analysis_confidence", 0),
            "category_scores": category_scores,
        },
        "ai_evidence": ai_evidence,
        "ai_error": "",
        "analysis_version": "ai-first-jobmatch-v3",
    }, None

# ============================================================
# STARTUP
# ============================================================

init_db()

if __name__ == "__main__":
    app.run(
        host=os.environ.get("JOBMATCH_HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG", "1") == "1",
    )
