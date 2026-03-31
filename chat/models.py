from django.db import models
from accounts.models import CustomUser
from teams.models import Team

class Message(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"
