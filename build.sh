#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "==> Step 1: Building React Frontend with Vite..."
cd frontend
npm install
npm run build
cd ..

echo "==> Step 2: Installing Python Dependencies..."
pip install -r backend/requirements.txt

echo "==> Step 3: Collecting Static Files..."
cd backend
python manage.py collectstatic --noinput

echo "==> Step 4: Running Database Migrations..."
python manage.py migrate

echo "==> Build Completed Successfully!"
