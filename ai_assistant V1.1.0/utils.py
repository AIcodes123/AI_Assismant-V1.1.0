"""
工具函数模块
"""
import json
import os
import time
import hashlib
from datetime import datetime
import shutil


def load_json(filepath, default=None):
    """加载JSON文件"""
    if default is None:
        default = {}

    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载JSON失败 {filepath}: {e}")

    return default


def save_json(data, filepath, indent=2):
    """保存JSON文件"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        return True
    except Exception as e:
        print(f"保存JSON失败 {filepath}: {e}")
        return False


def format_time(t=None, fmt="%H:%M"):
    """格式化时间"""
    if t is None:
        t = datetime.now()
    return t.strftime(fmt)


def file_size(path):
    """获取文件大小（人类可读）"""
    if not os.path.exists(path):
        return "0B"

    size = os.path.getsize(path)

    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0

    return f"{size:.1f}TB"


def ensure_dir(path):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)
    return path


def backup_file(path, suffix=".backup"):
    """备份文件"""
    if not os.path.exists(path):
        return False

    try:
        backup_path = f"{path}{suffix}"
        shutil.copy2(path, backup_path)
        return backup_path
    except Exception as e:
        print(f"备份失败 {path}: {e}")
        return False


def calculate_hash(text):
    """计算文本哈希"""
    return hashlib.md5(text.encode()).hexdigest()[:8]


def clean_old_files(dir_path, pattern="*.json", days=7):
    """清理旧文件"""
    import glob

    if not os.path.exists(dir_path):
        return

    current_time = time.time()
    cutoff = current_time - (days * 24 * 3600)

    for filepath in glob.glob(os.path.join(dir_path, pattern)):
        try:
            if os.path.getmtime(filepath) < cutoff:
                os.remove(filepath)
                print(f"清理: {filepath}")
        except:
            pass


def read_file(path, encoding='utf-8'):
    """读取文件"""
    try:
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        print(f"读取失败 {path}: {e}")
        return ""


def write_file(path, content, encoding='utf-8'):
    """写入文件"""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"写入失败 {path}: {e}")
        return False


def merge_dict(a, b):
    """合并字典"""
    result = a.copy()
    for key, value in b.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dict(result[key], value)
        else:
            result[key] = value
    return result


def filter_empty(items):
    """过滤空值"""
    return [item for item in items if item and str(item).strip()]


def get_system_info():
    """获取系统信息"""
    import platform
    import sys

    return {
        "system": platform.system(),
        "version": platform.version(),
        "python": platform.python_version(),
        "executable": sys.executable,
        "cwd": os.getcwd()
    }


def log_message(msg, level="INFO"):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {msg}"
    print(log_line)

    # 同时写入日志文件
    try:
        log_dir = ensure_dir("logs")
        log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_line + "\n")
    except:
        pass


def time_it(func):
    """计时装饰器"""

    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"⏱️ {func.__name__}: {end - start:.3f}s")
        return result

    return wrapper


def retry(max_attempts=3, delay=1):
    """重试装饰器"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"重试 {func.__name__} ({attempt + 1}/{max_attempts}): {e}")
                    time.sleep(delay)

        return wrapper

    return decorator


def validate_path(path):
    """验证路径"""
    return os.path.exists(path)


def get_file_list(dir_path, pattern="*"):
    """获取文件列表"""
    import glob
    if not os.path.exists(dir_path):
        return []

    return glob.glob(os.path.join(dir_path, pattern))


def human_time(seconds):
    """人类可读时间"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        return f"{seconds / 60:.1f}分钟"
    else:
        return f"{seconds / 3600:.1f}小时"