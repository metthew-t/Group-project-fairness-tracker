from django.core.management.base import BaseCommand
from teams.models import Team
from analytics.utils import calculate_team_analytics

class Command(BaseCommand):
    help = 'Update analytics for all teams'

    def handle(self, *args, **options):
        for team in Team.objects.all():
            calculate_team_analytics(team)
            self.stdout.write(f"Updated analytics for team {team.name}")