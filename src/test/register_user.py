import requests
import json

# 注册用户
register_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
}

try:
    response = requests.post('http://localhost:3000/api/users/register', 
                             headers={'Content-Type': 'application/json'},
                             data=json.dumps(register_data))
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")