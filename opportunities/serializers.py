"""
Django REST Framework Serializers
"""
from rest_framework import serializers
from .models import UserProfile, AppliedOpportunity, SavedOpportunity, ApplicationFormCache


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'id', 'email', 'funding_types', 'interests_main', 
            'interests_sub', 'location', 'organization', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class AppliedOpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AppliedOpportunity
        fields = [
            'id', 'opportunity_id', 'collection', 'title', 'agency',
            'url', 'application_url', 'application_instructions',
            'match_score', 'win_rate', 'win_rate_reasoning',
            'data', 'applied_at'
        ]
        read_only_fields = ['applied_at']


class SavedOpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedOpportunity
        fields = [
            'id', 'opportunity_id', 'collection', 'title', 'agency',
            'url', 'match_score', 'data', 'saved_at'
        ]
        read_only_fields = ['saved_at']


class OpportunitySerializer(serializers.Serializer):
    """Serializer for opportunity data from Firebase"""
    id = serializers.CharField()
    collection = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    summary = serializers.CharField(required=False, allow_blank=True)
    agency = serializers.CharField(required=False, allow_blank=True)
    department = serializers.CharField(required=False, allow_blank=True)
    url = serializers.URLField(required=False, allow_blank=True)
    synopsisUrl = serializers.URLField(required=False, allow_blank=True)
    link = serializers.URLField(required=False, allow_blank=True)
    openDate = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    closeDate = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    postedDate = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    deadline = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    place = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    contactEmail = serializers.EmailField(required=False, allow_blank=True)
    contactPhone = serializers.CharField(required=False, allow_blank=True)
    match_score = serializers.IntegerField(required=False)
    match_details = serializers.JSONField(required=False)
    win_rate = serializers.FloatField(required=False)
    win_rate_reasoning = serializers.JSONField(required=False)
    urgency = serializers.CharField(required=False)


class ApplicationFormCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationFormCache
        fields = [
            'id', 'opportunity_url', 'application_url', 'form_path',
            'last_checked', 'is_valid', 'notes'
        ]
        read_only_fields = ['last_checked']
