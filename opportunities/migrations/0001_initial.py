"""Initial migration for opportunities app."""
from __future__ import annotations

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("firebase_uid", models.CharField(help_text="UID in Firebase authentication, required for Firestore lookups.", max_length=128, unique=True)),
                ("organization_name", models.CharField(blank=True, max_length=255)),
                ("organization_type", models.CharField(blank=True, max_length=100)),
                ("mission_statement", models.TextField(blank=True)),
                ("focus_areas", models.JSONField(blank=True, default=list, help_text="List of thematic areas such as 'STEM', 'Arts', 'Community Health'.")),
                ("target_beneficiaries", models.JSONField(blank=True, default=list, help_text="List of audiences served, e.g. ['youth', 'women', 'rural'].")),
                ("location", models.CharField(blank=True, help_text="Primary geography for the organization.", max_length=150)),
                ("annual_budget_usd", models.PositiveIntegerField(blank=True, help_text="Approximate annual budget in USD for sizing opportunities.", null=True, validators=[django.core.validators.MinValueValidator(1000)])),
                ("preferred_funding_type", models.CharField(blank=True, max_length=100)),
                ("keywords", models.JSONField(blank=True, default=list, help_text="Additional keywords that should boost match scoring.")),
                ("capacity_stage", models.CharField(blank=True, help_text="Stage such as 'startup', 'growth', 'scale'.", max_length=100)),
                ("matching_bucket_override", models.CharField(blank=True, help_text="Force algorithm to use a specific bucket of opportunities.", max_length=100)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["user__username"],
            },
        ),
        migrations.CreateModel(
            name="OpportunityInteraction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("opportunity_id", models.CharField(max_length=255)),
                ("action", models.CharField(choices=[("apply", "Applied"), ("save", "Saved"), ("pass", "Passed")], max_length=10)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="opportunity_actions", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name="opportunityinteraction",
            index=models.Index(fields=["user", "action"], name="opportunit_user_id_5b47fa_idx"),
        ),
        migrations.AddIndex(
            model_name="opportunityinteraction",
            index=models.Index(fields=["opportunity_id"], name="opportunit_opportu_1a886b_idx"),
        ),
        migrations.AddConstraint(
            model_name="opportunityinteraction",
            constraint=models.UniqueConstraint(fields=("user", "opportunity_id", "action"), name="unique_action_per_opportunity"),
        ),
    ]
