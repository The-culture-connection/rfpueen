from django.contrib import admin
from .models import (
    UserProfile, Opportunity, OpportunityMatch,
    Application, SavedOpportunity, ApplicationPathway
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization_name', 'total_applied', 'total_saved', 'created_at')
    search_fields = ('user__email', 'user__username', 'organization_name', 'firebase_uid')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'collection_name', 'agency', 'close_date', 'urgency_bucket', 'created_at')
    search_fields = ('title', 'agency', 'department', 'firebase_id')
    list_filter = ('collection_name', 'close_date', 'created_at')
    readonly_fields = ('firebase_id', 'last_synced', 'created_at')
    

@admin.register(OpportunityMatch)
class OpportunityMatchAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'opportunity', 'relevance_score', 'win_rate', 'is_dismissed', 'created_at')
    search_fields = ('user_profile__user__email', 'opportunity__title')
    list_filter = ('is_viewed', 'is_dismissed', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'opportunity', 'status', 'applied_at')
    search_fields = ('user_profile__user__email', 'opportunity__title')
    list_filter = ('status', 'applied_at')
    readonly_fields = ('applied_at', 'updated_at')


@admin.register(SavedOpportunity)
class SavedOpportunityAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'opportunity', 'saved_at')
    search_fields = ('user_profile__user__email', 'opportunity__title')
    list_filter = ('saved_at',)
    readonly_fields = ('saved_at',)


@admin.register(ApplicationPathway)
class ApplicationPathwayAdmin(admin.ModelAdmin):
    list_display = ('opportunity', 'confidence_score', 'is_active', 'last_verified')
    search_fields = ('opportunity__title', 'application_url')
    list_filter = ('is_active', 'created_at', 'last_verified')
    readonly_fields = ('created_at', 'last_verified')
