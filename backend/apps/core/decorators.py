from django.shortcuts import redirect
from django.http import HttpResponseForbidden

def teacher_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        profile = getattr(request.user, 'userprofile', None)
        if not profile or not profile.is_teacher:
            return HttpResponseForbidden("Access denied. Teacher privileges required.")
        return view_func(request, *args, **kwargs)
    return wrapper

def parent_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        profile = getattr(request.user, 'userprofile', None)
        if profile and profile.is_teacher:
            return redirect('teacher_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper