import openai
import os
from fpdf import FPDF


class DocumentGenerator:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or os.getenv('LLM_API_KEY')
        self.model = model or os.getenv('LLM_MODEL', 'gpt-4')
        openai.api_key = self.api_key
    
    def generate_requirement_doc(self, requirement_data):
        """根据需求数据生成完整的需求文档"""
        prompt = self._build_prompt(requirement_data)
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional requirement analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating document: {str(e)}")
    
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
        try:
            # 创建临时文件路径
            import uuid
            filename = f"requirement-{req_id}-{uuid.uuid4().hex}.pdf"
            file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'uploads', filename)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            # 使用内置字体
            pdf.set_font("Arial", size=12)
            
            # 添加内容，使用multi_cell处理长文本
            pdf.multi_cell(0, 10, content)
            
            # 保存文件
            pdf.output(file_path)
            return file_path
        except Exception as e:
            raise Exception(f"Error exporting to PDF: {str(e)}")