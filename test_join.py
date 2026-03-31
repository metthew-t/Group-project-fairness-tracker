import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fairness_tracker.settings')
django.setup()

from accounts.models import CustomUser
from teams.models import Team, TeamMember

# Ensure testuser1 exists
user, _ = CustomUser.objects.get_or_create(username='testuser1', defaults={'email': 'testuser1@example.com', 'user_type': 'STUDENT'})

# Find the team
team = Team.objects.filter(name='Back End Team').first()
if not team:
    print("Team not found")
else:
    print(f"Testing join with code: {team.join_code} for user: {user.username}")
    code = team.join_code
    
    # Check if already a member
    if team.memberships.filter(user=user).exists():
        print("User is already a member")
    else:
        try:
            TeamMember.objects.create(team=team, user=user, role='MEMBER')
            print("Successfully joined via script!")
        except Exception as e:
            print(f"Failed to join: {e}")

# Check current members
print("\nCurrent Members of Back End Team:")
for tm in team.memberships.all():
    print(f"- {tm.user.username} ({tm.role})")
