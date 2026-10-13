# Deployment Guide: PythonAnywhere + Aiven Database

This guide explains how to deploy the **BMV3 Child Development and Daycare System** to **PythonAnywhere** connected to a managed **Aiven Database** (PostgreSQL or MySQL).

---

## Architecture Overview

- **Host**: PythonAnywhere (WSGI Web App)
- **Database**: Aiven Cloud Database (PostgreSQL with SSL enabled)
- **Frontend**: Pre-compiled React + Django templates served via WhiteNoise & PythonAnywhere static server
- **Email**: Brevo HTTP API (compatible with PythonAnywhere proxy)

---

## ⚠️ Important Note About PythonAnywhere Plans & External Databases

> [!IMPORTANT]
> - **Paid Account (Hacker $5/mo or custom)**: PythonAnywhere has unrestricted outbound TCP connections. Connecting directly to Aiven (PostgreSQL/MySQL) works immediately!
> - **Free Account ("Beginner")**: PythonAnywhere free accounts restrict outbound internet to an HTTP/HTTPS whitelist only and **block external database TCP ports** (e.g., Aiven port 10000+).
>   - If you are on the **Free tier**, you have two options:
>     1. **Option A (Recommended for Free Tier)**: Use PythonAnywhere's built-in **MySQL** database (found in the "Databases" tab of your PythonAnywhere dashboard) or **SQLite** (`db.sqlite3`).
>     2. **Option B**: Upgrade to the Hacker plan ($5/mo) to unlock external outbound TCP connections to Aiven.

---

## Step 1: Push Local Code to GitHub

If running locally on your computer in Git Bash or PowerShell:

```bash
git push origin main
```

If prompted for credentials, use your GitHub **Username** and a **Personal Access Token (Classic)** with the `repo` scope (generate one at [github.com/settings/tokens](https://github.com/settings/tokens)).

---

## Step 2: Get Your Aiven Database Service URI

1. Log into your [Aiven Console](https://console.aiven.io/).
2. Create or open your **PostgreSQL** (or **MySQL**) service.
3. In the **Overview** tab, find the **Service URI**.
   - It will look like:
     ```
     postgres://avnadmin:your_password@your-host.aivencloud.com:12345/defaultdb?sslmode=require
     ```
4. Copy this Service URI.

---

## Step 3: PythonAnywhere Setup via Bash Console

Open a **Bash Console** from your PythonAnywhere dashboard:

### 1. Clone Your Repository
```bash
git clone https://github.com/Hiro20671/DJANGO-REACT-CAPSTONE-SYSTEM.git
cd DJANGO-REACT-CAPSTONE-SYSTEM
```
*(If the folder already exists, run `cd DJANGO-REACT-CAPSTONE-SYSTEM && git pull origin main`)*

### 2. Create and Activate a Python 3.12 Virtual Environment
```bash
mkvirtualenv --python=/usr/bin/python3.12 bmv3-env
```
*(If already created in the future, activate with: `workon bmv3-env`)*

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

### 4. Run Migrations on Aiven Database
Export your environment variables temporarily in the console to run migrations and seed data:

```bash
export DJANGO_SETTINGS_MODULE=config.settings.prod
export DATABASE_URL="postgres://avnadmin:your_password@your-host.aivencloud.com:12345/defaultdb?sslmode=require"

cd backend
python manage.py migrate
```

### 5. (Optional) Create Superuser or Seed Initial Data
```bash
python manage.py createsuperuser
# Or to seed demo parents and historical school years:
python manage.py setup_demo_data
```

### 6. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

---

## Step 4: Configure the PythonAnywhere "Web" Tab

Navigate to the **Web** tab in your PythonAnywhere dashboard:

### 1. Create a Web App
- Click **Add a new web app**.
- Choose **Manual configuration** (do NOT choose Django automated wizard, as we already have our project configured).
- Select **Python 3.12**.

### 2. Set Paths
Scroll to the **Code** section:
- **Source code**:
  `/home/<your_username>/DJANGO-REACT-CAPSTONE-SYSTEM/backend`
- **Working directory**:
  `/home/<your_username>/DJANGO-REACT-CAPSTONE-SYSTEM/backend`

Scroll to the **Virtualenv** section:
- **Virtualenv**:
  `/home/<your_username>/.virtualenvs/bmv3-env`

### 3. Configure the WSGI Configuration File
Click on the link for the **WSGI configuration file** (e.g., `/var/www/<your_username>_pythonanywhere_com_wsgi.py`).

Delete all default boilerplate code and replace it with:

```python
import os
import sys

# 1. Project path
path = '/home/<your_username>/DJANGO-REACT-CAPSTONE-SYSTEM/backend'
if path not in sys.path:
    sys.path.append(path)

# 2. Production settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.prod'
os.environ['DEBUG'] = 'False'
os.environ['SECRET_KEY'] = 'replace-with-a-random-secret-string-at-least-50-chars'

# 3. Aiven Database URL
os.environ['DATABASE_URL'] = 'postgres://avnadmin:your_password@your-host.aivencloud.com:12345/defaultdb?sslmode=require'

# 4. Email configuration (Optional, Brevo HTTP API)
# os.environ['BREVO_API_KEY'] = 'your-brevo-api-key'
# os.environ['DEFAULT_FROM_EMAIL'] = 'your-email@example.com'

# 5. Serve Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```
*(Remember to replace `<your_username>` and `<your_password>` with your real credentials!)*

Click **Save**.

### 4. Configure Static Files Mappings
In the **Static files** section of the **Web** tab, add the following mappings:

| URL | Directory |
| :--- | :--- |
| `/static/` | `/home/<your_username>/DJANGO-REACT-CAPSTONE-SYSTEM/backend/staticfiles` |
| `/media/` | `/home/<your_username>/DJANGO-REACT-CAPSTONE-SYSTEM/backend/media` |

---

## Step 5: Reload and Test Your Web Application

1. At the very top of the **Web** tab, click the big green **Reload <your_username>.pythonanywhere.com** button.
2. Visit `https://<your_username>.pythonanywhere.com`.
3. Log in with your admin or teacher credentials.

---

## Useful Maintenance Commands

Whenever you push new updates to GitHub in the future:
1. Open PythonAnywhere Bash Console:
   ```bash
   cd ~/DJANGO-REACT-CAPSTONE-SYSTEM
   git pull origin main
   workon bmv3-env
   cd backend
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```
2. Go to the **Web** tab and click **Reload**.
