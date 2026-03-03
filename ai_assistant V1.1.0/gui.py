"""
GUI界面 - PyQt5实现
"""
import sys
import json
import threading
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class AIAssistantApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.chat_history = []
        self.is_processing = False
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("AI助手")
        self.setGeometry(100, 100, 850, 650)

        # 中央部件
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)

        # 1. 顶部按钮栏
        toolbar = self.create_toolbar()
        layout.addLayout(toolbar)

        # 2. 聊天显示区
        self.chat_display = QTextEdit()
        self.setup_chat_display()
        layout.addWidget(self.chat_display, 7)  # 70%高度

        # 3. 输入区
        input_section = self.create_input_section()
        layout.addLayout(input_section)

        # 4. 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

        # 5. 设置样式
        self.set_style()

    def create_toolbar(self):
        """创建工具栏"""
        layout = QHBoxLayout()

        buttons = [
            ("🚀 发送", self.send_message, "Ctrl+Return"),
            ("🗑️ 清空", self.clear_input, None),
            ("🔍 搜索", self.toggle_search, None),
            ("🖼️ 图片", self.make_image, None),
            ("💾 保存", self.save_chat, "Ctrl+S"),
            ("⚙️ 设置", self.open_settings, None)
        ]

        for text, slot, shortcut in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            if shortcut:
                btn.setShortcut(shortcut)
            btn.setMinimumHeight(35)
            layout.addWidget(btn)

        return layout

    def setup_chat_display(self):
        """设置聊天显示"""
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("微软雅黑", 10))
        self.chat_display.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px;
                background-color: #fafafa;
            }
        """)

    def create_input_section(self):
        """创建输入区域"""
        layout = QVBoxLayout()

        # 输入框
        self.input_box = QTextEdit()
        self.input_box.setMaximumHeight(90)
        self.input_box.setPlaceholderText("输入您的问题... (Ctrl+Enter发送，Enter换行)")
        self.input_box.setFont(QFont("微软雅黑", 10))
        self.input_box.setStyleSheet("""
            QTextEdit {
                border: 2px solid #4CAF50;
                border-radius: 6px;
                padding: 10px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #2196F3;
            }
        """)
        layout.addWidget(self.input_box)

        # 提示标签
        tip = QLabel("💡 支持多行输入、复制粘贴、上下文对话、图片生成")
        tip.setStyleSheet("color: #666; font-size: 12px; padding-left: 5px;")
        layout.addWidget(tip)

        return layout

    def set_style(self):
        """设置样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 6px;
                border: 1px solid #ccc;
                background-color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e8f5e8;
                border-color: #4CAF50;
            }
            QPushButton:pressed {
                background-color: #c8e6c9;
            }
        """)

    def send_message(self):
        """发送消息"""
        text = self.input_box.toPlainText().strip()
        if not text:
            self.status_bar.showMessage("请输入内容")
            return

        # 显示用户消息
        self.add_message("user", text)
        self.input_box.clear()

        # 处理消息
        self.process_message(text)

    def process_message(self, text):
        """处理消息"""
        self.is_processing = True
        self.status_bar.showMessage("思考中...")

        # 在新线程中处理
        thread = threading.Thread(target=self._process_in_thread, args=(text,))
        thread.daemon = True
        thread.start()

    def _process_in_thread(self, text):
        """线程中处理"""
        try:
            # 导入AI核心
            from ai_core import AIBrain

            # 获取上下文
            context = self.chat_history[-5:] if len(self.chat_history) > 5 else self.chat_history

            # 思考
            brain = AIBrain()
            response = brain.think(text, context)

            # 更新界面
            self.add_message("ai", response)

            # 保存历史
            self.chat_history.append({"role": "user", "content": text})
            self.chat_history.append({"role": "ai", "content": response})

            # 自动保存
            if len(self.chat_history) % 4 == 0:
                self.auto_save()

        except Exception as e:
            error_msg = f"处理出错: {str(e)}"
            self.add_message("ai", error_msg)
        finally:
            self.is_processing = False
            self.status_bar.showMessage("就绪")

    def add_message(self, role, content):
        """添加消息到聊天"""
        timestamp = datetime.now().strftime("%H:%M")

        if role == "user":
            color = "#E3F2FD"
            icon = "👤"
            name = "您"
        else:
            color = "#F1F8E9"
            icon = "🤖"
            name = "AI助手"

        # 创建HTML
        html = f"""
        <div style="margin: 10px 5px; padding: 12px; 
                    background: {color}; border-radius: 10px;
                    border: 1px solid #ddd; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <div style="font-weight: bold; color: #333; margin-bottom: 6px;">
                {icon} {name} <span style="color: #666; font-size: 12px;">[{timestamp}]</span>
            </div>
            <div style="color: #222; line-height: 1.5; font-size: 13px;">
                {content.replace('\n', '<br>')}
            </div>
        </div>
        """

        # 线程安全更新
        QMetaObject.invokeMethod(self, "_append_html",
                                 Qt.QueuedConnection,
                                 Q_ARG(str, html))

    @pyqtSlot(str)
    def _append_html(self, html):
        """添加HTML到显示区"""
        self.chat_display.append(html)
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_display.setTextCursor(cursor)

    def clear_input(self):
        """清空输入框"""
        self.input_box.clear()
        self.status_bar.showMessage("输入框已清空")

    def toggle_search(self):
        """切换搜索功能"""
        try:
            from search import toggle_search
            enabled = toggle_search()
            msg = f"搜索功能已{'开启' if enabled else '关闭'}"
            self.status_bar.showMessage(msg)
            QMessageBox.information(self, "搜索设置", msg)
        except Exception as e:
            self.status_bar.showMessage(f"搜索错误: {str(e)}")

    def make_image(self):
        """生成图片"""
        # 获取描述
        text = self.input_box.toPlainText().strip()
        if not text:
            # 尝试使用最后一条消息
            for msg in reversed(self.chat_history):
                if msg["role"] == "user":
                    text = msg["content"]
                    break

        if not text:
            QMessageBox.warning(self, "提示", "请输入图片描述")
            return

        # 确认描述
        desc, ok = QInputDialog.getText(
            self, "生成图片",
            "请输入图片描述:",
            QLineEdit.Normal, text[:80]
        )

        if not ok or not desc.strip():
            return

        # 显示进度对话框
        progress = QProgressDialog("正在生成图片...", "取消", 0, 100, self)
        progress.setWindowTitle("图片生成")
        progress.setWindowModality(Qt.WindowModal)
        progress.setValue(0)
        progress.show()

        # 在新线程中生成
        def generate():
            try:
                from image_gen import create_image
                result = create_image(desc, 408, 408)

                # 关闭进度条
                QMetaObject.invokeMethod(progress, "close", Qt.QueuedConnection)

                # 显示结果
                self.add_message("ai", f"🖼️ 图片生成结果:\n{result}")
                self.status_bar.showMessage("图片生成完成")

            except Exception as e:
                QMetaObject.invokeMethod(progress, "close", Qt.QueuedConnection)
                self.add_message("ai", f"❌ 图片生成失败: {str(e)}")

        thread = threading.Thread(target=generate)
        thread.daemon = True
        thread.start()

        # 模拟进度更新
        for i in range(101):
            if progress.wasCanceled():
                break
            progress.setValue(i)
            QThread.msleep(30)

    def save_chat(self):
        """保存对话"""
        if not self.chat_history:
            QMessageBox.warning(self, "提示", "没有可保存的对话")
            return

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"saved_chats/chat_{timestamp}.json"

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.chat_history, f, indent=2, ensure_ascii=False)

            self.status_bar.showMessage(f"已保存: {filename}")
            QMessageBox.information(self, "成功", f"对话已保存!\n{filename}")

        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存失败: {str(e)}")

    def auto_save(self):
        """自动保存"""
        try:
            with open("history.json", "w", encoding="utf-8") as f:
                json.dump(self.chat_history, f, indent=2, ensure_ascii=False)
        except:
            pass

    def open_settings(self):
        """打开设置"""
        dialog = QDialog(self)
        dialog.setWindowTitle("设置")
        dialog.setFixedSize(350, 250)

        layout = QVBoxLayout()

        # 上下文大小
        ctx_box = QSpinBox()
        ctx_box.setRange(5, 50)
        ctx_box.setValue(10)
        ctx_box.setSuffix(" 条消息")

        ctx_layout = QHBoxLayout()
        ctx_layout.addWidget(QLabel("上下文记忆:"))
        ctx_layout.addWidget(ctx_box)
        layout.addLayout(ctx_layout)

        # 自动保存
        auto_save = QCheckBox("自动保存对话")
        auto_save.setChecked(True)
        layout.addWidget(auto_save)

        # 启用图片生成
        enable_img = QCheckBox("启用图片生成")
        enable_img.setChecked(True)
        layout.addWidget(enable_img)

        # 启用搜索
        enable_search = QCheckBox("启用网络搜索")
        enable_search.setChecked(True)
        layout.addWidget(enable_search)

        layout.addStretch()

        # 按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")

        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)

        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            # 保存设置
            settings = {
                "context_size": ctx_box.value(),
                "auto_save": auto_save.isChecked(),
                "enable_image": enable_img.isChecked(),
                "enable_search": enable_search.isChecked()
            }

            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)

            self.status_bar.showMessage("设置已保存")

    def load_data(self):
        """加载数据"""
        # 加载历史
        try:
            with open("history.json", "r", encoding="utf-8") as f:
                self.chat_history = json.load(f)

            # 显示最近的消息
            for msg in self.chat_history[-20:]:
                self.add_message(msg["role"], msg["content"])

        except FileNotFoundError:
            self.chat_history = []
        except Exception as e:
            print(f"加载历史失败: {e}")
            self.chat_history = []

    def closeEvent(self, event):
        """关闭事件"""
        self.auto_save()
        event.accept()


def main():
    """启动GUI"""
    app = QApplication(sys.argv)

    # 设置高DPI支持
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    # 创建窗口
    window = AIAssistantApp()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()