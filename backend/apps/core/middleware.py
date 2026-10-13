from django.shortcuts import redirect
from django.http import JsonResponse
from django.urls import reverse
from apps.core.models import UserProfile

class FirstLoginRequiredMiddleware:
    """
    Middleware that enforces mandatory password change for parent accounts on first login.
    Blocks parents with `first_login=True` from navigating to the parent dashboard,
    normal parent pages, or accessing private child APIs until they update their temporary password.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                profile = getattr(request.user, 'userprofile', None)
                if not profile:
                    profile = UserProfile.objects.filter(user=request.user).first()
            except Exception:
                profile = None

            if profile and not profile.is_teacher and profile.is_account_restricted:
                from django.contrib.auth import logout
                from django.contrib import messages
                logout(request)
                if request.path.startswith('/api/'):
                    return JsonResponse({
                        'error': 'This parent account is no longer active. Please contact the daycare administrator if you need assistance.'
                    }, status=403)
                messages.error(request, "This parent account is no longer active. Please contact the daycare administrator if you need assistance.")
                return redirect('login')

            if profile and not profile.is_teacher and profile.first_login:
                path = request.path
                exempt_paths = [
                    '/parent/force-password-change/',
                    '/api/force-password-change/',
                    '/logout/',
                    '/static/',
                    '/media/',
                    '/favicon.ico',
                ]
                
                # Check if current path is exempt
                if not any(path.startswith(p) for p in exempt_paths):
                    if path.startswith('/api/'):
                        return JsonResponse({
                            'error': 'Mandatory password change required before accessing the system.',
                            'must_change_password': True
                        }, status=403)
                    return redirect('force_password_change')

        return self.get_response(request)
