import requests
import json

# 登录获取token
data = {
    "email": "test@example.com",
    "password": "password123"
}

response = requests.post('http://localhost:5000/api/users/login', 
                         headers={'Content-Type': 'application/json'},
                         data=json.dumps(data))

print(f"Login Status Code: {response.status_code}")
print(f"Login Response: {response.text}")

if response.status_code == 200:
    token = response.json()['access_token']
    print(f"Token: {token}")
    
    # 使用token获取需求列表
    response = requests.get('http://localhost:5000/api/requirements/list', 
                            headers={'Authorization': f'Bearer {token}'})
    
    print(f"Requirements Status Code: {response.status_code}")
    print(f"Requirements Response: {response.text}")
else:
    print("Login failed, cannot test requirements API")