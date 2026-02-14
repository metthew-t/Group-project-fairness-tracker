from django.db import models
from accounts.models import User
import random
import string

class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_teams')
    created_at = models.DateTimeField(auto_now_add=True)
    
class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    role = models.CharField(max_length=10, choices=[('MEMBER', 'Member'), ('LEAD', 'Lead')], default='MEMBER')
    joined_at = models.DateTimeField(auto_now_add=True)

class Team(models.Model):
    join_code = models.CharField(max_length=6, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.join_code:
            self.join_code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        while True:
            code = ''.join(random.choices(string.digits, k=6))
            if not Team.objects.filter(join_code=code).exists():
                return code