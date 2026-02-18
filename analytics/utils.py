from teams.models import Team
from contributions.models import Contribution
from django.db.models import Sum, FloatField
from django.db.models.functions import Coalesce
import numpy as np

def calculate_team_analytics(team):
    # Get all approved contributions for this team
    contributions = Contribution.objects.filter(
        task__project__team=team,
        status='approved'
    ).select_related('user')

    if not contributions.exists():
        return None

    # Aggregate per user
    user_data = {}
    for c in contributions:
        user_data.setdefault(c.user.id, {
            'user': c.user,
            'total_hours': 0,
            'weighted_hours': 0,
        })
        # Weight hours by difficulty (1-5) -> weight factor 1.0 to 2.0? Let's use difficulty as multiplier
        weighted = c.hours_spent * (c.difficulty / 2.5)  # difficulty 1 => 0.4, 5 => 2.0
        user_data[c.user.id]['total_hours'] += c.hours_spent
        user_data[c.user.id]['weighted_hours'] += weighted

    # Calculate fairness score (based on coefficient of variation)
    hours_list = [d['weighted_hours'] for d in user_data.values()]
    if len(hours_list) <= 1:
        fairness = 100.0
    else:
        mean = np.mean(hours_list)
        std = np.std(hours_list)
        cv = std / mean if mean > 0 else 0
        # Convert CV to score: CV=0 -> 100, CV=0.5 -> 50, etc.
        fairness = max(0, 100 * (1 - min(cv, 1)))

    # Find highest and lowest
    sorted_users = sorted(user_data.values(), key=lambda x: x['weighted_hours'])
    lowest = sorted_users[0]['user'] if sorted_users else None
    highest = sorted_users[-1]['user'] if sorted_users else None

    # Warning if difference > threshold (e.g., highest > 2 * lowest)
    warning = False
    if len(hours_list) > 1 and lowest and highest:
        if highest['weighted_hours'] > 2 * lowest['weighted_hours']:
            warning = True

    # Store distribution as JSON
    distribution = {str(d['user'].id): d['weighted_hours'] for d in user_data.values()}

    # Create or update TeamAnalytics
    from .models import TeamAnalytics
    obj, created = TeamAnalytics.objects.update_or_create(
        team=team,
        defaults={
            'fairness_score': fairness,
            'contribution_distribution': distribution,
            'highest_contributor': highest,
            'lowest_contributor': lowest,
            'imbalance_warning': warning,
        }
    )
    return obj