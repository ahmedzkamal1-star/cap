import requests
import json
import os

# Base URL - Set to your PythonAnywhere URL
BASE_URL = "https://your-username.pythonanywhere.com"

class AuthManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuthManager, cls).__new__(cls)
            cls._instance.token = None
            cls._instance.user_data = {}
            cls._instance.device_id = "MOBILE_DEMO_01" # In production, get real hardware ID
        return cls._instance

    def login(self, code, password):
        try:
            payload = {
                "code": code,
                "password": password,
                "device_id": self.device_id
            }
            response = requests.post(f"{BASE_URL}/api/login", json=payload, timeout=10)
            
            if response.status_code == 200:
                self.user_data = response.json()
                self.token = self.user_data.get('token')
                return True, "Success"
            else:
                try:
                    error_msg = response.json().get('error', 'Login failed')
                except:
                    error_msg = f"Server Error: {response.status_code}"
                return False, error_msg
        except Exception as e:
            return False, f"Connection Error: {str(e)}"

    def report_violation(self, reason, details):
        if not self.token:
            return False
            
        try:
            payload = {
                "reason": reason,
                "details": details
            }
            # Use cookie-based or token-based auth (since we use login_user on server)
            # For simplicity in this demo, we assume the session is maintained or pass token
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(f"{BASE_URL}/api/report_violation", json=payload, headers=headers, timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}
