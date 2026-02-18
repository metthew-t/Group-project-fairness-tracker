from django.db.models.signals import post_save
from django.dispatch import receiver
from contributions.models import Verification, Contribution
from .models import Notification

@receiver(post_save, sender=Verification)
def create_verification_notification(sender, instance, created, **kwargs):
    if created:
        # Notify the contributor
        message = f"Your contribution on task '{instance.contribution.task.title}' was {instance.decision} by {instance.verifier.email}."
        Notification.objects.create(
            recipient=instance.contribution.user,
            message=message
        )
        # If disputed, also notify team lead
        if instance.decision == 'disputed':
            # Find team lead(s) for the team
            team = instance.contribution.task.project.team
            leads = team.membership_set.filter(role='lead').values_list('user', flat=True)
            for lead_id in leads:
                if lead_id != instance.contribution.user.id:  # avoid duplicate if lead is also contributor
                    Notification.objects.create(
                        recipient_id=lead_id,
                        message=f"A contribution was disputed by {instance.verifier.email}. Please review."
                    )