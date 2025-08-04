#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
"""

import json
import os
import logging
from typing import Dict, Any, Optional

class Config:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.logger = logging.getLogger(__name__)
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.logger.info("配置文件加载成功")
                    return config
            else:
                # 创建默认配置
                default_config = self.get_default_config()
                self.save_config(default_config)
                self.logger.info("创建默认配置文件")
                return default_config
                
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {str(e)}")
            return self.get_default_config()
            
    def save_config(self, config: Dict[str, Any] = None) -> bool:
        """保存配置文件"""
        try:
            if config is None:
                config = self.config
                
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
            self.config = config
            self.logger.info("配置文件保存成功")
            return True
            
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {str(e)}")
            return False
            
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "database": {
                "path": "github_action_manager.db",
                "backup_enabled": True,
                "backup_interval": 24  # 小时
            },
            "github": {
                "api_base_url": "https://api.github.com",
                "timeout": 30,
                "retry_count": 3,
                "rate_limit_check": True
            },
            "ui": {
                "theme": "default",
                "language": "zh_CN",
                "window_size": {
                    "width": 1200,
                    "height": 800
                },
                "auto_refresh": True,
                "refresh_interval": 30  # 秒
            },
            "logging": {
                "level": "INFO",
                "file_enabled": True,
                "file_path": "github_action_manager.log",
                "max_file_size": 10,  # MB
                "backup_count": 5
            },
            "security": {
                "token_encryption": False,
                "session_timeout": 3600,  # 秒
                "max_login_attempts": 5
            },
            "workflow": {
                "default_branch": "main",
                "auto_save_config": True,
                "max_configs_per_user": 50
            }
        }
        
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
                    
            return value
            
        except Exception as e:
            self.logger.error(f"获取配置值失败: {str(e)}")
            return default
            
    def set(self, key: str, value: Any) -> bool:
        """设置配置值"""
        try:
            keys = key.split('.')
            config = self.config
            
            # 导航到父级
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
                
            # 设置值
            config[keys[-1]] = value
            
            # 保存配置
            return self.save_config()
            
        except Exception as e:
            self.logger.error(f"设置配置值失败: {str(e)}")
            return False
            
    def get_database_path(self) -> str:
        """获取数据库路径"""
        return self.get("database.path", "github_action_manager.db")
        
    def is_backup_enabled(self) -> bool:
        """是否启用备份"""
        return self.get("database.backup_enabled", True)
        
    def get_backup_interval(self) -> int:
        """获取备份间隔（小时）"""
        return self.get("database.backup_interval", 24)
        
    def get_github_api_url(self) -> str:
        """获取GitHub API URL"""
        return self.get("github.api_base_url", "https://api.github.com")
        
    def get_github_timeout(self) -> int:
        """获取GitHub请求超时时间"""
        return self.get("github.timeout", 30)
        
    def get_github_retry_count(self) -> int:
        """获取GitHub重试次数"""
        return self.get("github.retry_count", 3)
        
    def is_rate_limit_check_enabled(self) -> bool:
        """是否启用速率限制检查"""
        return self.get("github.rate_limit_check", True)
        
    def get_ui_theme(self) -> str:
        """获取UI主题"""
        return self.get("ui.theme", "default")
        
    def get_ui_language(self) -> str:
        """获取UI语言"""
        return self.get("ui.language", "zh_CN")
        
    def get_window_size(self) -> Dict[str, int]:
        """获取窗口大小"""
        return self.get("ui.window_size", {"width": 1200, "height": 800})
        
    def is_auto_refresh_enabled(self) -> bool:
        """是否启用自动刷新"""
        return self.get("ui.auto_refresh", True)
        
    def get_refresh_interval(self) -> int:
        """获取刷新间隔（秒）"""
        return self.get("ui.refresh_interval", 30)
        
    def get_log_level(self) -> str:
        """获取日志级别"""
        return self.get("logging.level", "INFO")
        
    def is_file_logging_enabled(self) -> bool:
        """是否启用文件日志"""
        return self.get("logging.file_enabled", True)
        
    def get_log_file_path(self) -> str:
        """获取日志文件路径"""
        return self.get("logging.file_path", "github_action_manager.log")
        
    def get_max_log_file_size(self) -> int:
        """获取最大日志文件大小（MB）"""
        return self.get("logging.max_file_size", 10)
        
    def get_log_backup_count(self) -> int:
        """获取日志备份数量"""
        return self.get("logging.backup_count", 5)
        
    def is_token_encryption_enabled(self) -> bool:
        """是否启用Token加密"""
        return self.get("security.token_encryption", False)
        
    def get_session_timeout(self) -> int:
        """获取会话超时时间（秒）"""
        return self.get("security.session_timeout", 3600)
        
    def get_max_login_attempts(self) -> int:
        """获取最大登录尝试次数"""
        return self.get("security.max_login_attempts", 5)
        
    def get_default_branch(self) -> str:
        """获取默认分支"""
        return self.get("workflow.default_branch", "main")
        
    def is_auto_save_config_enabled(self) -> bool:
        """是否启用自动保存配置"""
        return self.get("workflow.auto_save_config", True)
        
    def get_max_configs_per_user(self) -> int:
        """获取每个用户最大配置数量"""
        return self.get("workflow.max_configs_per_user", 50)
        
    def reset_to_default(self) -> bool:
        """重置为默认配置"""
        try:
            default_config = self.get_default_config()
            return self.save_config(default_config)
        except Exception as e:
            self.logger.error(f"重置配置失败: {str(e)}")
            return False
            
    def export_config(self, file_path: str) -> bool:
        """导出配置"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"配置导出成功: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"导出配置失败: {str(e)}")
            return False
            
    def import_config(self, file_path: str) -> bool:
        """导入配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # 验证配置格式
            if not self.validate_config(config):
                self.logger.error("配置格式无效")
                return False
                
            return self.save_config(config)
            
        except Exception as e:
            self.logger.error(f"导入配置失败: {str(e)}")
            return False
            
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置格式"""
        try:
            required_sections = ["database", "github", "ui", "logging", "security", "workflow"]
            
            for section in required_sections:
                if section not in config:
                    return False
                    
            return True
            
        except Exception:
            return False 