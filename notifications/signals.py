from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from contributions.models import Verification, Contribution
from tasks.models import Task
from .models import Notification

@receiver(post_save, sender=Contribution)
def create_contribution_notification(sender, instance, created, **kwargs):
    if created:
        # Notify team leads
        team = instance.task.project.team
        leads = team.memberships.filter(role='LEAD').values_list('user', flat=True)
        for lead_id in leads:
            if lead_id != instance.user.id:  # lead might be the contributor themselves
                Notification.objects.create(
                    recipient_id=lead_id,
                    message=f"Team member {instance.user.username} logged work on task: {instance.task.title}"
                )

@receiver(post_save, sender=Verification)
def create_verification_notification(sender, instance, created, **kwargs):
    if created:
        message = f"Your contribution on task '{instance.contribution.task.title}' was {instance.decision} by {instance.verifier.email}."
        Notification.objects.create(recipient=instance.contribution.user, message=message)
        if instance.decision == 'disputed':
            team = instance.contribution.task.project.team
            leads = team.memberships.filter(role='LEAD').values_list('user', flat=True)
            for lead_id in leads:
                if lead_id != instance.contribution.user.id:
                    Notification.objects.create(recipient_id=lead_id, message=f"A contribution was disputed by {instance.verifier.email}. Please review.")

@receiver(m2m_changed, sender=Task.assigned_to.through)
def task_assignment_notification(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for user_id in pk_set:
            Notification.objects.create(
                recipient_id=user_id,
                message=f"You have been assigned to a new task: {instance.title}"
            )