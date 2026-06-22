from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import UserProfile
from django.contrib.auth.decorators import login_required

@never_cache
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        from django.contrib.auth.models import User
        user = None
        if username and '@' in username:
            # Gather all candidate users that have this email address
            candidate_users = list(User.objects.filter(email__iexact=username))
            
            # Fallback to look up email in Child guardian contacts
            from django.db.models import Q
            from .models import Child
            matching_children = Child.objects.filter(
                Q(mother_email__iexact=username) |
                Q(father_email__iexact=username) |
                Q(other_guardian_email__iexact=username) |
                Q(email__iexact=username)
            )
            for child in matching_children:
                for profile in child.parents.all():
                    if profile.user and profile.user not in candidate_users:
                        candidate_users.append(profile.user)
            
            # Try to authenticate each candidate user
            for candidate in candidate_users:
                authenticated_user = authenticate(request, username=candidate.username, password=password)
                if authenticated_user:
                    user = authenticated_user
                    break
        
        # If no user authenticated via email candidates, fall back to standard username authentication
        if not user:
            user = authenticate(request, username=username, password=password)

        if user:
            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                # Fallback if somehow UserProfile is missing, default to parent or teacher
                profile = None

            login(request, user)
            
            if profile and profile.is_teacher:
                return redirect("home")
            else:
                if profile and profile.first_login:
                    return redirect("force_password_change")
                return redirect("parent_home")

        messages.error(request, "Invalid username or password")

    return render(request, "login.html")

@login_required
def parent_home(request):
    profile = request.user.userprofile
    if profile.is_teacher:
        return redirect("home")
    return render(request, "parents/parent_home.html")

@login_required
def parent_dashboard(request):
    profile = request.user.userprofile
    if profile.is_teacher:
        return redirect("home")
    return render(request, "parents/parent_dashboard.html")

@login_required
def parent_dropoff_pickup(request):
    return render(request, 'parents/drop_off_pick_up.html')

@login_required
def parent_attendance(request):
    return render(request, 'parents/attendance.html')

@login_required
def parent_milestones(request):
    return render(request, 'parents/milestones.html')


@login_required
def parent_engagement(request):
    return render(request, 'parents/parent_engagement.html')

@login_required
def parent_nutrition(request):
    return render(request, 'parents/nutrition.html')

@login_required
def parent_settings(request):
    return render(request, 'parents/parent_settings.html')

@login_required
def parent_children(request):
    return render(request, 'parents/children.html')

@login_required
def parent_force_password_change(request):
    return render(request, 'parents/force_password_change.html')

def home_view(request):
    return render(request, 'teachers/home.html')

@login_required
def teacher_dashboard(request):
    return render(request, 'teachers/dashboard.html')

@login_required
def teacher_dropoff_pickup(request):
    return render(request, 'teachers/drop_off_pick_up.html')

@login_required
def teacher_attendance(request):
    return render(request, 'teachers/attendance.html')

@login_required
def teacher_milestones(request):
    return render(request, 'teachers/milestones.html')


@login_required
def teacher_engagement(request):
    return render(request, 'teachers/parent_engagement.html')

@login_required
def teacher_nutrition(request):
    return render(request, 'teachers/nutrition.html')

@login_required
def teacher_children(request):
    return render(request, 'teachers/children.html')

@login_required
def teacher_settings(request):
    return render(request, 'teachers/settings.html')

def offline_view(request):
    return render(request, 'offline.html')

@login_required
def teacher_activities(request):
    return render(request, 'teachers/activities.html')

@login_required
def parent_activities(request):
    return render(request, 'parents/activities.html')

