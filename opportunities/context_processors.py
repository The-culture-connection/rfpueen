"""Template context helpers."""
from __future__ import annotations

from .models import Profile


def profile_context(request):
    """Expose the active profile (if any) to templates."""

    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"active_profile": None, "has_profile": False}

    try:
        profile = user.profile  # type: ignore[attr-defined]
    except Profile.DoesNotExist:
        return {"active_profile": None, "has_profile": False}

    return {"active_profile": profile, "has_profile": True}
