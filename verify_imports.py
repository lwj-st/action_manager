#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入验证脚本 - 检查所有模块导入是否正确
"""

import sys
import os

def test_imports():
    """测试所有模块导入"""
    print("🔍 验证GitHub Action管理系统模块导入...")
    print("=" * 50)
    
    modules_to_test = [
        ('database', 'DatabaseManager'),
        ('github_manager', 'GitHubManager'),
        ('workflow_manager', 'WorkflowManager'),
        ('user_manager', 'UserManager'),
        ('config', 'Config'),
        ('main', 'main')
    ]
    
    all_success = True
    
    for module_name, class_name in modules_to_test:
        try:
            if module_name == 'main':
                # 主程序特殊处理
                from main import main
                print(f"✅ {module_name} - 导入成功")
            else:
                # 其他模块
                module = __import__(module_name)
                if hasattr(module, class_name):
                    print(f"✅ {module_name} - {class_name} 导入成功")
                else:
                    print(f"❌ {module_name} - {class_name} 不存在")
                    all_success = False
        except ImportError as e:
            print(f"❌ {module_name} - 导入失败: {e}")
            all_success = False
        except Exception as e:
            print(f"❌ {module_name} - 其他错误: {e}")
            all_success = False
    
    print("=" * 50)
    
    if all_success:
        print("🎉 所有模块导入成功！")
        print("\n系统可以正常启动，请运行以下命令启动程序：")
        print("  python main.py")
        print("  或")
        print("  python run.py")
        print("  或")
        print("  start.bat")
    else:
        print("❌ 部分模块导入失败，请检查依赖包安装")
        print("\n请运行以下命令安装依赖：")
        print("  pip install -r requirements.txt")
    
    return all_success

def test_dependencies():
    """测试依赖包"""
    print("\n📦 检查依赖包...")
    print("-" * 30)
    
    dependencies = [
        'PyQt5',
        'requests'
    ]
    
    missing_deps = []
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - 未安装")
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"\n缺少依赖包: {', '.join(missing_deps)}")
        print("请运行: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ 所有依赖包已安装")
        return True

def main():
    """主函数"""
    print("🔧 GitHub Action管理系统 - 导入验证")
    print("=" * 60)
    
    # 测试依赖包
    deps_ok = test_dependencies()
    
    if deps_ok:
        # 测试模块导入
        imports_ok = test_imports()
        
        if imports_ok:
            print("\n🎊 验证完成！系统可以正常使用。")
            return True
        else:
            print("\n❌ 模块导入验证失败。")
            return False
    else:
        print("\n❌ 依赖包验证失败。")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 验证过程中发生错误: {e}")
        sys.exit(1) 