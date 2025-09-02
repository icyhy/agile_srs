from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import config
from .utils.database_adapter import init_database_adapter

# 初始化扩展
db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # 实例化配置类
    config_class = config[config_name]
    config_instance = config_class()
    
    # 将配置实例的属性复制到Flask配置中
    for key, value in config_instance.__dict__.items():
        app.config[key] = value
    
    # 如果使用Supabase，设置一个虚拟的SQLAlchemy URI以避免连接错误
    if app.config.get('DATABASE_TYPE', '').lower() == 'supabase':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    else:
        # SQLite模式下确保使用正确的数据库URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # 导入模型以确保SQLAlchemy知道要创建哪些表
    from .models.user import User
    from .models.requirement import Requirement, UserRequirement, RequirementContent
    
    # 初始化数据库适配器
    init_database_adapter(app)
    
    # 注册蓝图
    from .api.users import users_bp
    from .api.requirements import requirements_bp
    from .utils.llm_integration import test_blueprint
    
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(requirements_bp, url_prefix='/api/requirements')
    app.register_blueprint(test_blueprint)
    
    return app