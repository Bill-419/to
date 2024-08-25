from PySide6.QtWidgets import (QMenu, QTextEdit, QTableWidgetItem, QMainWindow,
                               QVBoxLayout,QColorDialog, QWidget,QInputDialog, QTableWidget, QApplication)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from function.option import TableOperations
class MenuOperations:
    def __init__(self, table, editable=False):
        self.table = table  # 表格对象
        self.table_operations = TableOperations(table)
        self.editable = editable
        # 连接信号和槽
        if self.editable:
            self.table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.table.customContextMenuRequested.connect(self.open_menu)

        # 用于存储原始和编辑后的文本
        self.original_texts = {}
        self.edited_texts = {}

    def add_common_actions(self, menu):
        # 添加设置单元格颜色、字体颜色和对齐方式的操作到菜单
        set_color_action = menu.addAction("设置单元格颜色")
        set_font_color_action = menu.addAction("设置字体颜色")
        align_menu = menu.addMenu("对齐单元格")
        align_left_action = align_menu.addAction("左对齐")
        align_center_action = align_menu.addAction("居中对齐")
        align_right_action = align_menu.addAction("右对齐")

        actions = {
            set_color_action: self.table_operations.set_cell_color,
            set_font_color_action: self.table_operations.set_font_color,
            align_left_action: lambda: self.table_operations.align_cells(Qt.AlignLeft, Qt.AlignVCenter),
            align_center_action: lambda: self.table_operations.align_cells(Qt.AlignHCenter, Qt.AlignVCenter),
            align_right_action: lambda: self.table_operations.align_cells(Qt.AlignRight, Qt.AlignVCenter),
        }
        return actions

    def add_additional_actions(self, menu):
        # 添加额外的菜单操作
        clear_action = menu.addAction("清空单元格")
        add_menu = menu.addMenu("添加")
        add_row_above_action = add_menu.addAction("在上方添加行")
        add_row_below_action = add_menu.addAction("在下方添加行")
        add_col_left_action = add_menu.addAction("在左侧添加列")
        add_col_right_action = add_menu.addAction("在右侧添加列")
        delete_menu = menu.addMenu("删除")
        delete_row_action = delete_menu.addAction("删除行")
        set_width_action = menu.addAction("设置列宽")
        set_height_action = menu.addAction("设置行高")
        set_font_size_action = menu.addAction("设置字体大小")
        toggle_bold_action = menu.addAction("切换加粗")
        sort_menu = menu.addMenu("排序")
        sort_asc_action = sort_menu.addAction("升序")
        sort_desc_action = sort_menu.addAction("降序")

        additional_actions = {
            clear_action: self.table_operations.clear_cells,
            add_row_above_action: lambda: self.table_operations.add_rows(above=True),
            add_row_below_action: lambda: self.table_operations.add_rows(above=False),
            add_col_left_action: lambda: self.table_operations.add_columns(left=True),
            add_col_right_action: lambda: self.table_operations.add_columns(left=False),
            delete_row_action: self.table_operations.delete_rows,
            set_width_action: self.table_operations.set_col_width,
            set_height_action: self.table_operations.set_row_height,
            set_font_size_action: self.table_operations.set_font_size,
            toggle_bold_action: self.table_operations.toggle_bold,
            sort_asc_action: lambda: self.table_operations.sort_table_by_column(self.table.currentColumn(),Qt.AscendingOrder),
            sort_desc_action: lambda: self.table_operations.sort_table_by_column(self.table.currentColumn(),Qt.DescendingOrder)
        }
        return additional_actions

    def open_menu(self, position):
        menu = QMenu()  # 创建右键菜单
        actions = self.add_common_actions(menu)
        additional_actions = self.add_additional_actions(menu)
        actions.update(additional_actions)

        # 执行选择的操作
        action = menu.exec(self.table.viewport().mapToGlobal(position))

        # 根据用户选择执行相应操作
        if action in actions:
            actions[action]()

    def on_cell_double_clicked(self, row, column):
        item = self.table.item(row, column)
        if item:
            text_edit = QTextEdit()
            text_edit.setPlainText(item.text())
            self.table.setCellWidget(row, column, text_edit)
            text_edit.setFocus()
            text_edit.setFont(item.font())
            text_edit.setAlignment(Qt.AlignmentFlag(item.textAlignment()))

            def focus_out_event(event):
                text = text_edit.toPlainText()
                self.table.removeCellWidget(row, column)
                new_item = QTableWidgetItem(text)
                new_item.setForeground(item.foreground())
                new_item.setBackground(item.background())
                new_item.setFont(item.font())
                alignment = item.textAlignment()
                if alignment:
                    new_item.setData(Qt.TextAlignmentRole, alignment)
                self.table.setItem(row, column, new_item)
                QTextEdit.focusOutEvent(text_edit, event)

            text_edit.focusOutEvent = focus_out_event
