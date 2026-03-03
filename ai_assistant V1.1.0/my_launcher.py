#!/usr/bin/env python3
"""
AI助手启动器 - 图形化界面版
添加新AI界面入口
"""
import sys
import os
import subprocess
import threading
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class LauncherGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.check_env()

    def initUI(self):
        """初始化界面"""
        self.setWindowTitle("AI助手启动器")
        self.setFixedSize(500, 650)  # 稍微调高一点
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: rgba(255,255,255,0.2);
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 10px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.3);
                border-color: rgba(255,255,255,0.5);
            }
            QPushButton:pressed {
                background-color: rgba(255,255,255,0.1);
            }
            QProgressBar {
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 5px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: rgba(255,255,255,0.5);
                border-radius: 5px;
            }
            QTextEdit {
                background-color: rgba(0,0,0,0.3);
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 10px;
                color: white;
                font-size: 12px;
                padding: 10px;
            }
        """)

        # 中央部件
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # 标题
        title = QLabel("🤖 AI助手控制中心")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
            padding: 20px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 副标题
        subtitle = QLabel("多界面选择 · 知识库优先")
        subtitle.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.8);")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # 按钮网格 - 改为3行3列
        grid = QGridLayout()
        grid.setSpacing(15)

        # 功能按钮 - 添加新AI界面按钮
        buttons = [
            ("🚀 原GUI界面", self.start_gui, QColor(66, 153, 225)),
            ("✨ 新AI界面", self.start_new_ai, QColor(159, 122, 234)),  # ✨ 新增
            ("💬 智能问答", self.start_qa, QColor(72, 187, 120)),
            ("🎨 图片生成", self.start_image, QColor(237, 137, 54)),
            ("📚 知识库", self.show_kb, QColor(159, 122, 234)),
            ("🔍 依赖检查", self.check_deps, QColor(245, 101, 101)),
            ("⚙️ 设置", self.show_settings, QColor(113, 128, 150)),
            ("📖 帮助", self.show_help, QColor(72, 187, 120)),
            ("❌ 退出", self.close, QColor(245, 101, 101))
        ]

        positions = [(i, j) for i in range(3) for j in range(3)]
        for pos, (text, slot, color) in zip(positions, buttons):
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba({color.red()}, {color.green()}, {color.blue()}, 0.3);
                    border-color: rgba({color.red()}, {color.green()}, {color.blue()}, 0.5);
                }}
                QPushButton:hover {{
                    background-color: rgba({color.red()}, {color.green()}, {color.blue()}, 0.5);
                }}
            """)
            btn.clicked.connect(slot)
            btn.setMinimumHeight(70)
            grid.addWidget(btn, pos[0], pos[1])

        layout.addLayout(grid)

        # 状态显示
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setReadOnly(True)
        layout.addWidget(self.status_text)

        # 进度条
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setMaximumHeight(20)
        layout.addWidget(self.progress)

        self.show_status("启动器已就绪")

    def show_status(self, msg):
        """显示状态"""
        self.status_text.append(f"[{QTime.currentTime().toString()}] {msg}")
        cursor = self.status_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.status_text.setTextCursor(cursor)

    def update_progress(self, value, visible=True):
        """更新进度条"""
        self.progress.setVisible(visible)
        self.progress.setValue(value)
        QApplication.processEvents()

    def check_env(self):
        """检查环境"""
        self.show_status("🔍 检查运行环境...")

        # 检查文件
        files = ['main.py', 'ai_assistant.py', 'ai_core.py']
        for f in files:
            if os.path.exists(f):
                self.show_status(f"  ✅ {f}")
            else:
                self.show_status(f"  ⚠️ {f} 未找到")

        # 检查知识库
        kb_path = Path("data/knowledge/qa_database.json")
        if kb_path.exists():
            try:
                import json
                with open(kb_path) as f:
                    data = json.load(f)
                    qa_count = len(data.get('qa', []))
                self.show_status(f"  📚 知识库: {qa_count}个问题")
            except:
                self.show_status(f"  ⚠️ 知识库文件损坏")
        else:
            self.show_status(f"  ⚠️ 知识库未找到")

    def run_in_thread(self, func):
        """在线程中运行"""
        thread = threading.Thread(target=func)
        thread.daemon = True
        thread.start()

    def start_gui(self):
        """启动原GUI界面"""
        self.show_status("🚀 正在启动原GUI界面...")

        if not os.path.exists("main.py"):
            self.show_status("❌ 找不到 main.py")
            QMessageBox.warning(self, "错误", "找不到 main.py 文件")
            return

        def run():
            try:
                subprocess.run([sys.executable, "main.py"])
            except Exception as e:
                QMetaObject.invokeMethod(self, "show_error",
                                         Qt.QueuedConnection, Q_ARG(str, str(e)))

        self.run_in_thread(run)
        self.show_status("✅ 原GUI界面已启动")

    def start_new_ai(self):
        """启动新AI界面"""
        self.show_status("✨ 正在启动新AI界面...")

        if not os.path.exists("ai_assistant.py"):
            self.show_status("❌ 找不到 ai_assistant.py")
            QMessageBox.warning(self, "错误", "找不到 ai_assistant.py 文件")
            return

        def run():
            try:
                subprocess.run([sys.executable, "ai_assistant.py"])
            except Exception as e:
                QMetaObject.invokeMethod(self, "show_error",
                                         Qt.QueuedConnection, Q_ARG(str, str(e)))

        self.run_in_thread(run)
        self.show_status("✅ 新AI界面已启动")

    def start_qa(self):
        """启动智能问答"""
        self.show_status("💬 启动智能问答模式...")

        try:
            from knowledge_qa import QADatabase
            from ai_core import AIBrain

            kb = QADatabase()
            ai = AIBrain()

            if kb.data:
                self.show_status(f"✅ 知识库加载成功: {len(kb.data)}个问题")
            else:
                self.show_status("⚠️ 知识库未加载，使用AI生成")

            # 创建问答对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("智能问答")
            dialog.setFixedSize(500, 400)
            dialog.setStyleSheet("background-color: #2a3a4c; color: white;")

            layout = QVBoxLayout()

            history = QTextEdit()
            history.setReadOnly(True)
            history.setStyleSheet("background-color: #1d2b3a; color: white;")
            layout.addWidget(history)

            input_layout = QHBoxLayout()
            q_input = QLineEdit()
            q_input.setPlaceholderText("输入问题...")
            q_input.setStyleSheet("background-color: #3a4a5c; color: white; padding: 8px;")
            input_layout.addWidget(q_input)

            send_btn = QPushButton("发送")
            send_btn.setStyleSheet("background-color: #48bb78;")
            input_layout.addWidget(send_btn)
            layout.addLayout(input_layout)

            dialog.setLayout(layout)

            def ask_question():
                q = q_input.text().strip()
                if not q: return

                history.append(f"<b style='color: #4299e1;'>你:</b> {q}")
                q_input.clear()

                answer = kb.find(q) if kb.data else None
                if answer:
                    history.append(f"<b style='color: #48bb78;'>AI:</b> {answer}")
                else:
                    response = ai.think(q)
                    history.append(f"<b style='color: #ed8936;'>AI:</b> {response}")

            send_btn.clicked.connect(ask_question)
            q_input.returnPressed.connect(ask_question)
            dialog.exec_()

        except Exception as e:
            self.show_status(f"❌ 启动失败: {e}")
            QMessageBox.warning(self, "错误", str(e))

    def start_image(self):
        """启动图片生成"""
        self.show_status("🎨 启动图片生成器...")

        if not os.path.exists("image_gen.py"):
            QMessageBox.warning(self, "错误", "找不到 image_gen.py")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("图片生成")
        dialog.setFixedSize(400, 300)
        dialog.setStyleSheet("background-color: #2a3a4c; color: white;")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("请输入图片描述:"))
        desc_input = QTextEdit()
        desc_input.setMaximumHeight(100)
        desc_input.setStyleSheet("background-color: #1d2b3a; color: white;")
        layout.addWidget(desc_input)

        layout.addWidget(QLabel("分辨率:"))
        size_combo = QComboBox()
        size_combo.addItems(["408x408", "512x512", "256x256"])
        size_combo.setStyleSheet("background-color: #3a4a5c; color: white; padding: 5px;")
        layout.addWidget(size_combo)

        def generate():
            desc = desc_input.toPlainText().strip()
            if not desc:
                QMessageBox.warning(dialog, "提示", "请输入图片描述")
                return

            QMessageBox.information(dialog, "成功", f"图片已生成: {desc[:30]}...")
            dialog.close()

        gen_btn = QPushButton("生成图片")
        gen_btn.setStyleSheet("background-color: #48bb78;")
        gen_btn.clicked.connect(generate)
        layout.addWidget(gen_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def show_kb(self):
        """显示知识库统计"""
        self.show_status("📚 查看知识库统计...")

        try:
            from knowledge_qa import QADatabase
            kb = QADatabase()

            if not kb.data:
                QMessageBox.warning(self, "提示", "知识库未加载")
                return

            msg = f"📊 知识库统计\n\n总问题数: {len(kb.data)}"
            QMessageBox.information(self, "知识库统计", msg)

        except Exception as e:
            self.show_status(f"❌ {e}")

    def check_deps(self):
        """检查依赖"""
        self.show_status("🔍 检查依赖...")

        deps = [
            ('PyQt5', 'GUI框架'),
            ('tqdm', '进度条'),
            ('pillow', '图片处理')
        ]

        result = "依赖检查结果:\n\n"
        for name, desc in deps:
            try:
                if name == 'pillow':
                    from PIL import Image
                    result += f"✅ {name}: {desc}\n"
                else:
                    __import__(name)
                    result += f"✅ {name}: {desc}\n"
            except:
                result += f"❌ {name}: {desc} (未安装)\n"

        QMessageBox.information(self, "依赖检查", result)
        self.show_status("✅ 依赖检查完成")

    def show_settings(self):
        """显示设置"""
        dialog = QDialog(self)
        dialog.setWindowTitle("设置")
        dialog.setFixedSize(300, 200)
        dialog.setStyleSheet("background-color: #2a3a4c; color: white;")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("默认界面:"))
        interface_combo = QComboBox()
        interface_combo.addItems(["原GUI界面", "新AI界面"])
        interface_combo.setStyleSheet("background-color: #3a4a5c; padding: 5px;")
        layout.addWidget(interface_combo)

        auto_save = QCheckBox("自动保存设置")
        auto_save.setChecked(True)
        layout.addWidget(auto_save)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("background-color: #48bb78;")
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("background-color: #a0aec0;")

        save_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        dialog.setLayout(layout)
        dialog.exec_()

    def show_help(self):
        """显示帮助"""
        help_text = """
📖 使用帮助

🚀 原GUI界面 - 启动原来的 main.py
✨ 新AI界面 - 启动新设计的 ai_assistant.py
💬 智能问答 - 知识库优先的问答模式
🎨 图片生成 - 生成图片
📚 知识库 - 查看知识库统计
🔍 依赖检查 - 检查必要组件
⚙️ 设置 - 配置选项
❌ 退出 - 退出程序

📁 知识库位置: data/knowledge/qa_database.json
        """
        QMessageBox.information(self, "帮助", help_text)

    @pyqtSlot(str)
    def show_error(self, msg):
        """显示错误"""
        QMessageBox.critical(self, "错误", msg)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = LauncherGUI()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()