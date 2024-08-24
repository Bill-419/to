from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget, \
    QCheckBox, \
    QDialog, QDialogButtonBox, QScrollArea, QHBoxLayout, QLabel, QLineEdit
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt


class TableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.table_widget = QTableWidget()
        self.checked_rows_per_column = {}  # 保存每列勾选的行号
        self.checkboxes = {}  # 存储复选框和行号的映射关系
        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        self.setLayout(layout)

    def populate_table(self, table_data, merged_cells):
        table = self.table_widget
        table.clearContents()
        table.setRowCount(len(table_data))  # 数据行数
        table.setColumnCount(max(len(row) for row in table_data) if table_data else 0)

        # 初始化保存勾选的行数据
        self.checked_rows_per_column = {col: set(range(1, len(table_data))) for col in range(table.columnCount())}

        # 添加按钮行
        for col_idx in range(table.columnCount()):
            if table_data:
                # 获取第一行的文本内容及其格式
                first_row_item = table_data[0].get(str(col_idx))
                if first_row_item:
                    button_text = first_row_item['text']
                    button_font = QFont()
                    button_font.setBold(first_row_item['font']['bold'])
                    button_font.setPointSize(first_row_item['font']['size'])

                    button = QPushButton(button_text)
                    button.setFont(button_font)
                    button.setStyleSheet(
                        f"color: {first_row_item['foreground']}; background-color: {first_row_item['background']};")
                    button.clicked.connect(lambda checked, idx=col_idx: self.show_checkboxes(idx))
                    table.setCellWidget(0, col_idx, button)

                    # 设置按钮单元格的高度和宽度
                    table.setRowHeight(0, first_row_item['row_height'])
                    table.setColumnWidth(col_idx, first_row_item['column_width'])

        for row_idx, row_data in enumerate(table_data[1:], start=1):  # 跳过第一行数据
            for col_idx_str, cell_data in row_data.items():
                col_idx = int(col_idx_str)
                item = QTableWidgetItem(cell_data['text'])
                item.setForeground(QColor(cell_data['foreground']))
                item.setBackground(QColor(cell_data['background']))
                item.setTextAlignment(Qt.AlignmentFlag(cell_data['alignment']))  # 使用AlignmentFlag设置对齐方式
                font = QFont()
                font.setBold(cell_data['font']['bold'])
                font.setPointSize(cell_data['font']['size'])
                item.setFont(font)
                table.setItem(row_idx, col_idx, item)
                table.setRowHeight(row_idx, cell_data['row_height'])
                table.setColumnWidth(col_idx, cell_data['column_width'])

        # 处理合并单元格
        for cell in merged_cells:
            table.setSpan(cell['row'], cell['col'], cell['row_span'], cell['col_span'])

        # 初次加载后更新显示
        self.update_table_visibility()

    def show_checkboxes(self, col_idx):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Select items from Column {col_idx}")
        # 创建一个搜索栏############################################
        search_bar = QLineEdit(dialog)
        search_bar.setPlaceholderText("Search...")
        # 创建一个搜索栏############################################
        # 创建一个滚动区域
        scroll_area = QScrollArea(dialog)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumWidth(300)  # 设置最小宽度
        scroll_area.setFixedHeight(100)  # 设置固定高度以显示滚动条
        # 创建一个容器和布局来存放复选框
        container = QWidget()
        layout = QVBoxLayout(container)
        checkboxes = []
        table = self.table_widget
        checked_rows = self.checked_rows_per_column.get(col_idx, set())
        content_to_rows = {}  # 内容到行号集合的映射
        for row_idx in range(1, table.rowCount()):  # 跳过第一行按钮行
            item = table.item(row_idx, col_idx)
            if item:
                content = item.text()
                if content not in content_to_rows:
                    content_to_rows[content] = []
                content_to_rows[content].append(row_idx)
        for content, rows in content_to_rows.items():
            # 复选框的选中状态取决于所有对应行是否被选中
            checkbox = QCheckBox(content)
            checkbox.setChecked(all(row in checked_rows for row in rows))
            layout.addWidget(checkbox)
            checkboxes.append((rows, checkbox))
        container.setLayout(layout)
        scroll_area.setWidget(container)
        dialog_layout = QVBoxLayout(dialog)
        # 创建一个搜索栏############################################
        dialog_layout.addWidget(search_bar)
        # 创建一个搜索栏############################################
        dialog_layout.addWidget(scroll_area)
        dialog_buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        dialog_buttons.accepted.connect(lambda: self.show_selected(dialog, col_idx, checkboxes))
        dialog_buttons.rejected.connect(dialog.reject)
        dialog_layout.addWidget(dialog_buttons)
        dialog.setLayout(dialog_layout)
        # 创建一个搜索栏############################################
        # 添加搜索栏的逻辑
        def filter_checkboxes(text):
            for rows, checkbox in checkboxes:
                checkbox.setVisible(text.lower() in checkbox.text().lower())
        search_bar.textChanged.connect(filter_checkboxes)
        # 创建一个搜索栏############################################
        dialog.exec()

    def show_selected(self, dialog, col_idx, checkboxes):
        checked_rows = set()
        for rows, cb in checkboxes:
            if cb.isChecked():
                checked_rows.update(rows)
        print(f"Column {col_idx} selected rows: {checked_rows}")  # 调试输出
        self.checked_rows_per_column[col_idx] = checked_rows
        dialog.accept()
        self.update_table_visibility()

    def update_table_visibility(self):
        table = self.table_widget
        total_rows = table.rowCount()

        # 初始化行显示状态
        rows_visibility = [True] * total_rows

        # 标记是否有任意列的复选框被勾选
        any_column_checked = False

        # 按列组合筛选
        for col_idx, checked_rows in self.checked_rows_per_column.items():
            if checked_rows:  # 仅当有勾选项时才筛选
                any_column_checked = True
                for row_idx in range(1, total_rows):
                    # 如果该行未在checked_rows中，设为False表示隐藏
                    if row_idx not in checked_rows:
                        rows_visibility[row_idx] = False

        print(f"Rows visibility: {rows_visibility}")  # 调试输出

        # 更新行的可见性
        for row_idx in range(1, total_rows):
            table.setRowHidden(row_idx, not rows_visibility[row_idx])

    # 更新复选框状态的方法（可在需要时调用）
    def update_checkbox_states(self):
        for (row_idx, col_idx), checkbox in self.checkboxes.items():
            checkbox.setChecked(row_idx in self.checked_rows_per_column.get(col_idx, set()))


# 示例主程序
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main_window = TableWidget()
    main_window.populate_table([{'0': {'text': '11111 1111', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100},
                                 '1': {'text': '22222222222222222222222222222222222222222222222222222', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100},
                                 '2': {'text': '3', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100},
                                 '3': {'text': '4', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100}},
                                {'0': {'text': '3', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100},
                                 '1': {'text': '4', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100},
                                 '2': {'text': '5', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100},
                                 '3': {'text': '644444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100}},
                                {'0': {'text': '4', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100},
                                 '1': {'text': '5', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100},
                                 '2': {'text': '6', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100},
                                 '3': {'text': '7', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100}}],
                               merged_cells=[])
    main_window.show()
    sys.exit(app.exec())
