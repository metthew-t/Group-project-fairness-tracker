import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fairness_tracker.settings')
django.setup()

from teams.models import Team, TeamMember

print(f"{'Team Name':<20} | {'Join Code':<10} | {'Creator':<20}")
print("-" * 60)
for team in Team.objects.all():
    print(f"{team.name:<20} | {team.join_code:<10} | {team.created_by.username:<20}")

print("\nRecent Memberships:")
for tm in TeamMember.objects.all().order_by('-joined_at')[:10]:
    print(f"{tm.user.username:<20} | {tm.team.name:<20} | {tm.role:<10}")
