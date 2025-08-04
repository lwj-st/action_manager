# GitHub Action 管理系统

一个友好的GitHub Action管理系统，支持通过图形界面管理和触发GitHub工作流。

## 功能特性

### 🔐 安全可靠
- 安全的Token管理
- 数据库加密存储
- 用户权限控制

### 🚀 工作流管理
- 可视化工作流配置
- 支持参数传递
- 一键触发工作流
- 实时状态监控

### 👥 多用户支持
- 多用户Token管理
- 用户权限隔离
- 操作日志记录

### 📊 日志系统
- 详细的操作日志
- 工作流运行日志
- 日志导出功能

### �� 美观界面
- 现代化GUI界面
- 中文界面支持
- 响应式设计

## 系统要求

- Windows 10/11
- Python 3.7+
- 网络连接

## 安装说明

### 方法一：直接运行（推荐）

1. 下载最新版本的exe文件
2. 双击运行 `GitHub Action Manager.exe`
3. 首次运行会自动创建数据库文件

### 方法二：从源码运行

1. 克隆项目
```bash
git clone <repository-url>
cd github-action-manager
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

**注意**: 如果看到 `sqlite3` 安装错误，这是正常的，因为 `sqlite3` 是 Python 标准库的一部分，无需单独安装。

3. 运行程序
```bash
python main.py
```

或使用启动脚本：
```bash
python run.py
```

## 使用指南

### 1. 添加GitHub Token

1. 打开程序，进入"用户管理"标签页
2. 输入您的GitHub用户名
3. 输入您的GitHub Personal Access Token
4. 点击"添加用户"

**如何获取GitHub Token：**
1. 登录GitHub
2. 进入 Settings > Developer settings > Personal access tokens
3. 点击 "Generate new token"
4. 选择需要的权限（至少需要 `repo` 权限）
5. 复制生成的Token

### 2. 配置工作流

1. 进入"工作流管理"标签页
2. 填写仓库信息（格式：owner/repository）
3. 填写工作流文件名或ID
4. 选择分支（默认为main）
5. 点击"设置参数"添加Key-Value格式的参数
6. 点击"保存配置"并输入配置名称

### 3. 触发工作流

1. 在"工作流管理"标签页中
2. 选择要触发的工作流配置
3. 点击"触发"按钮
4. 查看运行状态和日志

### 4. 查看日志

1. 进入"系统日志"标签页
2. 查看详细的操作日志
3. 可以清空或导出日志

## 配置说明

程序会在同级目录生成以下文件：

- `github_action_manager.db` - SQLite数据库文件
- `github_action_manager.log` - 系统日志文件
- `config.json` - 配置文件

### 数据库配置

支持连接外部数据库，修改 `config.json` 中的数据库配置：

```json
{
  "database": {
    "type": "sqlite",  // 或 "mysql", "postgresql"
    "host": "localhost",
    "port": 3306,
    "username": "user",
    "password": "password",
    "database": "github_action_manager"
  }
}
```

## 项目结构

```
github-action-manager/
├── main.py              # 主程序入口（GUI界面）
├── run.py               # 启动脚本
├── database.py          # 数据库管理模块
├── github_manager.py    # GitHub API管理模块
├── workflow_manager.py  # 工作流管理模块
├── user_manager.py      # 用户管理模块
├── config.py           # 配置管理模块
├── requirements.txt    # 依赖列表
├── README.md          # 说明文档
├── TROUBLESHOOTING.md # 故障排除指南
├── FIXES.md           # 修复说明
├── start.bat          # Windows启动文件
└── config.json        # 配置文件
```

## 技术栈

- **GUI框架**: PyQt5
- **GitHub API**: PyGithub
- **HTTP请求**: requests
- **数据库**: SQLite
- **加密**: cryptography
- **打包**: PyInstaller

## 安全说明

1. **Token安全**: Token以加密形式存储在本地数据库中
2. **权限控制**: 每个用户只能访问自己的Token和配置
3. **日志记录**: 所有操作都会记录详细日志
4. **数据备份**: 支持数据库备份和恢复

## 常见问题

### Q: 程序无法启动
A: 请检查是否安装了所有依赖包，或尝试重新安装Python环境。

### Q: GitHub Token无效
A: 请检查Token是否正确，以及是否具有足够的权限。

### Q: 工作流触发失败
A: 请检查仓库名称、工作流名称是否正确，以及Token是否有相应权限。

### Q: 数据库连接失败
A: 请检查数据库文件权限，或尝试删除数据库文件重新创建。

## 更新日志

### v2.1.0 (2024-01-01)
- 修复用户添加失败问题
- 修复工作流保存失败问题
- 添加用户与工作流关联
- 改进错误处理和状态显示
- 优化界面布局

### v2.0.0 (2024-01-01)
- 支持自定义工作流配置名称
- 改进Key-Value参数输入
- 添加编辑工作流配置功能
- 优化界面显示

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持基本的GitHub Action管理功能
- 图形化界面
- 多用户支持

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交GitHub Issue
- 发送邮件至：[your-email@example.com]

---

**注意**: 请妥善保管您的GitHub Token，不要分享给他人。建议定期更换Token以确保安全。 