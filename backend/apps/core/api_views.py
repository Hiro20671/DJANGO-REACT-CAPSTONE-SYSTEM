from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Child, UserProfile
from .serializers import ChildSerializer

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
            children = Child.objects.filter(parent=profile)
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

class ChildListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.userprofile
        if profile.is_teacher:
            children = Child.objects.all().order_by('-date_added')
        else:
            children = Child.objects.filter(parent=profile).order_by('-date_added')
            
        serializer = ChildSerializer(children, many=True)
        return Response(serializer.data)
