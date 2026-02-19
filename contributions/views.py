from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Contribution, Verification
from .serializers import ContributionSerializer, VerificationSerializer
from teams.models import TeamMember
from tasks.models import Task

class ContributionViewSet(viewsets.ModelViewSet):
    queryset = Contribution.objects.all()
    serializer_class = ContributionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only show contributions from tasks that belong to teams the user is in
        user = self.request.user
        return Contribution.objects.filter(
            task__project__team__memberships__user=user
        ).distinct()

    def perform_create(self, serializer):
        # Ensure the user is a member of the team that owns the task
        task_id = self.request.data.get('task')
        task = get_object_or_404(Task, id=task_id)
        if not TeamMember.objects.filter(team=task.project.team, user=self.request.user).exists():
            raise PermissionDenied("You are not a member of this team.")
        serializer.save(user=self.request.user, status='pending')

    def perform_update(self, serializer):
        # Only allow update if contribution is pending and user is owner
        contribution = self.get_object()
        if contribution.user != self.request.user:
            raise PermissionDenied("You can only update your own contributions.")
        if contribution.status != 'pending':
            raise PermissionDenied("Only pending contributions can be updated.")
        serializer.save()

    def perform_destroy(self, instance):
        # Only allow delete if contribution is pending and user is owner
        if instance.user != self.request.user:
            raise PermissionDenied("You can only delete your own contributions.")
        if instance.status != 'pending':
            raise PermissionDenied("Only pending contributions can be deleted.")
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def verify(self, request, pk=None):
        contribution = self.get_object()
        # Prevent self-verification
        if request.user == contribution.user:
            return Response({"error": "You cannot verify your own contribution."}, status=403)
        # Check verifier is in the same team
        if not TeamMember.objects.filter(team=contribution.task.project.team, user=request.user).exists():
            return Response({"error": "You are not a member of this team."}, status=403)
        # Check if already verified by this user
        if Verification.objects.filter(contribution=contribution, verifier=request.user).exists():
            return Response({"error": "You have already verified this contribution."}, status=400)

        serializer = VerificationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(contribution=contribution, verifier=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def lead_action(self, request, pk=None):
        contribution = self.get_object()
        # Check if user is team lead
        if not TeamMember.objects.filter(team=contribution.task.project.team, user=request.user, role='lead').exists():
            return Response({"error": "Only team lead can perform this action."}, status=403)
        decision = request.data.get('decision')
        if decision not in ['approved', 'rejected']:
            return Response({"error": "Decision must be 'approved' or 'rejected'."}, status=400)
        contribution.status = decision
        contribution.save()
        # Record the lead's decision as a verification
        Verification.objects.create(
            contribution=contribution,
            verifier=request.user,
            decision=decision,
            comments=request.data.get('comments', '')
        )
        return Response({"status": f"Contribution {decision}"})