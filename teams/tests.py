from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Team, TeamMember

User = get_user_model()

class TeamTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='alice', email='alice@example.com', password='pass123')
        self.user2 = User.objects.create_user(username='bob', email='bob@example.com', password='pass123')
        self.user3 = User.objects.create_user(username='charlie', email='charlie@example.com', password='pass123')
    
        self.team = Team.objects.create(name='Alpha', created_by=self.user1)
        TeamMember.objects.create(team=self.team, user=self.user1, role='LEAD')

        TeamMember.objects.create(team=self.team, user=self.user2, role='MEMBER')

        self.client.force_authenticate(user=self.user1)

    def test_list_teams_returns_only_users_teams(self):
        """Authenticated user should only see teams they are a member of."""
    # user1 sees Alpha
        response = self.client.get('/api/teams/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)          # <-- added
        self.assertEqual(response.data[0]['name'], 'Alpha')

    # user2 sees Alpha too
        self.client.force_authenticate(user=self.user2)
        response = self.client.get('/api/teams/')
        self.assertEqual(len(response.data), 1)

    # user3 sees none
        self.client.force_authenticate(user=self.user3)
        response = self.client.get('/api/teams/')
        self.assertEqual(len(response.data), 0)

    def test_create_team_sets_creator_as_lead(self):
        """Creating a team should make the creator a LEAD member."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/api/teams/', {'name': 'Beta', 'description': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        team_id = response.data['id']
        team = Team.objects.get(id=team_id)
        self.assertEqual(team.created_by, self.user1)
        # Check membership
        membership = TeamMember.objects.get(team=team, user=self.user1)
        self.assertEqual(membership.role, 'LEAD')

    def test_retrieve_team_details(self):
        """Team details should be accessible to members."""
        response = self.client.get(f'/api/teams/{self.team.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Alpha')
        self.assertEqual(len(response.data['members']), 2)

    def test_update_team(self):
        """Any team member can update team info (current behavior)."""
        response = self.client.patch(f'/api/teams/{self.team.id}/', {'description': 'New desc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.team.refresh_from_db()
        self.assertEqual(self.team.description, 'New desc')

        # Non‑member cannot update (should get 404 because queryset filters)
        self.client.force_authenticate(user=self.user3)
        response = self.client.patch(f'/api/teams/{self.team.id}/', {'description': 'Hack'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_team(self):
        """Any team member can delete team (current behavior)."""
        response = self.client.delete(f'/api/teams/{self.team.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Team.objects.filter(id=self.team.id).exists())

    def test_list_members(self):
        """Members list should include all team members."""
        response = self.client.get(f'/api/teams/{self.team.id}/members/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        usernames = [m['user_details']['username'] for m in response.data]
        self.assertIn('alice', usernames)
        self.assertIn('bob', usernames)

    def test_add_member_as_lead(self):
        """Team lead can add a new member."""
        response = self.client.post(f'/api/teams/{self.team.id}/members/', {
            'user_id': self.user3.id,
            'role': 'MEMBER'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(TeamMember.objects.filter(team=self.team, user=self.user3).exists())

    def test_add_member_as_non_lead_fails(self):
        """Regular member cannot add a member."""
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'/api/teams/{self.team.id}/members/', {
            'user_id': self.user3.id
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_existing_member_fails(self):
        """Adding a user already in the team should fail."""
        response = self.client.post(f'/api/teams/{self.team.id}/members/', {
            'user_id': self.user2.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_nonexistent_user_fails(self):
        """Adding a user that doesn't exist should fail."""
        response = self.client.post(f'/api/teams/{self.team.id}/members/', {
            'user_id': 99999
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_remove_member_as_lead(self):
        """Team lead can remove a member."""
        response = self.client.delete(f'/api/teams/{self.team.id}/members/{self.user2.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TeamMember.objects.filter(team=self.team, user=self.user2).exists())

    def test_remove_member_as_non_lead_fails(self):
        """Regular member cannot remove another member."""
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f'/api/teams/{self.team.id}/members/{self.user1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_remove_self_as_lead(self):
        """Lead removing themselves? Not implemented, but current code allows? The permission only checks if request.user is lead, which is true, so lead can remove themselves. That might be undesirable, but we'll test current behavior."""
        response = self.client.delete(f'/api/teams/{self.team.id}/members/{self.user1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TeamMember.objects.filter(team=self.team, user=self.user1).exists())

    def test_join_team_by_code_success(self):
        """User can join a team using a valid join code."""
        # Create a team with a known code
        team2 = Team.objects.create(name='Gamma', created_by=self.user2)
        # Manually set code for predictability
        team2.join_code = '123456'
        team2.save()
        # Add user2 as lead (serializer would have done it, but we didn't use serializer)
        TeamMember.objects.create(team=team2, user=self.user2, role='LEAD')

        self.client.force_authenticate(user=self.user3)
        response = self.client.post(f'/api/teams/join/123456/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(TeamMember.objects.filter(team=team2, user=self.user3).exists())

    def test_join_team_with_invalid_code(self):
        """Joining with a non‑existent code returns 404."""
        self.client.force_authenticate(user=self.user3)
        response = self.client.post('/api/teams/join/000000/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_join_team_already_member(self):
        """Joining a team the user is already in should fail."""
        self.client.force_authenticate(user=self.user2)  # user2 is already in Alpha
        response = self.client.post(f'/api/teams/join/{self.team.join_code}/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_access_denied(self):
        """All team endpoints require authentication."""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/teams/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post('/api/teams/', {'name': 'X'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.get(f'/api/teams/{self.team.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)