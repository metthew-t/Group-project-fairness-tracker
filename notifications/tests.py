from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from teams.models import Team, TeamMember
from projects.models import Project
from tasks.models import Task
from contributions.models import Contribution, Verification
from notifications.models import Notification

User = get_user_model()

class NotificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Users
        self.lead = User.objects.create_user(username='lead', email='lead@ex.com', password='pass')
        self.member = User.objects.create_user(username='member', email='member@ex.com', password='pass')
        self.other = User.objects.create_user(username='other', email='other@ex.com', password='pass')

        # Team
        self.team = Team.objects.create(name='Notif Team', created_by=self.lead)
        TeamMember.objects.create(team=self.team, user=self.lead, role='LEAD')  # <-- uppercase
        TeamMember.objects.create(team=self.team, user=self.member, role='MEMBER')  # <-- uppercase

        # Project & Task
        self.project = Project.objects.create(title='Project', team=self.team, created_by=self.lead)
        self.task = Task.objects.create(title='Task', project=self.project, created_by=self.lead)
        self.task.assigned_to.add(self.member)

        # Contribution by member
        self.contribution = Contribution.objects.create(
            task=self.task,
            user=self.member,
            work_type='coding',
            hours_spent=2,
            difficulty=3,
            description='Test'
        )

        # Default auth as lead
        self.client.force_authenticate(user=self.lead)

    # ------------------- List Tests -------------------
    def test_list_notifications_returns_only_own(self):
        """User should only see their own notifications."""
        Notification.objects.create(recipient=self.lead, message='Hello lead')
        Notification.objects.create(recipient=self.member, message='Hello member')

        response = self.client.get('/api/notifications/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['message'], 'Hello lead')

        self.client.force_authenticate(user=self.member)
        response = self.client.get('/api/notifications/notifications/')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['message'], 'Hello member')

    # ------------------- Mark Read -------------------
    def test_mark_read(self):
        """Mark a single notification as read."""
        notif = Notification.objects.create(recipient=self.lead, message='Test')
        self.assertFalse(notif.is_read)

        response = self.client.put(f'/api/notifications/notifications/{notif.id}/mark_read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

    def test_mark_read_other_user_fails(self):
        """Cannot mark another user's notification as read."""
        notif = Notification.objects.create(recipient=self.member, message='Secret')
        response = self.client.put(f'/api/notifications/notifications/{notif.id}/mark_read/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # filtered out

    # ------------------- Mark All Read -------------------
    def test_mark_all_read(self):
        """Mark all own notifications as read."""
        Notification.objects.create(recipient=self.lead, message='A')
        Notification.objects.create(recipient=self.lead, message='B')
        Notification.objects.create(recipient=self.member, message='C')

        response = self.client.put('/api/notifications/notifications/mark-all-read/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Notification.objects.filter(recipient=self.lead, is_read=True).count(), 2)
        self.assertEqual(Notification.objects.filter(recipient=self.member, is_read=True).count(), 0)

    # ------------------- Signal Tests -------------------
    def test_signal_creates_notification_on_verification(self):
        """When a verification is created, a notification should be sent to the contributor."""
        # Lead verifies member's contribution
        verification = Verification.objects.create(
            contribution=self.contribution,
            verifier=self.lead,
            decision='approved',
            comments='Good'
        )
        # Check notification for member
        notif = Notification.objects.filter(recipient=self.member).first()
        self.assertIsNotNone(notif)
        self.assertIn('approved', notif.message)
        self.assertIn(self.task.title, notif.message)

    def test_signal_creates_notification_on_rejection(self):
        """Verification rejection also creates notification."""
        verification = Verification.objects.create(
            contribution=self.contribution,
            verifier=self.lead,
            decision='rejected',
            comments='Bad'
        )
        notif = Notification.objects.filter(recipient=self.member).first()
        self.assertIsNotNone(notif)
        self.assertIn('rejected', notif.message)

    def test_signal_creates_notification_for_lead_on_dispute(self):
        """If a verification is disputed, team leads get notified."""
    # Create another member
        member2 = User.objects.create_user(username='member2', email='m2@ex.com', password='pass')
        TeamMember.objects.create(team=self.team, user=member2, role='MEMBER')

    # Contribution by member2
        contrib2 = Contribution.objects.create(
            task=self.task,
            user=member2,
            work_type='coding',
            hours_spent=1,
            difficulty=2,
            description='Another'
    )

    # Member2 disputes the contribution (verifier is member2)
        verification = Verification.objects.create(
            contribution=contrib2,
            verifier=member2,
            decision='disputed',
            comments='Not right'
    )

    # Should notify the lead
        notif = Notification.objects.filter(recipient=self.lead).first()
        self.assertIsNotNone(notif)
        self.assertIn('disputed', notif.message)
        self.assertIn(member2.email, notif.message)  # verifier's email appears in the message

    # ------------------- Unauthenticated Access -------------------
    def test_unauthenticated_access_denied(self):
        """All endpoints require authentication."""
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/notifications/notifications/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.put('/api/notifications/notifications/1/mark_read/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.put('/api/notifications/notifications/mark-all-read/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)