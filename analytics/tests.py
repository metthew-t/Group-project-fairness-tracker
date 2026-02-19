from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from teams.models import Team
from projects.models import Project
from tasks.models import Task
from contributions.models import Contribution
from .models import TeamAnalytics

User = get_user_model()

class AnalyticsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        self.team = Team.objects.create(name='Test Team', created_by=self.user1)
        self.team.members.add(self.user1, self.user2)
        self.project = Project.objects.create(name='Test Project', team=self.team, created_by=self.user1)
        self.task1 = Task.objects.create(title='Task1', project=self.project, created_by=self.user1)
        self.task2 = Task.objects.create(title='Task2', project=self.project, created_by=self.user1)
        self.client.force_authenticate(user=self.user1)

    def test_team_analytics(self):
        # Create contributions
        Contribution.objects.create(
            task=self.task1, user=self.user1, work_type='coding',
            hours_spent=4, difficulty='medium', description=''
        )
        Contribution.objects.create(
            task=self.task2, user=self.user2, work_type='coding',
            hours_spent=2, difficulty='easy', description=''
        )
        url = f'/api/teams/{self.team.id}/analytics/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIn('fairness_score', data)
        self.assertIn('contribution_percentages', data)
        self.assertEqual(data['total_hours'], 4*1.5 + 2*1.0)  # medium=1.5, easy=1.0

    def test_project_analytics(self):
        Contribution.objects.create(
            task=self.task1, user=self.user1, work_type='coding',
            hours_spent=3, difficulty='hard', description=''
        )
        url = f'/api/projects/{self.project.id}/analytics/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)