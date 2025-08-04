#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理模块
"""

import hashlib
import secrets
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from database import DatabaseManager
from github_manager import GitHubManager

class UserManager:
    """用户管理器"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.github_manager = GitHubManager()
        self.logger = logging.getLogger(__name__)
        
    def add_user(self, username: str, token: str) -> Optional[int]:
        """添加用户"""
        try:
            # 验证用户名是否已存在
            existing_user = self.db_manager.get_user_by_username(username)
            if existing_user:
                self.logger.error(f"用户名已存在: {username}")
                return None
                
            # 验证Token有效性
            if not self.github_manager.test_token(token):
                self.logger.error(f"无效的GitHub Token: {username}")
                return None
                
            # 添加用户到数据库
            user_id = self.db_manager.insert_user(username, token)
            
            if user_id:
                self.logger.info(f"用户添加成功: {username} (ID: {user_id})")
                return user_id
            else:
                self.logger.error(f"用户添加失败: {username}")
                return None
                
        except Exception as e:
            self.logger.error(f"添加用户失败: {str(e)}")
            return None
            
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        try:
            user = self.db_manager.get_user_by_id(user_id)
            if user:
                # 不返回Token信息
                user_info = dict(user)
                user_info.pop('token', None)
                return user_info
            return None
            
        except Exception as e:
            self.logger.error(f"获取用户信息失败: {str(e)}")
            return None
            
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名获取用户"""
        try:
            user = self.db_manager.get_user_by_username(username)
            if user:
                # 不返回Token信息
                user_info = dict(user)
                user_info.pop('token', None)
                return user_info
            return None
            
        except Exception as e:
            self.logger.error(f"获取用户信息失败: {str(e)}")
            return None
            
    def get_all_users(self) -> List[Dict[str, Any]]:
        """获取所有用户"""
        try:
            users = self.db_manager.get_all_users()
            
            # 不返回Token信息
            for user in users:
                user.pop('token', None)
                
            return users
            
        except Exception as e:
            self.logger.error(f"获取所有用户失败: {str(e)}")
            return []
            
    def update_user(self, user_id: int, username: str, token: str) -> bool:
        """更新用户信息"""
        try:
            # 检查用户是否存在
            existing_user = self.db_manager.get_user_by_id(user_id)
            if not existing_user:
                self.logger.error(f"用户不存在: {user_id}")
                return False
                
            # 检查用户名是否被其他用户使用
            user_with_same_name = self.db_manager.get_user_by_username(username)
            if user_with_same_name and user_with_same_name['id'] != user_id:
                self.logger.error(f"用户名已被使用: {username}")
                return False
                
            # 验证Token有效性
            if not self.github_manager.test_token(token):
                self.logger.error(f"无效的GitHub Token: {username}")
                return False
                
            # 更新用户信息
            success = self.db_manager.update_user(user_id, username, token)
            
            if success:
                self.logger.info(f"用户信息更新成功: {username}")
            else:
                self.logger.error(f"用户信息更新失败: {username}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"更新用户信息失败: {str(e)}")
            return False
            
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        try:
            # 检查用户是否存在
            existing_user = self.db_manager.get_user_by_id(user_id)
            if not existing_user:
                self.logger.error(f"用户不存在: {user_id}")
                return False
                
            # 删除用户
            success = self.db_manager.delete_user(user_id)
            
            if success:
                self.logger.info(f"用户删除成功: {user_id}")
            else:
                self.logger.error(f"用户删除失败: {user_id}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"删除用户失败: {str(e)}")
            return False
            
    def authenticate_user(self, username: str, token: str) -> Optional[int]:
        """用户认证"""
        try:
            # 获取用户信息
            user = self.db_manager.get_user_by_username(username)
            if not user:
                self.logger.warning(f"用户不存在: {username}")
                return None
                
            # 验证Token
            if user['token'] != token:
                self.logger.warning(f"Token验证失败: {username}")
                return None
                
            # 验证Token有效性
            if not self.github_manager.test_token(token):
                self.logger.warning(f"Token已失效: {username}")
                return None
                
            self.logger.info(f"用户认证成功: {username}")
            return user['id']
            
        except Exception as e:
            self.logger.error(f"用户认证失败: {str(e)}")
            return None
            
    def get_user_token(self, user_id: int) -> Optional[str]:
        """获取用户Token"""
        try:
            user = self.db_manager.get_user_by_id(user_id)
            if user:
                return user.get('token')
            return None
            
        except Exception as e:
            self.logger.error(f"获取用户Token失败: {str(e)}")
            return None
            
    def test_user_token(self, user_id: int) -> bool:
        """测试用户Token有效性"""
        try:
            token = self.get_user_token(user_id)
            if not token:
                return False
                
            return self.github_manager.test_token(token)
            
        except Exception as e:
            self.logger.error(f"测试用户Token失败: {str(e)}")
            return False
            
    def refresh_user_token(self, user_id: int, new_token: str) -> bool:
        """刷新用户Token"""
        try:
            # 验证新Token
            if not self.github_manager.test_token(new_token):
                self.logger.error(f"无效的新Token: {user_id}")
                return False
                
            # 获取用户信息
            user = self.db_manager.get_user_by_id(user_id)
            if not user:
                self.logger.error(f"用户不存在: {user_id}")
                return False
                
            # 更新Token
            success = self.db_manager.update_user(user_id, user['username'], new_token)
            
            if success:
                self.logger.info(f"用户Token刷新成功: {user['username']}")
            else:
                self.logger.error(f"用户Token刷新失败: {user['username']}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"刷新用户Token失败: {str(e)}")
            return False
            
    def get_user_github_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户GitHub信息"""
        try:
            token = self.get_user_token(user_id)
            if not token:
                return None
                
            # 临时设置Token
            self.github_manager.set_token(token)
            
            # 获取GitHub用户信息
            github_info = self.github_manager.get_user_info()
            
            return github_info
            
        except Exception as e:
            self.logger.error(f"获取用户GitHub信息失败: {str(e)}")
            return None
            
    def validate_username(self, username: str) -> bool:
        """验证用户名格式"""
        try:
            # 用户名不能为空
            if not username or not username.strip():
                return False
                
            # 用户名长度限制
            if len(username) < 3 or len(username) > 50:
                return False
                
            # 用户名只能包含字母、数字、下划线和连字符
            import re
            if not re.match(r'^[a-zA-Z0-9_-]+$', username):
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"验证用户名失败: {str(e)}")
            return False
            
    def validate_token(self, token: str) -> bool:
        """验证Token格式"""
        try:
            # Token不能为空
            if not token or not token.strip():
                return False
                
            # GitHub Token长度检查
            if len(token) < 40:
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"验证Token失败: {str(e)}")
            return False
            
    def get_user_statistics(self) -> Dict[str, Any]:
        """获取用户统计信息"""
        try:
            users = self.get_all_users()
            
            total_users = len(users)
            active_users = 0
            inactive_users = 0
            
            for user in users:
                if self.test_user_token(user['id']):
                    active_users += 1
                else:
                    inactive_users += 1
                    
            return {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': inactive_users,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"获取用户统计信息失败: {str(e)}")
            return {
                'total_users': 0,
                'active_users': 0,
                'inactive_users': 0,
                'last_updated': datetime.now().isoformat()
            } 