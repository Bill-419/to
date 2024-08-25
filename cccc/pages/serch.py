from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, \
    QApplication, QPushButton, QLineEdit, QDialog, QLabel, QHBoxLayout, QTabWidget
from PySide6.QtGui import QColor, QShortcut, QKeySequence
from PySide6.QtCore import Qt
from function.menu_base import MenuOperations
import re


class SearchTab(QWidget):
    def __init__(self, parent=None):
        super(SearchTab, self).__init__(parent)
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

        self.update_match_count()

    def replace_text(self):
        if not self.table_widget:
            return
        text_to_find = self.search_input.text()
        replace_with = self.replace_input.text()
        current_item = self.table_widget.currentItem()
        if current_item:
            cell_text = current_item.text()
            if text_to_find in cell_text:
                # 只替换匹配部分而不是整个单元格内容
                new_text = cell_text.replace(text_to_find, replace_with)
                current_item.setText(new_text)
            self.find_next()  # 找到并跳转到下一个匹配

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


class MultiColumnSearchTab(QWidget):
    def __init__(self, parent=None):
        super(MultiColumnSearchTab, self).__init__(parent)
        layout = QVBoxLayout(self)

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("{Title = condition}, {Title = condition}, ...")
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
        self.current_row = 1  # 从第二行开始搜索
        self.conditions = []
        self.matched_rows = []  # 存储所有匹配的行

    def set_table_widget(self, table_widget):
        self.table_widget = table_widget

    def multi_column_search(self):
        self.current_row = 1  # 重置行索引，从第二行开始
        self.matched_rows = []  # 重置匹配行
        self.conditions = self.parse_conditions(self.search_input.text())
        if not self.conditions:
            self.match_count_label.setText("No valid search conditions")
            print("No valid search conditions parsed.")
            return
        self.find_all_matches()
        self.find_next()

    def find_all_matches(self):
        """ 找到所有符合条件的行 """
        if not self.table_widget or not self.conditions:
            print("No table widget or conditions are set.")
            return
        row_count = self.table_widget.rowCount()

        # 初始化候选行列表为所有数据行
        candidate_rows = list(range(1, row_count))  # 从第二行开始（跳过标题行）

        for title, condition in self.conditions:
            col = self.get_column_index_by_title(title)
            if col is None:
                print(f"Column with title '{title}' not found.")
                continue  # 如果没有找到该标题对应的列，跳过

            # 筛选符合当前条件的行
            candidate_rows = [row for row in candidate_rows if self.cell_matches(row, col, condition)]

            # 如果没有匹配的行，则提前退出
            if not candidate_rows:
                break

        self.matched_rows = candidate_rows
        self.update_match_count()

    def cell_matches(self, row, col, condition):
        """检查单元格是否匹配条件"""
        item = self.table_widget.item(row, col)
        return item is not None and re.search(condition, item.text())

    def find_next(self):
        """ 找到下一个匹配的行 """
        if not self.matched_rows:
            return
        self.current_row += 1

        if self.current_row >= len(self.matched_rows):
            self.current_row = 1  # 如果到达末尾，重置索引为第二行
        else:
            row = self.matched_rows[self.current_row - 1]  # 注意 -1 因为 current_row 从 1 开始
            self.table_widget.selectRow(row)

    def get_column_index_by_title(self, title):
        """根据第一行的标题名称获取列索引"""
        for col in range(self.table_widget.columnCount()):
            header_item = self.table_widget.item(0, col)  # 第一行作为标题行
            if header_item and header_item.text() == title:
                return col
        print(f"Column '{title}' not found in the table.")
        return None

    def parse_conditions(self, text):
        """解析用户输入的条件，使用 '=' 分隔符"""
        conditions = []
        try:
            # 解析输入格式 {Title = condition}, {Title = condition}, ...
            matches = re.findall(r'\{([^=]+)=\s*([^\}]+)\}', text)
            for match in matches:
                title = match[0].strip()
                condition = match[1].strip()
                conditions.append((title, condition))
        except ValueError:
            print("Error parsing conditions from input.")
            pass
        return conditions

    def update_match_count(self):
        """更新匹配的行数"""
        count = len(self.matched_rows)
        self.match_count_label.setText(f"Rows matching conditions: {count}")


class SearchDialog(QDialog):
    def __init__(self, table_widget, parent=None):
        super(SearchDialog, self).__init__(parent)
        self.setWindowTitle('Search and Replace')
        layout = QVBoxLayout(self)

        # 创建Tab Widget
        self.tab_widget = QTabWidget()
        self.search_tab = SearchTab(self)
        self.search_tab.set_table_widget(table_widget)
        self.multi_column_search_tab = MultiColumnSearchTab(self)
        self.multi_column_search_tab.set_table_widget(table_widget)

        # 添加标签页
        self.tab_widget.addTab(self.search_tab, "Search")
        self.tab_widget.addTab(self.multi_column_search_tab, "Multi-Column Search")

        layout.addWidget(self.tab_widget)

    def show_search_dialog(self):
        self.show()
        self.search_tab.update_match_count()  # 更新搜索标签页的匹配计数


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

        layout.addLayout(button_layout)

        if self.editable:
            self.menu_operations = MenuOperations(self.table, self.editable)
            self.table.cellDoubleClicked.connect(self.menu_operations.on_cell_double_clicked)
            self.table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.table.customContextMenuRequested.connect(self.menu_operations.open_menu)

        # 创建搜索对话框
        self.search_dialog = SearchDialog(self.table, self)

        shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut.activated.connect(self.open_search_dialog)

    def open_search_dialog(self):
        self.search_dialog.show_search_dialog()

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
