"""AI-first reasoning engine for JobMatch.

The model is responsible for interpreting the job description and resume:
- identify meaningful job requirements and ignore metadata/marketing text
- classify requirements by dimension and importance
- find and judge resume evidence
- explain matches, partial matches, and gaps

Python remains responsible for arithmetic/scoring so the final percentage is
stable and auditable rather than being a number invented by the model.
"""

import json
import os
from typing import Any, Dict

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

AI_MODEL = os.environ.get("JOBMATCH_AI_MODEL", "gpt-5.4-mini")

SCHEMA = {
    "type": "object",
    "properties": {
        "role_title": {"type": "string"},
        "role_summary": {"type": "string"},
        "document_quality": {
            "type": "object",
            "properties": {
                "jd_quality": {"type": "number"},
                "resume_quality": {"type": "number"},
                "notes": {"type": "string"}
            },
            "required": ["jd_quality", "resume_quality", "notes"],
            "additionalProperties": False
        },
        "requirements": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "category": {
                        "type": "string",
                        "enum": ["technical", "responsibility", "professional", "differentiator", "eligibility"]
                    },
                    "importance": {
                        "type": "string",
                        "enum": ["mandatory", "supporting", "bonus"]
                    },
                    "source_section": {"type": "string"},
                    "jd_text": {"type": "string"},
                    "assessment": {
                        "type": "string",
                        "enum": ["strong", "partial", "missing", "not_applicable"]
                    },
                    "relationship": {
                        "type": "string",
                        "enum": ["direct", "semantic", "weak", "none"]
                    },
                    "evidence_strength": {"type": "number"},
                    "confidence": {"type": "number"},
                    "evidence_text": {"type": "string"},
                    "evidence_section": {"type": "string"},
                    "reason": {"type": "string"},
                    "scoring_relevance": {
                        "type": "string",
                        "enum": ["score", "context_only", "ignore"]
                    }
                },
                "required": [
                    "name", "category", "importance", "source_section", "jd_text",
                    "assessment", "relationship", "evidence_strength", "confidence",
                    "evidence_text", "evidence_section", "reason", "scoring_relevance"
                ],
                "additionalProperties": False
            }
        },
        "eligibility_checks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "criterion": {"type": "string"},
                    "status": {"type": "string", "enum": ["pass", "fail", "unknown"]},
                    "evidence": {"type": "string"},
                    "confidence": {"type": "number"}
                },
                "required": ["criterion", "status", "evidence", "confidence"],
                "additionalProperties": False
            }
        },
        "major_strengths": {"type": "array", "items": {"type": "string"}},
        "major_gaps": {"type": "array", "items": {"type": "string"}},
        "cautions": {"type": "array", "items": {"type": "string"}},
        "overall_reason": {"type": "string"},
        "analysis_confidence": {"type": "number"}
    },
    "required": [
        "role_title", "role_summary", "document_quality", "requirements",
        "eligibility_checks", "major_strengths", "major_gaps", "cautions",
        "overall_reason", "analysis_confidence"
    ],
    "additionalProperties": False
}

SYSTEM_PROMPT = r"""
You are the primary intelligence layer of JobMatch, an evidence-based resume-to-job
analysis system. You are not a keyword matcher and you are not a hiring-probability
oracle. Read the ENTIRE job description and ENTIRE resume as documents and reason
about their meaning.

Your job is to do the document interpretation that a careful technical recruiter or
hiring manager would do, while never inventing candidate experience.

EXECUTION ORDER
1. Identify the actual role and summarize what the employer is looking for.
2. Read the JD section-by-section and extract only meaningful evaluation criteria.
3. Distinguish actual requirements/responsibilities from company marketing, slogans,
   program metadata, cohort codes, legal disclaimers, boilerplate and examples.
4. Classify each meaningful criterion as technical, responsibility, professional,
   differentiator, or eligibility.
5. Classify importance:
   - mandatory: materially required for the role or explicitly stated as required/expected
   - supporting: useful/important but not a hard technical gate
   - bonus: differentiator, preferred evidence, values, or extra signal
6. Read the resume and find the strongest evidence for EACH criterion.
7. Judge evidence semantically. Do not require exact keyword overlap.
8. Distinguish:
   - direct: the resume explicitly demonstrates the capability through work/projects
   - semantic: the resume demonstrates a genuinely related capability, but not the exact requirement
   - weak: only indirect or thin evidence
   - none: no defensible evidence
9. Do not treat absence as proof that the candidate cannot do something. Say "not evidenced".
10. Never upgrade a related technology into an exact technology without evidence.
11. A skills-list mention is weaker than concrete internship/project evidence.
12. Education, coursework, certifications and activities can be evidence where relevant,
    but do not silently turn them into professional experience.
13. A project can be strong evidence when it actually demonstrates the requirement.
14. If a phrase appears only as a program/cohort identifier, it is NOT a skill requirement.
    Example: "spark_<init>" is metadata unless the JD separately requires Apache Spark.
15. Do not infer a technology from a substring inside an identifier, URL, email, company
    name, project code, or program name.
16. Section semantics matter. A "What Will Differentiate You" section is bonus/differentiator
    evidence, not a mandatory requirement. A "What We Value" section describes desired traits
    and should normally be supporting/bonus rather than hard technical requirements.
17. A sentence containing several ideas should not automatically become several independent
    hard requirements. Extract a requirement at the level that a recruiter would evaluate.
18. Do not turn every noun into a requirement. "AI-powered solutions" in employer marketing
    is not automatically an AI skill requirement.
19. Ignore company facts, revenue, headcount, culture slogans, Ethisphere claims, legal notices,
    location/travel boilerplate unless they are actual eligibility criteria.
20. If a criterion is only contextual/marketing text, use scoring_relevance=context_only or ignore.
21. Use scoring_relevance=score only for criteria that should affect candidate fit.
22. Keep requirements concise and non-duplicative. Prefer "Software development" over five
    near-duplicate requirements for design/develop/modify/maintain unless the JD clearly treats
    them as distinct competencies.
23. Evidence text must be copied or closely reproduced from the supplied resume. Never invent
    a quote. If no evidence exists, leave evidence_text empty.
24. The candidate's final numeric fit is NOT your job. Return evidence strength and classification;
    Python will calculate the score.
25. Be conservative. When uncertain, use partial/weak or missing and explain why.

SCORING SEMANTICS FOR EVIDENCE STRENGTH
- strong/direct evidence: usually 0.80-1.00
- strong semantic evidence: usually 0.60-0.79
- weak evidence: usually 0.25-0.59
- no evidence: 0.00
Do not use the number to hide uncertainty; confidence is separate.

The final output MUST follow the supplied JSON schema.
"""


def _client():
    if OpenAI is None or not os.environ.get("OPENAI_API_KEY"):
        return None
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def _clamp(value, low=0.0, high=1.0):
    try:
        return max(low, min(high, float(value)))
    except Exception:
        return low


def _clean_result(result: Dict[str, Any]) -> Dict[str, Any]:
    result["analysis_confidence"] = _clamp(result.get("analysis_confidence", 0.0))
    quality = result.get("document_quality", {}) or {}
    quality["jd_quality"] = _clamp(quality.get("jd_quality", 0.0))
    quality["resume_quality"] = _clamp(quality.get("resume_quality", 0.0))
    result["document_quality"] = quality

    cleaned = []
    seen = set()
    for req in result.get("requirements", []):
        name = str(req.get("name", "")).strip()
        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        req["name"] = name
        req["evidence_strength"] = _clamp(req.get("evidence_strength", 0.0))
        req["confidence"] = _clamp(req.get("confidence", 0.0))
        # Enforce logical consistency at the data boundary.
        if req.get("assessment") == "missing":
            req["evidence_strength"] = 0.0
            req["relationship"] = "none"
        elif req.get("assessment") == "strong":
            req["evidence_strength"] = max(req["evidence_strength"], 0.80)
        elif req.get("assessment") == "partial":
            req["evidence_strength"] = min(max(req["evidence_strength"], 0.25), 0.79)
        elif req.get("assessment") == "not_applicable":
            req["evidence_strength"] = 0.0
            req["scoring_relevance"] = "ignore"
        cleaned.append(req)
    result["requirements"] = cleaned
    return result


def analyze_documents(resume_text: str, job_description: str) -> Dict[str, Any]:
    """Perform the complete AI-first interpretation of a resume and JD."""
    client = _client()
    if client is None:
        return {
            "enabled": False,
            "requirements": [],
            "error": "OPENAI_API_KEY or openai package unavailable"
        }

    # Full-document reasoning is intentional here. The model, not a keyword list,
    # decides what matters. The documents are normally far below the model context limit.
    user_payload = {
        "job_description": job_description.strip(),
        "resume": resume_text.strip(),
        "task": "Produce the complete JobMatch analysis. Do not calculate a final percentage."
    }

    try:
        response = client.responses.create(
            model=AI_MODEL,
            reasoning={"effort": os.environ.get("JOBMATCH_REASONING_EFFORT", "medium")},
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "jobmatch_document_analysis",
                    "strict": True,
                    "schema": SCHEMA,
                }
            },
        )
        parsed = json.loads(response.output_text)
        parsed = _clean_result(parsed)
    except Exception as exc:
        return {
            "enabled": False,
            "requirements": [],
            "error": str(exc)
        }

    return {
        "enabled": True,
        "model": AI_MODEL,
        **parsed,
    }


# Backward-compatible alias used by older code paths.
def analyze_with_ai(requirements, resume_text):
    return {
        "enabled": False,
        "analyses": [],
        "summary": {},
        "error": "The AI-first engine now analyzes the full resume and JD together via analyze_documents()."
    }
