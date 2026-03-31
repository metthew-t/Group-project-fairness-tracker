from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser
from contributions.models import Contribution
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Sends reminders to users who haven\'t contributed in 2 days'

    def handle(self, *args, **options):
        threshold = timezone.now() - timedelta(days=2)
        users = CustomUser.objects.filter(email_verified=True)
        
        for user in users:
            last_contrib = Contribution.objects.filter(user=user).order_by('-created_at').first()
            
            if not last_contrib or last_contrib.created_at < threshold:
                self.stdout.write(f"Sending reminder to {user.username}")
                send_mail(
                    'Fairness Tracker: Inactivity Reminder',
                    f'Hi {user.username},\n\nWe noticed you haven\'t logged any contributions in the last 2 days. Please keep your progress updated to ensure fair tracking!',
                    'reminders@fairness-tracker.com',
                    [user.email],
                    fail_silently=True,
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully sent reminders'))
