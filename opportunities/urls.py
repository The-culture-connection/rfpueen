from django.urls import path
from . import views

app_name = 'opportunities'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('explore/', views.explore, name='explore'),
    path('dashboard-applied/', views.dashboard_applied, name='dashboard_applied'),
    path('dashboard-saved/', views.dashboard_saved, name='dashboard_saved'),
    path('api/match/', views.api_match_opportunities, name='api_match'),
    path('api/apply/<str:opp_id>/', views.api_apply, name='api_apply'),
    path('api/save/<str:opp_id>/', views.api_save, name='api_save'),
    path('api/pass/<str:opp_id>/', views.api_pass, name='api_pass'),
    path('api/remove-applied/<str:opp_id>/', views.api_remove_applied, name='api_remove_applied'),
    path('api/remove-saved/<str:opp_id>/', views.api_remove_saved, name='api_remove_saved'),
    path('api/find-application-form/', views.api_find_application_form, name='api_find_form'),
]
