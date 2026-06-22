# PythonAnywhere Deployment Guide

This guide outlines the step-by-step process to deploy your **DJANGO-REACT-CAPSTONE-SYSTEM** on **PythonAnywhere**.

---

## 1. Vercel vs. PythonAnywhere Hosting Choice

> [!NOTE]
> **You only need to deploy to PythonAnywhere.**
> Because your React code compiles directly into Django's static files directory and is served by Django's template engine, your system is fully integrated. Separating the frontend to Vercel is unnecessary, complex (requires CORS and separate API endpoints), and not recommended for this architecture.

---

## 2. Deployment Steps on PythonAnywhere

### Step A: Clone the Repository & Setup
1. Log in to [PythonAnywhere](https://www.pythonanywhere.com/).
2. Go to the **Consoles** tab and open a new **Bash Console**.
3. Clone your GitHub repository:
   ```bash
   git clone https://github.com/Hiro20671/DJANGO-REACT-CAPSTONE-SYSTEM.git
   ```
4. Navigate into the project folder:
   ```bash
   cd ~/DJANGO-REACT-CAPSTONE-SYSTEM
   ```

### Step B: Setup Virtual Environment & Install Dependencies
1. Create a Python 3.10 virtual environment (matching your local python environment):
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 bmv3-env
   ```
2. Install the backend Python dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

### Step C: Static Files Setup
1. Move to the backend folder:
   ```bash
   cd ~/DJANGO-REACT-CAPSTONE-SYSTEM/backend
   ```
2. Compile and collect all static assets (React bundle, CSS, images) into a single folder for PythonAnywhere's web server:
   ```bash
   python manage.py collectstatic --noinput
   ```

### Step D: Database Setup
You have two choices for your SQLite database:
* **Option 1 (Fresh Start)**: Run migrations to create a brand-new empty database:
  ```bash
  python manage.py migrate
  ```
* **Option 2 (Recommended - Migrate Local Data)**: Since SQLite is self-contained in a single file, you can upload your local `db.sqlite3` file directly to PythonAnywhere:
  1. Go to the **Files** tab on the PythonAnywhere dashboard.
  2. Navigate to: `DJANGO-REACT-CAPSTONE-SYSTEM / backend`.
  3. Click **Upload a file** on the right side.
  4. Select the `db.sqlite3` file from your local `c:\BACKUP CAPSTONE SYSTEM DJANGO-REACT\backend` folder.

---

## 3. Configure the PythonAnywhere Web App

1. Go to the **Web** tab on the PythonAnywhere dashboard.
2. Click **Add a new web app**.
3. Click **Next** -> Choose **Manual Configuration** (Do NOT choose "Django" as we want to use our existing config).
4. Choose **Python 3.10** -> Click **Next**.
5. Once created, update the following configurations:

### Code Settings
* **Source code**: `/home/<your-username>/DJANGO-REACT-CAPSTONE-SYSTEM/backend`
* **Working directory**: `/home/<your-username>/DJANGO-REACT-CAPSTONE-SYSTEM/backend`

### WSGI Configuration File
1. Under **Code**, click on the **WSGI configuration file** link (usually `/var/www/<your-username>_pythonanywhere_com_wsgi.py`).
2. Delete its entire contents and replace them with:
   ```python
   import os
   import sys

   # Path to your project directory
   path = '/home/<your-username>/DJANGO-REACT-CAPSTONE-SYSTEM/backend'
   if path not in sys.path:
       sys.path.insert(0, path)

   # Set environment variables for production
   os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.prod'

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
3. Click **Save** (top right) and close the tab.

### Virtualenv Settings
* **Virtualenv**: `/home/<your-username>/.virtualenvs/bmv3-env`

### Static Files Mappings (Crucial for styling/media loading)
Under the **Static files** section, add these two rows:

| URL | Path | Description |
| :--- | :--- | :--- |
| `/static/` | `/home/<your-username>/DJANGO-REACT-CAPSTONE-SYSTEM/backend/staticfiles` | Production static files |
| `/media/` | `/home/<your-username>/DJANGO-REACT-CAPSTONE-SYSTEM/backend/media` | Uploaded assets/avatars |

---

## 4. Launch the App

1. Scroll to the top of the **Web** tab page.
2. Click the green **Reload <your-username>.pythonanywhere.com** button.
3. Access your web app at `http://<your-username>.pythonanywhere.com/`!

---

## 5. Setting Up Email Notifications (Brevo / SMTP)

Your system has a smart email routing logic built into `base.py` settings:
* **PythonAnywhere Free Tier**: Direct SMTP connections (port 587) are blocked. You **must** use the **Brevo HTTP API** (via `django-anymail`), which communicates over whitelisted HTTPS.
* **PythonAnywhere Paid Tier / Local**: You can use either the Brevo HTTP API or standard SMTP.

### How to set your Email Credentials:
The most reliable way to set environment variables on PythonAnywhere is to put them directly in your **WSGI configuration file** (under the **Web** tab).

1. Go to the **Web** tab on PythonAnywhere.
2. Click your WSGI configuration file link under **Code**.
3. Add your keys at the bottom of the file (before getting the application):

```python
import os
import sys

path = '/home/<your-username>/DJANGO-REACT-CAPSTONE-SYSTEM/backend'
if path not in sys.path:
    sys.path.insert(0, path)

# ----------------- EMAIL CONFIGURATION -----------------
# Option A: Brevo HTTP API (Recommended - Works on FREE and PAID tiers)
os.environ['BREVO_API_KEY'] = 'your-actual-brevo-api-key-here'

# Option B: SMTP Relaying (Works on PAID tiers only)
# os.environ['EMAIL_HOST_USER'] = 'your-smtp-email@example.com'
# os.environ['EMAIL_HOST_PASSWORD'] = 'your-smtp-password'
# -------------------------------------------------------

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.prod'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

4. Click **Save** and **Reload** your web app on the **Web** tab.
