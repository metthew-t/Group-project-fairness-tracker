from rest_framework import serializers
from .models import Task
from accounts.serializers import UserSerializer

class TaskSerializer(serializers.ModelSerializer):
    assigned_to_details = UserSerializer(source='assigned_to', many=True, read_only=True)
    project_title = serializers.ReadOnlyField(source='project.title')
    created_by_username = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'project', 'project_title',
                  'assigned_to', 'assigned_to_details', 'estimated_effort',
                  'priority', 'deadline', 'status', 'weight', 'created_by',
                  'created_by_username', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)