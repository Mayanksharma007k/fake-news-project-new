import re
from urllib.parse import quote, urlparse
from xml.etree import ElementTree as ET

import httpx


GOOGLE_NEWS_URL = (
    "https://news.google.com/rss/search"
    "?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
)


TRUSTED_SOURCES = {
    "Reuters": 95,
    "Associated Press": 95,
    "BBC": 92,
    "BBC News": 92,
    "Britannica": 94,
    "NASA": 98,
    "NASA Science": 98,
    "NOAA": 98,
    "WHO": 98,
    "United Nations": 98,
    "The Guardian": 88,
    "NDTV": 78,
    "Moneycontrol": 72,
    "WION": 70,
}


def clean_text(text: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        text or "",
    ).strip()


def tokens(text: str) -> set[str]:
    stopwords = {
        "the", "and", "that", "this", "with",
        "from", "have", "has", "for", "are",
        "was", "were", "will", "would", "into",
        "about", "after", "before", "their",
        "they", "been", "being", "than", "then",
        "there", "here", "what", "when", "where",
        "which", "while", "also", "said", "says",
        "news", "does", "did", "not", "always",
        "currently", "technically", "strictly",
    }

    words = re.findall(
        r"[a-zA-Z0-9]{3,}",
        text.lower(),
    )

    return {
        word
        for word in words
        if word not in stopwords
    }


def source_reliability(
    source: str,
    url: str,
) -> int:

    source_clean = clean_text(source)

    for name, score in TRUSTED_SOURCES.items():
        if name.lower() in source_clean.lower():
            return score

    try:
        host = urlparse(url).netloc.lower()

        if host.endswith(".gov"):
            return 95

        if host.endswith(".gov.in"):
            return 95

        if host.endswith(".edu"):
            return 90

        if host.endswith(".ac.in"):
            return 90

    except Exception:
        pass

    return 55


def relevance_score(
    claim: str,
    title: str,
    description: str,
) -> int:

    claim_words = tokens(claim)

    evidence_words = tokens(
        f"{title} {description}"
    )

    if not claim_words:
        return 0

    overlap = (
        len(claim_words & evidence_words)
        / len(claim_words)
    )

    return min(
        100,
        round(overlap * 100),
    )


async def search_google_news(
    query_text: str,
    limit: int = 10,
) -> list[dict]:

    query = quote(
        clean_text(query_text)
    )

    url = GOOGLE_NEWS_URL.format(
        query=query
    )

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
        ) as client:

            response = await client.get(url)
            response.raise_for_status()

        root = ET.fromstring(
            response.content
        )

        results = []

        for item in root.findall(".//item")[
            :limit
        ]:

            title_node = item.find("title")
            link_node = item.find("link")
            description_node = item.find(
                "description"
            )
            source_node = item.find(
                "source"
            )

            title = clean_text(
                title_node.text
                if title_node is not None
                else ""
            )

            link = clean_text(
                link_node.text
                if link_node is not None
                else ""
            )

            description = clean_text(
                description_node.text
                if description_node is not None
                else ""
            )

            source = clean_text(
                source_node.text
                if source_node is not None
                else ""
            )

            if not title or not link:
                continue

            reliability = source_reliability(
                source,
                link,
            )

            relevance = relevance_score(
                query_text,
                title,
                description,
            )

            results.append(
                {
                    "title": title,
                    "url": link,
                    "source": (
                        source
                        or "Unknown source"
                    ),
                    "reliability": reliability,
                    "relevance": relevance,
                    "text": description[:500],
                    "query": query_text,
                }
            )

        return results

    except Exception as exc:
        print(
            "Google News search error:",
            repr(exc),
        )
        return []


def opposite_claim(claim: str) -> str:
    """
    Build the opposite proposition for a simple
    positive/negative factual claim.

    This is deliberately conservative. If we cannot
    identify a simple negation, return the original
    claim so we don't invent an opposite statement.
    """

    normalized = clean_text(claim)

    patterns = [
        (
            r"\bdoes not\b",
            "does",
        ),
        (
            r"\bdoesn't\b",
            "does",
        ),
        (
            r"\bis not\b",
            "is",
        ),
        (
            r"\bisn't\b",
            "is",
        ),
        (
            r"\bare not\b",
            "are",
        ),
        (
            r"\baren't\b",
            "are",
        ),
        (
            r"\bwas not\b",
            "was",
        ),
        (
            r"\bwasn't\b",
            "was",
        ),
        (
            r"\bwere not\b",
            "were",
        ),
        (
            r"\bweren't\b",
            "were",
        ),
        (
            r"\bdo not\b",
            "do",
        ),
        (
            r"\bdon't\b",
            "do",
        ),
        (
            r"\bcan not\b",
            "can",
        ),
        (
            r"\bcannot\b",
            "can",
        ),
        (
            r"\bcan't\b",
            "can",
        ),
    ]

    for pattern, replacement in patterns:
        if re.search(pattern, normalized, re.I):
            return re.sub(
                pattern,
                replacement,
                normalized,
                count=1,
                flags=re.I,
            )

    # Positive claim -> negative claim.
    words = normalized.split()

    insert_positions = {
        "is": "is not",
        "are": "are not",
        "was": "was not",
        "were": "were not",
        "does": "does not",
        "do": "do not",
        "can": "cannot",
    }

    for index, word in enumerate(words):
        lower = word.lower()

        if lower in insert_positions:
            words[index] = insert_positions[lower]
            return " ".join(words)

    return normalized


async def search_evidence(
    claim: str,
    limit: int = 10,
) -> list[dict]:

    original = clean_text(claim)
    opposite = opposite_claim(original)

    original_results = await search_google_news(
        original,
        limit,
    )

    # Only run the opposite search when it is
    # meaningfully different from the original.
    if opposite != original:
        opposite_results = await search_google_news(
            opposite,
            limit,
        )
    else:
        opposite_results = []

    combined = (
        original_results
        + opposite_results
    )

    # Remove duplicate URLs.
    unique = {}

    for item in combined:
        url = item["url"]

        if url not in unique:
            unique[url] = item

    results = list(unique.values())

    results.sort(
        key=lambda item: (
            item["relevance"],
            item["reliability"],
        ),
        reverse=True,
    )

    return results[:limit]
