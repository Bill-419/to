import redis
import json
from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

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

    def save_rn_record(self, rn_record_id, rn_record_data):
        rn_record_data['issue_number'] = rn_record_data.get('issue_number', str(rn_record_id))  # 确保 issue_number 存在
        redis_client.set(f'rn_record:{rn_record_id}', json.dumps(rn_record_data))

    def delete_rn_record(self, rn_record_id):
        redis_client.delete(f'rn_record:{rn_record_id}')

    def get_new_rn_record_id(self):
        keys = redis_client.keys('rn_record:*')
        if keys:
            max_id = max(int(key.split(b':')[-1]) for key in keys)
            return max_id + 1
        else:
            return 1

    def get_rn_record_by_id(self, rn_record_id):
        data =redis_client.get(f'rn_record:{rn_record_id}')
        if data:
            return json.loads(data)
        return None

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

@app.route('/rn_record/<int:rn_record_id>', methods=['GET'])
def get_rn_record_by_id(rn_record_id):
    future = executor.submit(redis_handler.get_rn_record_by_id, rn_record_id)
    rn_record = future.result()
    if rn_record:
        return jsonify(rn_record)
    return jsonify({"error": "Record not found"}), 404

@app.route('/rn_record', methods=['POST'])
def save_rn_record():
    data = request.json
    if not data.get('id'):
        rn_record_id = redis_handler.get_new_rn_record_id()
        data['id'] = rn_record_id
    else:
        rn_record_id = data['id']
    future = executor.submit(redis_handler.save_rn_record, rn_record_id, data)
    future.result()
    return jsonify({"status": "success", "rn_record_id": rn_record_id})

@app.route('/rn_record/<int:rn_record_id>', methods=['DELETE'])
def delete_rn_record(rn_record_id):
    future = executor.submit(redis_handler.delete_rn_record, rn_record_id)
    future.result()
    return jsonify({"status": "success"})


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
