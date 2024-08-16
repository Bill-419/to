from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView, QMenu, QMessageBox
from PySide6.QtCore import Qt
import re

class TableWidget(QTableWidget):
    def __init__(self, parent=None, client=None, main_window=None):
        super().__init__(0, 2, parent)
        self.client = client
        self.main_window = main_window  # 保存 MainWindow 的实例
        self.setHorizontalHeaderLabels(["问题单号", "描述"])
        self.horizontalHeader().setStretchLastSection(True)
        self.setColumnWidth(0, 150)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.doubleClicked.connect(main_window.open_html_viewer)

    def load_table_data(self, filters=None):
        print("Loading table data...")
        records = self.client.get_all_rn_records()
        print(records)
        print(f"Records fetched: {len(records)}")

        if filters:
            filtered_records = []
            for record in records:
                record_matches = set()  # 用于存储已经过滤的键
                include_record = True

                for filter_type, filter_key, filter_value in filters:
                    if filter_key in record_matches:
                        continue  # 如果该键已经被过滤过，则跳过

                    if filter_type == 'exact':
                        # 精确匹配
                        if filter_key in record and re.escape(record[filter_key]) == filter_value:
                            record_matches.add(filter_key)
                        else:
                            include_record = False
                            break

                    elif filter_type == 'contains':
                        # 模糊匹配
                        if filter_key in record and re.search(filter_value, record[filter_key], re.IGNORECASE):
                            record_matches.add(filter_key)
                        else:
                            include_record = False
                            break

                    elif filter_type == 'free':
                        # 自由形式搜索，搜索所有键值对
                        if any(re.search(filter_value, str(value), re.IGNORECASE) for key, value in record.items()):
                            # 如果有任意一个值匹配
                            record_matches.add(filter_key)  # 这里的key是None，我们可以跳过这个记录
                        else:
                            include_record = False
                            break

                if include_record:
                    filtered_records.append(record)

            records = filtered_records
            print(f"Records after filtering: {len(records)}")

        self.setRowCount(0)  # 清空表格内容
        print("Cleared the table.")

        for record in records:
            row_position = self.rowCount()
            self.insertRow(row_position)
            print(f"Inserting row at position {row_position}: {record}")
            issue_number_item = QTableWidgetItem(record.get('问题单号', ''))
            description_item = QTableWidgetItem(record.get('问题描述', ''))

            # 将记录保存到每行的 UserRole 中
            issue_number_item.setData(Qt.UserRole, record)

            self.setItem(row_position, 0, issue_number_item)
            self.setItem(row_position, 1, description_item)
        print("Table data loaded successfully.")

    def show_context_menu(self, position):
        menu = QMenu()

        # 初始化 edit_action 和 delete_action
        edit_action = None
        delete_action = None

        # 检查是否有行被选中
        index = self.indexAt(position)
        if index.isValid():
            # 如果有行被选中，则添加修改和删除选项
            edit_action = menu.addAction("修改项目")
            delete_action = menu.addAction("删除项目")

        add_action = menu.addAction("添加项目")
        refresh_action = menu.addAction("刷新项目")

        action = menu.exec(self.viewport().mapToGlobal(position))

        if action == add_action:
            self.main_window.add_item()
        elif action == edit_action and index.isValid():
            self.main_window.edit_item()
        elif action == delete_action and index.isValid():
            self.main_window.delete_item()
        elif action == refresh_action:
            self.load_table_data()

