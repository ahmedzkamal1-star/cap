import os
import subprocess
import sys

def run_command(command):
    print(f"Running: {command}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error: {stderr.decode()}")
    else:
        print(stdout.decode())

def setup():
    print("🚀 Starting Automatic Deployment for Mr7Riko...")

    # 1. Create Virtual Environment
    print("📦 Creating virtualenv...")
    run_command("mkvirtualenv --python=/usr/bin/python3.10 myenv")

    # 2. Install Requirements
    print("📚 Installing dependencies...")
    run_command("pip install -r requirements.txt")

    # 3. Initialize Database
    print("🗄️ Initializing remote database...")
    # This assumes the user has already created the DB via dashboard
    run_command("python init_db.py")

    print("\n✅ Setup complete!")
    print("Next Steps:")
    print("1. Go to the 'Web' tab on PythonAnywhere.")
    print("2. Set the 'Virtualenv' path to: /home/Mr7Riko/.virtualenvs/myenv")
    print("3. Update the 'WSGI configuration file' with the content of pa_wsgi_config.py")
    print("4. Click 'Reload' and visit Mr7Riko.pythonanywhere.com")

if __name__ == "__main__":
    setup()
