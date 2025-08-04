#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库管理模块 - 修复版本
添加了用户与工作流的关联
"""

import sqlite3
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "github_action_manager.db"):
        self.db_path = db_path
        self.connection = None
        self.logger = logging.getLogger(__name__)
        
    def init_database(self):
        """初始化数据库"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            
            # 创建表
            self._create_tables()
            
            self.logger.info("数据库初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"数据库初始化失败: {str(e)}")
            return False
            
    def _create_tables(self):
        """创建数据库表"""
        cursor = self.connection.cursor()
        
        # 用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                token TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 工作流配置表 - 添加用户ID关联
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                repo TEXT NOT NULL,
                workflow TEXT NOT NULL,
                branch TEXT DEFAULT 'main',
                inputs TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
        
        # 工作流运行记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_id INTEGER,
                run_id TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (config_id) REFERENCES workflow_configs (id) ON DELETE CASCADE
            )
        """)
        
        # 系统日志表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 检查是否需要升级现有数据库
        self._upgrade_database()
        
        self.connection.commit()
        
    def _upgrade_database(self):
        """升级现有数据库结构"""
        try:
            cursor = self.connection.cursor()
            
            # 检查workflow_configs表是否有user_id列
            cursor.execute("PRAGMA table_info(workflow_configs)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'user_id' not in columns:
                self.logger.info("升级数据库：添加user_id列到workflow_configs表")
                
                # 添加user_id列
                cursor.execute("ALTER TABLE workflow_configs ADD COLUMN user_id INTEGER DEFAULT 1")
                
                # 为现有记录设置默认用户ID
                cursor.execute("UPDATE workflow_configs SET user_id = 1 WHERE user_id IS NULL")
                
                # 添加外键约束
                cursor.execute("""
                    CREATE TABLE workflow_configs_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        repo TEXT NOT NULL,
                        workflow TEXT NOT NULL,
                        branch TEXT DEFAULT 'main',
                        inputs TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """)
                
                cursor.execute("""
                    INSERT INTO workflow_configs_new 
                    SELECT id, user_id, name, repo, workflow, branch, inputs, created_at, updated_at 
                    FROM workflow_configs
                """)
                
                cursor.execute("DROP TABLE workflow_configs")
                cursor.execute("ALTER TABLE workflow_configs_new RENAME TO workflow_configs")
                
                self.logger.info("数据库升级完成")
                
        except Exception as e:
            self.logger.error(f"数据库升级失败: {str(e)}")
            
    def is_connected(self) -> bool:
        """检查数据库连接状态"""
        try:
            if self.connection:
                self.connection.execute("SELECT 1")
                return True
            return False
        except:
            return False
            
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """执行查询"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            self.logger.error(f"查询执行失败: {str(e)}")
            return []
            
    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """执行更新操作"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            self.logger.error(f"更新执行失败: {str(e)}")
            return False
            
    def insert_user(self, username: str, token: str) -> Optional[int]:
        """插入用户"""
        try:
            query = """
                INSERT INTO users (username, token, created_at, updated_at)
                VALUES (?, ?, ?, ?)
            """
            now = datetime.now().isoformat()
            
            cursor = self.connection.cursor()
            cursor.execute(query, (username, token, now, now))
            self.connection.commit()
            
            user_id = cursor.lastrowid
            self.logger.info(f"用户插入成功: {username} (ID: {user_id})")
            return user_id
            
        except sqlite3.IntegrityError:
            self.logger.error(f"用户名已存在: {username}")
            return None
        except Exception as e:
            self.logger.error(f"插入用户失败: {str(e)}")
            return None
        
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户"""
        query = "SELECT * FROM users WHERE id = ?"
        results = self.execute_query(query, (user_id,))
        return results[0] if results else None
        
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名获取用户"""
        query = "SELECT * FROM users WHERE username = ?"
        results = self.execute_query(query, (username,))
        return results[0] if results else None
        
    def get_all_users(self) -> List[Dict[str, Any]]:
        """获取所有用户"""
        query = "SELECT * FROM users ORDER BY created_at DESC"
        return self.execute_query(query)
        
    def update_user(self, user_id: int, username: str, token: str) -> bool:
        """更新用户"""
        try:
            query = """
                UPDATE users 
                SET username = ?, token = ?, updated_at = ?
                WHERE id = ?
            """
            now = datetime.now().isoformat()
            
            cursor = self.connection.cursor()
            cursor.execute(query, (username, token, now, user_id))
            self.connection.commit()
            
            if cursor.rowcount > 0:
                self.logger.info(f"用户更新成功: {username}")
                return True
            else:
                self.logger.error(f"用户不存在: {user_id}")
                return False
                
        except sqlite3.IntegrityError:
            self.logger.error(f"用户名已存在: {username}")
            return False
        except Exception as e:
            self.logger.error(f"更新用户失败: {str(e)}")
            return False
        
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        query = "DELETE FROM users WHERE id = ?"
        return self.execute_update(query, (user_id,))
        
    def insert_workflow_config(self, user_id: int, name: str, repo: str, workflow: str, 
                             branch: str = "main", inputs: str = None) -> Optional[int]:
        """插入工作流配置"""
        try:
            query = """
                INSERT INTO workflow_configs (user_id, name, repo, workflow, branch, inputs, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            now = datetime.now().isoformat()
            
            cursor = self.connection.cursor()
            cursor.execute(query, (user_id, name, repo, workflow, branch, inputs, now, now))
            self.connection.commit()
            
            config_id = cursor.lastrowid
            self.logger.info(f"工作流配置插入成功: {name} (ID: {config_id})")
            return config_id
            
        except Exception as e:
            self.logger.error(f"插入工作流配置失败: {str(e)}")
            return None
        
    def get_workflow_config_by_id(self, config_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取工作流配置"""
        query = """
            SELECT wc.*, u.username as user_name 
            FROM workflow_configs wc 
            LEFT JOIN users u ON wc.user_id = u.id 
            WHERE wc.id = ?
        """
        results = self.execute_query(query, (config_id,))
        return results[0] if results else None
        
    def get_all_workflow_configs(self) -> List[Dict[str, Any]]:
        """获取所有工作流配置"""
        query = """
            SELECT wc.*, u.username as user_name 
            FROM workflow_configs wc 
            LEFT JOIN users u ON wc.user_id = u.id 
            ORDER BY wc.created_at DESC
        """
        return self.execute_query(query)
        
    def get_workflow_configs_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """获取指定用户的工作流配置"""
        query = """
            SELECT wc.*, u.username as user_name 
            FROM workflow_configs wc 
            LEFT JOIN users u ON wc.user_id = u.id 
            WHERE wc.user_id = ?
            ORDER BY wc.created_at DESC
        """
        return self.execute_query(query, (user_id,))
        
    def update_workflow_config(self, config_id: int, user_id: int, name: str, repo: str, 
                             workflow: str, branch: str = "main", inputs: str = None) -> bool:
        """更新工作流配置"""
        try:
            query = """
                UPDATE workflow_configs 
                SET user_id = ?, name = ?, repo = ?, workflow = ?, branch = ?, inputs = ?, updated_at = ?
                WHERE id = ?
            """
            now = datetime.now().isoformat()
            
            cursor = self.connection.cursor()
            cursor.execute(query, (user_id, name, repo, workflow, branch, inputs, now, config_id))
            self.connection.commit()
            
            if cursor.rowcount > 0:
                self.logger.info(f"工作流配置更新成功: {config_id}")
                return True
            else:
                self.logger.error(f"工作流配置不存在: {config_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"更新工作流配置失败: {str(e)}")
            return False
        
    def delete_workflow_config(self, config_id: int) -> bool:
        """删除工作流配置"""
        query = "DELETE FROM workflow_configs WHERE id = ?"
        return self.execute_update(query, (config_id,))
        
    def insert_workflow_run(self, config_id: int, run_id: str, status: str) -> Optional[int]:
        """插入工作流运行记录"""
        try:
            query = """
                INSERT INTO workflow_runs (config_id, run_id, status, created_at)
                VALUES (?, ?, ?, ?)
            """
            now = datetime.now().isoformat()
            
            cursor = self.connection.cursor()
            cursor.execute(query, (config_id, run_id, status, now))
            self.connection.commit()
            
            run_id_db = cursor.lastrowid
            self.logger.info(f"工作流运行记录插入成功: {run_id} (ID: {run_id_db})")
            return run_id_db
            
        except Exception as e:
            self.logger.error(f"插入工作流运行记录失败: {str(e)}")
            return None
        
    def update_workflow_run_status(self, run_id: str, status: str) -> bool:
        """更新工作流运行状态"""
        query = """
            UPDATE workflow_runs 
            SET status = ?, completed_at = ?
            WHERE run_id = ?
        """
        now = datetime.now().isoformat()
        return self.execute_update(query, (status, now, run_id))
        
    def get_workflow_runs(self, config_id: int = None) -> List[Dict[str, Any]]:
        """获取工作流运行记录"""
        if config_id:
            query = """
                SELECT wr.*, wc.name as config_name, wc.repo, u.username as user_name
                FROM workflow_runs wr
                JOIN workflow_configs wc ON wr.config_id = wc.id
                LEFT JOIN users u ON wc.user_id = u.id
                WHERE wr.config_id = ?
                ORDER BY wr.created_at DESC
            """
            return self.execute_query(query, (config_id,))
        else:
            query = """
                SELECT wr.*, wc.name as config_name, wc.repo, u.username as user_name
                FROM workflow_runs wr
                JOIN workflow_configs wc ON wr.config_id = wc.id
                LEFT JOIN users u ON wc.user_id = u.id
                ORDER BY wr.created_at DESC
            """
            return self.execute_query(query)
            
    def insert_system_log(self, level: str, message: str) -> bool:
        """插入系统日志"""
        query = """
            INSERT INTO system_logs (level, message, created_at)
            VALUES (?, ?, ?)
        """
        now = datetime.now().isoformat()
        return self.execute_update(query, (level, message, now))
        
    def get_system_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取系统日志"""
        query = """
            SELECT * FROM system_logs 
            ORDER BY created_at DESC 
            LIMIT ?
        """
        return self.execute_query(query, (limit,))
        
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None 