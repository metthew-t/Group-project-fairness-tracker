from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Project
from .serializers import ProjectSerializer
from teams.models import Team

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'STUDENT':
            return Project.objects.filter(team__memberships__user=user)
        elif user.user_type == 'TEAM_LEAD':
            return Project.objects.filter(team__memberships__user=user, team__memberships__role='LEAD')
        elif user.user_type == 'INSTRUCTOR':
            # Instructors see projects they are assigned as administrator
            return Project.objects.filter(administrator=user)
        return Project.objects.none()

    def perform_create(self, serializer):
        team_id = self.request.data.get('team')
        team = get_object_or_404(Team, id=team_id)
        if not team.memberships.filter(user=self.request.user, role='LEAD').exists():
            raise PermissionDenied("Only Team Leads can create projects.")
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['patch'], url_path='status')
    def set_status(self, request, pk=None):
        project = self.get_object()
        if not project.team.memberships.filter(user=request.user, role='LEAD').exists():
            return Response({'error': 'Only Team Leads can change status'}, status=status.HTTP_403_FORBIDDEN)
        new_status = request.data.get('status')
        if new_status not in dict(Project.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        project.status = new_status
        project.save()
        serializer = self.get_serializer(project)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'], url_path='tasks')
    def project_tasks(self, request, pk=None):
        project = self.get_object()
        from tasks.models import Task
        from tasks.serializers import TaskSerializer

        if request.method == 'GET':
            tasks = Task.objects.filter(project=project)
            serializer = TaskSerializer(tasks, many=True)
            return Response(serializer.data)

        if request.method == 'POST':
            if not project.team.memberships.filter(user=request.user, role='LEAD').exists():
                return Response({'error': 'Only Team Leads can create tasks'}, status=status.HTTP_403_FORBIDDEN)
            serializer = TaskSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(project=project, created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='download-merged')
    def download_merged(self, request, pk=None):
        project = self.get_object()
        from .utils import merge_project_files
        from django.http import HttpResponse
        
        buffer = merge_project_files(project)
        response = HttpResponse(buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="project_{project.id}_merged.zip"'
        return response
