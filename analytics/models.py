from django.db import models
from teams.models import Team
from accounts.models import CustomUser

class TeamAnalytics(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='analytics')
    fairness_score = models.FloatField(default=0.0)  # 0-100
    contribution_distribution = models.JSONField(default=dict)  # e.g., {"user_id": hours}
    highest_contributor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='+')
    lowest_contributor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='+')
    imbalance_warning = models.BooleanField(default=False)
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-calculated_at']