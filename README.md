# GitHub Action 管理系统 v3.0

一个功能完整的GitHub Actions工作流管理桌面应用程序，支持工作流触发、运行管理、用户管理等功能。

## ✨ 主要功能

### 🚀 工作流管理
- **工作流触发**：支持手动触发GitHub Actions工作流
- **参数配置**：支持自定义工作流参数
- **配置保存**：保存常用工作流配置，快速重复使用
- **工作流列表**：查看仓库中的所有可用工作流

### 📊 运行管理
- **运行记录**：查看所有工作流运行历史
- **状态监控**：实时监控运行状态和结果
- **运行取消**：支持取消正在运行的工作流
- **日志查看**：查看详细的运行日志（支持中文）
- **浏览器集成**：一键在浏览器中打开GitHub运行页面

### 👤 用户管理
- **多用户支持**：支持多个GitHub账户
- **Token管理**：安全的GitHub Token存储和管理
- **权限控制**：基于用户的工作流配置管理

### 🎨 用户界面
- **现代化UI**：美观的PyQt5界面设计
- **响应式布局**：自适应的界面布局
- **操作便捷**：简化的操作流程，提升用户体验

## 🛠️ 技术栈

- **Python 3.7+**
- **PyQt5** - 桌面GUI框架
- **SQLite3** - 本地数据存储
- **GitHub REST API** - GitHub集成

## 📦 安装和运行

### 环境要求
- Python 3.7 或更高版本
- Windows/Linux/macOS

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行应用
```bash
python main.py
```

### 打包为可执行文件
```bash
python build_exe.py
```

## 🔧 配置说明

### 1. GitHub Token
1. 在GitHub中生成Personal Access Token
2. 在应用中添加用户，输入Token
3. 测试Token有效性

### 2. 工作流配置
1. 填写仓库信息（格式：owner/repository）
2. 输入工作流文件名或ID
3. 设置分支名称（可选）
4. 配置工作流参数（可选）
5. 保存配置以便重复使用

## 📋 使用指南

### 工作流触发
1. 在"工作流管理"标签页填写仓库和工作流信息
2. 点击"触发工作流"按钮
3. 系统会立即显示成功提示
4. 在"工作流运行"标签页查看运行状态

### 运行管理
1. 在"工作流运行"标签页查看所有运行记录
2. 使用操作按钮进行管理：
   - **❌ 取消**：取消正在运行的workflow
   - **🌐 查看**：在浏览器中打开运行页面
   - **📋 日志**：查看详细运行日志

### 用户管理
1. 在"用户管理"标签页添加GitHub用户
2. 输入用户名和Personal Access Token
3. 测试Token有效性
4. 选择当前用户进行工作流操作

## 🗂️ 项目结构

```
action_manager/
├── main.py              # 主应用程序入口
├── config.py            # 配置管理
├── database.py          # 数据库管理
├── github_manager.py    # GitHub API集成
├── workflow_manager.py  # 工作流管理
├── user_manager.py      # 用户管理
├── build_exe.py         # 可执行文件打包
├── run.py              # 运行脚本
├── start.bat           # Windows启动脚本
├── requirements.txt    # Python依赖
├── config.json        # 应用配置
├── README.md          # 项目说明
└── LICENSE            # 开源协议
```

## 🔍 核心模块

### main.py
主应用程序，包含PyQt5 GUI界面和主要业务逻辑。

### database.py
SQLite数据库管理，处理用户、工作流配置、运行记录等数据存储。

### github_manager.py
GitHub REST API集成，处理工作流触发、状态查询、日志获取等操作。

### workflow_manager.py
工作流管理核心逻辑，协调数据库和GitHub API操作。

### user_manager.py
用户管理模块，处理GitHub Token验证和用户信息管理。

## 🚀 特性亮点

- **即时反馈**：触发后立即显示成功提示
- **后台同步**：自动同步运行信息，不阻塞用户界面
- **编码支持**：完美支持中文和英文日志显示
- **智能按钮**：根据数据状态智能显示操作按钮
- **简洁界面**：优化的按钮布局和间距设计

## 📄 开源协议

本项目采用 MIT 协议开源，详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

---

**GitHub Action 管理系统 v3.0** - 让GitHub Actions管理更简单！ 