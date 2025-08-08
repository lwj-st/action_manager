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
                             QScrollArea, QDialog, QDialogButtonBox, QListWidget, QListWidgetItem)
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
        self.setWindowTitle("GitHub Action 管理系统 v3.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
                margin-top: -1px;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 1px solid #dee2e6;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 12px 24px;
                margin-right: 2px;
                font-size: 13px;
                font-weight: 500;
                color: #495057;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border-bottom: 2px solid #007bff;
                color: #007bff;
                font-weight: 600;
            }
            QTabBar::tab:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e9ecef, stop:1 #dee2e6);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007bff, stop:1 #0056b3);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0056b3, stop:1 #004085);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #004085, stop:1 #002752);
            }
            QPushButton:disabled {
                background: #6c757d;
                color: #adb5bd;
            }
            QLineEdit, QTextEdit {
                border: 2px solid #e9ecef;
                border-radius: 6px;
                padding: 10px;
                font-size: 12px;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #007bff;
                outline: none;
            }
            QTableWidget {
                gridline-color: #e9ecef;
                selection-background-color: #e3f2fd;
                font-size: 12px;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #f8f9fa;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #000;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 1px solid #dee2e6;
                padding: 12px 8px;
                font-weight: 600;
                font-size: 12px;
                color: #495057;
            }
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                margin-top: 15px;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #495057;
            }
            QScrollBar:vertical {
                background: #f8f9fa;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #adb5bd;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #6c757d;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建标题
        title_label = QLabel("🚀 GitHub Action 管理系统 v3.0")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
        title_label.setStyleSheet("""
            color: #2c3e50;
            margin: 20px;
            padding: 15px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #3498db, stop:1 #2980b9);
            border-radius: 10px;
            color: white;
        """)
        main_layout.addWidget(title_label)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 创建各个标签页
        self.create_dashboard_tab()
        self.create_workflow_tab()
        self.create_workflow_runs_tab()  # 新增工作流运行管理标签页
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
        
        self.tab_widget.addTab(dashboard_widget, "📊 仪表板")
        
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
        self.workflow_table.setColumnWidth(7, 320)  # 进一步增加操作列宽度
        
        list_layout.addWidget(self.workflow_table)
        
        layout.addWidget(list_group)
        
        self.tab_widget.addTab(workflow_widget, "🛠️ 工作流管理")
        
    def create_workflow_runs_tab(self):
        """创建工作流运行管理标签页"""
        runs_widget = QWidget()
        layout = QVBoxLayout(runs_widget)
        
        # 操作按钮区域
        runs_actions_group = QGroupBox("操作")
        runs_actions_layout = QHBoxLayout(runs_actions_group)
        
        refresh_runs_btn = QPushButton("🔄 刷新")
        refresh_runs_btn.clicked.connect(self.load_workflow_runs)
        
        runs_actions_layout.addWidget(refresh_runs_btn)
        runs_actions_layout.addStretch()
        
        layout.addWidget(runs_actions_group)
        
        # 工作流运行列表
        runs_group = QGroupBox("工作流运行记录")
        runs_layout = QVBoxLayout(runs_group)
        
        self.runs_table = QTableWidget()
        self.runs_table.setColumnCount(8)
        self.runs_table.setHorizontalHeaderLabels([
            "运行ID", "工作流名称", "仓库", "分支", "状态", "结论", "开始时间", "操作"
        ])
        
        # 设置列宽
        header = self.runs_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 运行ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 工作流名称
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 仓库
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 分支
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 状态
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 结论
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # 开始时间
        header.setSectionResizeMode(7, QHeaderView.Fixed)  # 操作
        self.runs_table.setColumnWidth(7, 320)  # 进一步增加操作列宽度
        
        runs_layout.addWidget(self.runs_table)
        
        layout.addWidget(runs_group)
        
        self.tab_widget.addTab(runs_widget, "🚀 工作流运行")
        
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
        
        self.tab_widget.addTab(user_widget, "👤 用户管理")
        
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
        
        self.tab_widget.addTab(log_widget, "📝 系统日志")
        
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
            
            # 加载工作流运行记录
            self.load_workflow_runs()
            
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
            
            if result and result.get('success'):
                # 立即显示成功提示
                QMessageBox.information(self, "成功", "工作流触发成功！")
                
                self.log_message(f"工作流触发成功: {repo}/{workflow}")
                
                # 后台获取运行信息
                import threading
                import pytz
                from PyQt5.QtCore import QTimer
                
                trigger_time = datetime.now(pytz.UTC)
                thread = threading.Thread(
                    target=self.workflow_manager.get_triggered_run_info,
                    args=(repo, workflow, trigger_time, None)
                )
                thread.daemon = True
                thread.start()
                
                # 使用QTimer延迟6秒后刷新运行列表，避免SQLite线程问题
                QTimer.singleShot(6000, self.load_workflow_runs)
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
                # 去掉成功提示对话框，只保留日志
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
                # 去掉成功提示对话框，只保留日志
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
                delete_btn.setStyleSheet("background-color: #dc3545; font-size: 13px; font-weight: 600; padding: 1px 16px; min-width: 60px; min-height: 32px; border-radius: 4px;")
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
                button_layout.setContentsMargins(0, 0, 0, 0)
                button_layout.setSpacing(10)
                
                trigger_btn = QPushButton("触发")
                trigger_btn.setStyleSheet("background-color: #28a745; font-size: 13px; font-weight: 600; padding: 1px 16px; min-width: 60px; min-height: 32px; border-radius: 4px;")
                trigger_btn.clicked.connect(lambda checked, c=config: self.trigger_saved_workflow(c))
                
                edit_btn = QPushButton("编辑")
                edit_btn.setStyleSheet("background-color: #ffc107; color: black; font-size: 13px; font-weight: 600; padding: 1px 16px; min-width: 60px; min-height: 32px; border-radius: 4px;")
                edit_btn.clicked.connect(lambda checked, c=config: self.edit_workflow_config(c))
                
                delete_btn = QPushButton("删除")
                delete_btn.setStyleSheet("background-color: #dc3545; font-size: 13px; font-weight: 600; padding: 1px 16px; min-width: 60px; min-height: 32px; border-radius: 4px;")
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
                config.get('inputs', {}),
                config['id']  # 传递config_id
            )
            
            if result and result.get('success'):
                # 立即显示成功提示
                QMessageBox.information(self, "成功", "工作流触发成功！")
                
                self.log_message(f"保存的工作流触发成功: {config['name']}")
                
                # 后台获取运行信息
                import threading
                import pytz
                from PyQt5.QtCore import QTimer
                
                trigger_time = datetime.now(pytz.UTC)
                thread = threading.Thread(
                    target=self.workflow_manager.get_triggered_run_info,
                    args=(config['repo'], config['workflow'], trigger_time, config['id'])
                )
                thread.daemon = True
                thread.start()
                
                # 使用QTimer延迟6秒后刷新运行列表，避免SQLite线程问题
                QTimer.singleShot(6000, self.load_workflow_runs)
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

    def load_workflow_runs(self):
        """加载工作流运行记录"""
        try:
            # 先尝试同步运行信息
            self.sync_workflow_runs_silent()
            
            # 然后加载运行记录
            runs = self.workflow_manager.get_workflow_runs_from_db()
            self.runs_table.setRowCount(len(runs))
            
            for i, run in enumerate(runs):
                self.runs_table.setItem(i, 0, QTableWidgetItem(str(run.get('run_id', ''))))
                self.runs_table.setItem(i, 1, QTableWidgetItem(run.get('workflow_name', '未知')))
                self.runs_table.setItem(i, 2, QTableWidgetItem(run.get('repo', '')))
                self.runs_table.setItem(i, 3, QTableWidgetItem(run.get('branch', '')))
                
                # 状态列
                status = run.get('status', 'unknown')
                status_item = QTableWidgetItem(status)
                if status == 'completed':
                    status_item.setForeground(QColor("green"))
                elif status == 'in_progress':
                    status_item.setForeground(QColor("blue"))
                elif status == 'failed':
                    status_item.setForeground(QColor("red"))
                self.runs_table.setItem(i, 4, status_item)
                
                # 结论列
                conclusion = run.get('conclusion', '')
                conclusion_item = QTableWidgetItem(conclusion)
                if conclusion == 'success':
                    conclusion_item.setForeground(QColor("green"))
                elif conclusion == 'failure':
                    conclusion_item.setForeground(QColor("red"))
                elif conclusion == 'cancelled':
                    conclusion_item.setForeground(QColor("orange"))
                self.runs_table.setItem(i, 5, conclusion_item)
                
                # 开始时间
                created_at = run.get('created_at', '')
                if created_at:
                    # 格式化时间显示
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                        self.runs_table.setItem(i, 6, QTableWidgetItem(formatted_time))
                    except:
                        self.runs_table.setItem(i, 6, QTableWidgetItem(created_at))
                else:
                    self.runs_table.setItem(i, 6, QTableWidgetItem(''))
                
                # 操作按钮
                button_layout = QHBoxLayout()
                button_layout.setContentsMargins(0, 0, 0, 0)
                button_layout.setSpacing(10)
                
                # 取消运行按钮
                cancel_btn = QPushButton("❌ 取消")
                cancel_btn.setStyleSheet("background-color: #dc3545; font-size: 13px; font-weight: 600; padding: 1px 16px; min-width: 70px; min-height: 32px; border-radius: 4px;")
                cancel_btn.setToolTip("取消运行")
                cancel_btn.clicked.connect(lambda checked, run_id=run.get('run_id'): self.cancel_workflow_run(run_id))
                button_layout.addWidget(cancel_btn)
                
                # 浏览器查看按钮
                if run.get('html_url'):
                    open_browser_btn = QPushButton("🌐 查看")
                    open_browser_btn.setStyleSheet("background-color: #28a745; font-size: 13px; font-weight: 600; padding: 1px 16px; min-width: 70px; min-height: 32px; border-radius: 4px;")
                    open_browser_btn.setToolTip("在浏览器中打开")
                    open_browser_btn.clicked.connect(lambda checked, run_id=run.get('run_id'): self.open_run_in_browser(run_id))
                    button_layout.addWidget(open_browser_btn)
                
                # 查看日志按钮
                view_logs_btn = QPushButton("📋 日志")
                view_logs_btn.setStyleSheet("background-color: #007bff; font-size: 13px; font-weight: 600; padding: 1px 16px; min-width: 70px; min-height: 32px; border-radius: 4px;")
                view_logs_btn.setToolTip("查看日志")
                view_logs_btn.clicked.connect(lambda checked, run_id=run.get('run_id'): self.view_run_logs(run_id))
                button_layout.addWidget(view_logs_btn)
                
                button_widget = QWidget()
                button_widget.setLayout(button_layout)
                self.runs_table.setCellWidget(i, 7, button_widget)
                
        except Exception as e:
            self.log_message(f"加载工作流运行记录失败: {str(e)}", "ERROR")
            

            
    def open_run_in_browser(self, run_id):
        """在浏览器中打开指定运行"""
        try:
            run = self.workflow_manager.get_run_by_id(run_id)
            if run and run.get('html_url'):
                url = run['html_url']
                self.log_message(f"尝试打开运行URL: {url}")
                if self.github_manager.open_url_in_browser(url):
                    self.log_message(f"成功打开运行URL: {url}")
                    QMessageBox.information(self, "成功", f"已打开运行URL: {url}")
                else:
                    self.log_message(f"无法打开运行URL: {url}", "ERROR")
                    QMessageBox.critical(self, "错误", f"无法打开运行URL: {url}")
            else:
                self.log_message(f"运行记录或URL不存在: {run_id}", "ERROR")
                QMessageBox.critical(self, "错误", f"运行记录或URL不存在: {run_id}")
        except Exception as e:
            self.log_message(f"打开运行URL失败: {str(e)}", "ERROR")
            QMessageBox.critical(self, "错误", f"打开运行URL失败: {str(e)}")
            
    def view_run_logs(self, run_id):
        """查看指定运行的日志"""
        try:
            # 检查是否是临时run_id
            if run_id.startswith('triggered_'):
                QMessageBox.warning(self, "警告", f"无法获取临时运行ID的日志: {run_id}\n请等待运行信息同步或手动刷新。")
                return
                
            logs = self.workflow_manager.get_run_logs(run_id)
            if logs:
                self.log_message(f"获取到运行日志: {run_id}")
                self.show_run_logs(logs)
            else:
                self.log_message(f"未找到日志: {run_id}", "ERROR")
                QMessageBox.critical(self, "错误", f"未找到日志: {run_id}")
        except Exception as e:
            self.log_message(f"获取运行日志失败: {str(e)}", "ERROR")
            QMessageBox.critical(self, "错误", f"获取运行日志失败: {str(e)}")
            
    def show_run_logs(self, logs):
        """显示运行日志"""
        try:
            # 检查日志格式
            if isinstance(logs, dict):
                # 多文件日志，使用新的查看器
                if len(logs) > 1:
                    # 多个文件，使用多文件查看器
                    viewer = MultiFileLogViewer(logs, self)
                    viewer.exec_()
                else:
                    # 单个文件，显示内容
                    filename = list(logs.keys())[0]
                    content = logs[filename]
                    self.show_single_log(filename, content)
            elif isinstance(logs, str):
                # 单个字符串日志
                self.show_single_log("日志", logs)
            elif isinstance(logs, bytes):
                # 字节格式，尝试解码
                try:
                    decoded_logs = logs.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        decoded_logs = logs.decode('gbk')
                    except UnicodeDecodeError:
                        decoded_logs = logs.decode('utf-8', errors='ignore')
                self.show_single_log("日志", decoded_logs)
            else:
                # 其他格式，转换为字符串
                self.show_single_log("日志", str(logs))
                
        except Exception as e:
            self.log_message(f"显示日志失败: {str(e)}", "ERROR")
            QMessageBox.critical(self, "错误", f"显示日志失败: {str(e)}")
    
    def show_single_log(self, title, content):
        """显示单个日志文件"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle(f"运行日志 - {title}")
            dialog.setModal(True)
            dialog.resize(800, 600)
            
            layout = QVBoxLayout(dialog)
            
            # 日志文本区域
            log_text = QTextEdit()
            log_text.setReadOnly(True)
            log_text.setFont(QFont("Consolas", 10))
            log_text.setPlainText(content)
            
            layout.addWidget(log_text)
            
            # 按钮
            button_layout = QHBoxLayout()
            
            copy_btn = QPushButton("复制")
            copy_btn.clicked.connect(lambda: self.copy_to_clipboard(content))
            
            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(dialog.accept)
            
            button_layout.addWidget(copy_btn)
            button_layout.addStretch()
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
            
            dialog.exec_()
            
        except Exception as e:
            self.log_message(f"显示日志失败: {str(e)}", "ERROR")
            QMessageBox.critical(self, "错误", f"显示日志失败: {str(e)}")
    
    def copy_to_clipboard(self, text):
        """复制文本到剪贴板"""
        try:
            from PyQt5.QtWidgets import QApplication
            QApplication.clipboard().setText(text)
            self.log_message("日志已复制到剪贴板")
        except Exception as e:
            self.log_message(f"复制到剪贴板失败: {str(e)}", "ERROR")
        
    def cancel_workflow_run(self, run_id):
        """取消指定运行"""
        try:
            # 检查是否是临时run_id
            if run_id.startswith('triggered_'):
                QMessageBox.warning(self, "警告", f"无法取消临时运行ID: {run_id}\n请等待运行信息同步或手动刷新。")
                return
                
            run = self.workflow_manager.get_run_by_id(run_id)
            if run:
                status = run.get('status', '')
                if status == 'completed':
                    QMessageBox.warning(self, "警告", f"运行已结束，无法取消: {run_id}")
                    return
                    
                reply = QMessageBox.question(self, "确认", f"确定要取消运行 {run_id} 吗？",
                                           QMessageBox.Yes | QMessageBox.No)
                
                if reply == QMessageBox.Yes:
                    if self.workflow_manager.cancel_workflow_run(run_id):
                        self.log_message(f"运行取消成功: {run_id}")
                        QMessageBox.information(self, "成功", f"运行取消成功: {run_id}")
                        self.load_workflow_runs() # 刷新运行列表
                    else:
                        self.log_message(f"运行取消失败: {run_id}", "ERROR")
                        QMessageBox.critical(self, "错误", f"运行取消失败: {run_id}")
            else:
                self.log_message(f"未找到运行记录: {run_id}", "ERROR")
                QMessageBox.critical(self, "错误", f"未找到运行记录: {run_id}")
        except Exception as e:
            self.log_message(f"取消运行失败: {str(e)}", "ERROR")
            QMessageBox.critical(self, "错误", f"取消运行失败: {str(e)}")

    def sync_workflow_runs_silent(self):
        """静默同步工作流运行信息"""
        try:
            # 获取所有配置
            configs = self.workflow_manager.get_all_configs()
            if not configs:
                return
                
            # 检查是否有可用的Token
            users = self.user_manager.get_all_users()
            if not users:
                return
                
            # 使用当前用户或第一个用户的Token
            user_id = self.current_user_id if self.current_user_id else users[0]['id']
            user_token = self.user_manager.get_user_token(user_id)
            if not user_token:
                return
                
            # 设置Token
            self.github_manager.set_token(user_token)
            self.workflow_manager.set_github_token(user_token)
            
            # 同步每个配置的最新运行信息
            synced_count = 0
            for config in configs:
                try:
                    # 获取该配置的最新运行
                    latest_run = self.github_manager.get_latest_workflow_run(config['repo'], config['workflow'])
                    if latest_run:
                        # 更新或插入运行记录
                        self.db_manager.insert_workflow_run(
                            config_id=config['id'],
                            run_id=str(latest_run['id']),
                            status=latest_run.get('status', 'unknown'),
                            html_url=latest_run.get('html_url'),
                            conclusion=latest_run.get('conclusion'),
                            logs_url=latest_run.get('logs_url'),
                            workflow_name=latest_run.get('name'),
                            repo=config['repo'],
                            branch=config['branch'],
                            trigger_user=latest_run.get('actor', {}).get('login')
                        )
                        synced_count += 1
                        
                        # 同时更新现有运行的状态
                        self.update_existing_runs_status(config['repo'], config['workflow'])
                        
                except Exception as e:
                    self.log_message(f"静默同步配置 {config['name']} 失败: {str(e)}", "ERROR")
                    continue
            
            if synced_count > 0:
                self.log_message(f"静默同步完成，更新了 {synced_count} 个运行记录")
            
        except Exception as e:
            self.log_message(f"静默同步运行信息失败: {str(e)}", "ERROR")
            
    def update_existing_runs_status(self, repo: str, workflow: str):
        """更新现有运行的状态"""
        try:
            # 获取该workflow的最近几个运行
            runs = self.github_manager.list_workflow_runs(repo, workflow, per_page=5)
            
            for run in runs:
                run_id = str(run['id'])
                # 更新数据库中的运行状态
                self.db_manager.update_workflow_run_status(
                    run_id,
                    run.get('status', 'unknown'),
                    run.get('conclusion')
                )
                
        except Exception as e:
            self.log_message(f"更新运行状态失败: {str(e)}", "ERROR")

class MultiFileLogViewer(QDialog):
    """多文件日志查看器"""
    
    def __init__(self, logs_data, parent=None):
        super().__init__(parent)
        self.logs_data = logs_data  # 格式: { 'filename': 'content', ... }
        self.current_file = None
        self.init_ui()
        
    def clean_ansi_escape_codes(self, text):
        """清理ANSI转义序列"""
        import re
        # 移除ANSI转义序列
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
        
    def init_ui(self):
        self.setWindowTitle("工作流运行日志")
        self.setModal(True)
        self.resize(1000, 700)
        
        layout = QVBoxLayout(self)
        
        # 顶部信息栏
        info_layout = QHBoxLayout()
        info_label = QLabel(f"日志文件数量: {len(self.logs_data)}")
        info_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        
        # 清理ANSI按钮
        self.clean_ansi_btn = QPushButton("清理ANSI代码")
        self.clean_ansi_btn.clicked.connect(self.toggle_ansi_cleaning)
        self.clean_ansi_btn.setCheckable(True)
        self.clean_ansi_btn.setChecked(True)  # 默认开启
        info_layout.addWidget(self.clean_ansi_btn)
        
        # 导出按钮
        export_btn = QPushButton("导出所有日志")
        export_btn.clicked.connect(self.export_all_logs)
        info_layout.addWidget(export_btn)
        
        layout.addLayout(info_layout)
        
        # 分割器：左侧文件列表，右侧日志内容
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：文件列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        file_label = QLabel("日志文件:")
        file_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        left_layout.addWidget(file_label)
        
        self.file_list = QListWidget()
        self.file_list.setMaximumWidth(300)
        self.file_list.itemClicked.connect(self.on_file_selected)
        left_layout.addWidget(self.file_list)
        
        # 右侧：日志内容
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        content_label = QLabel("日志内容:")
        content_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        right_layout.addWidget(content_label)
        
        # 日志文本区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        right_layout.addWidget(self.log_text)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        self.copy_btn = QPushButton("复制当前文件")
        self.copy_btn.clicked.connect(self.copy_current_file)
        self.copy_btn.setEnabled(False)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(self.copy_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        right_layout.addLayout(button_layout)
        
        # 添加到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 700])  # 设置初始分割比例
        
        layout.addWidget(splitter)
        
        # 加载文件列表
        self.load_file_list()
        
    def load_file_list(self):
        """加载文件列表"""
        self.file_list.clear()
        
        for filename in sorted(self.logs_data.keys()):
            item = QListWidgetItem(filename)
            # 根据文件类型设置图标或颜色
            if filename.endswith('.txt'):
                item.setForeground(QColor("#2c3e50"))
            elif filename.endswith('.log'):
                item.setForeground(QColor("#e74c3c"))
            else:
                item.setForeground(QColor("#7f8c8d"))
            self.file_list.addItem(item)
        
        # 默认选择第一个文件
        if self.file_list.count() > 0:
            self.file_list.setCurrentRow(0)
            self.on_file_selected(self.file_list.item(0))
    
    def on_file_selected(self, item):
        """文件选择事件"""
        if not item:
            return
            
        filename = item.text()
        self.current_file = filename
        
        # 显示文件内容
        content = self.logs_data.get(filename, '')
        
        # 根据按钮状态决定是否清理ANSI代码
        if self.clean_ansi_btn.isChecked():
            content = self.clean_ansi_escape_codes(content)
            
        self.log_text.setPlainText(content)
        
        # 启用复制按钮
        self.copy_btn.setEnabled(True)
        
        # 更新标题显示当前文件
        self.setWindowTitle(f"工作流运行日志 - {filename}")
    
    def toggle_ansi_cleaning(self):
        """切换ANSI清理状态"""
        if self.current_file:
            # 重新显示当前文件内容
            self.on_file_selected(self.file_list.currentItem())
    
    def copy_current_file(self):
        """复制当前文件内容"""
        if not self.current_file:
            return
            
        content = self.logs_data.get(self.current_file, '')
        
        # 根据按钮状态决定是否清理ANSI代码
        if self.clean_ansi_btn.isChecked():
            content = self.clean_ansi_escape_codes(content)
            
        try:
            from PyQt5.QtWidgets import QApplication
            QApplication.clipboard().setText(content)
            QMessageBox.information(self, "成功", f"已复制 {self.current_file} 到剪贴板")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"复制失败: {str(e)}")
    
    def export_all_logs(self):
        """导出所有日志文件"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            import os
            
            # 选择导出目录
            export_dir = QFileDialog.getExistingDirectory(
                self, "选择导出目录", "", QFileDialog.ShowDirsOnly
            )
            
            if not export_dir:
                return
            
            # 创建日志文件夹
            logs_dir = os.path.join(export_dir, "workflow_logs")
            os.makedirs(logs_dir, exist_ok=True)
            
            # 导出所有文件
            exported_count = 0
            for filename, content in self.logs_data.items():
                file_path = os.path.join(logs_dir, filename)
                try:
                    # 根据按钮状态决定是否清理ANSI代码
                    if self.clean_ansi_btn.isChecked():
                        content = self.clean_ansi_escape_codes(content)
                        
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    exported_count += 1
                except Exception as e:
                    print(f"导出文件 {filename} 失败: {str(e)}")
            
            QMessageBox.information(
                self, "导出成功", 
                f"已导出 {exported_count}/{len(self.logs_data)} 个日志文件到:\n{logs_dir}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出日志失败: {str(e)}")

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