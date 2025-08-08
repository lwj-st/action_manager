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
import zipfile
import io

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
            
            
    def get_workflow_run_logs(self, repo: str, run_id: str) -> Optional[dict]:
        """
        获取工作流运行日志
        返回格式: { 'job1.txt': '内容...', 'job2.txt': '内容...' }
        """
        try:
            if not self.token:
                return None

            url = f"{self.base_url}/repos/{repo}/actions/runs/{run_id}/logs"
            response = self.session.get(url)

            if response.status_code == 200:
                logs = {}
                try:
                    zip_bytes = io.BytesIO(response.content)
                    with zipfile.ZipFile(zip_bytes) as zf:
                        for f in zf.namelist():
                            with zf.open(f) as log_file:
                                logs[f] = log_file.read().decode("utf-8", errors="ignore")
                    return logs
                except Exception as e:
                    self.logger.error(f"解压日志失败: {str(e)}")
                    return None
            else:
                self.logger.error(f"获取日志失败: {response.status_code} - {response.text}")
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

    def get_latest_workflow_run(self, repo: str, workflow_file: str) -> Optional[Dict[str, Any]]:
        """获取最新触发的workflow运行信息"""
        try:
            if not self.token:
                return None
                
            # 获取workflow runs，按创建时间倒序排列
            url = f"{self.base_url}/repos/{repo}/actions/workflows/{workflow_file}/runs"
            params = {
                "per_page": 1,  # 只获取最新的一个
                "sort": "created_at",  # 按创建时间排序
                "direction": "desc"  # 倒序，最新的在前
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                runs = data.get('workflow_runs', [])
                if runs:
                    return runs[0]
            return None
            
        except Exception as e:
            self.logger.error(f"获取最新workflow运行信息失败: {str(e)}")
            return None
    
    def get_workflow_run_after_trigger(self, repo: str, workflow_file: str, 
                                      trigger_time: datetime) -> Optional[Dict[str, Any]]:
        """获取触发后的workflow运行信息"""
        try:
            if not self.token:
                return None
                
            # 获取workflow runs
            url = f"{self.base_url}/repos/{repo}/actions/workflows/{workflow_file}/runs"
            params = {
                "per_page": 10  # 获取最近10个运行
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                runs = data.get('workflow_runs', [])
                
                # 确保trigger_time是UTC时间
                if trigger_time.tzinfo is None:
                    # 如果没有时区信息，假设为本地时间，转换为UTC
                    import pytz
                    local_tz = pytz.timezone('Asia/Shanghai')
                    trigger_time = local_tz.localize(trigger_time).astimezone(pytz.UTC)
                else:
                    # 如果有时区信息，转换为UTC
                    trigger_time = trigger_time.astimezone(pytz.UTC)
                
                self.logger.info(f"触发时间(UTC): {trigger_time}")
                
                # 查找触发时间之后的运行
                for run in runs:
                    try:
                        # 解析GitHub时间格式（GitHub返回的是UTC时间）
                        run_created_at_str = run['created_at']
                        if run_created_at_str.endswith('Z'):
                            run_created_at_str = run_created_at_str[:-1] + '+00:00'
                        
                        run_created_at = datetime.fromisoformat(run_created_at_str)
                        # GitHub时间已经是UTC，确保时区信息正确
                        if run_created_at.tzinfo is None:
                            import pytz
                            run_created_at = pytz.UTC.localize(run_created_at)
                        
                        self.logger.info(f"运行时间(UTC): {run_created_at}, 运行ID: {run['id']}")
                        
                        if run_created_at > trigger_time:
                            self.logger.info(f"找到匹配的运行: {run['id']}")
                            return run
                    except Exception as e:
                        self.logger.warning(f"解析运行时间失败: {e}")
                        continue
                        
                self.logger.warning("未找到触发时间之后的运行")
            return None
            
        except Exception as e:
            self.logger.error(f"获取触发后的workflow运行信息失败: {str(e)}")
            return None
    
    def open_url_in_browser(self, url: str) -> bool:
        """在浏览器中打开URL"""
        try:
            import webbrowser
            webbrowser.open(url)
            return True
        except Exception as e:
            self.logger.error(f"在浏览器中打开URL失败: {str(e)}")
            return False 