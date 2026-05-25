from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from . import views
from .api_views import (
    ChildViewSet, AttendanceRecordViewSet, MilestoneRecordViewSet, NutritionRecordViewSet,
    SchoolYearViewSet, EngagementRecordViewSet,
    ParentHistoryAPIView, ParentListAPIView, UserSettingsAPIView, ParentDashboardStatsAPIView,
    TeacherDashboardStatsAPIView, UpdateChildProfileAPIView, NutritionAnalyticsAPIView,
    UpdateUsernameAPIView, RequestPasswordChangeAPIView, VerifyPasswordChangeAPIView,
    GenerateParentAccountAPIView, ForcePasswordChangeAPIView, VerifyOTPOnlyAPIView,
    link_guardian_profile, NoClassDayViewSet,
    ECCDDomainViewSet, ECCDMilestoneViewSet, ECCDAssessmentViewSet, ECCDMilestoneScoreViewSet,
    ECCDReportAPIView, ECCDOverallReportAPIView, ScoringAccessRequestViewSet
)

router = DefaultRouter()
router.register(r'children', ChildViewSet, basename='child')
router.register(r'attendance', AttendanceRecordViewSet, basename='attendance')
router.register(r'milestones', MilestoneRecordViewSet, basename='milestone')
router.register(r'nutrition', NutritionRecordViewSet, basename='nutrition')
router.register(r'engagement', EngagementRecordViewSet, basename='engagement')
router.register(r'school-years', SchoolYearViewSet, basename='school_year')
router.register(r'no-class-days', NoClassDayViewSet, basename='no_class_day')
router.register(r'eccd-domains', ECCDDomainViewSet, basename='eccd_domain')
router.register(r'eccd-milestones', ECCDMilestoneViewSet, basename='eccd_milestone')
router.register(r'eccd-assessments', ECCDAssessmentViewSet, basename='eccd_assessment')
router.register(r'eccd-scores', ECCDMilestoneScoreViewSet, basename='eccd_score')
router.register(r'scoring-requests', ScoringAccessRequestViewSet, basename='scoring_request')

urlpatterns = [
    path('', views.login_view, name='login'),

    path('login/', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dropoff-pickup/', views.teacher_dropoff_pickup, name='teacher_dropoff_pickup'),
    path('attendance/', views.teacher_attendance, name='teacher_attendance'),
    path('milestones/', views.teacher_milestones, name='teacher_milestones'),
    path('engagement/', views.teacher_engagement, name='teacher_engagement'),
    path('nutrition/', views.teacher_nutrition, name='teacher_nutrition'),
    path('children/', views.teacher_children, name='teacher_children'),
    path("parent/home/", views.parent_home, name="parent_home"),

    path("parent/dashboard/", views.parent_dashboard, name="parent_dashboard"),
    path('parent/dropoff-pickup/', views.parent_dropoff_pickup, name='parent_dropoff_pickup'),
    path('parent/attendance/', views.parent_attendance, name='parent_attendance'),
    path('parent/milestones/', views.parent_milestones, name='parent_milestones'),
    path('parent/engagement/', views.parent_engagement, name='parent_engagement'),
    path('parent/nutrition/', views.parent_nutrition, name='parent_nutrition'),
    path('parent/children/', views.parent_children, name='parent_children'),
    path('parent/settings/', views.parent_settings, name='parent_settings'),
    path('parent/force-password-change/', views.parent_force_password_change, name='force_password_change'),
    path('settings/', views.teacher_settings, name='teacher_settings'),
    
    # API Endpoints
    path('sw.js', TemplateView.as_view(template_name='sw.js', content_type='application/javascript'), name='sw_js'),
    path('manifest.json', TemplateView.as_view(template_name='manifest.json', content_type='application/json'), name='manifest_json'),
    path('api/parent/history/', ParentHistoryAPIView.as_view(), name='api_parent_history'),
    path('api/parents/', ParentListAPIView.as_view(), name='api_parents'),
    # Existing API endpoints
    path('api/teacher/dashboard/', TeacherDashboardStatsAPIView.as_view(), name='api_teacher_dashboard'),
    path('api/parent/dashboard/', ParentDashboardStatsAPIView.as_view(), name='api_parent_dashboard'),
    path('api/user/settings/', UserSettingsAPIView.as_view(), name='api_user_settings'),
    path('api/children/<int:child_id>/update_profile/', UpdateChildProfileAPIView.as_view(), name='api_child_update_profile'),
    path('api/nutrition-analytics/', NutritionAnalyticsAPIView.as_view(), name='api_nutrition_analytics'),
    path('api/generate_parent_account/', GenerateParentAccountAPIView.as_view(), name='api_generate_parent_account'),
    path('api/force-password-change/', ForcePasswordChangeAPIView.as_view(), name='api_force_password_change'),
    path('api/request-password-change/', RequestPasswordChangeAPIView.as_view(), name='api_request_password_change'),
    path('api/verify-password-change/', VerifyPasswordChangeAPIView.as_view(), name='api_verify_password_change'),
    path('api/verify-otp-only/', VerifyOTPOnlyAPIView.as_view(), name='api_verify_otp_only'),
    path('api/link_guardian/', link_guardian_profile, name='api_link_guardian'),
    path('api/eccd-report/<int:assessment_id>/', ECCDReportAPIView.as_view(), name='api_eccd_report'),
    path('api/eccd-report/overall/<int:child_id>/', ECCDOverallReportAPIView.as_view(), name='api_eccd_overall_report'),
    path('api/', include(router.urls)),
]
