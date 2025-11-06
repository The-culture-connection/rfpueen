"""Admin registrations for opportunities app."""
from django.contrib import admin

from .models import OpportunityInteraction, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "firebase_uid",
        "organization_name",
        "organization_type",
        "location",
    )
    search_fields = (
        "user__username",
        "user__email",
        "firebase_uid",
        "organization_name",
    )
    readonly_fields = ("firebase_uid",)


@admin.register(OpportunityInteraction)
class OpportunityInteractionAdmin(admin.ModelAdmin):
    list_display = ("user", "opportunity_id", "action", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("user__username", "opportunity_id")
