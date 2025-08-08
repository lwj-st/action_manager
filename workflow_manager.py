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
                        inputs: Dict[str, Any] = None, config_id: int = None) -> Optional[Dict[str, Any]]:
        """触发工作流"""
        try:
            # 检查GitHub连接
            if not self.github_manager.test_connection():
                self.logger.error("GitHub连接失败")
                return None
                
            # 记录触发时间（使用UTC时间）
            import pytz
            trigger_time = datetime.now(pytz.UTC)
                
            # 触发工作流
            result = self.github_manager.trigger_workflow(repo, workflow, branch, inputs)
            
            if result:
                self.logger.info(f"工作流触发成功: {repo}/{workflow}")
                
                # 立即返回成功，后台获取运行信息
                return {
                    'success': True,
                    'repo': repo,
                    'workflow': workflow,
                    'triggered_at': trigger_time.isoformat(),
                    'note': '触发成功，运行信息将在后台获取'
                }
            else:
                self.logger.error(f"工作流触发失败: {repo}/{workflow}")
                return None
                
        except Exception as e:
            self.logger.error(f"触发工作流失败: {str(e)}")
            return None
            
    def get_triggered_run_info(self, repo: str, workflow: str, trigger_time: datetime, config_id: int = None):
        """后台获取刚触发的运行信息"""
        try:
            import time
            # 等待5秒让GitHub处理
            time.sleep(5)
            
            # 直接获取最新的运行（应该是刚触发的）
            run_info = self.github_manager.get_latest_workflow_run(repo, workflow)
            
            if run_info:
                # 创建独立的数据库连接
                from database import DatabaseManager
                temp_db = DatabaseManager()
                temp_db.init_database()
                
                try:
                    # 存储运行信息到数据库
                    if config_id:
                        temp_db.insert_workflow_run(
                            config_id=config_id,
                            run_id=str(run_info['id']),
                            status=run_info.get('status', 'unknown'),
                            html_url=run_info.get('html_url'),
                            conclusion=run_info.get('conclusion'),
                            logs_url=run_info.get('logs_url'),
                            workflow_name=run_info.get('name'),
                            repo=repo,
                            branch=run_info.get('head_branch', 'main'),
                            trigger_user=run_info.get('actor', {}).get('login')
                        )
                        self.logger.info(f"运行信息已存储到数据库: {run_info['id']}")
                    else:
                        # 如果没有config_id，也存储到数据库
                        temp_db.insert_workflow_run(
                            config_id=None,
                            run_id=str(run_info['id']),
                            status=run_info.get('status', 'unknown'),
                            html_url=run_info.get('html_url'),
                            conclusion=run_info.get('conclusion'),
                            logs_url=run_info.get('logs_url'),
                            workflow_name=run_info.get('name'),
                            repo=repo,
                            branch=run_info.get('head_branch', 'main'),
                            trigger_user=run_info.get('actor', {}).get('login')
                        )
                        self.logger.info(f"运行信息已存储到数据库: {run_info['id']}")
                finally:
                    temp_db.close()
                    
        except Exception as e:
            self.logger.error(f"后台获取运行信息失败: {str(e)}")
            
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
            
    def get_workflow_runs_from_db(self, config_id: int = None) -> List[Dict[str, Any]]:
        """从数据库获取工作流运行记录"""
        try:
            if not self.db_manager:
                return []
                
            return self.db_manager.get_workflow_runs(config_id)
            
        except Exception as e:
            self.logger.error(f"从数据库获取工作流运行记录失败: {str(e)}")
            return []
    
    def refresh_workflow_run_status(self, run_id: str) -> Optional[Dict[str, Any]]:
        """刷新工作流运行状态"""
        try:
            # 从数据库获取运行记录
            run_record = self.db_manager.get_workflow_run_by_run_id(run_id)
            if not run_record:
                return None
                
            # 从GitHub获取最新状态
            run_info = self.github_manager.get_workflow_run(run_record['repo'], run_id)
            if run_info:
                # 更新数据库
                self.db_manager.update_workflow_run_status(
                    run_id, 
                    run_info.get('status', 'unknown'),
                    run_info.get('conclusion')
                )
                
                return {
                    'run_id': run_id,
                    'status': run_info.get('status'),
                    'conclusion': run_info.get('conclusion'),
                    'html_url': run_info.get('html_url'),
                    'created_at': run_info.get('created_at'),
                    'updated_at': run_info.get('updated_at')
                }
            return None
            
        except Exception as e:
            self.logger.error(f"刷新工作流运行状态失败: {str(e)}")
            return None
    
    def cancel_workflow_run(self, run_id: str) -> bool:
        """取消工作流运行"""
        try:
            # 检查是否是临时run_id
            if run_id.startswith('triggered_'):
                self.logger.warning(f"无法取消临时运行ID: {run_id}")
                return False
                
            # 从数据库获取运行记录
            run_record = self.db_manager.get_workflow_run_by_run_id(run_id)
            if not run_record:
                self.logger.error(f"工作流运行记录不存在: {run_id}")
                return False
                
            # 取消运行
            success = self.github_manager.cancel_workflow_run(run_record['repo'], run_id)
            
            if success:
                # 更新数据库状态
                self.db_manager.update_workflow_run_status(run_id, 'cancelled', 'cancelled')
                self.logger.info(f"工作流运行取消成功: {run_id}")
            else:
                self.logger.error(f"工作流运行取消失败: {run_id}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"取消工作流运行失败: {str(e)}")
            return False
    
    def get_workflow_run_logs(self, run_id: str) -> Optional[dict]:
        """获取工作流运行日志"""
        try:
            # 检查是否是临时run_id
            if run_id.startswith('triggered_'):
                self.logger.warning(f"无法获取临时运行ID的日志: {run_id}")
                return {"error.txt": "无法获取临时运行ID的日志，请等待运行信息同步或手动刷新。"}
                
            # 从数据库获取运行记录
            run_record = self.db_manager.get_workflow_run_by_run_id(run_id)
            if not run_record:
                self.logger.error(f"工作流运行记录不存在: {run_id}")
                return None
                
            # 获取日志
            logs = self.github_manager.get_workflow_run_logs(run_record['repo'], run_id)
            
            if logs:
                self.logger.info(f"获取工作流运行日志成功: {run_id}")
            else:
                self.logger.warning(f"工作流运行日志为空: {run_id}")
                
            return logs
            
        except Exception as e:
            self.logger.error(f"获取工作流运行日志失败: {str(e)}")
            return None
    
    def open_workflow_run_in_browser(self, run_id: str) -> bool:
        """在浏览器中打开工作流运行"""
        try:
            import webbrowser
            
            # 从数据库获取运行记录
            run_record = self.db_manager.get_workflow_run_by_run_id(run_id)
            if not run_record or not run_record.get('html_url'):
                self.logger.error(f"工作流运行记录或URL不存在: {run_id}")
                return False
                
            # 打开浏览器
            webbrowser.open(run_record['html_url'])
            self.logger.info(f"在浏览器中打开工作流运行: {run_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"打开工作流运行失败: {str(e)}")
            return False
            
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

    def get_all_runs(self) -> List[Dict[str, Any]]:
        """获取所有工作流运行记录"""
        try:
            if not self.db_manager:
                return []
                
            return self.db_manager.get_workflow_runs()
            
        except Exception as e:
            self.logger.error(f"获取所有工作流运行记录失败: {str(e)}")
            return []
    
    def get_run_by_id(self, run_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取工作流运行记录"""
        try:
            if not self.db_manager:
                return None
                
            return self.db_manager.get_workflow_run_by_run_id(run_id)
            
        except Exception as e:
            self.logger.error(f"根据ID获取工作流运行记录失败: {str(e)}")
            return None
    
    def get_run_logs(self, run_id: str) -> Optional[dict]:
        """获取工作流运行日志（兼容方法）"""
        return self.get_workflow_run_logs(run_id) 