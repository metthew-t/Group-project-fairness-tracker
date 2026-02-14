from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from accounts.models import User
from .models import Team, TeamMember
from .serializers import TeamSerializer, TeamMemberSerializer

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.teams.all()
    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['get', 'post'], url_path='members')
    def members(self, request, pk=None):
        team = self.get_object()
        if request.method == 'GET':
            members = TeamMember.objects.filter(team=team)
            serializer = TeamMemberSerializer(members, many=True)
            return Response(serializer.data)
        if request.method == 'POST':
            if not team.memberships.filter(user=request.user, role='LEAD').exists():
                return Response({'error': 'Only team leads can add members'}, status=status.HTTP_403_FORBIDDEN)
            user_id = request.data.get('user_id')
            role = request.data.get('role', 'MEMBER')
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            if team.memberships.filter(user=user).exists():
                return Response({'error': 'User already in team'}, status=status.HTTP_400_BAD_REQUEST)
            member = TeamMember.objects.create(team=team, user=user, role=role)
            serializer = TeamMemberSerializer(member)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='members/(?P<user_id>[^/.]+)')
    def remove_member(self, request, pk=None, user_id=None):
        team = self.get_object()
        if not team.memberships.filter(user=request.user, role='LEAD').exists():
            return Response({'error': 'Only team leads can remove members'}, status=status.HTTP_403_FORBIDDEN)
        member = get_object_or_404(TeamMember, team=team, user_id=user_id)
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='join/(?P<code>[^/.]+)')
    def join_by_code(self, request, code=None):
        team = get_object_or_404(Team, join_code=code)
        if team.memberships.filter(user=request.user).exists():
            return Response({'error': 'Already a member'}, status=status.HTTP_400_BAD_REQUEST)
        TeamMember.objects.create(team=team, user=request.user, role='MEMBER')
        return Response({'message': 'Joined successfully'}, status=status.HTTP_200_OK)