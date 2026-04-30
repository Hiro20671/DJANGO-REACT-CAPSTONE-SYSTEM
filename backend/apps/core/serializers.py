from rest_framework import serializers
from .models import Child, AttendanceRecord, MilestoneRecord, BehaviorRecord, NutritionRecord

class ChildSerializer(serializers.ModelSerializer):
    stats = serializers.SerializerMethodField()

    class Meta:
        model = Child
        fields = '__all__'

    def get_stats(self, obj):
        # Attendance
        att_records = obj.attendance_records.all()
        total_att = att_records.count()
        present = att_records.filter(status='present').count()
        att_pct = round((present / total_att) * 100) if total_att > 0 else 0

        # Milestones
        m_rec = getattr(obj, 'milestone_record', None)
        ach = 0
        if m_rec and isinstance(m_rec.tasks, dict):
            ach = sum(1 for v in m_rec.tasks.values() if v == 'achieved')
        mile_pct = round((ach / 16) * 100)

        # Behavior
        b_recs = obj.behavior_records.all()
        pos = b_recs.filter(behavior_type='positive').count()
        neg = b_recs.filter(behavior_type='negative').count()
        neu = b_recs.filter(behavior_type='neutral').count()
        tot = pos + neg + neu
        beh_pct = round(((pos + neu) / tot) * 100) if tot > 0 else 0

        # Nutrition
        n_recs = obj.nutrition_records.all()
        n_days = n_recs.count()
        tot_n_pct = 0
        for n in n_recs:
            eaten = sum([n.breakfast, n.snack1, n.lunch, n.snack2])
            tot_n_pct += (eaten / 4) * 100
        nut_pct = round(tot_n_pct / n_days) if n_days > 0 else 0

        return {
            'attendance': att_pct,
            'milestones': mile_pct,
            'behavior': beh_pct,
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

class BehaviorRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BehaviorRecord
        fields = '__all__'

class NutritionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionRecord
        fields = '__all__'

class ParentProfileSerializer(serializers.Serializer):
    name = serializers.CharField()
    child_id = serializers.IntegerField(allow_null=True)
    img = serializers.URLField(allow_null=True, required=False)
