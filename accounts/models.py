from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):

    USER_TYPE_CHOICES = [
        ('STUDENT', 'Student'),
        ('TEAM_LEAD', 'Team Lead'),
        ('INSTRUCTOR', 'Instructor'),
    ]
    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES, default='STUDENT')
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    teams = models.ManyToManyField('teams.Team', through='teams.TeamMember', related_name='users')
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_expiry = models.DateTimeField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email