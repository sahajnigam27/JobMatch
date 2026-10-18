# JobMatch — Project Analysis Report

## 1. Executive Summary

JobMatch is a resume-to-job matching web application developed to solve a practical problem: understanding how well a candidate's resume aligns with a specific job description.

The application goes beyond a simple keyword counter. It extracts meaningful requirements, evaluates resume evidence, applies weighted scoring, separates strong/partial/missing evidence, explains gaps, and provides recommendations.

The final portfolio version is intentionally frozen at the stable working implementation and does not require a paid AI API.

---

## 2. Problem Statement

Candidates often compare a resume and a job description manually. This makes it difficult to determine:

- which requirements are actually covered
- which skills are only partially evidenced
- which requirements have no evidence
- which gaps matter most
- why a resume receives a particular match score
- what should be improved before applying

JobMatch addresses these issues through an explainable web-based analysis workflow.

---

## 3. Objectives

The project was designed to:

1. Accept resumes and job descriptions in PDF/text form.
2. Extract usable text from uploaded documents.
3. Identify technical requirements and resume skills.
4. Compare requirements against resume evidence.
5. Use weighted scoring instead of simple keyword counting.
6. Distinguish strong, related/partial, and missing evidence.
7. Provide recommendations and skills-to-learn.
8. Show project alignment with job requirements.
9. Maintain analysis history using SQLite.
10. Present the results through a professional web interface.

---

## 4. Technology Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Web framework | Flask |
| PDF extraction | pypdf |
| Database | SQLite |
| Template engine | Jinja2 |
| Frontend | HTML, CSS, JavaScript |
| Text processing | Regular expressions, normalization |
| Data representation | JSON |
| Development environment | VS Code |

---

## 5. System Architecture

```text
                 ┌──────────────────────┐
                 │ Resume PDF / Text    │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Document Extraction   │
                 │ & Normalization       │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Resume Evidence      │
                 │ Analysis             │
                 └──────────┬───────────┘
                            │
                            │
                 ┌──────────▼───────────┐
                 │ Requirement Analysis │
                 │ from Job Description │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Requirement Matching │
                 │ & Weighted Scoring   │
                 └──────────┬───────────┘
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
        Strong Match    Partial/Related   Missing
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                 ┌──────────────────────┐
                 │ Recommendations &   │
                 │ Skill Gaps           │
                 └──────────┬───────────┘
                            ▼
                 ┌──────────────────────┐
                 │ SQLite Analysis      │
                 │ History              │
                 └──────────────────────┘
```

---

## 6. Functional Modules

### 6.1 Document input

The application supports resume and job-description input through PDF uploads and text input.

### 6.2 PDF text extraction

Uploaded PDFs are processed using `pypdf` so that the application can work with document text without requiring manual copying.

### 6.3 Skill extraction

The application normalizes text and identifies supported technical skills and technology aliases.

Examples include:

- Python
- Java
- C++
- JavaScript
- Flask
- Django
- REST APIs
- SQL
- MySQL
- PostgreSQL
- MongoDB
- SQLite
- Pandas
- NumPy
- Scikit-learn
- Machine Learning
- NLP
- Git/GitHub
- Docker
- Kubernetes
- AWS/Azure/GCP
- DSA
- OOP
- Testing

The dictionary is used as a deterministic baseline rather than pretending that every textual mention represents professional expertise.

### 6.4 Requirement classification

Job requirements are categorized and weighted so that the final result is not equivalent to counting all keywords equally.

The implementation distinguishes higher-priority/core requirements from supporting requirements and handles professional/responsibility dimensions separately.

### 6.5 Evidence evaluation

Evidence strength depends on context.

A concrete internship or project demonstration is stronger evidence than merely listing a technology in a skills section.

The system therefore attempts to answer:

> "Where is this requirement evidenced in the resume?"

rather than only:

> "Does this word appear?"

### 6.6 Weighted scoring

The scoring layer calculates:

- overall match percentage
- technical fit
- responsibility fit
- professional fit
- skill coverage
- core score
- supporting score
- matched weight
- total requirement weight

This makes the result more explainable than a simple percentage based on word overlap.

### 6.7 Recommendations

The application converts missing or partial requirements into recommendations and skills-to-learn.

### 6.8 Project alignment

The application also evaluates how the candidate's projects relate to detected job requirements.

### 6.9 Analysis history

SQLite stores previous analyses so that users can return to earlier results.

---

## 7. User Interface

The final UI was designed as a professional dark SaaS-style application.

Major screens include:

### Analyzer

- JobMatch branding
- Resume input/upload
- Job description input/upload
- Analyze action
- Match result visualization
- Skill coverage
- Matched and missing skill chips
- Recommendations

### History

- Previous analysis cards
- Match score
- Coverage information
- Date/time
- Details navigation

### Details

- Overall score
- Match metrics
- Strong matches
- Partial/related evidence
- Missing requirements
- Recommendations
- Requirement-level explanations

---

## 8. Data Flow

```text
Input
  ↓
PDF/Text extraction
  ↓
Text normalization
  ↓
Resume skill/evidence extraction
  ↓
Job requirement extraction
  ↓
Requirement classification
  ↓
Evidence comparison
  ↓
Weighted score calculation
  ↓
Gap analysis
  ↓
Recommendations
  ↓
Persist result in SQLite
  ↓
Render result in UI
```

---

## 9. Database Design

The application uses SQLite because the project is intended as a lightweight local web application.

### Analysis history

The analysis table stores information such as:

- resume skills
- job skills
- matched skills
- missing skills
- match percentage
- skill coverage
- matched weight
- total weight
- creation timestamp
- requirement details
- core score
- supporting score

### Active analysis state

A separate state table supports multi-step analysis workflows and stores the active resume/job-description context.

---

## 10. Engineering Decisions

### Why Flask?

Flask provides a lightweight backend suitable for demonstrating:

- routing
- request handling
- server-side rendering
- application logic
- database integration

### Why SQLite?

SQLite provides persistent storage without requiring a separate database server. It keeps the project easy to run and demonstrate.

### Why deterministic scoring?

For the portfolio release, deterministic scoring provides reproducibility and explainability. The same input produces a predictable analysis without requiring external API access.

### Why weighted requirements?

Not every job requirement has equal importance. A core programming requirement should have more influence than a low-priority supporting criterion.

---

## 11. Testing Performed

The project was iteratively tested during development for:

- Flask application startup
- PDF extraction
- skill extraction
- requirement extraction
- requirement weighting
- match classification
- missing/partial/strong result generation
- SQLite history
- details-page JSON handling
- responsive UI behavior
- multiple job/resume scenarios

The project was also tested against a realistic Software Engineer job description to identify weaknesses in literal keyword matching and improve the requirement/evidence model.

---

## 12. Important Lessons From Development

### Lesson 1 — Keyword presence is not expertise

A technology appearing in a resume does not automatically prove professional experience.

### Lesson 2 — Evidence context matters

"Python" in a Skills section is weaker evidence than Python used in an internship project.

### Lesson 3 — Missing evidence is not proof of inability

The correct interpretation is:

> "No evidence found in the submitted resume."

It should not claim that the candidate does not know the skill.

### Lesson 4 — Job descriptions contain noise

Marketing statements, metadata, cohort identifiers and general company language should not automatically become hard technical requirements.

### Lesson 5 — Explainability matters

A useful matching system should explain why a requirement was considered strong, related, or missing.

---

## 13. Limitations

The current release has important limitations:

1. It is not a hiring prediction system.
2. It cannot determine whether a candidate will be selected.
3. Its semantic understanding is limited compared with a large language model.
4. Resume formatting can affect extracted text quality.
5. A deterministic skill taxonomy cannot cover every technology or phrase in every job description.
6. The score represents resume/JD alignment, not real-world engineering ability.
7. Professional traits such as communication and leadership are difficult to prove from a one-page resume.
8. The application is designed primarily as a portfolio/local application rather than a production multi-user service.

These limitations are intentional and should not be hidden when presenting the project.

---

## 14. AI Exploration

During development, an experimental AI semantic layer was explored to improve contextual evidence interpretation.

The intended architecture was:

```text
Resume + JD
    ↓
AI semantic interpretation
    ↓
Structured requirement/evidence output
    ↓
Python scoring layer
    ↓
Final explainable analysis
```

The experiment was not made a dependency of the final portfolio release because it required external API credits.

This is a useful future direction, but the current project remains fully demonstrable without an API key.

---

## 15. Security and Repository Hygiene

The GitHub repository must never contain:

- API keys
- `.env` files containing secrets
- virtual environments
- generated Python cache files
- local SQLite databases containing user data

Recommended `.gitignore` entries:

```gitignore
venv/
.venv/
__pycache__/
*.py[cod]
.env
.env.*
jobmatch.db
.DS_Store
```

---

## 16. Portfolio Value

JobMatch demonstrates practical evidence of:

- Python development
- Flask backend development
- REST/web application concepts
- PDF processing
- text processing
- SQL/SQLite
- data modeling
- algorithmic scoring
- requirement analysis
- frontend integration
- debugging
- explainable application design

For a fresher software/backend role, the strongest part of the project is not the visual design alone. It is the attempt to build a complete workflow from unstructured documents to structured analysis and persistent results.

---

## 17. Final Project Status

**Status: COMPLETE / PORTFOLIO READY**

The project should now be frozen.

Further enhancements are not required for the current resume.

The recommended next step is to publish the stable version to GitHub with a clean README and then move to the next project.

---

## 18. Suggested GitHub Description

> A Flask-based resume intelligence application that compares resumes with job descriptions using weighted requirement matching, evidence analysis, skill-gap detection, recommendations, and SQLite-backed analysis history.

## 19. Suggested Resume Bullet

> Built a Flask-based resume and job skill matcher that extracts requirements from job descriptions, performs weighted evidence-based matching, identifies skill gaps, generates recommendations, and stores analysis history using SQLite.
