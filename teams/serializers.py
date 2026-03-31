from rest_framework import serializers
from .models import Team, TeamMember
from accounts.serializers import UserSerializer

class TeamMemberSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = TeamMember
        fields = ['id', 'user', 'user_details', 'role', 'joined_at']
        extra_kwargs = {'user': {'write_only': True}}

class TeamSerializer(serializers.ModelSerializer):
    members = TeamMemberSerializer(source='memberships', many=True, read_only=True)
    created_by_username = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'join_code', 'created_by', 'created_by_username',
                  'created_at', 'members']
        read_only_fields = ['join_code', 'created_by', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['created_by'] = request.user
        team = super().create(validated_data)
        role = 'LEAD' if request.user.user_type == 'TEAM_LEAD' else 'MEMBER'
        TeamMember.objects.create(team=team, user=request.user, role=role)
        return team