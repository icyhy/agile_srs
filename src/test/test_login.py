import requests
import json

def test_admin_login():
    # 后端服务地址
    base_url = 'http://localhost:5001'
    
    # 登录端点
    login_url = f'{base_url}/api/users/login'
    
    # admin用户凭证
    credentials = {
        'email': 'admin@example.com',
        'password': '123123'
    }
    
    try:
        # 发送登录请求
        response = requests.post(login_url, json=credentials)
        
        if response.status_code == 200:
            print('Admin login successful!')
            print('Response:', response.json())
            return True
        else:
            print(f'Login failed with status code: {response.status_code}')
            print('Response:', response.text)
            return False
    except Exception as e:
        print(f'Error during login test: {str(e)}')
        return False

if __name__ == '__main__':
    test_admin_login()