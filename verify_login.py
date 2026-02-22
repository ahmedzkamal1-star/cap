import requests

session = requests.Session()
login_url = 'http://127.0.0.1:5000/login'
dashboard_url = 'http://127.0.0.1:5000/dashboard'

payload = {
    'code': '2023001',
    'password': '123456'
}

response = session.post(login_url, data=payload)

print(f"Login Status Code: {response.status_code}")
print(f"Login URL after redirect: {response.url}")

if response.url == dashboard_url:
    print("SUCCESS: Logged in and redirected to dashboard.")
else:
    print("FAILURE: Did not redirect to dashboard.")
    if "فشل تسجيل الدخول" in response.text:
        print("Reason: Login failed message found.")
