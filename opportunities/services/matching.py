"""Match opportunities against a profile with traceable scoring."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence, TYPE_CHECKING

from django.utils.text import slugify

from .firestore_service import FirestoreOpportunity, FirestoreProfile


if TYPE_CHECKING:  # pragma: no cover - type checking only
    from opportunities.models import Profile

@dataclass(slots=True)
class MatchInsight:
    """Explains how a particular criterion contributed to the score."""

    label: str
    detail: str
    weight: float
    met: bool


@dataclass(slots=True)
class OpportunityMatch:
    """Represents an opportunity with its computed match statistics."""

    opportunity: FirestoreOpportunity
    score: float
    win_rate: float
    confidence: float
    insights: list[MatchInsight]
    missing_criteria: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "opportunity": self.opportunity,
            "score": round(self.score, 3),
            "win_rate": round(self.win_rate, 1),
            "confidence": round(self.confidence, 2),
            "insights": [insight.__dict__ for insight in self.insights],
            "missing_criteria": self.missing_criteria,
        }


WEIGHTS = {
    "focus_areas": 0.28,
    "beneficiaries": 0.14,
    "location": 0.14,
    "funding_type": 0.1,
    "keywords": 0.12,
    "organization_type": 0.1,
    "budget": 0.12,
}


def build_opportunity_matches(
    *,
    profile: FirestoreProfile | None,
    fallback_profile: "Profile | None" = None,
    opportunities: Sequence[FirestoreOpportunity],
) -> list[OpportunityMatch]:
    """Compute match metrics for a list of opportunities."""

    normalized = _merge_profiles(profile, fallback_profile)
    results: list[OpportunityMatch] = []

    for opportunity in opportunities:
        insights: list[MatchInsight] = []
        missing: list[str] = []
        score = 0.0

        score, insights, missing = _score_opportunity(opportunity, normalized, insights, missing)
        win_rate = min(99.0, max(3.0, score * 100))
        confidence = _estimate_confidence(normalized, insights)

        results.append(
            OpportunityMatch(
                opportunity=opportunity,
                score=score,
                win_rate=win_rate,
                confidence=confidence,
                insights=insights,
                missing_criteria=missing,
            )
        )

    return sorted(results, key=lambda item: item.score, reverse=True)


def _merge_profiles(fs_profile: FirestoreProfile | None, fallback_profile: "Profile | None") -> dict[str, object]:
    data: dict[str, object] = {
        "focus_areas": [],
        "target_beneficiaries": [],
        "location": None,
        "preferred_funding_type": None,
        "keywords": [],
        "organization_type": None,
        "annual_budget_usd": None,
    }

    if fs_profile:
        data.update(
            {
                "focus_areas": [slugify(item) for item in fs_profile.focus_areas],
                "target_beneficiaries": [slugify(item) for item in fs_profile.target_beneficiaries],
                "location": slugify(fs_profile.location) if fs_profile.location else None,
                "preferred_funding_type": slugify(fs_profile.data.get("funding_type", "")),
                "keywords": [slugify(item) for item in fs_profile.keywords],
                "organization_type": slugify(fs_profile.organization_type) if fs_profile.organization_type else None,
                "annual_budget_usd": fs_profile.annual_budget_usd,
            }
        )

    if fallback_profile:
        data.setdefault("focus_areas", [])
        if not data["focus_areas"]:
            data["focus_areas"] = [slugify(item) for item in fallback_profile.focus_areas]
        if not data["target_beneficiaries"]:
            data["target_beneficiaries"] = [slugify(item) for item in fallback_profile.target_beneficiaries]
        if not data["location"] and fallback_profile.location:
            data["location"] = slugify(fallback_profile.location)
        if not data["preferred_funding_type"] and fallback_profile.preferred_funding_type:
            data["preferred_funding_type"] = slugify(fallback_profile.preferred_funding_type)
        if not data["keywords"]:
            data["keywords"] = [slugify(item) for item in fallback_profile.keywords]
        if not data["organization_type"] and fallback_profile.organization_type:
            data["organization_type"] = slugify(fallback_profile.organization_type)
        if not data["annual_budget_usd"] and fallback_profile.annual_budget_usd:
            data["annual_budget_usd"] = fallback_profile.annual_budget_usd

    return data


def _score_opportunity(opportunity, profile_data, insights, missing):
    score = 0.0

    score += _score_focus(opportunity, profile_data, insights, missing)
    score += _score_beneficiaries(opportunity, profile_data, insights, missing)
    score += _score_location(opportunity, profile_data, insights, missing)
    score += _score_funding_type(opportunity, profile_data, insights, missing)
    score += _score_keywords(opportunity, profile_data, insights, missing)
    score += _score_organization_type(opportunity, profile_data, insights, missing)
    score += _score_budget(opportunity, profile_data, insights, missing)

    return score, insights, missing


def _score_focus(opportunity, profile_data, insights, missing):
    weight = WEIGHTS["focus_areas"]
    profile_focus = set(profile_data.get("focus_areas", []))
    opp_focus = {
        slugify(tag)
        for tag in opportunity.raw.get("focus_areas", opportunity.tags)
    }
    if not profile_focus or not opp_focus:
        missing.append("focus areas alignment")
        insights.append(
            MatchInsight(
                label="Focus Areas",
                detail="Not enough data to compare focus areas.",
                weight=0.0,
                met=False,
            )
        )
        return 0.0

    overlap = profile_focus & opp_focus
    ratio = len(overlap) / len(profile_focus)
    contribution = ratio * weight
    insights.append(
        MatchInsight(
            label="Focus Areas",
            detail=f"Matched {len(overlap)} focus areas: {', '.join(overlap) if overlap else 'none'}.",
            weight=round(contribution, 3),
            met=bool(overlap),
        )
    )
    if not overlap:
        missing.append("focus areas do not overlap")
    return contribution


def _score_beneficiaries(opportunity, profile_data, insights, missing):
    weight = WEIGHTS["beneficiaries"]
    profile_beneficiaries = set(profile_data.get("target_beneficiaries", []))
    opp_beneficiaries = {
        slugify(item)
        for item in opportunity.raw.get("beneficiaries", opportunity.eligibility)
    }
    if not profile_beneficiaries or not opp_beneficiaries:
        insights.append(
            MatchInsight(
                label="Beneficiaries",
                detail="Beneficiary information incomplete to compare.",
                weight=0.0,
                met=False,
            )
        )
        return 0.0

    overlap = profile_beneficiaries & opp_beneficiaries
    ratio = len(overlap) / len(profile_beneficiaries)
    contribution = ratio * weight
    insights.append(
        MatchInsight(
            label="Beneficiaries",
            detail=f"Overlap on {', '.join(overlap) if overlap else 'no beneficiaries'}.",
            weight=round(contribution, 3),
            met=bool(overlap),
        )
    )
    if not overlap:
        missing.append("target beneficiaries")
    return contribution


def _score_location(opportunity, profile_data, insights, missing):
    weight = WEIGHTS["location"]
    profile_location = profile_data.get("location")
    opp_location = slugify(opportunity.location) if opportunity.location else None
    if not profile_location or not opp_location:
        insights.append(
            MatchInsight(
                label="Location",
                detail="Missing location data to compare.",
                weight=0.0,
                met=False,
            )
        )
        return 0.0
    is_match = profile_location in opp_location or opp_location in profile_location
    contribution = weight if is_match else 0.0
    insights.append(
        MatchInsight(
            label="Location",
            detail=f"Profile vs opportunity: {profile_location} / {opp_location}.",
            weight=round(contribution, 3),
            met=is_match,
        )
    )
    if not is_match:
        missing.append("preferred geography")
    return contribution


def _score_funding_type(opportunity, profile_data, insights, missing):
    weight = WEIGHTS["funding_type"]
    profile_type = profile_data.get("preferred_funding_type")
    opp_type = slugify(opportunity.raw.get("funding_type", ""))
    if not profile_type or not opp_type:
        insights.append(
            MatchInsight(
                label="Funding Type",
                detail="Funding type preference not available.",
                weight=0.0,
                met=False,
            )
        )
        return 0.0
    is_match = profile_type == opp_type
    contribution = weight if is_match else weight * 0.25
    insights.append(
        MatchInsight(
            label="Funding Type",
            detail=f"Preferred {profile_type}; opportunity offers {opp_type or 'unspecified'}.",
            weight=round(contribution, 3),
            met=is_match,
        )
    )
    if not is_match:
        missing.append("funding type alignment")
    return contribution


def _score_keywords(opportunity, profile_data, insights, missing):
    weight = WEIGHTS["keywords"]
    profile_keywords = set(profile_data.get("keywords", []))
    if not profile_keywords:
        insights.append(
            MatchInsight(
                label="Keywords",
                detail="No profile keywords provided.",
                weight=0.0,
                met=False,
            )
        )
        return 0.0

    text_haystack = " ".join(
        str(value)
        for key, value in opportunity.raw.items()
        if isinstance(value, (str, list))
    ).lower()

    hits = {kw for kw in profile_keywords if kw in text_haystack}
    ratio = len(hits) / len(profile_keywords)
    contribution = ratio * weight
    insights.append(
        MatchInsight(
            label="Keywords",
            detail=f"Hit {len(hits)} / {len(profile_keywords)} profile keywords.",
            weight=round(contribution, 3),
            met=bool(hits),
        )
    )
    if not hits:
        missing.append("keyword relevance")
    return contribution


def _score_organization_type(opportunity, profile_data, insights, missing):
    weight = WEIGHTS["organization_type"]
    profile_type = profile_data.get("organization_type")
    opp_types: Iterable[str] = opportunity.raw.get("eligible_organizations", [])
    opp_types = [slugify(item) for item in opp_types] if opp_types else []
    if not profile_type or not opp_types:
        insights.append(
            MatchInsight(
                label="Organization Type",
                detail="Eligibility by organization type missing.",
                weight=0.0,
                met=False,
            )
        )
        return 0.0
    is_match = profile_type in opp_types
    contribution = weight if is_match else 0.0
    insights.append(
        MatchInsight(
            label="Organization Type",
            detail=f"{profile_type} {'is' if is_match else 'is not'} eligible.",
            weight=round(contribution, 3),
            met=is_match,
        )
    )
    if not is_match:
        missing.append("organization type eligibility")
    return contribution


def _score_budget(opportunity, profile_data, insights, missing):
    weight = WEIGHTS["budget"]
    budget = profile_data.get("annual_budget_usd")
    opp_min = opportunity.raw.get("budget_min")
    opp_max = opportunity.raw.get("budget_max")
    if not budget:
        insights.append(
            MatchInsight(
                label="Budget",
                detail="No organizational budget provided.",
                weight=0.0,
                met=False,
            )
        )
        return 0.0

    def _to_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    opp_min = _to_int(opp_min)
    opp_max = _to_int(opp_max)

    if opp_min is None and opp_max is None:
        insights.append(
            MatchInsight(
                label="Budget",
                detail="Opportunity does not specify organizational budget window.",
                weight=weight * 0.3,
                met=True,
            )
        )
        return weight * 0.3

    within_range = True
    if opp_min is not None and budget < opp_min:
        within_range = False
    if opp_max is not None and budget > opp_max:
        within_range = False

    contribution = weight if within_range else 0.0
    insights.append(
        MatchInsight(
            label="Budget",
            detail=f"Org budget {budget} vs required {opp_min or 'N/A'} - {opp_max or 'N/A'}.",
            weight=round(contribution, 3),
            met=within_range,
        )
    )
    if not within_range:
        missing.append("budget compatibility")
    return contribution


def _estimate_confidence(profile_data, insights):
    completeness = sum(1 for insight in insights if insight.met)
    total = len(insights) or 1
    base_confidence = completeness / total
    if profile_data.get("keywords"):
        base_confidence += 0.1
    return min(0.99, max(0.35, base_confidence))
