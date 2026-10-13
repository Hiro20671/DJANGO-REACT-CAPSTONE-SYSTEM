from rest_framework import viewsets, parsers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated

from .models import Child, UserProfile, AttendanceRecord, MilestoneRecord, NutritionRecord, SchoolYear, EngagementRecord, PasswordResetOTP, NoClassDay, ECCDDomain, ECCDMilestone, ECCDAssessment, ECCDMilestoneScore, BMIRecord, CenterSettings, PublicReminder, TextblastLog, ECCDBookletRecord
from .serializers import ChildSerializer, AttendanceRecordSerializer, MilestoneRecordSerializer, NutritionRecordSerializer, SchoolYearSerializer, EngagementRecordSerializer, NoClassDaySerializer, ECCDDomainSerializer, ECCDMilestoneSerializer, ECCDAssessmentSerializer, ECCDMilestoneScoreSerializer, BMIRecordSerializer, CenterSettingsSerializer, PublicReminderSerializer, TextblastLogSerializer, ECCDBookletRecordSerializer


from django.core.mail import send_mail
from django.conf import settings
import random
import string
from django.contrib.auth.models import User

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_parent_account(request):
    profile = getattr(request.user, 'userprofile', None)
    if not (request.user.is_superuser or (profile and profile.is_teacher)):
        return Response({'detail': 'Teacher permission required.'}, status=403)
        
    child_id = request.data.get('child_id')
    child = None
    if child_id:
        try:
            child = Child.objects.get(id=child_id)
        except Child.DoesNotExist:
            return Response({'detail': 'Child record not found.'}, status=404)

        # Check whether the child already has an associated parent account
        existing_parent = child.parents.filter(user__isnull=False).first()
        if existing_parent and existing_parent.user:
            return Response({
                'already_exists': True,
                'username': existing_parent.user.username,
                'email': existing_parent.user.email,
                'first_login': existing_parent.first_login,
                'message': f"A parent account already exists for {child.first_name} {child.last_name} with username: '{existing_parent.user.username}'."
            }, status=200)

    email = request.data.get('email')
    if not email and child:
        email = child.mother_email or child.father_email or child.other_guardian_email or child.email

    if not email and child:
        # Generate clean institutional placeholder email for child's guardian
        clean_first = "".join(filter(str.isalnum, child.first_name.lower()))
        email = f"parent_{clean_first}{child.id}@bmv3.local"
    elif not email:
        return Response({'detail': 'Email or child ID is required to generate parent account.'}, status=400)
        
    # Check if a user with this email already exists
    if User.objects.filter(email=email).exists():
        existing_user = User.objects.filter(email=email).first()
        existing_profile, _ = UserProfile.objects.get_or_create(user=existing_user, defaults={'is_teacher': False})
        if child and not child.parents.filter(id=existing_profile.id).exists():
            child.parents.add(existing_profile)
        return Response({
            'already_exists': True,
            'username': existing_user.username,
            'email': existing_user.email,
            'message': f"Account with email '{email}' already exists (Username: {existing_user.username}) and has been connected to the pupil."
        }, status=200)

    # Generate unique username and secure temporary password
    prefix = "".join(filter(str.isalnum, email.split('@')[0].lower()))[:8] or "parent"
    username = f"{prefix}_{random.randint(100, 999)}"
    while User.objects.filter(username=username).exists():
        username = f"{prefix}_{random.randint(1000, 9999)}"

    # Temporary password matching security requirements: letters, digits, special character
    letters = ''.join(random.choices(string.ascii_letters, k=5))
    digits = ''.join(random.choices(string.digits, k=3))
    password = f"Bmv3!{letters}{digits}"

    user = User.objects.create_user(username=username, email=email, password=password)
    user_profile = UserProfile.objects.create(user=user, is_teacher=False, first_login=True)

    if child:
        child.parents.add(user_profile)

    # Optional email notification
    from django.core.mail import send_mail
    email_dispatched = False
    try:
        subject = "BMV3 Child Development Center - Parent Login Account"
        message = (
            f"Hello,\n\n"
            f"Your parent account for BMV3 Child Development Center has been provisioned.\n\n"
            f"Username: {username}\n"
            f"Temporary Password: {password}\n\n"
            f"Please log in and update your temporary password on first login.\n\n"
            f"BMV3 Child Development Center"
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=True
        )
        email_dispatched = True
    except Exception as e:
        print(f"Failed to send credentials email: {e}")

    return Response({
        'success': True,
        'username': username,
        'temporary_password': password,
        'email': email,
        'email_sent': email_dispatched,
        'first_login': True,
        'child_name': f"{child.first_name} {child.last_name}" if child else None,
        'message': f"Parent account '{username}' successfully generated! Please provide these temporary credentials to the parent."
    })

class TeacherDashboardStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, 'userprofile', None)
        if not profile or not profile.is_teacher:
            return Response({'detail': 'Teacher permission required.'}, status=403)
            
        active_year = SchoolYear.objects.filter(is_active=True).first()
        school_year_id = request.query_params.get('school_year')
        
        target_year = None
        if school_year_id and str(school_year_id).strip() != '' and str(school_year_id).upper() != 'ALL':
            target_year = SchoolYear.objects.filter(id=school_year_id).first()
        elif (school_year_id is None or str(school_year_id).strip() == '') and active_year:
            target_year = active_year

        qs = Child.objects.all()
        if target_year:
            qs = qs.filter(school_year=target_year)
        elif school_year_id and str(school_year_id).upper() == 'ALL':
            pass
        elif active_year:
            qs = qs.filter(school_year=active_year)

        shift = request.query_params.get('shift')
        if shift:
            qs = qs.filter(shift__iexact=shift)
            
        total_children = qs.filter(enrollment_status='Enrolled').count()
        pending = qs.filter(enrollment_status='Pending').count()
        present = qs.filter(attendance_status='Present').count()
        absent = qs.filter(attendance_status='Absent').count()
        late = qs.filter(attendance_status='Late').count()
        morning_count = qs.filter(enrollment_status='Enrolled', shift='Morning').count()
        afternoon_count = qs.filter(enrollment_status='Enrolled', shift='Afternoon').count()
        
        data = {
            'total_children': total_children,
            'pending_count': pending,
            'morning_count': morning_count,
            'afternoon_count': afternoon_count,
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
            from django.db.models import Q
            parent_email = (request.user.email or '').strip()
            parent_q = Q(parents=profile)
            if parent_email:
                parent_q |= Q(mother_email__iexact=parent_email) | Q(father_email__iexact=parent_email) | Q(other_guardian_email__iexact=parent_email) | Q(email__iexact=parent_email)
            qs = Child.objects.filter(parent_q).distinct()
            for c in qs:
                if profile not in c.parents.all():
                    c.parents.add(profile)

            child_id = request.query_params.get('child') or request.query_params.get('child_id')
            if child_id:
                qs = qs.filter(id=child_id)

            school_year_id = request.query_params.get('school_year')
            if school_year_id:
                qs = qs.filter(school_year_id=school_year_id)
            else:
                active_year = SchoolYear.objects.filter(is_active=True).first()
                if active_year:
                    active_qs = qs.filter(Q(school_year=active_year) | Q(school_year__isnull=True) | Q(enrollment_status='Pending'))
                    if active_qs.exists():
                        qs = active_qs
                
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
                # If parent user doesn't have a personal name yet, set it from the child's guardian details
                user = self.request.user
                if not user.first_name or user.first_name in ('Parent', 'parent', 'Elena', 'elena'):
                    guardian_fname = child.mother_first_name or child.father_first_name or child.other_guardian_first_name
                    guardian_lname = child.mother_last_name or child.father_last_name or child.other_guardian_last_name
                    if guardian_fname and guardian_fname != 'No Info':
                        user.first_name = guardian_fname
                        if guardian_lname and guardian_lname != 'No Info':
                            user.last_name = guardian_lname
                        user.save()
            else:
                child = serializer.save(school_year=active_year)
            child.parents.add(profile)
        else:
            serializer.save(school_year=active_year)

    def get_queryset(self):
        profile = getattr(self.request.user, 'userprofile', None)
        if not profile:
            return Child.objects.none()
        
        shift_param = self.request.query_params.get('shift')
        school_year_id = self.request.query_params.get('school_year')

        if profile.is_teacher:
            qs = Child.objects.all().order_by('-date_added')
            if shift_param and shift_param.strip() and shift_param.upper() != 'ALL':
                qs = qs.filter(shift__iexact=shift_param.strip())

            if school_year_id and str(school_year_id).strip() != '' and str(school_year_id).upper() != 'ALL':
                qs = qs.filter(school_year_id=school_year_id)
            elif school_year_id and str(school_year_id).upper() == 'ALL':
                pass
            else:
                active_year = SchoolYear.objects.filter(is_active=True).first()
                if active_year:
                    from django.db.models import Q
                    qs = qs.filter(Q(school_year=active_year) | Q(enrollment_status='Pending'))
            return qs
        else:
            all_students = self.request.query_params.get('all_students') == 'true' or self.request.query_params.get('scope') == 'all'
            if all_students and school_year_id:
                # Parents viewing historical archive directory of all pupils for that school year
                qs = Child.objects.filter(school_year_id=school_year_id).exclude(enrollment_status__in=['Pending', 'Rejected']).order_by('last_name', 'first_name')
                if shift_param and shift_param.strip() and shift_param.upper() != 'ALL':
                    qs = qs.filter(shift__iexact=shift_param.strip())
                return qs

            from django.db.models import Q
            parent_email = (self.request.user.email or '').strip()
            parent_q = Q(parents=profile)
            if parent_email:
                parent_q |= Q(mother_email__iexact=parent_email) | Q(father_email__iexact=parent_email) | Q(other_guardian_email__iexact=parent_email) | Q(email__iexact=parent_email)
            qs = Child.objects.filter(parent_q).distinct().order_by('-date_added')
            
            for c in qs:
                if profile not in c.parents.all():
                    c.parents.add(profile)

            if school_year_id and str(school_year_id).strip() != '' and str(school_year_id).upper() != 'ALL':
                qs = qs.filter(school_year_id=school_year_id)
            else:
                active_year = SchoolYear.objects.filter(is_active=True).first()
                if active_year:
                    active_qs = qs.filter(Q(school_year=active_year) | Q(school_year__isnull=True) | Q(enrollment_status='Pending'))
                    if active_qs.exists():
                        qs = active_qs
            return qs

class AttendanceRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AttendanceRecordSerializer

    def create(self, request, *args, **kwargs):
        child_id = request.data.get('child')
        date = request.data.get('date')
        session = request.data.get('session') or 'Morning'
        status_val = request.data.get('status')
        absence_reason = request.data.get('absence_reason', '')
        active_year = SchoolYear.objects.filter(is_active=True).first()

        record, created = AttendanceRecord.objects.update_or_create(
            child_id=child_id,
            date=date,
            session=session,
            defaults={
                'status': status_val,
                'absence_reason': absence_reason,
                'school_year': active_year
            }
        )
        serializer = self.get_serializer(record)
        from rest_framework import status as http_status
        return Response(serializer.data, status=http_status.HTTP_201_CREATED if created else http_status.HTTP_200_OK)

    def get_queryset(self):
        profile = getattr(self.request.user, 'userprofile', None)
        if not profile:
            return AttendanceRecord.objects.none()
            
        if profile.is_teacher:
            qs = AttendanceRecord.objects.all()
            shift = self.request.query_params.get('shift')
            if shift and shift != 'All':
                qs = qs.filter(child__shift__iexact=shift)
        else:
            parent_children = Child.objects.filter(parents=profile)
            qs = AttendanceRecord.objects.filter(child__in=parent_children)
        
        school_year_id = self.request.query_params.get('school_year')
        session = self.request.query_params.get('session')
        date = self.request.query_params.get('date')

        if school_year_id:
            qs = qs.filter(school_year_id=school_year_id)
        elif profile.is_teacher:
            active_year = SchoolYear.objects.filter(is_active=True).first()
            if active_year:
                qs = qs.filter(school_year=active_year)
            
        if session and session != 'All':
            qs = qs.filter(session__iexact=session)
        if date:
            qs = qs.filter(date=date)

        return qs

class MilestoneRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MilestoneRecordSerializer

    def get_queryset(self):
        profile = getattr(self.request.user, 'userprofile', None)
        if not profile:
            return MilestoneRecord.objects.none()
            
        if profile.is_teacher:
            qs = MilestoneRecord.objects.all()
            shift = self.request.query_params.get('shift')
            if shift and shift != 'All':
                qs = qs.filter(child__shift__iexact=shift)
        else:
            parent_children = Child.objects.filter(parents=profile)
            qs = MilestoneRecord.objects.filter(child__in=parent_children)
        
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
            
        if profile.is_teacher:
            qs = NutritionRecord.objects.all()
            shift = self.request.query_params.get('shift')
            if shift and shift != 'All':
                qs = qs.filter(child__shift__iexact=shift)
        else:
            parent_children = Child.objects.filter(parents=profile)
            qs = NutritionRecord.objects.filter(child__in=parent_children)
        
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
        active_year = SchoolYear.objects.filter(is_active=True).first()
        serializer.save(school_year=active_year)

    def perform_update(self, serializer):
        serializer.save()

    def get_queryset(self):
        profile = getattr(self.request.user, 'userprofile', None)
        if not profile:
            return BMIRecord.objects.none()
            
        if profile.is_teacher:
            qs = BMIRecord.objects.all()
            shift = self.request.query_params.get('shift')
            if shift and shift != 'All':
                qs = qs.filter(child__shift__iexact=shift)
        else:
            parent_children = Child.objects.filter(parents=profile)
            qs = BMIRecord.objects.filter(child__in=parent_children)
        
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
            default_date = getattr(active_year, f'eccd_{quarter}_start', None) or date.today()
            
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
            
        if profile.is_teacher:
            qs = EngagementRecord.objects.all()
            shift = self.request.query_params.get('shift')
            if shift and shift != 'All':
                qs = qs.filter(child__shift__iexact=shift)
        else:
            parent_children = Child.objects.filter(parents=profile)
            qs = EngagementRecord.objects.filter(child__in=parent_children)
        
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
        if profile.is_teacher:
            qs = ECCDAssessment.objects.all()
            shift = self.request.query_params.get('shift')
            if shift and shift != 'All':
                qs = qs.filter(child__shift__iexact=shift)
        else:
            parent_children = Child.objects.filter(parents=profile)
            qs = ECCDAssessment.objects.filter(child__in=parent_children)
        
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
            from django.db.models import Q
            parent_email = (request.user.email or '').strip()
            parent_q = Q(parents=profile)
            if parent_email:
                parent_q |= Q(mother_email__iexact=parent_email) | Q(father_email__iexact=parent_email) | Q(other_guardian_email__iexact=parent_email) | Q(email__iexact=parent_email)
            children = Child.objects.filter(parent_q).distinct()
            for c in children:
                if profile not in c.parents.all():
                    c.parents.add(profile)
            
            school_year_id = request.query_params.get('school_year')
            if school_year_id:
                children = children.filter(school_year_id=school_year_id)
            else:
                active_year = SchoolYear.objects.filter(is_active=True).first()
                if active_year:
                    children = children.filter(Q(school_year=active_year) | Q(school_year__isnull=True) | Q(enrollment_status='Pending'))
                    
            if not children.exists():
                return Response({'detail': 'No child linked for this academic year.'}, status=404)
        except UserProfile.DoesNotExist:
            return Response({'detail': 'User profile missing.'}, status=400)

        child_param = request.query_params.get('child') or request.query_params.get('child_id')
        if child_param:
            child = children.filter(id=child_param).first() or children.first()
        else:
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

    def perform_create(self, serializer):
        instance = serializer.save()
        if instance.is_active:
            SchoolYear.objects.exclude(id=instance.id).update(is_active=False)

    @action(detail=False, methods=['post'])
    def archive_and_rollover(self, request):
        profile = getattr(request.user, 'userprofile', None)
        if not profile or not profile.is_teacher:
            return Response({'error': 'Only teachers can perform academic year rollover.'}, status=403)

        next_name = (request.data.get('next_school_year_name') or '').strip()
        archive_name = (request.data.get('archive_label') or request.data.get('archive_name') or '').strip()

        if not next_name:
            return Response({'error': 'Please provide the next school year name to activate (e.g. 2026-2027).'}, status=400)

        current_active = SchoolYear.objects.filter(is_active=True).first()
        
        # 1. Archive current active year
        disabled_parents_count = 0
        if current_active:
            if archive_name and archive_name != current_active.name:
                if not SchoolYear.objects.exclude(id=current_active.id).filter(name=archive_name).exists():
                    current_active.name = archive_name
            current_active.is_active = False
            current_active.save()

            # Disable parent accounts whose children belong to this archived school year
            archived_children = Child.objects.filter(school_year=current_active)
            for child in archived_children:
                for parent_prof in child.parents.all():
                    if not parent_prof.is_teacher:
                        has_other_active = parent_prof.children.filter(school_year__is_active=True).exclude(school_year=current_active).exists()
                        if not has_other_active:
                            parent_prof.is_account_restricted = True
                            parent_prof.save()
                            if parent_prof.user:
                                parent_prof.user.is_active = False
                                parent_prof.user.save()
                            disabled_parents_count += 1

        # 2. Create or activate next school year
        next_sy = SchoolYear.objects.filter(name=next_name).first()
        if not next_sy:
            import re, datetime
            years = [int(p) for p in re.findall(r'\d{4}', next_name)]
            if len(years) >= 2:
                sy_start_year, sy_end_year = years[0], years[1]
            elif len(years) == 1:
                sy_start_year, sy_end_year = years[0], years[0] + 1
            else:
                today_year = datetime.date.today().year
                sy_start_year, sy_end_year = today_year, today_year + 1

            next_sy = SchoolYear.objects.create(
                name=next_name,
                is_active=True,
                is_deleted=False,
                start_date=datetime.date(sy_start_year, 8, 24),
                end_date=datetime.date(sy_end_year, 5, 28),
                eccd_1st_start=datetime.date(sy_start_year, 9, 1),
                eccd_1st_end=datetime.date(sy_start_year, 9, 25),
                eccd_2nd_start=datetime.date(sy_end_year, 1, 4),
                eccd_2nd_end=datetime.date(sy_end_year, 1, 29),
                eccd_3rd_start=datetime.date(sy_end_year, 5, 3),
                eccd_3rd_end=datetime.date(sy_end_year, 5, 28),
            )
        else:
            next_sy.is_active = True
            next_sy.is_deleted = False
            next_sy.save()

        # Ensure only next_sy is active
        SchoolYear.objects.exclude(id=next_sy.id).update(is_active=False)

        return Response({
            'status': 'success',
            'message': f"School Year '{current_active.name if current_active else 'Previous'}' archived. Next School Year '{next_sy.name}' is now active!",
            'archived_year_id': current_active.id if current_active else None,
            'archived_year_name': current_active.name if current_active else None,
            'active_year_id': next_sy.id,
            'active_year_name': next_sy.name,
            'disabled_parents_count': disabled_parents_count
        })

    @action(detail=True, methods=['post'])
    def undo_archive(self, request, pk=None):
        profile = getattr(request.user, 'userprofile', None)
        if not profile or not profile.is_teacher:
            return Response({'error': 'Only teachers can restore school years.'}, status=403)

        sy = get_object_or_404(SchoolYear, pk=pk)

        # Make this school year active
        sy.is_active = True
        sy.is_deleted = False
        sy.save()
        SchoolYear.objects.exclude(id=sy.id).update(is_active=False)

        # Re-enable parent accounts for pupils enrolled in this restored school year
        re_enabled_count = 0
        children = Child.objects.filter(school_year=sy)
        for child in children:
            for parent_prof in child.parents.all():
                if not parent_prof.is_teacher:
                    parent_prof.is_account_restricted = False
                    parent_prof.save()
                    if parent_prof.user:
                        parent_prof.user.is_active = True
                        parent_prof.user.save()
                    re_enabled_count += 1

        return Response({
            'status': 'success',
            'message': f"School Year '{sy.name}' has been restored as active! Associated parent accounts have been re-enabled.",
            'active_year_id': sy.id,
            'active_year_name': sy.name,
            're_enabled_parents_count': re_enabled_count
        })

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

        # Update user first_name and last_name so their personal name appears across the system
        if first_name and first_name != 'No Info':
            user = request.user
            user.first_name = first_name
            if last_name and last_name != 'No Info':
                user.last_name = last_name
            user.save()
        
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
        profile = getattr(user, 'userprofile', None)
        
        if not profile or not profile.first_login:
            return Response({'error': 'Password change requirement has already been satisfied or is not applicable.'}, status=400)
            
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password') or request.data.get('confirmPassword')
        
        # 0. Validate and update new username if provided
        new_username = (request.data.get('new_username') or '').strip()
        if new_username and new_username != user.username:
            from django.contrib.auth.models import User
            if User.objects.filter(username__iexact=new_username).exclude(id=user.id).exists():
                return Response({'error': f"The username '{new_username}' is already taken. Please choose another username."}, status=400)
            import re
            if not re.match(r'^[a-zA-Z0-9_.-]+$', new_username):
                return Response({'error': 'Username can only contain letters, numbers, underscores, dots, and hyphens.'}, status=400)
            if len(new_username) < 3:
                return Response({'error': 'Username must be at least 3 characters long.'}, status=400)
            user.username = new_username

        # Clear any accidental demo names so it shows 'Parent' until they enroll their child
        if user.first_name in ('Elena', 'elena', 'Demo'):
            user.first_name = 'Parent'
            user.last_name = ''

        # 1. Validate current password (if supplied)
        if current_password:
            if not user.check_password(current_password):
                return Response({'error': 'Current temporary password is incorrect.'}, status=400)
        
        # 2. Check new password presence
        if not new_password:
            return Response({'error': 'New password is required.'}, status=400)
            
        # 3. Check confirmation match
        if confirm_password is not None and new_password != confirm_password:
            return Response({'error': 'New password and confirmation do not match.'}, status=400)
            
        # 4. Check minimum length
        if len(new_password) < 8:
            return Response({'error': 'Password must be at least 8 characters long.'}, status=400)
            
        # 5. Validate using Django password validators
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            return Response({'error': ' '.join(e.messages)}, status=400)
            
        # 6. Set new hashed password
        user.set_password(new_password)
        user.save()
        
        # 7. Mark requirement completed
        profile.first_login = False
        profile.save()
        
        # 8. Maintain authenticated session
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)
        
        return Response({
            'success': True,
            'message': f"Account credentials updated successfully! Your username is now '{user.username}'."
        })

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
    
    def post(self, request, child_id=None):
        profile = getattr(request.user, 'userprofile', None)
        if not (request.user.is_superuser or (profile and profile.is_teacher)):
            return Response({'error': 'Teacher permission required.'}, status=403)

        child_id = child_id or request.data.get('child_id')
        child = None
        if child_id:
            try:
                child = Child.objects.get(id=child_id)
            except Child.DoesNotExist:
                return Response({'error': 'Child record not found.'}, status=404)

        parent_name = request.data.get('parent_name', '').strip()
        email = request.data.get('email', '').strip()

        if child and not parent_name:
            parent_name = (
                f"{child.mother_first_name} {child.mother_last_name}".strip() if child.mother_first_name else
                (f"{child.father_first_name} {child.father_last_name}".strip() if child.father_first_name else
                (f"{child.other_guardian_first_name} {child.other_guardian_last_name}".strip() if child.other_guardian_first_name else
                f"Guardian of {child.first_name}"))
            )

        if not parent_name:
            parent_name = "Parent"

        # Generate secure temporary password
        letters = ''.join(random.choices(string.ascii_letters, k=5))
        digits = ''.join(random.choices(string.digits, k=3))
        password = f"Bmv3!{letters}{digits}"

        # CRITICAL SAFETY RULE: NEVER EVER MATCH OR MODIFY A TEACHER, STAFF, OR SUPERUSER ACCOUNT!
        existing_user = None
        if child:
            existing_parent_profile = child.parents.filter(
                user__isnull=False,
                is_teacher=False,
                user__is_staff=False,
                user__is_superuser=False
            ).first()
            if existing_parent_profile and existing_parent_profile.user:
                existing_user = existing_parent_profile.user

        if not existing_user and email and '@' in email and not email.endswith('.local'):
            # Only consider genuine parent accounts (never teachers, staff, or superusers)
            from django.db.models import Q
            candidate = User.objects.filter(
                email=email,
                is_staff=False,
                is_superuser=False
            ).exclude(
                userprofile__is_teacher=True
            ).first()
            if candidate:
                existing_user = candidate

        try:
            if existing_user:
                user = existing_user
                user.set_password(password)
                if email and '@' in email:
                    user.email = email
                user.save()

                p_profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'is_teacher': False})
                p_profile.is_teacher = False
                p_profile.first_login = True
                p_profile.save()

                if child and not child.parents.filter(id=p_profile.id).exists():
                    child.parents.add(p_profile)

                username = user.username
                account_is_new = False
            else:
                # Generate unique parent username (avoid using teacher/admin names)
                clean_prefix = "".join(filter(str.isalnum, parent_name.split()[0].lower())) if parent_name else "parent"
                if not clean_prefix or clean_prefix in ['admin', 'teacher', 'staff', 'root']:
                    clean_prefix = "parent"
                username = f"{clean_prefix}_{random.randint(100, 999)}"
                while User.objects.filter(username=username).exists():
                    username = f"{clean_prefix}_{random.randint(1000, 9999)}"

                user_email = email if (email and '@' in email) else f"{username}@bmv3.local"

                user = User.objects.create_user(username=username, email=user_email, password=password)
                user.is_staff = False
                user.is_superuser = False
                name_parts = parent_name.split() if parent_name else ['Parent']
                user.first_name = name_parts[0]
                if len(name_parts) > 1:
                    user.last_name = " ".join(name_parts[1:])
                user.save()

                p_profile = UserProfile.objects.create(user=user, is_teacher=False, first_login=True)
                if child:
                    child.parents.add(p_profile)

                account_is_new = True

            # Send credentials via Brevo SMTP relay ONLY if a real deliverable email is provided
            has_real_email = bool(email and '@' in email and not email.endswith('.local') and not email.endswith('.test'))
            email_sent = False
            email_error = None

            if has_real_email:
                from django.core.mail import EmailMultiAlternatives
                from django.utils.html import strip_tags

                login_url = request.build_absolute_uri('/login/') if hasattr(request, 'build_absolute_uri') else 'https://jeremy2004.pythonanywhere.com/login/'
                subject = "Welcome to BMV3 Child Care - Your Account Details"
                from_email = f"BMV3 Child Development Center <{settings.DEFAULT_FROM_EMAIL}>"
                html_content = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff;">
                    <div style="text-align: center; margin-bottom: 20px;">
                        <h2 style="color: #1e40af; margin: 0 0 6px 0;">BMV3 Child Development Center</h2>
                        <p style="color: #64748b; margin: 0; font-size: 0.9rem;">Parent Portal Access & Login Credentials</p>
                    </div>
                    <p style="color: #334155; font-size: 1rem;">Hello <strong>{parent_name}</strong>,</p>
                    <p style="color: #475569; font-size: 0.95rem; line-height: 1.5;">Your parent account has been created. You can now log into the BMV3 Parent Portal to monitor attendance, milestones, daily activities, announcements, and nutrition.</p>
                    
                    <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; padding: 18px; border-radius: 10px; margin: 20px 0;">
                        <h3 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.05rem;">Your Login Credentials:</h3>
                        <p style="margin: 6px 0; font-size: 0.95rem;"><strong>Portal URL:</strong> <a href="{login_url}" style="color: #2563eb;">{login_url}</a></p>
                        <p style="margin: 6px 0; font-size: 0.95rem;"><strong>Username:</strong> <span style="font-weight: 800; color: #1e40af; font-size: 1.15rem; background: #e0f2fe; padding: 2px 8px; border-radius: 6px;">{username}</span></p>
                        <p style="margin: 6px 0; font-size: 0.95rem;"><strong>Temporary Password:</strong> <span style="font-weight: 800; color: #dc2626; font-size: 1.15rem; background: #fee2e2; padding: 2px 8px; border-radius: 6px;">{password}</span></p>
                    </div>
                    
                    <div style="background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 12px 14px; border-radius: 4px; margin-bottom: 20px;">
                        <p style="color: #991b1b; font-weight: 700; margin: 0; font-size: 0.88rem;">
                            IMPORTANT: For your security, you will be prompted to set your personal permanent password immediately upon first login.
                        </p>
                    </div>
                    
                    <p style="margin-top: 24px; color: #64748b; font-size: 0.88rem;">Best Regards,<br><strong>BMV3 Administration & Teaching Staff</strong><br>Barangay Market View, Lucena City</p>
                </div>
                """
                text_content = strip_tags(html_content)
                try:
                    msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send(fail_silently=False)
                    email_sent = True
                except Exception as e:
                    email_sent = False
                    email_error = str(e)
                    print(f"Failed to dispatch Brevo email to {email}: {e}")

            return Response({
                'success': True,
                'account_created': True,
                'already_exists': not account_is_new,
                'username': username,
                'temporary_password': password,
                'parent_name': parent_name,
                'email': email if has_real_email else '',
                'has_email': has_real_email,
                'email_sent': email_sent,
                'email_error': email_error,
                'first_login': True,
                'child_name': f"{child.first_name} {child.last_name}" if child else None,
                'message': f"Parent account successfully created for '{username}'!"
            })

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

class ECCDBookletRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ECCDBookletRecordSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return ECCDBookletRecord.objects.none()
        if user.is_superuser:
            qs = ECCDBookletRecord.objects.all()
            child_id = self.request.query_params.get('child')
            if child_id:
                qs = qs.filter(child_id=child_id)
            return qs
        profile = getattr(user, 'userprofile', None)
        if not profile:
            return ECCDBookletRecord.objects.none()
        qs = ECCDBookletRecord.objects.all()
        child_id = self.request.query_params.get('child')
        if child_id:
            qs = qs.filter(child_id=child_id)
        if not profile.is_teacher:
            parent_children = Child.objects.filter(parents=profile)
            qs = qs.filter(child__in=parent_children)
        return qs

    @action(detail=False, methods=['get', 'post'], url_path='by-child/(?P<child_id>[^/.]+)')
    def by_child(self, request, child_id=None):
        return self._handle_by_child(request, child_id)

    @action(detail=False, methods=['get', 'post'], url_path='by-child')
    def by_child_query(self, request):
        child_id = request.data.get('child_id') or request.query_params.get('child_id') or request.query_params.get('child')
        return self._handle_by_child(request, child_id)

    def _handle_by_child(self, request, child_id):
        if not child_id:
            return Response({'error': 'child_id is required.'}, status=400)
        from django.shortcuts import get_object_or_404
        child = get_object_or_404(Child, pk=child_id)
        if not request.user.is_authenticated:
            return Response({'error': 'Unauthorized'}, status=401)
        if not request.user.is_superuser:
            profile = getattr(request.user, 'userprofile', None)
            if not profile:
                return Response({'error': 'Unauthorized'}, status=403)
            if not profile.is_teacher and not child.parents.filter(id=profile.id).exists():
                return Response({'error': 'Not authorized to access this booklet.'}, status=403)

        booklet, created = ECCDBookletRecord.objects.get_or_create(child=child)

        # Prepopulate defaults if sociodemographic is empty
        if not booklet.sociodemographic:
            booklet.sociodemographic = {
                'child_name': f"{child.first_name} {child.middle_initial or ''} {child.last_name}".strip(),
                'sex': child.gender or '',
                'dob': str(child.dob) if child.dob else '',
                'barangay': child.barangay or '',
                'city': child.city_municipality or 'Lucena City',
                'province': 'Quezon',
                'region': 'Region IV-A (CALABARZON)',
                'handedness': 'Right',
                'is_studying': 'Yes',
                'school_name': 'Barangay Market View 3 Child Development Center',
                'father_name': f"{child.father_first_name or ''} {child.father_last_name or ''}".strip(),
                'father_age': '',
                'father_occupation': '',
                'father_education': '',
                'mother_name': f"{child.mother_first_name or ''} {child.mother_last_name or ''}".strip(),
                'mother_age': '',
                'mother_occupation': '',
                'mother_education': '',
                'siblings_count': '',
                'birth_order': '1st'
            }
            booklet.save()

        if request.method == 'POST':
            from django.utils import timezone
            data = request.data
            is_teacher = request.user.is_superuser or (profile and profile.is_teacher)
            updated_fields = []
            
            allowed_fields = ['sociodemographic', 'mchat_r', 'intake_form', 'consent_form', 'health_record', 'eye_vision', 'growth_chart_data', 'behavior_records']
            if is_teacher:
                allowed_fields.append('examiner_notes')

            for field in allowed_fields:
                if field in data:
                    setattr(booklet, field, data[field])
                    updated_fields.append(field)

            # Record audit trail
            audit_entry = {
                'user': request.user.username,
                'role': 'Teacher' if is_teacher else 'Parent',
                'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                'updated_fields': updated_fields
            }
            if not isinstance(booklet.audit_history, list):
                booklet.audit_history = []
            booklet.audit_history.append(audit_entry)
            booklet.save()

            serializer = ECCDBookletRecordSerializer(booklet, context={'request': request})
            return Response({'success': True, 'data': serializer.data})

        serializer = ECCDBookletRecordSerializer(booklet, context={'request': request})
        return Response(serializer.data)

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
        user = self.request.user
        profile = getattr(user, 'userprofile', None)
        if profile and not profile.is_teacher:
            parent_children = Child.objects.filter(parents=profile)
            qs = StudentActivityCompletion.objects.filter(child__in=parent_children)
        else:
            qs = StudentActivityCompletion.objects.all()
            shift = self.request.query_params.get('shift')
            if shift and shift != 'All':
                qs = qs.filter(child__shift__iexact=shift)
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
        shift = request.query_params.get('shift')
        if shift:
            children = children.filter(shift__iexact=shift)

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
                'shift': child.shift or 'Morning',
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
        test_email = (request.data.get('test_email') or request.data.get('test_recipient') or '').strip()
        school_year_id = request.data.get('school_year_id') or request.data.get('school_year')

        if not title or not message:
            return Response({'detail': 'Title and message are required for textblast.'}, status=400)

        # 1. Resolve children based on SY selection or active SY
        if school_year_id:
            active_children = Child.objects.filter(school_year_id=school_year_id)
        else:
            active_year = SchoolYear.objects.filter(is_active=True).first()
            if active_year:
                active_children = Child.objects.filter(school_year=active_year)
            else:
                active_children = Child.objects.none()

        # If current SY has 0 enrolled children, fall back to all enrolled children across SYs
        if not active_children.exists():
            active_children = Child.objects.all()

        email_set = set()
        phone_set = set()

        for child in active_children:
            if child.mother_email and '@' in child.mother_email: email_set.add(child.mother_email.strip())
            if child.father_email and '@' in child.father_email: email_set.add(child.father_email.strip())
            if child.other_guardian_email and '@' in child.other_guardian_email: email_set.add(child.other_guardian_email.strip())

            if child.mother_phone and child.mother_phone != 'No Info': phone_set.add(child.mother_phone.strip())
            if child.father_phone and child.father_phone != 'No Info': phone_set.add(child.father_phone.strip())
            if child.other_guardian_phone and child.other_guardian_phone != 'No Info': phone_set.add(child.other_guardian_phone.strip())

            for p_user in child.parents.all():
                if p_user.user and p_user.user.email and '@' in p_user.user.email:
                    email_set.add(p_user.user.email.strip())

        # Fallback to parent profiles if still empty
        if not email_set and not phone_set:
            parents = UserProfile.objects.filter(is_teacher=False)
            for p in parents:
                if p.user and p.user.email and '@' in p.user.email:
                    email_set.add(p.user.email.strip())

        # Filter out .local and fake demo domains for real SMTP delivery
        deliverable_emails = {
            e for e in email_set
            if not e.lower().endswith('.local') and not e.lower().endswith('.test') and 'demo.bmv3' not in e.lower()
        }

        # Include test recipient if provided
        if test_email and '@' in test_email:
            deliverable_emails.add(test_email)

        # Include sender's email or DEFAULT_FROM_EMAIL if requested or if no real parent emails found
        if request.data.get('send_copy_to_sender') or (not deliverable_emails and getattr(request.user, 'email', None)):
            if request.user.email and '@' in request.user.email and not request.user.email.endswith('.local'):
                deliverable_emails.add(request.user.email.strip())
            elif settings.DEFAULT_FROM_EMAIL and '@' in settings.DEFAULT_FROM_EMAIL:
                deliverable_emails.add(settings.DEFAULT_FROM_EMAIL)

        email_list = list(deliverable_emails)
        phone_list = list(phone_set)

        emails_sent = 0
        sms_sent = 0
        email_errors = []

        # 1. EMAIL DISPATCH (Brevo SMTP Relay)
        if send_email and email_list:
            from django.core.mail import EmailMultiAlternatives
            subject = f"[{category.upper()}] {title}"
            from_email = f"BMV3 Child Development Center <{settings.DEFAULT_FROM_EMAIL}>"
            html_body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff;">
                <div style="border-bottom: 2px solid #1e40af; padding-bottom: 12px; margin-bottom: 16px;">
                    <span style="background: #1e40af; color: #ffffff; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">{category}</span>
                    <h2 style="color: #0f172a; margin: 10px 0 4px 0; font-size: 1.3rem;">{title}</h2>
                    <div style="color: #64748b; font-size: 0.82rem;">Barangay Market View 3 Child Development Center</div>
                </div>
                <p style="color: #334155; font-size: 0.95rem; line-height: 1.6; white-space: pre-line;">{message}</p>
                <div style="margin-top: 24px; padding-top: 14px; border-top: 1px solid #f1f5f9; color: #94a3b8; font-size: 0.8rem;">
                    This is an official advisory from BMV3 Child Development Center sent to registered parents & guardians via Brevo Relay.
                </div>
            </div>
            """
            text_body = f"[{category.upper()}] {title}\n\n{message}\n\nBarangay Market View 3 Child Development Center"

            for target in email_list:
                try:
                    msg = EmailMultiAlternatives(subject, text_body, from_email, [target])
                    msg.attach_alternative(html_body, "text/html")
                    msg.send(fail_silently=False)
                    emails_sent += 1
                except Exception as e:
                    err_msg = f"{target}: {str(e)}"
                    email_errors.append(err_msg)
                    print(f"Brevo textblast error for {target}: {e}")

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
            'recipients_count': len(email_list),
            'recipients': email_list,
            'email_errors': email_errors,
            'log_id': log_entry.id
        })


class TextblastHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = TextblastLog.objects.all().order_by('-created_at')
        serializer = TextblastLogSerializer(logs, many=True)
        return Response(serializer.data)


class GeneralAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .analytics_engine import get_full_analytics_data
        school_year_id = request.query_params.get('school_year')
        data = get_full_analytics_data(school_year_id=school_year_id)
        return Response(data)


class AIInsightsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from .analytics_engine import get_full_analytics_data, answer_ai_query
        question = request.data.get('question', '')
        school_year_id = request.data.get('school_year') or request.query_params.get('school_year')
        data = get_full_analytics_data(school_year_id=school_year_id)
        answer = answer_ai_query(question, data)
        return Response({
            'status': 'success',
            'question': question,
            'answer': answer
        })


class WithdrawChildAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, child_id):
        profile = getattr(request.user, 'userprofile', None)
        if not (request.user.is_superuser or (profile and profile.is_teacher)):
            return Response({'detail': 'Teacher permission required.'}, status=403)
            
        child = get_object_or_404(Child, pk=child_id)
        withdrawal_date = request.data.get('withdrawal_date') or timezone.now().date()
        withdrawal_reason = request.data.get('withdrawal_reason', '').strip()
        
        child.enrollment_status = 'Withdrawn'
        child.withdrawal_date = withdrawal_date
        child.withdrawal_reason = withdrawal_reason
        child.save()
        
        # Check parent accounts
        # For each parent: check if they have any other actively enrolled children
        restricted_parents = []
        for parent_prof in child.parents.all():
            other_active = parent_prof.children.filter(enrollment_status='Enrolled').exclude(id=child.id).exists()
            if not other_active:
                parent_prof.is_account_restricted = True
                parent_prof.save()
                if parent_prof.user:
                    parent_prof.user.is_active = False
                    parent_prof.user.save()
                restricted_parents.append(parent_prof.user.username if parent_prof.user else 'Unknown')
                
        return Response({
            'success': True,
            'message': f"Student {child.first_name} {child.last_name} has been marked as Withdrawn.",
            'withdrawal_date': str(child.withdrawal_date),
            'restricted_parents': restricted_parents
        })


class ReEnrollChildAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, child_id):
        profile = getattr(request.user, 'userprofile', None)
        if not (request.user.is_superuser or (profile and profile.is_teacher)):
            return Response({'detail': 'Teacher permission required.'}, status=403)

        child = get_object_or_404(Child, pk=child_id)
        child.enrollment_status = 'Enrolled'
        child.withdrawal_date = None
        child.withdrawal_reason = None
        child.save()

        # Reactivate parent account if deactivated
        reactivated_parents = []
        for parent_prof in child.parents.all():
            parent_prof.is_account_restricted = False
            parent_prof.save()
            if parent_prof.user:
                parent_prof.user.is_active = True
                parent_prof.user.save()
                reactivated_parents.append(parent_prof.user.username)

        return Response({
            'success': True,
            'message': f"Student {child.first_name} {child.last_name} has been successfully re-enrolled.",
            'reactivated_parents': reactivated_parents
        })


class TranslateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        text = (request.data.get('text') or '').strip()
        source_lang = (request.data.get('source_lang') or 'en').lower().strip()
        target_lang = (request.data.get('target_lang') or 'tl').lower().strip()

        if not text:
            return Response({'error': 'Please enter text to translate.'}, status=400)

        if source_lang == target_lang:
            return Response({
                'translated_text': text,
                'source_lang': source_lang,
                'target_lang': target_lang
            })

        # Curated domain dictionary for Daycare / ECCD / School communication
        COMMON_PHRASES = {
            "en": {
                "please complete your child's eccd booklet before the assessment.": "Pakikumpleto ang ECCD booklet ng inyong anak bago ang pagtatasa.",
                "please complete your child's eccd booklet before the assessment": "Pakikumpleto ang ECCD booklet ng inyong anak bago ang pagtatasa.",
                "please complete your child's booklet.": "Pakikumpleto ang booklet ng inyong anak.",
                "please bring your child to daycare on time.": "Pakidala po ang inyong anak sa daycare sa tamang oras.",
                "attendance has been recorded for today.": "Naitala na ang pagdalo para sa araw na ito.",
                "student has been marked present.": "Ang mag-aaral ay namarkahan bilang naroroon.",
                "student has been marked absent.": "Ang mag-aaral ay namarkahan bilang liban.",
                "good morning parents and guardians!": "Magandang araw sa mga magulang at tagapag-alaga!",
                "please pick up your child by 10:30 am.": "Pakisundo po ang inyong anak bago mag-10:30 ng umaga.",
                "please pick up your child by 3:30 pm.": "Pakisundo po ang inyong anak bago mag-3:30 ng hapon.",
                "there will be no classes tomorrow.": "Walang pasok bukas.",
                "developmental assessment is scheduled next week.": "Nakatakda ang pagtatasa ng pag-unlad sa susunod na linggo.",
                "welcome to bmv3 child development center.": "Maligayang pagdating sa BMV3 Child Development Center.",
                "parent-teacher meeting": "Pagpupulong ng mga magulang at guro",
                "morning shift": "Pang-umagang sesyon",
                "afternoon shift": "Pang-hapong sesyon"
            },
            "tl": {
                "pakikumpleto ang eccd booklet ng inyong anak bago ang pagtatasa.": "Please complete your child's ECCD booklet before the assessment.",
                "pakikumpleto ang eccd booklet ng inyong anak bago ang pagtatasa": "Please complete your child's ECCD booklet before the assessment.",
                "maligayang pagdating sa bmv3 child development center.": "Welcome to BMV3 Child Development Center.",
                "walang pasok bukas.": "There will be no classes tomorrow.",
                "magandang araw sa mga magulang at tagapag-alaga!": "Good morning parents and guardians!"
            }
        }

        # Check curated phrases
        norm_key = text.lower().strip()
        if source_lang in COMMON_PHRASES and norm_key in COMMON_PHRASES[source_lang]:
            return Response({
                'translated_text': COMMON_PHRASES[source_lang][norm_key],
                'source_lang': source_lang,
                'target_lang': target_lang,
                'engine': 'curated'
            })

        # Try online translation via MyMemory API with 3.5-second timeout
        translated_result = None
        try:
            import urllib.request
            import urllib.parse
            import json

            s_pair = 'en' if source_lang.startswith('en') else 'tl'
            t_pair = 'tl' if target_lang.startswith('tl') or target_lang.startswith('fil') else 'en'
            
            encoded_text = urllib.parse.quote(text)
            url = f"https://api.mymemory.translated.net/get?q={encoded_text}&langpair={s_pair}|{t_pair}"
            req = urllib.request.Request(url, headers={'User-Agent': 'BMV3-Translation-Client/1.0'})
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data.get('responseStatus') == 200:
                    cand = data.get('responseData', {}).get('translatedText')
                    if cand and not cand.startswith('MYMEMORY WARNING'):
                        translated_result = cand
        except Exception:
            pass

        # Fallback word substitution heuristic if network was unavailable
        if not translated_result:
            WORD_MAP_EN_TL = {
                "please": "paki", "complete": "kumpleto", "child": "anak", "children": "mga bata",
                "booklet": "booklet", "before": "bago", "assessment": "pagtatasa", "today": "ngayong araw",
                "tomorrow": "bukas", "teacher": "guro", "parent": "magulang", "parents": "mga magulang",
                "guardian": "tagapag-alaga", "school": "paaralan", "center": "sentro",
                "attendance": "pagdalo", "present": "naroroon", "absent": "liban", "late": "huli",
                "morning": "umaga", "afternoon": "hapon", "class": "klase", "classes": "mga klase",
                "healthy": "malusog", "nutrition": "nutrisyon", "snack": "meryenda", "water": "tubig",
                "welcome": "maligayang pagdating", "thank you": "salamat", "good": "mabuti", "day": "araw"
            }
            WORD_MAP_TL_EN = {v: k for k, v in WORD_MAP_EN_TL.items()}

            words = text.split()
            translated_words = []
            dict_map = WORD_MAP_EN_TL if source_lang == 'en' else WORD_MAP_TL_EN
            for w in words:
                clean_w = w.lower().strip(".,!?:;")
                punct = w[len(clean_w):] if len(w) > len(clean_w) else ''
                trans = dict_map.get(clean_w, clean_w)
                if w and w[0].isupper():
                    trans = trans.capitalize()
                translated_words.append(trans + punct)
            translated_result = " ".join(translated_words)

        return Response({
            'translated_text': translated_result,
            'source_lang': source_lang,
            'target_lang': target_lang
        })


