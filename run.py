#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Action管理系统启动脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函数"""
    try:
        # 检查依赖
        print("检查依赖包...")
        required_packages = [
            'PyQt5',
            'requests'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"✗ {package} - 未安装")
        
        if missing_packages:
            print(f"\n缺少依赖包: {', '.join(missing_packages)}")
            print("请运行: pip install -r requirements.txt")
            return
        
        print("\n所有依赖包已安装，启动GitHub Action管理系统...")
        
        # 导入并启动主程序
        from main import main as start_app
        start_app()
        
    except Exception as e:
        print(f"启动失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 