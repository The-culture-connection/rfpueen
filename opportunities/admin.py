"""
Django Admin Configuration
"""
from django.contrib import admin
from .models import (
    UserProfile, Opportunity, AppliedOpportunity, 
    SavedOpportunity, ApplicationFormCache
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'organization', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['email', 'organization']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ['title', 'collection', 'agency', 'close_date', 'last_synced']
    list_filter = ['collection', 'close_date', 'last_synced']
    search_fields = ['title', 'agency', 'description']
    readonly_fields = ['firebase_id', 'last_synced']
    date_hierarchy = 'close_date'


@admin.register(AppliedOpportunity)
class AppliedOpportunityAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'agency', 'match_score', 'win_rate', 'applied_at']
    list_filter = ['collection', 'applied_at']
    search_fields = ['title', 'agency', 'user__email']
    readonly_fields = ['applied_at']
    date_hierarchy = 'applied_at'


@admin.register(SavedOpportunity)
class SavedOpportunityAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'agency', 'match_score', 'saved_at']
    list_filter = ['collection', 'saved_at']
    search_fields = ['title', 'agency', 'user__email']
    readonly_fields = ['saved_at']
    date_hierarchy = 'saved_at'


@admin.register(ApplicationFormCache)
class ApplicationFormCacheAdmin(admin.ModelAdmin):
    list_display = ['opportunity_url', 'is_valid', 'last_checked']
    list_filter = ['is_valid', 'last_checked']
    search_fields = ['opportunity_url', 'application_url']
    readonly_fields = ['last_checked']
