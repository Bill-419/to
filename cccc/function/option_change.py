from abc import ABC, abstractmethod
from PySide6.QtWidgets import (QTableWidgetItem, QInputDialog, QColorDialog,
                               QMainWindow, QTableWidget, QApplication, QMenu)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


# 策略接口
class TableOperationStrategy(ABC):
    @abstractmethod
    def execute(self, table):
        pass


# 清空单元格策略
class ClearCellsStrategy(TableOperationStrategy):
    def execute(self, table):
        for item in table.selectedItems():
            item.setText("")


# 添加行策略
class AddRowsStrategy(TableOperationStrategy):
    def __init__(self, above=True):
        self.above = above

    def execute(self, table):
        rows = sorted(set(index.row() for index in table.selectedIndexes()))
        count = len(rows)
        insert_at = rows[0] if self.above else rows[-1] + 1
        for _ in range(count):
            table.insertRow(insert_at)
            for column in range(table.columnCount()):
                item = QTableWidgetItem()
                item.setForeground(Qt.black)
                item.setBackground(Qt.white)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                table.setItem(insert_at, column, item)


# 添加列策略
class AddColumnsStrategy(TableOperationStrategy):
    def __init__(self, left=True):
        self.left = left

    def execute(self, table):
        columns = sorted(set(index.column() for index in table.selectedIndexes()))
        count = len(columns)
        insert_at = columns[0] if self.left else columns[-1] + 1
        for _ in range(count):
            table.insertColumn(insert_at)
            for row in range(table.rowCount()):
                item = QTableWidgetItem()
                item.setForeground(Qt.black)
                item.setBackground(Qt.white)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                table.setItem(row, insert_at, item)


# 删除行策略
class DeleteRowsStrategy(TableOperationStrategy):
    def execute(self, table):
        rows = sorted(set(index.row() for index in table.selectedIndexes()), reverse=True)
        for row in rows:
            table.removeRow(row)


# 删除列策略
class DeleteColumnsStrategy(TableOperationStrategy):
    def execute(self, table):
        columns = sorted(set(index.column() for index in table.selectedIndexes()), reverse=True)
        for col in columns:
            table.removeColumn(col)


# 设置单元格颜色策略
class SetCellColorStrategy(TableOperationStrategy):
    def execute(self, table):
        color = QColorDialog.getColor()
        if color.isValid():
            for index in table.selectedIndexes():
                item = table.item(index.row(), index.column())
                if not item:
                    item = QTableWidgetItem()
                    table.setItem(index.row(), index.column(), item)
                item.setBackground(color)


# 设置字体颜色策略
class SetFontColorStrategy(TableOperationStrategy):
    def execute(self, table):
        color = QColorDialog.getColor()
        if color.isValid():
            for index in table.selectedIndexes():
                item = table.item(index.row(), index.column())
                if not item:
                    item = QTableWidgetItem()
                    table.setItem(index.row(), index.column(), item)
                item.setForeground(color)


# 设置行高策略
class SetRowHeightStrategy(TableOperationStrategy):
    def execute(self, table):
        rows = set(index.row() for index in table.selectedIndexes())
        height, ok = QInputDialog.getInt(table, "Set Row Height", "Enter new row height:", 30, 10, 500, 1)
        if ok:
            for row in rows:
                table.setRowHeight(row, height)


# 设置列宽策略
class SetColumnWidthStrategy(TableOperationStrategy):
    def execute(self, table):
        cols = set(index.column() for index in table.selectedIndexes())
        width, ok = QInputDialog.getInt(table, "Set Column Width", "Enter new column width:", 100, 10, 500, 1)
        if ok:
            for col in cols:
                table.setColumnWidth(col, width)


# 设置字体大小策略
class SetFontSizeStrategy(TableOperationStrategy):
    def execute(self, table):
        size, ok = QInputDialog.getInt(table, "Set Font Size", "Enter new font size:", 10, 1, 100, 1)
        if ok:
            for index in table.selectedIndexes():
                item = table.item(index.row(), index.column())
                if item is None:
                    item = QTableWidgetItem()
                    table.setItem(index.row(), index.column(), item)
                widget = table.cellWidget(index.row(), index.column())
                if widget:
                    font = widget.font()
                    font.setPointSize(size)
                    widget.setFont(font)
                else:
                    font = item.font()
                    font.setPointSize(size)
                    item.setFont(font)


# 切换粗体策略
class ToggleBoldStrategy(TableOperationStrategy):
    def execute(self, table):
        for index in table.selectedIndexes():
            item = table.item(index.row(), index.column())
            if item is None:
                item = QTableWidgetItem()
                table.setItem(index.row(), index.column(), item)
            widget = table.cellWidget(index.row(), index.column())
            if widget:
                font = widget.font()
                font.setBold(not font.bold())
                widget.setFont(font)
            else:
                font = item.font()
                font.setBold(not font.bold())
                item.setFont(font)


# 合并单元格策略
class MergeCellsStrategy(TableOperationStrategy):
    def execute(self, table):
        selected_ranges = table.selectedRanges()
        if not selected_ranges:
            return

        top_row = min(selected_range.topRow() for selected_range in selected_ranges)
        bottom_row = max(selected_range.bottomRow() for selected_range in selected_ranges)
        left_col = min(selected_range.leftColumn() for selected_range in selected_ranges)
        right_col = max(selected_range.rightColumn() for selected_range in selected_ranges)

        if bottom_row == top_row and right_col == left_col:
            return

        text = ''
        background_color = QColor("#ffffff")
        font = table.font()
        font_color = QColor("#000000")
        found_non_empty = False
        for col in range(left_col, right_col + 1):
            for row in range(top_row, bottom_row + 1):
                item = table.item(row, col)
                if item and item.text().strip():
                    text = item.text()
                    background_color = item.background().color()
                    font = item.font()
                    font_color = item.foreground().color()
                    if background_color == QColor("#000000") and font_color == QColor("#000000"):
                        background_color = QColor("#ffffff")
                    found_non_empty = True
                    break
            if found_non_empty:
                break

        for row in range(top_row, bottom_row + 1):
            for col in range(left_col, right_col + 1):
                if row == top_row and col == left_col:
                    continue
                item = table.item(row, col)
                if not item:
                    item = QTableWidgetItem()
                    table.setItem(row, col, item)
                item.setText(text)
                item.setBackground(background_color)
                item.setFont(font)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item.setForeground(font_color)

        table.setSpan(top_row, left_col, bottom_row - top_row + 1, right_col - left_col + 1)
        if not table.item(top_row, left_col):
            table.setItem(top_row, left_col, QTableWidgetItem())
        top_left_item = table.item(top_row, left_col)
        top_left_item.setText(text)
        top_left_item.setBackground(background_color)
        top_left_item.setFont(font)
        top_left_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        top_left_item.setForeground(font_color)


# 取消合并单元格策略
class UnmergeCellsStrategy(TableOperationStrategy):
    def execute(self, table):
        selected_ranges = table.selectedRanges()
        if not selected_ranges:
            return

        for selected_range in selected_ranges:
            top_row = selected_range.topRow()
            left_col = selected_range.leftColumn()
            bottom_row = selected_range.bottomRow()
            right_col = selected_range.rightColumn()

            merged_item = table.item(top_row, left_col)
            merged_text = merged_item.text() if merged_item else ''
            background_color = merged_item.background().color() if merged_item else QColor("#ffffff")
            font = merged_item.font() if merged_item else table.font()
            font_color = merged_item.foreground().color() if merged_item else QColor("#000000")

            for row in range(top_row, bottom_row + 1):
                for col in range(left_col, right_col + 1):
                    if table.rowSpan(row, col) > 1 or table.columnSpan(row, col) > 1:
                        table.setSpan(row, col, 1, 1)
                    item = table.item(row, col)
                    if not item:
                        item = QTableWidgetItem()
                        table.setItem(row, col, item)
                    item.setBackground(background_color)
                    item.setFont(font)
                    item.setForeground(font_color)
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                    if row == top_row and col == left_col:
                        item.setText(merged_text)
                    else:
                        item.setText('')


# 设置单元格对齐策略
class AlignCellsStrategy(TableOperationStrategy):
    def __init__(self, horizontal_alignment, vertical_alignment):
        self.horizontal_alignment = horizontal_alignment
        self.vertical_alignment = vertical_alignment

    def execute(self, table):
        for index in table.selectedIndexes():
            item = table.item(index.row(), index.column())
            if not item:
                item = QTableWidgetItem()
                table.setItem(index.row(), index.column(), item)
            item.setTextAlignment(self.horizontal_alignment | self.vertical_alignment)


# 表格操作上下文类
class TableOperations:
    def __init__(self, table):
        self.table = table
        self.current_strategy = None  # 当前策略

    def set_strategy(self, strategy: TableOperationStrategy):
        self.current_strategy = strategy

    def execute_strategy(self):
        if self.current_strategy:
            self.current_strategy.execute(self.table)


# 主窗口类
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Table Operations with Strategy Pattern")
        self.table = QTableWidget(5, 5)  # 默认5行5列
        self.setCentralWidget(self.table)

        self.table_operations = TableOperations(self.table)

        # 创建并设置菜单操作
        self.create_context_menu()

    def create_context_menu(self):
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.open_menu)

    def open_menu(self, position):
        menu = QMenu()
        clear_action = menu.addAction("清空单元格")
        add_row_action = menu.addAction("在上方添加行")
        add_col_action = menu.addAction("在左侧添加列")
        delete_row_action = menu.addAction("删除行")
        delete_col_action = menu.addAction("删除列")
        set_color_action = menu.addAction("设置单元格颜色")
        set_font_color_action = menu.addAction("设置字体颜色")
        set_row_height_action = menu.addAction("设置行高")
        set_col_width_action = menu.addAction("设置列宽")
        set_font_size_action = menu.addAction("设置字体大小")
        toggle_bold_action = menu.addAction("切换加粗")
        merge_cells_action = menu.addAction("合并单元格")
        unmerge_cells_action = menu.addAction("取消合并单元格")

        align_left_action = menu.addAction("左对齐")
        align_center_action = menu.addAction("居中对齐")
        align_right_action = menu.addAction("右对齐")

        action = menu.exec(self.table.viewport().mapToGlobal(position))

        # 根据选择的菜单项设置不同的策略
        if action == clear_action:
            self.table_operations.set_strategy(ClearCellsStrategy())
        elif action == add_row_action:
            self.table_operations.set_strategy(AddRowsStrategy(above=True))
        elif action == add_col_action:
            self.table_operations.set_strategy(AddColumnsStrategy(left=True))
        elif action == delete_row_action:
            self.table_operations.set_strategy(DeleteRowsStrategy())
        elif action == delete_col_action:
            self.table_operations.set_strategy(DeleteColumnsStrategy())
        elif action == set_color_action:
            self.table_operations.set_strategy(SetCellColorStrategy())
        elif action == set_font_color_action:
            self.table_operations.set_strategy(SetFontColorStrategy())
        elif action == set_row_height_action:
            self.table_operations.set_strategy(SetRowHeightStrategy())
        elif action == set_col_width_action:
            self.table_operations.set_strategy(SetColumnWidthStrategy())
        elif action == set_font_size_action:
            self.table_operations.set_strategy(SetFontSizeStrategy())
        elif action == toggle_bold_action:
            self.table_operations.set_strategy(ToggleBoldStrategy())
        elif action == merge_cells_action:
            self.table_operations.set_strategy(MergeCellsStrategy())
        elif action == unmerge_cells_action:
            self.table_operations.set_strategy(UnmergeCellsStrategy())
        elif action == align_left_action:
            self.table_operations.set_strategy(AlignCellsStrategy(Qt.AlignLeft, Qt.AlignVCenter))
        elif action == align_center_action:
            self.table_operations.set_strategy(AlignCellsStrategy(Qt.AlignHCenter, Qt.AlignVCenter))
        elif action == align_right_action:
            self.table_operations.set_strategy(AlignCellsStrategy(Qt.AlignRight, Qt.AlignVCenter))

        # 执行策略
        self.table_operations.execute_strategy()


if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()
