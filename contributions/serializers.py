from rest_framework import serializers
from .models import Contribution, Verification
from accounts.serializers import UserSerializer
from tasks.serializers import TaskSerializer   # assuming Task model is in tasks app

class ContributionSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    task_details = TaskSerializer(source='task', read_only=True)

    class Meta:
        model = Contribution
        fields = '__all__'
        read_only_fields = ('user', 'status', 'created_at', 'updated_at')

class VerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verification
        fields = '__all__'
        read_only_fields = ('verifier', 'contribution', 'created_at')