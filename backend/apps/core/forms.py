from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Enrollment, Subject
from .models import UserProfile

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(user=user, is_teacher=False)
        return user

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        self.fields['username'].label = ''
        self.fields['username'].widget.attrs.update({'placeholder': 'Username'})
        self.fields['password1'].label = ''
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password'})
        self.fields['password2'].label = ''
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['full_name', 'course', 'email']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'course': forms.TextInput(attrs={'placeholder': 'Course'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }
class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['subject_code', 'subject_name', 'instructor', 'room', 'department', 'time']

