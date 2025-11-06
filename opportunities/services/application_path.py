"""Utility to identify the most direct application pathway for an opportunity."""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Iterable
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


APPLY_KEYWORDS = [
    "apply",
    "application",
    "submit",
    "start",
    "begin",
    "proposal",
]


@dataclass(slots=True)
class ApplicationPathResult:
    """Represents the discovered path to an application entry point."""

    application_url: str | None
    instructions: list[str]
    visited_urls: list[str] = field(default_factory=list)
    confidence: float = 0.0
    notes: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "application_url": self.application_url,
            "instructions": self.instructions,
            "visited_urls": self.visited_urls,
            "confidence": round(self.confidence, 2),
            "notes": self.notes,
        }


def discover_application_path(
    starting_url: str,
    *,
    max_depth: int = 2,
    timeout: int = 10,
    session: requests.Session | None = None,
) -> ApplicationPathResult:
    """Attempt to find the most direct apply link on a website."""

    session = session or requests.Session()
    visited: list[str] = []
    frontier: list[tuple[str, int]] = [(starting_url, 0)]

    while frontier:
        url, depth = frontier.pop(0)
        if url in visited:
            continue
        visited.append(url)

        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
        except requests.RequestException as exc:  # pragma: no cover - network failure path
            logger.warning("Failed to fetch %s: %s", url, exc)
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # 1. Look for explicit application links.
        candidate = _find_apply_link(url, soup)
        if candidate:
            return ApplicationPathResult(
                application_url=candidate,
                instructions=[
                    "Open the opportunity page",
                    "Use the apply link highlighted on the site",
                ],
                visited_urls=visited,
                confidence=0.85 if depth == 0 else 0.75,
            )

        # 2. If too deep, stop.
        if depth >= max_depth:
            continue

        # 3. Enqueue additional relevant links to explore.
        for link in _gather_relevant_links(url, soup):
            if link not in visited:
                frontier.append((link, depth + 1))

    # Fallback instructions.
    return ApplicationPathResult(
        application_url=None,
        instructions=[
            "Visit the opportunity page",
            "Look for buttons or navigation items labelled Apply / Submit",
            "Follow the organization's grants or funding portal if required",
        ],
        visited_urls=visited,
        confidence=0.2,
        notes="Automatic discovery could not find a direct apply link; manual review suggested.",
    )


def _find_apply_link(base_url: str, soup: BeautifulSoup) -> str | None:
    anchors = soup.find_all("a", href=True)
    for anchor in anchors:
        text = (anchor.get_text(strip=True) or "").lower()
        href = anchor["href"].strip()
        if not href:
            continue
        if _matches_keyword(text) or _matches_keyword(anchor.get("title", "")):
            return urljoin(base_url, href)

        # Use data attributes for buttons.
        data_attrs = " ".join(
            str(value) for key, value in anchor.attrs.items() if key.startswith("data-")
        ).lower()
        if _matches_keyword(data_attrs):
            return urljoin(base_url, href)

    # Scan for button elements that wrap anchors.
    buttons = soup.find_all("button")
    for button in buttons:
        text = button.get_text(strip=True).lower()
        if _matches_keyword(text):
            parent_anchor = button.find_parent("a")
            if parent_anchor and parent_anchor.get("href"):
                return urljoin(base_url, parent_anchor["href"])
    return None


def _gather_relevant_links(base_url: str, soup: BeautifulSoup) -> Iterable[str]:
    relevant_patterns = re.compile(r"grant|apply|fund|portal|login|submission", re.IGNORECASE)
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        text = anchor.get_text(strip=True)
        if not href:
            continue
        if _matches_keyword(text) or relevant_patterns.search(text) or relevant_patterns.search(href):
            yield urljoin(base_url, href)


def _matches_keyword(text: str) -> bool:
    text = (text or "").lower()
    return any(keyword in text for keyword in APPLY_KEYWORDS)
