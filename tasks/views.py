from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Task
from .serializers import TaskSerializer
from projects.models import Project
from accounts.models import CustomUser

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_teams = self.request.user.teams.all()
        projects = Project.objects.filter(team__in=user_teams)
        return Task.objects.filter(project__in=projects)

    def perform_create(self, serializer):
        project_id = self.request.data.get('project')
        project = get_object_or_404(Project, id=project_id)
        if not project.team.memberships.filter(user=self.request.user).exists():
            raise permissions.PermissionDenied("You are not a member of this team.")
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='assign')
    def assign_users(self, request, pk=None):
        task = self.get_object()
        if not task.project.team.memberships.filter(user=request.user).exists():
            return Response({'error': 'Not a team member'}, status=status.HTTP_403_FORBIDDEN)
        user_ids = request.data.get('user_ids', [])
        if not isinstance(user_ids, list):
            return Response({'error': 'user_ids must be a list'}, status=status.HTTP_400_BAD_REQUEST)
        users = CustomUser.objects.filter(id__in=user_ids)
        team = task.project.team
        valid_users = [u for u in users if team.memberships.filter(user=u).exists()]
        task.assigned_to.add(*valid_users)
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='unassign')
    def unassign_users(self, request, pk=None):
        task = self.get_object()
        if not task.project.team.memberships.filter(user=request.user).exists():
            return Response({'error': 'Not a team member'}, status=status.HTTP_403_FORBIDDEN)
        user_ids = request.data.get('user_ids', [])
        if not isinstance(user_ids, list):
            return Response({'error': 'user_ids must be a list'}, status=status.HTTP_400_BAD_REQUEST)
        task.assigned_to.remove(*user_ids)
        serializer = self.get_serializer(task)
        return Response(serializer.data)