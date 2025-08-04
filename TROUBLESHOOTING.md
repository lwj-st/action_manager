# 故障排除指南

## 常见问题及解决方案

### 1. GitHub连接失败

**症状**: 日志显示 "GitHub连接失败"

**可能原因**:
- 未添加GitHub Token
- Token无效或过期
- Token权限不足
- 网络连接问题

**解决方案**:
1. 确保已添加有效的GitHub Personal Access Token
2. 检查Token是否具有以下权限:
   - `repo` (完整仓库访问权限)
   - `workflow` (工作流权限)
3. 运行调试脚本检查Token:
   ```bash
   python debug.py
   ```

### 2. 工作流触发失败

**症状**: 点击触发按钮后显示失败

**可能原因**:
- 仓库名称格式错误
- 工作流名称或ID错误
- Token没有相应权限
- 工作流文件不存在

**解决方案**:
1. 检查仓库名称格式: `owner/repository`
2. 确认工作流文件名或ID正确
3. 使用"列出工作流"功能查看可用的工作流
4. 检查Token权限

### 3. 用户添加失败

**症状**: Token测试成功但用户添加失败

**可能原因**:
- 用户名已存在
- 数据库连接问题
- Token权限不足

**解决方案**:
1. 使用不同的用户名
2. 检查数据库文件权限
3. 确保Token有足够权限

### 4. 数据库连接失败

**症状**: 数据库状态显示"未连接"

**可能原因**:
- 数据库文件被占用
- 文件权限问题
- 磁盘空间不足

**解决方案**:
1. 关闭其他可能使用数据库的程序
2. 检查文件权限
3. 删除数据库文件重新创建

### 5. 程序无法启动

**症状**: 双击exe文件无反应

**可能原因**:
- 缺少依赖文件
- 杀毒软件拦截
- 系统兼容性问题

**解决方案**:
1. 从源码运行: `python main.py`
2. 添加程序到杀毒软件白名单
3. 以管理员身份运行

## 调试步骤

### 步骤1: 检查环境
```bash
python check_env.py
```

### 步骤2: 检查Token
```bash
python debug.py
```

### 步骤3: 查看日志
检查 `github_action_manager.log` 文件中的详细错误信息

### 步骤4: 测试基本功能
```bash
python demo.py
```

## 获取GitHub Token

1. 登录GitHub
2. 进入 Settings > Developer settings > Personal access tokens
3. 点击 "Generate new token (classic)"
4. 选择权限:
   - `repo` (完整仓库访问权限)
   - `workflow` (工作流权限)
5. 生成并复制Token

## 常见错误代码

- `401 Unauthorized`: Token无效或过期
- `403 Forbidden`: Token权限不足
- `404 Not Found`: 仓库或工作流不存在
- `422 Unprocessable Entity`: 请求参数错误

## 联系支持

如果问题仍然存在，请提供以下信息:
1. 错误日志内容
2. 系统环境信息
3. 复现步骤
4. GitHub Token权限截图 