import os
import sys
from app import create_app, db
from app.models.user import User
from app.utils.database_adapter import init_database_adapter

def init_db():
    # 创建Flask应用上下文
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    
    with app.app_context():
        # 初始化数据库适配器
        db_adapter = init_database_adapter(app)
        
        # 获取数据库信息
        db_info = db_adapter.get_database_info()
        print(f"数据库类型: {db_info['database_type']}")
        print(f"连接URI: {db_info['connection_uri']}")
        print(f"连接状态: {'正常' if db_info['is_connected'] else '失败'}")
        
        if not db_info['is_connected']:
            print(f"数据库连接失败: {db_info['connection_message']}")
            print("请检查数据库配置")
            return False
        
        try:
            # 创建所有表
            print("正在创建数据库表...")
            db.create_all()
            print("数据库表创建成功")
            
            # 检查是否已存在admin用户
            admin_user = User.query.filter_by(username='admin').first()
            
            if not admin_user:
                # 创建默认admin用户
                print("正在创建默认admin用户...")
                admin_user = User(
                    username='admin',
                    email='admin@example.com'
                )
                admin_user.set_password('123123')
                
                db.session.add(admin_user)
                db.session.commit()
                print('数据库初始化成功，已创建默认admin用户 (密码: 123123)')
            else:
                print('Admin用户已存在，跳过创建')
            
            return True
            
        except Exception as e:
            print(f"数据库初始化失败: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    init_db()