import sys
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget,QMessageBox, QPushButton, QHBoxLayout, QApplication,QColorDialog,QInputDialog
from server.client import DataClient
from pages.table_search import TableWidget
from pages.table_handler import TableHandler
from PySide6.QtCore import QThread, Signal, Slot
import threading
from redis import Redis, ConnectionPool
import redis
import json
import uuid

class UpdateListener(QThread):
    update_signal = Signal(str)

    def __init__(self, server_url, table_name, client_id, parent=None):
        super().__init__(parent)
        self.client_id = client_id
        self.table_name = table_name
        self.pool = ConnectionPool(host='127.0.0.1', port=6379, db=0)
        self.is_running = True

    def run(self):
        redis_client = Redis(connection_pool=self.pool)
        pubsub = redis_client.pubsub()
        pubsub.subscribe('table_updates')
        print("Subscribed to channel.")
        while self.is_running:
            message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
            if message and message['type'] == 'message':
                data = json.loads(message['data'])
                if data['table_name'] == self.table_name and data['client_id'] != self.client_id:
                    self.update_signal.emit("数据已更新")

    def stop(self):
        self.is_running = False
        self.quit()
        self.wait()


def check_bit(user_flag, n):
    if user_flag & (1 << (n - 1)):
        return True
    else:
        return False

class KpiWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Table Handler Example")
        server_url = "http://127.0.0.1:5002"
        table_name = "test_collection1"
        self.client_id = str(uuid.uuid4())

        self.db_handler = DataClient(server_url, table_name, self.client_id)
        flag = check_bit(self.db_handler.get_permissions("c50039960"), 1)  # 权限检查
        self.table_widget = TableWidget(editable=flag)
        self.table_handler = TableHandler(self.table_widget, self.db_handler, can_save_data=flag)

        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)

        button_layout = QHBoxLayout()
        save_button = QPushButton("Save Data")
        save_button.clicked.connect(self.table_handler.save_data)
        button_layout.addWidget(save_button)

        refresh_button = QPushButton("Refresh Data")
        refresh_button.clicked.connect(self.table_handler.refresh_data)
        button_layout.addWidget(refresh_button)

        export_button = QPushButton("Export to Excel")
        export_button.clicked.connect(self.table_handler.export_to_excel)
        button_layout.addWidget(export_button)

        layout.addLayout(button_layout)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 启动更新监听线程
        self.update_listener = UpdateListener(server_url, table_name, self.client_id)
        self.update_listener.update_signal.connect(self.display_update_notification)
        self.update_listener.start()

        self.table_handler.load_table_data()


    @Slot(str)
    def display_update_notification(self, message):
        QMessageBox.information(self, "更新通知", message)

    def closeEvent(self, event):
        if hasattr(self, 'update_listener'):
            self.update_listener.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KpiWindow()
    window.show()
    sys.exit(app.exec())