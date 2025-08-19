import openai
import os
import logging
import time
from fpdf import FPDF
from flask import current_app

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentGenerator:
    def __init__(self, api_key=None, model=None, base_url=None):
        # 优先从Flask配置中获取
        if current_app:
            self.api_key = api_key or current_app.config.get('LLM_API_KEY')
            self.model = model or current_app.config.get('LLM_MODEL', 'DeepSeek-R1')
            self.base_url = base_url or current_app.config.get('LLM_BASE_URL', 'https://api.siliconflow.cn/v1')
        else:
            self.api_key = api_key or os.getenv('LLM_API_KEY')
            self.model = model or os.getenv('LLM_MODEL', 'DeepSeek-R1')
            self.base_url = base_url or os.getenv('LLM_BASE_URL', 'https://api.siliconflow.cn/v1')
        
        openai.api_key = self.api_key
        openai.api_base = self.base_url
        
        # 验证API密钥
        if not self.api_key or self.api_key == 'your-llm-api-key-here':
            logger.warning('LLM API key is not properly configured. Using default value which may not work.')
    
    def generate_requirement_doc(self, requirement_data):
        """根据需求数据生成完整的需求文档"""
        requirement_title = requirement_data.get('title', 'N/A')
        logger.info(f"Starting document generation for requirement: {requirement_title}")
        
        prompt = self._build_prompt(requirement_data)
        logger.debug(f"Generated prompt length: {len(prompt)} characters")
        
        try:
            if not self.api_key or self.api_key == 'your-llm-api-key-here':
                raise ValueError("LLM API key is not properly configured. Please set a valid API key in the configuration.")
                
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
        except openai.error.AuthenticationError:
            logger.error("Authentication error with LLM API. Please check your API key.")
            raise Exception("生成文档失败: 认证错误，请检查您的API密钥。")
        except openai.error.APIError as e:
            logger.error(f"LLM API error: {str(e)}")
            raise Exception(f"生成文档失败: API错误 - {str(e)}")
        except openai.error.RateLimitError:
            logger.error("Rate limit exceeded for LLM API.")
            raise Exception("生成文档失败: API请求频率过高，请稍后再试。")
        except Exception as e:
            logger.error(f"Unexpected error generating document: {str(e)}", exc_info=True)
            raise Exception(f"生成文档失败: {str(e)}")
    
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
            if content['content_type'] == 'text':
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
        """将文档内容导出为PDF"""
        logger.info(f"Starting PDF export for requirement: {req_id}")
        try:
            # 创建临时文件路径
            import uuid
            filename = f"requirement-{req_id}-{uuid.uuid4().hex}.pdf"
            file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'uploads', filename)
            
            logger.debug(f"PDF file will be saved to: {file_path}")
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            logger.debug(f"Ensured uploads directory exists: {os.path.dirname(file_path)}")
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # 使用默认字体
            pdf.set_font('Arial', size=12)
            
            # 处理内容编码，确保能被latin-1编码
            logger.debug(f"Adding content to PDF (approx. {len(content)} characters)")
            # 将内容转换为latin-1编码，忽略无法编码的字符
            content_latin1 = content.encode('latin-1', 'ignore').decode('latin-1')
            pdf.multi_cell(0, 10, content_latin1)
            
            # 保存文件
            pdf.output(file_path, 'F')
            logger.info(f"Successfully exported PDF for requirement: {req_id} to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error exporting PDF for requirement: {req_id}, error: {str(e)}", exc_info=True)
            raise Exception(f"Error exporting to PDF: {str(e)}")