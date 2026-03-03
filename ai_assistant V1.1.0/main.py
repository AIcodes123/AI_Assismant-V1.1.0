#!/usr/bin/env python3
"""
AI助手主程序 - 修复版
"""
import sys
import time
import json
import os


def print_header():
    """打印标题"""
    print("=" * 60)
    print("AI助手 - 本地智能助手")
    print("=" * 60)


def check_python_version():
    """检查Python版本"""
    import platform
    print(f"Python版本: {platform.python_version()}")
    print(f"系统平台: {platform.system()} {platform.release()}")
    print(f"工作目录: {os.getcwd()}")
    print("-" * 60)


def simple_check_deps():
    """简单检查依赖"""
    print("检查依赖库...")

    deps_ok = True

    # 检查PyQt5
    try:
        # 直接导入QtCore测试
        from PyQt5.QtCore import QT_VERSION_STR
        print(f"✓ PyQt5 版本: {QT_VERSION_STR}")
    except ImportError:
        print("✗ PyQt5 未安装")
        print("  运行: pip install PyQt5")
        deps_ok = False
    except Exception as e:
        print(f"✗ PyQt5 有问题: {e}")
        print("  尝试: pip uninstall PyQt5 PyQt5-sip -y")
        print("  然后: pip install PyQt5==5.15.10")
        deps_ok = False

    # 检查tqdm
    try:
        import tqdm
        print(f"✓ tqdm 版本: {tqdm.__version__}")
    except ImportError:
        print("✗ tqdm 未安装")
        print("  运行: pip install tqdm")
        deps_ok = False

    # 检查PIL (pillow)
    try:
        from PIL import Image
        print(f"✓ Pillow 版本: {Image.__version__}")
    except ImportError:
        print("✗ Pillow 未安装")
        print("  运行: pip install pillow")
        deps_ok = False

    print("-" * 60)
    return deps_ok


def check_optional_deps():
    """检查可选依赖"""
    print("检查可选依赖...")

    optional_deps = [
        ("torch", "图片生成"),
        ("diffusers", "高级图片生成"),
        ("transformers", "AI模型")
    ]

    for dep, desc in optional_deps:
        try:
            module = __import__(dep)
            version = getattr(module, '__version__', '已安装')
            print(f"  ✓ {dep}: {version} ({desc})")
        except ImportError:
            print(f"  ⚠ {dep}: 未安装 ({desc}功能受限)")
        except Exception:
            print(f"  ⚠ {dep}: 检查失败")

    print("-" * 60)


def create_directories():
    """创建目录"""
    print("创建目录结构...")

    directories = [
        "generated_images",  # 生成的图片
        "saved_chats",  # 保存的对话
        "logs",  # 日志文件
        "models"  # 模型文件
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"  ✓ 创建: {directory}/")
        else:
            print(f"  ✓ 已存在: {directory}/")

    print("-" * 60)


def load_config():
    """加载配置文件"""
    config_file = "config.json"
    default_config = {
        "context_size": 10,
        "auto_save": True,
        "enable_search": True,
        "enable_image": True,
        "image_width": 408,
        "image_height": 408,
        "theme": "light",
        "language": "zh"
    }

    if not os.path.exists(config_file):
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        print("✓ 创建默认配置文件")
    else:
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            print(f"✓ 加载配置文件: {len(config)} 个设置")
        except:
            print("⚠ 配置文件损坏，使用默认值")

    print("-" * 60)
    return True


def simple_progress_bar(total=10):
    """简单的进度条"""
    for i in range(total + 1):
        percent = i * 10
        bar = "█" * i + "░" * (total - i)
        print(f"\r[{bar}] {percent}%", end="", flush=True)
        time.sleep(0.1)
    print()


def start_application():
    """启动应用程序"""
    print("\n启动AI助手...")

    # 显示简单进度
    simple_progress_bar(10)

    try:
        # 导入GUI
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt

        from gui import AIAssistantApp

        # 创建应用
        app = QApplication(sys.argv)
        app.setApplicationName("AI助手")
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)

        # 创建主窗口
        window = AIAssistantApp()
        window.show()

        print("\n" + "=" * 60)
        print("✅ AI助手启动成功！")
        print("=" * 60)
        print("\n使用说明:")
        print("1. 在输入框输入问题")
        print("2. 按 Ctrl+Enter 发送")
        print("3. 使用工具栏按钮切换功能")
        print("4. 对话自动保存")
        print("=" * 60)

        # 运行应用
        sys.exit(app.exec_())

    except ImportError as e:
        print(f"\n❌ 导入失败: {e}")
        print("请确保所有依赖已正确安装")
        input("\n按回车键退出...")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")


def main():
    """主函数"""
    try:
        # 显示标题
        print_header()

        # 检查Python版本
        check_python_version()

        # 检查依赖
        if not simple_check_deps():
            print("❌ 依赖检查失败，请安装缺少的依赖")
            input("\n按回车键退出...")
            return

        # 检查可选依赖
        check_optional_deps()

        # 创建目录
        create_directories()

        # 加载配置
        load_config()

        # 启动应用
        start_application()

    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        input("\n按回车键退出...")


if __name__ == "__main__":
    main()