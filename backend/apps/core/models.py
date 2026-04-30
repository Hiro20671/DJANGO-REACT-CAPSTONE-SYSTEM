from django.db import models
from django.contrib.auth.models import User

class Enrollment(models.Model):
    full_name = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    email = models.EmailField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

class Subject(models.Model):
    subject_code = models.CharField(max_length=20)
    subject_name = models.CharField(max_length=100)
    instructor = models.CharField(max_length=100)
    room = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    time = models.CharField(max_length=50)
    
    def __str__(self):
        return self.subject_name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_teacher = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {'Teacher' if self.is_teacher else 'Parent'}"

class Child(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    parents = models.ManyToManyField(UserProfile, related_name='children', blank=True)
    attendance_status = models.CharField(max_length=20, default='Present')
    date_added = models.DateTimeField(auto_now_add=True)
    
    # New fields to replace localStorage data
    dob = models.DateField(null=True, blank=True)
    doe = models.DateField(null=True, blank=True)
    allergies = models.CharField(max_length=255, null=True, blank=True)
    mother_name = models.CharField(max_length=100, null=True, blank=True)
    father_name = models.CharField(max_length=100, null=True, blank=True)
    other_guardian_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    img = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class AttendanceRecord(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=20) # 'present', 'absent', 'late'
    dropoff_time = models.CharField(max_length=50, blank=True, null=True)
    pickup_status = models.CharField(max_length=50, blank=True, null=True)
    authorized_guardian = models.CharField(max_length=100, blank=True, null=True)
    session = models.CharField(max_length=50, blank=True, null=True)

class MilestoneRecord(models.Model):
    child = models.OneToOneField(Child, on_delete=models.CASCADE, related_name='milestone_record')
    tasks = models.JSONField(default=dict)

class BehaviorRecord(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='behavior_records')
    date = models.DateField()
    behavior_type = models.CharField(max_length=20) # 'positive', 'negative', 'neutral'
    note = models.TextField()

class NutritionRecord(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='nutrition_records')
    date = models.DateField()
    breakfast = models.BooleanField(default=False)
    snack1 = models.BooleanField(default=False)
    lunch = models.BooleanField(default=False)
    snack2 = models.BooleanField(default=False)