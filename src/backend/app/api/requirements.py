from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.requirement import Requirement, UserRequirement, RequirementContent
from ..models.document import RequirementDocument
from ..models.user import User
from .. import db
from ..utils.llm_integration import DocumentGenerator
from ..utils.database_adapter import get_database_adapter
import uuid
from datetime import datetime
from io import BytesIO
from flask import send_file
import os
import time
import logging
import traceback

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

requirements_bp = Blueprint('requirements', __name__)

@requirements_bp.route('/create', methods=['POST'])
@jwt_required()
def create_requirement():
    try:
        print("=== 开始创建需求 ===")
        current_user_id = get_jwt_identity()
        data = request.get_json()
        print(f"接收到的需求数据: {data}")
        print(f"当前用户ID: {current_user_id}")
        
        # 验证输入
        if not data or not data.get('title'):
            return jsonify({'message': 'Title is required'}), 400
        
        print("初始化数据库适配器")
        db_adapter = get_database_adapter()
        
        # 生成需求ID
        requirement_id = str(uuid.uuid4())
        print(f"生成需求ID: {requirement_id}")
        
        # 创建需求任务
        requirement_data = {
            'id': requirement_id,
            'title': data['title'],
            'description': data.get('description', ''),
            'creator_id': current_user_id,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'active'
        }
        
        print(f"准备插入需求数据: {requirement_data}")
        
        # 根据连接方式选择插入方法
        if hasattr(db_adapter, 'connection_method') and db_adapter.connection_method == 'rest_api':
            print("使用Supabase REST API插入需求")
            result = db_adapter.supabase_rest_adapter.insert('requirements', requirement_data)
            print(f"需求插入结果: {result}")
        else:
            print("使用原始SQL插入需求")
            insert_sql = """
                INSERT INTO requirements (id, title, description, creator_id, created_at, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            db_adapter.execute_raw_query(insert_sql, (
                requirement_id, data['title'], data.get('description', ''),
                current_user_id, datetime.utcnow(), 'active'
            ))
        
        # 创建用户-需求关联（创建者）
        user_req_data = {
            'user_id': current_user_id,
            'requirement_id': requirement_id,
            'role': 'owner',
            'joined_at': datetime.utcnow().isoformat()
        }
        
        print(f"准备插入用户需求关联数据: {user_req_data}")
        
        if hasattr(db_adapter, 'connection_method') and db_adapter.connection_method == 'rest_api':
            print("使用Supabase REST API插入用户需求关联")
            result = db_adapter.supabase_rest_adapter.insert('user_requirements', user_req_data)
            print(f"用户需求关联插入结果: {result}")
        else:
            print("使用原始SQL插入用户需求关联")
            insert_sql = """
                INSERT INTO user_requirements (user_id, requirement_id, role, joined_at)
                VALUES (%s, %s, %s, %s)
            """
            db_adapter.execute_raw_query(insert_sql, (
                current_user_id, requirement_id, 'owner', datetime.utcnow()
            ))
        
        print("需求创建成功")
        return jsonify({
            'message': 'Requirement created successfully',
            'requirement': requirement_data
        }), 201
    except Exception as e:
        print(f"创建需求时发生错误: {str(e)}")
        traceback.print_exc()
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
        # 确保类型一致再比较
        if str(requirement.creator_id) != current_user_id:
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
        print("=== 开始获取需求列表 ===")
        current_user_id = get_jwt_identity()
        print(f"当前用户ID: {current_user_id}")
        
        print("初始化数据库适配器")
        db_adapter = get_database_adapter()
        
        # 获取用户参与的所有需求任务
        print("查询用户参与的需求任务")
        if hasattr(db_adapter, 'connection_method') and db_adapter.connection_method == 'rest_api':
            print("使用Supabase REST API查询用户需求关联")
            user_requirements = db_adapter.supabase_rest_adapter.select(
                'user_requirements', 
                filters={'user_id': current_user_id}
            )
            print(f"用户需求关联查询结果: {user_requirements}")
        else:
            print("使用原始SQL查询用户需求关联")
            select_sql = "SELECT * FROM user_requirements WHERE user_id = %s"
            user_requirements = db_adapter.execute_raw_query(select_sql, (current_user_id,))
        
        if not user_requirements:
            print("用户没有参与任何需求任务")
            return jsonify({'requirements': []}), 200
        
        # 提取需求ID列表
        req_ids = [ur['requirement_id'] for ur in user_requirements]
        print(f"需求ID列表: {req_ids}")
        
        # 查询需求任务详情
        requirements_with_role = []
        for req_id in req_ids:
            print(f"查询需求详情: {req_id}")
            if hasattr(db_adapter, 'connection_method') and db_adapter.connection_method == 'rest_api':
                print("使用Supabase REST API查询需求详情")
                requirements = db_adapter.supabase_rest_adapter.select(
                    'requirements', 
                    filters={'id': req_id}
                )
                print(f"需求详情查询结果: {requirements}")
            else:
                print("使用原始SQL查询需求详情")
                select_sql = "SELECT * FROM requirements WHERE id = %s"
                requirements = db_adapter.execute_raw_query(select_sql, (req_id,))
            
            if requirements:
                req = requirements[0]  # 取第一个结果
                # 查找当前用户在该需求中的角色
                user_req = next((ur for ur in user_requirements if ur['requirement_id'] == req_id), None)
                req['role'] = user_req['role'] if user_req else 'member'
                requirements_with_role.append(req)
        
        print(f"最终需求列表: {requirements_with_role}")
        return jsonify({
            'requirements': requirements_with_role
        }), 200
    except Exception as e:
        print(f"获取需求列表时发生错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'message': 'Error fetching requirements', 'error': str(e)}), 500

@requirements_bp.route('/<req_id>', methods=['GET'])
@jwt_required()
def get_requirement(req_id):
    try:
        print(f"=== 开始获取需求详情: {req_id} ===")
        current_user_id = get_jwt_identity()
        print(f"当前用户ID: {current_user_id}")
        
        print("初始化数据库适配器")
        db_adapter = get_database_adapter()
        
        # 检查需求任务是否存在
        print(f"查询需求详情: {req_id}")
        if hasattr(db_adapter, 'connection_method') and db_adapter.connection_method == 'rest_api':
            print("使用Supabase REST API查询需求详情")
            requirements = db_adapter.supabase_rest_adapter.select(
                'requirements', 
                filters={'id': req_id}
            )
            print(f"需求详情查询结果: {requirements}")
        else:
            print("使用原始SQL查询需求详情")
            select_sql = "SELECT * FROM requirements WHERE id = %s"
            requirements = db_adapter.execute_raw_query(select_sql, (req_id,))
        
        if not requirements:
            print("需求不存在")
            return jsonify({'message': 'Requirement not found'}), 404
        
        requirement = requirements[0]
        
        # 检查用户是否有权限访问
        print(f"检查用户权限: user_id={current_user_id}, requirement_id={req_id}")
        if hasattr(db_adapter, 'connection_method') and db_adapter.connection_method == 'rest_api':
            print("使用Supabase REST API查询用户权限")
            user_requirements = db_adapter.supabase_rest_adapter.select(
                'user_requirements', 
                filters={'user_id': current_user_id, 'requirement_id': req_id}
            )
            print(f"用户权限查询结果: {user_requirements}")
        else:
            print("使用原始SQL查询用户权限")
            select_sql = "SELECT * FROM user_requirements WHERE user_id = %s AND requirement_id = %s"
            user_requirements = db_adapter.execute_raw_query(select_sql, (current_user_id, req_id))
        
        if not user_requirements:
            print("用户无权限访问")
            return jsonify({'message': 'Permission denied'}), 403
        
        print("需求详情获取成功")
        return jsonify({
            'requirement': requirement
        }), 200
    except Exception as e:
        print(f"获取需求详情时发生错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'message': 'Error fetching requirement', 'error': str(e)}), 500

@requirements_bp.route('/<req_id>/participants', methods=['GET'])
@jwt_required()
def get_participants(req_id):
    try:
        current_user_id = get_jwt_identity()
        db_adapter = get_database_adapter()
        
        print(f"[get_participants] Starting for req_id: {req_id}, user_id: {current_user_id}")
        
        # 检查需求任务是否存在
        if hasattr(db_adapter, 'connection_method') and db_adapter.connection_method == 'rest_api':
            # 使用Supabase REST API
            requirement_response = db_adapter.supabase_rest_adapter.select('requirements', filters={'id': req_id})
            print(f"[get_participants] Requirement query response: {requirement_response}")
            
            if not requirement_response:
                return jsonify({'message': 'Requirement not found'}), 404
            
            # 检查用户是否有权限访问
            user_req_response = db_adapter.supabase_rest_adapter.select('user_requirements', filters={'user_id': current_user_id, 'requirement_id': req_id})
            print(f"[get_participants] User requirement query response: {user_req_response}")
            
            if not user_req_response:
                return jsonify({'message': 'Permission denied'}), 403
            
            # 获取参与者列表
            user_requirements_response = db_adapter.supabase_rest_adapter.select('user_requirements', filters={'requirement_id': req_id})
            print(f"[get_participants] User requirements query response: {user_requirements_response}")
            
            participants = []
            for ur in user_requirements_response:
                user_response = db_adapter.supabase_rest_adapter.select('users', filters={'id': ur['user_id']})
                print(f"[get_participants] User query response for user_id {ur['user_id']}: {user_response}")
                
                if user_response:
                    user = user_response[0]
                    participants.append({
                        'id': user['id'],
                        'username': user['username'],
                        'role': ur['role']
                    })
        else:
            # 使用原始SQL查询
            requirement_query = "SELECT * FROM requirements WHERE id = %s"
            requirement_result = db_adapter.execute_query(requirement_query, (req_id,))
            print(f"[get_participants] Requirement query result: {requirement_result}")
            
            if not requirement_result:
                return jsonify({'message': 'Requirement not found'}), 404
            
            # 检查用户是否有权限访问
            user_req_query = "SELECT * FROM user_requirements WHERE user_id = %s AND requirement_id = %s"
            user_req_result = db_adapter.execute_query(user_req_query, (current_user_id, req_id))
            print(f"[get_participants] User requirement query result: {user_req_result}")
            
            if not user_req_result:
                return jsonify({'message': 'Permission denied'}), 403
            
            # 获取参与者列表
            user_requirements_query = "SELECT * FROM user_requirements WHERE requirement_id = %s"
            user_requirements_result = db_adapter.execute_query(user_requirements_query, (req_id,))
            print(f"[get_participants] User requirements query result: {user_requirements_result}")
            
            participants = []
            for ur in user_requirements_result:
                user_query = "SELECT * FROM users WHERE id = %s"
                user_result = db_adapter.execute_query(user_query, (ur['user_id'],))
                print(f"[get_participants] User query result for user_id {ur['user_id']}: {user_result}")
                
                if user_result:
                    user = user_result[0]
                    participants.append({
                        'id': user['id'],
                        'username': user['username'],
                        'role': ur['role']
                    })
        
        print(f"[get_participants] Final participants: {participants}")
        return jsonify({
            'participants': participants
        }), 200
    except Exception as e:
        print(f"[get_participants] Error: {str(e)}")
        print(f"[get_participants] Traceback: {traceback.format_exc()}")
        return jsonify({'message': 'Error fetching participants', 'error': str(e)}), 500

@requirements_bp.route('/<req_id>/contents', methods=['GET'])
@jwt_required()
def get_contents(req_id):
    try:
        print(f"=== 开始获取需求内容: {req_id} ===")
        current_user_id = get_jwt_identity()
        print(f"当前用户ID: {current_user_id}")
        
        print("初始化数据库适配器")
        db_adapter = get_database_adapter()
        
        # 检查需求任务是否存在
        print(f"查询需求详情: {req_id}")
        if hasattr(db_adapter, 'connection_method') and db_adapter.connection_method == 'rest_api':
            print("使用Supabase REST API查询需求详情")
            requirements = db_adapter.supabase_rest_adapter.select(
                'requirements', 
                filters={'id': req_id}
            )
            print(f"需求详情查询结果: {requirements}")
        else:
            print("使用原始SQL查询需求详情")
            select_sql = "SELECT * FROM requirements WHERE id = %s"
            requirements = db_adapter.execute_raw_query(select_sql, (req_id,))
        
        if not requirements:
            print("需求不存在")
            return jsonify({'message': 'Requirement not found'}), 404
        
        # 检查用户是否有权限访问
        print(f"检查用户权限: user_id={current_user_id}, requirement_id={req_id}")
        if hasattr(db_adapter, 'connection_method') and db_adapter.connection_method == 'rest_api':
            print("使用Supabase REST API查询用户权限")
            user_requirements = db_adapter.supabase_rest_adapter.select(
                'user_requirements', 
                filters={'user_id': current_user_id, 'requirement_id': req_id}
            )
            print(f"用户权限查询结果: {user_requirements}")
        else:
            print("使用原始SQL查询用户权限")
            select_sql = "SELECT * FROM user_requirements WHERE user_id = %s AND requirement_id = %s"
            user_requirements = db_adapter.execute_raw_query(select_sql, (current_user_id, req_id))
        
        if not user_requirements:
            print("用户无权限访问")
            return jsonify({'message': 'Permission denied'}), 403
        
        # 获取已提交内容
        print(f"查询需求内容: {req_id}")
        if hasattr(db_adapter, 'connection_method') and db_adapter.connection_method == 'rest_api':
            print("使用Supabase REST API查询需求内容")
            contents = db_adapter.supabase_rest_adapter.select(
                'requirement_contents', 
                filters={'requirement_id': req_id}
            )
            print(f"需求内容查询结果: {contents}")
        else:
            print("使用原始SQL查询需求内容")
            select_sql = "SELECT * FROM requirement_contents WHERE requirement_id = %s"
            contents = db_adapter.execute_raw_query(select_sql, (req_id,))
        
        print("需求内容获取成功")
        return jsonify({
            'contents': contents or []
        }), 200
    except Exception as e:
        print(f"获取需求内容时发生错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'message': 'Error fetching contents', 'error': str(e)}), 500

@requirements_bp.route('/<req_id>/submit', methods=['POST'])
@jwt_required()
def submit_content(req_id):
    db_adapter = None
    try:
        current_user_id = get_jwt_identity()
        print(f"[submit_content] Starting for req_id: {req_id}, user_id: {current_user_id}")
        db_adapter = get_database_adapter()
        print(f"[submit_content] db_adapter: {db_adapter}, type: {type(db_adapter)}")
        if hasattr(db_adapter, 'connection_method'):
            print(f"[submit_content] connection_method: {db_adapter.connection_method}")
        else:
            print(f"[submit_content] No connection_method attribute")
        
        # 检查需求任务是否存在
        if hasattr(db_adapter, 'connection_method') and db_adapter.connection_method == 'rest_api':
            requirement_response = db_adapter.supabase_rest_adapter.select('requirements', filters={'id': req_id})
            if not requirement_response:
                return jsonify({'message': 'Requirement not found'}), 404
        else:
            print(f"[submit_content] Querying requirement with id: {req_id}")
            requirement = Requirement.query.get(req_id)
            print(f"[submit_content] Requirement query result: {requirement}")
            if not requirement:
                print(f"[submit_content] Requirement not found for id: {req_id}")
                return jsonify({'message': 'Requirement not found'}), 404
        
        # 检查用户是否有权限提交
        if hasattr(db_adapter, 'connection_method') and db_adapter.connection_method == 'rest_api':
            user_req_response = db_adapter.supabase_rest_adapter.select('user_requirements', filters={'user_id': current_user_id, 'requirement_id': req_id})
            if not user_req_response:
                return jsonify({'message': 'Permission denied'}), 403
        else:
            user_req = UserRequirement.query.get((current_user_id, req_id))
            if not user_req:
                return jsonify({'message': 'Permission denied'}), 403
        
        # 处理文本内容
        text_content = request.form.get('text', '')
        
        # 获取前端传递的内容类型，如果没有则默认为'text'
        content_type = request.form.get('content_type', 'text')
        
        # 处理文件上传
        file_path = None
        
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
                
                # 如果上传了文件，但内容类型已经设置为markdown，则保留markdown类型
                # 否则根据文件类型设置内容类型
                if content_type != 'markdown':
                    if file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        content_type = 'image'
                    elif file.filename.lower().endswith('.mp3'):
                        content_type = 'audio'
                    else:
                        content_type = 'file'
        
        # 保存内容记录
        content_data = {
            'id': str(uuid.uuid4()),
            'requirement_id': req_id,
            'content_type': content_type,
            'content_text': text_content if content_type in ['text', 'markdown'] else None,
            'file_path': file_path,
            'submitted_by': current_user_id,
            'created_at': datetime.utcnow().isoformat()
        }
        
        if hasattr(db_adapter, 'connection_method') and db_adapter.connection_method == 'rest_api':
            content_record = db_adapter.supabase_rest_adapter.insert('requirement_contents', content_data)
            if not content_record:
                return jsonify({'message': 'Error submitting content'}), 500
        else:
            content_record = RequirementContent(
                requirement_id=req_id,
                content_type=content_type,
                content_text=text_content if content_type in ['text', 'markdown'] else None,
                file_path=file_path,
                submitted_by=current_user_id
            )
            db.session.add(content_record)
            db.session.commit()
            content_data = content_record.to_dict()
        
        return jsonify({
            'message': 'Content submitted successfully',
            'content': content_data
        }), 201
    except Exception as e:
        print(f"[submit_content] Exception occurred: {str(e)}")
        print(f"[submit_content] Exception type: {type(e)}")
        import traceback
        print(f"[submit_content] Traceback: {traceback.format_exc()}")
        try:
            if db_adapter and hasattr(db_adapter, 'connection_method') and db_adapter.connection_method != 'rest_api':
                db.session.rollback()
        except:
            print(f"[submit_content] Error in rollback")
        return jsonify({'message': 'Error submitting content', 'error': str(e)}), 500

@requirements_bp.route('/<req_id>/generate-document', methods=['POST'])
@jwt_required()
def generate_document(req_id):
    try:
        current_user_id = get_jwt_identity()
        logger.info(f"Received request to generate document for requirement: {req_id} by user: {current_user_id}")
        
        # 检查需求任务是否存在
        requirement = Requirement.query.get(req_id)
        if not requirement:
            logger.warning(f"Requirement not found: {req_id} requested by user: {current_user_id}")
            return jsonify({'message': 'Requirement not found'}), 404
        
        # 检查用户是否有权限访问
        user_req = UserRequirement.query.get((current_user_id, req_id))
        if not user_req:
            logger.warning(f"Permission denied: User {current_user_id} tried to access requirement {req_id}")
            return jsonify({'message': 'Permission denied'}), 403
        
        # 获取需求的所有内容
        contents = RequirementContent.query.filter_by(requirement_id=req_id).all()
        logger.info(f"Found {len(contents)} content items for requirement: {req_id}")
        
        # 准备需求数据
        requirement_data = {
            'title': requirement.title,
            'description': requirement.description,
            'contents': [content.to_dict() for content in contents]
        }
        
        # 生成文档
        generator = DocumentGenerator()
        logger.info(f"Starting document generation for requirement: {req_id} - {requirement.title}")
        document = generator.generate_requirement_doc(requirement_data)
        
        logger.info(f"Successfully generated document for requirement: {req_id} - {requirement.title}")
        
        # 保存文档版本
        # 获取当前最新版本号
        latest_version = db.session.query(db.func.max(RequirementDocument.version))\
            .filter_by(requirement_id=req_id).scalar() or 0
        new_version = latest_version + 1
        
        # 创建文档版本记录（不再生成PDF）
        doc_record = RequirementDocument(
            requirement_id=req_id,
            version=new_version,
            content=document,
            pdf_path=None  # PDF不再生成，设为None
        )
        
        db.session.add(doc_record)
        db.session.commit()
        
        return jsonify({
            'message': 'Document generated successfully',
            'document': document,
            'version': new_version
        }), 200
    except Exception as e:
        logger.error(f"Error generating document for requirement: {req_id}, error: {str(e)}", exc_info=True)
        return jsonify({'message': 'Error generating document', 'error': str(e)}), 500

@requirements_bp.route('/<req_id>/documents', methods=['GET'])
@jwt_required()
def get_requirement_documents(req_id):
    try:
        user_id = get_jwt_identity()
        db_adapter = get_database_adapter()
        
        print(f"[get_requirement_documents] Starting for req_id: {req_id}, user_id: {user_id}")
        
        # 检查用户权限
        if hasattr(db_adapter, 'connection_method') and db_adapter.connection_method == 'rest_api':
            # 使用Supabase REST API
            user_req_response = db_adapter.supabase_rest_adapter.select('user_requirements', filters={'user_id': user_id, 'requirement_id': req_id})
            print(f"[get_requirement_documents] User requirement query response: {user_req_response}")
            
            if not user_req_response:
                return jsonify({'message': 'Unauthorized access'}), 403
            
            # 获取所有文档版本
            documents_response = db_adapter.supabase_rest_adapter.select('requirement_documents', filters={'requirement_id': req_id})
            print(f"[get_requirement_documents] Documents query response: {documents_response}")
            
            documents = []
            for doc in documents_response:
                documents.append({
                    'id': doc['id'],
                    'requirement_id': doc['requirement_id'],
                    'version': doc['version'],
                    'content': doc['content'],
                    'created_at': doc['created_at']
                })
        else:
            # 使用原始SQL查询
            user_req_query = "SELECT * FROM user_requirements WHERE user_id = %s AND requirement_id = %s"
            user_req_result = db_adapter.execute_query(user_req_query, (user_id, req_id))
            print(f"[get_requirement_documents] User requirement query result: {user_req_result}")
            
            if not user_req_result:
                return jsonify({'message': 'Unauthorized access'}), 403
            
            # 获取所有文档版本
            documents_query = "SELECT * FROM requirement_documents WHERE requirement_id = %s ORDER BY version DESC"
            documents_result = db_adapter.execute_query(documents_query, (req_id,))
            print(f"[get_requirement_documents] Documents query result: {documents_result}")
            
            documents = []
            for doc in documents_result:
                documents.append({
                    'id': doc['id'],
                    'requirement_id': doc['requirement_id'],
                    'version': doc['version'],
                    'content': doc['content'],
                    'created_at': doc['created_at']
                })
        
        print(f"[get_requirement_documents] Final documents: {len(documents)} documents found")
        return jsonify({
            'documents': documents
        }), 200
    except Exception as e:
        print(f"[get_requirement_documents] Error: {str(e)}")
        print(f"[get_requirement_documents] Traceback: {traceback.format_exc()}")
        return jsonify({'message': 'Error fetching documents', 'error': str(e)}), 500


@requirements_bp.route('/<req_id>/documents/<int:version>', methods=['GET'])
@jwt_required()
def get_requirement_document_version(req_id, version):
    user_id = get_jwt_identity()
    
    # 检查用户权限
    if not UserRequirement.query.filter_by(
        user_id=user_id, requirement_id=req_id
    ).first():  
        return jsonify({'message': 'Unauthorized access'}), 403
    
    # 获取特定版本文档
    document = RequirementDocument.query.filter_by(
        requirement_id=req_id, version=version
    ).first()
    
    if not document:
        return jsonify({'message': 'Document version not found'}), 404
    
    return jsonify({
        'document': document.to_dict()
    }), 200


@requirements_bp.route('/<req_id>/document/<int:version>', methods=['DELETE'])
@jwt_required()
def delete_requirement_document(req_id, version):
    try:
        current_user_id = get_jwt_identity()
        
        # 检查需求任务是否存在
        requirement = Requirement.query.get(req_id)
        if not requirement:
            return jsonify({'message': 'Requirement not found'}), 404
        
        # 验证当前用户是任务创建者
        if str(requirement.creator_id) != current_user_id:
            return jsonify({'message': 'Permission denied'}), 403
        
        # 获取特定版本文档
        document = RequirementDocument.query.filter_by(
            requirement_id=req_id, version=version
        ).first()
        
        if not document:
            return jsonify({'message': 'Document version not found'}), 404
        
        # 删除文档版本
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({
            'message': 'Document version deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting document version', 'error': str(e)}), 500


# 为了保持兼容性，保留无版本参数的路由
@requirements_bp.route('/<req_id>/export-markdown', methods=['GET'])
@jwt_required()
def export_markdown_latest(req_id):
    try:
        # 获取最新版本
        latest_document = RequirementDocument.query.filter_by(requirement_id=req_id)\
            .order_by(RequirementDocument.version.desc()).first()
        
        if latest_document:
            return export_markdown(req_id, latest_document.version)
        else:
            logger.error(f"No document found in database for requirement: {req_id}")
            return jsonify({'message': 'Failed to download document: No document found in database'}), 404
    except Exception as e:
        logger.error(f"Error fetching latest document version: {str(e)}")
        return jsonify({'message': 'Failed to download document: Database error'}), 500

@requirements_bp.route('/<req_id>/export-markdown/<int:version>', methods=['GET'])
@jwt_required()
def export_markdown(req_id, version):
    try:
        current_user_id = get_jwt_identity()
        logger.info(f"Received request to export Markdown for requirement: {req_id}, version: {version} by user: {current_user_id}")
        
        # 检查需求任务是否存在
        requirement = Requirement.query.get(req_id)
        if not requirement:
            logger.warning(f"Requirement not found: {req_id} requested by user: {current_user_id}")
            return jsonify({'message': 'Requirement not found'}), 404
        
        # 检查用户是否有权限访问
        user_req = UserRequirement.query.get((current_user_id, req_id))
        if not user_req:
            logger.warning(f"Permission denied: User {current_user_id} tried to access requirement {req_id}")
            return jsonify({'message': 'Permission denied'}), 403
        
        # 从数据库获取指定版本的文档
        try:
            document = RequirementDocument.query.filter_by(
                requirement_id=req_id,
                version=version
            ).first()
            
            if document:
                logger.info(f"Found document for requirement: {req_id}, version: {version}")
                document_content = document.content

                # 生成Markdown文件
                from io import BytesIO
                buffer = BytesIO()
                buffer.write(document_content.encode('utf-8'))
                buffer.seek(0)

                # 设置文件名，包含版本信息
                file_name = f"requirement_{req_id}_v{version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

                return send_file(
                    buffer,
                    as_attachment=True,
                    download_name=file_name,
                    mimetype='text/markdown'
                )
            else:
                logger.error(f"Document version {version} not found for requirement: {req_id}")
                return jsonify({'message': f'Failed to download document: Version {version} not found'}), 404
        except Exception as e:
            logger.error(f"Error fetching document from database: {str(e)}")
            return jsonify({'message': 'Failed to download document: Database error'}), 500
        
        # 使用BytesIO而不是临时文件，避免Windows上的文件锁定问题
        from io import BytesIO
        import os
        
        # 准备文件名
        safe_title = requirement.title.replace(' ', '_').replace('/', '_')[:50]
        filename = f"{safe_title}_v{int(time.time())}.md"
        
        # 将文档内容转换为字节流
        file_stream = BytesIO()
        file_stream.write(document.encode('utf-8'))
        file_stream.seek(0)
        
        logger.info(f"Successfully created Markdown content for requirement: {req_id} - {requirement.title}")
        
        # 返回文档内容作为附件下载
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=filename,
            mimetype='text/markdown',
            max_age=0  # 禁用缓存
        )
    except Exception as e:
          logger.error(f"Error exporting Markdown for requirement: {req_id}, error: {str(e)}", exc_info=True)
          return jsonify({'message': 'Failed to export Markdown', 'error': str(e)}), 500

@requirements_bp.route('/<req_id>/remove_participant/<user_id>', methods=['DELETE'])
@jwt_required()
def remove_participant(req_id, user_id):
    try:
        current_user_id = get_jwt_identity()
        
        # 检查需求任务是否存在
        requirement = Requirement.query.get(req_id)
        if not requirement:
            return jsonify({'message': 'Requirement not found'}), 404
        
        # 验证当前用户是任务创建者
        if str(requirement.creator_id) != current_user_id:
            return jsonify({'message': 'Permission denied'}), 403
        
        # 不能删除自己
        if str(user_id) == current_user_id:
            return jsonify({'message': 'Cannot remove yourself'}), 400
        
        # 检查用户是否是参与者
        user_req = UserRequirement.query.get((user_id, req_id))
        if not user_req:
            return jsonify({'message': 'User is not a participant'}), 400
        
        # 删除用户-需求关联
        db.session.delete(user_req)
        db.session.commit()
        
        return jsonify({
            'message': 'Participant removed successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error removing participant', 'error': str(e)}), 500

@requirements_bp.route('/<req_id>/content/<content_id>', methods=['DELETE'])
@jwt_required()
def delete_content(req_id, content_id):
    try:
        current_user_id = get_jwt_identity()
        
        # 检查需求任务是否存在
        requirement = Requirement.query.get(req_id)
        if not requirement:
            return jsonify({'message': 'Requirement not found'}), 404
        
        # 检查内容是否存在
        content = RequirementContent.query.get(content_id)
        if not content:
            return jsonify({'message': 'Content not found'}), 404
        
        # 检查内容是否属于该需求
        if content.requirement_id != req_id:
            return jsonify({'message': 'Content does not belong to this requirement'}), 400
        
        # 检查用户是否有权限删除（只能删除自己提交的内容）
        if str(content.submitted_by) != current_user_id:
            return jsonify({'message': 'Permission denied'}), 403
        
        # 删除内容
        db.session.delete(content)
        db.session.commit()
        
        return jsonify({
            'message': 'Content deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error deleting content', 'error': str(e)}), 500

@requirements_bp.route('/<req_id>', methods=['PUT'])
@jwt_required()
def update_requirement(req_id):
    try:
        # 注意：get_jwt_identity()返回的是字符串类型，需要转换为整数
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # 检查需求任务是否存在
        requirement = Requirement.query.get(req_id)
        if not requirement:
            return jsonify({'message': 'Requirement not found'}), 404
        
        # 检查用户是否有权限编辑（只有创建者可以编辑）
        if requirement.creator_id != current_user_id:
            return jsonify({'message': 'Permission denied'}), 403
        
        # 更新需求信息
        if 'title' in data:
            requirement.title = data['title']
        if 'description' in data:
            requirement.description = data['description']
        if 'status' in data:
            requirement.status = data['status']
        
        requirement.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Requirement updated successfully',
            'requirement': requirement.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating requirement', 'error': str(e)}), 500