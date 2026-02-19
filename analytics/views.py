from datetime import date
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import TeamAnalytics
from .serializers import TeamAnalyticsSerializer
from .utils import calculate_team_analytics
from teams.models import Team
from projects.models import Project

class TeamAnalyticsViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TeamAnalyticsSerializer

    def get_queryset(self):
        return TeamAnalytics.objects.filter(team__members=self.request.user)

    def retrieve_team(self, request, team_id=None):
        team = get_object_or_404(Team, id=team_id)
        if not team.members.filter(id=request.user.id).exists():
            return Response({'error': 'Not a member'}, status=status.HTTP_403_FORBIDDEN)
        # Check if we have cached analytics for today
        analytics = TeamAnalytics.objects.filter(team=team, project=None, date=date.today()).first()
        if not analytics:
            data = calculate_team_analytics(team)
            analytics = TeamAnalytics.objects.create(team=team, **data)
        serializer = self.get_serializer(analytics)
        return Response(serializer.data)

    def retrieve_project(self, request, project_id=None):
        project = get_object_or_404(Project, id=project_id)
        if not project.team.members.filter(id=request.user.id).exists():
            return Response({'error': 'Not a member'}, status=status.HTTP_403_FORBIDDEN)
        analytics = TeamAnalytics.objects.filter(team=project.team, project=project, date=date.today()).first()
        if not analytics:
            data = calculate_team_analytics(project.team, project)
            analytics = TeamAnalytics.objects.create(team=project.team, project=project, **data)
        serializer = self.get_serializer(analytics)
        return Response(serializer.data)