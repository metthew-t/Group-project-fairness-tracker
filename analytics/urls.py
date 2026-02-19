from django.urls import path
from .views import TeamAnalyticsViewSet

urlpatterns = [
    path('teams/<int:team_id>/analytics/', TeamAnalyticsViewSet.as_view({'get': 'retrieve_team'}), name='team-analytics'),
    path('projects/<int:project_id>/analytics/', TeamAnalyticsViewSet.as_view({'get': 'retrieve_project'}), name='project-analytics'),
]