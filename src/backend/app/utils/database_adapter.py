import os
import logging
from flask import current_app
from supabase import create_client, Client
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from .supabase_adapter import SupabaseRESTAdapter

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseAdapter:
    """
    数据库适配器类，用于处理不同类型数据库的连接和操作
    支持SQLite和Supabase数据库
    """
    
    def __init__(self, config=None):
        self.config = config or current_app.config
        self.database_type = self.config.get('DATABASE_TYPE', 'sqlite').lower()
        self.supabase_client = None
        self.supabase_rest_adapter = None
        self.engine = None
        self.connection_method = None  # 'postgresql', 'rest_api', 'sqlite'
        
        logger.info(f"初始化数据库适配器，数据库类型: {self.database_type}")
        
        # 自动初始化连接
        self.initialize_connection()
        
    def initialize_connection(self):
        """
        初始化数据库连接
        """
        if self.database_type == 'supabase':
            # Supabase初始化包含内部回退逻辑，不需要外部异常处理
            self._initialize_supabase()
        else:
            try:
                self._initialize_sqlite()
            except Exception as e:
                logger.error(f"SQLite连接初始化失败: {str(e)}")
                return False
        return True
    
    def _initialize_supabase(self):
        """
        初始化Supabase连接，尝试多种连接方式
        """
        supabase_url = self.config.get('SUPABASE_URL')
        supabase_key = self.config.get('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL和SUPABASE_KEY必须设置")
        
        # 首先尝试PostgreSQL直连（尝试所有连接选项）
        connection_options = self.config.get('SUPABASE_CONNECTION_OPTIONS', [])
        if not connection_options:
            # 如果没有连接选项，使用默认的SQLALCHEMY_DATABASE_URI
            database_uri = self.config.get('SQLALCHEMY_DATABASE_URI')
            if database_uri and 'postgresql' in database_uri:
                connection_options = [database_uri]
        
        # 尝试每个PostgreSQL连接选项
        for uri in connection_options:
            try:
                logger.info(f"尝试PostgreSQL连接: {uri.split('@')[1].split(':')[0] if '@' in uri else 'unknown'}")
                self.engine = create_engine(uri, connect_args={'connect_timeout': 5})
                # 测试连接
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                self.connection_method = 'postgresql'
                logger.info("Supabase PostgreSQL直连初始化成功")
                return
            except Exception as e:
                logger.warning(f"PostgreSQL连接失败: {str(e)[:50]}...")
                continue
        
        logger.warning("所有PostgreSQL连接选项都失败，尝试REST API")
        
        # 尝试REST API连接
        try:
            self.supabase_rest_adapter = SupabaseRESTAdapter(supabase_url, supabase_key)
            test_result = self.supabase_rest_adapter.test_connection()
            if test_result['success']:
                self.connection_method = 'rest_api'
                logger.info("Supabase REST API连接初始化成功")
                return
            else:
                logger.warning(f"REST API连接失败: {test_result['message']}")
        except Exception as e:
            logger.warning(f"REST API连接失败: {str(e)}")
        
        # 如果都失败，回退到SQLite
        logger.warning("所有Supabase连接方式都失败，回退到SQLite")
        self.database_type = 'sqlite'
        self._initialize_sqlite()
    
    def _initialize_sqlite(self):
        """
        初始化SQLite连接
        """
        database_uri = self.config.get('SQLALCHEMY_DATABASE_URI')
        if database_uri:
            self.engine = create_engine(database_uri)
        
        self.connection_method = 'sqlite'
        logger.info("SQLite连接初始化成功")
    
    def test_connection(self):
        """
        测试数据库连接
        """
        try:
            if self.database_type == 'supabase':
                return self._test_supabase_connection()
            else:
                return self._test_sqlite_connection()
        except Exception as e:
            logger.error(f"数据库连接测试失败: {str(e)}")
            return False, str(e)
    
    def _test_supabase_connection(self):
        """
        测试Supabase连接
        """
        try:
            if self.connection_method == 'postgresql' and self.engine:
                with self.engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    result.fetchone()
                logger.info("Supabase PostgreSQL连接测试成功")
                return True, "Supabase PostgreSQL连接正常"
            
            elif self.connection_method == 'rest_api' and self.supabase_rest_adapter:
                test_result = self.supabase_rest_adapter.test_connection()
                if test_result['success']:
                    logger.info("Supabase REST API连接测试成功")
                    return True, "Supabase REST API连接正常"
                else:
                    return False, f"REST API连接失败: {test_result['message']}"
            
            else:
                return False, "没有可用的Supabase连接方式"
                
        except Exception as e:
            logger.error(f"Supabase连接测试失败: {str(e)}")
            return False, f"Supabase连接失败: {str(e)}"
    
    def _test_sqlite_connection(self):
        """
        测试SQLite连接
        """
        if not self.engine:
            return False, "SQLite引擎未初始化"
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            logger.info("SQLite连接测试成功")
            return True, "SQLite连接正常"
        except Exception as e:
            logger.error(f"SQLite连接测试失败: {str(e)}")
            return False, f"SQLite连接失败: {str(e)}"
    
    def get_database_info(self):
        """
        获取数据库信息
        """
        info = {
            'database_type': self.database_type,
            'connection_uri': self.config.get('SQLALCHEMY_DATABASE_URI', 'Not set'),
            'is_connected': False
        }
        
        # 测试连接状态
        is_connected, message = self.test_connection()
        info['is_connected'] = is_connected
        info['connection_message'] = message
        
        if self.database_type == 'supabase':
            info['supabase_url'] = self.config.get('SUPABASE_URL', 'Not set')
            info['supabase_key_set'] = bool(self.config.get('SUPABASE_KEY'))
        
        return info
    
    def execute_raw_query(self, query, params=None):
        """
        执行原始SQL查询
        """
        if not self.engine:
            raise RuntimeError("数据库引擎未初始化")
        
        try:
            with self.engine.connect() as conn:
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))
                
                # 检查查询类型，只对SELECT查询返回结果
                query_upper = query.strip().upper()
                if query_upper.startswith('SELECT'):
                    return result.fetchall()
                else:
                    # 对于INSERT、UPDATE、DELETE等操作，提交事务并返回受影响的行数
                    conn.commit()
                    return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"SQL查询执行失败: {str(e)}")
            raise
    
    def close_connection(self):
        """
        关闭数据库连接
        """
        if self.engine:
            self.engine.dispose()
            logger.info("数据库连接已关闭")

# 全局数据库适配器实例
db_adapter = None

def get_database_adapter(config=None):
    """
    获取数据库适配器实例（单例模式）
    """
    global db_adapter
    if db_adapter is None:
        db_adapter = DatabaseAdapter(config)
        db_adapter.initialize_connection()
    return db_adapter

def init_database_adapter(app):
    """
    在Flask应用中初始化数据库适配器
    """
    global db_adapter
    with app.app_context():
        db_adapter = DatabaseAdapter(app.config)
        db_adapter.initialize_connection()
        logger.info("数据库适配器已在Flask应用中初始化")
    return db_adapter