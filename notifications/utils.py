from django.core.mail import send_mail
from django.conf import settings

def send_progress_email(user, task, progress):
    """
    Simulates sending an email notification to all team members about task progress.
    In development, this will log to the console or a file.
    """
    subject = f"Team Progress Update: {task.title}"
    message = f"Hello Team,\n\n{user.username}'s contribution was just approved! The progress on task '{task.title}' has been updated to {progress}%.\n\nKeep up the great work!\n- Fairness Tracker System"
    from_email = settings.DEFAULT_FROM_EMAIL
    
    # Fetch all user emails belonging to the project's team
    team_users = task.project.team.users.all()
    recipient_list = [u.email for u in team_users if u.email]
    
    try:
        # This will use the backend configured in SETTINGS (file-based or console for dev)
        send_mail(subject, message, from_email, recipient_list)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
