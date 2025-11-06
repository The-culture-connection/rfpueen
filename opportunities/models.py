from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Extended user profile with matching preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    firebase_uid = models.CharField(max_length=128, unique=True, null=True, blank=True)
    
    organization_name = models.CharField(max_length=255, blank=True)
    organization_type = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    
    funding_types = models.JSONField(default=list, blank=True)
    interests_main = models.JSONField(default=list, blank=True)
    interests_sub = models.JSONField(default=list, blank=True)
    
    total_applied = models.IntegerField(default=0)
    total_saved = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - Profile"
    
    class Meta:
        db_table = 'user_profiles'


class Opportunity(models.Model):
    """Opportunity model synced from Firebase"""
    firebase_id = models.CharField(max_length=255, unique=True)
    collection_name = models.CharField(max_length=100)
    
    title = models.TextField()
    description = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    
    agency = models.CharField(max_length=255, blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    
    posted_date = models.DateField(null=True, blank=True)
    close_date = models.DateField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    place = models.CharField(max_length=255, blank=True, null=True)
    
    url = models.URLField(max_length=1000, blank=True, null=True)
    synopsis_url = models.URLField(max_length=1000, blank=True, null=True)
    link = models.URLField(max_length=1000, blank=True, null=True)
    
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=50, blank=True, null=True)
    
    extra_data = models.JSONField(default=dict, blank=True)
    
    last_synced = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title[:50]} ({self.collection_name})"
    
    @property
    def urgency_bucket(self):
        if not self.close_date and not self.deadline:
            return "ongoing"
        
        from datetime import datetime
        deadline = self.close_date or self.deadline
        days_until = (deadline - datetime.now().date()).days
        
        if days_until <= 30:
            return "urgent"
        elif days_until <= 92:
            return "soon"
        return "ongoing"
    
    class Meta:
        db_table = 'opportunities'
        ordering = ['-posted_date']
        indexes = [
            models.Index(fields=['collection_name']),
            models.Index(fields=['close_date']),
            models.Index(fields=['firebase_id']),
        ]


class OpportunityMatch(models.Model):
    """Stores matched opportunities for users with relevance scores"""
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='matches')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='matches')
    
    relevance_score = models.FloatField(default=0.0)
    win_rate = models.FloatField(default=0.0)
    win_rate_reasoning = models.JSONField(default=dict, blank=True)
    
    is_viewed = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'opportunity_matches'
        unique_together = [['user_profile', 'opportunity']]
        ordering = ['-relevance_score', '-created_at']


class Application(models.Model):
    """Tracks user applications"""
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='applications')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='applications')
    
    application_url = models.URLField(max_length=1000, blank=True, null=True)
    application_instructions = models.TextField(blank=True, null=True)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('in_review', 'In Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    user_notes = models.TextField(blank=True, null=True)
    
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'applications'
        unique_together = [['user_profile', 'opportunity']]
        ordering = ['-applied_at']


class SavedOpportunity(models.Model):
    """Tracks saved opportunities"""
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='saved_opportunities')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='saved_by')
    
    user_notes = models.TextField(blank=True, null=True)
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'saved_opportunities'
        unique_together = [['user_profile', 'opportunity']]
        ordering = ['-saved_at']


class ApplicationPathway(models.Model):
    """Stores application pathway information"""
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='pathways')
    
    application_url = models.URLField(max_length=1000)
    pathway_steps = models.JSONField(default=list)
    confidence_score = models.FloatField(default=0.0)
    
    last_verified = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'application_pathways'
        ordering = ['-confidence_score']
