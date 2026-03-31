from rest_framework import serializers
from .models import Project

class ProjectSerializer(serializers.ModelSerializer):
    team_name = serializers.ReadOnlyField(source='team.name')
    created_by_username = serializers.ReadOnlyField(source='created_by.username')

    administrator_name = serializers.ReadOnlyField(source='administrator.username')

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'team', 'team_name', 'administrator', 'administrator_name', 'phase', 'created_by',
                  'created_by_username', 'deadline', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at']