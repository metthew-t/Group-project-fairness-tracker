from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from teams.models import Team, TeamMember
from projects.models import Project
from tasks.models import Task

User = get_user_model()

class TaskTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create users
        self.lead = User.objects.create_user(username='lead', email='lead@example.com', password='pass')
        self.member = User.objects.create_user(username='member', email='member@example.com', password='pass')
        self.other = User.objects.create_user(username='other', email='other@example.com', password='pass')

        # Create team
        self.team = Team.objects.create(name='Dev Team', created_by=self.lead)
        TeamMember.objects.create(team=self.team, user=self.lead, role='LEAD')
        TeamMember.objects.create(team=self.team, user=self.member, role='MEMBER')

        # Create project
        self.project = Project.objects.create(
            title='Sprint 1',
            team=self.team,
            created_by=self.lead
        )

        # Create a task
        self.task = Task.objects.create(
            title='Write tests',
            project=self.project,
            created_by=self.lead,
            estimated_effort=3,
            priority='HIGH'
        )
        self.task.assigned_to.add(self.member)

        # Default auth as lead
        self.client.force_authenticate(user=self.lead)

    # ------------------- List Tests -------------------
    def test_list_tasks_returns_only_user_team_tasks(self):
        """User should only see tasks from projects of teams they belong to."""
        # lead sees the task
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Write tests')

        # member sees it too
        self.client.force_authenticate(user=self.member)
        response = self.client.get('/api/tasks/')
        self.assertEqual(len(response.data), 1)

        # other sees none
        self.client.force_authenticate(user=self.other)
        response = self.client.get('/api/tasks/')
        self.assertEqual(len(response.data), 0)

    # ------------------- Create Tests -------------------
    def test_create_task_as_team_member(self):
        """Team member can create a task in a project they have access to."""
        data = {
            'title': 'New Task',
            'project': self.project.id,
            'estimated_effort': 5,
            'priority': 'MEDIUM'
        }
        response = self.client.post('/api/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
        new_task = Task.objects.get(title='New Task')
        self.assertEqual(new_task.created_by, self.lead)
        self.assertEqual(new_task.project, self.project)

    def test_create_task_as_non_member_fails(self):
        """Non‑member cannot create a task under a project they don't have access to."""
        self.client.force_authenticate(user=self.other)
        data = {'title': 'Hack Task', 'project': self.project.id}
        response = self.client.post('/api/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Task.objects.count(), 1)

    def test_create_task_without_project_fails(self):
        """Creating a task without a project should fail."""
        data = {'title': 'No Project Task'}
        response = self.client.post('/api/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_task_with_invalid_project_fails(self):
        """Creating a task with a non‑existent project should fail."""
        data = {'title': 'Bad Project', 'project': 99999}
        response = self.client.post('/api/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # changed from 404

    # ------------------- Retrieve Tests -------------------
    def test_retrieve_task_as_member(self):
        """Team member can retrieve task details."""
        response = self.client.get(f'/api/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Write tests')

    def test_retrieve_task_as_non_member_fails(self):
        """Non‑member cannot retrieve a task (404 due to queryset filter)."""
        self.client.force_authenticate(user=self.other)
        response = self.client.get(f'/api/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ------------------- Update Tests -------------------
    def test_update_task_as_member(self):
        """Any team member can update task info."""
        data = {'description': 'Updated desc'}
        response = self.client.patch(f'/api/tasks/{self.task.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.description, 'Updated desc')

    def test_update_task_as_non_member_fails(self):
        """Non‑member cannot update a task (404)."""
        self.client.force_authenticate(user=self.other)
        data = {'description': 'hack'}
        response = self.client.patch(f'/api/tasks/{self.task.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ------------------- Delete Tests -------------------
    def test_delete_task_as_member(self):
        """Any team member can delete a task."""
        response = self.client.delete(f'/api/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_delete_task_as_non_member_fails(self):
        """Non‑member cannot delete a task (404)."""
        self.client.force_authenticate(user=self.other)
        response = self.client.delete(f'/api/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ------------------- Assign / Unassign Actions -------------------
    def test_assign_users_to_task(self):
        """Team member can assign other team members to a task."""
        data = {'user_ids': [self.lead.id]}
        response = self.client.post(f'/api/tasks/{self.task.id}/assign/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.lead, self.task.assigned_to.all())

    def test_assign_users_not_in_team_fails(self):
        """Assigning a user who is not in the team should silently ignore them (or not add)."""
        data = {'user_ids': [self.other.id]}
        response = self.client.post(f'/api/tasks/{self.task.id}/assign/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.other, self.task.assigned_to.all())

    def test_assign_users_invalid_list_fails(self):
        """Providing a non‑list user_ids returns 400."""
        data = {'user_ids': self.member.id}  # not a list
        response = self.client.post(f'/api/tasks/{self.task.id}/assign/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_users_as_non_member_fails(self):
        """Non‑member cannot assign users to a task."""
        self.client.force_authenticate(user=self.other)
        data = {'user_ids': [self.member.id]}
        response = self.client.post(f'/api/tasks/{self.task.id}/assign/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unassign_users_from_task(self):
        """Team member can unassign users from a task."""
        data = {'user_ids': [self.member.id]}
        response = self.client.post(f'/api/tasks/{self.task.id}/unassign/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.member, self.task.assigned_to.all())

    def test_unassign_users_as_non_member_fails(self):
        """Non‑member cannot unassign users."""
        self.client.force_authenticate(user=self.other)
        data = {'user_ids': [self.member.id]}
        response = self.client.post(f'/api/tasks/{self.task.id}/unassign/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ------------------- Unauthenticated Access -------------------
    def test_unauthenticated_access_denied(self):
        """All task endpoints require authentication."""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post('/api/tasks/', {'title': 'x'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.get(f'/api/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)