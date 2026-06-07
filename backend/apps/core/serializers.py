from rest_framework import serializers
from .models import (Child, AttendanceRecord, MilestoneRecord, NutritionRecord, SchoolYear, 
                     EngagementRecord, ECCDDomain, ECCDMilestone, ECCDAssessment, ECCDMilestoneScore, BMIRecord)

class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolYear
        fields = '__all__'

class BMIRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BMIRecord
        fields = '__all__'

class ChildSerializer(serializers.ModelSerializer):
    stats = serializers.SerializerMethodField()
    parent_usernames = serializers.SerializerMethodField()
    bmi_records = BMIRecordSerializer(many=True, read_only=True)

    class Meta:
        model = Child
        fields = '__all__'

    def get_parent_usernames(self, obj):
        return [p.user.username for p in obj.parents.all() if p.user]

    def validate(self, attrs):
        dob = attrs.get('dob')
        if dob:
            from datetime import date
            today = date.today()
            if dob >= today:
                raise serializers.ValidationError({'dob': "DOB cannot be today or in the future."})
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age not in [3, 4]:
                raise serializers.ValidationError({'dob': f"Child must be 3 or 4 years old to enroll. Computed age is {age}."})
            attrs['age'] = age
        return attrs

    def get_stats(self, obj):
        # Attendance
        att_records = obj.attendance_records.all()
        total_att = att_records.count()
        present = att_records.filter(status='present').count()
        att_pct = round((present / total_att) * 100) if total_att > 0 else 0

        # Milestones (ECCD Tracker)
        from .models import SchoolYear, ECCDMilestone, ECCDAssessment, ECCDMilestoneScore
        assessments = obj.eccd_assessments.all()
        if obj.school_year:
            assessments = assessments.filter(school_year=obj.school_year)
        else:
            active_year = SchoolYear.objects.filter(is_active=True).first()
            if active_year:
                assessments = assessments.filter(school_year=active_year)
            
        total_possible = ECCDMilestone.objects.count()
        achieved = 0
        if total_possible > 0:
            achieved = ECCDMilestoneScore.objects.filter(
                assessment__in=assessments,
                teacher_score=1
            ).values('milestone').distinct().count()
            mile_pct = round((achieved / total_possible) * 100)
        else:
            mile_pct = 0

        # Nutrition
        n_recs = obj.nutrition_records.all()
        n_days = n_recs.count()
        tot_n_pct = 0
        for n in n_recs:
            if n.snack_status in ['Naubos', 'Finished']:
                tot_n_pct += 100
            elif n.snack_status in ['May tira', 'Some Left']:
                tot_n_pct += 50
        nut_pct = round(tot_n_pct / n_days) if n_days > 0 else 0

        return {
            'attendance': att_pct,
            'milestones': mile_pct,
            'milestones_achieved': achieved,
            'milestones_total': total_possible,
            'nutrition': nut_pct
        }

class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = '__all__'

class MilestoneRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MilestoneRecord
        fields = '__all__'



class NutritionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionRecord
        fields = '__all__'

class EngagementRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EngagementRecord
        fields = '__all__'

# BMIRecordSerializer defined above ChildSerializer

# ==========================================
# ECCD MILESTONE TRACKER SERIALIZERS
# ==========================================

class ECCDMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ECCDMilestone
        fields = '__all__'

class ECCDDomainSerializer(serializers.ModelSerializer):
    milestones = ECCDMilestoneSerializer(many=True, read_only=True)
    class Meta:
        model = ECCDDomain
        fields = '__all__'

class ECCDMilestoneScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ECCDMilestoneScore
        fields = '__all__'

class ECCDAssessmentSerializer(serializers.ModelSerializer):
    scores = ECCDMilestoneScoreSerializer(many=True, read_only=True)
    class Meta:
        model = ECCDAssessment
        fields = '__all__'

class ParentProfileSerializer(serializers.Serializer):
    name = serializers.CharField()
    child_id = serializers.IntegerField(allow_null=True)
    img = serializers.URLField(allow_null=True, required=False)

from .models import NoClassDay
class NoClassDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = NoClassDay
        fields = '__all__'

from .models import ScoringAccessRequest
class ScoringAccessRequestSerializer(serializers.ModelSerializer):
    child_name = serializers.ReadOnlyField(source='child.first_name')
    child_lastname = serializers.ReadOnlyField(source='child.last_name')
    parent_name = serializers.ReadOnlyField(source='parent.user.username')
    class Meta:
        model = ScoringAccessRequest
        fields = '__all__'
        read_only_fields = ('parent', 'approved_at')

from .models import Activity, StudentActivityCompletion

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'

class StudentActivityCompletionSerializer(serializers.ModelSerializer):
    child_name = serializers.ReadOnlyField(source='child.first_name')
    child_lastname = serializers.ReadOnlyField(source='child.last_name')
    activity_name = serializers.ReadOnlyField(source='activity.name')
    class Meta:
        model = StudentActivityCompletion
        fields = '__all__'
