import requests

url = 'http://127.0.0.1:8000/api/auth/register/'
data = {
    'username': 'instructor_test_3',
    'email': 'instructor3@test.com',
    'password': 'Password123!',
    'password2': 'Password123!',
    'first_name': 'Test',
    'last_name': 'Instructor',
    'user_type': 'INSTRUCTOR',
    'phone_number': '+1234567890'
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    print(response.text)
except Exception as e:
    print(f"Request failed: {e}")
