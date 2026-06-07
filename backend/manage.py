import os
import sys
import subprocess

def start_frontend_dev_server():
    # Launch the React/Vite dev server in a separate subprocess
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    # Use CREATE_NEW_PROCESS_GROUP on Windows to avoid signal propagation
    try:
        subprocess.Popen(['npm', 'run', 'dev'], cwd=frontend_path, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP, shell=True)
    except Exception as e:
        print(f'Failed to start frontend dev server: {e}')

"""Django's command-line utility for administrative tasks."""




def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
    start_frontend_dev_server()
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
