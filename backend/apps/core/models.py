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
    parent = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='children', null=True, blank=True)
    attendance_status = models.CharField(max_length=20, default='Present')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"