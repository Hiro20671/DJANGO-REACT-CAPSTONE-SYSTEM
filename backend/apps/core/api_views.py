from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Child, UserProfile, AttendanceRecord, MilestoneRecord, NutritionRecord, SchoolYear, EngagementRecord, PasswordResetOTP, NoClassDay, ECCDDomain, ECCDMilestone, ECCDAssessment, ECCDMilestoneScore
from .serializers import ChildSerializer, AttendanceRecordSerializer, MilestoneRecordSerializer, NutritionRecordSerializer, SchoolYearSerializer, EngagementRecordSerializer, NoClassDaySerializer, ECCDDomainSerializer, ECCDMilestoneSerializer, ECCDAssessmentSerializer, ECCDMilestoneScoreSerializer
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from django.contrib.auth.models import User

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_parent_account(request):
    profile = getattr(request.user, 'userprofile', None)
    if not profile or not profile.is_teacher:
        return Response({'detail': 'Not authorized'}, status=403)
        
    email = request.data.get('email')
    
    if not email:
        return Response({'detail': 'Email is required'}, status=400)
        
    if User.objects.filter(email=email).exists():
        return Response({'detail': 'Email already in use'}, status=400)
        
    # Generate temporary credentials
    username = email.split('@')[0] + str(random.randint(100, 999))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    user = User.objects.create_user(username=username, email=email, password=password)
    user_profile = UserProfile.objects.create(user=user, is_teacher=False)
    
    # Check if a child_id was provided to link
    child_id = request.data.get('child_id')
    if child_id:
        try:
            child = Child.objects.get(id=child_id)
            child.parents.add(user_profile)
        except Child.DoesNotExist:
            pass # Or handle error if necessary
    
    from django.core.mail import send_mail
    
    try:
        subject = "BMV3 Childcare - Temporary Parent Account"
        message = f"Hello,\n\nA temporary parent account has been created for you.\n\nUsername: {username}\nPassword: {password}\n\nPlease log in and change your password.\n\nThank you!"
        send_mail(
            subject,
            message,
            "noreply@bmv3.com",
            [email],
            fail_silently=True
        )
    except Exception as e:
        print(f"Failed to send email: {e}")
        
    return Response({
        'message': 'Parent account generated successfully and credentials sent to email'
    })

class TeacherDashboardStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Child.objects.all()
        school_year_id = request.query_params.get('school_year')
        if school_year_id:
            qs = qs.filter(school_year_id=school_year_id)
            
        total_children = qs.count()
        present = qs.filter(attendance_status='Present').count()
        absent = qs.filter(attendance_status='Absent').count()
        late = qs.filter(attendance_status='Late').count()
        
        data = {
            'total_children': total_children,
            'attendance': {
                'present': present,
                'absent': absent,
                'late': late,
            }
        }
        return Response(data)

class ParentDashboardStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Parents only see their children's stats
        try:
            profile = request.user.userprofile
            qs = Child.objects.filter(parents=profile)
            school_year_id = request.query_params.get('school_year')
            if school_year_id:
                qs = qs.filter(school_year_id=school_year_id)
                
            total = qs.count()
            data = {
                'total_children': total,
                'attendance': {
                    'present': qs.filter(attendance_status='Present').count(),
                    'absent': qs.filter(attendance_status='Absent').count(),
                    'late': qs.filter(attendance_status='Late').count(),
                }
            }
        except UserProfile.DoesNotExist:
            data = {'total_children': 0, 'attendance': {'present': 0, 'absent': 0, 'late': 0}}
        
        return Response(data)

class ChildViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ChildSerializer

    def perform_create(self, serializer):
        profile = getattr(self.request.user, 'userprofile', None)
        active_year = SchoolYear.objects.filter(is_active=True).first()
        
        if profile:
            if not profile.is_teacher:
                child = serializer.save(enrollment_status='Draft', school_year=active_year)
            else:
                child = serializer.save(school_year=active_year)
            child.parents.add(profile)
        else:
            serializer.save(school_year=active_year)

    def get_queryset(self):
        profile = getattr(self.request.user, 'userprofile', None)
        if not profile:
            return Child.objects.none()
        
        qs = Child.objects.all().order_by('-date_added') if profile.is_teacher else Child.objects.filter(parents=profile).order_by('-date_added')
        
        school_year_id = self.request.query_params.get('school_year')
        if school_year_id:
            qs = qs.filter(school_year_id=school_year_id)
        else:
            active_year = SchoolYear.objects.filter(is_active=True).first()
            if active_year:
                qs = qs.filter(school_year=active_year)
            
        return qs

class AttendanceRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AttendanceRecordSerializer

    def perform_create(self, serializer):
        active_year = SchoolYear.objects.filter(is_active=True).first()
        serializer.save(school_year=active_year)

    def get_queryset(self):
        profile = getattr(self.request.user, 'userprofile', None)
        if not profile:
            return AttendanceRecord.objects.none()
            
        qs = AttendanceRecord.objects.all() if profile.is_teacher else AttendanceRecord.objects.filter(child__parents=profile)
        
        school_year_id = self.request.query_params.get('school_year')
        if school_year_id:
            qs = qs.filter(school_year_id=school_year_id)
        else:
            active_year = SchoolYear.objects.filter(is_active=True).first()
            if active_year:
                qs = qs.filter(school_year=active_year)
            
        return qs

class MilestoneRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MilestoneRecordSerializer

    def get_queryset(self):
        profile = getattr(self.request.user, 'userprofile', None)
        if not profile:
            return MilestoneRecord.objects.none()
            
        qs = MilestoneRecord.objects.all() if profile.is_teacher else MilestoneRecord.objects.filter(child__parents=profile)
        
        school_year_id = self.request.query_params.get('school_year')
        if school_year_id:
            qs = qs.filter(child__school_year_id=school_year_id)
        else:
            active_year = SchoolYear.objects.filter(is_active=True).first()
            if active_year:
                qs = qs.filter(child__school_year_id=active_year.id)
            
        return qs

class NutritionRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NutritionRecordSerializer

    def perform_create(self, serializer):
        active_year = SchoolYear.objects.filter(is_active=True).first()
        serializer.save(school_year=active_year)

    def get_queryset(self):
        profile = getattr(self.request.user, 'userprofile', None)
        if not profile:
            return NutritionRecord.objects.none()
            
        qs = NutritionRecord.objects.all() if profile.is_teacher else NutritionRecord.objects.filter(child__parents=profile)
        
        school_year_id = self.request.query_params.get('school_year')
        if school_year_id:
            qs = qs.filter(school_year_id=school_year_id)
        else:
            active_year = SchoolYear.objects.filter(is_active=True).first()
            if active_year:
                qs = qs.filter(school_year=active_year)
            
        return qs

class EngagementRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = EngagementRecordSerializer

    def perform_create(self, serializer):
        active_year = SchoolYear.objects.filter(is_active=True).first()
        serializer.save(school_year=active_year)

    def get_queryset(self):
        profile = getattr(self.request.user, 'userprofile', None)
        if not profile:
            return EngagementRecord.objects.none()
            
        qs = EngagementRecord.objects.all() if profile.is_teacher else EngagementRecord.objects.filter(child__parents=profile)
        
        school_year_id = self.request.query_params.get('school_year')
        if school_year_id:
            qs = qs.filter(school_year_id=school_year_id)
        else:
            active_year = SchoolYear.objects.filter(is_active=True).first()
            if active_year:
                qs = qs.filter(school_year=active_year)
            
        return qs

# ==========================================
# ECCD MILESTONE TRACKER VIEWSETS
# ==========================================

class ECCDDomainViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ECCDDomain.objects.all().order_by('order')
    serializer_class = ECCDDomainSerializer

class ECCDMilestoneViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ECCDMilestoneSerializer
    
    def get_queryset(self):
        qs = ECCDMilestone.objects.all().order_by('domain__order', 'order_number')
        domain = self.request.query_params.get('domain')
        if domain:
            qs = qs.filter(domain=domain)
        return qs

class ECCDAssessmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ECCDAssessmentSerializer

    def perform_create(self, serializer):
        profile = getattr(self.request.user, 'userprofile', None)
        active_year = SchoolYear.objects.filter(is_active=True).first()
        serializer.save(school_year=active_year, teacher=profile)

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'userprofile'):
            return ECCDAssessment.objects.none()
            
        profile = user.userprofile
        qs = ECCDAssessment.objects.all() if profile.is_teacher else ECCDAssessment.objects.filter(child__parents=profile)
        
        child_id = self.request.query_params.get('child')
        if child_id:
            qs = qs.filter(child_id=child_id)
            
        sy_id = self.request.query_params.get('school_year')
        if sy_id:
            qs = qs.filter(school_year_id=sy_id)
        else:
            active_year = SchoolYear.objects.filter(is_active=True).first()
            if active_year:
                qs = qs.filter(school_year_id=active_year.id)
            
        return qs

class ECCDMilestoneScoreViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ECCDMilestoneScoreSerializer
    
    def get_queryset(self):
        qs = ECCDMilestoneScore.objects.all()
        assessment = self.request.query_params.get('assessment')
        if assessment:
            qs = qs.filter(assessment=assessment)
        milestone = self.request.query_params.get('milestone')
        if milestone:
            qs = qs.filter(milestone=milestone)
        school_year_id = self.request.query_params.get('school_year')
        if school_year_id:
            qs = qs.filter(assessment__school_year_id=school_year_id)
        else:
            active_year = SchoolYear.objects.filter(is_active=True).first()
            if active_year:
                qs = qs.filter(assessment__school_year_id=active_year.id)
        return qs

from .eccd_scoring import compute_age, get_age_group, get_scaled_score, get_standard_score, get_standard_score_interpretation
from django.shortcuts import get_object_or_404
from datetime import date

class ECCDReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, assessment_id):
        assessment = get_object_or_404(ECCDAssessment, id=assessment_id)
        
        # Security check
        user = request.user
        if hasattr(user, 'userprofile') and not user.userprofile.is_teacher:
            if not assessment.child.parents.filter(id=user.userprofile.id).exists():
                return Response({'detail': 'Not authorized'}, status=403)
                
        # 1. Compute Age
        # Date tested could be the assessment created_at, or just today if it's not finished
        date_tested = getattr(assessment, 'assessment_date', date.today())
        if not date_tested: date_tested = date.today()
        if type(date_tested) != date:
            try:
                date_tested = date_tested.date()
            except:
                pass
            
        dob = assessment.child.dob
        years, months, days = compute_age(date_tested, dob)
        age_group = get_age_group(years, months)
        
        # 2. Compute Raw Scores per Domain
        domains = ECCDDomain.objects.all().order_by('order')
        scores = ECCDMilestoneScore.objects.filter(assessment=assessment, teacher_score=1)
        
        domain_results = []
        sum_scaled = 0
        
        for d in domains:
            milestones = ECCDMilestone.objects.filter(domain=d)
            raw_score = scores.filter(milestone__in=milestones).count()
            
            scaled_score = 0
            if age_group:
                ss = get_scaled_score(age_group, d.name, raw_score)
                if ss: scaled_score = ss
                
            sum_scaled += scaled_score
            
            domain_results.append({
                'domain_id': d.id,
                'domain_name': d.name,
                'raw_score': raw_score,
                'scaled_score': scaled_score
            })
            
        standard_score = get_standard_score(sum_scaled)
        interpretation = get_standard_score_interpretation(standard_score)
        
        teacher_name = "Not Assigned"
        if assessment.teacher and assessment.teacher.user:
            teacher_name = assessment.teacher.user.get_full_name() or assessment.teacher.user.username

        return Response({
            'child_name': f"{assessment.child.first_name} {assessment.child.last_name}",
            'date_of_birth': dob,
            'date_tested': date_tested,
            'age_years': years,
            'age_months': months,
            'age_days': days,
            'age_group': age_group,
            'domains': domain_results,
            'sum_scaled_scores': sum_scaled,
            'standard_score': standard_score,
            'interpretation': interpretation,
            'teacher_name': teacher_name
        })

class ECCDOverallReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, child_id):
        child = get_object_or_404(Child, id=child_id)
        
        # Security check
        user = request.user
        if hasattr(user, 'userprofile') and not user.userprofile.is_teacher:
            if not child.parents.filter(id=user.userprofile.id).exists():
                return Response({'detail': 'Not authorized'}, status=403)
                
        # 1. Compute Age
        date_tested = date.today()
        dob = child.dob
        years, months, days = compute_age(date_tested, dob)
        age_group = get_age_group(years, months)
        
        # 2. Compute Raw Scores per Domain
        domains = ECCDDomain.objects.all().order_by('order')
        
        # Find all assessments for this child
        assessments = ECCDAssessment.objects.filter(child=child)
        
        domain_results = []
        sum_scaled = 0
        
        for d in domains:
            milestones = ECCDMilestone.objects.filter(domain=d)
            # Find all unique milestones achieved by this child in ANY assessment period
            scores = ECCDMilestoneScore.objects.filter(assessment__in=assessments, teacher_score=1, milestone__in=milestones)
            raw_score = scores.values('milestone').distinct().count()
            
            scaled_score = 0
            if age_group:
                ss = get_scaled_score(age_group, d.name, raw_score)
                if ss: scaled_score = ss
                
            sum_scaled += scaled_score
            
            domain_results.append({
                'domain_id': d.id,
                'domain_name': d.name,
                'raw_score': raw_score,
                'scaled_score': scaled_score
            })
            
        standard_score = get_standard_score(sum_scaled)
        interpretation = get_standard_score_interpretation(standard_score)
        
        return Response({
            'child_name': f"{child.first_name} {child.last_name}",
            'date_of_birth': dob,
            'date_tested': date_tested,
            'age_years': years,
            'age_months': months,
            'age_days': days,
            'age_group': age_group,
            'domains': domain_results,
            'sum_scaled_scores': sum_scaled,
            'standard_score': standard_score,
            'interpretation': interpretation,
            'teacher_name': "Overall Aggregated"
        })

class NutritionAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, 'userprofile', None)
        child_id = request.query_params.get('child_id')
        
        from datetime import datetime, timedelta
        today = datetime.today().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        qs = NutritionRecord.objects.all()
        
        if profile and not profile.is_teacher:
            qs = qs.filter(child__parents=profile)
            
        if child_id:
            qs = qs.filter(child_id=child_id)
            
        school_year_id = request.query_params.get('school_year')
        if school_year_id:
            qs = qs.filter(school_year_id=school_year_id)
        else:
            active_year = SchoolYear.objects.filter(is_active=True).first()
            if active_year:
                qs = qs.filter(school_year_id=active_year.id)
            
        weekly_qs = qs.filter(date__gte=week_ago)
        monthly_qs = qs.filter(date__gte=month_ago)
        
        weekly_counts = {
            'Finished': weekly_qs.filter(snack_status='Finished').count(),
            'Some Left': weekly_qs.filter(snack_status='Some Left').count(),
            'Not Eaten': weekly_qs.filter(snack_status='Not Eaten').count(),
        }
        monthly_counts = {
            'Finished': monthly_qs.filter(snack_status='Finished').count(),
            'Some Left': monthly_qs.filter(snack_status='Some Left').count(),
            'Not Eaten': monthly_qs.filter(snack_status='Not Eaten').count(),
        }

        return Response({
            'weekly': weekly_counts,
            'monthly': monthly_counts
        })

class ParentHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return past 30 days of attendance, nutrition, behavior, and milestones for the linked child."""
        try:
            profile = request.user.userprofile
            children = Child.objects.filter(parents=profile)
            
            school_year_id = request.query_params.get('school_year')
            if school_year_id:
                children = children.filter(school_year_id=school_year_id)
            else:
                active_year = SchoolYear.objects.filter(is_active=True).first()
                if active_year:
                    children = children.filter(school_year=active_year)
                    
            if not children.exists():
                return Response({'detail': 'No child linked for this academic year.'}, status=404)
        except UserProfile.DoesNotExist:
            return Response({'detail': 'User profile missing.'}, status=400)

        # Get first child for backwards compatibility
        child = children.first()

        from datetime import datetime, timedelta
        today = datetime.today().date()
        start_date = today - timedelta(days=30)

        # Attendance
        attendance_qs = AttendanceRecord.objects.filter(child=child, date__range=[start_date, today])
        attendance_data = AttendanceRecordSerializer(attendance_qs, many=True).data
        # Nutrition
        nutrition_qs = NutritionRecord.objects.filter(child=child, date__range=[start_date, today])
        nutrition_data = NutritionRecordSerializer(nutrition_qs, many=True).data
        # Engagement
        engagement_qs = EngagementRecord.objects.filter(child=child, date__range=[start_date, today])
        engagement_data = EngagementRecordSerializer(engagement_qs, many=True).data
        # Milestones (latest only, but include all milestones records if multiple)
        milestone_qs = MilestoneRecord.objects.filter(child=child)
        milestone_data = MilestoneRecordSerializer(milestone_qs, many=True).data

        child_data = ChildSerializer(child).data
        children_data = ChildSerializer(children, many=True).data

        # Determine parent name robustly
        parent_name = ""
        if profile.user.first_name or profile.user.last_name:
            parent_name = f"{profile.user.first_name} {profile.user.last_name}".strip()
        if not parent_name:
            for c in children:
                if c.mother_email == profile.user.email and c.mother_first_name:
                    parent_name = f"{c.mother_first_name} {c.mother_last_name}".strip()
                    break
                elif c.father_email == profile.user.email and c.father_first_name:
                    parent_name = f"{c.father_first_name} {c.father_last_name}".strip()
                    break
                elif c.other_guardian_email == profile.user.email and c.other_guardian_first_name:
                    parent_name = f"{c.other_guardian_first_name} {c.other_guardian_last_name}".strip()
                    break
        if not parent_name:
            parent_name = profile.user.username

        return Response({
            'child': child_data,
            'children': children_data,
            'parent_profile_id': profile.id,
            'parent_name': parent_name,
            'attendance': attendance_data,
            'nutrition': nutrition_data,
            'engagement': engagement_data,
            'milestones': milestone_data,
        })

class ParentListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        parents_data = []
        try:
            # Fetch all user profiles that are not teachers
            profiles = UserProfile.objects.filter(is_teacher=False).select_related('user')
            for profile in profiles:
                # Find children linked to this parent profile
                children = Child.objects.filter(parents=profile)
                if not children.exists():
                    continue  # Only show parents with enrolled children
                
                # Determine parent name robustly
                parent_name = ""
                if profile.user.first_name or profile.user.last_name:
                    parent_name = f"{profile.user.first_name} {profile.user.last_name}".strip()
                if not parent_name:
                    for c in children:
                        if c.mother_email == profile.user.email and c.mother_first_name:
                            parent_name = f"{c.mother_first_name} {c.mother_last_name}".strip()
                            break
                        elif c.father_email == profile.user.email and c.father_first_name:
                            parent_name = f"{c.father_first_name} {c.father_last_name}".strip()
                            break
                        elif c.other_guardian_email == profile.user.email and c.other_guardian_first_name:
                            parent_name = f"{c.other_guardian_first_name} {c.other_guardian_last_name}".strip()
                            break
                if not parent_name:
                    parent_name = profile.user.username
                
                children_names = [f"{c.first_name} {c.last_name}" for c in children]
                
                parents_data.append({
                    'id': profile.id,
                    'name': parent_name,
                    'children': children_names,
                    'email': profile.user.email
                })
        except Exception as e:
            return Response({'detail': str(e)}, status=500)
            
        return Response(parents_data)

class SchoolYearViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SchoolYearSerializer
    queryset = SchoolYear.objects.all().order_by('-start_date')

class NoClassDayViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NoClassDaySerializer
    
    def get_queryset(self):
        qs = NoClassDay.objects.all().order_by('-date')
        school_year_id = self.request.query_params.get('school_year')
        if school_year_id:
            qs = qs.filter(school_year_id=school_year_id)
        return qs

    def perform_create(self, serializer):
        active_year = SchoolYear.objects.filter(is_active=True).first()
        serializer.save(school_year=active_year)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def link_guardian_profile(request):
    try:
        profile = request.user.userprofile
        if profile.is_teacher:
            return Response({'detail': 'Teachers cannot link as guardians.'}, status=403)
            
        data = request.data
        child_id = data.get('child_id')
        guardian_type = data.get('guardian_type') # 'Mother', 'Father', 'Other Relative'
        
        if not child_id or not guardian_type:
            return Response({'detail': 'Child ID and Guardian Type are required.'}, status=400)
            
        child = Child.objects.get(id=child_id)
        
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        middle_initial = data.get('middle_initial', '')
        email = data.get('email', '')
        phone = data.get('phone', '')
        
        # Combine address parts
        address_line1 = data.get('address_line1', '')
        barangay = data.get('barangay', '')
        city_municipality = data.get('city_municipality', '')
        province = data.get('province', '')
        region = data.get('region', '')
        
        address_parts = [p for p in [address_line1, barangay, city_municipality, province, region] if p]
        full_address = ", ".join(address_parts)
        
        if guardian_type == 'Mother':
            child.mother_first_name = first_name
            child.mother_middle_initial = middle_initial
            child.mother_last_name = last_name
            child.mother_email = email
            child.mother_phone = phone
            child.mother_address = full_address
        elif guardian_type == 'Father':
            child.father_first_name = first_name
            child.father_middle_initial = middle_initial
            child.father_last_name = last_name
            child.father_email = email
            child.father_phone = phone
            child.father_address = full_address
        elif guardian_type == 'Other Relative':
            child.other_guardian_first_name = first_name
            child.other_guardian_middle_initial = middle_initial
            child.other_guardian_last_name = last_name
            child.other_guardian_email = email
            child.other_guardian_phone = phone
            child.other_guardian_address = full_address
        else:
            return Response({'detail': 'Invalid guardian type.'}, status=400)
            
        child.enrollment_status = 'Pending'
        child.save()
        
        # Link the user profile to the child
        child.parents.add(profile)
        
        # Handle profile picture upload
        profile_pic = request.FILES.get('profile_pic')
        if profile_pic:
            profile.profile_pic = profile_pic
            profile.save()
        
        return Response({'detail': 'Guardian profile linked successfully.', 'child_id': child.id}, status=200)
        
    except Child.DoesNotExist:
        return Response({'detail': 'Child not found.'}, status=404)
    except Exception as e:
        return Response({'detail': str(e)}, status=500)

class ForcePasswordChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        profile = user.userprofile
        
        if not profile.first_login:
            return Response({'error': 'Not your first login.'}, status=400)
            
        new_password = request.data.get('new_password')
        if not new_password or len(new_password) < 8:
            return Response({'error': 'Password must be at least 8 characters long.'}, status=400)
            
        user.set_password(new_password)
        user.save()
        
        profile.first_login = False
        profile.save()
        
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)
        
        return Response({'success': True, 'message': 'Password updated successfully.'})

class UpdateUsernameAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        new_username = request.data.get('new_username')
        if not new_username:
            return Response({'error': 'New username is required'}, status=400)
        
        if User.objects.filter(username=new_username).exclude(id=request.user.id).exists():
            return Response({'error': 'Username is already taken'}, status=400)
            
        user = request.user
        user.username = new_username
        user.save()
        return Response({'success': True, 'message': 'Username updated successfully'})

class RequestPasswordChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.email:
            return Response({'error': 'No email associated with this account. Please update your email first.'}, status=400)
            
        import random
        otp_code = str(random.randint(100000, 999999))
        
        # Clear old OTPs
        PasswordResetOTP.objects.filter(user=user).delete()
        
        # Save new OTP
        PasswordResetOTP.objects.create(user=user, otp_code=otp_code)
        
        # Send Email
        email_sent = False
        try:
            send_mail(
                'Password Verification Code - BMV3 Child Care',
                f'Your password verification code is: {otp_code}\n\nThis code will expire in 5 minutes.',
                'jeremybryanvillanueva@gmail.com',
                [user.email],
                fail_silently=False,
            )
            email_sent = True
        except Exception as e:
            print(f"FAILED TO SEND EMAIL. OTP IS: {otp_code}. Error: {e}")
            
        from django.conf import settings
        if settings.DEBUG or not email_sent:
            return Response({
                'success': True, 
                'dev_otp': otp_code, 
                'message': 'Verification code generated locally (DEBUG mode/SMTP fallback).'
            })
            
        return Response({'success': True, 'message': 'Verification code sent to your email.'})

class VerifyPasswordChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        otp_code = request.data.get('otp_code')
        new_password = request.data.get('new_password')
        
        if not otp_code or not new_password:
            return Response({'error': 'Missing OTP or new password'}, status=400)
            
        otp_record = PasswordResetOTP.objects.filter(user=user).last()
        if not otp_record:
            return Response({'error': 'No verification code requested.'}, status=400)
            
        if not otp_record.is_valid():
            otp_record.delete()
            return Response({'error': 'Verification code expired (valid for 5 minutes).'}, status=400)
            
        if otp_record.otp_code != otp_code:
            return Response({'error': 'Invalid verification code.'}, status=400)
            
        if len(new_password) < 8:
            return Response({'error': 'Password must be at least 8 characters long.'}, status=400)
            
        user.set_password(new_password)
        user.save()
        otp_record.delete()
        
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)
        
        return Response({'success': True, 'message': 'Password changed successfully.'})

class VerifyOTPOnlyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        otp_code = request.data.get('otp_code')
        
        if not otp_code:
            return Response({'error': 'Missing OTP'}, status=400)
            
        otp_record = PasswordResetOTP.objects.filter(user=user).last()
        if not otp_record:
            return Response({'error': 'No verification code requested.'}, status=400)
            
        if not otp_record.is_valid():
            otp_record.delete()
            return Response({'error': 'Verification code expired (valid for 5 minutes).'}, status=400)
            
        if otp_record.otp_code != otp_code:
            return Response({'error': 'Invalid verification code.'}, status=400)
            
        return Response({'success': True, 'message': 'OTP verified successfully.'})

class UserSettingsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            profile = user.userprofile
            child = Child.objects.filter(parents=profile).first()
        except UserProfile.DoesNotExist:
            child = None
            
        data = {
            'username': user.username,
            'name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        try:
            if user.userprofile.profile_pic:
                data['profile_pic'] = user.userprofile.profile_pic.url
        except:
            pass
        
        if child:
            data['child_id'] = child.id
            data['child_first_name'] = child.first_name
            data['child_last_name'] = child.last_name
            data['child_allergies'] = child.allergies
            data['child_health_conditions'] = child.health_conditions
            
            if child.mother_email and child.mother_email.lower() == user.email.lower():
                data['phone'] = child.mother_phone
                data['address'] = child.mother_address
                data['guardian_type'] = 'Mother'
            elif child.father_email and child.father_email.lower() == user.email.lower():
                data['phone'] = child.father_phone
                data['address'] = child.father_address
                data['guardian_type'] = 'Father'
            elif child.other_guardian_email and child.other_guardian_email.lower() == user.email.lower():
                data['phone'] = child.other_guardian_phone
                data['address'] = child.other_guardian_address
                data['guardian_type'] = 'Other Relative'
            else:
                # Fallback if email mismatch
                if child.mother_first_name and child.mother_first_name != 'No Info':
                    data['phone'] = child.mother_phone
                    data['address'] = child.mother_address
                    data['guardian_type'] = 'Mother'
                elif child.father_first_name and child.father_first_name != 'No Info':
                    data['phone'] = child.father_phone
                    data['address'] = child.father_address
                    data['guardian_type'] = 'Father'
                else:
                    data['phone'] = child.other_guardian_phone
                    data['address'] = child.other_guardian_address
                    data['guardian_type'] = 'Other Relative'
                
                
        return Response(data)

    def post(self, request):
        user = request.user
        data = request.data
        
        new_username = data.get('username')
        if new_username and new_username != user.username:
            if User.objects.filter(username=new_username).exists():
                return Response({'detail': 'Username is already taken.'}, status=400)
            user.username = new_username
            
        if 'first_name' in data: user.first_name = data['first_name']
        if 'last_name' in data: user.last_name = data['last_name']
        if 'email' in data: user.email = data['email']
            
        user.save()
        
        try:
            profile = user.userprofile
            children = Child.objects.filter(parents=profile)
            guardian_type = data.get('guardian_type')
            
            for child in children:
                if guardian_type == 'Mother':
                    if 'first_name' in data: child.mother_first_name = data['first_name']
                    if 'last_name' in data: child.mother_last_name = data['last_name']
                    if 'email' in data: child.mother_email = data['email']
                    if 'phone' in data: child.mother_phone = data['phone']
                    if 'address' in data: child.mother_address = data['address']
                elif guardian_type == 'Father':
                    if 'first_name' in data: child.father_first_name = data['first_name']
                    if 'last_name' in data: child.father_last_name = data['last_name']
                    if 'email' in data: child.father_email = data['email']
                    if 'phone' in data: child.father_phone = data['phone']
                    if 'address' in data: child.father_address = data['address']
                elif guardian_type == 'Other Relative':
                    if 'first_name' in data: child.other_guardian_first_name = data['first_name']
                    if 'last_name' in data: child.other_guardian_last_name = data['last_name']
                    if 'email' in data: child.other_guardian_email = data['email']
                    if 'phone' in data: child.other_guardian_phone = data['phone']
                    if 'address' in data: child.other_guardian_address = data['address']
                child.save()
        except UserProfile.DoesNotExist:
            pass
            
        return Response({'detail': 'Profile updated successfully.'})

class UpdateChildProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request, child_id):
        try:
            profile = request.user.userprofile
            child = Child.objects.get(id=child_id, parents=profile)
            
            data = request.data
            if 'first_name' in data: child.first_name = data['first_name']
            if 'last_name' in data: child.last_name = data['last_name']
            if 'allergies' in data: child.allergies = data['allergies']
            if 'health_conditions' in data: child.health_conditions = data['health_conditions']
            
            child.save()
            return Response({'detail': 'Child profile updated.'})
            
        except Child.DoesNotExist:
            return Response({'detail': 'Child not found or not linked.'}, status=404)

from django.core.mail import send_mail
from .models import PasswordResetOTP
import random

class RequestPasswordOTPAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        otp_code = str(random.randint(100000, 999999))
        
        PasswordResetOTP.objects.filter(user=user).delete()
        PasswordResetOTP.objects.create(user=user, otp_code=otp_code)
        
        try:
            send_mail(
                "BMV3 Childcare - Password Reset Code",
                f"Hello {user.username},\n\nYour password reset code is: {otp_code}\n\nThis code will expire in 10 minutes.",
                "noreply@bmv3.com",
                [user.email],
                fail_silently=True
            )
            return Response({'detail': 'Verification code sent to your email.'})
        except Exception as e:
            print(f"OTP for {user.username}: {otp_code}")
            return Response({'detail': 'Verification code sent.'})

class VerifyPasswordOTPAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        otp_code = request.data.get('otp_code')
        new_password = request.data.get('new_password')
        
        if not otp_code or not new_password:
            return Response({'detail': 'OTP and new password are required.'}, status=400)
            
        otp_record = PasswordResetOTP.objects.filter(user=user, otp_code=otp_code).last()
        
        if not otp_record:
            return Response({'detail': 'Invalid verification code.'}, status=400)
            
        if not otp_record.is_valid():
            return Response({'detail': 'Verification code has expired.'}, status=400)
            
        user.set_password(new_password)
        user.save()
        
        otp_record.delete()
        
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)
        
        return Response({'detail': 'Password changed successfully.'})

import string

class GenerateParentAccountAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        child_id = request.data.get('child_id')
        parent_name = request.data.get('parent_name', '').strip()
        email = request.data.get('email', '').strip()
        
        if not parent_name or not email:
            return Response({'error': 'Parent Name and Email are required.'}, status=400)
            
        # Generate random username and password
        username_base = parent_name.split()[0].lower() + str(random.randint(100, 999))
        username = username_base
        while User.objects.filter(username=username).exists():
            username = username_base + str(random.randint(10, 99))
            
        password_chars = string.ascii_letters + string.digits
        password = ''.join(random.choice(password_chars) for _ in range(8))
        
        try:
            # Create user
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = parent_name.split()[0]
            if len(parent_name.split()) > 1:
                user.last_name = " ".join(parent_name.split()[1:])
            user.save()
            
            # Create profile (first_login is True by default now)
            profile = UserProfile.objects.create(user=user, is_teacher=False, first_login=True)
            
            # Link to child if provided
            if child_id:
                try:
                    child = Child.objects.get(id=child_id)
                    child.parents.add(profile)
                except Child.DoesNotExist:
                    pass
            
            # Send email
            from django.core.mail import EmailMultiAlternatives
            from django.utils.html import strip_tags
            
            subject = "Welcome to BMV3 Child Care - Your Account Details"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #4a90e2; text-align: center;">Welcome to BMV3 Child Care!</h2>
                <p>Hello <strong>{parent_name}</strong>,</p>
                <p>A parent account has been created for you. You can use this account to track your child's attendance, milestones, nutrition, and more.</p>
                
                <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #333;">Your Temporary Credentials:</h3>
                    <p style="margin: 5px 0;"><strong>Username:</strong> <span style="color: #d9534f; font-size: 1.1rem;">{username}</span></p>
                    <p style="margin: 5px 0;"><strong>Password:</strong> <span style="color: #d9534f; font-size: 1.1rem;">{password}</span></p>
                </div>
                
                <p style="color: #e74a3b; font-weight: bold;">⚠️ IMPORTANT: For your security, you will be required to change this temporary password immediately upon your first login.</p>
                
                <p style="margin-top: 30px;">Best Regards,<br>The BMV3 Administration Team</p>
            </div>
            """
            text_content = strip_tags(html_content)
            
            from django.conf import settings
            email_sent = False
            is_console_backend = (getattr(settings, 'EMAIL_BACKEND', '') == 'django.core.mail.backends.console.EmailBackend')
            
            try:
                msg = EmailMultiAlternatives(subject, text_content, "jeremybryanvillanueva@gmail.com", [email])
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=False)
                # If we are using the console backend, no real email is sent to the parent,
                # so we treat email_sent as False so that credentials show on-screen.
                if not is_console_backend:
                    email_sent = True
            except Exception as e:
                print(f"Failed to send email to {email}: {e}")
                email_sent = False
                
            res_data = {
                'success': True,
                'message': 'Account generated successfully.'
            }
            if settings.DEBUG or not email_sent or is_console_backend:
                res_data['dev_credentials'] = {
                    'username': username,
                    'password': password
                }
            return Response(res_data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)

from .models import ScoringAccessRequest
from .serializers import ScoringAccessRequestSerializer
from rest_framework import serializers as drf_serializers
from django.utils import timezone

class ScoringAccessRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ScoringAccessRequestSerializer

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'userprofile'):
            return ScoringAccessRequest.objects.none()
        profile = user.userprofile
        qs = ScoringAccessRequest.objects.all()
        
        child_id = self.request.query_params.get('child')
        if child_id:
            qs = qs.filter(child_id=child_id)
            
        if profile.is_teacher:
            return qs.order_by('-requested_at')
        else:
            return qs.filter(parent=profile).order_by('-requested_at')

    def perform_create(self, serializer):
        profile = getattr(self.request.user, 'userprofile', None)
        child_id = self.request.data.get('child')
        if child_id:
            existing = ScoringAccessRequest.objects.filter(child_id=child_id, parent=profile, status='Pending').first()
            if existing:
                raise drf_serializers.ValidationError("A request is already pending for this child.")
        serializer.save(parent=profile)

    def perform_update(self, serializer):
        status = self.request.data.get('status')
        if status == 'Approved':
            serializer.save(approved_at=timezone.now())
        else:
            serializer.save()
