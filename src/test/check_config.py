import os
import sys

sys.path.append('.')

# 直接导入config模块
try:
    import config
    print("直接从config模块导入的配置:")
    print(f"Config.LLM_API_KEY: {config.Config.LLM_API_KEY}")
    print(f"Config.LLM_MODEL: {config.Config.LLM_MODEL}")
    print(f"Config.LLM_BASE_URL: {config.Config.LLM_BASE_URL}")
    
    # 检查当前使用的配置类
    print("\n当前配置环境和配置类:")
    config_name = os.getenv('FLASK_CONFIG', 'default')
    print(f"FLASK_CONFIG环境变量: {config_name}")
    print(f"使用的配置类: {config.config[config_name]}")
    
    # 打印具体配置类的属性
    current_config = config.config[config_name]()
    print(f"当前配置类的LLM_API_KEY: {current_config.LLM_API_KEY}")
    print(f"当前配置类的LLM_MODEL: {current_config.LLM_MODEL}")
    print(f"当前配置类的LLM_BASE_URL: {current_config.LLM_BASE_URL}")

    # 检查是否存在instance/config.py覆盖配置
    try:
        from instance import config as instance_config
        print("\n实例配置(instance/config.py)存在:")
        print(f"instance_config.LLM_API_KEY: {getattr(instance_config, 'LLM_API_KEY', 'Not found')}")
    except ImportError:
        print("\n实例配置(instance/config.py)不存在")

except Exception as e:
    print(f"导入配置时出错: {str(e)}")