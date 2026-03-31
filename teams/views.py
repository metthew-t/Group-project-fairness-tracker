from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from accounts.models import CustomUser
from .models import Team, TeamMember
from .serializers import TeamSerializer, TeamMemberSerializer

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Team.objects.filter(memberships__user=self.request.user)
    def perform_create(self, serializer):
        from rest_framework.exceptions import PermissionDenied
        user = self.request.user
        if user.user_type not in ['TEAM_LEAD', 'INSTRUCTOR']:
            raise PermissionDenied(f"Access Denied: Your current role is {user.user_type}. Only Team Leads or Instructors can create teams.")
        serializer.save(created_by=user)

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
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
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

    @action(detail=False, methods=['post'], url_path='join')
    def join_by_code(self, request):
        code = request.data.get('join_code')
        if not code:
            return Response({'error': 'Join code required'}, status=status.HTTP_400_BAD_REQUEST)
        team = get_object_or_404(Team, join_code=code)
        if team.memberships.filter(user=request.user).exists():
            return Response({'error': 'Already a member of this team'}, status=status.HTTP_400_BAD_REQUEST)
        TeamMember.objects.create(team=team, user=request.user, role='MEMBER')
        return Response({'message': f'Successfully joined {team.name}'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='members/(?P<user_id>[^/.]+)/promote')
    def promote_member(self, request, pk=None, user_id=None):
        team = self.get_object()
        if not team.memberships.filter(user=request.user, role='LEAD').exists():
            return Response({'error': 'Only team leads can promote members'}, status=status.HTTP_403_FORBIDDEN)
        member = get_object_or_404(TeamMember, team=team, user_id=user_id)
        member.role = 'LEAD'
        member.save()
        return Response({'message': f'{member.user.username} promoted to Lead'})