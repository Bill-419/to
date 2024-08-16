import redis
import json
from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
from readerwriterlock import rwlock

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=10)

redis_client = redis.Redis(host='localhost', port=6379, db=0)

# 初始化读写锁
rw_lock = rwlock.RWLockWrite()


def rn_compare_dictionaries(original, modified):
    changes = []

    keys_to_ignore = ['client_id','issue_number']

    all_keys = set(original.keys()).union(modified.keys()).difference(keys_to_ignore)

    for key in all_keys:
        original_value = original.get(key, None)
        modified_value = modified.get(key, None)

        if original_value != modified_value:
            if original_value is None:
                changes.append(f"'{key}' 新增了值 '{modified_value}'。")
            elif modified_value is None or modified_value == "":
                changes.append(f"'{key}' 被删除，原来的值是 '{original_value}'。")
            elif original_value == "":
                changes.append(f"'{key}' 添加了值 '{modified_value}'。")
            else:
                changes.append(f"'{key}' 从 '{original_value}' 变为 '{modified_value}'。")

    if changes:
        summary = "检测到以下变化：\n" + "\n".join(changes)
    else:
        summary = "未检测到任何变化。"

    return summary


@app.route('/rn_record_exists', methods=['POST'])
def check_issue_number_exists():
    request_data = request.json
    issue_number = request_data.get('issue_number')

    if not issue_number:
        return jsonify({"error": "issue_number 是必填项"}), 400

    with rw_lock.gen_rlock():
        exists = redis_client.exists(f'rn_record:{issue_number}') > 0

    return jsonify({"exists": exists})


@app.route('/save_rn_record', methods=['POST'])
def save_rn_record():
    data = request.json
    issue_number = data.get('issue_number')
    client_id = data.get('client_id')
    save_username_key = data.get('username')

    save_username = redis_client.hget('kpi_username', save_username_key)
    if save_username:
        save_username = save_username.decode('utf-8')
    else:
        return jsonify({"error": "未找到对应的中文名字"}), 404

    old_issue_number = data.pop('old_issue_number', None)

    if not issue_number:
        return jsonify({"error": "issue_number 是必填项"}), 400

    try:
        with rw_lock.gen_wlock():
            if old_issue_number:
                existing_record = redis_client.get(f'rn_record:{old_issue_number}')
                if existing_record:
                    existing_record = json.loads(existing_record)
                    summary = rn_compare_dictionaries(existing_record, data)
                if old_issue_number == issue_number:
                    if existing_record:
                        redis_client.set(f'rn_record:{issue_number}', json.dumps(data))
                        message = {
                            'client_id': client_id,
                            'operation': 'update',
                            'new_issue_number': issue_number,
                            'rn_record': data,
                            'username': save_username,
                            'summary': summary
                        }
                        redis_client.publish('rn_channel', json.dumps(message))
                    else:
                        return jsonify({"error": "未找到对应的问题单号"}), 404
                else:
                    if existing_record:
                        redis_client.delete(f'rn_record:{old_issue_number}')
                        redis_client.set(f'rn_record:{issue_number}', json.dumps(data))
                        message = {
                            'client_id': client_id,
                            'operation': 'update_with_rename',
                            'old_issue_number': old_issue_number,
                            'new_issue_number': issue_number,
                            'rn_record': data,
                            'username': save_username,
                            'summary': summary
                        }
                        redis_client.publish('rn_channel', json.dumps(message))
                    else:
                        return jsonify({"error": "未找到旧的问题单号"}), 404
            else:
                existing_record = redis_client.get(f'rn_record:{issue_number}')
                if existing_record:
                    existing_record = json.loads(existing_record)
                    summary = rn_compare_dictionaries(existing_record, data)
                    redis_client.set(f'rn_record:{issue_number}', json.dumps(data))
                    message = {
                        'client_id': client_id,
                        'operation': 'update',
                        'new_issue_number': issue_number,
                        'rn_record': data,
                        'username': save_username,
                        'summary': summary
                    }
                    redis_client.publish('rn_channel', json.dumps(message))
                else:
                    summary = rn_compare_dictionaries({}, data)
                    redis_client.set(f'rn_record:{issue_number}', json.dumps(data))
                    message = {
                        'client_id': client_id,
                        'operation': 'post',
                        'new_issue_number': issue_number,
                        'rn_record': data,
                        'username': save_username,
                        'summary': summary
                    }
                    redis_client.publish('rn_channel', json.dumps(message))

        return jsonify({"status": "success", "issue_number": issue_number})

    except Exception as e:
        print(f"Error processing record: {e}")
        return jsonify({"error": "处理记录时出错", "details": str(e)}), 500


@app.route('/get_rn_record_by_issue_number', methods=['GET'])
def get_rn_record_by_issue_number():
    issue_number = request.args.get('issue_number')
    if not issue_number:
        return jsonify({"error": "issue_number 是必填项"}), 400

    with rw_lock.gen_rlock():
        data = redis_client.get(f'rn_record:{issue_number}')

    if data:
        rn_record = json.loads(data)
        return jsonify(rn_record)
    return jsonify({"error": "Record not found"}), 404


@app.route('/delete_rn_record', methods=['DELETE'])
def delete_rn_record():
    request_data = request.json
    issue_number = request_data.get('issue_number')
    client_id = request_data.get('client_id')
    del_username_key = request_data.get('username')

    if not issue_number or not client_id:
        return jsonify({"error": "issue_number 和 client_id 是必填项"}), 400

    del_username = redis_client.hget('kpi_username', del_username_key)
    if del_username:
        del_username = del_username.decode('utf-8')
    else:
        return jsonify({"error": "未找到对应的中文名字"}), 404

    with rw_lock.gen_wlock():
        delete_data = redis_client.get(f'rn_record:{issue_number}')
        if delete_data:
            delete_data = json.loads(delete_data)
            summary = rn_compare_dictionaries(delete_data, {})
            redis_client.delete(f'rn_record:{issue_number}')
            message = {
                'client_id': client_id,
                'operation': 'delete',
                'issue_number': issue_number,
                'username': del_username,
                'summary': summary
            }
            redis_client.publish('rn_channel', json.dumps(message))
            return jsonify({"status": "success"})
        else:
            return jsonify({"error": "issue_number不存在"})


@app.route('/get_all_rn_records', methods=['GET'])
def get_all_rn_records():
    with rw_lock.gen_rlock():
        keys = redis_client.keys('rn_record:*')
        rn_records = []
        for key in keys:
            data = redis_client.get(key)
            rn_record = json.loads(data)
            rn_records.append(rn_record)
    return jsonify(rn_records)


@app.route('/save_all', methods=['POST'])
def save_all_route():
    request_data = request.json
    table_name = request_data['table_name']
    client_id = request_data.get('client_id')

    with rw_lock.gen_wlock():
        redis_client.set(f'{table_name}_data', json.dumps(request_data['data']))
        redis_client.set(f'{table_name}_merged_cells', json.dumps(request_data['merged_cells']))

        message_data = {
            'table_name': table_name,
            'client_id': client_id,
            'message': '数据已更新'
        }
        redis_client.publish('table_updates', json.dumps(message_data))

    return jsonify({"status": "success"})


@app.route('/get_all', methods=['POST'])
def get_all_route():
    request_data = request.json
    table_name = request_data['table_name']

    with rw_lock.gen_rlock():
        table_data_json = redis_client.get(f'{table_name}_data')
        merged_cells_json = redis_client.get(f'{table_name}_merged_cells')

        result = {
            "table_data": json.loads(table_data_json) if table_data_json else [],
            "merged_cells": json.loads(merged_cells_json) if merged_cells_json else []
        }

    return jsonify({"status": "success", "data": result})


@app.route('/save_table', methods=['POST'])
def save_table_route():
    request_data = request.json
    table_name = request_data['table_name']

    with rw_lock.gen_wlock():
        redis_client.set(f'{table_name}_data', json.dumps(request_data['data']))

    return jsonify({"status": "success"})


@app.route('/get_table', methods=['POST'])
def get_table_route():
    request_data = request.json
    table_name = request_data['table_name']

    with rw_lock.gen_rlock():
        table_data_json = redis_client.get(f'{table_name}_data')

    return jsonify({"status": "success", "data": json.loads(table_data_json) if table_data_json else []})


@app.route('/save_merged_cells', methods=['POST'])
def save_merged_cells_route():
    request_data = request.json
    table_name = request_data['table_name']

    with rw_lock.gen_wlock():
        redis_client.set(f'{table_name}_merged_cells', json.dumps(request_data['merged_cells']))

    return jsonify({"status": "success"})


@app.route('/get_permissions', methods=['POST'])
def get_permissions_route():
    request_data = request.json
    permission_username = request_data.get('username')

    with rw_lock.gen_rlock():
        permissions = redis_client.get(f'permissions_{permission_username}')

    if permissions is not None:
        return jsonify({"status": "success", "permissions": int(permissions)})
    else:
        return jsonify({"status": "error", "message": "No permissions found for user"})


if __name__ == '__main__':
    username_list = {
        'c50039964': '蔡佳文',
        'c50039960': '赵良媛'
    }

    for username, name in username_list.items():
        redis_client.hset('kpi_username', username, name)
        print({username}, {name})

    user_permissions = {
        'c50039960': 1,
        'c50039964': 1,
        'c50039961': 2,
        'c50039962': 3,
        'c50039963': 4,
        'c50039965': 6,
        'c50039966': 7
    }
    for username, permissions in user_permissions.items():
        redis_client.set(f'permissions_{username}', permissions)

    app.run(host="0.0.0.0", port=5002)
