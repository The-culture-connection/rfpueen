"""rfpueen URL Configuration."""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("opportunities.urls", namespace="opportunities")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("dashboard/", RedirectView.as_view(pattern_name="opportunities:dashboard", permanent=False)),
]
