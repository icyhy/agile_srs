import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-jwt-secret-key-here'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # LLM配置
    # 硅基流动模型服务地址
    LLM_BASE_URL = os.environ.get('LLM_BASE_URL') or 'https://api.siliconflow.cn/v1'
    # 模型API密钥
    LLM_API_KEY = os.environ.get('LLM_API_KEY') or 'LLM_API_KEY_here'
    # 模型名称
    LLM_MODEL = os.environ.get('LLM_MODEL') or 'deepseek-ai/DeepSeek-R1'

    # Redis配置（用于缓存）
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///app.db'
    # 开发环境下，禁用文件系统的临时文件自动删除，便于调试
    TEMPFILE_DELETE_ON_CLOSE = False


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}