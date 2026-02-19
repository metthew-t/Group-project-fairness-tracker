from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied  # <-- correct import
from django.shortcuts import get_object_or_404
from .models import Project
from .serializers import ProjectSerializer
from teams.models import Team

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_teams = Team.objects.filter(memberships__user=self.request.user)
        return Project.objects.filter(team__in=user_teams)

    def perform_create(self, serializer):
        team_id = self.request.data.get('team')
        team = get_object_or_404(Team, id=team_id)
        if not team.memberships.filter(user=self.request.user).exists():
            raise PermissionDenied("You are not a member of this team.")  # <-- fixed
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['patch'], url_path='status')
    def set_status(self, request, pk=None):
        project = self.get_object()
        if not project.team.memberships.filter(user=request.user).exists():
            return Response({'error': 'Not a team member'}, status=status.HTTP_403_FORBIDDEN)
        new_status = request.data.get('status')
        if new_status not in dict(Project.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        project.status = new_status
        project.save()
        serializer = self.get_serializer(project)
        return Response(serializer.data)