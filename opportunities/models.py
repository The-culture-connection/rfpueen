from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    """User profile with matching preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    firebase_uid = models.CharField(max_length=255, unique=True, null=True, blank=True)
    
    # Funding preferences
    funding_types = models.JSONField(default=list, help_text="List of funding types: Contracts, Grants, RFPs, Bids")
    
    # Interests for matching
    interests_main = models.JSONField(default=list, help_text="Main interest keywords")
    interests_sub = models.JSONField(default=list, help_text="Sub interest keywords")
    grants_by_interest = models.JSONField(default=list, help_text="Grants by interest")
    
    # Additional profile data
    organization_name = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - Profile"


class Opportunity(models.Model):
    """Opportunity from Firebase"""
    firebase_id = models.CharField(max_length=255, unique=True)
    collection = models.CharField(max_length=100, help_text="Firebase collection name")
    
    # Basic info
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    
    # Agency/Organization
    agency = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    
    # Dates
    open_date = models.DateField(null=True, blank=True)
    posted_date = models.DateField(null=True, blank=True)
    close_date = models.DateField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    
    # Location
    place = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    
    # URLs
    url = models.URLField(blank=True)
    synopsis_url = models.URLField(blank=True)
    link = models.URLField(blank=True)
    application_url = models.URLField(blank=True, null=True)
    
    # Contact info
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    
    # Application form detection
    application_form_found = models.BooleanField(default=False)
    application_form_url = models.URLField(blank=True, null=True)
    application_instructions = models.TextField(blank=True)
    
    # Raw data from Firebase
    raw_data = models.JSONField(default=dict)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_scanned_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Opportunities"
        ordering = ['-close_date', '-deadline']
    
    def __str__(self):
        return self.title
    
    @property
    def urgency_bucket(self):
        """Calculate urgency bucket: urgent, soon, or ongoing"""
        deadline = self.close_date or self.deadline
        if not deadline:
            return "ongoing"
        
        days_until = (deadline - timezone.now().date()).days
        if days_until <= 30:
            return "urgent"
        elif days_until <= 92:
            return "soon"
        return "ongoing"


class AppliedOpportunity(models.Model):
    """Opportunities user has applied to"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applied_opportunities')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='applications')
    firebase_opportunity_id = models.CharField(max_length=255, help_text="Original Firebase ID")
    firebase_collection = models.CharField(max_length=100)
    
    # Application details
    application_url = models.URLField(blank=True, null=True)
    application_instructions = models.TextField(blank=True)
    
    # Match quality metrics
    match_score = models.FloatField(null=True, blank=True, help_text="Original matching score")
    win_rate = models.FloatField(null=True, blank=True, help_text="Calculated win rate percentage")
    win_rate_reasoning = models.TextField(blank=True, help_text="Explanation of win rate calculation")
    
    applied_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Applied Opportunities"
        unique_together = ['user', 'firebase_opportunity_id']
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.opportunity.title}"


class SavedOpportunity(models.Model):
    """Opportunities saved for later"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_opportunities')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='saved_by')
    firebase_opportunity_id = models.CharField(max_length=255)
    firebase_collection = models.CharField(max_length=100)
    
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Saved Opportunities"
        unique_together = ['user', 'firebase_opportunity_id']
        ordering = ['-saved_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.opportunity.title}"
