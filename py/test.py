import sys
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QHBoxLayout, QTableWidgetItem, QMessageBox, QSplitter, \
    QVBoxLayout, QLineEdit, QPushButton, QWidget, QSystemTrayIcon, QStyle, QLabel
from rn_client import RN_Client
from html_tab_widget import HtmlTabWidget
from table_widget import TableWidget
from data_dialog import DataDialog
from html_generator import generate_html
import re
from broadcast_listener import BroadcastListener
from PySide6.QtCore import Qt, QTimer, QRect, QPropertyAnimation
from html_manager import HtmlManager
import uuid

class NotificationWindow(QWidget):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.ToolTip)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 设置字体和大小
        label = QLabel(message)
        label.setFont(QFont('Arial', 12))
        label.setStyleSheet("background-color: black; color: white; padding: 10px; border-radius: 10px;")

        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
        self.adjustSize()

        # 设置窗口在父窗口的右下角
        if parent:
            parent_geometry = parent.geometry()
            x = parent_geometry.x() + parent_geometry.width() - self.width() - 20
            y = parent_geometry.y() + parent_geometry.height() - self.height() - 20
            self.setGeometry(x, y, self.width(), self.height())

        # 设置窗口显示动画
        self.show_animation = QPropertyAnimation(self, b"geometry")
        self.show_animation.setDuration(500)
        self.show_animation.setStartValue(QRect(x, y + 50, self.width(), self.height()))
        self.show_animation.setEndValue(QRect(x, y, self.width(), self.height()))
        self.show_animation.start()

        # 设置定时器自动关闭窗口
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close)
        self.timer.start(10000)  # 10秒后自动关闭

class RN_summary_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.client_id = str(uuid.uuid4())
        self.server_url = "http://127.0.0.1:5000"
        self.username = "c50039964"
        self.client = RN_Client(self.server_url, self.client_id, self.username)

        self.setWindowTitle("Redis表格管理示例")
        self.setGeometry(100, 100, 1200, 800)

        # 创建主布局
        main_layout = QVBoxLayout(self)

        splitter = QSplitter(Qt.Horizontal, self)
        main_layout.addWidget(splitter)

        layout = QVBoxLayout()

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("组合搜索使用 {} 包含每个关键字, 完全匹配搜索采用[]")
        self.search_button = QPushButton("搜索", self)
        self.search_button.clicked.connect(self.search_records)

        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)

        search_widget = QWidget()
        search_widget.setLayout(search_layout)
        layout.addWidget(search_widget)

        self.table = TableWidget(self, self.client, main_window=self)
        layout.addWidget(self.table)

        table_widget = QWidget()
        table_widget.setLayout(layout)
        splitter.addWidget(table_widget)

        self.html_tab_widget = HtmlTabWidget()
        splitter.addWidget(self.html_tab_widget)
        splitter.setSizes([400, 800])

        # 创建 HtmlManager 实例
        self.html_manager = HtmlManager(self.html_tab_widget)

        self.broadcast_listener = BroadcastListener(self.client_id, self.server_url)
        self.broadcast_listener.update_table_signal.connect(self.update_table_based_on_broadcast)
        self.broadcast_listener.start()

        self.table.load_table_data()

    def show_notification(self, issue_number):
        """在右下角显示自定义通知窗口"""
        message = f"问题单号 {issue_number} 的 HTML 页面已刷新。"
        notification = NotificationWindow(message, self)
        notification.show()

    def search_records(self):
        search_pattern = self.search_input.text()
        filters = []

        if search_pattern:
            # 处理精确匹配的部分 (以 [] 包围)
            exact_matches = re.findall(r'\[(.*?)\]', search_pattern)
            for match in exact_matches:
                filters.append(('exact', re.escape(match)))  # 精确匹配

            # 处理模糊搜索部分 (以 {} 包围)
            non_exact_search_pattern = re.sub(r'\[.*?\]', '', search_pattern).strip()
            if non_exact_search_pattern:
                if "{" in non_exact_search_pattern and "}" in non_exact_search_pattern:
                    keywords = re.findall(r'\{(.*?)\}', non_exact_search_pattern)
                else:
                    keywords = [non_exact_search_pattern]

                for keyword in keywords:
                    filters.append(('contains', re.escape(keyword)))  # 模糊匹配

            print(f"Filters applied: {filters}")
            self.table.load_table_data(filters=filters)
        else:
            print("No filters applied, loading all data.")
            self.table.load_table_data()

    def add_item(self):
        dialog = DataDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            issue_number = data.get('问题单号')

            if self.client.check_issue_number_exists(issue_number):
                QMessageBox.warning(self, "错误", f"问题单号 '{issue_number}' 已存在，请使用不同的单号。")
                return

            result = self.client.save_rn_record(data)
            if result and result.get("status") == "success":
                self.table.load_table_data()

    def edit_item(self):
        selected_row = self.table.currentRow()  # 从表格对象中获取当前选中的行

        if selected_row >= 0:
            item = self.table.item(selected_row, 0)
            if item is None:
                print("Error: No item found in the selected row.")
                return

            old_record = item.data(Qt.UserRole)
            print(f"Data found in selected row: {old_record}")

            if old_record is None:
                print("Error: No data found for selected row.")
                return

            old_issue_number = old_record.get('问题单号')
            print(f"Old issue number: {old_issue_number}")

            dialog = DataDialog(self, old_record)
            if dialog.exec():
                new_data = dialog.get_data()
                new_issue_number = new_data.get('问题单号')
                print(f"New issue number: {new_issue_number}")

                if new_issue_number != old_issue_number:
                    # 检查新问题单号是否已存在
                    if self.client.check_issue_number_exists(new_issue_number):
                        print(f"Error: Issue number '{new_issue_number}' already exists.")
                        QMessageBox.warning(self, "错误", f"问题单号 '{new_issue_number}' 已存在，请使用不同的单号。")
                        return

                    # 尝试保存新记录，并传入旧单号
                    print(f"Saving new record with issue number: {new_issue_number}")
                    save_result = self.client.save_rn_record(new_data, old_issue_number=old_issue_number)
                    if save_result and save_result.get("status") == "success":
                        print("New record saved successfully.")
                        self.table.load_table_data()  # 调用 TableWidget 的 load_table_data 方法
                        self.html_manager.close_html(old_issue_number)
                        self.html_manager.open_html(new_issue_number, generate_html(new_data))
                    else:
                        print("Error saving new record.")
                        QMessageBox.warning(self, "错误", "保存新记录时出错。")
                else:
                    # 如果问题单号未改变，只更新记录
                    print(f"Updating record for issue number: {new_issue_number}")
                    save_result = self.client.save_rn_record(new_data)
                    if save_result and save_result.get("status") == "success":
                        print("Record updated successfully.")
                        self.table.setItem(selected_row, 0, QTableWidgetItem(new_data.get('问题单号')))
                        self.table.setItem(selected_row, 1, QTableWidgetItem(new_data.get('问题描述')))
                        self.table.item(selected_row, 0).setData(Qt.UserRole, new_data)
                        self.html_manager.reload_html(old_issue_number, generate_html(new_data))
                    else:
                        print("Error updating record.")
                        QMessageBox.warning(self, "错误", "更新记录时出错。")
        else:
            print("Error: No row selected for editing.")

    def delete_item(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            item = self.table.item(selected_row, 0)
            record = item.data(Qt.UserRole)
            issue_number = record.get('问题单号')

            if issue_number:
                reply = QMessageBox.question(
                    self,
                    '确认删除',
                    f"你确定要删除问题单号 '{issue_number}' 的记录吗？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    # 删除数据库中的记录
                    result = self.client.delete_rn_record(issue_number)
                    if result and result.get("status") == "success":
                        # 删除成功后，刷新表格数据
                        self.table.load_table_data()

                        # 如果有对应的HTML页面，关闭它
                        if issue_number in self.html_manager.get_opened_html_list():
                            self.html_manager.close_html(issue_number)

                    else:
                        QMessageBox.warning(self, "错误", "删除记录时出错。")

    def open_html_viewer(self, index):
        row = index.row()
        if row >= 0:
            item = self.table.item(row, 0)
            if not item:
                print(f"Error: No item found in table at row {row}")
                return  # 避免 AttributeError

            record = item.data(Qt.UserRole)
            if not record:
                print(f"Error: No data found for item at row {row}")
                return  # 避免 AttributeError

            issue_number = record.get('问题单号')
            if not issue_number:
                print(f"Error: No '问题单号' found in record {record}")
                return  # 避免 KeyError

            html_content = generate_html(record)
            self.html_manager.open_html(issue_number, html_content)

    def delete_record_from_table(self, rn_record):
        """从表格中删除记录"""
        issue_number = rn_record.get('问题单号')

        if not issue_number:
            print(f"Error: Received rn_record without '问题单号': {rn_record}")
            return  # 如果数据不包含 '问题单号' 键，直接返回

        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.text() == issue_number:
                self.table.removeRow(row)
                print(f"Deleted row for issue_number: {issue_number}")
                break
        else:
            print(f"Error: No row found with issue_number: {issue_number}")

    def update_table_based_on_broadcast(self, data, operation):
        """根据广播消息更新表格和HTML视图"""
        username = data.get('username')  # 从广播数据中获取 username

        if operation == 'delete':
            issue_number = data.get('issue_number')
            print(f"Received delete operation for issue_number: {issue_number} by {username}")
            self.delete_record_from_table({'问题单号': issue_number})
            # 关闭对应的 HTML 页面（如果已打开）
            if self.html_manager.is_html_open(issue_number):
                self.html_manager.close_html(issue_number)
            # 显示通知
            self.show_notification(f"问题单号 {issue_number} 已被 {username} 删除。")

        elif operation == 'update_with_rename':
            old_issue_number = data.get('old_issue_number')
            new_issue_number = data.get('new_issue_number')
            print(
                f"Received update_with_rename operation, old_issue_number: {old_issue_number}, new_issue_number: {new_issue_number} by {username}")

            # 删除旧记录，添加新记录
            self.delete_record_from_table({'问题单号': old_issue_number})
            self.add_record_to_table(data['rn_record'])

            # 关闭旧页面并打开新页面（如果旧页面已打开）
            if self.html_manager.is_html_open(old_issue_number):
                self.html_manager.close_html(old_issue_number)
            if self.html_manager.is_html_open(new_issue_number):
                self.html_manager.reload_html(new_issue_number, generate_html(data['rn_record']))

            # 显示通知
            if old_issue_number and old_issue_number != new_issue_number:
                self.show_notification(
                    f"问题单号 {old_issue_number} 已被 {username} 删除，新的问题单号 {new_issue_number} 已被创建。")
            else:
                self.show_notification(f"问题单号 {new_issue_number} 已被 {username} 修改。")

        elif operation == 'update':
            issue_number = data.get('new_issue_number')
            print(f"Received update operation for issue_number: {issue_number} by {username}")
            self.delete_record_from_table({'问题单号': issue_number})
            self.add_record_to_table(data['rn_record'])
            # 仅在页面已打开的情况下重新加载 HTML
            if self.html_manager.is_html_open(issue_number):
                self.html_manager.reload_html(issue_number, generate_html(data['rn_record']))
            # 显示通知
            self.show_notification(f"问题单号 {issue_number} 已被 {username} 更新。")

        elif operation == 'post':
            issue_number = data.get('new_issue_number')
            print(f"Received post operation for new issue_number: {issue_number} by {username}")
            self.add_record_to_table(data['rn_record'])
            # 仅在页面已打开的情况下打开 HTML 页面
            if self.html_manager.is_html_open(issue_number):
                self.html_manager.reload_html(issue_number, generate_html(data['rn_record']))
            self.show_notification(f"新问题单号 {issue_number} 已被 {username} 创建。")

        else:
            print(f"Unknown operation: {operation}")

        # 刷新表格以确保同步
        self.table.load_table_data()

    def add_record_to_table(self, rn_record):
        """添加或更新记录到表格"""
        issue_number = rn_record.get('问题单号')
        description = rn_record.get('问题描述')

        if not issue_number:
            print(f"Error: Received rn_record without '问题单号': {rn_record}")
            return  # 如果数据不包含 '问题单号' 键，直接返回

        # 首先检查表格中是否已有此记录
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.text() == issue_number:
                # 如果存在，更新记录
                self.table.setItem(row, 1, QTableWidgetItem(description))
                return

        # 如果不存在，插入新记录
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(issue_number))
        self.table.setItem(row_position, 1, QTableWidgetItem(description))


    def closeEvent(self, event):
        """处理窗口关闭事件"""
        if hasattr(self, 'broadcast_listener'):
            self.broadcast_listener.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RN_summary_Window()
    window.show()
    sys.exit(app.exec())
