from django.http import HttpResponseForbidden

def teacher_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.userprofile.is_teacher:
            return HttpResponseForbidden("Access denied")
        return view_func(request, *args, **kwargs)
    return wrapper