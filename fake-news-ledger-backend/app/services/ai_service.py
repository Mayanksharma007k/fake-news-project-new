from __future__ import annotations

import re
from typing import Any

from app.services.evidence_service import search_evidence


STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "does", "do", "did", "has", "have", "had", "can", "could", "will",
    "would", "should", "may", "might", "of", "to", "in", "on", "for",
    "from", "with", "by", "and", "or", "but", "that", "this", "these",
    "those", "it", "its", "as", "at", "about", "into", "than", "then",
    "they", "their", "them", "he", "she", "we", "you", "i"
}

NEGATION_WORDS = {
    "not", "never", "no", "neither", "nor"
}

FACT_CHECK_TERMS = {
    "fact check",
    "fact-check",
    "factcheck",
    "false",
    "incorrect",
    "misleading",
    "debunked",
    "untrue",
    "wrong",
    "hoax",
    "fake",
    "no evidence",
    "not true",
    "isn't true",
    "isnt true",
    "doesn't",
    "doesnt",
}

AUTHORITATIVE_SOURCES = {
    "nasa": 98,
    "nasa science": 98,
    "noaa": 98,
    "who": 98,
    "un": 98,
    "united nations": 98,
    "britannica": 96,
    "reuters": 95,
    "associated press": 95,
    "ap": 95,
    "bbc": 92,
    "national geographic": 90,
}


def normalize(text: str) -> str:
    text = (text or "").lower()

    text = re.sub(r"https?://\S+", " ", text)

    # Preserve apostrophes temporarily because doesn't/isn't matter.
    text = text.replace("’", "'")

    text = re.sub(r"[^a-z0-9\s'-]", " ", text)

    return re.sub(r"\s+", " ", text).strip()


def words(text: str) -> set[str]:
    return set(normalize(text).split())


def content_words(text: str) -> set[str]:
    return {
        w for w in words(text)
        if w not in STOPWORDS and len(w) > 2
    }


def similarity(a: str, b: str) -> float:
    aa = content_words(a)
    bb = content_words(b)

    if not aa or not bb:
        return 0.0

    return len(aa & bb) / len(aa | bb)


def has_negation(text: str) -> bool:
    normalized = normalize(text)

    if any(
        re.search(
            rf"\b{re.escape(word)}\b",
            normalized
        )
        for word in NEGATION_WORDS
    ):
        return True

    return bool(
        re.search(
            r"\b(?:does|do|did|is|are|was|were|can|will|has|have|had)\s+not\b",
            normalized,
        )
    ) or bool(
        re.search(
            r"\b(?:doesn't|isn't|aren't|wasn't|weren't|can't|won't|haven't|hasn't|didn't)\b",
            normalized,
        )
    )


def has_fact_check(text: str) -> bool:
    normalized = normalize(text)
    return any(term in normalized for term in FACT_CHECK_TERMS)


def source_reliability(source: str, url: str = "") -> int:
    source_n = normalize(source)
    url_n = (url or "").lower()

    for name, score in AUTHORITATIVE_SOURCES.items():
        if name in source_n:
            return score

    if ".gov" in url_n:
        return 95

    if ".edu" in url_n:
        return 90

    return 55


def relevance_score(claim: str, evidence_text: str) -> int:
    """
    Measures whether the evidence is actually about the same subject.

    Uses both token overlap and important noun/entity overlap.
    """

    claim_n = normalize(claim)
    evidence_n = normalize(evidence_text)

    claim_words = content_words(claim_n)
    evidence_words = content_words(evidence_n)

    if not claim_words or not evidence_words:
        return 0

    overlap = len(claim_words & evidence_words)

    coverage = overlap / len(claim_words)

    score = int(coverage * 100)

    # Exact phrase is strong evidence of topical relevance.
    claim_tokens = claim_n.split()

    for size in (6, 5, 4):
        if len(claim_tokens) < size:
            continue

        for i in range(len(claim_tokens) - size + 1):
            phrase = " ".join(claim_tokens[i:i + size])

            if len(phrase) >= 12 and phrase in evidence_n:
                score += 20
                break

    return min(100, score)


def remove_negation(text: str) -> str:
    text = normalize(text)

    replacements = [
        (r"\bdoesn't\b", "does"),
        (r"\bisn't\b", "is"),
        (r"\baren't\b", "are"),
        (r"\bwasn't\b", "was"),
        (r"\bweren't\b", "were"),
        (r"\bdidn't\b", "did"),
        (r"\bcan't\b", "can"),
        (r"\bwon't\b", "will"),
        (r"\bhasn't\b", "has"),
        (r"\bhaven't\b", "have"),
        (r"\bdoes not\b", "does"),
        (r"\bdo not\b", "do"),
        (r"\bdid not\b", "did"),
        (r"\bis not\b", "is"),
        (r"\bare not\b", "are"),
        (r"\bwas not\b", "was"),
        (r"\bwere not\b", "were"),
        (r"\bcan not\b", "can"),
        (r"\bcannot\b", "can"),
        (r"\bwill not\b", "will"),
        (r"\bhas not\b", "has"),
        (r"\bhave not\b", "have"),
        (r"\bhad not\b", "had"),
        (r"\bnever\b", ""),
        (r"\bnot\b", ""),
    ]

    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)

    return re.sub(r"\s+", " ", text).strip()


def same_proposition(claim: str, evidence: str) -> bool:
    """
    Determines whether two pieces of text discuss the same underlying
    proposition, ignoring grammatical negation.

    Threshold intentionally lower than ordinary semantic similarity
    because headlines often use synonyms such as:

        revolves / revolution / orbits
    """

    base_similarity = similarity(
        remove_negation(claim),
        remove_negation(evidence),
    )

    if base_similarity >= 0.35:
        return True

    # Common scientific/news terminology.
    claim_n = remove_negation(claim)
    evidence_n = remove_negation(evidence)

    synonym_groups = [
        {"revolve", "revolves", "revolution", "orbit", "orbits", "orbital"},
        {"made", "composition", "composed"},
        {"earth", "earth's"},
        {"sun", "solar"},
    ]

    claim_tokens = set(claim_n.split())
    evidence_tokens = set(evidence_n.split())

    matched_groups = 0

    for group in synonym_groups:
        if claim_tokens & group and evidence_tokens & group:
            matched_groups += 1

    return matched_groups >= 2 and base_similarity >= 0.20


def evidence_mentions_wrong_subject(
    claim: str,
    evidence: str,
) -> bool:
    """
    Prevents a result about another entity from being treated as evidence.

    Example:
      Claim: Earth is made of cheese.
      Evidence: Moon is not made of cheese.

    These share 'made' and 'cheese', but the subject differs.
    """

    claim_tokens = content_words(remove_negation(claim))
    evidence_tokens = content_words(remove_negation(evidence))

    important_entities = {
        "earth",
        "moon",
        "sun",
        "mars",
        "jupiter",
        "venus",
        "mercury",
        "saturn",
        "uranus",
        "neptune",
        "human",
        "humans",
        "people",
        "person",
    }

    claim_entities = claim_tokens & important_entities
    evidence_entities = evidence_tokens & important_entities

    if claim_entities and evidence_entities:
        if not claim_entities.intersection(evidence_entities):
            return True

    return False


def classify_evidence(
    claim: str,
    evidence: dict[str, Any],
) -> tuple[str, int]:

    title = evidence.get("title", "")
    description = evidence.get("description", "")
    text = f"{title}. {description}".strip()

    if not text:
        return "NEUTRAL", 0

    relevance = relevance_score(claim, text)

    if relevance < 35:
        return "NEUTRAL", 10

    if evidence_mentions_wrong_subject(claim, text):
        return "NEUTRAL", 10

    reliability = int(evidence.get("reliability", 55))

    claim_negative = has_negation(claim)
    evidence_negative = has_negation(text)

    normalized = normalize(text)

    # ----------------------------------------------------------
    # IMPORTANT:
    #
    # Some articles use wording such as:
    #
    # "Earth does not revolve around the Sun but something else"
    #
    # while actually explaining the Solar System barycenter.
    #
    # That is a technical qualification, NOT a simple factual
    # contradiction of the ordinary statement that Earth orbits
    # the Sun.
    # ----------------------------------------------------------

    technical_qualification_terms = {
        "barycenter",
        "center of mass",
        "centre of mass",
        "solar system barycenter",
        "technically",
        "strictly speaking",
        "not exactly",
        "not always",
        "something else nearby",
        "point around which",
        "jupiter",
        "gas giants",
        "motion of the solar system",
    }

    technical_qualification = any(
        term in normalized
        for term in technical_qualification_terms
    )

    # If the article is explaining a technical nuance, do not
    # classify it as direct support/contradiction.
    if technical_qualification:
        return "NEUTRAL", 55

    same = same_proposition(claim, text)

    if not same:
        return "NEUTRAL", 20

    # ----------------------------------------------------------
    # Explicit fact-check language.
    # ----------------------------------------------------------

    explicit_false_patterns = [
        "false",
        "incorrect",
        "inaccurate",
        "misleading",
        "debunked",
        "untrue",
        "wrong",
        "hoax",
        "fake",
        "no evidence",
        "not true",
    ]

    explicit_false = any(
        term in normalized
        for term in explicit_false_patterns
    )

    if explicit_false:
        return "CONTRADICTS", min(
            100,
            75 + reliability // 8,
        )

    # ----------------------------------------------------------
    # Direct polarity match.
    #
    # We only allow high-confidence sources to directly establish
    # a factual proposition.
    # ----------------------------------------------------------

    if claim_negative == evidence_negative:

        if reliability >= 90 and relevance >= 45:
            return "SUPPORTS", min(
                100,
                80 + reliability // 8,
            )

        if reliability >= 70 and relevance >= 70:
            return "SUPPORTS", 72

        return "NEUTRAL", 35

    # ----------------------------------------------------------
    # Opposite polarity.
    #
    # An opposite statement from a reliable source can contradict
    # the claim, BUT technical qualification has already been
    # excluded above.
    # ----------------------------------------------------------

    if claim_negative != evidence_negative:

        if reliability >= 90 and relevance >= 45:
            return "CONTRADICTS", min(
                100,
                82 + reliability // 8,
            )

        if reliability >= 70 and relevance >= 70:
            return "CONTRADICTS", 75

        return "NEUTRAL", 35

    return "NEUTRAL", 20

def determine_status(
    supports: float,
    contradicts: float,
    neutral: float,
    evidence_count: int,
    evidence: list[dict[str, Any]] | None = None,
) -> str:

    if evidence_count == 0:
        return "UNCERTAIN"

    evidence = evidence or []

    supporting = [
        x for x in evidence
        if x.get("type") == "SUPPORTS"
    ]

    contradicting = [
        x for x in evidence
        if x.get("type") == "CONTRADICTS"
    ]

    # ----------------------------------------------------------
    # Strong direct evidence.
    #
    # A highly reliable source (NASA, Britannica, Reuters, etc.)
    # with good relevance should dominate ordinary news repetition.
    # ----------------------------------------------------------

    strong_support = [
        x for x in supporting
        if x.get("reliability", 0) >= 90
        and x.get("relevance", 0) >= 45
    ]

    strong_contradiction = [
        x for x in contradicting
        if x.get("reliability", 0) >= 90
        and x.get("relevance", 0) >= 45
    ]

    # A strong authoritative source supports the claim unless there
    # is equally strong authoritative evidence directly contradicting it.
    if strong_support and not strong_contradiction:
        return "SUPPORTED"

    if strong_contradiction and not strong_support:
        return "HIGH_RISK"

    # ----------------------------------------------------------
    # Multiple reliable sources can establish a result even when
    # no single source is authoritative.
    # ----------------------------------------------------------

    reliable_support = [
        x for x in supporting
        if x.get("reliability", 0) >= 70
        and x.get("relevance", 0) >= 65
    ]

    reliable_contradiction = [
        x for x in contradicting
        if x.get("reliability", 0) >= 70
        and x.get("relevance", 0) >= 65
    ]

    if len(reliable_support) >= 2 and len(reliable_support) > len(reliable_contradiction):
        return "SUPPORTED"

    if (
        len(reliable_contradiction) >= 2
        and len(reliable_contradiction) > len(reliable_support)
    ):
        return "HIGH_RISK"

    # One medium-quality source is not enough to overturn the claim.
    if len(strong_support) >= 1 and not reliable_contradiction:
        return "SUPPORTED"

    if len(strong_contradiction) >= 1 and not reliable_support:
        return "HIGH_RISK"

    return "UNCERTAIN"

def calculate_trust_score(
    status: str,
    supports: float,
    contradicts: float,
    evidence: list[dict[str, Any]],
) -> int:

    meaningful = [
        item for item in evidence
        if item["type"] in {"SUPPORTS", "CONTRADICTS"}
    ]

    if not meaningful:
        return 50

    reliability = sum(
        int(item["reliability"])
        for item in meaningful
    ) / len(meaningful)

    if status == "SUPPORTED":
        score = 55 + reliability * 0.45

    elif status == "HIGH_RISK":
        score = 45 - reliability * 0.15

    else:
        balance = supports - contradicts
        score = 50 + balance * 0.10

    return max(0, min(100, int(score)))


async def analyze_claim(
    claim: str,
    article_text: str = "",
) -> dict[str, Any]:

    claim = claim.strip()

    if not claim:
        return {
            "status": "UNCERTAIN",
            "trust_score": 50,
            "ai_confidence": 0,
            "evidence_strength": 0,
            "source_reliability": 0,
            "explanation": "No claim was provided.",
            "evidence": [],
        }

    raw_evidence = await search_evidence(
        claim,
        limit=12,
    )

    processed: list[dict[str, Any]] = []

    supports = 0.0
    contradicts = 0.0
    neutral = 0.0

    for item in raw_evidence:

        title = item.get("title", "")
        description = item.get("description", "")

        text = f"{title}. {description}".strip()

        relevance = relevance_score(claim, text)

        reliability = int(
            item.get(
                "reliability",
                source_reliability(
                    item.get("source", ""),
                    item.get("link", ""),
                ),
            )
        )

        evidence_type, confidence = classify_evidence(
            claim,
            {
                **item,
                "reliability": reliability,
            },
        )

        result = {
            **item,
            "type": evidence_type,
            "relevance": relevance,
            "reliability": reliability,
            "confidence": confidence,
            "text": text,
        }

        processed.append(result)

        # Evidence weight.
        weight = (
            (relevance / 100.0)
            * (reliability / 100.0)
            * (confidence / 100.0)
            * 100
        )

        if evidence_type == "SUPPORTS":
            supports += weight

        elif evidence_type == "CONTRADICTS":
            contradicts += weight

        else:
            neutral += weight * 0.25

    status = determine_status(
        supports,
        contradicts,
        neutral,
        len(processed),
        processed,
    )

    trust_score = calculate_trust_score(
        status,
        supports,
        contradicts,
        processed,
    )

    meaningful = [
        item for item in processed
        if item["type"] in {"SUPPORTS", "CONTRADICTS"}
    ]

    if meaningful:
        avg_reliability = sum(
            item["reliability"]
            for item in meaningful
        ) / len(meaningful)

        ai_confidence = max(
            55,
            min(
                98,
                int(
                    avg_reliability
                    + min(10, len(meaningful) * 2)
                ),
            ),
        )
    else:
        ai_confidence = 45

    evidence_strength = min(
        100,
        int(
            min(70, max(supports, contradicts))
            + min(30, len(meaningful) * 5)
        ),
    )

    if status == "SUPPORTED":
        explanation = (
            "The claim is supported by relevant evidence, "
            "including evidence from reliable sources."
        )

    elif status == "HIGH_RISK":
        explanation = (
            "The claim is contradicted by relevant evidence "
            "from reliable sources."
        )

    else:
        explanation = (
            "The available evidence is insufficient, conflicting, "
            "or too nuanced to establish the claim confidently."
        )

    return {
        "status": status,
        "trust_score": trust_score,
        "ai_confidence": ai_confidence,
        "evidence_strength": evidence_strength,
        "source_reliability": (
            int(
                sum(item["reliability"] for item in processed)
                / len(processed)
            )
            if processed
            else 0
        ),
        "explanation": explanation,
        "evidence": processed,
    }