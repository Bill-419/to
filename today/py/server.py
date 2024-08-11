import redis
import json
from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
import json
app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=10)

redis_client = redis.Redis(host='localhost', port=6379, db=0)  

class RedisHandler:

    def load_all_rn_records(self):
        keys = redis_client.keys('rn_record:*')
        rn_records = []
        for key in keys:
            data = redis_client.get(key)
            rn_record = json.loads(data)
            rn_records.append(rn_record)
        return rn_records

    def save_rn_record(self, issue_number, rn_record_data):
        redis_client.set(f'rn_record:{issue_number}', json.dumps(rn_record_data))

    def delete_rn_record(self, issue_number):
        redis_client.delete(f'rn_record:{issue_number}')

    def get_rn_record_by_issue_number(self, issue_number):
        data = redis_client.get(f'rn_record:{issue_number}')
        if data:
            return json.loads(data)
        return None

    def issue_number_exists(self, issue_number):
        return redis_client.exists(f'rn_record:{issue_number}') > 0

    def save_table(self, table_name: str, data: List[Dict[str, Any]]):
        redis_client.set(f'{table_name}_data', json.dumps(data)) 

    def get_table(self, table_name: str):
        table_data_json = redis_client.get(f'{table_name}_data')
        return json.loads(table_data_json) if table_data_json else []

    def save_merged_cells(self, table_name: str, merged_cells: List[Dict[str, Any]]):
        redis_client.set(f'{table_name}_merged_cells', json.dumps(merged_cells))

    def get_merged_cells(self, table_name: str):
        merged_cells_json = redis_client.get(f'{table_name}_merged_cells')
        return json.loads(merged_cells_json) if merged_cells_json else []

    def save_all(self, table_name: str, data: List[Dict[str, Any]], merged_cells: List[Dict[str, Any]], client_id: str):
        self.save_table(table_name, data)
        self.save_merged_cells(table_name, merged_cells)
        message_data = {
            'table_name': table_name,
            'client_id': client_id,
            'message': '数据已更新'
        }
        redis_client.publish('table_updates', json.dumps(message_data))

    def get_all(self, table_name: str):
        return {
            "table_data": self.get_table(table_name),
            "merged_cells": self.get_merged_cells(table_name)
        }

    def set_permissions(self, username: str, permissions: int):
        redis_client.set(f'permissions_{username}', permissions)

    def get_permissions(self, username: str):
        permissions = redis_client.get(f'permissions_{username}')
        return int(permissions) if permissions else None
    
    def set_multiple_permissions(self, user_permissions):
        for username, permissions in user_permissions.items():
            self.set_permissions(username, permissions)
        print("Permissions set successfully for all provided users.")

    def clear_permissions(self, usernames):
        for username in usernames:
            redis_client.delete(f'permissions_{username}')
        print("Permissions cleared successfully for all provided users.")

    def publish_message(self, channel, message):
        redis_client.publish(channel, message)

redis_handler = RedisHandler()

@app.route("/save_all", methods=["POST"])
def save_all_route():
    request_data = request.json
    table_name = request_data['table_name'] 
    client_id = request_data.get('client_id') 
    future = executor.submit(redis_handler.save_all, table_name, request_data['data'], request_data['merged_cells'], client_id)
    future.result()
    return jsonify({"status": "success"})

@app.route("/get_all", methods=["POST"])
def get_all_route():
    request_data = request.json
    table_name = request_data['table_name']
    result = executor.submit(redis_handler.get_all, table_name).result()
    return jsonify({"status": "success", "data": result})

@app.route("/save_table", methods=["POST"])
def save_table_route():
    request_data = request.json
    table_name = request_data['table_name']
    future = executor.submit(redis_handler.save_table, table_name, request_data['data'])
    future.result()
    return jsonify({"status": "success"})

@app.route("/get_table", methods=["POST"])
def get_table_route():
    request_data = request.json
    table_name = request_data['table_name']
    result = executor.submit(redis_handler.get_table, table_name).result()
    return jsonify({"status": "success", "data": result})

@app.route("/save_merged_cells", methods=["POST"])
def save_merged_cells_route():
    request_data = request.json
    table_name = request_data['table_name']
    future = executor.submit(redis_handler.save_merged_cells, table_name, request_data['merged_cells'])
    future.result()
    return jsonify({"status": "success"})

@app.route("/get_permissions", methods=["GET"])
def get_permissions_route():
    username = request.args.get('username')
    permissions = redis_handler.get_permissions(username)
    if permissions is not None:
        return jsonify({"status": "success", "permissions": permissions})
    else:
        return jsonify({"status": "error", "message": "No permissions found for user"})

@app.route('/rn_records', methods=['GET'])
def get_all_rn_records():
    future = executor.submit(redis_handler.load_all_rn_records)
    rn_records = future.result()
    return jsonify(rn_records)

@app.route('/rn_record/<string:issue_number>', methods=['GET'])
def get_rn_record_by_issue_number(issue_number):
    future = executor.submit(redis_handler.get_rn_record_by_issue_number, issue_number)
    rn_record = future.result()
    if rn_record:
        return jsonify(rn_record)
    return jsonify({"error": "Record not found"}), 404

@app.route('/rn_record', methods=['POST'])
def save_rn_record():
    data = request.json
    issue_number = data.get('问题单号')
    client_id = data.get('client_id')

    if not issue_number:
        return jsonify({"error": "问题单号是必填项"}), 400

    # 检查是否是更新操作，并且单号名称是否发生变化
    existing_record = redis_handler.get_rn_record_by_issue_number(issue_number)
    if existing_record:
        old_issue_number = existing_record.get('问题单号')
        if old_issue_number != issue_number:
            # 如果单号名称发生变化
            future = executor.submit(redis_handler.save_rn_record, issue_number, data)
            future.result()

            # 广播消息，标识这是一个单号名称修改的操作
            message = {
                'client_id': client_id,
                'operation': 'update_with_rename',
                'old_issue_number': old_issue_number,
                'new_issue_number': issue_number,
                'rn_record': data
            }
            redis_handler.publish_message('rn_channel', json.dumps(message))
        else:
            # 如果单号名称未发生变化
            future = executor.submit(redis_handler.save_rn_record, issue_number, data)
            future.result()

            # 广播消息，标识这是一个普通的更新操作
            message = {
                'client_id': client_id,
                'operation': 'update',
                'new_issue_number': issue_number,
                'rn_record': data
            }
            redis_handler.publish_message('rn_channel', json.dumps(message))
    else:
        # 如果是一个新的记录
        future = executor.submit(redis_handler.save_rn_record, issue_number, data)
        future.result()

        # 广播消息，标识这是一个新增操作
        message = {
            'client_id': client_id,
            'operation': 'post',
            'new_issue_number': issue_number,
            'rn_record': data
        }
        redis_handler.publish_message('rn_channel', json.dumps(message))

    return jsonify({"status": "success", "issue_number": issue_number})

@app.route('/rn_record/<string:issue_number>', methods=['DELETE'])
def delete_rn_record(issue_number):
    client_id = request.args.get('client_id')
    if not client_id:
        return jsonify({"error": "client_id 是必填项"}), 400

    future = executor.submit(redis_handler.delete_rn_record, issue_number)
    future.result()

    # 广播消息，直接使用 issue_number
    message = {
        'client_id': client_id,
        'operation': 'delete',
        'issue_number': issue_number  # 直接传递 issue_number
    }
    redis_handler.publish_message('rn_channel', json.dumps(message))

    return jsonify({"status": "success"})


@app.route('/rn_record_exists/<string:issue_number>', methods=['GET'])
def check_issue_number_exists(issue_number):
    future = executor.submit(redis_handler.issue_number_exists, issue_number)
    exists = future.result()
    return jsonify({"exists": exists})


if __name__ == '__main__':

    user_permissions = {
        'c50039960': 1,
        'c50039961': 2,
        'c50039962': 3,
        'c50039963': 4,
        'c50039964': 5,
        'c50039965': 6,
        'c50039966': 7
    }
    redis_handler.set_multiple_permissions(user_permissions)

    app.run(host="0.0.0.0", port=5002)
