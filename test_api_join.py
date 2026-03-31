import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_join():
    # 1. Login to get token for testuser1
    # Note: I need the password. Assuming it's 'password123' or similar for testing?
    # Actually, I'll just use a script that uses DRF's APIClient for a cleaner test.
    pass

# Using django test client is better
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fairness_tracker.settings')
django.setup()

from rest_framework.test import APIClient
from accounts.models import CustomUser
from teams.models import Team

user = CustomUser.objects.get(username='testuser1')
team = Team.objects.get(name='Back End Team')

client = APIClient()
client.force_authenticate(user=user)

print(f"Testing POST /api/teams/join/ with code {team.join_code}")
res = client.post('/api/teams/join/', {'join_code': team.join_code}, format='json')

print(f"Status: {res.status_code}")
print(f"Body: {res.data}")
