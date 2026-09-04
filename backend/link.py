import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.core.models import Child, UserProfile
from django.contrib.auth.models import User

def link(child_first, parent_usernames):
    child = Child.objects.get(first_name=child_first)
    for un in parent_usernames:
        u = User.objects.get(username=un)
        child.parents.add(u.userprofile)

link('Lyra', ['Jastine', 'Jake'])
link('Khianna Rose', ['Japhet', 'Fhaye'])
link('Leona Grace', ['Ginalyn', 'Jobart'])

print([(c.first_name, [p.user.username for p in c.parents.all()]) for c in Child.objects.all()])