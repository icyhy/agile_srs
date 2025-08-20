import openai
import os
import logging
import time
from fpdf import FPDF
from flask import current_app, Blueprint, jsonify

# 创建测试蓝图
test_blueprint = Blueprint('test', __name__, url_prefix='/api/test')

@test_blueprint.route('/config', methods=['GET'])
def test_config():
    """测试配置读取的API端点"""
    if current_app:
        config_info = {
            'LLM_API_KEY': current_app.config.get('LLM_API_KEY', 'Not found'),
            'LLM_MODEL': current_app.config.get('LLM_MODEL', 'Not found'),
            'LLM_BASE_URL': current_app.config.get('LLM_BASE_URL', 'Not found'),
            'FLASK_CONFIG': os.getenv('FLASK_CONFIG', 'default')
        }
        logging.info(f"Current Flask config: {config_info}")
        return jsonify(config_info), 200
    else:
        return jsonify({'error': 'No Flask app context'}), 500

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentGenerator:
    def __init__(self, api_key=None, model=None, base_url=None):
        # 优先从Flask配置中获取
        if current_app:
            # 打印当前配置环境信息
            current_config_name = os.getenv('FLASK_CONFIG', 'default')
            logger.info(f"Current Flask configuration name: {current_config_name}")
            
            # 获取并记录所有LLM相关配置
            config_model = current_app.config.get('LLM_MODEL', 'DeepSeek-R1')
            config_api_key = current_app.config.get('LLM_API_KEY', 'Not found')
            config_base_url = current_app.config.get('LLM_BASE_URL', 'Not found')
            
            # 检查配置来源
            logger.info(f"Flask app config - LLM_API_KEY: {config_api_key}, LLM_MODEL: {config_model}, LLM_BASE_URL: {config_base_url}")
            
            # 打印配置文件内容进行调试
            try:
                import config
                logger.info(f"Direct config import - LLM_API_KEY: {config.Config.LLM_API_KEY}, LLM_MODEL: {config.Config.LLM_MODEL}")
            except Exception as e:
                logger.warning(f"Failed to directly import config: {str(e)}")
            
            self.api_key = api_key or config_api_key
            self.model = model or config_model
            self.base_url = base_url or config_base_url
            logger.info(f"Loading LLM configuration from Flask app - Model: {self.model}, Base URL: {self.base_url}")
            logger.info(f"Final API key value before setting: {self.api_key}")
        else:
            env_model = os.getenv('LLM_MODEL', 'DeepSeek-R1')
            env_api_key = os.getenv('LLM_API_KEY', 'Not found')
            env_base_url = os.getenv('LLM_BASE_URL', 'Not found')
            logger.info(f"Environment variables - LLM_API_KEY: {env_api_key}, LLM_MODEL: {env_model}, LLM_BASE_URL: {env_base_url}")
            
            self.api_key = api_key or env_api_key
            self.model = model or env_model
            self.base_url = base_url or env_base_url
            logger.info(f"Loading LLM configuration from environment - Model: {self.model}, Base URL: {self.base_url}")
        
        # 强制使用配置文件中设置的模型名称
        if self.model != 'deepseek-ai/DeepSeek-R1':
            logger.warning(f"Overriding model to use configured value: deepseek-ai/DeepSeek-R1 instead of {self.model}")
            self.model = 'deepseek-ai/DeepSeek-R1'
            
        openai.api_key = self.api_key
        openai.api_base = self.base_url
        logger.info(f"OpenAI client configured with API key: {'Set' if self.api_key else 'Not set'}, API base: {self.base_url}")
        logger.info(f"OpenAI client full config - API key exists: {bool(openai.api_key)}, API key length: {len(openai.api_key) if openai.api_key else 0}")

        # 验证API密钥
        if not self.api_key:
            logger.warning('LLM API key is not configured.')
            self.api_key_valid = False
        elif self.api_key in ['your-llm-api-key-here', 'LLM_API_KEY', 'sk-placeholder-for-testing']:
            # 检测默认占位符值
            logger.warning(f'LLM API key is using default placeholder value: {self.api_key}')
            self.api_key_valid = False
        else:
            self.api_key_valid = True
            logger.info(f'LLM API key validation passed (length: {len(self.api_key)})')
    
    def generate_requirement_doc(self, requirement_data):
        """根据需求数据生成完整的需求文档"""
        requirement_title = requirement_data.get('title', 'N/A')
        logger.info(f"Starting document generation for requirement: {requirement_title}")
        
        prompt = self._build_prompt(requirement_data)
        logger.debug(f"Generated prompt length: {len(prompt)} characters")
        
        try:
            if not self.api_key or not getattr(self, 'api_key_valid', True):
                # 如果API密钥无效或未配置，返回示例文档内容，而不是抛出异常
                logger.warning("Using mock document content due to invalid or unconfigured LLM API key")
                
                # 生成示例Markdown文档
                mock_document = f"# {requirement_title}\n\n"
                
                # 添加需求描述
                description = requirement_data.get('description', '无描述')
                mock_document += f"## 需求概述\n\n{description}\n\n"
                
                # 添加内容列表
                mock_document += "## 收集到的内容\n\n"
                contents = requirement_data.get('contents', [])
                for i, content in enumerate(contents, 1):
                    if content.get('content_type') == 'markdown' and content.get('content_text'):
                        mock_document += f"### {i}. 文本内容\n\n{content.get('content_text')[:100]}...\n\n"
                    elif content.get('file_path'):
                        file_name = os.path.basename(content.get('file_path'))
                        mock_document += f"### {i}. 文件附件\n\n[{file_name}]\n\n"
                
                # 添加其他章节
                mock_document += "## 用户场景\n\n此处为用户场景描述\n\n"
                mock_document += "## 功能要求\n\n此处为功能要求列表\n\n"
                mock_document += "## 非功能要求\n\n此处为非功能要求描述\n\n"
                mock_document += "## 附录\n\n此处为附录信息\n\n"
                mock_document += "*此文档使用示例模板生成，因为未配置有效的LLM API密钥。*\n"
                
                return mock_document
            
            # 如果API密钥有效，调用LLM API
            start_time = time.time()
            logger.info(f"Calling LLM API with model: {self.model}")
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional requirement analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            end_time = time.time()
            response_time = round(end_time - start_time, 2)
            logger.info(f"LLM API call completed in {response_time} seconds for requirement: {requirement_title}")
            logger.info(f"Successfully generated document for requirement: {requirement_title}")
            
            # 记录响应统计信息
            token_usage = response.get('usage', {})
            logger.info(f"Token usage - Prompt: {token_usage.get('prompt_tokens', 0)}, \
                       Completion: {token_usage.get('completion_tokens', 0)}, \
                       Total: {token_usage.get('total_tokens', 0)}")
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Unexpected error generating document: {str(e)}", exc_info=True)
            # 即使发生错误，也返回一个示例文档
            fallback_document = f"# {requirement_title}\n\n## 错误信息\n\n生成文档时发生错误：{str(e)}\n\n*此文档为备用模板，用于测试下载功能。*\n"
            return fallback_document
    
    def _build_prompt(self, requirement_data):
        """构建LLM提示词"""
        prompt = f"""
请根据以下用户需求信息，生成一份完整、专业的用户需求文档：

需求标题：{requirement_data.get('title', '')}
需求描述：{requirement_data.get('description', '')}

收集到的原始需求内容：
"""
        
        # 添加收集到的内容
        contents = requirement_data.get('contents', [])
        for i, content in enumerate(contents, 1):
            if content['content_type'] == 'markdown':
                prompt += f"\n{i}. 文本内容：{content['content_text']}"
            elif content['content_type'] == 'image':
                prompt += f"\n{i}. 图片内容：[图片文件 - {content.get('file_path', 'N/A')}]"
            elif content['content_type'] == 'audio':
                prompt += f"\n{i}. 语音内容：[音频文件 - {content.get('file_path', 'N/A')}]"
        
        prompt += """

请按照以下结构生成需求文档：

1. 需求概述
   - 需求背景
   - 需求目标

2. 用户场景
   - 主要用户角色
   - 使用场景描述

3. 功能要求
   - 核心功能列表
   - 功能详细描述

4. 非功能要求
   - 性能要求
   - 安全要求
   - 兼容性要求

5. 附录
   - 术语解释
   - 参考资料

请确保文档内容专业、完整、清晰，符合软件工程规范。
"""
        
        return prompt
    
    def export_to_pdf(self, content, req_id):
        """PDF导出功能已被移除，改用Markdown格式导出"""
        logger.info(f"PDF export requested for requirement: {req_id}, but this feature has been removed")
        logger.warning(f"PDF export is deprecated, use Markdown export instead for requirement: {req_id}")
        raise NotImplementedError("PDF export is no longer supported. Please use Markdown export instead.")