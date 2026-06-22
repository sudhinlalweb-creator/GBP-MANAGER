"""Defensive parsing for Google organic and local pack results."""

from __future__ import annotations

from typing import Iterable
from urllib.parse import parse_qs, urlparse

from pydantic import BaseModel, HttpUrl
from selectolax.parser import HTMLParser, Node

from app.services.serp.base import SERPParseError


class OrganicResult(BaseModel):
    """Structured representation of one organic result."""

    position: int
    title: str
    url: HttpUrl | str


class MapPackResult(BaseModel):
    """Structured representation of one local map pack listing."""

    position: int
    business_name: str
    rating: float | None = None
    review_count: int | None = None


class ParsedSERPResult(BaseModel):
    """Structured SERP parse output."""

    organic_results: list[OrganicResult]
    map_pack_results: list[MapPackResult]


def parse_google_serp(html: str) -> ParsedSERPResult:
    """Parse organic and local pack results from Google SERP HTML."""
    if not html.strip():
        raise SERPParseError("Cannot parse an empty SERP HTML payload.")

    tree = HTMLParser(html)
    organic_results = _parse_organic_results(tree)
    map_pack_results = _parse_map_pack_results(tree)

    if not organic_results and not map_pack_results:
        raise SERPParseError("No organic or map pack results were detected in the SERP HTML.")

    return ParsedSERPResult(
        organic_results=organic_results,
        map_pack_results=map_pack_results,
    )


def _parse_organic_results(tree: HTMLParser) -> list[OrganicResult]:
    """Extract organic results using several fallback selectors."""
    organic_candidates = tree.css(
        "#search div.g, #search div[data-snc], #search div.tF2Cxc, div#rso div.g"
    )
    results: list[OrganicResult] = []
    seen_urls: set[str] = set()

    for candidate in organic_candidates:
        anchor = candidate.css_first("a[href]")
        title_node = candidate.css_first("h3")
        if anchor is None or title_node is None:
            continue

        url = _normalize_google_result_url(anchor.attributes.get("href", ""))
        title = title_node.text(strip=True)
        if not url or not title or url in seen_urls or _is_google_internal_url(url):
            continue

        seen_urls.add(url)
        results.append(
            OrganicResult(
                position=len(results) + 1,
                title=title,
                url=url,
            )
        )

    return results


def _parse_map_pack_results(tree: HTMLParser) -> list[MapPackResult]:
    """Extract local map pack entries using heuristic selectors."""
    selectors = (
        "div.VkpGBb",
        "div.rllt__details",
        "div[data-local-attribute]",
        "div[role='article']",
    )
    results: list[MapPackResult] = []
    seen_names: set[str] = set()

    for selector in selectors:
        for candidate in tree.css(selector):
            business_name = _extract_business_name(candidate)
            if not business_name or business_name in seen_names:
                continue

            rating = _extract_rating(candidate)
            review_count = _extract_review_count(candidate)
            results.append(
                MapPackResult(
                    position=len(results) + 1,
                    business_name=business_name,
                    rating=rating,
                    review_count=review_count,
                )
            )
            seen_names.add(business_name)

            if len(results) >= 3:
                return results

    return results


def _extract_business_name(node: Node) -> str | None:
    """Return the best-effort business name for a map pack node."""
    candidates: Iterable[str | None] = (
        _text_or_none(node.css_first(".dbg0pd")),
        _text_or_none(node.css_first("[role='heading']")),
        _text_or_none(node.css_first("a[aria-label]")),
        _text_or_none(node.css_first("span.OSrXXb")),
    )
    for candidate in candidates:
        if candidate:
            return candidate
    return None


def _extract_rating(node: Node) -> float | None:
    """Parse a numeric rating from map pack text content."""
    rating_selectors = (".yi40Hd", ".MW4etd", "[aria-label*='stars']")
    for selector in rating_selectors:
        rating_node = node.css_first(selector)
        if rating_node is None:
            continue
        rating_text = rating_node.text(strip=True)
        parsed = _extract_first_float(rating_text)
        if parsed is not None:
            return parsed
    return None


def _extract_review_count(node: Node) -> int | None:
    """Parse the review count from map pack text content."""
    review_selectors = (".RDApEe", ".UY7F9", "[aria-label*='reviews']")
    for selector in review_selectors:
        review_node = node.css_first(selector)
        if review_node is None:
            continue
        parsed = _extract_first_int(review_node.text(strip=True))
        if parsed is not None:
            return parsed
    return None


def _normalize_google_result_url(url: str) -> str | None:
    """Unwrap Google tracking URLs into their destination URL."""
    if not url:
        return None

    if url.startswith("/url?"):
        query_string = urlparse(url).query
        params = parse_qs(query_string)
        return params.get("q", [None])[0]

    if url.startswith("http://") or url.startswith("https://"):
        return url

    return None


def _is_google_internal_url(url: str) -> bool:
    """Return True when a URL points to a Google-owned destination."""
    parsed = urlparse(url)
    return "google." in parsed.netloc


def _text_or_none(node: Node | None) -> str | None:
    """Safely extract stripped text from an optional node."""
    if node is None:
        return None
    text = node.text(strip=True)
    return text or None


def _extract_first_float(text: str) -> float | None:
    """Extract the first float-looking token from freeform text."""
    current = []
    for character in text:
        if character.isdigit() or character == ".":
            current.append(character)
        elif current:
            break
    if not current:
        return None
    try:
        return float("".join(current))
    except ValueError:
        return None


def _extract_first_int(text: str) -> int | None:
    """Extract the first integer-looking token from freeform text."""
    digits = [character for character in text if character.isdigit()]
    if not digits:
        return None
    try:
        return int("".join(digits))
    except ValueError:
        return None
