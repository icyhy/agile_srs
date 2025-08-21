import os
from dotenv import load_dotenv
from app import create_app
from app.utils.llm_integration import DocumentGenerator

# 加载.env文件
load_dotenv()

# 创建Flask应用上下文
app = create_app('development')

# 打印直接从环境变量获取的值
print(f"直接从环境变量获取的LLM_API_KEY: {os.environ.get('LLM_API_KEY')}")
print(f"直接从环境变量获取的LLM_MODEL: {os.environ.get('LLM_MODEL')}")

# 在应用上下文中测试DocumentGenerator
with app.app_context():
    print("\n在Flask应用上下文中测试DocumentGenerator:")
    # 打印Flask应用配置中的值
    print(f"Flask配置中的LLM_API_KEY: {app.config.get('LLM_API_KEY')}")
    print(f"Flask配置中的LLM_MODEL: {app.config.get('LLM_MODEL')}")
    
    # 创建DocumentGenerator实例
    generator = DocumentGenerator()
    
    # 打印DocumentGenerator实例使用的配置
    print(f"DocumentGenerator使用的API_KEY: {'Set' if generator.api_key and generator.api_key != 'Not found' else 'Not set'}")
    print(f"DocumentGenerator使用的MODEL: {generator.model}")
    print(f"DocumentGenerator的API_KEY是否有效: {generator.api_key_valid}")

# 不在应用上下文中测试DocumentGenerator
print("\n不在Flask应用上下文中测试DocumentGenerator:")
try:
    generator_no_context = DocumentGenerator()
    print(f"DocumentGenerator(无上下文)使用的API_KEY: {'Set' if generator_no_context.api_key and generator_no_context.api_key != 'Not found' else 'Not set'}")
    print(f"DocumentGenerator(无上下文)使用的MODEL: {generator_no_context.model}")
except Exception as e:
    print(f"错误: {str(e)}")