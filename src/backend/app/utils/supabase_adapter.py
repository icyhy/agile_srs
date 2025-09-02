import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SupabaseRESTAdapter:
    """Supabase REST API适配器，用于替代直接的PostgreSQL连接"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.base_url = supabase_url.rstrip('/')
        self.api_url = f"{self.base_url}/rest/v1"
        self.headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
    def test_connection(self) -> Dict[str, Any]:
        """测试Supabase连接"""
        try:
            # 使用OpenAPI规范端点测试连接
            response = requests.get(f"{self.base_url}/rest/v1/", headers=self.headers, timeout=10)
            
            # 如果基础端点失败，尝试访问系统表
            if response.status_code != 200:
                # 尝试访问pg_tables系统视图来测试连接
                test_headers = self.headers.copy()
                test_headers['Accept'] = 'application/json'
                response = requests.get(
                    f"{self.api_url}/pg_tables?select=tablename&limit=1",
                    headers=test_headers,
                    timeout=10
                )
            
            success = response.status_code in [200, 404]  # 404也表示连接成功，只是没有权限或表不存在
            return {
                'success': success,
                'status_code': response.status_code,
                'message': 'Connection successful' if success else f'HTTP {response.status_code}: {response.text[:100]}'
            }
        except Exception as e:
            return {
                'success': False,
                'status_code': 0,
                'message': str(e)
            }
    
    def create_table_if_not_exists(self, table_name: str, schema: Dict[str, str]) -> bool:
        """创建表（如果不存在）
        
        Args:
            table_name: 表名
            schema: 表结构定义，格式: {'column_name': 'column_type'}
        """
        try:
            # 检查表是否存在
            response = requests.get(
                f"{self.api_url}/{table_name}?limit=1",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"表 {table_name} 已存在")
                return True
            elif response.status_code == 404:
                # 表不存在，需要通过SQL创建
                logger.warning(f"表 {table_name} 不存在，需要手动在Supabase控制台创建")
                logger.info(f"建议的SQL: CREATE TABLE {table_name} ({', '.join([f'{col} {typ}' for col, typ in schema.items()])});")
                return False
            else:
                logger.error(f"检查表 {table_name} 时出错: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"创建表 {table_name} 时出错: {str(e)}")
            return False
    
    def insert(self, table_name: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """插入数据"""
        try:
            response = requests.post(
                f"{self.api_url}/{table_name}",
                headers=self.headers,
                json=data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return response.json()[0] if response.json() else data
            else:
                logger.error(f"插入数据失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"插入数据时出错: {str(e)}")
            return None
    
    def select(self, table_name: str, filters: Optional[Dict[str, Any]] = None, 
               columns: Optional[List[str]] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """查询数据"""
        try:
            url = f"{self.api_url}/{table_name}"
            params = {}
            
            # 添加列选择
            if columns:
                params['select'] = ','.join(columns)
            
            # 添加过滤条件
            if filters:
                for key, value in filters.items():
                    if isinstance(value, str):
                        params[key] = f'eq.{value}'
                    else:
                        params[key] = f'eq.{value}'
            
            # 添加限制
            if limit:
                params['limit'] = limit
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"查询数据失败: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"查询数据时出错: {str(e)}")
            return []
    
    def update(self, table_name: str, filters: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """更新数据"""
        try:
            url = f"{self.api_url}/{table_name}"
            params = {}
            
            # 添加过滤条件
            for key, value in filters.items():
                if isinstance(value, str):
                    params[key] = f'eq.{value}'
                else:
                    params[key] = f'eq.{value}'
            
            response = requests.patch(
                url,
                headers=self.headers,
                params=params,
                json=data,
                timeout=10
            )
            
            return response.status_code in [200, 204]
            
        except Exception as e:
            logger.error(f"更新数据时出错: {str(e)}")
            return False
    
    def delete(self, table_name: str, filters: Dict[str, Any]) -> bool:
        """删除数据"""
        try:
            url = f"{self.api_url}/{table_name}"
            params = {}
            
            # 添加过滤条件
            for key, value in filters.items():
                if isinstance(value, str):
                    params[key] = f'eq.{value}'
                else:
                    params[key] = f'eq.{value}'
            
            response = requests.delete(
                url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            return response.status_code in [200, 204]
            
        except Exception as e:
            logger.error(f"删除数据时出错: {str(e)}")
            return False
    
    def count(self, table_name: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """统计数据数量"""
        try:
            url = f"{self.api_url}/{table_name}"
            headers = {**self.headers, 'Prefer': 'count=exact'}
            params = {'select': 'id'}  # 只选择id列以提高性能
            
            # 添加过滤条件
            if filters:
                for key, value in filters.items():
                    if isinstance(value, str):
                        params[key] = f'eq.{value}'
                    else:
                        params[key] = f'eq.{value}'
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                # 从Content-Range头获取总数
                content_range = response.headers.get('Content-Range', '')
                if content_range and '/' in content_range:
                    return int(content_range.split('/')[-1])
                else:
                    return len(response.json())
            else:
                logger.error(f"统计数据失败: {response.status_code} - {response.text}")
                return 0
                
        except Exception as e:
            logger.error(f"统计数据时出错: {str(e)}")
            return 0

    def get_table_schema(self, table_name: str) -> Dict[str, str]:
        """获取表结构（简化版本）"""
        # 由于REST API限制，这里返回预定义的表结构
        schemas = {
            'users': {
                'id': 'SERIAL PRIMARY KEY',
                'username': 'VARCHAR(80) UNIQUE NOT NULL',
                'email': 'VARCHAR(120) UNIQUE NOT NULL',
                'password_hash': 'VARCHAR(255) NOT NULL',
                'is_active': 'BOOLEAN DEFAULT TRUE',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            },
            'requirements': {
                'id': 'SERIAL PRIMARY KEY',
                'title': 'VARCHAR(200) NOT NULL',
                'description': 'TEXT',
                'priority': 'VARCHAR(20) DEFAULT \'medium\'',
                'status': 'VARCHAR(20) DEFAULT \'pending\'',
                'created_by': 'INTEGER REFERENCES users(id)',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            }
        }
        return schemas.get(table_name, {})