from rest_framework import serializers
from .models import TeamAnalytics

class TeamAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamAnalytics
        fields = '__all__'
        read_only_fields = ['id', 'team', 'project', 'date']