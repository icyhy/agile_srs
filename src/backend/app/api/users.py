from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..models.user import User
from .. import db
from ..utils.database_adapter import DatabaseAdapter
from datetime import timedelta
import os
import hashlib

users_bp = Blueprint('users', __name__)

@users_bp.route('/register', methods=['POST'])
def register():
    try:
        print("=== 开始用户注册 ===")
        data = request.get_json()
        print(f"接收到的数据: {data}")
        
        # 验证输入
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            print("缺少必需字段")
            return jsonify({'message': 'Missing required fields'}), 400
        
        # 获取数据库适配器
        print("初始化数据库适配器")
        db_adapter = DatabaseAdapter()
        print(f"数据库适配器连接方法: {db_adapter.connection_method}")
        
        # 检查用户是否已存在
        print(f"检查邮箱是否存在: {data['email']}")
        if db_adapter.connection_method == 'rest_api':
            existing_user_email = db_adapter.supabase_rest_adapter.select('users', filters={'email': data['email']})
        else:
            # 使用原始SQL查询
            existing_user_email = db_adapter.execute_raw_query(
                "SELECT * FROM users WHERE email = :email", 
                {'email': data['email']}
            )
        print(f"邮箱查询结果: {existing_user_email}")
        if existing_user_email:
            return jsonify({'message': 'Email already registered'}), 400
        
        print(f"检查用户名是否存在: {data['username']}")
        if db_adapter.connection_method == 'rest_api':
            existing_user_username = db_adapter.supabase_rest_adapter.select('users', filters={'username': data['username']})
        else:
            # 使用原始SQL查询
            existing_user_username = db_adapter.execute_raw_query(
                "SELECT * FROM users WHERE username = :username", 
                {'username': data['username']}
            )
        print(f"用户名查询结果: {existing_user_username}")
        if existing_user_username:
            return jsonify({'message': 'Username already taken'}), 400
        
        # 创建密码哈希
        print("创建密码哈希")
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          data['password'].encode('utf-8'), 
                                          b'salt', 
                                          100000).hex()
        
        # 创建新用户数据
        user_data = {
            'username': data['username'],
            'email': data['email'],
            'password_hash': password_hash,
            'is_active': True
        }
        print(f"准备插入用户数据: {user_data}")
        
        # 插入用户
        print("执行用户插入")
        if db_adapter.connection_method == 'rest_api':
            result = db_adapter.supabase_rest_adapter.insert('users', user_data)
        else:
            # 使用原始SQL插入
            try:
                db_adapter.execute_raw_query(
                    "INSERT INTO users (username, email, password_hash, is_active) VALUES (:username, :email, :password_hash, :is_active)",
                    user_data
                )
                result = user_data  # 返回插入的数据作为成功标志
            except Exception as e:
                print(f"SQL插入失败: {str(e)}")
                result = None
        print(f"插入结果: {result}")
        
        if result:
            print("用户创建成功")
            return jsonify({'message': 'User created successfully'}), 201
        else:
            print("用户创建失败")
            return jsonify({'message': 'Error creating user'}), 500
            
    except Exception as e:
        print(f"注册过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Error creating user', 'error': str(e)}), 500

@users_bp.route('/login', methods=['POST'])
def login():
    try:
        print("=== 开始用户登录 ===")
        data = request.get_json()
        print(f"接收到的登录数据: {data}")
        
        # 验证输入
        if not data or not data.get('email') or not data.get('password'):
            print("缺少邮箱或密码")
            return jsonify({'message': 'Missing email or password'}), 400
        
        # 获取数据库适配器
        print("初始化数据库适配器")
        db_adapter = DatabaseAdapter()
        print(f"数据库适配器连接方法: {db_adapter.connection_method}")
        
        # 查找用户
        print(f"查找用户: {data['email']}")
        if db_adapter.connection_method == 'rest_api':
            users = db_adapter.supabase_rest_adapter.select('users', filters={'email': data['email']})
        else:
            # 使用原始SQL查询
            users = db_adapter.execute_raw_query(
                "SELECT * FROM users WHERE email = :email", 
                {'email': data['email']}
            )
        print(f"用户查询结果: {users}")
        
        if not users:
            print("用户不存在")
            return jsonify({'message': 'Invalid credentials'}), 401
        
        user_row = users[0]
        # 将Row对象转换为字典以便访问
        if hasattr(user_row, '_asdict'):
            user_data = user_row._asdict()
        else:
            # 对于SQLAlchemy Row对象，使用._mapping属性
            user_data = dict(user_row._mapping)
        print(f"找到用户: {user_data.get('username', 'unknown')}")
        
        # 验证密码
        print("验证密码")
        password_hash = hashlib.pbkdf2_hmac('sha256', 
                                          data['password'].encode('utf-8'), 
                                          b'salt', 
                                          100000).hex()
        print(f"计算的密码哈希: {password_hash}")
        print(f"存储的密码哈希: {user_data.get('password_hash', 'none')}")
        
        if user_data.get('password_hash') != password_hash:
            print("密码不匹配")
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # 生成访问令牌
        print("生成访问令牌")
        access_token = create_access_token(
            identity=str(user_data['id']),
            expires_delta=timedelta(days=7)
        )
        
        print("登录成功")
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user_data['id'],
                'username': user_data['username'],
                'email': user_data['email'],
                'created_at': user_data.get('created_at'),
                'is_active': user_data.get('is_active', True)
            }
        }), 200
    except Exception as e:
        print(f"登录过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Error during login', 'error': str(e)}), 500

@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching profile', 'error': str(e)}), 500

@users_bp.route('/email/<email>', methods=['GET'])
@jwt_required()
def get_user_by_email(email):
    try:
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching user by email', 'error': str(e)}), 500

@users_bp.route('/search', methods=['GET'])
@jwt_required()
def search_users():
    try:
        email_prefix = request.args.get('email_prefix', '')
        
        if not email_prefix:
            return jsonify({'users': []}), 200
        
        # 根据邮箱前缀搜索用户
        users = User.query.filter(User.email.like(f'{email_prefix}%')).limit(10).all()
        
        return jsonify({'users': [user.to_dict() for user in users]}), 200
    except Exception as e:
        return jsonify({'message': 'Error searching users', 'error': str(e)}), 500