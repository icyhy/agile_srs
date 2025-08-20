import os
import sys
import importlib.util
import traceback

# 添加当前目录到Python路径
sys.path.append('.')

print("======= 详细配置检查 =======")

# 1. 首先检查环境变量
print("\n1. 环境变量检查:")
env_vars = ['LLM_API_KEY', 'LLM_MODEL', 'LLM_BASE_URL', 'FLASK_CONFIG']
for var in env_vars:
    value = os.environ.get(var)
    print(f"  {var}: {value if value else 'Not set'}")

# 2. 检查是否存在instance/config.py文件
print("\n2. 实例配置(instance/config.py)检查:")
instance_config_path = os.path.join('instance', 'config.py')
if os.path.exists(instance_config_path):
    print(f"  发现实例配置文件: {instance_config_path}")
    # 尝试导入并检查实例配置
    try:
        spec = importlib.util.spec_from_file_location("instance_config", instance_config_path)
        instance_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(instance_config)
        
        # 检查LLM相关配置
        for var in env_vars:
            if hasattr(instance_config, var):
                print(f"    {var}: {getattr(instance_config, var)}")
    except Exception as e:
        print(f"  导入实例配置出错: {str(e)}")
else:
    print(f"  实例配置文件不存在: {instance_config_path}")

# 3. 检查默认配置模块
print("\n3. 默认配置模块(config.py)检查:")
try:
    import config
    print(f"  配置模块导入成功")
    print(f"  配置映射中的键: {list(config.config.keys())}")
    
    # 打印基础Config类的配置
    print(f"\n  基础Config类配置:")
    for var in env_vars:
        if hasattr(config.Config, var):
            print(f"    {var}: {getattr(config.Config, var)}")
            
    # 打印DevelopmentConfig类的配置
    if hasattr(config, 'DevelopmentConfig'):
        print(f"\n  DevelopmentConfig类配置:")
        for var in env_vars:
            if hasattr(config.DevelopmentConfig, var):
                print(f"    {var}: {getattr(config.DevelopmentConfig, var)}")
                
    # 打印ProductionConfig类的配置
    if hasattr(config, 'ProductionConfig'):
        print(f"\n  ProductionConfig类配置:")
        for var in env_vars:
            if hasattr(config.ProductionConfig, var):
                print(f"    {var}: {getattr(config.ProductionConfig, var)}")
                
    # 检查是否存在Docker相关配置
    docker_compose_path = os.path.join('..', 'deployment', 'docker-compose.yml')
    if os.path.exists(docker_compose_path):
        print(f"\n4. Docker Compose配置检查:")
        print(f"   发现docker-compose.yml文件: {docker_compose_path}")
        # 这里简单读取文件内容查找LLM_API_KEY
        try:
            with open(docker_compose_path, 'r') as f:
                content = f.read()
                if 'LLM_API_KEY' in content:
                    print("   文件中包含LLM_API_KEY配置")
                if 'your-llm-api-key-here' in content:
                    print("   文件中包含'your-llm-api-key-here'字符串")
        except Exception as e:
            print(f"   读取docker-compose.yml文件出错: {str(e)}")
            
except Exception as e:
    print(f"  导入配置模块出错: {str(e)}")
    print("  错误追踪:")
    traceback.print_exc()

# 5. 模拟Flask应用配置加载过程
print("\n5. Flask应用配置加载模拟:")
try:
    from flask import Flask
    from config import config
    
    # 创建模拟应用
    app = Flask(__name__)
    
    # 确定配置名称
    config_name = os.getenv('FLASK_CONFIG', 'default')
    print(f"  使用配置名称: {config_name}")
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 打印加载后的配置
    print(f"  加载后Flask配置中的值:")
    for var in env_vars:
        value = app.config.get(var, 'Not found')
        print(f"    {var}: {value}")
        
except Exception as e:
    print(f"  模拟Flask配置加载出错: {str(e)}")
    print("  错误追踪:")
    traceback.print_exc()

# 6. 检查文件系统中是否存在其他配置文件
print("\n6. 检查其他可能的配置文件:")
potential_config_files = [
    os.path.join('app', 'config.py'),
    os.path.join('app', 'utils', 'config.py'),
    '.env',
    '.flaskenv',
    'settings.py'
]
for file_path in potential_config_files:
    if os.path.exists(file_path):
        print(f"  发现配置相关文件: {file_path}")
        
# 7. 检查是否存在缓存文件
print("\n7. 检查Python缓存文件:")
potential_cache_files = [
    '__pycache__/config.cpython-*.pyc',
    'app/__pycache__/config.cpython-*.pyc',
    'app/utils/__pycache__/llm_integration.cpython-*.pyc'
]
import glob
for pattern in potential_cache_files:
    matches = glob.glob(pattern)
    if matches:
        print(f"  发现缓存文件: {matches}")

print("\n======= 配置检查完成 =======")