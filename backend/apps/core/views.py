from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from .models import UserProfile
from django.contrib.auth.decorators import login_required


def register_view(request):
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully!")
            return redirect('login')
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        role = request.POST.get("role")
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            profile = UserProfile.objects.get(user=user)

            # Prevent teachers from logging into parent tab and vice versa
            if role == "teacher" and not profile.is_teacher:
                messages.warning(request, "Attention: You are using a Parent account. Please switch to the Parent login tab.")
                return redirect("login")
            elif role == "parent" and profile.is_teacher:
                messages.warning(request, "Attention: You are using a Teacher account. Please switch to the Teacher login tab.")
                return redirect("login")

            login(request, user)
            
            if profile.is_teacher:
                return redirect("home")
            else:
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
def parent_behavior(request):
    return render(request, 'parents/behavior.html')

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
def teacher_behavior(request):
    return render(request, 'teachers/behavior.html')

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
