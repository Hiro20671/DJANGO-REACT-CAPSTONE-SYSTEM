from django.contrib import admin
from django.urls import path
from . import views, api_views

urlpatterns = [
    path('', views.login_view, name='login'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dropoff-pickup/', views.teacher_dropoff_pickup, name='teacher_dropoff_pickup'),
    path('attendance/', views.teacher_attendance, name='teacher_attendance'),
    path('milestones/', views.teacher_milestones, name='teacher_milestones'),
    path('behavior/', views.teacher_behavior, name='teacher_behavior'),
    path('engagement/', views.teacher_engagement, name='teacher_engagement'),
    path('nutrition/', views.teacher_nutrition, name='teacher_nutrition'),
    path('children/', views.teacher_children, name='teacher_children'),
    path("parent/home/", views.parent_home, name="parent_home"),

    path("parent/dashboard/", views.parent_dashboard, name="parent_dashboard"),
    path('parent/dropoff-pickup/', views.parent_dropoff_pickup, name='parent_dropoff_pickup'),
    path('parent/attendance/', views.parent_attendance, name='parent_attendance'),
    path('parent/milestones/', views.parent_milestones, name='parent_milestones'),
    path('parent/behavior/', views.parent_behavior, name='parent_behavior'),
    path('parent/engagement/', views.parent_engagement, name='parent_engagement'),
    path('parent/nutrition/', views.parent_nutrition, name='parent_nutrition'),
    path('parent/children/', views.parent_children, name='parent_children'),
    path('parent/settings/', views.parent_settings, name='parent_settings'),
    path('settings/', views.teacher_settings, name='teacher_settings'),
    
    # API Endpoints
    path('api/teacher/dashboard/', api_views.TeacherDashboardStatsAPIView.as_view(), name='api_teacher_dashboard'),
    path('api/parent/dashboard/', api_views.ParentDashboardStatsAPIView.as_view(), name='api_parent_dashboard'),
    path('api/children/', api_views.ChildListAPIView.as_view(), name='api_children_list'),
]
