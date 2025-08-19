import requests
import json

# 测试需求详情接口

# 首先登录获取token
def login():
    url = 'http://localhost:5000/api/users/login'
    data = {
        'email': 'test@example.com',
        'password': 'password123'
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f'Login failed with status code {response.status_code}')
        print(response.text)
        return None

# 创建需求
def create_requirement(token):
    url = 'http://localhost:5000/api/requirements/create'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    data = {
        'title': '测试需求',
        'description': '这是一个测试需求'
    }
    response = requests.post(url, headers=headers, json=data)
    print(f'Create requirement status code: {response.status_code}')
    if response.status_code == 201:
        req_id = response.json()['requirement']['id']
        print(f'Created requirement with ID: {req_id}')
        return req_id
    else:
        print('Error creating requirement:', response.text)
        return None

# 获取需求列表
def get_requirements(token):
    url = 'http://localhost:5000/api/requirements/list'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['requirements']
    else:
        print(f'Get requirements failed with status code {response.status_code}')
        print(response.text)
        return None

# 获取需求详情
def get_requirement_detail(token, req_id):
    url = f'http://localhost:5000/api/requirements/{req_id}'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    print(f'Get requirement detail status code: {response.status_code}')
    if response.status_code == 200:
        print('Requirement detail:', json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print('Error:', response.text)

# 获取参与者列表
def get_participants(token, req_id):
    url = f'http://localhost:5000/api/requirements/{req_id}/participants'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    print(f'Get participants status code: {response.status_code}')
    if response.status_code == 200:
        print('Participants:', json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print('Error:', response.text)

# 获取已提交内容
def get_contents(token, req_id):
    url = f'http://localhost:5000/api/requirements/{req_id}/contents'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    print(f'Get contents status code: {response.status_code}')
    if response.status_code == 200:
        print('Contents:', json.dumps(response.json(), indent=2, ensure_ascii=False))
    else:
        print('Error:', response.text)

if __name__ == '__main__':
    # 登录
    token = login()
    if not token:
        exit(1)
    
    print('Login successful, token:', token[:20] + '...')
    
    # 创建需求
    req_id = create_requirement(token)
    if not req_id:
        exit(1)
    
    # 获取需求列表
    requirements = get_requirements(token)
    if not requirements:
        print('No requirements found')
        exit(1)
    
    print(f'Found {len(requirements)} requirements')
    
    # 获取第一个需求的详情
    if not req_id:
        req_id = requirements[0]['id']
    print(f'\nGetting detail for requirement {req_id}')
    get_requirement_detail(token, req_id)
    
    # 获取参与者列表
    print(f'\nGetting participants for requirement {req_id}')
    get_participants(token, req_id)
    
    # 获取已提交内容
    print(f'\nGetting contents for requirement {req_id}')
    get_contents(token, req_id)