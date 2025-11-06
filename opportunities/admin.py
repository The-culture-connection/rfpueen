from django.contrib import admin
from .models import UserProfile, Opportunity, AppliedOpportunity, SavedOpportunity


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization_name', 'funding_types', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'organization_name']


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ['title', 'agency', 'collection', 'close_date', 'urgency_bucket', 'application_form_found']
    list_filter = ['collection', 'application_form_found', 'created_at']
    search_fields = ['title', 'description', 'agency', 'department']
    readonly_fields = ['created_at', 'updated_at', 'last_scanned_at']


@admin.register(AppliedOpportunity)
class AppliedOpportunityAdmin(admin.ModelAdmin):
    list_display = ['user', 'opportunity', 'win_rate', 'applied_at']
    list_filter = ['applied_at', 'win_rate']
    search_fields = ['user__username', 'opportunity__title']
    readonly_fields = ['applied_at']


@admin.register(SavedOpportunity)
class SavedOpportunityAdmin(admin.ModelAdmin):
    list_display = ['user', 'opportunity', 'saved_at']
    list_filter = ['saved_at']
    search_fields = ['user__username', 'opportunity__title']
    readonly_fields = ['saved_at']
