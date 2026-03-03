#!/usr/bin/env python3
"""
AI助手 - 美观图形化界面版
整合所有功能，不新增文件
"""
import sys
import os
import json
import random
import threading
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class AIAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.chat_history = []
        self.knowledge = []
        self.initUI()
        self.load_knowledge()

    def initUI(self):
        """初始化美观界面"""
        self.setWindowTitle("🤖 AI智能助手")
        self.setFixedSize(900, 700)

        # 设置全局样式
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2b3a4d, stop:1 #1d2b3a);
            }
            QLabel {
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #3a4a5c;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 13px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a5a6c;
            }
            QPushButton:pressed {
                background-color: #2a3a4c;
            }
            QTextEdit, QLineEdit {
                background-color: #2a3a4c;
                border: 2px solid #3a4a5c;
                border-radius: 10px;
                color: white;
                font-size: 13px;
                padding: 10px;
                selection-background-color: #5a6a7c;
            }
            QTextEdit:focus, QLineEdit:focus {
                border-color: #6a7a8c;
            }
            QScrollBar:vertical {
                background: #2a3a4c;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #5a6a7c;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #6a7a8c;
            }
            QMenuBar {
                background-color: #1d2b3a;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #3a4a5c;
            }
            QMenu {
                background-color: #2a3a4c;
                color: white;
                border: 1px solid #3a4a5c;
            }
            QMenu::item:selected {
                background-color: #3a4a5c;
            }
        """)

        # 中央部件
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ========== 顶部标题栏 ==========
        title_layout = QHBoxLayout()

        title = QLabel("🤖 AI智能助手")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #a0c0ff; padding: 10px;")
        title_layout.addWidget(title)

        title_layout.addStretch()

        # 状态指示器
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("color: #4caf50; font-size: 20px;")
        title_layout.addWidget(self.status_indicator)

        self.status_label = QLabel("在线")
        self.status_label.setStyleSheet("color: #4caf50; font-size: 14px;")
        title_layout.addWidget(self.status_label)

        main_layout.addLayout(title_layout)

        # ========== 功能按钮栏 ==========
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        buttons = [
            ("💬 对话", self.new_chat, "#4299e1"),
            ("🎨 图片", self.generate_image, "#ed8936"),
            ("📚 知识库", self.show_knowledge, "#9f7aea"),
            ("⚙️ 设置", self.show_settings, "#a0aec0"),
            ("🗑️ 清空", self.clear_chat, "#f56565")
        ]

        for text, func, color in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    padding: 10px 20px;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {color}dd;
                }}
            """)
            btn.clicked.connect(func)
            btn_layout.addWidget(btn)

        main_layout.addLayout(btn_layout)

        # ========== 聊天区域 ==========
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: #1d2b3a;
                border: 2px solid #3a4a5c;
                border-radius: 15px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        main_layout.addWidget(self.chat_area, 1)

        # ========== 输入区域 ==========
        input_container = QWidget()
        input_container.setStyleSheet("""
            QWidget {
                background-color: #1d2b3a;
                border-radius: 15px;
                padding: 10px;
            }
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(10, 10, 10, 10)

        self.input_box = QTextEdit()
        self.input_box.setMaximumHeight(80)
        self.input_box.setPlaceholderText("输入您的问题... (Ctrl+Enter发送)")
        self.input_box.setStyleSheet("""
            QTextEdit {
                background-color: #2a3a4c;
                border: 2px solid #4a5a6c;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        input_layout.addWidget(self.input_box, 1)

        send_btn = QPushButton("📤 发送")
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #48bb78;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #38a169;
            }
        """)
        send_btn.clicked.connect(self.send_message)
        send_btn.setShortcut("Ctrl+Return")
        input_layout.addWidget(send_btn)

        main_layout.addWidget(input_container)

        # ========== 状态栏 ==========
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #1d2b3a;
                color: #a0aec0;
                border-top: 1px solid #3a4a5c;
            }
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

        # 显示欢迎消息
        self.add_message("system", "你好！我是AI助手，有什么可以帮你的？")

    def load_knowledge(self):
        """加载知识库"""
        try:
            kb_path = Path("data/knowledge/qa_database.json")
            if kb_path.exists():
                with open(kb_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.knowledge = data.get('qa', [])
                self.status_bar.showMessage(f"知识库加载成功: {len(self.knowledge)}个问题")
        except:
            self.knowledge = []

    def add_message(self, role, content):
        """添加消息到聊天区域"""
        timestamp = QTime.currentTime().toString("hh:mm")

        if role == "user":
            color = "#4299e1"
            name = "你"
            icon = "👤"
        elif role == "system":
            color = "#9f7aea"
            name = "系统"
            icon = "🤖"
        else:
            color = "#48bb78"
            name = "AI"
            icon = "🤖"

        html = f"""
        <div style="margin: 15px 0;">
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <span style="background: {color}; color: white; border-radius: 15px;
                          padding: 5px 15px; font-size: 13px; font-weight: bold;">
                    {icon} {name} · {timestamp}
                </span>
            </div>
            <div style="color: #e0e0e0; padding-left: 15px; border-left: 3px solid {color};">
                {content.replace(chr(10), '<br>')}
            </div>
        </div>
        """

        self.chat_area.append(html)
        self.chat_area.moveCursor(QTextCursor.End)

    def send_message(self):
        """发送消息"""
        text = self.input_box.toPlainText().strip()
        if not text:
            return

        self.add_message("user", text)
        self.input_box.clear()
        self.status_bar.showMessage("思考中...")

        # 在新线程中处理
        thread = threading.Thread(target=self.process_message, args=(text,))
        thread.daemon = True
        thread.start()

    def process_message(self, text):
        """处理消息"""
        # 模拟思考
        QThread.msleep(500)

        # 在知识库中查找
        answer = self.search_knowledge(text)

        if answer:
            result = f"📚 [知识库] {answer}"
        else:
            # AI生成
            responses = [
                f"关于「{text}」，这是一个很好的问题。",
                f"我认为「{text}」涉及多个方面。",
                f"让我想想，「{text}」的核心是...",
                f"从我的角度理解，「{text}」..."
            ]
            result = random.choice(responses) + " (AI生成)"

        # 更新UI
        QMetaObject.invokeMethod(self, "add_message",
                                 Qt.QueuedConnection, Q_ARG(str, "ai"), Q_ARG(str, result))
        QMetaObject.invokeMethod(self.status_bar, "showMessage",
                                 Qt.QueuedConnection, Q_ARG(str, "就绪"))

    def search_knowledge(self, text):
        """在知识库中搜索"""
        text = text.lower()
        for item in self.knowledge:
            if item['q'].lower() in text or text in item['q'].lower():
                return item['a']
        return None

    def new_chat(self):
        """新建对话"""
        self.chat_area.clear()
        self.add_message("system", "你好！我是AI助手，有什么可以帮你的？")
        self.status_bar.showMessage("新对话已开始")

    def generate_image(self):
        """生成图片"""
        desc = self.input_box.toPlainText().strip()
        if not desc:
            QMessageBox.warning(self, "提示", "请输入图片描述")
            return

        # 模拟图片生成
        progress = QProgressDialog("正在生成图片...", "取消", 0, 100, self)
        progress.setWindowTitle("图片生成")
        progress.setWindowModality(Qt.WindowModal)
        progress.show()

        for i in range(101):
            if progress.wasCanceled():
                break
            progress.setValue(i)
            QThread.msleep(10)

        progress.close()

        result = f"✅ 图片已生成！\n描述: {desc}\n分辨率: 408x408"
        self.add_message("ai", f"🖼️ {result}")
        self.status_bar.showMessage("图片生成完成")

    def show_knowledge(self):
        """显示知识库"""
        if not self.knowledge:
            QMessageBox.information(self, "知识库", "知识库为空")
            return

        msg = f"📚 知识库统计\n\n总问题数: {len(self.knowledge)}\n\n"
        for i, item in enumerate(self.knowledge[:10], 1):
            msg += f"{i}. {item['q'][:30]}...\n"

        if len(self.knowledge) > 10:
            msg += f"\n... 还有 {len(self.knowledge) - 10} 个问题"

        QMessageBox.information(self, "知识库", msg)

    def show_settings(self):
        """显示设置"""
        dialog = QDialog(self)
        dialog.setWindowTitle("设置")
        dialog.setFixedSize(350, 250)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2a3a4c;
                color: white;
            }
            QLabel {
                color: white;
            }
            QCheckBox {
                color: white;
            }
            QComboBox {
                background-color: #3a4a5c;
                color: white;
                border: 1px solid #5a6a7c;
                padding: 5px;
            }
            QLineEdit {
                background-color: #3a4a5c;
                color: white;
                border: 1px solid #5a6a7c;
                padding: 5px;
            }
        """)

        layout = QVBoxLayout()

        # 主题选择
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("主题:"))
        theme_combo = QComboBox()
        theme_combo.addItems(["深色", "浅色"])
        theme_layout.addWidget(theme_combo)
        layout.addLayout(theme_layout)

        # 字体大小
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("字体大小:"))
        font_spin = QSpinBox()
        font_spin.setRange(10, 20)
        font_spin.setValue(13)
        font_layout.addWidget(font_spin)
        layout.addLayout(font_layout)

        # 自动保存
        auto_save = QCheckBox("自动保存对话")
        auto_save.setChecked(True)
        layout.addWidget(auto_save)

        # 知识库优先
        kb_first = QCheckBox("知识库优先")
        kb_first.setChecked(True)
        layout.addWidget(kb_first)

        layout.addStretch()

        # 按钮
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

    def clear_chat(self):
        """清空对话"""
        reply = QMessageBox.question(self, "确认", "确定清空所有对话？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.chat_area.clear()
            self.add_message("system", "对话已清空")
            self.status_bar.showMessage("对话已清空")


def main():
    app = QApplication(sys.argv)

    # 设置应用图标
    app.setWindowIcon(QIcon())

    # 创建主窗口
    window = AIAssistant()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()