import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

from app import create_app, db
from app.models.user import User
from app.models.requirement import Requirement, UserRequirement, RequirementContent

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    return dict(
        app=app,
        db=db,
        User=User,
        Requirement=Requirement,
        UserRequirement=UserRequirement,
        RequirementContent=RequirementContent
    )

with app.app_context():
    # 只有在非Supabase模式下才创建表
    if app.config.get('DATABASE_TYPE', '').lower() != 'supabase':
        db.create_all()
    else:
        print("使用Supabase模式，跳过SQLAlchemy表创建")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)