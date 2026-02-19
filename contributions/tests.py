from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from teams.models import Team, TeamMember
from projects.models import Project
from tasks.models import Task
from contributions.models import Contribution, Verification

User = get_user_model()

class ContributionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create users
        self.lead = User.objects.create_user(username='lead', email='lead@example.com', password='pass')
        self.member = User.objects.create_user(username='member', email='member@example.com', password='pass')
        self.other = User.objects.create_user(username='other', email='other@example.com', password='pass')

        # Create team
        self.team = Team.objects.create(name='Alpha Team', created_by=self.lead)
        TeamMember.objects.create(team=self.team, user=self.lead, role='lead')
        TeamMember.objects.create(team=self.team, user=self.member, role='member')

        # Create project
        self.project = Project.objects.create(
            title='Sprint 1',
            team=self.team,
            created_by=self.lead
        )

        # Create task
        self.task = Task.objects.create(
            title='Write code',
            project=self.project,
            created_by=self.lead,
            estimated_effort=5
        )
        self.task.assigned_to.add(self.member)

        # Create a contribution by member
        self.contribution = Contribution.objects.create(
            task=self.task,
            user=self.member,
            work_type='coding',
            hours_spent=4.5,
            difficulty=3,
            description='Implemented feature X',
            status='pending'
        )

        # Default auth as member
        self.client.force_authenticate(user=self.member)

    # ------------------- List Tests -------------------
    def test_list_contributions_returns_only_team_contributions(self):
        """User should only see contributions from tasks in teams they belong to."""
        # member sees their contribution
        response = self.client.get('/api/contributions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.contribution.id)

        # lead also sees it (since in same team)
        self.client.force_authenticate(user=self.lead)
        response = self.client.get('/api/contributions/')
        self.assertEqual(len(response.data), 1)

        # other sees none
        self.client.force_authenticate(user=self.other)
        response = self.client.get('/api/contributions/')
        self.assertEqual(len(response.data), 0)

    # ------------------- Create Tests -------------------
    def test_create_contribution_as_team_member(self):
        """Team member can create a contribution for a task they are assigned to."""
        data = {
            'task': self.task.id,
            'work_type': 'coding',
            'hours_spent': 3.0,
            'difficulty': 2,
            'description': 'Bug fix'
        }
        response = self.client.post('/api/contributions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contribution.objects.count(), 2)
        new_contrib = Contribution.objects.latest('id')
        self.assertEqual(new_contrib.user, self.member)
        self.assertEqual(new_contrib.status, 'pending')

    def test_create_contribution_as_non_member_fails(self):
        """Non‑member cannot create a contribution for a task in a team they don't belong to."""
        self.client.force_authenticate(user=self.other)
        data = {
            'task': self.task.id,
            'work_type': 'coding',
            'hours_spent': 1,
            'difficulty': 1,
            'description': 'hack'
        }
        response = self.client.post('/api/contributions/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Contribution.objects.count(), 1)

    def test_create_contribution_without_task_fails(self):
        """Creating a contribution without a task should fail."""
        data = {'work_type': 'coding', 'hours_spent': 2, 'description': 'No task'}
        response = self.client.post('/api/contributions/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_contribution_with_invalid_task_fails(self):
        """Creating a contribution with a non‑existent task should fail."""
        data = {'task': 99999, 'work_type': 'coding', 'hours_spent': 2, 'description': 'Bad task'}
        response = self.client.post('/api/contributions/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------- Retrieve Tests -------------------
    def test_retrieve_contribution_as_team_member(self):
        """Team member can retrieve contribution details."""
        response = self.client.get(f'/api/contributions/{self.contribution.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.contribution.id)

    def test_retrieve_contribution_as_non_member_fails(self):
        """Non‑member cannot retrieve a contribution (404 due to filtered queryset)."""
        self.client.force_authenticate(user=self.other)
        response = self.client.get(f'/api/contributions/{self.contribution.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ------------------- Update Tests -------------------
    def test_update_own_pending_contribution(self):
        """User can update their own pending contribution."""
        data = {'description': 'Updated description'}
        response = self.client.patch(f'/api/contributions/{self.contribution.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.contribution.refresh_from_db()
        self.assertEqual(self.contribution.description, 'Updated description')

    def test_update_others_contribution_fails(self):
        """User cannot update someone else's contribution."""
        self.client.force_authenticate(user=self.lead)  # lead but not owner
        data = {'description': 'hack'}
        response = self.client.patch(f'/api/contributions/{self.contribution.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_contribution_after_verification_fails(self):
        """Cannot update a contribution that is not pending (e.g., approved)."""
        self.contribution.status = 'approved'
        self.contribution.save()
        data = {'description': 'trying to change'}
        response = self.client.patch(f'/api/contributions/{self.contribution.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ------------------- Delete Tests -------------------
    def test_delete_own_pending_contribution(self):
        """User can delete their own pending contribution."""
        response = self.client.delete(f'/api/contributions/{self.contribution.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Contribution.objects.filter(id=self.contribution.id).exists())

    def test_delete_others_contribution_fails(self):
        """User cannot delete someone else's contribution."""
        self.client.force_authenticate(user=self.lead)
        response = self.client.delete(f'/api/contributions/{self.contribution.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_contribution_after_verification_fails(self):
        """Cannot delete a contribution that is not pending."""
        self.contribution.status = 'approved'
        self.contribution.save()
        response = self.client.delete(f'/api/contributions/{self.contribution.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ------------------- Verification Action Tests -------------------
    def test_verify_contribution_as_team_member(self):
        """Team member can verify (add verification) to a contribution."""
        self.client.force_authenticate(user=self.lead)  # lead is in team
        data = {'decision': 'approved', 'comments': 'Looks good'}
        response = self.client.post(f'/api/contributions/{self.contribution.id}/verify/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Verification.objects.count(), 1)
        verification = Verification.objects.first()
        self.assertEqual(verification.verifier, self.lead)
        self.assertEqual(verification.decision, 'approved')
        # Status of contribution should not change yet (only lead_action changes it)
        self.contribution.refresh_from_db()
        self.assertEqual(self.contribution.status, 'pending')

    def test_verify_own_contribution_fails(self):
        """User cannot verify their own contribution."""
        data = {'decision': 'approved'}
        response = self.client.post(f'/api/contributions/{self.contribution.id}/verify/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_verify_contribution_as_non_member_fails(self):
        """Non‑member cannot verify a contribution."""
        self.client.force_authenticate(user=self.other)
        data = {'decision': 'approved'}
        response = self.client.post(f'/api/contributions/{self.contribution.id}/verify/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_verify_contribution_twice_by_same_user_fails(self):
        """User cannot verify the same contribution twice."""
        Verification.objects.create(
            contribution=self.contribution,
            verifier=self.lead,
            decision='approved'
        )
        self.client.force_authenticate(user=self.lead)
        data = {'decision': 'approved'}
        response = self.client.post(f'/api/contributions/{self.contribution.id}/verify/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------- Lead Action Tests -------------------
    def test_lead_action_approve(self):
        """Team lead can approve a contribution (changes status)."""
        self.client.force_authenticate(user=self.lead)
        data = {'decision': 'approved', 'comments': 'Good work'}
        response = self.client.post(f'/api/contributions/{self.contribution.id}/lead_action/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.contribution.refresh_from_db()
        self.assertEqual(self.contribution.status, 'approved')
        # Verification should be created
        self.assertEqual(Verification.objects.count(), 1)
        verification = Verification.objects.first()
        self.assertEqual(verification.verifier, self.lead)
        self.assertEqual(verification.decision, 'approved')
        self.assertEqual(verification.comments, 'Good work')

    def test_lead_action_reject(self):
        """Team lead can reject a contribution."""
        self.client.force_authenticate(user=self.lead)
        data = {'decision': 'rejected', 'comments': 'Incomplete'}
        response = self.client.post(f'/api/contributions/{self.contribution.id}/lead_action/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.contribution.refresh_from_db()
        self.assertEqual(self.contribution.status, 'rejected')
        self.assertEqual(Verification.objects.count(), 1)
        verification = Verification.objects.first()
        self.assertEqual(verification.decision, 'rejected')

    def test_lead_action_as_non_lead_fails(self):
        """Regular member cannot perform lead action."""
        self.client.force_authenticate(user=self.member)  # member, not lead
        data = {'decision': 'approved'}
        response = self.client.post(f'/api/contributions/{self.contribution.id}/lead_action/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lead_action_invalid_decision_fails(self):
        """Lead action with invalid decision returns 400."""
        self.client.force_authenticate(user=self.lead)
        data = {'decision': 'maybe'}
        response = self.client.post(f'/api/contributions/{self.contribution.id}/lead_action/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------- Unauthenticated Access -------------------
    def test_unauthenticated_access_denied(self):
        """All contribution endpoints require authentication."""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/contributions/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post('/api/contributions/', {'task': 1})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.get(f'/api/contributions/{self.contribution.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)