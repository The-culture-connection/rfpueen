"""Views for the opportunity matching workflow."""
from __future__ import annotations

import json
from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView, UpdateView

from .forms import ProfileForm
from .models import OpportunityInteraction, Profile
from .services import (
    FirestoreService,
    build_opportunity_matches,
    discover_application_path,
)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "opportunities/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = getattr(user, "profile", None)
        firestore = FirestoreService()
        firebase_uid = getattr(profile, "firebase_uid", None)

        applied_ids: set[str] = set()
        saved_ids: set[str] = set()
        if firebase_uid:
            applied_ids = firestore.get_user_action_ids(firebase_uid, "applied")
            saved_ids = firestore.get_user_action_ids(firebase_uid, "saved")

        context.update(
            {
                "applied_count": len(applied_ids) or OpportunityInteraction.objects.filter(
                    user=user, action=OpportunityInteraction.ACTION_APPLY
                ).count(),
                "saved_count": len(saved_ids) or OpportunityInteraction.objects.filter(
                    user=user, action=OpportunityInteraction.ACTION_SAVE
                ).count(),
            }
        )
        return context


class OpportunityListView(LoginRequiredMixin, TemplateView):
    template_name = "opportunities/recommended_list.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = getattr(user, "profile", None)
        firestore = FirestoreService()
        firebase_profile = None

        bucket = None
        if profile:
            bucket = profile.matching_bucket_override or None
            if profile.firebase_uid:
                firebase_profile = firestore.get_profile(profile.firebase_uid)
                bucket = bucket or getattr(firebase_profile, "matching_bucket", None)

        bucket = bucket or self.request.GET.get("bucket")
        opportunities = firestore.get_opportunities(bucket=bucket)
        matches = build_opportunity_matches(
            profile=firebase_profile,
            fallback_profile=profile,
            opportunities=opportunities,
        )

        # Deduplicate by the highest score per opportunity id.
        unique_matches = {}
        for match in matches:
            key = match.opportunity.id
            if key not in unique_matches or unique_matches[key].score < match.score:
                unique_matches[key] = match

        serialized_matches = [_serialize_match(match) for match in unique_matches.values()]

        context.update(
            {
                "matches": serialized_matches,
                "matches_json": json.dumps(serialized_matches),
                "bucket": bucket,
            }
        )
        return context


class AppliedListView(LoginRequiredMixin, TemplateView):
    template_name = "opportunities/applied_list.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = getattr(user, "profile", None)
        firestore = FirestoreService()
        firebase_uid = getattr(profile, "firebase_uid", None)

        applied_ids: set[str] = set()
        if firebase_uid:
            applied_ids = firestore.get_user_action_ids(firebase_uid, "applied")

        interactions = OpportunityInteraction.objects.filter(
            user=user,
            action=OpportunityInteraction.ACTION_APPLY,
        ).order_by("-created_at")

        rows = [
            {
                "interaction": interaction,
                "metadata": interaction.metadata or {},
                "metadata_json": json.dumps(interaction.metadata or {}),
            }
            for interaction in interactions
        ]

        context.update(
            {
                "firebase_ids": applied_ids,
                "rows": rows,
            }
        )
        return context


class SavedListView(LoginRequiredMixin, TemplateView):
    template_name = "opportunities/saved_list.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = getattr(user, "profile", None)
        firestore = FirestoreService()
        firebase_uid = getattr(profile, "firebase_uid", None)

        saved_ids: set[str] = set()
        if firebase_uid:
            saved_ids = firestore.get_user_action_ids(firebase_uid, "saved")

        interactions = OpportunityInteraction.objects.filter(
            user=user,
            action=OpportunityInteraction.ACTION_SAVE,
        ).order_by("-created_at")

        rows = [
            {
                "interaction": interaction,
                "metadata": interaction.metadata or {},
                "metadata_json": json.dumps(interaction.metadata or {}),
            }
            for interaction in interactions
        ]

        context.update(
            {
                "firebase_ids": saved_ids,
                "rows": rows,
            }
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "opportunities/profile_form.html"
    form_class = ProfileForm
    success_url = reverse_lazy("opportunities:profile")

    def get_object(self, queryset=None):  # type: ignore[override]
        profile, _ = Profile.objects.get_or_create(
            user=self.request.user,
            defaults={"firebase_uid": self.request.user.username},
        )
        return profile

    def form_valid(self, form):  # type: ignore[override]
        messages.success(self.request, "Profile updated. Matching will refresh with new data.")
        return super().form_valid(form)


class OpportunityActionView(LoginRequiredMixin, View):
    """Handle apply/save/pass interactions via AJAX requests."""

    def post(self, request: HttpRequest, opportunity_id: str) -> HttpResponse:
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            payload = request.POST

        action = payload.get("action")
        match_meta = payload.get("match", {})

        if action not in {
            OpportunityInteraction.ACTION_APPLY,
            OpportunityInteraction.ACTION_SAVE,
            OpportunityInteraction.ACTION_PASS,
        }:
            return JsonResponse({"error": "Unsupported action"}, status=400)

        user = request.user
        profile = getattr(user, "profile", None)
        firestore = FirestoreService()

        metadata = {
            "win_rate": match_meta.get("win_rate"),
            "score": match_meta.get("score"),
            "confidence": match_meta.get("confidence"),
            "insights": match_meta.get("insights"),
            "title": match_meta.get("title"),
            "summary": match_meta.get("summary"),
            "funding_amount": match_meta.get("funding_amount"),
            "deadline": match_meta.get("deadline"),
            "location": match_meta.get("location"),
            "bucket": match_meta.get("bucket"),
            "tags": match_meta.get("tags"),
            "url": match_meta.get("url"),
            "actioned_at": timezone.now().isoformat(),
        }

        interaction, _ = OpportunityInteraction.objects.update_or_create(
            user=user,
            opportunity_id=opportunity_id,
            action=action,
            defaults={"metadata": metadata},
        )

        response_payload: dict[str, Any] = {
            "status": "ok",
            "action": action,
            "interaction_id": interaction.id,
        }

        if action == OpportunityInteraction.ACTION_APPLY:
            target_url = payload.get("url")
            if not target_url:
                target_url = match_meta.get("url")
            if target_url:
                app_path = discover_application_path(target_url)
                response_payload.update(app_path.as_dict())
                metadata.update(
                    {
                        "application_url": app_path.application_url,
                        "application_instructions": app_path.instructions,
                        "application_confidence": app_path.confidence,
                        "application_notes": app_path.notes,
                        "application_trace": app_path.visited_urls,
                    }
                )
            else:
                response_payload.update(
                    {
                        "application_url": None,
                        "instructions": [
                            "Opportunity URL not provided. Review the listing manually and locate the apply button.",
                        ],
                        "confidence": 0.1,
                        "notes": "No URL was available for automatic discovery.",
                    }
                )

        # Persist any metadata changes after apply discovery.
        if metadata != interaction.metadata:
            interaction.metadata = metadata
            interaction.save(update_fields=["metadata"])

        # Mirror to Firestore if we know the user there (after metadata finalize).
        firebase_uid = getattr(profile, "firebase_uid", None)
        if firebase_uid:
            firestore.record_user_action(firebase_uid, opportunity_id, action, metadata)

        return JsonResponse(response_payload)


@login_required
def home_redirect(request: HttpRequest) -> HttpResponse:
    return redirect("opportunities:recommendations")


def _serialize_match(match) -> dict[str, Any]:
    opportunity = match.opportunity
    return {
        "id": opportunity.id,
        "title": opportunity.title,
        "summary": opportunity.summary,
        "bucket": opportunity.bucket,
        "tags": opportunity.tags,
        "funding_amount": opportunity.funding_amount,
        "deadline": opportunity.deadline,
        "location": opportunity.location,
        "eligibility": opportunity.eligibility,
        "url": opportunity.url,
        "raw": opportunity.raw,
        "score": round(match.score, 3),
        "win_rate": round(match.win_rate, 1),
        "confidence": round(match.confidence, 2),
        "insights": [insight.__dict__ for insight in match.insights],
        "missing_criteria": match.missing_criteria,
    }
