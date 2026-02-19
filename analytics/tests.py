from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from teams.models import Team, TeamMember
from projects.models import Project
from tasks.models import Task
from contributions.models import Contribution
from analytics.models import TeamAnalytics

User = get_user_model()

class AnalyticsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Users
        self.lead = User.objects.create_user(username='lead', email='lead@ex.com', password='pass')
        self.member1 = User.objects.create_user(username='member1', email='m1@ex.com', password='pass')
        self.member2 = User.objects.create_user(username='member2', email='m2@ex.com', password='pass')
        self.outsider = User.objects.create_user(username='outsider', email='out@ex.com', password='pass')

        # Team
        self.team = Team.objects.create(name='Analytics Team', created_by=self.lead)
        TeamMember.objects.create(team=self.team, user=self.lead, role='lead')
        TeamMember.objects.create(team=self.team, user=self.member1, role='member')
        TeamMember.objects.create(team=self.team, user=self.member2, role='member')

        # Project
        self.project = Project.objects.create(title='Project X', team=self.team, created_by=self.lead)

        # Tasks
        self.task1 = Task.objects.create(title='Task A', project=self.project, created_by=self.lead)
        self.task2 = Task.objects.create(title='Task B', project=self.project, created_by=self.lead)

        # Contributions (weighted by difficulty)
        Contribution.objects.create(
            task=self.task1, user=self.member1, work_type='coding',
            hours_spent=5, difficulty=3, description='', status='approved'
        )
        Contribution.objects.create(
            task=self.task1, user=self.member2, work_type='coding',
            hours_spent=2, difficulty=1, description='', status='approved'
        )
        Contribution.objects.create(
            task=self.task2, user=self.member1, work_type='coding',
            hours_spent=3, difficulty=2, description='', status='approved'
        )
        # member1 total weighted: 5*3/3? Actually weight = difficulty/3, so 5*(3/3)=5, 3*(2/3)=2 => total 7
        # member2 total weighted: 2*(1/3)=0.666...

        self.client.force_authenticate(user=self.lead)

    def test_team_analytics_success(self):
        """Team lead can retrieve team analytics."""
        response = self.client.get(f'/api/analytics/teams/{self.team.id}/analytics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIn('fairness_score', data)
        self.assertIn('contribution_distribution', data)
        self.assertIn('highest_contributor', data)
        self.assertIn('lowest_contributor', data)
        self.assertIn('imbalance_warning', data)

    def test_team_analytics_as_member(self):
        """Team member can retrieve team analytics."""
        self.client.force_authenticate(user=self.member1)
        response = self.client.get(f'/api/analytics/teams/{self.team.id}/analytics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_team_analytics_as_non_member_fails(self):
        """Non‑member cannot retrieve team analytics."""
        self.client.force_authenticate(user=self.outsider)
        response = self.client.get(f'/api/analytics/teams/{self.team.id}/analytics/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_project_analytics_success(self):
        """Team lead can retrieve project analytics."""
        response = self.client.get(f'/api/analytics/projects/{self.project.id}/analytics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_project_analytics_as_non_member_fails(self):
        """Non‑member cannot retrieve project analytics."""
        self.client.force_authenticate(user=self.outsider)
        response = self.client.get(f'/api/analytics/projects/{self.project.id}/analytics/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_analytics_caching(self):
        """Subsequent requests return cached analytics without recalculation."""
        # First request creates analytics record
        response1 = self.client.get(f'/api/analytics/teams/{self.team.id}/analytics/')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        first_id = response1.data['id']

        # Second request should return same record
        response2 = self.client.get(f'/api/analytics/teams/{self.team.id}/analytics/')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['id'], first_id)

    def test_analytics_update_after_new_contribution(self):
        """After a new contribution, analytics should be recalculated (next day or forced)."""
        # Get initial analytics
        initial = self.client.get(f'/api/analytics/teams/{self.team.id}/analytics/').data
        # Add a new contribution
        Contribution.objects.create(
            task=self.task2, user=self.member2, work_type='coding',
            hours_spent=10, difficulty=5, description='', status='approved'
        )
        # Because caching is per day, we need to force a new day or delete the old record.
        # For testing, we can delete the old record to force recalculation.
        TeamAnalytics.objects.filter(team=self.team, project=None).delete()
        response = self.client.get(f'/api/analytics/teams/{self.team.id}/analytics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['id'], initial['id'])
        # Check that fairness_score changed (should be more imbalanced now)
        self.assertNotEqual(response.data['fairness_score'], initial['fairness_score'])