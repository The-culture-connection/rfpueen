"""
URL Configuration for Opportunities App
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet)
router.register(r'opportunities', views.OpportunityViewSet, basename='opportunity')
router.register(r'applied', views.AppliedOpportunityViewSet, basename='applied')
router.register(r'saved', views.SavedOpportunityViewSet, basename='saved')

urlpatterns = [
    path('', include(router.urls)),
    path('health/', views.health_check, name='health_check'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
]
