from datetime import date
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import TeamAnalytics
from .serializers import TeamAnalyticsSerializer
from .utils import calculate_team_analytics
from teams.models import Team, TeamMember
from projects.models import Project

class TeamAnalyticsViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TeamAnalyticsSerializer

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'INSTRUCTOR':
            return TeamAnalytics.objects.filter(project__administrator=user)
        return TeamAnalytics.objects.filter(team__memberships__user=user)

    def retrieve_team(self, request, team_id=None):
        team = get_object_or_404(Team, id=team_id)
        is_member = TeamMember.objects.filter(team=team, user=request.user).exists()
        is_instructor = team.projects.filter(administrator=request.user).exists()
        if not (is_member or is_instructor):
            return Response({'error': 'Not a member or assigned instructor'}, status=status.HTTP_403_FORBIDDEN)
        analytics = TeamAnalytics.objects.filter(team=team, project=None, date=date.today()).first()
        if not analytics:
            data = calculate_team_analytics(team)
            analytics = TeamAnalytics.objects.create(team=team, **data)
        serializer = self.get_serializer(analytics)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def user_history(self, request, user_id=None):
        from contributions.models import Contribution
        from contributions.serializers import ContributionSerializer
        contributions = Contribution.objects.filter(user_id=user_id)
        serializer = ContributionSerializer(contributions, many=True)
        return Response(serializer.data)

    def retrieve_project(self, request, project_id=None):
        project = get_object_or_404(Project, id=project_id)
        is_member = TeamMember.objects.filter(team=project.team, user=request.user).exists()
        is_instructor = (project.administrator == request.user)
        if not (is_member or is_instructor):
            return Response({'error': 'Not a member or assigned instructor'}, status=status.HTTP_403_FORBIDDEN)
        analytics = TeamAnalytics.objects.filter(team=project.team, project=project, date=date.today()).first()
        if not analytics:
            data = calculate_team_analytics(project.team, project)
            analytics = TeamAnalytics.objects.create(team=project.team, project=project, **data)
        serializer = self.get_serializer(analytics)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='export-csv')
    def export_csv(self, request, pk=None):
        import csv
        from django.http import HttpResponse
        from contributions.models import Contribution
        
        team = get_object_or_404(Team, id=pk)
        is_member = TeamMember.objects.filter(team=team, user=request.user).exists()
        is_instructor = team.projects.filter(administrator=request.user).exists()
        if not (is_member or is_instructor):
            return Response({'error': 'Not a member or assigned instructor'}, status=status.HTTP_403_FORBIDDEN)
            
        contributions = Contribution.objects.filter(task__project__team=team)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="fairness_report_{team.id}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Task', 'User', 'Work Type', 'Hours', 'Difficulty', 'Status', 'Date'])
        
        for c in contributions:
            writer.writerow([
                c.task.title,
                c.user.username,
                c.work_type,
                c.hours_spent,
                c.difficulty,
                c.status,
                c.created_at.strftime('%Y-%m-%d %H:%M')
            ])
            
        return response