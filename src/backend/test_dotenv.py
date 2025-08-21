import os
from dotenv import load_dotenv

# 打印当前工作目录
dir_path = os.getcwd()
print(f"Current working directory: {dir_path}")

# 检查.env文件是否存在
env_file_path = os.path.join(dir_path, '.env')
print(f".env file exists: {os.path.exists(env_file_path)}")

# 打印.env文件内容（如果存在）
if os.path.exists(env_file_path):
    with open(env_file_path, 'r') as f:
        print(".env file content:")
        print(f.read())

# 加载.env文件
print("Loading .env file...")
load_dotenv()

# 打印LLM_API_KEY和其他关键环境变量的值
print(f"LLM_API_KEY from os.environ: {os.environ.get('LLM_API_KEY')}")
print(f"SECRET_KEY from os.environ: {os.environ.get('SECRET_KEY')}")
print(f"FLASK_CONFIG from os.environ: {os.environ.get('FLASK_CONFIG')}")
print(f"DATABASE_URL from os.environ: {os.environ.get('DATABASE_URL')}")