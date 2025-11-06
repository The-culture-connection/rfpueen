from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    """User profile with matching preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField()
    funding_types = models.JSONField(default=list)  # ['Contracts', 'Grants', 'RFPs', 'Bids']
    interests_main = models.JSONField(default=list)  # Main keywords
    interests_sub = models.JSONField(default=list)  # Sub-interest keywords
    location = models.CharField(max_length=255, blank=True)
    organization = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile: {self.email}"
    
    class Meta:
        db_table = 'user_profiles'


class Opportunity(models.Model):
    """Cached opportunity data from Firebase"""
    firebase_id = models.CharField(max_length=255, unique=True)
    collection = models.CharField(max_length=100)  # SAM, grants.gov, etc.
    title = models.TextField()
    description = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    agency = models.CharField(max_length=500, blank=True)
    department = models.CharField(max_length=500, blank=True)
    url = models.URLField(max_length=1000, blank=True)
    synopsis_url = models.URLField(max_length=1000, blank=True)
    application_url = models.URLField(max_length=1000, blank=True)
    open_date = models.DateField(null=True, blank=True)
    close_date = models.DateField(null=True, blank=True)
    posted_date = models.DateField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    place = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=100, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    data = models.JSONField(default=dict)  # Store all raw data
    last_synced = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.collection}: {self.title[:50]}"
    
    class Meta:
        db_table = 'opportunities'
        indexes = [
            models.Index(fields=['collection']),
            models.Index(fields=['close_date']),
            models.Index(fields=['deadline']),
        ]


class AppliedOpportunity(models.Model):
    """Track opportunities user has applied to"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applied_opportunities')
    opportunity_id = models.CharField(max_length=255)  # Firebase ID
    collection = models.CharField(max_length=100)
    title = models.TextField()
    agency = models.CharField(max_length=500)
    url = models.URLField(max_length=1000, blank=True)
    application_url = models.URLField(max_length=1000, blank=True)
    application_instructions = models.TextField(blank=True)
    match_score = models.IntegerField(default=0)
    win_rate = models.FloatField(default=0.0)
    win_rate_reasoning = models.JSONField(default=dict)
    data = models.JSONField(default=dict)
    applied_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.email} applied to {self.title[:30]}"
    
    class Meta:
        db_table = 'applied_opportunities'
        unique_together = ['user', 'opportunity_id']
        ordering = ['-applied_at']


class SavedOpportunity(models.Model):
    """Track opportunities user has saved for later"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_opportunities')
    opportunity_id = models.CharField(max_length=255)  # Firebase ID
    collection = models.CharField(max_length=100)
    title = models.TextField()
    agency = models.CharField(max_length=500)
    url = models.URLField(max_length=1000, blank=True)
    match_score = models.IntegerField(default=0)
    data = models.JSONField(default=dict)
    saved_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.user.email} saved {self.title[:30]}"
    
    class Meta:
        db_table = 'saved_opportunities'
        unique_together = ['user', 'opportunity_id']
        ordering = ['-saved_at']


class ApplicationFormCache(models.Model):
    """Cache discovered application form URLs"""
    opportunity_url = models.URLField(max_length=1000, unique=True)
    application_url = models.URLField(max_length=1000, blank=True)
    form_path = models.TextField(blank=True)  # Navigation path to form
    last_checked = models.DateTimeField(auto_now=True)
    is_valid = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Form cache for {self.opportunity_url[:50]}"
    
    class Meta:
        db_table = 'application_form_cache'
