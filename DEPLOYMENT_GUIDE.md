# Complete Deployment Guide: PythonAnywhere + Aiven Database + Brevo Email

This guide walks you through deploying the **BMV3 Child Development and Daycare System** to **PythonAnywhere**, connected to an **Aiven Managed Database**, with 100% working **Brevo Email Notifications**.

---

## 🔑 Crucial Notes Before Starting

### 1. Brevo Email on PythonAnywhere (Why It Errored Last Time)
- **The Problem:** PythonAnywhere blocks direct SMTP port `587`. If you use the SMTP key (`xsmtpsib-...`), connections to `smtp-relay.brevo.com:587` fail with network timeouts or connection refused errors.
- **The Solution:** Use **Brevo HTTP REST API (port 443)** via `django-anymail`, which is fully allowed through PythonAnywhere.
- **How to get the right Brevo Key:**
  1. Log into your [Brevo Dashboard](https://app.brevo.com/).
  2. Click your account name at the top right ➔ select **SMTP & API**.
  3. Go to the **API Keys** tab (⚠️ **NOT** the SMTP tab!).
  4. Click **Generate a new API key** (Name it e.g. `PythonAnywhere-Prod`).
  5. Copy the generated key. **It starts with `xkeysib-...`** (NOT `xsmtpsib-`).
  6. Use this as your `BREVO_API_KEY`.

### 2. Aiven Database on PythonAnywhere Plans
- **Paid PythonAnywhere Plan (Hacker $5/mo or higher):** Outbound TCP connections to external databases like Aiven work immediately.
- **Free PythonAnywhere Plan:** Free accounts block outbound TCP connections to external database hosts (like Aiven port 10000+). 
  - *If you are on the Free tier:* Use PythonAnywhere's built-in MySQL (in the "Databases" tab) or SQLite (`db.sqlite3`), OR upgrade to the $5/mo plan to connect to Aiven.

---

## Step 1: Push Local Changes to GitHub

On your local machine in Command Prompt, PowerShell, or Git Bash:

```bash
git push origin main
```

If prompted for authentication:
- **Username:** `Hiro20671`
- **Password:** Paste a GitHub **Personal Access Token (Classic)** with `repo` permissions (generate one at [github.com/settings/tokens](https://github.com/settings/tokens)).

---

## Step 2: Retrieve Your Aiven Database URI

1. In your [Aiven Console](https://console.aiven.io/), click on your PostgreSQL or MySQL service.
2. In the **Overview** tab, copy the **Service URI**.
   It looks like:
   ```
   postgres://avnadmin:your_password@your-service-name.aivencloud.com:12345/defaultdb?sslmode=require
   ```

---

## Step 3: PythonAnywhere Bash Console Setup

In your PythonAnywhere dashboard, open a **Bash Console**:

```bash
# 1. Clone repository (or pull latest changes if already cloned)
git clone https://github.com/Hiro20671/DJANGO-REACT-CAPSTONE-SYSTEM.git
cd DJANGO-REACT-CAPSTONE-SYSTEM

# If you already cloned it previously:
# cd ~/DJANGO-REACT-CAPSTONE-SYSTEM && git pull origin main

# 2. Create and activate a Python 3.12 virtual environment
mkvirtualenv --python=/usr/bin/python3.12 bmv3-env

# 3. Install dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# 4. Set environment variables to run migrations on Aiven
export DJANGO_SETTINGS_MODULE=config.settings.prod
export DATABASE_URL="postgres://avnadmin:your_password@your-service-name.aivencloud.com:12345/defaultdb?sslmode=require"
export BREVO_API_KEY="xkeysib-your-real-brevo-api-key"
export DEFAULT_FROM_EMAIL="jeremybryanvillanueva@gmail.com"

# 5. Run migrations & setup initial system data
cd backend
python manage.py migrate
python manage.py setup_demo_data
python manage.py createsuperuser

# 6. Collect all static files
python manage.py collectstatic --noinput
```

---

## Step 4: Configure the PythonAnywhere "Web" Tab

1. Navigate to the **Web** tab in PythonAnywhere.
2. Click **Add a new web app** ➔ Choose **Manual configuration** ➔ Select **Python 3.12**.
3. Under the **Code** section:
   - **Source code:** `/home/<your_username>/DJANGO-REACT-CAPSTONE-SYSTEM/backend`
   - **Working directory:** `/home/<your_username>/DJANGO-REACT-CAPSTONE-SYSTEM/backend`
4. Under the **Virtualenv** section:
   - Enter: `/home/<your_username>/.virtualenvs/bmv3-env`
5. Click on the **WSGI configuration file** link (e.g. `/var/www/<your_username>_pythonanywhere_com_wsgi.py`).
   Delete all boilerplate content and paste:

```python
import os
import sys

# 1. Add backend directory to sys.path
path = '/home/<your_username>/DJANGO-REACT-CAPSTONE-SYSTEM/backend'
if path not in sys.path:
    sys.path.append(path)

# 2. Production Settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.prod'
os.environ['DEBUG'] = 'False'
os.environ['SECRET_KEY'] = 'bmv3-super-secret-key-replace-with-random-chars-123456789'

# 3. Aiven Database URI (with SSL required)
os.environ['DATABASE_URL'] = 'postgres://avnadmin:your_password@your-service-name.aivencloud.com:12345/defaultdb?sslmode=require'

# 4. Brevo Email API Configuration (HTTP REST API via port 443)
os.environ['BREVO_API_KEY'] = 'xkeysib-your-real-brevo-api-key'
os.environ['DEFAULT_FROM_EMAIL'] = 'jeremybryanvillanueva@gmail.com'

# 5. Load Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```
*(Make sure to replace `<your_username>`, database credentials, and `xkeysib-...` with your actual values!)*

Click **Save** at the top right of the editor.

---

## Step 5: Static Files Mapping

Under the **Static files** section of the **Web** tab, configure:

| URL | Directory |
| :--- | :--- |
| `/static/` | `/home/<your_username>/DJANGO-REACT-CAPSTONE-SYSTEM/backend/staticfiles` |
| `/media/` | `/home/<your_username>/DJANGO-REACT-CAPSTONE-SYSTEM/backend/media` |

---

## Step 6: Test & Verify

1. Click the green **Reload <your_username>.pythonanywhere.com** button.
2. Open `https://<your_username>.pythonanywhere.com`.
3. Test logging in as Teacher / Admin.
4. Test triggering an email feature (e.g. requesting a password reset OTP or provisioning a parent account) — it will send via Brevo's HTTPS API seamlessly!
