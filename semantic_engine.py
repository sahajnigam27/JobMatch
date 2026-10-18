"""JobMatch semantic retrieval layer.

Uses OpenAI embeddings when an API key and SDK are available. It is deliberately
independent of Flask so the core engine can be tested without the web app.
"""

import math
import os
import re
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

EMBEDDING_MODEL = os.environ.get("JOBMATCH_EMBEDDING_MODEL", "text-embedding-3-small")


def _client():
    if OpenAI is None or not os.environ.get("OPENAI_API_KEY"):
        return None
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if not na or not nb:
        return 0.0
    return max(0.0, min(1.0, dot / (na * nb)))


def split_resume_evidence(resume_text: str) -> List[Dict[str, str]]:
    """Create compact, traceable evidence chunks from resume bullets/lines."""
    text = resume_text or ""
    chunks: List[Dict[str, str]] = []
    current_section = "other"

    section_patterns = {
        "summary": re.compile(r"^(summary|profile|professional summary|objective)$", re.I),
        "experience": re.compile(r"^(experience|work experience|internship|internships|professional experience)$", re.I),
        "projects": re.compile(r"^(projects?|personal projects?|academic projects?)$", re.I),
        "skills": re.compile(r"^(technical skills|skills|core skills)$", re.I),
        "education": re.compile(r"^(education|academic background)$", re.I),
        "certifications": re.compile(r"^(certifications?|certificates?)$", re.I),
        "achievements": re.compile(r"^(achievements?|activities?|extracurriculars?|leadership)$", re.I),
    }

    for raw in text.splitlines():
        line = re.sub(r"\s+", " ", raw).strip()
        if not line:
            continue

        matched_section = None
        for section, pattern in section_patterns.items():
            if pattern.match(line):
                matched_section = section
                break
        if matched_section:
            current_section = matched_section
            continue

        # Ignore extremely short decorative lines.
        if len(line) < 12:
            continue

        chunks.append({"section": current_section, "text": line})

    # Add short adjacent pairs so context spanning two resume lines survives.
    enriched = list(chunks)
    for i in range(len(chunks) - 1):
        a, b = chunks[i], chunks[i + 1]
        if a["section"] == b["section"] and len(a["text"]) + len(b["text"]) < 420:
            enriched.append({
                "section": a["section"],
                "text": a["text"] + " " + b["text"],
            })

    # Deduplicate while keeping order.
    seen = set()
    output = []
    for item in enriched:
        key = (item["section"], item["text"].lower())
        if key not in seen:
            seen.add(key)
            output.append(item)
    return output


def _lexical_candidates(requirement: Dict[str, Any], chunks: List[Dict[str, str]], limit: int = 10):
    """Cheap pre-filter so embeddings are not generated for every resume line."""
    req = " ".join([
        str(requirement.get("skill", "")),
        str(requirement.get("type", "")),
        str(requirement.get("jd_evidence", "")),
    ]).lower()
    tokens = set(re.findall(r"[a-z0-9+#.]{3,}", req))

    scored = []
    for chunk in chunks:
        text = chunk["text"].lower()
        overlap = sum(1 for token in tokens if token in text)
        section_bonus = 0.0
        if chunk["section"] in {"experience", "projects"}:
            section_bonus = 0.25
        elif chunk["section"] == "skills":
            section_bonus = 0.10
        scored.append((overlap + section_bonus, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [x[1] for x in scored[:limit]]


def semantic_candidates(requirement: Dict[str, Any], resume_text: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Return semantically similar resume evidence for one requirement."""
    client = _client()
    if client is None:
        return []

    chunks = split_resume_evidence(resume_text)
    if not chunks:
        return []

    candidates = _lexical_candidates(requirement, chunks, limit=12)
    requirement_text = (
        f"Requirement: {requirement.get('skill', '')}\n"
        f"Type: {requirement.get('type', '')}\n"
        f"Importance: {requirement.get('tier', '')}\n"
        f"Job description evidence: {requirement.get('jd_evidence', '')}"
    )

    inputs = [requirement_text] + [x["text"] for x in candidates]
    try:
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=inputs,
        )
        vectors = [item.embedding for item in sorted(response.data, key=lambda x: x.index)]
    except Exception:
        return []

    requirement_vector = vectors[0]
    ranked = []
    for chunk, vector in zip(candidates, vectors[1:]):
        similarity = _cosine(requirement_vector, vector)
        ranked.append({
            "section": chunk["section"],
            "text": chunk["text"],
            "similarity": round(similarity, 4),
        })

    ranked.sort(key=lambda x: x["similarity"], reverse=True)
    return ranked[:limit]


def semantic_batch(requirements: List[Dict[str, Any]], resume_text: str, per_requirement: int = 5):
    """Batch embedding retrieval for all requirements in one API call."""
    client = _client()
    if client is None or not requirements:
        return {}

    chunks = split_resume_evidence(resume_text)
    if not chunks:
        return {}

    # Keep the candidate pool bounded. Lexical prefiltering reduces cost and noise.
    all_inputs = []
    mapping = []
    for req_index, requirement in enumerate(requirements):
        candidates = _lexical_candidates(requirement, chunks, limit=10)
        req_text = (
            f"Requirement: {requirement.get('skill', '')}\n"
            f"Type: {requirement.get('type', '')}\n"
            f"Importance: {requirement.get('tier', '')}\n"
            f"Job description evidence: {requirement.get('jd_evidence', '')}"
        )
        req_pos = len(all_inputs)
        all_inputs.append(req_text)
        mapping.append((req_index, req_pos, candidates))
        for candidate in candidates:
            all_inputs.append(candidate["text"])

    try:
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=all_inputs)
        vectors = [item.embedding for item in sorted(response.data, key=lambda x: x.index)]
    except Exception:
        return {}

    output = {}
    cursor = 0
    for req_index, req_pos, candidates in mapping:
        req_vector = vectors[req_pos]
        ranked = []
        for offset, candidate in enumerate(candidates, start=1):
            vector = vectors[req_pos + offset]
            ranked.append({
                "section": candidate["section"],
                "text": candidate["text"],
                "similarity": round(_cosine(req_vector, vector), 4),
            })
        ranked.sort(key=lambda x: x["similarity"], reverse=True)
        output[req_index] = ranked[:per_requirement]
        cursor += 1

    return output
