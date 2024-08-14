import json
from urllib.parse import urlparse

from PySide6.QtCore import QThread, Signal
from redis import Redis, ConnectionPool

class BroadcastListener(QThread):
    update_table_signal = Signal(dict, str)  # 定义信号，传递 rn_record 和操作类型

    def __init__(self, client_id, redis_url, parent=None):
        super().__init__(parent)
        self.client_id = client_id
        parsed_url = urlparse(redis_url)
        self.redis_host = parsed_url.hostname
        self.redis_port = 6379
        self.pool = ConnectionPool(host=self.redis_host, port=self.redis_port, db=0)
        self.is_running = True

    def run(self):
        redis_client = Redis(connection_pool=self.pool)
        pubsub = redis_client.pubsub()
        pubsub.subscribe('rn_channel')  # 订阅频道
        print("Subscribed to rn_channel.")
        while self.is_running:
            message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
            if message and message['type'] == 'message':
                data = json.loads(message['data'])
                if data['client_id'] != self.client_id:  # 忽略本客户端的消息
                    operation = data.get('operation')
                    if operation:
                        self.update_table_signal.emit(data, operation)  # 发射信号更新表格

    def stop(self):
        self.is_running = False
        self.quit()
        self.wait()
