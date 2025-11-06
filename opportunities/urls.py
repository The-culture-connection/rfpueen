"""URL configuration for the opportunities app."""
from django.urls import path

from . import views


app_name = "opportunities"


urlpatterns = [
    path("", views.home_redirect, name="home"),
    path("dashboard", views.DashboardView.as_view(), name="dashboard"),
    path("recommendations", views.OpportunityListView.as_view(), name="recommendations"),
    path("applied", views.AppliedListView.as_view(), name="applied"),
    path("saved", views.SavedListView.as_view(), name="saved"),
    path("profile", views.ProfileUpdateView.as_view(), name="profile"),
    path(
        "opportunities/<str:opportunity_id>/action",
        views.OpportunityActionView.as_view(),
        name="opportunity-action",
    ),
]
