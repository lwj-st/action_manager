#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub API管理模块
"""

import requests
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

class GitHubManager:
    """GitHub API管理器"""
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        self.token = None
        self.logger = logging.getLogger(__name__)
        
        # 设置默认请求头
        self.session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-Action-Manager/1.0.0'
        })
        
    def set_token(self, token: str):
        """设置GitHub Token"""
        self.token = token
        self.session.headers.update({
            'Authorization': f'token {token}'
        })
        
    def test_connection(self) -> bool:
        """测试GitHub连接"""
        try:
            if not self.token:
                return False
                
            response = self.session.get(f"{self.base_url}/user")
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"测试GitHub连接失败: {str(e)}")
            return False
            
    def test_token(self, token: str) -> bool:
        """测试Token有效性"""
        try:
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'GitHub-Action-Manager/1.0.0'
            }
            
            response = requests.get(f"{self.base_url}/user", headers=headers)
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"测试Token失败: {str(e)}")
            return False
            
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        try:
            if not self.token:
                return None
                
            response = self.session.get(f"{self.base_url}/user")
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            self.logger.error(f"获取用户信息失败: {str(e)}")
            return None
            
    def list_workflows(self, repo: str) -> List[Dict[str, Any]]:
        """列出仓库的工作流"""
        try:
            if not self.token:
                return []
                
            url = f"{self.base_url}/repos/{repo}/actions/workflows"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('workflows', [])
            else:
                self.logger.error(f"获取工作流列表失败: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            self.logger.error(f"获取工作流列表失败: {str(e)}")
            return []
            
    def get_workflow(self, repo: str, workflow_id: str) -> Optional[Dict[str, Any]]:
        """获取特定工作流信息"""
        try:
            if not self.token:
                return None
                
            url = f"{self.base_url}/repos/{repo}/actions/workflows/{workflow_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            self.logger.error(f"获取工作流信息失败: {str(e)}")
            return None
            
    def trigger_workflow(self, repo: str, workflow_id: str, ref: str = "main", 
                        inputs: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """触发工作流"""
        try:
            if not self.token:
                return None
                
            url = f"{self.base_url}/repos/{repo}/actions/workflows/{workflow_id}/dispatches"
            
            data = {
                "ref": ref
            }
            
            if inputs:
                data["inputs"] = inputs
                
            response = self.session.post(url, json=data)
            
            if response.status_code == 204:
                # 成功触发，返回基本信息
                return {
                    "success": True,
                    "repo": repo,
                    "workflow_id": workflow_id,
                    "ref": ref,
                    "triggered_at": datetime.now().isoformat()
                }
            else:
                self.logger.error(f"触发工作流失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"触发工作流失败: {str(e)}")
            return None
            
    def list_workflow_runs(self, repo: str, workflow_id: str = None, 
                          per_page: int = 30) -> List[Dict[str, Any]]:
        """列出工作流运行记录"""
        try:
            if not self.token:
                return []
                
            if workflow_id:
                url = f"{self.base_url}/repos/{repo}/actions/workflows/{workflow_id}/runs"
            else:
                url = f"{self.base_url}/repos/{repo}/actions/runs"
                
            params = {
                "per_page": per_page
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('workflow_runs', [])
            else:
                self.logger.error(f"获取工作流运行记录失败: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            self.logger.error(f"获取工作流运行记录失败: {str(e)}")
            return []
            
    def get_workflow_run(self, repo: str, run_id: str) -> Optional[Dict[str, Any]]:
        """获取特定工作流运行信息"""
        try:
            if not self.token:
                return None
                
            url = f"{self.base_url}/repos/{repo}/actions/runs/{run_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            self.logger.error(f"获取工作流运行信息失败: {str(e)}")
            return None
            
    def cancel_workflow_run(self, repo: str, run_id: str) -> bool:
        """取消工作流运行"""
        try:
            if not self.token:
                return False
                
            url = f"{self.base_url}/repos/{repo}/actions/runs/{run_id}/cancel"
            response = self.session.post(url)
            
            return response.status_code == 202
            
        except Exception as e:
            self.logger.error(f"取消工作流运行失败: {str(e)}")
            return False
            
    def get_workflow_run_logs(self, repo: str, run_id: str) -> Optional[str]:
        """获取工作流运行日志"""
        try:
            if not self.token:
                return None
                
            url = f"{self.base_url}/repos/{repo}/actions/runs/{run_id}/logs"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.text
            return None
            
        except Exception as e:
            self.logger.error(f"获取工作流运行日志失败: {str(e)}")
            return None
            
    def list_repositories(self, username: str = None) -> List[Dict[str, Any]]:
        """列出仓库"""
        try:
            if not self.token:
                return []
                
            if username:
                url = f"{self.base_url}/users/{username}/repos"
            else:
                url = f"{self.base_url}/user/repos"
                
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"获取仓库列表失败: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            self.logger.error(f"获取仓库列表失败: {str(e)}")
            return []
            
    def get_repository(self, repo: str) -> Optional[Dict[str, Any]]:
        """获取仓库信息"""
        try:
            if not self.token:
                return None
                
            url = f"{self.base_url}/repos/{repo}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            self.logger.error(f"获取仓库信息失败: {str(e)}")
            return None
            
    def check_rate_limit(self) -> Optional[Dict[str, Any]]:
        """检查API速率限制"""
        try:
            response = self.session.get(f"{self.base_url}/rate_limit")
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            self.logger.error(f"检查速率限制失败: {str(e)}")
            return None 