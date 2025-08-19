from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.requirement import Requirement, UserRequirement, RequirementContent
from ..models.user import User
from .. import db
from ..utils.llm_integration import DocumentGenerator
import uuid
from datetime import datetime
import os

requirements_bp = Blueprint('requirements', __name__)

@requirements_bp.route('/create', methods=['POST'])
@jwt_required()
def create_requirement():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证输入
        if not data or not data.get('title'):
            return jsonify({'message': 'Title is required'}), 400
        
        # 创建需求任务
        requirement = Requirement(
            id=str(uuid.uuid4()),
            title=data['title'],
            description=data.get('description', ''),
            creator_id=current_user_id
        )
        
        db.session.add(requirement)
        
        # 创建用户-需求关联（创建者）
        user_req = UserRequirement(
            user_id=current_user_id,
            requirement_id=requirement.id,
            role='owner'
        )
        
        db.session.add(user_req)
        db.session.commit()
        
        return jsonify({
            'message': 'Requirement created successfully',
            'requirement': requirement.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating requirement', 'error': str(e)}), 500

@requirements_bp.route('/<req_id>/invite', methods=['POST'])
@jwt_required()
def invite_member(req_id):
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # 验证输入
        if not data or not data.get('user_ids'):
            return jsonify({'message': 'User IDs are required'}), 400
        
        # 检查需求任务是否存在
        requirement = Requirement.query.get(req_id)
        if not requirement:
            return jsonify({'message': 'Requirement not found'}), 404
        
        # 验证当前用户是任务创建者
        if requirement.creator_id != current_user_id:
            return jsonify({'message': 'Permission denied'}), 403
        
        # 邀请用户
        invited_users = []
        for user_id in data['user_ids']:
            user = User.query.get(user_id)
            if not user:
                continue
            
            # 检查是否已关联
            if not UserRequirement.query.get((user_id, req_id)):
                user_req = UserRequirement(
                    user_id=user_id,
                    requirement_id=req_id,
                    role='member',
                    joined_at=datetime.utcnow()
                )
                db.session.add(user_req)
                invited_users.append(user.to_dict())
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(invited_users)} users invited successfully',
            'invited_users': invited_users
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error inviting users', 'error': str(e)}), 500

@requirements_bp.route('/list', methods=['GET'])
@jwt_required()
def list_requirements():
    try:
        current_user_id = get_jwt_identity()
        
        # 获取用户参与的所有需求任务
        user_requirements = UserRequirement.query.filter_by(user_id=current_user_id).all()
        req_ids = [ur.requirement_id for ur in user_requirements]
        
        # 查询需求任务
        requirements = Requirement.query.filter(Requirement.id.in_(req_ids)).all()
        
        return jsonify({
            'requirements': [req.to_dict() for req in requirements]
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching requirements', 'error': str(e)}), 500

@requirements_bp.route('/<req_id>', methods=['GET'])
@jwt_required()
def get_requirement(req_id):
    try:
        current_user_id = get_jwt_identity()
        
        # 检查需求任务是否存在
        requirement = Requirement.query.get(req_id)
        if not requirement:
            return jsonify({'message': 'Requirement not found'}), 404
        
        # 检查用户是否有权限访问
        user_req = UserRequirement.query.get((current_user_id, req_id))
        if not user_req:
            return jsonify({'message': 'Permission denied'}), 403
        
        return jsonify({
            'requirement': requirement.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching requirement', 'error': str(e)}), 500

@requirements_bp.route('/<req_id>/participants', methods=['GET'])
@jwt_required()
def get_participants(req_id):
    try:
        current_user_id = get_jwt_identity()
        
        # 检查需求任务是否存在
        requirement = Requirement.query.get(req_id)
        if not requirement:
            return jsonify({'message': 'Requirement not found'}), 404
        
        # 检查用户是否有权限访问
        user_req = UserRequirement.query.get((current_user_id, req_id))
        if not user_req:
            return jsonify({'message': 'Permission denied'}), 403
        
        # 获取参与者列表
        user_requirements = UserRequirement.query.filter_by(requirement_id=req_id).all()
        participants = []
        for ur in user_requirements:
            user = User.query.get(ur.user_id)
            if user:
                participants.append({
                    'id': user.id,
                    'username': user.username,
                    'role': ur.role
                })
        
        return jsonify({
            'participants': participants
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching participants', 'error': str(e)}), 500

@requirements_bp.route('/<req_id>/contents', methods=['GET'])
@jwt_required()
def get_contents(req_id):
    try:
        current_user_id = get_jwt_identity()
        
        # 检查需求任务是否存在
        requirement = Requirement.query.get(req_id)
        if not requirement:
            return jsonify({'message': 'Requirement not found'}), 404
        
        # 检查用户是否有权限访问
        user_req = UserRequirement.query.get((current_user_id, req_id))
        if not user_req:
            return jsonify({'message': 'Permission denied'}), 403
        
        # 获取已提交内容
        contents = RequirementContent.query.filter_by(requirement_id=req_id).all()
        
        return jsonify({
            'contents': [content.to_dict() for content in contents]
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error fetching contents', 'error': str(e)}), 500

@requirements_bp.route('/<req_id>/submit', methods=['POST'])
@jwt_required()
def submit_content(req_id):
    try:
        current_user_id = get_jwt_identity()
        
        # 检查需求任务是否存在
        requirement = Requirement.query.get(req_id)
        if not requirement:
            return jsonify({'message': 'Requirement not found'}), 404
        
        # 检查用户是否有权限提交
        user_req = UserRequirement.query.get((current_user_id, req_id))
        if not user_req:
            return jsonify({'message': 'Permission denied'}), 403
        
        # 处理文本内容
        text_content = request.form.get('text', '')
        
        # 处理文件上传
        file_path = None
        content_type = 'text'
        
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '':
                # 创建上传目录
                upload_dir = current_app.config['UPLOAD_FOLDER']
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                
                # 保存文件
                filename = f"{req_id}_{uuid.uuid4().hex}_{file.filename}"
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                
                # 确定内容类型
                if file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    content_type = 'image'
                elif file.filename.lower().endswith('.mp3'):
                    content_type = 'audio'
                else:
                    content_type = 'file'
        
        # 保存内容记录
        content_record = RequirementContent(
            requirement_id=req_id,
            content_type=content_type,
            content_text=text_content if content_type == 'text' else None,
            file_path=file_path,
            submitted_by=current_user_id
        )
        
        db.session.add(content_record)
        db.session.commit()
        
        return jsonify({
            'message': 'Content submitted successfully',
            'content': content_record.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error submitting content', 'error': str(e)}), 500

@requirements_bp.route('/<req_id>/generate-document', methods=['POST'])
@jwt_required()
def generate_document(req_id):
    try:
        current_user_id = get_jwt_identity()
        
        # 检查需求任务是否存在
        requirement = Requirement.query.get(req_id)
        if not requirement:
            return jsonify({'message': 'Requirement not found'}), 404
        
        # 检查用户是否有权限访问
        user_req = UserRequirement.query.get((current_user_id, req_id))
        if not user_req:
            return jsonify({'message': 'Permission denied'}), 403
        
        # 获取需求的所有内容
        contents = RequirementContent.query.filter_by(requirement_id=req_id).all()
        
        # 准备需求数据
        requirement_data = {
            'title': requirement.title,
            'description': requirement.description,
            'contents': [content.to_dict() for content in contents]
        }
        
        # 生成文档
        generator = DocumentGenerator()
        document = generator.generate_requirement_doc(requirement_data)
        
        return jsonify({
            'message': 'Document generated successfully',
            'document': document
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error generating document', 'error': str(e)}), 500

@requirements_bp.route('/<req_id>/export-pdf', methods=['GET'])
@jwt_required()
def export_pdf(req_id):
    try:
        current_user_id = get_jwt_identity()
        
        # 检查需求任务是否存在
        requirement = Requirement.query.get(req_id)
        if not requirement:
            return jsonify({'message': 'Requirement not found'}), 404
        
        # 检查用户是否有权限访问
        user_req = UserRequirement.query.get((current_user_id, req_id))
        if not user_req:
            return jsonify({'message': 'Permission denied'}), 403
        
        # 获取需求的所有内容
        contents = RequirementContent.query.filter_by(requirement_id=req_id).all()
        
        # 准备需求数据
        requirement_data = {
            'title': requirement.title,
            'description': requirement.description,
            'contents': [content.to_dict() for content in contents]
        }
        
        # 生成文档
        generator = DocumentGenerator()
        document = generator.generate_requirement_doc(requirement_data)
        
        # 导出PDF
        pdf_path = generator.export_to_pdf(document, req_id)
        
        # 返回PDF文件
        return send_file(pdf_path, as_attachment=True, download_name=f'requirement-{req_id}.pdf')
    except Exception as e:
        return jsonify({'message': 'Error exporting PDF', 'error': str(e)}), 500