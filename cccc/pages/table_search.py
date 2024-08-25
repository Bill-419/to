from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, \
    QApplication, QPushButton, QLineEdit, QDialog, QLabel, QHBoxLayout
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from function.menu_base import MenuOperations
import re


class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super(SearchDialog, self).__init__(parent)
        self.setWindowTitle('Search and Replace')
        layout = QVBoxLayout(self)

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search...")
        layout.addWidget(self.search_input)

        self.replace_input = QLineEdit(self)
        self.replace_input.setPlaceholderText("Replace with...")
        layout.addWidget(self.replace_input)

        self.next_button = QPushButton("Next", self)
        self.next_button.clicked.connect(self.find_next)
        layout.addWidget(self.next_button)

        self.replace_button = QPushButton("Replace", self)
        self.replace_button.clicked.connect(self.replace_text)
        layout.addWidget(self.replace_button)

        self.match_count_label = QLabel(self)
        layout.addWidget(self.match_count_label)

        self.table_widget = None
        self.current_index = -1

    def set_table_widget(self, table_widget):
        self.table_widget = table_widget

    def find_next(self):
        if not self.table_widget:
            return
        text_to_find = self.search_input.text()
        row_count = self.table_widget.rowCount()
        col_count = self.table_widget.columnCount()
        self.current_index += 1
        found = False

        for i in range(max(self.current_index, col_count), row_count * col_count):
            row = i // col_count
            col = i % col_count
            if row == 0:  # 跳过第一行标题
                continue
            item = self.table_widget.item(row, col)
            if item and text_to_find in item.text():
                self.table_widget.setCurrentCell(row, col)
                self.current_index = i
                found = True
                break

        if not found:
            self.current_index = -1

        self.update_match_count()  # 更新匹配计数

    def replace_text(self):
        if not self.table_widget:
            return
        replace_with = self.replace_input.text()
        current_item = self.table_widget.currentItem()
        if current_item:
            current_item.setText(replace_with)
            self.find_next()

    def update_match_count(self):
        if not self.table_widget:
            return
        text_to_find = self.search_input.text()
        row_count = self.table_widget.rowCount()
        col_count = self.table_widget.columnCount()
        match_count = 0

        for row in range(1, row_count):  # 从第二行开始
            for col in range(col_count):
                item = self.table_widget.item(row, col)
                if item and text_to_find in item.text():
                    match_count += 1

        self.match_count_label.setText(f"Matches found: {match_count}")


class MultiColumnSearchDialog(QDialog):
    def __init__(self, parent=None):
        super(MultiColumnSearchDialog, self).__init__(parent)
        self.setWindowTitle('Multi-Column Search')
        layout = QVBoxLayout(self)

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("{column: condition}, {column: condition}, ...")
        layout.addWidget(self.search_input)

        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.multi_column_search)
        layout.addWidget(self.search_button)

        self.next_button = QPushButton("Next", self)
        self.next_button.clicked.connect(self.find_next)
        layout.addWidget(self.next_button)

        self.match_count_label = QLabel(self)
        layout.addWidget(self.match_count_label)

        self.table_widget = None
        self.current_row = -1
        self.conditions = []

    def set_table_widget(self, table_widget):
        self.table_widget = table_widget

    def multi_column_search(self):
        self.current_row = 1  # 重置为第二行
        self.conditions = self.parse_conditions(self.search_input.text())
        self.find_next()
        self.update_match_count()  # 搜索后立即更新匹配计数

    def find_next(self):
        if not self.table_widget or not self.conditions:
            return
        row_count = self.table_widget.rowCount()
        self.current_row += 1
        found = False

        for row in range(max(self.current_row, 1), row_count):  # 从第二行开始
            if self.row_matches(row):
                self.table_widget.selectRow(row)
                self.current_row = row
                found = True
                break

        if not found:
            self.current_row = -1

    def row_matches(self, row):
        for col, condition in self.conditions:
            item = self.table_widget.item(row, col)
            if item is None or not re.search(condition, item.text()):
                return False
        return True

    def parse_conditions(self, text):
        conditions = []
        try:
            # 解析输入格式 {1: 1}, {2: 2}
            matches = re.findall(r'\{(\d+):\s*([^\}]+)\}', text)
            for match in matches:
                col = int(match[0].strip()) - 1  # 转换为0索引
                condition = match[1].strip()
                conditions.append((col, condition))
        except ValueError:
            pass
        return conditions

    def update_match_count(self):
        if not self.table_widget or not self.conditions:
            self.match_count_label.setText("Matches found: 0")
            return
        match_count = 0
        row_count = self.table_widget.rowCount()

        for row in range(1, row_count):  # 从第二行开始
            if self.row_matches(row):
                match_count += 1

        self.match_count_label.setText(f"Rows matching conditions: {match_count}")


class TableWidget(QWidget):
    def __init__(self, table=None, editable=False):
        super().__init__()
        self.editable = editable

        if table is None:
            self.table = QTableWidget(6, 8)
            self.items = []
            for row in range(6):
                for col in range(8):
                    item = QTableWidgetItem(f"Item {row + 1},{col + 1}")
                    item.setBackground(QColor("#ffffff"))
                    item.setForeground(QColor("#000000"))
                    self.table.setItem(row, col, item)
                    self.items.append(item)
        else:
            self.table = table

        layout = QVBoxLayout(self)

        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.open_search_dialog)
        button_layout.addWidget(self.search_button)

        self.multi_column_search_button = QPushButton("Multi-Column Search", self)
        self.multi_column_search_button.clicked.connect(self.open_multi_column_search_dialog)
        button_layout.addWidget(self.multi_column_search_button)

        layout.addLayout(button_layout)

        if self.editable:
            self.menu_operations = MenuOperations(self.table, self.editable)
            self.table.cellDoubleClicked.connect(self.menu_operations.on_cell_double_clicked)
            self.table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.table.customContextMenuRequested.connect(self.menu_operations.open_menu)

        self.search_dialog = SearchDialog(self)
        self.search_dialog.set_table_widget(self.table)

        self.multi_column_search_dialog = MultiColumnSearchDialog(self)
        self.multi_column_search_dialog.set_table_widget(self.table)

    def open_search_dialog(self):
        self.search_dialog.show()
        self.search_dialog.update_match_count()  # 打开对话框时更新匹配计数

    def open_multi_column_search_dialog(self):
        self.multi_column_search_dialog.show()

    def get_table(self):
        return self.table

    @staticmethod
    def create_table_widget(editable=False):
        return TableWidget(editable=editable)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    table_widget = TableWidget.create_table_widget(editable=True)
    main_window.setCentralWidget(table_widget)
    main_window.show()
    sys.exit(app.exec())
