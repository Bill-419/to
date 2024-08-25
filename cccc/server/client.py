import requests
import json
from concurrent.futures import ThreadPoolExecutor

class DataClient:
    def __init__(self, server_url, table_name, client_id):
        self.client_id = client_id
        self.server_url = server_url
        self.table_name = table_name
        self.executor = ThreadPoolExecutor(max_workers=10)

    def _async_request(self, method, endpoint, payload=None, params=None):
        url = f"{self.server_url}/{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=10)
            else:
                response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"HTTP request failed: {e}")
            return {"error": str(e), "status": "request_error"}
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return {"error": "Invalid JSON response", "status": "response_error"}

    def get_permissions(self, username):
        params = {'username': username}
        future = self.executor.submit(self._async_request, "GET", "get_permissions", params=params)
        result = future.result()
        if "status" in result and result["status"] == "success":
            permissions = result.get("permissions")
            if permissions is not None:
                return int(permissions)
            else:
                print("Permissions not found for user:", username)
                return 0

    def save_all(self, data, merged_cells):
        payload = {
            "table_name": self.table_name,
            "data": data,
            "merged_cells": merged_cells,
            "client_id": self.client_id
        }
        future = self.executor.submit(self._async_request, "POST", "save_all", payload=payload)
        return future.result()

    def get_all(self):
        future = self.executor.submit(self._async_request, "POST", "get_all", payload={"table_name": self.table_name})
        return future.result()

    def save_table(self, data):
        payload = {
            "table_name": self.table_name,
            "data": data
        }
        future = self.executor.submit(self._async_request, "POST", "save_table", payload=payload)
        return future.result()

    def get_table(self):
        future = self.executor.submit(self._async_request, "POST", "get_table", payload={"table_name": self.table_name})
        return future.result()

    def save_merged_cells(self, merged_cells):
        payload = {
            "table_name": self.table_name,
            "merged_cells": merged_cells
        }
        future = self.executor.submit(self._async_request, "POST", "save_merged_cells", payload=payload)
        return future.result()

    def get_merged_cells(self):
        future = self.executor.submit(self._async_request, "POST", "get_merged_cells", payload={"table_name": self.table_name})
        return future.result()

    def append_table(self, data):
        payload = {
            "table_name": self.table_name,
            "data": data
        }
        future = self.executor.submit(self._async_request, "POST", "append_table", payload=payload)
        return future.result()

