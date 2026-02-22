import sys
import os

# Add your project directory to the sys.path
path = '/home/Mr7Riko/StudentManagementSystem'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables for production
os.environ['PYTHONANYWHERE_DOMAIN'] = 'true'

from app import create_app
application = create_app()
