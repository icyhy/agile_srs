from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import config

# 初始化扩展
db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # 注册蓝图
    from .api.users import users_bp
    from .api.requirements import requirements_bp
    
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(requirements_bp, url_prefix='/api/requirements')
    
    return app