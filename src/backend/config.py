import os

class Config:
    def __init__(self):
        self.SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
        
        # 数据库类型配置 (sqlite 或 supabase)
        self.DATABASE_TYPE = os.environ.get('DATABASE_TYPE', 'sqlite').lower()
        
        # SQLite配置
        self.SQLITE_DATABASE_URI = os.environ.get('SQLITE_DATABASE_URI') or \
            'sqlite:///app.db'
        
        # Supabase配置
        self.SUPABASE_URL = os.environ.get('SUPABASE_URL')
        self.SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
        self.SUPABASE_DATABASE_URI = None
        
        # Supabase数据库密码（不同于API Key）
        self.SUPABASE_DB_PASSWORD = os.environ.get('SUPABASE_DB_PASSWORD')
        
        # 根据数据库类型设置连接URI
        if self.DATABASE_TYPE == 'supabase':
            if self.SUPABASE_URL and self.SUPABASE_DB_PASSWORD:
                # 从Supabase URL提取数据库连接信息
                project_ref = self.SUPABASE_URL.replace('https://', '').replace('.supabase.co', '')
                
                # 准备多种连接方式，但不在这里测试连接
                # 连接测试将在database_adapter中进行
                connection_options = [
                    # 1. 使用主机名
                    f"postgresql://postgres:{self.SUPABASE_DB_PASSWORD}@db.{project_ref}.supabase.co:5432/postgres",
                    # 2. 使用IPv6地址
                    f"postgresql://postgres:{self.SUPABASE_DB_PASSWORD}@[2406:da18:243:7408:924d:ab7f:379d:c74]:5432/postgres"
                ]
                
                # 设置第一个连接选项作为默认值，实际连接测试在database_adapter中进行
                self.SUPABASE_DATABASE_URI = connection_options[0]
                self.SQLALCHEMY_DATABASE_URI = connection_options[0]
                self.SUPABASE_CONNECTION_OPTIONS = connection_options
            else:
                raise ValueError("SUPABASE_URL and SUPABASE_DB_PASSWORD must be set when using supabase database")
        
        if self.DATABASE_TYPE == 'sqlite':
            # 使用SQLite
            self.SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or self.SQLITE_DATABASE_URI
    
        
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-jwt-secret-key-here'
        self.UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
        self.MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
        
        # LLM配置
        # 硅基流动模型服务地址
        self.LLM_BASE_URL = os.environ.get('LLM_BASE_URL') or 'https://api.siliconflow.cn/v1'
        # 模型API密钥
        self.LLM_API_KEY = os.environ.get('LLM_API_KEY') or 'LLM_API_KEY_here'
        # 模型名称
        self.LLM_MODEL = os.environ.get('LLM_MODEL') or 'deepseek-ai/DeepSeek-R1'

        # Redis配置（用于缓存）
        self.REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'


class DevelopmentConfig(Config):
    def __init__(self):
        super().__init__()
        self.DEBUG = True
        
        # 开发环境数据库配置 - 重新设置以支持开发环境特定的默认值
        if self.DATABASE_TYPE == 'sqlite' and not os.environ.get('SQLITE_DATABASE_URI'):
            # 开发环境默认数据库路径
            self.SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///app.db'
        
        # 开发环境特定配置
        self.TEMPFILE_DELETE_ON_CLOSE = False


class ProductionConfig(Config):
    def __init__(self):
        super().__init__()
        self.DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}