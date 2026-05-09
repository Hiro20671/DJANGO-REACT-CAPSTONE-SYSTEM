from django.contrib.auth.models import User
from apps.core.models import UserProfile, Child

# Find all UserProfiles that are NOT teachers
parent_profiles = UserProfile.objects.filter(is_teacher=False)
parent_users = User.objects.filter(userprofile__in=parent_profiles)

count_users = parent_users.count()
count_children = Child.objects.count()

# Delete children (which cascades to attendance, nutrition, milestones)
Child.objects.all().delete()

# Delete parent users (which cascades to UserProfile)
parent_users.delete()

print(f"Successfully deleted {count_users} Parent Accounts and {count_children} Child records.")
print("The system is now completely fresh for parents and enrollments!")
