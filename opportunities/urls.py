from django.urls import path
from . import views

app_name = 'opportunities'

urlpatterns = [
    # HTML Pages
    path('', views.index, name='index'),
    path('explore/', views.explore, name='explore'),
    path('applied/', views.applied, name='applied'),
    path('saved/', views.saved, name='saved'),
    
    # API Endpoints
    path('api/auth/verify/', views.auth_verify, name='auth_verify'),
    path('api/match/', views.match_opportunities, name='match_opportunities'),
    path('api/apply/', views.apply_opportunity, name='apply_opportunity'),
    path('api/save/', views.save_opportunity, name='save_opportunity'),
    path('api/pass/', views.pass_opportunity, name='pass_opportunity'),
    path('api/applications/', views.get_applications, name='get_applications'),
    path('api/saved/', views.get_saved, name='get_saved'),
]
