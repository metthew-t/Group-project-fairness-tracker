from django.db import models
from accounts.models import CustomUser
from teams.models import Team

class Project(models.Model):
    STATUS_CHOICES = [
        ('PLANNING', 'Planning'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
    ]
    
    PHASE_CHOICES = [
        ('Proposal', 'Proposal'),
        ('Development', 'Development'),
        ('Review', 'Review'),
        ('Finalization', 'Finalization'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='projects')
    administrator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='administered_projects')
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_projects')
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNING')
    phase = models.CharField(max_length=30, choices=PHASE_CHOICES, default='Proposal')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title