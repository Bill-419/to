import requests
from PySide6.QtWidgets import QMessageBox


class RN_Client:
    def __init__(self, server_url, client_id, username):
        self.server_url = server_url
        self.client_id = client_id  # 使用传入的client_id
        self.username = username

    def check_permissions(self):
        """向服务器请求权限"""
        try:
            response = requests.get(
                f"{self.server_url}/get_permissions",
                params={'username': self.username}
            )
            response.raise_for_status()
            result = response.json()
            if result['status'] == 'success' and result['permissions'] == 1:
                return True
            else:
                return False
        except requests.RequestException as e:
            print(f"Error checking permissions: {e}")
            return False

    def get_all_rn_records(self):
        try:
            response = requests.get(
                f"{self.server_url}/rn_records",
                params={'client_id': self.client_id},  # 将client_id作为请求参数传递
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching RN records: {e}")
            return []

    def get_rn_record(self, issue_number):
        try:
            response = requests.get(
                f"{self.server_url}/rn_record/{issue_number}",
                params={'client_id': self.client_id}  # 将client_id作为请求参数传递
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching RN record with issue number {issue_number}: {e}")
            return None

    def save_rn_record(self, record_data):
        if not self.check_permissions():
            QMessageBox.warning(None, "权限错误", "您没有权限执行此操作")
            return None

        try:
            # 确保 '问题单号' 存在于发送的数据中
            issue_number = record_data.get('问题单号')
            if not issue_number:
                raise ValueError("记录数据必须包含 '问题单号' 字段")

            # 添加client_id到发送的数据中
            record_data['client_id'] = self.client_id

            response = requests.post(f"{self.server_url}/rn_record", json=record_data)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as e:
            print(f"Error saving RN record: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.content}")
            return None

    def delete_rn_record(self, issue_number):
        if not self.check_permissions():
            QMessageBox.warning(None, "权限错误", "您没有权限执行此操作")
            return None

        try:
            response = requests.delete(
                f"{self.server_url}/rn_record/{issue_number}",
                params={'client_id': self.client_id}  # 将client_id作为请求参数传递
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error deleting RN record with issue number {issue_number}: {e}")
            return None

    def check_issue_number_exists(self, issue_number):
        try:
            response = requests.get(
                f"{self.server_url}/rn_record_exists/{issue_number}",
                params={'client_id': self.client_id}  # 将client_id作为请求参数传递
            )
            response.raise_for_status()
            return response.json().get('exists', False)
        except requests.RequestException as e:
            print(f"Error checking if issue number exists: {e}")
            return False
