from PySide6.QtWidgets import QMenu, QTextEdit, QTableWidgetItem, QInputDialog, QColorDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from function.option_change import (TableOperations, ClearCellsStrategy, AddRowsStrategy,
                                    AddColumnsStrategy, DeleteRowsStrategy, DeleteColumnsStrategy,
                                    SetCellColorStrategy, SetFontColorStrategy, SetRowHeightStrategy,
                                    SetColumnWidthStrategy, SetFontSizeStrategy, ToggleBoldStrategy,
                                    MergeCellsStrategy, UnmergeCellsStrategy, AlignCellsStrategy)


class MenuOperations:
    _instance = None  # 单例实例

    def __new__(cls, table, editable=False):
        if cls._instance is None:
            cls._instance = super(MenuOperations, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, table, editable=False):
        if self._initialized:
            return  # 防止重复初始化

        self._initialized = True
        self.table = table
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
        set_color_action = menu.addAction("设置单元格颜色")
        set_font_color_action = menu.addAction("设置字体颜色")
        align_menu = menu.addMenu("对齐单元格")
        align_left_action = align_menu.addAction("左对齐")
        align_center_action = align_menu.addAction("居中对齐")
        align_right_action = align_menu.addAction("右对齐")

        actions = {
            set_color_action: SetCellColorStrategy(),
            set_font_color_action: SetFontColorStrategy(),
            align_left_action: AlignCellsStrategy(Qt.AlignLeft, Qt.AlignVCenter),
            align_center_action: AlignCellsStrategy(Qt.AlignHCenter, Qt.AlignVCenter),
            align_right_action: AlignCellsStrategy(Qt.AlignRight, Qt.AlignVCenter)
        }
        return actions

    def add_additional_actions(self, menu):
        clear_action = menu.addAction("清空单元格")
        add_menu = menu.addMenu("添加")
        add_row_above_action = add_menu.addAction("在上方添加行")
        add_row_below_action = add_menu.addAction("在下方添加行")
        add_col_left_action = add_menu.addAction("在左侧添加列")
        add_col_right_action = add_menu.addAction("在右侧添加列")
        delete_menu = menu.addMenu("删除")
        delete_row_action = delete_menu.addAction("删除行")
        delete_col_action = delete_menu.addAction("删除列")
        set_width_action = menu.addAction("设置列宽")
        set_height_action = menu.addAction("设置行高")
        set_font_size_action = menu.addAction("设置字体大小")
        toggle_bold_action = menu.addAction("切换加粗")
        merge_action = menu.addAction("合并单元格")
        unmerge_action = menu.addAction("取消合并单元格")

        sort_menu = menu.addMenu("排序")
        sort_asc_action = sort_menu.addAction("升序")
        sort_desc_action = sort_menu.addAction("降序")

        additional_actions = {
            clear_action: ClearCellsStrategy(),
            add_row_above_action: AddRowsStrategy(above=True),
            add_row_below_action: AddRowsStrategy(above=False),
            add_col_left_action: AddColumnsStrategy(left=True),
            add_col_right_action: AddColumnsStrategy(left=False),
            delete_row_action: DeleteRowsStrategy(),
            delete_col_action: DeleteColumnsStrategy(),
            set_width_action: SetColumnWidthStrategy(),
            set_height_action: SetRowHeightStrategy(),
            set_font_size_action: SetFontSizeStrategy(),
            toggle_bold_action: ToggleBoldStrategy(),
            merge_action: MergeCellsStrategy(),
            unmerge_action: UnmergeCellsStrategy(),
            sort_asc_action: lambda: self.table_operations.sort_table_by_column(self.table.currentColumn(),
                                                                                Qt.AscendingOrder),
            sort_desc_action: lambda: self.table_operations.sort_table_by_column(self.table.currentColumn(),
                                                                                 Qt.DescendingOrder)
        }
        return additional_actions

    def open_menu(self, position):
        menu = QMenu()  # 创建右键菜单
        actions = self.add_common_actions(menu)
        additional_actions = self.add_additional_actions(menu)
        actions.update(additional_actions)

        action = menu.exec(self.table.viewport().mapToGlobal(position))

        if action in actions:
            self.table_operations.set_strategy(actions[action])
            self.table_operations.execute_strategy()

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
