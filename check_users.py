import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fairness_tracker.settings')
django.setup()

from accounts.models import CustomUser

print(f"{'Username':<20} | {'Email':<30} | {'User Type':<15}")
print("-" * 70)
for user in CustomUser.objects.all():
    print(f"{user.username:<20} | {user.email:<30} | {user.user_type:<15}")
