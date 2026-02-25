from collections import defaultdict
from contributions.models import Contribution
from accounts.models import CustomUser

def calculate_team_analytics(team, project=None):
    """
    Calculate analytics for a team (optionally filtered by project).
    Returns a dict with:
        fairness_score,
        contribution_distribution,
        highest_contributor,
        lowest_contributor,
        imbalance_warning
    """
    contributions = Contribution.objects.filter(task__project__team=team)
    if project:
        contributions = contributions.filter(task__project=project)

    if not contributions.exists():
        return {
            'fairness_score': 100.0,
            'contribution_distribution': {},
            'highest_contributor': None,
            'lowest_contributor': None,
            'imbalance_warning': False,
        }

    # Group by user
    user_hours = defaultdict(float)
    for c in contributions:
        # Weight by difficulty (1-5) – you can adjust formula
        weight = c.difficulty / 3.0  # simple weight
        user_hours[c.user_id] += float(c.hours_spent) * weight

    total = sum(user_hours.values())
    distribution = {str(uid): hours for uid, hours in user_hours.items()}

    # Find highest/lowest contributors
    if user_hours:
        highest_id = max(user_hours, key=user_hours.get)
        lowest_id = min(user_hours, key=user_hours.get)
        highest = CustomUser.objects.get(id=highest_id)
        lowest = CustomUser.objects.get(id=lowest_id)
    else:
        highest = lowest = None

    # Simple fairness score: coefficient of variation
    if len(user_hours) > 1:
        hours_list = list(user_hours.values())
        mean = sum(hours_list) / len(hours_list)
        variance = sum((x - mean) ** 2 for x in hours_list) / len(hours_list)
        std_dev = variance ** 0.5
        cv = std_dev / mean if mean > 0 else 0
        fairness = max(0, 100 * (1 - min(cv, 1)))
    else:
        fairness = 100.0

    # Warning if any user has < 50% of average?
    if len(user_hours) > 1:
        avg = total / len(user_hours)
        min_hours = min(user_hours.values())
        imbalance_warning = min_hours < (0.5 * avg)
    else:
        imbalance_warning = False

    return {
        'fairness_score': round(fairness, 2),
        'contribution_distribution': distribution,
        'highest_contributor': highest,
        'lowest_contributor': lowest,
        'imbalance_warning': imbalance_warning,
    }