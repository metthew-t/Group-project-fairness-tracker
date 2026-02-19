from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from teams.models import Team, TeamMember
from projects.models import Project

User = get_user_model()

class ProjectTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create users
        self.lead = User.objects.create_user(username='lead', email='lead@example.com', password='pass')
        self.member = User.objects.create_user(username='member', email='member@example.com', password='pass')
        self.non_member = User.objects.create_user(username='outsider', email='outsider@example.com', password='pass')

        # Create team
        self.team = Team.objects.create(name='Alpha Team', created_by=self.lead)

        # Add memberships
        TeamMember.objects.create(team=self.team, user=self.lead, role='LEAD')
        TeamMember.objects.create(team=self.team, user=self.member, role='MEMBER')

        # Create a project under this team
        self.project = Project.objects.create(
            title='Initial Project',
            description='Test project',
            team=self.team,
            created_by=self.lead,
            status='PLANNING'
        )

        # Authenticate as lead by default
        self.client.force_authenticate(user=self.lead)

    # ------------------- List Tests -------------------
    def test_list_projects_returns_only_teams_user_belongs_to(self):
        """Authenticated user should only see projects of teams they are members of."""
        # lead sees their project
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)                     # <-- length check added
        self.assertEqual(response.data[0]['title'], 'Initial Project')

        # member sees the same project
        self.client.force_authenticate(user=self.member)
        response = self.client.get('/api/projects/')
        self.assertEqual(len(response.data), 1)

        # non-member sees none
        self.client.force_authenticate(user=self.non_member)
        response = self.client.get('/api/projects/')
        self.assertEqual(len(response.data), 0)

    # ------------------- Create Tests -------------------
    def test_create_project_as_team_member(self):
        """Team member can create a project under their team."""
        data = {
            'title': 'New Project',
            'description': 'Desc',
            'team': self.team.id,
            'status': 'PLANNING'
        }
        response = self.client.post('/api/projects/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)
        new_project = Project.objects.get(title='New Project')
        self.assertEqual(new_project.created_by, self.lead)
        self.assertEqual(new_project.team, self.team)

    def test_create_project_as_non_member_fails(self):
        """Non‑member cannot create a project under a team they don't belong to."""
        self.client.force_authenticate(user=self.non_member)
        data = {
            'title': 'New Project',
            'team': self.team.id,
        }
        response = self.client.post('/api/projects/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_create_project_without_team_fails(self):
        """Creating a project without providing a team should fail."""
        data = {'title': 'No Team Project'}
        response = self.client.post('/api/projects/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_project_with_invalid_team_fails(self):
        """Creating a project with a team that doesn't exist should fail."""
        data = {'title': 'Bad Team', 'team': 99999}
        response = self.client.post('/api/projects/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------- Retrieve Tests -------------------
    def test_retrieve_project_as_member(self):
        """Team member can retrieve project details."""
        response = self.client.get(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Initial Project')

    def test_retrieve_project_as_non_member_fails(self):
        """Non‑member cannot retrieve a project (gets 404 because filtered out)."""
        self.client.force_authenticate(user=self.non_member)
        response = self.client.get(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ------------------- Update Tests -------------------
    def test_update_project_as_member(self):
        """Any team member can update project info."""
        data = {'description': 'Updated description'}
        response = self.client.patch(f'/api/projects/{self.project.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.description, 'Updated description')

    def test_update_project_as_non_member_fails(self):
        """Non‑member cannot update a project (404)."""
        self.client.force_authenticate(user=self.non_member)
        data = {'description': 'hack'}
        response = self.client.patch(f'/api/projects/{self.project.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ------------------- Delete Tests -------------------
    def test_delete_project_as_member(self):
        """Any team member can delete a project."""
        response = self.client.delete(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_delete_project_as_non_member_fails(self):
        """Non‑member cannot delete a project (404)."""
        self.client.force_authenticate(user=self.non_member)
        response = self.client.delete(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ------------------- Custom Action: set_status -------------------
    def test_set_status_as_member(self):
        """Team member can change project status."""
        data = {'status': 'ACTIVE'}
        response = self.client.patch(f'/api/projects/{self.project.id}/status/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, 'ACTIVE')

    def test_set_status_as_non_member_fails(self):
        """Non‑member cannot change project status."""
        self.client.force_authenticate(user=self.non_member)
        data = {'status': 'ACTIVE'}
        response = self.client.patch(f'/api/projects/{self.project.id}/status/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_set_status_with_invalid_status_fails(self):
        """Providing an invalid status returns 400."""
        data = {'status': 'INVALID'}
        response = self.client.patch(f'/api/projects/{self.project.id}/status/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------- Unauthenticated Access -------------------
    def test_unauthenticated_access_denied(self):
        """All project endpoints require authentication."""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post('/api/projects/', {'title': 'x'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.get(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)