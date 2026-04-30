from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Child, UserProfile, AttendanceRecord, MilestoneRecord, BehaviorRecord, NutritionRecord
from .serializers import ChildSerializer, AttendanceRecordSerializer, MilestoneRecordSerializer, BehaviorRecordSerializer, NutritionRecordSerializer

class TeacherDashboardStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_children = Child.objects.count()
        present = Child.objects.filter(attendance_status='Present').count()
        absent = Child.objects.filter(attendance_status='Absent').count()
        late = Child.objects.filter(attendance_status='Late').count()
        
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
            children = Child.objects.filter(parents=profile)
            total = children.count()
            data = {
                'total_children': total,
                'attendance': {
                    'present': children.filter(attendance_status='Present').count(),
                    'absent': children.filter(attendance_status='Absent').count(),
                    'late': children.filter(attendance_status='Late').count(),
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
        if profile:
            child = serializer.save()
            child.parents.add(profile)
        else:
            serializer.save()

    def get_queryset(self):
        profile = getattr(self.request.user, 'userprofile', None)
        if not profile:
            return Child.objects.none()
        if profile.is_teacher:
            return Child.objects.all().order_by('-date_added')
        return Child.objects.filter(parents=profile).order_by('-date_added')

class AttendanceRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AttendanceRecordSerializer

    def get_queryset(self):
        profile = getattr(self.request.user, 'userprofile', None)
        if not profile:
            return AttendanceRecord.objects.none()
        if profile.is_teacher:
            return AttendanceRecord.objects.all()
        return AttendanceRecord.objects.filter(child__parents=profile)

class MilestoneRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MilestoneRecordSerializer

    def get_queryset(self):
        profile = getattr(self.request.user, 'userprofile', None)
        if not profile:
            return MilestoneRecord.objects.none()
        if profile.is_teacher:
            return MilestoneRecord.objects.all()
        return MilestoneRecord.objects.filter(child__parents=profile)

class BehaviorRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BehaviorRecordSerializer

    def get_queryset(self):
        profile = getattr(self.request.user, 'userprofile', None)
        if not profile:
            return BehaviorRecord.objects.none()
        if profile.is_teacher:
            return BehaviorRecord.objects.all()
        return BehaviorRecord.objects.filter(child__parents=profile)

class NutritionRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = NutritionRecordSerializer

    def get_queryset(self):
        profile = getattr(self.request.user, 'userprofile', None)
        if not profile:
            return NutritionRecord.objects.none()
        if profile.is_teacher:
            return NutritionRecord.objects.all()
        return NutritionRecord.objects.filter(child__parents=profile)
class ParentHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return past 30 days of attendance, nutrition, behavior, and milestones for the linked child."""
        try:
            profile = request.user.userprofile
            child = Child.objects.filter(parents=profile).first()
            if not child:
                return Response({'detail': 'No child linked.'}, status=404)
        except UserProfile.DoesNotExist:
            return Response({'detail': 'User profile missing.'}, status=400)

        from datetime import datetime, timedelta
        today = datetime.today().date()
        start_date = today - timedelta(days=30)

        # Attendance
        attendance_qs = AttendanceRecord.objects.filter(child=child, date__range=[start_date, today])
        attendance_data = AttendanceRecordSerializer(attendance_qs, many=True).data
        # Nutrition
        nutrition_qs = NutritionRecord.objects.filter(child=child, date__range=[start_date, today])
        nutrition_data = NutritionRecordSerializer(nutrition_qs, many=True).data
        # Behavior
        behavior_qs = BehaviorRecord.objects.filter(child=child, date__range=[start_date, today])
        behavior_data = BehaviorRecordSerializer(behavior_qs, many=True).data
        # Milestones (latest only, but include all milestones records if multiple)
        milestone_qs = MilestoneRecord.objects.filter(child=child)
        milestone_data = MilestoneRecordSerializer(milestone_qs, many=True).data

        return Response({
            'attendance': attendance_data,
            'nutrition': nutrition_data,
            'behavior': behavior_data,
            'milestones': milestone_data,
        })
