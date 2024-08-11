from PySide6.QtWidgets import (
    QDialog, QFormLayout, QTextEdit, QPushButton, QMessageBox, QSizePolicy,
    QApplication, QWidget, QScrollArea, QVBoxLayout, QLabel, QGridLayout, QHBoxLayout
)
from PySide6.QtCore import Qt

class AutoResizingTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initial_height = 30  # 初始高度
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(self.initial_height)  # 设置初始高度
        self.textChanged.connect(self.adjust_height)

    def adjust_height(self):
        doc_height = self.document().size().height()
        new_height = max(self.initial_height, doc_height + 10)  # 高度至少为初始高度
        self.setFixedHeight(new_height)  # 根据文档内容调整高度

class DataDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("填充数据")
        self.setFixedSize(400, 600)  # 设置对话框固定大小

        # 创建滚动区域
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        # 滚动区域内容
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)

        # 创建网格布局
        self.layout = QGridLayout(content_widget)

        self.fields = {}
        labels = ["标题", "标题详情", "代码合入版本", "RN呈现点", "写作人信息", "问题单号", "问题描述", "严重级别", "根因分析", "解决方案", "修改影响", "涉及制式", "涉及网元"]
        for i, label in enumerate(labels):
            label_widget = QLabel(f"{label}:", self)
            label_widget.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # 标签左对齐
            text_edit = AutoResizingTextEdit(self)
            self.fields[label] = text_edit
            self.layout.addWidget(label_widget, i, 0)
            self.layout.addWidget(text_edit, i, 1)

        # 创建保存按钮区域
        save_button_layout = QHBoxLayout()
        self.save_button = QPushButton("保存", self)
        save_button_layout.addStretch()  # 添加伸展项将按钮推到中间
        save_button_layout.addWidget(self.save_button)
        save_button_layout.addStretch()  # 添加伸展项将按钮推到中间
        self.save_button.clicked.connect(self.accept)

        # 添加滚动区和按钮区到主布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        main_layout.addLayout(save_button_layout)

        self.setLayout(main_layout)

        if data:
            for key, value in data.items():
                if key in self.fields:
                    self.fields[key].setPlainText(value)

    def get_data(self):
        data = {key: field.toPlainText() for key, field in self.fields.items()}
        return data

    def accept(self):
        data = self.get_data()
        if self.validate_data(data):
            super().accept()

    def validate_data(self, data):
        missing_fields = []
        if not data.get('问题单号'):
            missing_fields.append('问题单号')
        if not data.get('问题描述'):
            missing_fields.append('问题描述')
        if missing_fields:
            QMessageBox.warning(self, '缺少信息', f"请填写以下必填字段: {', '.join(missing_fields)}")
            return False
        return True

if __name__ == "__main__":
    app = QApplication([])
    dialog = DataDialog()
    dialog.exec()
