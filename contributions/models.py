from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from accounts.models import CustomUser
from tasks.models import Task

class Contribution(models.Model):
    WORK_TYPES = [
        ('Coding', 'Coding'),
        ('Research', 'Research'),
        ('Design', 'Design'),
        ('Documentation', 'Documentation'),
        ('Testing', 'Testing'),
        ('Presentation', 'Presentation'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='contributions')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='contributions')
    work_type = models.CharField(max_length=20, choices=WORK_TYPES)
    hours_spent = models.FloatField(validators=[MinValueValidator(0.1), MaxValueValidator(168)])
    difficulty = models.IntegerField(choices=[(i, i) for i in range(1,6)], default=3)
    description = models.TextField()
    proof_file = models.FileField(
        upload_to='proofs/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png','pdf','doc','docx'])]
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    file_upload = models.FileField(upload_to='contributions/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.task.title} - {self.hours_spent}h"
    
class Verification(models.Model):
    DECISION_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disputed', 'Disputed'),
    ]
    contribution = models.ForeignKey(Contribution, on_delete=models.CASCADE, related_name='verifications')
    verifier = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='verifications')
    decision = models.CharField(max_length=10, choices=DECISION_CHOICES)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('contribution', 'verifier')  # one verification per user per contribution

    def __str__(self):
        return f"{self.verifier.email} – {self.decision}"