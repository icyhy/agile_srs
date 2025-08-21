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
    db.create_all()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)