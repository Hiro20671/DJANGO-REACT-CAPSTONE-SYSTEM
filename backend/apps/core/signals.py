# signals.py
from django.db.models.signals import post_migrate
from django.contrib.auth.models import User

def create_default_accounts(sender, **kwargs):
    if sender.name != 'apps.core':
        return
        
    from .models import UserProfile

    # Seed Default Teacher Account
    teacher, created = User.objects.get_or_create(
        username="teacher",
        defaults={"email": "teacher@example.com", "is_staff": True, "is_superuser": True}
    )
    teacher.set_password("TeacherPassword123")
    teacher.is_staff = True
    teacher.is_superuser = True
    teacher.save()
    
    teacher_profile, _ = UserProfile.objects.get_or_create(user=teacher)
    if not teacher_profile.is_teacher:
        teacher_profile.is_teacher = True
        teacher_profile.save()

    # Seed Default Parent Account
    parent, created = User.objects.get_or_create(
        username="parent",
        defaults={"email": "parent@example.com", "is_staff": False, "is_superuser": False}
    )
    parent.set_password("ParentPassword123")
    parent.save()
    
    parent_profile, _ = UserProfile.objects.get_or_create(user=parent)

post_migrate.connect(create_default_accounts)