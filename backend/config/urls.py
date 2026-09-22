"""
URL configuration for bmv3_childcare project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:(bmv3-env) 13:34 ~/DJANGO-REACT-CAPSTONE-SYSTEM/backend (main)$ tail -n 25 /var/log/jeremy2004.pythonanywhere.com.server.log
2026-09-14 13:42:12 building mime-types dictionary from file /etc/mime.types...
2026-09-14 13:42:12 1516 entry found
2026-09-14 13:42:12 lock engine: pthread robust mutexes
2026-09-14 13:42:12 thunder lock: disabled (you can enable it with --thunder-lock)
2026-09-14 13:42:12 uwsgi socket 0 bound to UNIX address /var/sockets/jeremy2004.pythonanywhere.com/socket fd 3
2026-09-14 13:42:12 Python version: 3.13.1 (main, Jan 16 2025, 13:50:41) [GCC 11.4.0]
2026-09-14 13:42:12 PEP 405 virtualenv detected: /home/Jeremy2004/.virtualenvs/bmv3-env
2026-09-14 13:42:12 Set PythonHome to /home/Jeremy2004/.virtualenvs/bmv3-env
2026-09-14 13:42:12 Python main interpreter initialized at 0x79c40f3b0ab0
2026-09-14 13:42:12 python threads support enabled
2026-09-14 13:42:12 your server socket listen backlog is limited to 100 connections
2026-09-14 13:42:12 your mercy for graceful operations on workers is 60 seconds
2026-09-14 13:42:12 setting request body buffering size to 65536 bytes
2026-09-14 13:42:12 mapped 334256 bytes (326 KB) for 1 cores
2026-09-14 13:42:12 *** Operational MODE: single process ***
2026-09-14 13:42:12 initialized 38 metrics
2026-09-14 13:42:12 WSGI app 0 (mountpoint='') ready in 2 seconds on interpreter 0x79c40f3b0ab0 pid: 1 (default app)
2026-09-14 13:42:12 *** uWSGI is running in multiple interpreter mode ***
2026-09-14 13:42:12 gracefully (RE)spawned uWSGI master process (pid: 1)
2026-09-14 13:42:12 spawned uWSGI worker 1 (pid: 2, cores: 1)
2026-09-14 13:42:12 metrics collector thread started
2026-09-14 13:42:12 spawned 2 offload threads for uWSGI worker 1
2026-09-14 13:42:12 announcing my loyalty to the Emperor...
2026-09-14 13:42:51 Failed to send email to jeremybryanvillanueva@gmail.com: SendinBlue API response 401 (Unauthorized):#012{#012  "message": "Key not found",#012  "code": "
unauthorized"#012}
2026-09-14 13:42:51 
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
