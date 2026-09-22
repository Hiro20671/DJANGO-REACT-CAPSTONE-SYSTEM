from rest_framework import viewsets, parsers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated

from .models import Child, UserProfile, AttendanceRecord, MilestoneRecord, NutritionRecord, SchoolYear, EngagementRecord, PasswordResetOTP, NoClassDay, ECCDDomain, ECCDMilestone, ECCDAssessment, ECCDMilestoneScore, BMIRecord, CenterSettings, PublicReminder, TextblastLog
from .serializers import ChildSerializer, AttendanceRecordSerializer, MilestoneRecordSerializer, NutritionRecordSerializer, SchoolYearSerializer, EngagementRecordSerializer, NoClassDaySerializer, ECCDDomainSerializer, ECCDMilestoneSerializer, ECCDAssessmentSerializer, ECCDMilestoneScoreSerializer, BMIRecordSerializer, CenterSettingsSerializer, PublicReminderSerializer, TextblastLogSerializer


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
            settings.DEFAULT_FROM_EMAIL,
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
                child = serializer.save(enrollment_status='Pending', school_year=active_year)
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
                from django.db.models import Q
                if profile.is_teacher:
                    qs = qs.filter(Q(school_year=active_year) | Q(enrollment_status='Pending'))
                else:
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
        elif profile.is_teacher:
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
        elif profile.is_teacher:
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
        elif profile.is_teacher:
            active_year = SchoolYear.objects.filter(is_active=True).first()
            if active_year:
                qs = qs.filter(school_year=active_year)
            
        return qs

class BMIRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BMIRecordSerializer

    def perform_create(self, serializer):
        child = serializer.validated_data.get('child')
        quarter = serializer.validated_data.get('quarter')
        active_year = SchoolYear.objects.filter(is_active=True).first()
        
        # Check locking logic
        from rest_framework.exceptions import ValidationError
        if quarter == '2nd':
            first_q = BMIRecord.objects.filter(child=child, school_year=active_year, quarter='1st').first()
            if not first_q or first_q.status != 'Finalized':
                raise ValidationError("Cannot create 2nd Quarter record because 1st Quarter is not finalized.")
        elif quarter == '3rd':
            second_q = BMIRecord.objects.filter(child=child, school_year=active_year, quarter='2nd').first()
            if not second_q or second_q.status != 'Finalized':
                raise ValidationError("Cannot create 3rd Quarter record because 2nd Quarter is not finalized.")
                
        serializer.save(school_year=active_year)

    def perform_update(self, serializer):
        instance = serializer.instance
        quarter = serializer.validated_data.get('quarter', instance.quarter)
        child = instance.child
        active_year = instance.school_year
        
        # Check locking logic
        from rest_framework.exceptions import ValidationError
        # Only enforce locking if they are moving forward or changing values
        if quarter == '2nd':
            first_q = BMIRecord.objects.filter(child=child, school_year=active_year, quarter='1st').first()
            if not first_q or first_q.status != 'Finalized':
                raise ValidationError("Cannot update 2nd Quarter record because 1st Quarter is not finalized.")
        elif quarter == '3rd':
            second_q = BMIRecord.objects.filter(child=child, school_year=active_year, quarter='2nd').first()
            if not second_q or second_q.status != 'Finalized':
                raise ValidationError("Cannot update 3rd Quarter record because 2nd Quarter is not finalized.")
                
        serializer.save()

    def get_queryset(self):
        profile = getattr(self.request.user, 'userprofile', None)
        if not profile:
            return BMIRecord.objects.none()
            
        qs = BMIRecord.objects.all() if profile.is_teacher else BMIRecord.objects.filter(child__parents=profile)
        
        child_id = self.request.query_params.get('child')
        if child_id:
            qs = qs.filter(child_id=child_id)
            
        school_year_id = self.request.query_params.get('school_year')
        if school_year_id:
            qs = qs.filter(school_year_id=school_year_id)
        elif profile.is_teacher:
            active_year = SchoolYear.objects.filter(is_active=True).first()
            if active_year:
                qs = qs.filter(school_year=active_year)
            
        return qs

    @action(detail=False, methods=['post'])
    def bulk_finalize(self, request):
        user = request.user
        if not hasattr(user, 'userprofile') or not user.userprofile.is_teacher:
            return Response({'error': 'Only teachers can perform bulk finalization.'}, status=403)
            
        quarter = request.data.get('quarter')
        if not quarter:
            return Response({'error': 'Quarter is required.'}, status=400)
            
        active_year = SchoolYear.objects.filter(is_active=True).first()
        if not active_year:
            return Response({'error': 'No active school year found.'}, status=400)
            
        # Get all enrolled children
        children = Child.objects.filter(school_year=active_year, enrollment_status='Enrolled')
        
        from datetime import date
        count = 0
        for child in children:
            # Check if previous quarter is finalized if needed
            prev_record = None
            if quarter == '2nd':
                prev_record = BMIRecord.objects.filter(child=child, school_year=active_year, quarter='1st').first()
            elif quarter == '3rd':
                prev_record = BMIRecord.objects.filter(child=child, school_year=active_year, quarter='2nd').first()
                if not prev_record:
                    prev_record = BMIRecord.objects.filter(child=child, school_year=active_year, quarter='1st').first()
                    
            default_weight = prev_record.weight if prev_record else 15.0
            default_height = prev_record.height if prev_record else 100.0
            default_date = getattr(active_year, f'eccd_{quarter}_start') or date.today()
            
            record, created = BMIRecord.objects.get_or_create(
                child=child,
                school_year=active_year,
                quarter=quarter,
                defaults={
                    'weight': default_weight,
                    'height': default_height,
                    'measurement_date': default_date,
                    'status': 'Finalized'
                }
            )
            if not created and record.status != 'Finalized':
                record.status = 'Finalized'
                record.save()
            count += 1
            
        return Response({'message': f'Successfully finalized {quarter} Quarter nutrition records for all {count} enrolled students.'})
        
    @action(detail=False, methods=['post'])
    def bulk_unlock(self, request):
        user = request.user
        if not hasattr(user, 'userprofile') or not user.userprofile.is_teacher:
            return Response({'error': 'Only teachers can perform bulk unlock.'}, status=403)
            
        quarter = request.data.get('quarter')
        if not quarter:
            return Response({'error': 'Quarter is required.'}, status=400)
            
        active_year = SchoolYear.objects.filter(is_active=True).first()
        if not active_year:
            return Response({'error': 'No active school year found.'}, status=400)
            
        records = BMIRecord.objects.filter(school_year=active_year, quarter=quarter)
        count = records.update(status='Draft')
        return Response({'message': f'Successfully unlocked {quarter} Quarter nutrition records for all {count} students.'})

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
        elif profile.is_teacher:
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

    @action(detail=False, methods=['post'])
    def bulk_finalize(self, request):
        user = request.user
        if not hasattr(user, 'userprofile') or not user.userprofile.is_teacher:
            return Response({'error': 'Only teachers can perform bulk finalization.'}, status=403)
            
        period = request.data.get('period')
        if not period:
            return Response({'error': 'Period is required.'}, status=400)
            
        active_year = SchoolYear.objects.filter(is_active=True).first()
        if not active_year:
            return Response({'error': 'No active school year found.'}, status=400)
            
        # Get all enrolled children in active school year
        children = Child.objects.filter(school_year=active_year, enrollment_status='Enrolled')
        
        # Ensure an assessment exists for each child for this period, and set its status to Finalized
        from datetime import date
        count = 0
        for child in children:
            initial_date = getattr(active_year, f'eccd_{period}_start') or date.today()
            assessment, created = ECCDAssessment.objects.get_or_create(
                child=child,
                school_year=active_year,
                assessment_period=period,
                defaults={
                    'status': 'Finalized',
                    'assessment_date': initial_date,
                    'teacher': user.userprofile
                }
            )
            if not created and assessment.status != 'Finalized':
                assessment.status = 'Finalized'
                assessment.save()
            count += 1
            
        return Response({'message': f'Successfully finalized {period} Assessment for all {count} enrolled students.'})

    @action(detail=False, methods=['post'])
    def bulk_unlock(self, request):
        user = request.user
        if not hasattr(user, 'userprofile') or not user.userprofile.is_teacher:
            return Response({'error': 'Only teachers can perform bulk unlock.'}, status=403)
            
        period = request.data.get('period')
        if not period:
            return Response({'error': 'Period is required.'}, status=400)
            
        active_year = SchoolYear.objects.filter(is_active=True).first()
        if not active_year:
            return Response({'error': 'No active school year found.'}, status=400)
            
        # Update all assessments for this period to Draft
        assessments = ECCDAssessment.objects.filter(
            school_year=active_year,
            assessment_period=period
        )
        count = assessments.update(status='Draft')
        return Response({'message': f'Successfully unlocked {period} Assessment for all {count} students.'})

class ECCDMilestoneScoreViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ECCDMilestoneScoreSerializer
    
    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'userprofile'):
            return ECCDMilestoneScore.objects.none()
            
        profile = user.userprofile
        if profile.is_teacher:
            qs = ECCDMilestoneScore.objects.all()
        else:
            # Parents only see scores for their children
            qs = ECCDMilestoneScore.objects.filter(assessment__child__parents=profile)
            
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
            # Default to active year only for teachers
            if profile.is_teacher:
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
        # BMI Records
        bmi_qs = BMIRecord.objects.filter(child=child)
        if school_year_id:
            bmi_qs = bmi_qs.filter(school_year_id=school_year_id)
        else:
            if active_year:
                bmi_qs = bmi_qs.filter(school_year=active_year)
        bmi_data = BMIRecordSerializer(bmi_qs, many=True).data

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
            'bmi_records': bmi_data,
        })

class ParentListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        parents_data = []
        try:
            # Fetch all user profiles that are not teachers
            profiles = UserProfile.objects.filter(is_teacher=False).select_related('user')
            school_year_id = request.query_params.get('school_year')
            active_year = None if school_year_id else SchoolYear.objects.filter(is_active=True).first()
            
            for profile in profiles:
                # Find children linked to this parent profile in the active/selected school year
                if school_year_id:
                    children = Child.objects.filter(parents=profile, school_year_id=school_year_id)
                elif active_year:
                    children = Child.objects.filter(parents=profile, school_year=active_year)
                else:
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

    def get_queryset(self):
        # Only return non-deleted school years by default
        return SchoolYear.objects.filter(is_deleted=False).order_by('-start_date')

    def destroy(self, request, *args, **kwargs):
        # Allow hard deleting from the recycle bin
        instance = get_object_or_404(SchoolYear, pk=kwargs.get('pk'))
        self.perform_destroy(instance)
        return Response(status=204)

    @action(detail=True, methods=['post'])
    def soft_delete(self, request, pk=None):
        school_year = get_object_or_404(SchoolYear, pk=pk)
        if school_year.is_active:
            return Response({'error': 'Cannot delete the active school year.'}, status=400)
        from django.utils import timezone
        school_year.is_deleted = True
        school_year.deleted_at = timezone.now()
        school_year.save()
        return Response({'message': f'School year {school_year.name} moved to recycle bin.'})

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        school_year = get_object_or_404(SchoolYear, pk=pk)
        school_year.is_deleted = False
        school_year.deleted_at = None
        school_year.save()
        return Response({'message': f'School year {school_year.name} restored successfully.'})

    @action(detail=False, methods=['get'])
    def recycle_bin(self, request):
        from django.utils import timezone
        from datetime import timedelta
        # Auto cleanup: permanently delete entries older than 30 days
        limit = timezone.now() - timedelta(days=30)
        SchoolYear.objects.filter(is_deleted=True, deleted_at__lt=limit).delete()
        
        deleted_years = SchoolYear.objects.filter(is_deleted=True).order_by('-deleted_at')
        serializer = self.get_serializer(deleted_years, many=True)
        return Response(serializer.data)

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
                settings.DEFAULT_FROM_EMAIL,
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
        if hasattr(user, 'userprofile'):
            profile = user.userprofile
            data['home_latitude'] = float(profile.home_latitude) if profile.home_latitude is not None else 13.9395
            data['home_longitude'] = float(profile.home_longitude) if profile.home_longitude is not None else 121.6160
            data['home_address_text'] = profile.home_address_text or ''

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
            if 'home_latitude' in data and data['home_latitude'] is not None:
                profile.home_latitude = data['home_latitude']
            if 'home_longitude' in data and data['home_longitude'] is not None:
                profile.home_longitude = data['home_longitude']
            if 'home_address_text' in data:
                profile.home_address_text = data['home_address_text']
            profile.save()

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
                    if 'email' in data: child.email = data['email']
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
                settings.DEFAULT_FROM_EMAIL,
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
                
                <p style="color: #e74a3b; font-weight: bold;">IMPORTANT: For your security, you will be required to change this temporary password immediately upon your first login.</p>
                
                <p style="margin-top: 30px;">Best Regards,<br>The BMV3 Administration Team</p>
            </div>
            """
            text_content = strip_tags(html_content)
            
            from django.conf import settings
            email_sent = False
            is_console_backend = (getattr(settings, 'EMAIL_BACKEND', '') == 'django.core.mail.backends.console.EmailBackend')
            
            try:
                msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [email])
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

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Activity, StudentActivityCompletion
from .serializers import ActivitySerializer, StudentActivityCompletionSerializer

class ActivityViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ActivitySerializer
    queryset = Activity.objects.all()

    def get_queryset(self):
        qs = Activity.objects.all()
        date = self.request.query_params.get('date')
        if date:
            qs = qs.filter(date=date)
        return qs.order_by('id')

class StudentActivityCompletionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentActivityCompletionSerializer
    queryset = StudentActivityCompletion.objects.all()

    def get_queryset(self):
        qs = StudentActivityCompletion.objects.all()
        child_id = self.request.query_params.get('child')
        activity_id = self.request.query_params.get('activity')
        date = self.request.query_params.get('date')
        if child_id:
            qs = qs.filter(child_id=child_id)
        if activity_id:
            qs = qs.filter(activity_id=activity_id)
        if date:
            qs = qs.filter(activity__date=date)
        return qs.order_by('child__last_name', 'child__first_name')

    @action(detail=False, methods=['post'], url_path='bulk-save')
    def bulk_save(self, request):
        completions = request.data.get('completions', [])
        results = []
        for item in completions:
            cid = item.get('child_id')
            aid = item.get('activity_id')
            comp = item.get('completed', False)
            rem = item.get('remarks', '')
            
            if not cid or not aid:
                continue
                
            completion, created = StudentActivityCompletion.objects.update_or_create(
                child_id=cid,
                activity_id=aid,
                defaults={'completed': comp, 'remarks': rem}
            )
            results.append(StudentActivityCompletionSerializer(completion).data)
            
        return Response({'success': True, 'results': results})

# ==========================================
# PUBLIC LANDING PAGE & ANNOUNCEMENTS API
# ==========================================

from rest_framework.permissions import AllowAny
from datetime import date
from django.db.models import Q
from .models import Announcement, EnrollmentInfo, ProgramHighlight, PublicReminder
from .serializers import (AnnouncementSerializer, EnrollmentInfoSerializer, 
                          ProgramHighlightSerializer, PublicReminderSerializer)

class PublicLandingDataAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        today = date.today()

        # 1. School Year Status Calculation
        active_sy = SchoolYear.objects.filter(is_active=True).first()
        sy_data = {
            'has_active_year': False,
            'name': '2026-2027',
            'status': 'ongoing',
            'title': 'Child Development Program is Currently Ongoing',
            'start_date': None,
            'end_date': None,
            'days_until': None,
            'message': 'Welcome to the Barangay Market View 3 Child Development Center.'
        }
        if active_sy:
            sy_data['has_active_year'] = True
            sy_data['name'] = active_sy.name
            sy_data['start_date'] = str(active_sy.start_date) if active_sy.start_date else None
            sy_data['end_date'] = str(active_sy.end_date) if active_sy.end_date else None

            if active_sy.start_date and today < active_sy.start_date:
                days = (active_sy.start_date - today).days
                sy_data['status'] = 'upcoming'
                sy_data['days_until'] = days
                sy_data['title'] = f"Upcoming Child Development Program ({active_sy.name})"
                if days == 1:
                    sy_data['message'] = f"The Child Development Program begins tomorrow on {active_sy.start_date.strftime('%B %d, %Y')}! Please prepare the required documents."
                else:
                    sy_data['message'] = f"The Child Development Program for School Year {active_sy.name} will begin on {active_sy.start_date.strftime('%B %d, %Y')} ({days} days remaining)."
            elif active_sy.start_date and today == active_sy.start_date:
                sy_data['status'] = 'starting_today'
                sy_data['title'] = f"Child Development Program Starts Today!"
                sy_data['message'] = f"Welcome to the {active_sy.name} Child Development Program! Program sessions begin today, {active_sy.start_date.strftime('%B %d, %Y')}."
            elif active_sy.end_date and today > active_sy.end_date:
                sy_data['status'] = 'ended'
                sy_data['title'] = f"School Year {active_sy.name} Has Concluded"
                sy_data['message'] = f"The BMV3 Child Development Program for School Year {active_sy.name} officially ended on {active_sy.end_date.strftime('%B %d, %Y')}. Thank you to our children and families!"
            else:
                sy_data['status'] = 'ongoing'
                sy_data['title'] = f"Child Development Program is Currently Ongoing"
                sy_data['message'] = f"School Year {active_sy.name} is currently ongoing."

        # 2. No-Class Day Integration
        no_class_notice = None
        no_class_today = NoClassDay.objects.filter(date=today).first()
        if no_class_today:
            no_class_notice = {
                'status': 'today',
                'date': str(today),
                'formatted_date': today.strftime('%B %d, %Y'),
                'title': f"NO CLASS TODAY — {today.strftime('%B %d, %Y')}",
                'reason': no_class_today.reason or 'Center Activity / Suspension',
                'message': f"There will be NO CLASS today ({today.strftime('%B %d, %Y')}). Reason: {no_class_today.reason or 'Scheduled Center Break'}. Classes resume next session."
            }
        else:
            upcoming_no_class = NoClassDay.objects.filter(date__gt=today).order_by('date').first()
            if upcoming_no_class:
                no_class_notice = {
                    'status': 'upcoming',
                    'date': str(upcoming_no_class.date),
                    'formatted_date': upcoming_no_class.date.strftime('%B %d, %Y'),
                    'title': f"UPCOMING NO CLASS — {upcoming_no_class.date.strftime('%B %d, %Y')}",
                    'reason': upcoming_no_class.reason or 'Center Activity',
                    'message': f"Please be informed that there will be NO CLASS on {upcoming_no_class.date.strftime('%B %d, %Y')}. Reason: {upcoming_no_class.reason or 'Scheduled Break'}."
                }

        # 3. Dynamic Published Announcements
        pub_announcements = Announcement.objects.filter(status='Published').filter(
            Q(publish_date__isnull=True) | Q(publish_date__lte=today)
        ).filter(
            Q(expiration_date__isnull=True) | Q(expiration_date__gte=today)
        ).order_by('-is_important', '-is_featured', '-created_at')

        ann_serializer = AnnouncementSerializer(pub_announcements, many=True)

        # Featured announcement
        featured_ann = pub_announcements.filter(is_featured=True).first()
        if not featured_ann:
            featured_ann = pub_announcements.filter(is_important=True).first()
        if not featured_ann:
            featured_ann = pub_announcements.first()

        featured_data = AnnouncementSerializer(featured_ann).data if featured_ann else None

        # 4. Enrollment Info
        enroll_info = EnrollmentInfo.objects.filter(is_active=True).first()
        if not enroll_info:
            enroll_info = EnrollmentInfo.objects.create(
                program_name="Child Development Program 2026–2027",
                start_date=date(2026, 8, 25),
                end_date=date(2026, 9, 15),
                age_requirement="3 to 4.11 years old",
                available_slots=30,
                requirements_text="• Photocopy of PSA Birth Certificate\n• 2x2 ID Photo of Child (2 copies)\n• Barangay Certificate of Residency\n• Parent/Guardian Government Issued ID\n• Child Health / Immunization Record",
                instructions_text="Please visit the Barangay Market View 3 Child Development Center to submit your documents before the deadline."
            )
        enroll_data = EnrollmentInfoSerializer(enroll_info).data

        # 5. Dynamic Activities from DB (only actual DB entries)
        activities = Activity.objects.filter(date__gte=today).order_by('date')[:6]
        act_serializer = ActivitySerializer(activities, many=True)

        # 6. Events (Announcements categorized as Events or with event_date)
        events = pub_announcements.filter(Q(category='Events') | Q(event_date__isnull=False)).order_by('event_date', '-created_at')[:6]
        events_serializer = AnnouncementSerializer(events, many=True)

        # 7. Reminders
        reminders = PublicReminder.objects.filter(is_active=True).order_by('-created_at')[:6]
        rem_serializer = PublicReminderSerializer(reminders, many=True)

        # 8. Highlights
        highlights = ProgramHighlight.objects.all().order_by('-date', '-created_at')[:8]
        hl_serializer = ProgramHighlightSerializer(highlights, many=True)

        return Response({
            'school_year_status': sy_data,
            'no_class_notice': no_class_notice,
            'featured_announcement': featured_data,
            'announcements': ann_serializer.data,
            'enrollment_info': enroll_data,
            'activities': act_serializer.data,
            'events': events_serializer.data,
            'reminders': rem_serializer.data,
            'highlights': hl_serializer.data
        })

class AnnouncementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    serializer_class = AnnouncementSerializer
    queryset = Announcement.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        profile = getattr(self.request.user, 'userprofile', None)
        serializer.save(created_by=profile)

class EnrollmentInfoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    serializer_class = EnrollmentInfoSerializer
    queryset = EnrollmentInfo.objects.all().order_by('-updated_at')

class ProgramHighlightViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    serializer_class = ProgramHighlightSerializer
    queryset = ProgramHighlight.objects.all().order_by('-date', '-created_at')


class PublicReminderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PublicReminderSerializer
    queryset = PublicReminder.objects.filter(is_active=True).order_by('-created_at')

    def perform_create(self, serializer):
        profile = getattr(self.request.user, 'userprofile', None)
        serializer.save(created_by=profile)


class TeacherStudentMapAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, 'userprofile', None)
        if not profile or not profile.is_teacher:
            return Response({'detail': 'Only teachers can access student map.'}, status=403)

        sy_id = request.query_params.get('school_year')
        if sy_id:
            active_year = SchoolYear.objects.filter(id=sy_id).first()
        else:
            active_year = SchoolYear.objects.filter(is_active=True).first()

        children = Child.objects.filter(school_year=active_year) if active_year else Child.objects.all()

        results = []
        for child in children:
            parent_profile = child.parents.first()
            lat = float(parent_profile.home_latitude) if parent_profile and parent_profile.home_latitude is not None else 13.9395
            lng = float(parent_profile.home_longitude) if parent_profile and parent_profile.home_longitude is not None else 121.6160

            parent_name = f"{parent_profile.user.first_name} {parent_profile.user.last_name}".strip() if parent_profile and parent_profile.user else "N/A"
            phone = child.mother_phone or child.father_phone or child.other_guardian_phone or 'N/A'
            email = parent_profile.user.email if parent_profile and parent_profile.user else 'N/A'
            photo = child.img.url if child.img else '/static/core/image/bmv3_logo.png'


            results.append({
                'child_id': child.id,
                'child_name': f"{child.first_name} {child.last_name}".strip(),
                'child_photo': photo,
                'parent_name': parent_name if parent_name != "N/A" else (child.mother_first_name if child.mother_first_name != 'No Info' else 'Parent'),
                'phone': phone,
                'email': email,
                'home_latitude': lat,
                'home_longitude': lng,
                'address_text': child.mother_address or child.father_address or 'Barangay Market View 3'
            })

        return Response(results)


class CenterSettingsAPIView(APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_permissions(self):

        if self.request.method == 'GET':
            return []
        return [IsAuthenticated()]

    def get(self, request):
        settings_obj = CenterSettings.get_settings()
        serializer = CenterSettingsSerializer(settings_obj)
        return Response(serializer.data)

    def post(self, request):
        profile = getattr(request.user, 'userprofile', None)
        is_teacher_or_admin = request.user.is_staff or request.user.is_superuser or (profile and profile.is_teacher)
        if not is_teacher_or_admin:
            return Response({'detail': 'Only teachers and center administrators can update school branding & location settings.'}, status=403)

        settings_obj = CenterSettings.get_settings()
        serializer = CenterSettingsSerializer(settings_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class TextblastSendAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = getattr(request.user, 'userprofile', None)
        is_teacher_or_admin = request.user.is_staff or request.user.is_superuser or (profile and profile.is_teacher)
        if not is_teacher_or_admin:
            return Response({'detail': 'Only teachers and center administrators can broadcast textblasts.'}, status=403)

        title = request.data.get('title')
        message = request.data.get('message')
        category = request.data.get('category', 'General Announcement')
        send_email = request.data.get('send_email', True)
        send_sms = request.data.get('send_sms', True)

        if not title or not message:
            return Response({'detail': 'Title and message are required for textblast.'}, status=400)

        active_year = SchoolYear.objects.filter(is_active=True).first()
        if active_year:
            active_children = Child.objects.filter(school_year=active_year)
        else:
            active_children = Child.objects.all()

        email_set = set()
        phone_set = set()

        for child in active_children:
            if child.mother_email and '@' in child.mother_email: email_set.add(child.mother_email)
            if child.father_email and '@' in child.father_email: email_set.add(child.father_email)
            if child.other_guardian_email and '@' in child.other_guardian_email: email_set.add(child.other_guardian_email)

            if child.mother_phone and child.mother_phone != 'No Info': phone_set.add(child.mother_phone)
            if child.father_phone and child.father_phone != 'No Info': phone_set.add(child.father_phone)
            if child.other_guardian_phone and child.other_guardian_phone != 'No Info': phone_set.add(child.other_guardian_phone)

            for p_user in child.parents.all():
                if p_user.user and p_user.user.email:
                    email_set.add(p_user.user.email)



        if not email_set and not phone_set:
            parents = UserProfile.objects.filter(is_teacher=False)
            for p in parents:
                if p.user and p.user.email: email_set.add(p.user.email)

        email_list = list(email_set)
        phone_list = list(phone_set)


        emails_sent = 0
        sms_sent = 0

        # 1. EMAIL DISPATCH (Brevo SMTP Relay)
        if send_email and email_list:
            subject = f"[{category.upper()}] {title}"
            body = f"Dear Parent/Guardian,\n\n{message}\n\nBest regards,\nBarangay Market View 3 Child Development Center"
            for email in email_list:
                try:
                    sent = send_mail(
                        subject=subject,
                        message=body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=True
                    )
                    emails_sent += 1
                except Exception as e:
                    print(f"Email dispatch note for {email}: {e}")


        # 2. SMS DISPATCH (Semaphore SMS Gateway API with Live Defense Simulator fallback)
        if send_sms and phone_list:
            import os
            import requests
            center_cfg = CenterSettings.get_settings()
            semaphore_api_key = getattr(center_cfg, 'semaphore_api_key', '') or os.environ.get('SEMAPHORE_API_KEY', '')
            sms_body = f"[{category.upper()}] {title}: {message}"

            for phone in phone_list:
                if semaphore_api_key:
                    try:
                        resp = requests.post('https://api.semaphore.co/api/v4/messages', data={
                            'apikey': semaphore_api_key,
                            'number': phone,
                            'message': sms_body,
                            'sendername': getattr(center_cfg, 'short_name', 'BMV3')[:11]
                        }, timeout=10)
                        if resp.status_code == 200:
                            sms_sent += 1
                        else:
                            print(f"Semaphore SMS API Error ({resp.status_code}): {resp.text}")
                    except Exception as err:
                        print(f"Semaphore SMS connection exception for {phone}: {err}")
                else:
                    # Simulated dispatch for local testing & live defense demonstration
                    print(f"[SMS TEXTBLAST SIMULATOR] Sent SMS to {phone}: {sms_body}")
                    sms_sent += 1


        try:
            PublicReminder.objects.create(
                title=title,
                description=message,
                category=category,
                is_active=True
            )
        except Exception:
            pass

        log_entry = TextblastLog.objects.create(
            title=title,
            message=message,
            category=category,
            send_email=send_email,
            send_sms=send_sms,
            target_group='All Active Parents',
            emails_sent_count=emails_sent,
            sms_sent_count=sms_sent,
            created_by=profile
        )

        return Response({
            'message': 'Textblast broadcast dispatched successfully!',
            'emails_sent': emails_sent,
            'sms_sent': sms_sent,
            'total_parents_reached': max(emails_sent, sms_sent),
            'log_id': log_entry.id
        })


class TextblastHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = TextblastLog.objects.all().order_by('-created_at')
        serializer = TextblastLogSerializer(logs, many=True)
        return Response(serializer.data)


