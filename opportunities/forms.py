"""Forms for the opportunities application."""
from __future__ import annotations

from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    """Form to capture matching preferences."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key in ("focus_areas", "target_beneficiaries", "keywords"):
            value = self.initial.get(key)
            if isinstance(value, (list, tuple)):
                self.initial[key] = ", ".join(value)

    focus_areas = forms.CharField(
        required=False,
        help_text="Comma-separated list of topical focus areas.",
    )
    target_beneficiaries = forms.CharField(
        required=False,
        help_text="Comma-separated list of beneficiaries.",
    )
    keywords = forms.CharField(
        required=False,
        help_text="Comma-separated keywords that should boost matching.",
    )

    class Meta:
        model = Profile
        fields = [
            "organization_name",
            "organization_type",
            "mission_statement",
            "focus_areas",
            "target_beneficiaries",
            "location",
            "annual_budget_usd",
            "preferred_funding_type",
            "capacity_stage",
            "keywords",
            "matching_bucket_override",
        ]
        widgets = {
            "mission_statement": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_focus_areas(self) -> list[str]:
        data = self.cleaned_data.get("focus_areas", "")
        return _split_comma_list(data)

    def clean_target_beneficiaries(self) -> list[str]:
        data = self.cleaned_data.get("target_beneficiaries", "")
        return _split_comma_list(data)

    def clean_keywords(self) -> list[str]:
        data = self.cleaned_data.get("keywords", "")
        return _split_comma_list(data)


def _split_comma_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]
