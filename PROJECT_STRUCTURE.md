# GitHub Action管理系统 - 项目结构

## 📁 文件说明

### 核心程序文件
- `main.py` - 主程序入口，包含完整的GUI界面
- `run.py` - 启动脚本，检查依赖并启动程序
- `start.bat` - Windows批处理启动文件

### 核心模块
- `database.py` - 数据库管理模块，处理SQLite数据库操作
- `github_manager.py` - GitHub API管理模块，处理GitHub API交互
- `workflow_manager.py` - 工作流管理模块，处理工作流配置和触发
- `user_manager.py` - 用户管理模块，处理用户认证和Token管理
- `config.py` - 配置管理模块，处理系统配置

### 配置文件
- `requirements.txt` - Python依赖包列表
- `config.json` - 系统配置文件（自动生成）

### 文档文件
- `README.md` - 项目主要说明文档
- `TROUBLESHOOTING.md` - 故障排除指南
- `FIXES.md` - 修复说明文档
- `PROJECT_STRUCTURE.md` - 项目结构说明（本文件）

### 运行时文件
- `github_action_manager.db` - SQLite数据库文件（自动生成）
- `github_action_manager.log` - 系统日志文件（自动生成）

## 🚀 启动方式

### 方法一：直接运行
```bash
python main.py
```

### 方法二：使用启动脚本
```bash
python run.py
```

### 方法三：Windows批处理
```bash
start.bat
```

## 📋 依赖包

### 必需依赖
- `PyQt5` - GUI界面框架
- `requests` - HTTP请求库

### 可选依赖
- `PyGithub` - GitHub API客户端（如果使用GitHub功能）
- `cryptography` - 加密库（如果使用加密功能）

## 🔧 安装依赖

```bash
pip install -r requirements.txt
```

## 📊 文件大小统计

| 文件 | 大小 | 说明 |
|------|------|------|
| main.py | 40KB | 主程序，包含GUI界面 |
| database.py | 16KB | 数据库管理模块 |
| workflow_manager.py | 12KB | 工作流管理模块 |
| user_manager.py | 11KB | 用户管理模块 |
| github_manager.py | 9.7KB | GitHub API管理模块 |
| config.py | 9.7KB | 配置管理模块 |
| README.md | 5.3KB | 主要说明文档 |
| FIXES.md | 4.0KB | 修复说明文档 |
| TROUBLESHOOTING.md | 2.7KB | 故障排除指南 |
| run.py | 1.3KB | 启动脚本 |
| start.bat | 908B | Windows启动文件 |
| requirements.txt | 114B | 依赖列表 |
| config.json | 979B | 配置文件 |

## 🗂️ 目录结构

```
github-action-manager/
├── 核心程序文件
│   ├── main.py              # 主程序入口
│   ├── run.py               # 启动脚本
│   └── start.bat            # Windows启动文件
│
├── 核心模块
│   ├── database.py          # 数据库管理
│   ├── github_manager.py    # GitHub API管理
│   ├── workflow_manager.py  # 工作流管理
│   ├── user_manager.py      # 用户管理
│   └── config.py           # 配置管理
│
├── 配置文件
│   ├── requirements.txt     # 依赖列表
│   └── config.json         # 系统配置
│
├── 文档文件
│   ├── README.md           # 主要说明
│   ├── TROUBLESHOOTING.md # 故障排除
│   ├── FIXES.md           # 修复说明
│   └── PROJECT_STRUCTURE.md # 项目结构
│
└── 运行时文件
    ├── github_action_manager.db  # 数据库文件
    └── github_action_manager.log # 日志文件
```

## 🎯 系统特点

### 简洁性
- 只保留必要的文件
- 删除所有测试和演示文件
- 清理缓存和临时文件

### 完整性
- 包含所有核心功能模块
- 保留必要的文档和说明
- 维护配置文件和数据文件

### 可维护性
- 清晰的文件结构
- 详细的文档说明
- 模块化的代码设计

## 📝 注意事项

1. **数据库文件**: `github_action_manager.db` 包含用户和工作流配置，请定期备份
2. **日志文件**: `github_action_manager.log` 记录系统操作，可用于问题诊断
3. **配置文件**: `config.json` 包含系统设置，首次运行会自动生成
4. **依赖包**: 确保安装了所有必需的Python包

## 🔄 更新维护

- 定期检查依赖包更新
- 备份重要的数据文件
- 查看日志文件了解系统运行状态
- 参考文档解决常见问题 