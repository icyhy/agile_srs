import os
import sys
from app import create_app, db
from app.models.user import User

def init_db():
    # 创建Flask应用上下文
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 检查是否已存在admin用户
        admin_user = User.query.filter_by(username='admin').first()
        
        if not admin_user:
            # 创建默认admin用户
            admin_user = User(
                username='admin',
                email='admin@example.com'
            )
            admin_user.set_password('123123')
            
            db.session.add(admin_user)
            db.session.commit()
            print('Database initialized successfully with default admin user (password: 123123)')
        else:
            print('Admin user already exists')

if __name__ == '__main__':
    init_db()