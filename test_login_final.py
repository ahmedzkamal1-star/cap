import requests

session = requests.Session()
login_url = 'http://127.0.0.1:5000/login'
dashboard_url = 'http://127.0.0.1:5000/dashboard'

payload = {
    'code': '231266',
    'password': '123456'
}

print(f"Attempting login to {login_url} with code: {payload['code']}")
response = session.post(login_url, data=payload, allow_redirects=False)

print(f"Status Code: {response.status_code}")
print(f"Headers: {response.headers}")

if response.status_code == 302:
    print(f"Login Success! Redirecting to: {response.headers.get('Location')}")
else:
    print("Login Failed.")
    # Check if there's a flash message in the HTML
    if "فشل تسجيل الدخول" in response.text:
        print("Error message found in HTML: 'فشل تسجيل الدخول'")
    else:
        print("Specific error message not found. Page content snippet:")
        print(response.text[:500])
