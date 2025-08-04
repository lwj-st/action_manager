#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Action 管理系统 - 完全修复版本
解决了用户管理、工作流关联、错误处理等问题
"""

import sys
import os
import json
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QPushButton, QLabel, 
                             QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem,
                             QComboBox, QMessageBox, QInputDialog, QHeaderView,
                             QGroupBox, QFormLayout, QSplitter, QFrame, QGridLayout,
                             QScrollArea, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor

# 使用修复版本的数据库管理器
from database import DatabaseManager
from github_manager import GitHubManager
from workflow_manager import WorkflowManager
from user_manager import UserManager
from config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('github_action_manager.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class KeyValueInputDialog(QDialog):
    """Key-Value输入对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("输入参数")
        self.setModal(True)
        self.resize(400, 300)
        
        self.params = {}
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 说明
        label = QLabel("请输入工作流参数 (Key-Value格式):")
        layout.addWidget(label)
        
        # 参数输入区域
        self.params_text = QTextEdit()
        self.params_text.setPlaceholderText("key1=value1\nkey2=value2\nkey3=value3")
        layout.addWidget(self.params_text)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_params(self):
        """获取参数"""
        text = self.params_text.toPlainText().strip()
        if not text:
            return {}
            
        params = {}
        for line in text.split('\n'):
            line = line.strip()
            if '=' in line:
                key, value = line.split('=', 1)
                params[key.strip()] = value.strip()
                
        return params

class WorkflowNameDialog(QDialog):
    """工作流名称输入对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("工作流配置名称")
        self.setModal(True)
        self.resize(300, 150)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 说明
        label = QLabel("请为这个工作流配置输入一个名称:")
        layout.addWidget(label)
        
        # 名称输入
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如: 同步数据工作流")
        layout.addWidget(self.name_input)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_name(self):
        return self.name_input.text().strip()

class UserSelectionDialog(QDialog):
    """用户选择对话框"""
    
    def __init__(self, users, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择用户")
        self.setModal(True)
        self.resize(300, 200)
        self.users = users
        self.selected_user_id = None
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 说明
        label = QLabel("请选择要使用的工作流配置所属用户:")
        layout.addWidget(label)
        
        # 用户选择下拉框
        self.user_combo = QComboBox()
        for user in self.users:
            self.user_combo.addItem(f"{user['username']} (ID: {user['id']})", user['id'])
        layout.addWidget(self.user_combo)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_selected_user_id(self):
        if self.user_combo.currentData():
            return self.user_combo.currentData()
        return None

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.db_manager = DatabaseManager()
        self.github_manager = GitHubManager()
        self.workflow_manager = WorkflowManager()
        self.user_manager = UserManager(self.db_manager)
        
        self.current_user_id = None  # 当前选中的用户ID
        
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("GitHub Action 管理系统 v2.1 (修复版)")
        self.setGeometry(100, 100, 1400, 900)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e1e1e1;
                padding: 10px 20px;
                margin-right: 2px;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 3px solid #0078d4;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
            }
            QTableWidget {
                gridline-color: #e1e1e1;
                selection-background-color: #e3f2fd;
                font-size: 11px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                border: 1px solid #e1e1e1;
                padding: 8px;
                font-weight: bold;
                font-size: 11px;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建标题
        title_label = QLabel("GitHub Action 管理系统 v2.1 (修复版)")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        title_label.setStyleSheet("color: #0078d4; margin: 15px;")
        main_layout.addWidget(title_label)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 创建各个标签页
        self.create_dashboard_tab()
        self.create_workflow_tab()
        self.create_user_tab()
        self.create_log_tab()
        
    def create_dashboard_tab(self):
        """创建仪表板标签页"""
        dashboard_widget = QWidget()
        layout = QVBoxLayout(dashboard_widget)
        
        # 状态信息
        status_group = QGroupBox("系统状态")
        status_layout = QFormLayout(status_group)
        
        self.db_status_label = QLabel("未连接")
        self.github_status_label = QLabel("未连接")
        self.user_count_label = QLabel("0")
        self.workflow_count_label = QLabel("0")
        self.current_user_label = QLabel("未选择")
        
        status_layout.addRow("数据库状态:", self.db_status_label)
        status_layout.addRow("GitHub连接:", self.github_status_label)
        status_layout.addRow("用户数量:", self.user_count_label)
        status_layout.addRow("工作流数量:", self.workflow_count_label)
        status_layout.addRow("当前用户:", self.current_user_label)
        
        layout.addWidget(status_group)
        
        # 快速操作
        quick_group = QGroupBox("快速操作")
        quick_layout = QHBoxLayout(quick_group)
        
        refresh_btn = QPushButton("刷新状态")
        refresh_btn.clicked.connect(self.refresh_status)
        
        test_connection_btn = QPushButton("测试连接")
        test_connection_btn.clicked.connect(self.test_connections)
        
        select_user_btn = QPushButton("选择用户")
        select_user_btn.clicked.connect(self.select_current_user)
        
        quick_layout.addWidget(refresh_btn)
        quick_layout.addWidget(test_connection_btn)
        quick_layout.addWidget(select_user_btn)
        quick_layout.addStretch()
        
        layout.addWidget(quick_group)
        layout.addStretch()
        
        self.tab_widget.addTab(dashboard_widget, "仪表板")
        
    def create_workflow_tab(self):
        """创建工作流管理标签页"""
        workflow_widget = QWidget()
        layout = QVBoxLayout(workflow_widget)
        
        # 工作流配置区域
        config_group = QGroupBox("工作流配置")
        config_layout = QFormLayout(config_group)
        
        self.repo_input = QLineEdit()
        self.repo_input.setPlaceholderText("owner/repository")
        
        self.workflow_input = QLineEdit()
        self.workflow_input.setPlaceholderText("workflow文件名或ID")
        
        self.branch_input = QLineEdit()
        self.branch_input.setPlaceholderText("分支名称 (可选)")
        self.branch_input.setText("main")
        
        # 参数输入改为按钮
        self.params_btn = QPushButton("设置参数")
        self.params_btn.clicked.connect(self.open_params_dialog)
        self.current_params = {}
        
        config_layout.addRow("仓库:", self.repo_input)
        config_layout.addRow("工作流:", self.workflow_input)
        config_layout.addRow("分支:", self.branch_input)
        config_layout.addRow("参数:", self.params_btn)
        
        layout.addWidget(config_group)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.trigger_btn = QPushButton("触发工作流")
        self.trigger_btn.clicked.connect(self.trigger_workflow)
        
        self.list_workflows_btn = QPushButton("列出工作流")
        self.list_workflows_btn.clicked.connect(self.list_workflows)
        
        self.save_config_btn = QPushButton("保存配置")
        self.save_config_btn.clicked.connect(self.save_workflow_config)
        
        button_layout.addWidget(self.trigger_btn)
        button_layout.addWidget(self.list_workflows_btn)
        button_layout.addWidget(self.save_config_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # 工作流列表
        list_group = QGroupBox("已保存的工作流配置")
        list_layout = QVBoxLayout(list_group)
        
        self.workflow_table = QTableWidget()
        self.workflow_table.setColumnCount(8)
        self.workflow_table.setHorizontalHeaderLabels([
            "ID", "配置名称", "用户", "仓库", "工作流", "分支", "状态", "操作"
        ])
        
        # 设置列宽
        header = self.workflow_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 配置名称
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 用户
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # 仓库
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # 工作流
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 分支
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # 状态
        header.setSectionResizeMode(7, QHeaderView.Fixed)  # 操作
        self.workflow_table.setColumnWidth(7, 200)
        
        list_layout.addWidget(self.workflow_table)
        
        layout.addWidget(list_group)
        
        self.tab_widget.addTab(workflow_widget, "工作流管理")
        
    def create_user_tab(self):
        """创建用户管理标签页"""
        user_widget = QWidget()
        layout = QVBoxLayout(user_widget)
        
        # 用户配置
        user_config_group = QGroupBox("用户配置")
        user_config_layout = QFormLayout(user_config_group)
        
        self.username_input = QLineEdit()
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.Password)
        
        user_config_layout.addRow("用户名:", self.username_input)
        user_config_layout.addRow("Token:", self.token_input)
        
        layout.addWidget(user_config_group)
        
        # 用户操作按钮
        user_button_layout = QHBoxLayout()
        
        add_user_btn = QPushButton("添加用户")
        add_user_btn.clicked.connect(self.add_user)
        
        test_token_btn = QPushButton("测试Token")
        test_token_btn.clicked.connect(self.test_user_token)
        
        user_button_layout.addWidget(add_user_btn)
        user_button_layout.addWidget(test_token_btn)
        user_button_layout.addStretch()
        
        layout.addLayout(user_button_layout)
        
        # 用户列表
        user_list_group = QGroupBox("用户列表")
        user_list_layout = QVBoxLayout(user_list_group)
        
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(5)
        self.user_table.setHorizontalHeaderLabels([
            "ID", "用户名", "Token状态", "创建时间", "操作"
        ])
        
        # 设置列宽
        header = self.user_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 用户名
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Token状态
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 创建时间
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # 操作
        self.user_table.setColumnWidth(4, 150)
        
        user_list_layout.addWidget(self.user_table)
        
        layout.addWidget(user_list_group)
        
        self.tab_widget.addTab(user_widget, "用户管理")
        
    def create_log_tab(self):
        """创建日志标签页"""
        log_widget = QWidget()
        layout = QVBoxLayout(log_widget)
        
        # 日志显示区域
        log_group = QGroupBox("系统日志")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        
        log_layout.addWidget(self.log_text)
        
        # 日志操作按钮
        log_button_layout = QHBoxLayout()
        
        clear_log_btn = QPushButton("清空日志")
        clear_log_btn.clicked.connect(self.clear_log)
        
        export_log_btn = QPushButton("导出日志")
        export_log_btn.clicked.connect(self.export_log)
        
        log_button_layout.addWidget(clear_log_btn)
        log_button_layout.addWidget(export_log_btn)
        log_button_layout.addStretch()
        
        log_layout.addLayout(log_button_layout)
        
        layout.addWidget(log_group)
        
        self.tab_widget.addTab(log_widget, "系统日志")
        
    def select_current_user(self):
        """选择当前用户"""
        users = self.user_manager.get_all_users()
        if not users:
            QMessageBox.warning(self, "警告", "请先添加用户")
            return
            
        dialog = UserSelectionDialog(users, self)
        if dialog.exec_() == QDialog.Accepted:
            self.current_user_id = dialog.get_selected_user_id()
            if self.current_user_id:
                user = next((u for u in users if u['id'] == self.current_user_id), None)
                if user:
                    self.current_user_label.setText(f"{user['username']} (ID: {self.current_user_id})")
                    self.log_message(f"已选择用户: {user['username']}")
                    self.load_workflow_configs()  # 重新加载工作流配置
        
    def open_params_dialog(self):
        """打开参数输入对话框"""
        dialog = KeyValueInputDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.current_params = dialog.get_params()
            if self.current_params:
                self.params_btn.setText(f"已设置 {len(self.current_params)} 个参数")
                self.params_btn.setStyleSheet("background-color: #28a745;")
            else:
                self.params_btn.setText("设置参数")
                self.params_btn.setStyleSheet("")
        
    def load_data(self):
        """加载数据"""
        try:
            # 初始化数据库
            self.db_manager.init_database()
            
            # 设置工作流管理器的数据库管理器
            self.workflow_manager.set_database_manager(self.db_manager)
            
            # 加载用户列表
            self.load_users()
            
            # 加载工作流配置
            self.load_workflow_configs()
            
            # 更新状态
            self.refresh_status()
            
            self.log_message("系统初始化完成")
            
        except Exception as e:
            self.log_message(f"加载数据失败: {str(e)}", "ERROR")
            
    def refresh_status(self):
        """刷新系统状态"""
        try:
            # 更新数据库状态
            if self.db_manager.is_connected():
                self.db_status_label.setText("已连接")
                self.db_status_label.setStyleSheet("color: green;")
            else:
                self.db_status_label.setText("未连接")
                self.db_status_label.setStyleSheet("color: red;")
                
            # 更新用户数量
            user_count = len(self.user_manager.get_all_users())
            self.user_count_label.setText(str(user_count))
            
            # 更新工作流数量
            workflow_count = len(self.workflow_manager.get_all_configs())
            self.workflow_count_label.setText(str(workflow_count))
            
        except Exception as e:
            self.log_message(f"刷新状态失败: {str(e)}", "ERROR")
            
    def test_connections(self):
        """测试连接"""
        try:
            # 测试数据库连接
            if self.db_manager.is_connected():
                self.log_message("数据库连接正常")
            else:
                self.log_message("数据库连接失败", "ERROR")
                
            # 测试GitHub连接
            users = self.user_manager.get_all_users()
            if not users:
                self.github_status_label.setText("未连接")
                self.github_status_label.setStyleSheet("color: red;")
                self.log_message("GitHub连接失败: 未找到Token", "ERROR")
                return
                
            # 使用第一个用户的Token测试
            user_token = self.user_manager.get_user_token(users[0]['id'])
            if not user_token:
                self.github_status_label.setText("未连接")
                self.github_status_label.setStyleSheet("color: red;")
                self.log_message("GitHub连接失败: Token无效", "ERROR")
                return
                
            self.github_manager.set_token(user_token)
            if self.github_manager.test_connection():
                self.github_status_label.setText("已连接")
                self.github_status_label.setStyleSheet("color: green;")
                self.log_message("GitHub连接正常")
            else:
                self.github_status_label.setText("未连接")
                self.github_status_label.setStyleSheet("color: red;")
                self.log_message("GitHub连接失败", "ERROR")
                
        except Exception as e:
            self.log_message(f"测试连接失败: {str(e)}", "ERROR")
            
    def trigger_workflow(self):
        """触发工作流"""
        try:
            repo = self.repo_input.text().strip()
            workflow = self.workflow_input.text().strip()
            branch = self.branch_input.text().strip()
            
            if not repo or not workflow:
                QMessageBox.warning(self, "警告", "请填写仓库和工作流信息")
                return
                
            # 检查是否有可用的Token
            users = self.user_manager.get_all_users()
            if not users:
                QMessageBox.warning(self, "警告", "请先添加GitHub Token")
                return
                
            # 使用当前用户或第一个用户的Token
            user_id = self.current_user_id if self.current_user_id else users[0]['id']
            user_token = self.user_manager.get_user_token(user_id)
            if not user_token:
                QMessageBox.warning(self, "警告", "无法获取有效的GitHub Token")
                return
                
            # 设置Token
            self.github_manager.set_token(user_token)
            self.workflow_manager.set_github_token(user_token)
                
            # 触发工作流
            result = self.workflow_manager.trigger_workflow(repo, workflow, branch, self.current_params)
            
            if result:
                self.log_message(f"工作流触发成功: {repo}/{workflow}")
                QMessageBox.information(self, "成功", "工作流触发成功")
            else:
                self.log_message(f"工作流触发失败: {repo}/{workflow}", "ERROR")
                QMessageBox.critical(self, "错误", "工作流触发失败")
                
        except Exception as e:
            self.log_message(f"触发工作流失败: {str(e)}", "ERROR")
            QMessageBox.critical(self, "错误", f"触发工作流失败: {str(e)}")
            
    def list_workflows(self):
        """列出工作流"""
        try:
            repo = self.repo_input.text().strip()
            if not repo:
                QMessageBox.warning(self, "警告", "请填写仓库信息")
                return
                
            # 检查是否有可用的Token
            users = self.user_manager.get_all_users()
            if not users:
                QMessageBox.warning(self, "警告", "请先添加GitHub Token")
                return
                
            # 使用当前用户或第一个用户的Token
            user_id = self.current_user_id if self.current_user_id else users[0]['id']
            user_token = self.user_manager.get_user_token(user_id)
            if not user_token:
                QMessageBox.warning(self, "警告", "无法获取有效的GitHub Token")
                return
                
            # 设置Token
            self.github_manager.set_token(user_token)
                
            workflows = self.github_manager.list_workflows(repo)
            self.log_message(f"获取到 {len(workflows)} 个工作流")
            
            # 显示工作流列表
            self.show_workflow_list(workflows)
            
        except Exception as e:
            self.log_message(f"获取工作流列表失败: {str(e)}", "ERROR")
            QMessageBox.critical(self, "错误", f"获取工作流列表失败: {str(e)}")
            
    def show_workflow_list(self, workflows):
        """显示工作流列表"""
        dialog = QMessageBox(self)
        dialog.setWindowTitle("工作流列表")
        dialog.setIcon(QMessageBox.Information)
        
        if workflows:
            text = "找到以下工作流:\n\n"
            for workflow in workflows:
                text += f"• {workflow['name']} (ID: {workflow['id']})\n"
        else:
            text = "未找到工作流"
            
        dialog.setText(text)
        dialog.exec_()
        
    def save_workflow_config(self):
        """保存工作流配置"""
        try:
            repo = self.repo_input.text().strip()
            workflow = self.workflow_input.text().strip()
            branch = self.branch_input.text().strip()
            
            if not repo or not workflow:
                QMessageBox.warning(self, "警告", "请填写仓库和工作流信息")
                return
                
            # 检查是否有用户
            users = self.user_manager.get_all_users()
            if not users:
                QMessageBox.warning(self, "警告", "请先添加用户")
                return
                
            # 选择用户
            user_id = self.current_user_id
            if not user_id:
                dialog = UserSelectionDialog(users, self)
                if dialog.exec_() != QDialog.Accepted:
                    return
                user_id = dialog.get_selected_user_id()
                if not user_id:
                    QMessageBox.warning(self, "警告", "请选择用户")
                    return
                
            # 获取配置名称
            name_dialog = WorkflowNameDialog(self)
            if name_dialog.exec_() != QDialog.Accepted:
                return
                
            config_name = name_dialog.get_name()
            if not config_name:
                QMessageBox.warning(self, "警告", "请输入配置名称")
                return
                    
            # 保存配置
            config_id = self.workflow_manager.save_config_with_name(
                config_name, repo, workflow, branch, self.current_params, user_id
            )
            
            if config_id:
                self.log_message(f"工作流配置保存成功: {config_name}")
                QMessageBox.information(self, "成功", "工作流配置保存成功")
                self.load_workflow_configs()
            else:
                self.log_message("工作流配置保存失败", "ERROR")
                QMessageBox.critical(self, "错误", "工作流配置保存失败")
                
        except Exception as e:
            self.log_message(f"保存工作流配置失败: {str(e)}", "ERROR")
            QMessageBox.critical(self, "错误", f"保存工作流配置失败: {str(e)}")
            
    def add_user(self):
        """添加用户"""
        try:
            username = self.username_input.text().strip()
            token = self.token_input.text().strip()
            
            if not username or not token:
                QMessageBox.warning(self, "警告", "请填写用户名和Token")
                return
                
            # 检查用户名是否已存在
            existing_user = self.user_manager.get_user_by_username(username)
            if existing_user:
                QMessageBox.warning(self, "警告", f"用户名 '{username}' 已存在")
                return
                
            # 添加用户
            user_id = self.user_manager.add_user(username, token)
            
            if user_id:
                self.log_message(f"用户添加成功: {username} (ID: {user_id})")
                QMessageBox.information(self, "成功", f"用户添加成功 (ID: {user_id})")
                self.load_users()
                self.username_input.clear()
                self.token_input.clear()
            else:
                self.log_message("用户添加失败", "ERROR")
                QMessageBox.critical(self, "错误", "用户添加失败")
                
        except Exception as e:
            self.log_message(f"添加用户失败: {str(e)}", "ERROR")
            QMessageBox.critical(self, "错误", f"添加用户失败: {str(e)}")
            
    def test_user_token(self):
        """测试用户Token"""
        try:
            username = self.username_input.text().strip()
            token = self.token_input.text().strip()
            
            if not username or not token:
                QMessageBox.warning(self, "警告", "请填写用户名和Token")
                return
                
            # 测试Token
            if self.github_manager.test_token(token):
                self.log_message(f"Token测试成功: {username}")
                QMessageBox.information(self, "成功", "Token测试成功")
            else:
                self.log_message(f"Token测试失败: {username}", "ERROR")
                QMessageBox.critical(self, "错误", "Token测试失败")
                
        except Exception as e:
            self.log_message(f"Token测试失败: {str(e)}", "ERROR")
            QMessageBox.critical(self, "错误", f"Token测试失败: {str(e)}")
            
    def load_users(self):
        """加载用户列表"""
        try:
            users = self.user_manager.get_all_users()
            self.user_table.setRowCount(len(users))
            
            for i, user in enumerate(users):
                self.user_table.setItem(i, 0, QTableWidgetItem(str(user['id'])))
                self.user_table.setItem(i, 1, QTableWidgetItem(user['username']))
                
                # 测试Token状态
                token_status = "有效" if self.user_manager.test_user_token(user['id']) else "无效"
                status_item = QTableWidgetItem(token_status)
                status_item.setForeground(QColor("green") if token_status == "有效" else QColor("red"))
                self.user_table.setItem(i, 2, status_item)
                
                self.user_table.setItem(i, 3, QTableWidgetItem(user['created_at']))
                
                # 删除按钮
                delete_btn = QPushButton("删除")
                delete_btn.setStyleSheet("background-color: #dc3545; font-size: 10px; padding: 4px 8px;")
                delete_btn.clicked.connect(lambda checked, user_id=user['id']: self.delete_user(user_id))
                self.user_table.setCellWidget(i, 4, delete_btn)
                
        except Exception as e:
            self.log_message(f"加载用户列表失败: {str(e)}", "ERROR")
            
    def delete_user(self, user_id):
        """删除用户"""
        try:
            reply = QMessageBox.question(self, "确认", "确定要删除这个用户吗？\n删除用户会同时删除该用户的所有工作流配置。",
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                if self.user_manager.delete_user(user_id):
                    self.log_message(f"用户删除成功: {user_id}")
                    self.load_users()
                    self.load_workflow_configs()
                else:
                    self.log_message("用户删除失败", "ERROR")
                    
        except Exception as e:
            self.log_message(f"删除用户失败: {str(e)}", "ERROR")
            
    def load_workflow_configs(self):
        """加载工作流配置列表"""
        try:
            configs = self.workflow_manager.get_all_configs()
            self.workflow_table.setRowCount(len(configs))
            
            for i, config in enumerate(configs):
                self.workflow_table.setItem(i, 0, QTableWidgetItem(str(config['id'])))
                self.workflow_table.setItem(i, 1, QTableWidgetItem(config['name']))
                self.workflow_table.setItem(i, 2, QTableWidgetItem(config.get('user_name', '未知')))
                self.workflow_table.setItem(i, 3, QTableWidgetItem(config['repo']))
                self.workflow_table.setItem(i, 4, QTableWidgetItem(config['workflow']))
                self.workflow_table.setItem(i, 5, QTableWidgetItem(config['branch']))
                self.workflow_table.setItem(i, 6, QTableWidgetItem("已保存"))
                
                # 操作按钮
                button_layout = QHBoxLayout()
                button_layout.setContentsMargins(2, 2, 2, 2)
                button_layout.setSpacing(4)
                
                trigger_btn = QPushButton("触发")
                trigger_btn.setStyleSheet("background-color: #28a745; font-size: 10px; padding: 4px 8px;")
                trigger_btn.clicked.connect(lambda checked, c=config: self.trigger_saved_workflow(c))
                
                edit_btn = QPushButton("编辑")
                edit_btn.setStyleSheet("background-color: #ffc107; color: black; font-size: 10px; padding: 4px 8px;")
                edit_btn.clicked.connect(lambda checked, c=config: self.edit_workflow_config(c))
                
                delete_btn = QPushButton("删除")
                delete_btn.setStyleSheet("background-color: #dc3545; font-size: 10px; padding: 4px 8px;")
                delete_btn.clicked.connect(lambda checked, config_id=config['id']: self.delete_workflow_config(config_id))
                
                button_layout.addWidget(trigger_btn)
                button_layout.addWidget(edit_btn)
                button_layout.addWidget(delete_btn)
                
                button_widget = QWidget()
                button_widget.setLayout(button_layout)
                self.workflow_table.setCellWidget(i, 7, button_widget)
                
        except Exception as e:
            self.log_message(f"加载工作流配置失败: {str(e)}", "ERROR")
            
    def trigger_saved_workflow(self, config):
        """触发保存的工作流"""
        try:
            # 获取用户Token
            user_token = self.user_manager.get_user_token(config['user_id'])
            if not user_token:
                QMessageBox.warning(self, "警告", "无法获取用户的GitHub Token")
                return
                
            # 设置Token
            self.github_manager.set_token(user_token)
            self.workflow_manager.set_github_token(user_token)
            
            result = self.workflow_manager.trigger_workflow(
                config['repo'], 
                config['workflow'], 
                config['branch'], 
                config.get('inputs', {})
            )
            
            if result:
                self.log_message(f"保存的工作流触发成功: {config['name']}")
                QMessageBox.information(self, "成功", "工作流触发成功")
            else:
                self.log_message(f"保存的工作流触发失败: {config['name']}", "ERROR")
                QMessageBox.critical(self, "错误", "工作流触发失败")
                
        except Exception as e:
            self.log_message(f"触发保存的工作流失败: {str(e)}", "ERROR")
            QMessageBox.critical(self, "错误", f"触发保存的工作流失败: {str(e)}")
            
    def edit_workflow_config(self, config):
        """编辑工作流配置"""
        try:
            # 填充表单
            self.repo_input.setText(config['repo'])
            self.workflow_input.setText(config['workflow'])
            self.branch_input.setText(config['branch'])
            
            # 设置参数
            self.current_params = config.get('inputs', {})
            if self.current_params:
                self.params_btn.setText(f"已设置 {len(self.current_params)} 个参数")
                self.params_btn.setStyleSheet("background-color: #28a745;")
            else:
                self.params_btn.setText("设置参数")
                self.params_btn.setStyleSheet("")
                
            # 切换到工作流标签页
            self.tab_widget.setCurrentIndex(1)
            
            self.log_message(f"已加载工作流配置: {config['name']}")
            
        except Exception as e:
            self.log_message(f"编辑工作流配置失败: {str(e)}", "ERROR")
            
    def delete_workflow_config(self, config_id):
        """删除工作流配置"""
        try:
            reply = QMessageBox.question(self, "确认", "确定要删除这个工作流配置吗？",
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                if self.workflow_manager.delete_config(config_id):
                    self.log_message(f"工作流配置删除成功: {config_id}")
                    self.load_workflow_configs()
                else:
                    self.log_message("工作流配置删除失败", "ERROR")
                    
        except Exception as e:
            self.log_message(f"删除工作流配置失败: {str(e)}", "ERROR")
            
    def log_message(self, message, level="INFO"):
        """记录日志消息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        # 添加到日志文本区域
        self.log_text.append(log_entry)
        
        # 滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # 同时记录到文件
        if level == "ERROR":
            logging.error(message)
        else:
            logging.info(message)
            
    def clear_log(self):
        """清空日志"""
        self.log_text.clear()
        self.log_message("日志已清空")
        
    def export_log(self):
        """导出日志"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "导出日志", "github_action_log.txt", "Text Files (*.txt)"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                    
                self.log_message(f"日志已导出到: {filename}")
                QMessageBox.information(self, "成功", "日志导出成功")
                
        except Exception as e:
            self.log_message(f"导出日志失败: {str(e)}", "ERROR")
            QMessageBox.critical(self, "错误", f"导出日志失败: {str(e)}")

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("GitHub Action 管理系统 v2.1")
    app.setApplicationVersion("2.1.0")
    app.setOrganizationName("AI Assistant")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 