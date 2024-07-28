from PySide6.QtWidgets import QTableWidgetItem,QInputDialog
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QColorDialog
from PySide6.QtGui import QColor
class TableOperations:
    def __init__(self, table):
        self.table = table  # 保存对表格控件的引用

    def clear_cells(self):
        for item in self.table.selectedItems():  # 遍历表格中每个选中的单元格
            item.setText("")  # 将选中单元格的文本设置为空字符串

    def add_rows(self, above):
        rows = sorted(set(index.row() for index in self.table.selectedIndexes()))  # 获取所有选中单元格的行号，并去重、排序
        count = len(rows)  # 计算选中行的数量
        insert_at = rows[0] if above else rows[-1] + 1  # 判断是在上方还是下方添加行，并确定插入位置
        for _ in range(count):  # 根据选中行的数量重复添加行
            self.table.insertRow(insert_at)  # 在指定位置插入行
            for column in range(self.table.columnCount()):  # 遍历所有列
                item = QTableWidgetItem()  # 创建新的单元格项
                item.setForeground(Qt.black)  # 设置字体颜色为黑色
                item.setBackground(Qt.white)  # 设置单元格背景为白色
                item.setTextAlignment(Qt.AlignLeft|Qt.AlignVCenter)
                self.table.setItem(insert_at, column, item)  # 将新的单元格项添加到表格中

    def add_columns(self, left):
        columns = sorted(set(index.column() for index in self.table.selectedIndexes()))  # 获取所有选中单元格的列号，并去重、排序
        count = len(columns)  # 计算选中列的数量
        insert_at = columns[0] if left else columns[-1] + 1  # 判断是在左侧还是右侧添加列，并确定插入位置
        for _ in range(count):  # 根据选中列的数量重复添加列
            self.table.insertColumn(insert_at)  # 在指定位置插入列
            for row in range(self.table.rowCount()):  # 遍历所有行
                item = QTableWidgetItem()  # 创建新的单元格项
                item.setForeground(Qt.black)  # 设置字体颜色为黑色
                item.setBackground(Qt.white)  # 设置单元格背景为白色
                item.setTextAlignment(Qt.AlignLeft|Qt.AlignVCenter)
                self.table.setItem(row, insert_at, item)  # 将新的单元格项添加到表格中

    def delete_rows(self):
        rows = sorted(set(index.row() for index in self.table.selectedIndexes()), reverse=True)  # 获取所有选中行的行号，并去重、倒序排序
        for row in rows:  # 遍历所有选中的行
            self.table.removeRow(row)  # 删除行

    def delete_columns(self):
        columns = sorted(set(index.column() for index in self.table.selectedIndexes()), reverse=True)  # 获取所有选中列的列号，并去重、倒序排序
        for col in columns:  # 遍历所有选中的列
            self.table.removeColumn(col)  # 删除列

    def align_cells(self, horizontal_alignment, vertical_alignment):
        for index in self.table.selectedIndexes():  # 遍历所有选中的单元格
            item = self.table.item(index.row(), index.column())  # 获取单元格项
            if not item:
                item = QTableWidgetItem()  # 如果单元格项不存在，则创建新的单元格项
                self.table.setItem(index.row(), index.column(), item)  # 将新的单元格项添加到表格中
            item.setTextAlignment(horizontal_alignment | vertical_alignment)  # 设置单元格的文本对齐方式
    
    def sort_table_by_column(self, column, order=Qt.AscendingOrder):
        self.table.sortItems(column, order)  # 根据指定列和顺序对表格进行排序

    def set_cell_color(self):
        color = QColorDialog.getColor()  # 打开颜色选择对话框
        if color.isValid():  # 如果选中的颜色有效
            for index in self.table.selectedIndexes():  # 遍历所有选中的单元格
                item = self.table.item(index.row(), index.column())
                if not item:  # 如果单元格不存在，创建新的单元格
                    item = QTableWidgetItem()
                    self.table.setItem(index.row(), index.column(), item)
                item.setBackground(color)  # 设置单元格的背景颜色

    def set_row_height(self):
        rows = set(index.row() for index in self.table.selectedIndexes())  # 获取所有选中的行
        height, ok = QInputDialog.getInt(self.table, "Set Row Height", "Enter new row height:", 30, 10, 500, 1)  # 打开输入对话框获取新的行高
        if ok:  # 如果用户点击确认
            for row in rows:
                self.table.setRowHeight(row, height)  # 设置行高

    def set_col_width(self):
        cols = set(index.column() for index in self.table.selectedIndexes())  # 获取所有选中的列
        width, ok = QInputDialog.getInt(self.table, "Set Column Width", "Enter new column width:", 100, 10, 500, 1)  # 打开输入对话框获取新的列宽
        if ok:  # 如果用户点击确认
            for col in cols:
                self.table.setColumnWidth(col, width)  # 设置列宽

    def set_font_size(self):
        size, ok = QInputDialog.getInt(self.table, "Set Font Size", "Enter new font size:", 10, 1, 100, 1)  # 打开输入对话框获取新的字体大小
        if ok:  # 如果用户点击确认
            for index in self.table.selectedIndexes():  # 遍历所有选中的单元格
                item = self.table.item(index.row(), index.column())
                if item is None:  # 如果单元格不存在，创建新的单元格
                    item = QTableWidgetItem()
                    self.table.setItem(index.row(), index.column(), item)
                widget = self.table.cellWidget(index.row(), index.column())
                if widget:  # 如果单元格是一个特殊控件
                    font = widget.font()  # 获取控件的字体
                    font.setPointSize(size)  # 设置字体大小
                    widget.setFont(font)
                else:
                    font = item.font()  # 获取单元格字体
                    font.setPointSize(size)  # 设置字体大小
                    item.setFont(font)

    def set_font_color(self):
        color = QColorDialog.getColor()  # 打开颜色选择对话框
        if color.isValid():  # 如果选中的颜色有效
            for index in self.table.selectedIndexes():  # 遍历所有选中的单元格
                item = self.table.item(index.row(), index.column())
                if item is None:  # 如果单元格不存在，创建新的单元格
                    item = QTableWidgetItem()
                    self.table.setItem(index.row(), index.column(), item)
                item.setForeground(color)  # 设置单元格的字体颜色
                item.setText(item.text())  # 强制更新单元格内容以刷新显示
            self.table.viewport().update()  # 更新视图以应用颜色更改

    def toggle_bold(self):
        for index in self.table.selectedIndexes():  # 遍历所有选中的单元格
            item = self.table.item(index.row(), index.column())
            if item is None:  # 如果单元格不存在，创建新的单元格
                item = QTableWidgetItem()
                self.table.setItem(index.row(), index.column(), item)
            widget = self.table.cellWidget(index.row(), index.column())
            if widget:  # 如果单元格是一个特殊控件
                font = widget.font()  # 获取控件的字体
                font.setBold(not font.bold())  # 切换字体粗体状态
                widget.setFont(font)
            else:
                font = item.font()  # 获取单元格字体
                font.setBold(not font.bold())  # 切换字体粗体状态
                item.setFont(font)

    def merge_cells(self):
        selected_ranges = self.table.selectedRanges()  # 获取所有选中的单元格范围
        if not selected_ranges:
            return

        top_row = min(selected_range.topRow() for selected_range in selected_ranges)  # 获取选中范围的最顶端行号
        bottom_row = max(selected_range.bottomRow() for selected_range in selected_ranges)  # 获取选中范围的最底端行号
        left_col = min(selected_range.leftColumn() for selected_range in selected_ranges)  # 获取选中范围的最左端列号
        right_col = max(selected_range.rightColumn() for selected_range in selected_ranges)  # 获取选中范围的最右端列号

        # 确保选择跨越多行或多列
        if bottom_row == top_row and right_col == left_col:
            return

        # 查找第一个非空单元格的文本、背景颜色、字体、字体颜色和字体大小
        text = ''
        background_color = QColor("#ffffff")
        font = self.table.font()
        font_color = QColor("#000000")
        found_non_empty = False
        for col in range(left_col, right_col + 1):
            for row in range(top_row, bottom_row + 1):
                item = self.table.item(row, col)
                if item and item.text().strip():
                    text = item.text()
                    background_color = item.background().color()
                    font = item.font()
                    font_color = item.foreground().color()
                    
                    # 如果背景颜色和字体颜色都是黑色，则将背景颜色设置为白色
                    if background_color == QColor("#000000") and font_color == QColor("#000000"):
                        background_color = QColor("#ffffff")
                    
                    found_non_empty = True
                    break
            if found_non_empty:
                break

        # 清空所有选中单元格的文本并保留背景颜色、字体、字体颜色和字体大小，除了第一个单元格
        for row in range(top_row, bottom_row + 1):
            for col in range(left_col, right_col + 1):
                if row == top_row and col == left_col:
                    continue
                item = self.table.item(row, col)
                if not item:
                    item = QTableWidgetItem()
                    self.table.setItem(row, col, item)
                item.setText('')
                item.setBackground(background_color)
                item.setFont(font)
                item.setTextAlignment(Qt.AlignLeft|Qt.AlignVCenter)
                item.setForeground(font_color)

        # 设置跨度和在左上角单元格中设置文本
        self.table.setSpan(top_row, left_col, bottom_row - top_row + 1, right_col - left_col + 1)
        if not self.table.item(top_row, left_col):
            self.table.setItem(top_row, left_col, QTableWidgetItem())
        top_left_item = self.table.item(top_row, left_col)
        top_left_item.setText(text)
        top_left_item.setBackground(background_color)
        top_left_item.setFont(font)
        top_left_item.setTextAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        top_left_item.setForeground(font_color)

    def unmerge_cells(self):
        table = self.table  # 确保使用的是正确的表格对象
        selected_ranges = table.selectedRanges()  # 获取所有选中的单元格范围
        if not selected_ranges:
            return

        for selected_range in selected_ranges:
            top_row = selected_range.topRow()  # 获取选中范围的最顶端行号
            left_col = selected_range.leftColumn()  # 获取选中范围的最左端列号
            bottom_row = selected_range.bottomRow()  # 获取选中范围的最底端行号
            right_col = selected_range.rightColumn()  # 获取选中范围的最右端列号

            merged_item = table.item(top_row, left_col)  # 获取左上角单元格
            merged_text = merged_item.text() if merged_item else ''  # 获取合并单元格的文本
            background_color = merged_item.background().color() if merged_item else QColor("#ffffff")  # 获取合并单元格的背景颜色
            font = merged_item.font() if merged_item else table.font()  # 获取合并单元格的字体
            font_color = merged_item.foreground().color() if merged_item else QColor("#000000")  # 获取合并单元格的字体颜色

            for row in range(top_row, bottom_row + 1):
                for col in range(left_col, right_col + 1):
                    # 只有当单元格是合并的一部分时才取消合并
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
                    item.setFlags(item.flags() | Qt.ItemIsEditable)  # 确保单元格可编辑
                    if row == top_row and col == left_col:
                        item.setText(merged_text)
                    else:
                        item.setText('')