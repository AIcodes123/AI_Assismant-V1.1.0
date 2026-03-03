#!/usr/bin/env python3
"""
修复PyQt5安装问题
"""
import sys
import subprocess
import os


def run_command(cmd):
    """运行命令"""
    print(f"执行: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✓ 成功: {result.stdout}")
        return True
    else:
        print(f"✗ 失败: {result.stderr}")
        return False


def fix_pyqt5():
    """修复PyQt5问题"""
    print("=" * 60)
    print("修复PyQt5安装问题")
    print("=" * 60)

    # 1. 检查当前Python
    print(f"\nPython路径: {sys.executable}")
    print(f"Python版本: {sys.version}")

    # 2. 卸载有问题的PyQt5
    print("\n1. 卸载有问题的PyQt5...")
    packages = ["PyQt5", "PyQt5-sip", "PyQt5-tools", "pyqt5", "pyqt5-sip"]
    for pkg in packages:
        run_command(f"{sys.executable} -m pip uninstall {pkg} -y")

    # 3. 清理pip缓存
    print("\n2. 清理pip缓存...")
    run_command(f"{sys.executable} -m pip cache purge")

    # 4. 安装正确版本
    print("\n3. 安装PyQt5...")
    # 尝试不同版本
    versions = [
        "PyQt5==5.15.10",
        "PyQt5-sip==12.13.0",
        "PyQt5==5.15.9",
        "PyQt5-sip==12.12.0"
    ]

    for version in versions:
        if run_command(f"{sys.executable} -m pip install {version}"):
            break

    # 5. 安装其他依赖
    print("\n4. 安装其他依赖...")
    deps = ["tqdm", "pillow"]
    for dep in deps:
        run_command(f"{sys.executable} -m pip install {dep}")

    # 6. 测试安装
    print("\n5. 测试安装...")
    try:
        from PyQt5.QtCore import QT_VERSION_STR
        print(f"✓ PyQt5测试通过，版本: {QT_VERSION_STR}")

        from PyQt5.QtWidgets import QApplication
        print(f"✓ QApplication测试通过")

        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def install_optional():
    """安装可选依赖"""
    print("\n" + "=" * 60)
    print("安装可选依赖 (用于图片生成)")
    print("=" * 60)

    optional_deps = [
        "torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
        "diffusers",
        "transformers",
        "accelerate"
    ]

    for dep in optional_deps:
        print(f"\n安装: {dep}")
        run_command(f"{sys.executable} -m pip install {dep}")


def main():
    """主函数"""
    print("PyQt5修复工具")
    print("-" * 60)

    # 询问用户要做什么
    print("选择操作:")
    print("1. 修复PyQt5问题")
    print("2. 安装所有依赖 (包括可选)")
    print("3. 仅测试当前环境")
    print("4. 退出")

    choice = input("\n请输入选择 (1-4): ").strip()

    if choice == "1":
        if fix_pyqt5():
            print("\n✅ PyQt5修复完成！")
        else:
            print("\n❌ PyQt5修复失败")
    elif choice == "2":
        fix_pyqt5()
        install_optional()
        print("\n✅ 所有依赖安装完成！")
    elif choice == "3":
        test_environment()
    elif choice == "4":
        print("退出")
        return
    else:
        print("无效选择")

    input("\n按回车键退出...")


def test_environment():
    """测试环境"""
    print("\n" + "=" * 60)
    print("环境测试")
    print("=" * 60)

    tests = [
        ("PyQt5", "from PyQt5.QtCore import QT_VERSION_STR"),
        ("tqdm", "import tqdm"),
        ("Pillow", "from PIL import Image"),
        ("torch", "import torch"),
        ("diffusers", "import diffusers"),
        ("transformers", "import transformers")
    ]

    for name, code in tests:
        try:
            exec(code)
            print(f"✓ {name}: 正常")
        except ImportError:
            print(f"✗ {name}: 未安装")
        except Exception as e:
            print(f"⚠ {name}: 错误 ({e})")


if __name__ == "__main__":
    main()