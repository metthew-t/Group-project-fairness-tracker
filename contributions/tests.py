from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from teams.models import Team
from projects.models import Project
from tasks.models import Task
from contributions.models import Contribution, Verification

User = get_user_model()

class ContributionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.other_user = User.objects.create_user(username='otheruser', password='pass')
        
        # If role field exists, set it
        if hasattr(self.user, 'role'):
            self.user.role = 'Student'
            self.user.save()
        if hasattr(self.other_user, 'role'):
            self.other_user.role = 'Student'
            self.other_user.save()

        # Create team
        self.team = Team.objects.create(name='Test Team', created_by=self.user)

        # Add users to team
        if hasattr(self.team, 'members'):
            self.team.members.add(self.user, self.other_user)
        else:
            from teams.models import TeamMember
            TeamMember.objects.create(team=self.team, user=self.user, role='Member')
            TeamMember.objects.create(team=self.team, user=self.other_user, role='Member')

        # Create project
        self.project = Project.objects.create(
            title='Test Project',
            team=self.team,
            created_by=self.user
        )

        # Create task
        self.task = Task.objects.create(
            title='Test Task',
            project=self.project,
            created_by=self.user
        )

        self.client.force_authenticate(user=self.user)

    def test_create_contribution(self):
        url = f'/api/tasks/{self.task.id}/contributions/'
        data = {
            'work_type': 'coding',
            'hours_spent': '3.5',
            'difficulty': 'medium',
            'description': 'Worked on backend'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contribution.objects.count(), 1)
        contrib = Contribution.objects.first()
        self.assertEqual(contrib.user, self.user)
        self.assertEqual(contrib.status, 'pending')

    def test_list_contributions(self):
        Contribution.objects.create(
            task=self.task, user=self.user, work_type='coding',
            hours_spent=2, difficulty='easy', description='test'
        )
        url = f'/api/tasks/{self.task.id}/contributions/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_own_pending_contribution(self):
        contrib = Contribution.objects.create(
            task=self.task, user=self.user, work_type='coding',
            hours_spent=2, difficulty='easy', description='test'
        )
        url = f'/api/contributions/{contrib.id}/'
        data = {'description': 'updated'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contrib.refresh_from_db()
        self.assertEqual(contrib.description, 'updated')

    def test_cannot_update_others_contribution(self):
        contrib = Contribution.objects.create(
            task=self.task, user=self.other_user, work_type='coding',
            hours_spent=2, difficulty='easy', description='test'
        )
        url = f'/api/contributions/{contrib.id}/'
        response = self.client.patch(url, {'description': 'hack'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_verify_contribution_approve(self):
        """Test that a team member can approve a contribution."""
        contrib = Contribution.objects.create(
            task=self.task, user=self.other_user, work_type='coding',
            hours_spent=2, difficulty='easy', description='test'
        )
        url = f'/api/contributions/{contrib.id}/verify/'
        data = {'approved': True, 'comment': 'Good job'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contrib.refresh_from_db()
        self.assertEqual(contrib.status, 'verified')
        self.assertEqual(Verification.objects.count(), 1)
        verification = Verification.objects.first()
        self.assertTrue(verification.approved)
        self.assertEqual(verification.verifier, self.user)

    def test_verify_contribution_reject(self):
        """Test that a team member can reject a contribution."""
        contrib = Contribution.objects.create(
            task=self.task, user=self.other_user, work_type='coding',
            hours_spent=2, difficulty='easy', description='test'
        )
        url = f'/api/contributions/{contrib.id}/verify/'
        data = {'approved': False, 'comment': 'Not enough detail'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contrib.refresh_from_db()
        self.assertEqual(contrib.status, 'rejected')
        self.assertEqual(Verification.objects.count(), 1)
        verification = Verification.objects.first()
        self.assertFalse(verification.approved)

    def test_cannot_verify_non_pending_contribution(self):
        """Test that verification fails if contribution is not pending."""
        contrib = Contribution.objects.create(
            task=self.task, user=self.other_user, work_type='coding',
            hours_spent=2, difficulty='easy', description='test', status='verified'
        )
        url = f'/api/contributions/{contrib.id}/verify/'
        response = self.client.post(url, {'approved': True})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_team_member_cannot_verify(self):
        """Test that a user not in the team cannot verify."""
        outsider = User.objects.create_user(username='outsider', password='pass')
        self.client.force_authenticate(user=outsider)
        contrib = Contribution.objects.create(
            task=self.task, user=self.other_user, work_type='coding',
            hours_spent=2, difficulty='easy', description='test'
        )
        url = f'/api/contributions/{contrib.id}/verify/'
        response = self.client.post(url, {'approved': True})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_flag_contribution(self):
        """Test that the contributor can flag their own contribution as disputed."""
        contrib = Contribution.objects.create(
            task=self.task, user=self.user, work_type='coding',
            hours_spent=2, difficulty='easy', description='test'
        )
        url = f'/api/contributions/{contrib.id}/flag/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contrib.refresh_from_db()
        self.assertEqual(contrib.status, 'disputed')

    def test_cannot_flag_others_contribution(self):
        """Test that a user cannot flag another user's contribution."""
        contrib = Contribution.objects.create(
            task=self.task, user=self.other_user, work_type='coding',
            hours_spent=2, difficulty='easy', description='test'
        )
        url = f'/api/contributions/{contrib.id}/flag/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_flag_non_pending_contribution(self):
        """Test that flagging fails if contribution is not pending."""
        contrib = Contribution.objects.create(
            task=self.task, user=self.user, work_type='coding',
            hours_spent=2, difficulty='easy', description='test', status='verified'
        )
        url = f'/api/contributions/{contrib.id}/flag/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)