"""Database models that complement Firestore data."""
from __future__ import annotations

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class Profile(models.Model):
    """Metadata about a user that powers the matching algorithm."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    firebase_uid = models.CharField(
        max_length=128,
        unique=True,
        help_text="UID in Firebase authentication, required for Firestore lookups.",
    )
    organization_name = models.CharField(max_length=255, blank=True)
    organization_type = models.CharField(max_length=100, blank=True)
    mission_statement = models.TextField(blank=True)
    focus_areas = models.JSONField(
        default=list,
        blank=True,
        help_text="List of thematic areas such as 'STEM', 'Arts', 'Community Health'.",
    )
    target_beneficiaries = models.JSONField(
        default=list,
        blank=True,
        help_text="List of audiences served, e.g. ['youth', 'women', 'rural'].",
    )
    location = models.CharField(
        max_length=150,
        blank=True,
        help_text="Primary geography for the organization.",
    )
    annual_budget_usd = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1000)],
        help_text="Approximate annual budget in USD for sizing opportunities.",
    )
    preferred_funding_type = models.CharField(max_length=100, blank=True)
    keywords = models.JSONField(
        default=list,
        blank=True,
        help_text="Additional keywords that should boost match scoring.",
    )
    capacity_stage = models.CharField(
        max_length=100,
        blank=True,
        help_text="Stage such as 'startup', 'growth', 'scale'.",
    )
    matching_bucket_override = models.CharField(
        max_length=100,
        blank=True,
        help_text="Force algorithm to use a specific bucket of opportunities.",
    )

    class Meta:
        ordering = ["user__username"]

    def __str__(self) -> str:  # pragma: no cover - string repr
        return f"Profile<{self.user}>"


class OpportunityInteraction(models.Model):
    """Tracks how users interacted with opportunities inside Django."""

    ACTION_APPLY = "apply"
    ACTION_SAVE = "save"
    ACTION_PASS = "pass"
    ACTION_CHOICES = [
        (ACTION_APPLY, "Applied"),
        (ACTION_SAVE, "Saved"),
        (ACTION_PASS, "Passed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="opportunity_actions")
    opportunity_id = models.CharField(max_length=255)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "action"]),
            models.Index(fields=["opportunity_id"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "opportunity_id", "action"],
                name="unique_action_per_opportunity",
            )
        ]

    def __str__(self) -> str:  # pragma: no cover - string repr
        return f"{self.user} {self.action} {self.opportunity_id}"
