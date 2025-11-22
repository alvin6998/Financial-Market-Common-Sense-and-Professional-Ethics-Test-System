# Fixed version of 金融市場常識題庫系統.py
# Key fixes:
# - Removed duplicate clear_layout definition & unified into one working version
# - Ensure clear_layout(self.main_layout) is always used
# - Build pages correctly without leaving old widgets

import sys
import json
import random
import time
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QHBoxLayout, QSpinBox, QMessageBox, QScrollArea, QWidgetItem
)
from PyQt6.QtCore import Qt

QUESTION_FILE = "金融市場常識題庫.json"


class QuizApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("金融市場常識題庫系統（PyQt6）")
        self.resize(800, 600)

        # 載入題庫
        try:
            with open(QUESTION_FILE, "r", encoding="utf-8") as f:
                self.question_bank = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入題庫失敗：{e}")
            sys.exit(1)

        # 主 layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # 狀態變數
        self.selected_questions = []
        self.current_index = 0
        self.user_answers = []
        self.start_time = None

        # 建立起始頁面
        self.build_start_page()

    # ---------- utilities ----------
    def clear_layout(self, layout):
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self.clear_layout(child_layout)

    # ---------- start page ----------
    def build_start_page(self):
        self.clear_layout(self.main_layout)

        title = QLabel("金融市場常識題庫系統")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; margin: 12px;")
        self.main_layout.addWidget(title)

        hint = QLabel(f"題庫共 {len(self.question_bank)} 題（JSON）\n請選擇欲作答的題數：")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("font-size: 14px; margin-bottom: 8px;")
        self.main_layout.addWidget(hint)

        h = QHBoxLayout()
        lbl = QLabel("題目數量：")
        lbl.setStyleSheet("font-size: 16px;")
        self.spin = QSpinBox()
        self.spin.setRange(1, len(self.question_bank))
        self.spin.setValue(min(20, len(self.question_bank)))
        self.spin.setStyleSheet("font-size: 16px;")
        h.addStretch()
        h.addWidget(lbl)
        h.addWidget(self.spin)
        h.addStretch()
        self.main_layout.addLayout(h)

        start_btn = QPushButton("開始測驗")
        start_btn.clicked.connect(self.start_quiz)
        start_btn.setStyleSheet("font-size: 18px; padding: 10px;")
        self.main_layout.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    # ---------- start quiz ----------
    def start_quiz(self):
        total = self.spin.value()
        self.selected_questions = random.sample(self.question_bank, total)
        self.current_index = 0
        self.user_answers = [None] * total
        self.start_time = time.time()

        self.clear_layout(self.main_layout)
        self.build_quiz_page()

    # ---------- quiz page ----------
    def build_quiz_page(self):
        self.clear_layout(self.main_layout)

        progress = QLabel(f"第 {self.current_index + 1} / {len(self.selected_questions)} 題")
        progress.setStyleSheet("font-size: 16px;")
        self.main_layout.addWidget(progress)

        q = self.selected_questions[self.current_index]
        q_label = QLabel(q.get("題目", ""))
        q_label.setWordWrap(True)
        q_label.setStyleSheet("font-size: 18px;")
        self.main_layout.addWidget(q_label)

        self.btn_group = QButtonGroup(self)
        self.option_buttons = []

        items = list(q.get("選項", {}).items())
        random.shuffle(items)

        for key, text in items:
            rb = QRadioButton(text)
            rb.setStyleSheet("font-size: 16px;")
            self.btn_group.addButton(rb)
            self.option_buttons.append((rb, str(key)))
            self.main_layout.addWidget(rb)

        prev_val = self.user_answers[self.current_index]
        if prev_val is not None:
            for rb, k in self.option_buttons:
                if k == prev_val:
                    rb.setChecked(True)

        h = QHBoxLayout()
        prev_btn = QPushButton("上一題")
        prev_btn.setEnabled(self.current_index > 0)
        prev_btn.clicked.connect(self.go_previous)
        h.addWidget(prev_btn)

        next_label = "下一題" if self.current_index < len(self.selected_questions) - 1 else "完成測驗"
        next_btn = QPushButton(next_label)
        next_btn.clicked.connect(self.on_next_clicked)
        h.addWidget(next_btn)

        self.main_layout.addLayout(h)

    def on_next_clicked(self):
        selected = None
        for rb, key in self.option_buttons:
            if rb.isChecked():
                selected = key
                break

        if selected is None:
            QMessageBox.warning(self, "尚未作答", "請先選擇一個答案。")
            return

        self.user_answers[self.current_index] = selected

        if self.current_index < len(self.selected_questions) - 1:
            self.current_index += 1
            self.build_quiz_page()
        else:
            self.finish_quiz()

    def go_previous(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.build_quiz_page()

    # ---------- finish ----------
    def finish_quiz(self):
        total_time = int(time.time() - self.start_time)
        correct = 0
        wrongs = []

        for idx, q in enumerate(self.selected_questions):
            correct_key = str(q.get("答案", ""))
            user_key = self.user_answers[idx]

            if user_key == correct_key:
                correct += 1
            else:
                wrongs.append({
                    "題目": q.get("題目", ""),
                    "你的答案_key": user_key,
                    "正確答案_key": correct_key,
                    "你的答案_text": q.get("選項", {}).get(user_key, ""),
                    "正確答案_text": q.get("選項", {}).get(correct_key, "")
                })

        total = len(self.selected_questions)
        rate = correct / total * 100

        self.clear_layout(self.main_layout)

        title = QLabel("測驗結果")
        title.setStyleSheet("font-size: 26px; font-weight: bold;")
        self.main_layout.addWidget(title)

        summary = QLabel(f"總題數：{total}\n答對：{correct}\n正確率：{rate:.2f}%\n作答時間：{total_time} 秒")
        summary.setStyleSheet("font-size: 18px;")
        self.main_layout.addWidget(summary)

        if wrongs:
            wl = QLabel("錯題清單：")
            wl.setStyleSheet("font-size: 18px; color:red;")
            self.main_layout.addWidget(wl)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            container = QWidget()
            v = QVBoxLayout(container)

            for w in wrongs:
                t = QLabel(
                    f"題目：{w['題目']}\n你的答案：{w['你的答案_text']}\n正確答案：{w['正確答案_text']}\n"
                )
                t.setWordWrap(True)
                t.setStyleSheet("font-size: 15px;")
                v.addWidget(t)

            scroll.setWidget(container)
            scroll.setFixedHeight(300)
            self.main_layout.addWidget(scroll)

        h = QHBoxLayout()
        back = QPushButton("返回主選單")
        back.clicked.connect(self.build_start_page)
        h.addWidget(back)

        self.main_layout.addLayout(h)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = QuizApp()
    win.show()
    sys.exit(app.exec())

