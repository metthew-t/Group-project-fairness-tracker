import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fairness_tracker.settings')
django.setup()

from accounts.models import CustomUser

# Map old/incorrect roles to new roles
mapping = {
    'MEMBER': 'STUDENT',
    'MANAGER': 'TEAM_LEAD',
    'ADMIN': 'INSTRUCTOR',
}

for user in CustomUser.objects.all():
    if user.user_type in mapping:
        old = user.user_type
        new = mapping[old]
        user.user_type = new
        user.save()
        print(f"Updated {user.username}: {old} -> {new}")
    elif user.user_type not in ['STUDENT', 'TEAM_LEAD', 'INSTRUCTOR']:
        # Default to STUDENT if unknown
        user.user_type = 'STUDENT'
        user.save()
        print(f"Defaulted {user.username} (was {user.user_type}) to STUDENT")

print("Migration complete.")
