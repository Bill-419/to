from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget, QCheckBox, QDialog, QDialogButtonBox
from PyQt5.QtGui import QColor, QFont

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
        table.setRowCount(len(table_data) + 1)  # 增加一行用于按钮
        table.setColumnCount(max(len(row) for row in table_data) if table_data else 0)

        # 初始化保存勾选的行数据
        self.checked_rows_per_column = {col: set(range(1, len(table_data) + 1)) for col in range(table.columnCount())}

        # 添加按钮行
        for col_idx in range(table.columnCount()):
            button = QPushButton("筛选")
            button.clicked.connect(lambda checked, idx=col_idx: self.show_checkboxes(idx))
            table.setCellWidget(0, col_idx, button)

        # 填充数据
        for row_idx, row_data in enumerate(table_data, start=1):
            for col_idx_str, cell_data in row_data.items():
                col_idx = int(col_idx_str)
                item = QTableWidgetItem(cell_data['text'])
                item.setForeground(QColor(cell_data['foreground']))
                item.setBackground(QColor(cell_data['background']))
                item.setTextAlignment(cell_data['alignment'])
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
        layout = QVBoxLayout()

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

        dialog_buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        dialog_buttons.accepted.connect(lambda: self.show_selected(dialog, col_idx, checkboxes))
        dialog_buttons.rejected.connect(dialog.reject)

        layout.addWidget(dialog_buttons)
        dialog.setLayout(layout)
        dialog.exec_()

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
    main_window.populate_table([{'0': {'text': '1', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100},
                                 '1': {'text': '2', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100},
                                 '2': {'text': '3', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100},
                                 '3': {'text': '4', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100}},
                                {'0': {'text': '3', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100},
                                 '1': {'text': '4', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100},
                                 '2': {'text': '5', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100},
                                 '3': {'text': '6', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100}},
                                {'0': {'text': '4', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100},
                                 '1': {'text': '5', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100},
                                 '2': {'text': '6', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100},
                                 '3': {'text': '7', 'foreground': '#000000', 'background': '#FFFFFF', 'alignment': 1, 'font': {'bold': False, 'size': 12}, 'row_height': 30, 'column_width': 100}}],
                               merged_cells=[])
    main_window.show()
    sys.exit(app.exec_())
