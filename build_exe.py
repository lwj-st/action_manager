#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Action管理系统 - EXE打包脚本
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """检查PyInstaller是否安装"""
    try:
        import PyInstaller
        print("✅ PyInstaller已安装")
        return True
    except ImportError:
        print("❌ PyInstaller未安装")
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ PyInstaller安装失败")
        return False

def create_spec_file():
    """创建PyInstaller spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),
        ('requirements.txt', '.'),
        ('README.md', '.'),
        ('TROUBLESHOOTING.md', '.'),
        ('FIXES.md', '.'),
        ('PROJECT_STRUCTURE.md', '.')
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'requests',
        'PyGithub',
        'cryptography',
        'sqlite3',
        'json',
        'logging',
        'datetime',
        'urllib.request',
        'urllib.error'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GitHub Action Manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version_file=None,
)
'''
    
    with open('github_action_manager.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ spec文件创建成功")

def build_exe():
    """构建exe文件"""
    print("开始构建exe文件...")
    
    try:
        # 使用spec文件构建
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "github_action_manager.spec"
        ])
        
        print("✅ exe文件构建成功!")
        
        # 检查输出文件
        dist_dir = Path("dist")
        exe_file = dist_dir / "GitHub Action Manager.exe"
        
        if exe_file.exists():
            print(f"✅ 可执行文件位置: {exe_file.absolute()}")
            
            # 创建README文件
            readme_content = """GitHub Action管理系统

使用说明:
1. 双击运行 "GitHub Action Manager.exe"
2. 首次运行会在程序目录下创建数据库文件
3. 在"用户管理"标签页中添加您的GitHub Token
4. 在"工作流管理"标签页中配置和触发工作流

注意事项:
- 程序会自动创建数据库和日志文件
- 请妥善保管您的GitHub Token
- 建议定期备份配置文件

技术支持:
如有问题，请查看程序日志文件。
"""
            
            with open(dist_dir / "README.txt", 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            print("✅ README文件已创建")
            
            return True
        else:
            print("❌ exe文件未找到")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 构建过程中发生错误: {e}")
        return False

def clean_build_files():
    """清理构建文件"""
    print("清理构建文件...")
    
    files_to_clean = [
        "github_action_manager.spec",
        "build",
        "__pycache__"
    ]
    
    for item in files_to_clean:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)
            print(f"✅ 已删除: {item}")

def main():
    """主函数"""
    print("🔧 GitHub Action管理系统 - EXE打包工具")
    print("=" * 60)
    
    # 检查PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("❌ 无法安装PyInstaller，打包失败")
            return False
    
    # 检查主程序文件
    if not os.path.exists("main.py"):
        print("❌ 未找到main.py文件")
        return False
    
    print("✅ 所有检查通过，开始打包...")
    
    # 创建spec文件
    create_spec_file()
    
    # 构建exe
    if build_exe():
        print("\n🎉 打包完成！")
        print("\n可执行文件位置:")
        print("  dist/GitHub Action Manager.exe")
        print("\n使用说明:")
        print("1. 将整个dist目录复制到目标机器")
        print("2. 双击运行exe文件")
        print("3. 程序会自动创建必要的文件")
        
        # 清理构建文件
        clean_build_files()
        
        return True
    else:
        print("\n❌ 打包失败")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n打包被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n打包过程中发生错误: {e}")
        sys.exit(1) 