"""
PythonAnywhere WSGI Configuration Template
-----------------------------------------
Copy and paste this content into your PythonAnywhere WSGI configuration file:
/var/www/<your_username>_pythonanywhere_com_wsgi.py

Replace `<your_username>` with your actual PythonAnywhere username,
and paste your Aiven Database Service URI into `DATABASE_URL`.
"""

import os
import sys

# 1. Add your project directory (containing manage.py) to sys.path
path = '/home/<your_username>/DJANGO-REACT-CAPSTONE-SYSTEM/backend'
if path not in sys.path:
    sys.path.append(path)

# 2. Production Environment Settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.prod'
os.environ['DEBUG'] = 'False'
os.environ['SECRET_KEY'] = 'bmv3-prod-capstone-secret-key-replace-with-random-chars'

# 3. Aiven Database Service URI (PostgreSQL or MySQL)
# Example: postgres://avnadmin:password@pg-xxx.aivencloud.com:12345/defaultdb?sslmode=require
os.environ['DATABASE_URL'] = 'postgres://avnadmin:your_password@your-aiven-host:your-port/defaultdb?sslmode=require'

# 4. Optional: Brevo Email API Key for system email alerts / parent invites
# os.environ['BREVO_API_KEY'] = 'xkeysib-your-key-here'

# 5. Serve Django WSGI Application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
