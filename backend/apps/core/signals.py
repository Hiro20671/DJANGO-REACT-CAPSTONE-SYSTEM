# signals.py
from django.db.models.signals import post_migrate
from django.contrib.auth.models import User
from .models import UserProfile

def create_teacher_account(sender, **kwargs):
    teacher, created = User.objects.get_or_create(
        username="teacher",
        defaults={"email": "EMAIL_ADDRESS", "is_staff": True, "is_superuser": True}
    )
    if created:
        teacher.set_password("TeacherPassword123")
        teacher.save()
        UserProfile.objects.create(user=teacher, is_teacher=True)

post_migrate.connect(create_teacher_account)