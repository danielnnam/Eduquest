from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Instructor


class InstructorRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    department = forms.CharField(max_length=100, required=True)
    expertise = forms.CharField(widget=forms.Textarea, required=True)
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'department', 'expertise', 'phone']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = True  # Set the user as active immediately
        if commit:
            user.save()
            instructor = Instructor(
                user=user,
                department=self.cleaned_data['department'],
                expertise=self.cleaned_data['expertise'],
                phone=self.cleaned_data['phone']
            )
            instructor.save()
        return user