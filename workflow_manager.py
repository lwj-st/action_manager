#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流管理模块
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from github_manager import GitHubManager
from database import DatabaseManager

class WorkflowManager:
    """工作流管理器"""
    
    def __init__(self, db_manager: DatabaseManager = None):
        self.github_manager = GitHubManager()
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
    def set_database_manager(self, db_manager: DatabaseManager):
        """设置数据库管理器"""
        self.db_manager = db_manager
        
    def set_github_token(self, token: str):
        """设置GitHub Token"""
        self.github_manager.set_token(token)
        
    def save_config(self, repo: str, workflow: str, branch: str = "main", 
                   inputs: Dict[str, Any] = None) -> Optional[int]:
        """保存工作流配置"""
        try:
            if not self.db_manager:
                self.logger.error("数据库管理器未设置")
                return None
                
            # 生成配置名称
            name = f"{repo}/{workflow}"
            
            # 序列化输入参数
            inputs_json = json.dumps(inputs) if inputs else None
            
            # 保存到数据库
            config_id = self.db_manager.insert_workflow_config(
                name, repo, workflow, branch, inputs_json
            )
            
            if config_id:
                self.logger.info(f"工作流配置保存成功: {config_id}")
                return config_id
            else:
                self.logger.error("工作流配置保存失败")
                return None
                
        except Exception as e:
            self.logger.error(f"保存工作流配置失败: {str(e)}")
            return None
            
    def save_config_with_name(self, name: str, repo: str, workflow: str, branch: str = "main", 
                             inputs: Dict[str, Any] = None, user_id: int = None) -> Optional[int]:
        """保存工作流配置（自定义名称）"""
        try:
            if not self.db_manager:
                self.logger.error("数据库管理器未设置")
                return None
                
            if user_id is None:
                self.logger.error("用户ID不能为空")
                return None
                
            # 序列化输入参数
            inputs_json = json.dumps(inputs) if inputs else None
            
            # 保存到数据库
            config_id = self.db_manager.insert_workflow_config(
                user_id, name, repo, workflow, branch, inputs_json
            )
            
            if config_id:
                self.logger.info(f"工作流配置保存成功: {name} (ID: {config_id})")
                return config_id
            else:
                self.logger.error("工作流配置保存失败")
                return None
                
        except Exception as e:
            self.logger.error(f"保存工作流配置失败: {str(e)}")
            return None
            
    def get_config(self, config_id: int) -> Optional[Dict[str, Any]]:
        """获取工作流配置"""
        try:
            if not self.db_manager:
                return None
                
            config = self.db_manager.get_workflow_config_by_id(config_id)
            
            if config and config.get('inputs'):
                try:
                    config['inputs'] = json.loads(config['inputs'])
                except json.JSONDecodeError:
                    config['inputs'] = {}
                    
            return config
            
        except Exception as e:
            self.logger.error(f"获取工作流配置失败: {str(e)}")
            return None
            
    def get_all_configs(self) -> List[Dict[str, Any]]:
        """获取所有工作流配置"""
        try:
            if not self.db_manager:
                return []
                
            configs = self.db_manager.get_all_workflow_configs()
            
            # 解析输入参数
            for config in configs:
                if config.get('inputs'):
                    try:
                        config['inputs'] = json.loads(config['inputs'])
                    except json.JSONDecodeError:
                        config['inputs'] = {}
                        
            return configs
            
        except Exception as e:
            self.logger.error(f"获取所有工作流配置失败: {str(e)}")
            return []
            
    def update_config(self, config_id: int, repo: str, workflow: str, 
                     branch: str = "main", inputs: Dict[str, Any] = None) -> bool:
        """更新工作流配置"""
        try:
            if not self.db_manager:
                return False
                
            # 生成配置名称
            name = f"{repo}/{workflow}"
            
            # 序列化输入参数
            inputs_json = json.dumps(inputs) if inputs else None
            
            # 更新数据库
            success = self.db_manager.update_workflow_config(
                config_id, name, repo, workflow, branch, inputs_json
            )
            
            if success:
                self.logger.info(f"工作流配置更新成功: {config_id}")
            else:
                self.logger.error(f"工作流配置更新失败: {config_id}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"更新工作流配置失败: {str(e)}")
            return False
            
    def delete_config(self, config_id: int) -> bool:
        """删除工作流配置"""
        try:
            if not self.db_manager:
                return False
                
            success = self.db_manager.delete_workflow_config(config_id)
            
            if success:
                self.logger.info(f"工作流配置删除成功: {config_id}")
            else:
                self.logger.error(f"工作流配置删除失败: {config_id}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"删除工作流配置失败: {str(e)}")
            return False
            
    def trigger_workflow(self, repo: str, workflow: str, branch: str = "main", 
                        inputs: Dict[str, Any] = None) -> bool:
        """触发工作流"""
        try:
            # 检查GitHub连接
            if not self.github_manager.test_connection():
                self.logger.error("GitHub连接失败")
                return False
                
            # 触发工作流
            result = self.github_manager.trigger_workflow(repo, workflow, branch, inputs)
            
            if result:
                self.logger.info(f"工作流触发成功: {repo}/{workflow}")
                
                # 记录运行信息
                if self.db_manager:
                    # 查找对应的配置ID
                    configs = self.get_all_configs()
                    config_id = None
                    for config in configs:
                        if config['repo'] == repo and config['workflow'] == workflow:
                            config_id = config['id']
                            break
                            
                    if config_id:
                        self.db_manager.insert_workflow_run(
                            config_id, 
                            f"triggered_{datetime.now().strftime('%Y%m%d_%H%M%S')}", 
                            "triggered"
                        )
                        
                return True
            else:
                self.logger.error(f"工作流触发失败: {repo}/{workflow}")
                return False
                
        except Exception as e:
            self.logger.error(f"触发工作流失败: {str(e)}")
            return False
            
    def trigger_config_workflow(self, config_id: int) -> bool:
        """触发配置的工作流"""
        try:
            config = self.get_config(config_id)
            if not config:
                self.logger.error(f"工作流配置不存在: {config_id}")
                return False
                
            return self.trigger_workflow(
                config['repo'],
                config['workflow'],
                config['branch'],
                config.get('inputs', {})
            )
            
        except Exception as e:
            self.logger.error(f"触发配置工作流失败: {str(e)}")
            return False
            
    def list_workflows(self, repo: str) -> List[Dict[str, Any]]:
        """列出仓库的工作流"""
        try:
            return self.github_manager.list_workflows(repo)
        except Exception as e:
            self.logger.error(f"列出工作流失败: {str(e)}")
            return []
            
    def get_workflow_runs(self, repo: str, workflow_id: str = None) -> List[Dict[str, Any]]:
        """获取工作流运行记录"""
        try:
            return self.github_manager.list_workflow_runs(repo, workflow_id)
        except Exception as e:
            self.logger.error(f"获取工作流运行记录失败: {str(e)}")
            return []
            
    def cancel_workflow_run(self, repo: str, run_id: str) -> bool:
        """取消工作流运行"""
        try:
            success = self.github_manager.cancel_workflow_run(repo, run_id)
            
            if success:
                self.logger.info(f"工作流运行取消成功: {run_id}")
            else:
                self.logger.error(f"工作流运行取消失败: {run_id}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"取消工作流运行失败: {str(e)}")
            return False
            
    def get_workflow_run_logs(self, repo: str, run_id: str) -> Optional[str]:
        """获取工作流运行日志"""
        try:
            return self.github_manager.get_workflow_run_logs(repo, run_id)
        except Exception as e:
            self.logger.error(f"获取工作流运行日志失败: {str(e)}")
            return None
            
    def validate_workflow_config(self, repo: str, workflow: str) -> bool:
        """验证工作流配置"""
        try:
            workflows = self.list_workflows(repo)
            
            for wf in workflows:
                if wf['name'] == workflow or str(wf['id']) == workflow:
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"验证工作流配置失败: {str(e)}")
            return False
            
    def get_workflow_status(self, repo: str, run_id: str) -> Optional[str]:
        """获取工作流运行状态"""
        try:
            run_info = self.github_manager.get_workflow_run(repo, run_id)
            if run_info:
                return run_info.get('status')
            return None
            
        except Exception as e:
            self.logger.error(f"获取工作流状态失败: {str(e)}")
            return None
            
    def search_workflows(self, repo: str, keyword: str) -> List[Dict[str, Any]]:
        """搜索工作流"""
        try:
            workflows = self.list_workflows(repo)
            
            if not keyword:
                return workflows
                
            filtered_workflows = []
            keyword_lower = keyword.lower()
            
            for workflow in workflows:
                if (keyword_lower in workflow['name'].lower() or 
                    keyword_lower in workflow.get('path', '').lower()):
                    filtered_workflows.append(workflow)
                    
            return filtered_workflows
            
        except Exception as e:
            self.logger.error(f"搜索工作流失败: {str(e)}")
            return [] 