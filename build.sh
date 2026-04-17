#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Build the Vite React Frontend
echo "Building Vite Frontend..."
cd frontend
npm install
npm run build
cd ..

# 2. Build the Django Backend
echo "Building Django Backend..."
cd backend
pip install -r requirements.txt

# 3. Collect Static Files (this pulls in the React build from static/react)
python manage.py collectstatic --no-input

# 4. Migrate the Database
python manage.py migrate
