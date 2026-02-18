from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from teams.models import Team
from projects.models import Project
from .models import TeamAnalytics
from .serializers import TeamAnalyticsSerializer
from .utils import calculate_team_analytics

class AnalyticsViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TeamAnalytics.objects.filter(team__members=self.request.user)

    @action(detail=False, url_path='team/(?P<team_id>[^/.]+)')
    def team_analytics(self, request, team_id=None):
        team = get_object_or_404(Team, id=team_id, members=request.user)
        recalc = request.query_params.get('recalculate', 'false').lower() == 'true'
        if recalc:
            analytics = calculate_team_analytics(team)
        else:
            analytics = TeamAnalytics.objects.filter(team=team).first()
            if not analytics:
                analytics = calculate_team_analytics(team)
        if not analytics:
            return Response({"detail": "No data yet."}, status=404)
        serializer = TeamAnalyticsSerializer(analytics)
        return Response(serializer.data)

    @action(detail=False, url_path='project/(?P<project_id>[^/.]+)')
    def project_analytics(self, request, project_id=None):
        project = get_object_or_404(Project, id=project_id, team__members=request.user)
        # For a project, we could aggregate contributions from tasks in that project
        # Simplified: we can create a separate model or just return contribution breakdown
        # Let's just return a simple aggregate
        from contributions.models import Contribution
        from django.db.models import Sum
        data = Contribution.objects.filter(
            task__project=project,
            status='approved'
        ).values('user__email').annotate(total_hours=Sum('hours_spent'))
        return Response(data)

    @action(detail=False, url_path='user/(?P<user_id>[^/.]+)')
    def user_history(self, request, user_id=None):
        # Ensure user is requesting their own or is instructor? We'll just allow if same user or team lead?
        if request.user.id != int(user_id) and not request.user.is_staff:
            return Response({"error": "Permission denied."}, status=403)
        from contributions.models import Contribution
        contributions = Contribution.objects.filter(user_id=user_id, status='approved')
        serializer = ContributionSerializer(contributions, many=True)
        return Response(serializer.data)