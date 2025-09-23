from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Instructor, Module
from .models import Course
from django.contrib.auth.forms import PasswordChangeForm
from .models import InstructorWithdrawalRequest





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
        user.email = self.cleaned_data.get('email')
        user.is_active = True
        if commit:
            user.save()
            Instructor.objects.create(
                user=user,
                department=self.cleaned_data.get('department'),
                expertise=self.cleaned_data.get('expertise'),
                phone=self.cleaned_data.get('phone')
            )
        return user


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add bootstrap classes
        for name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')


class InstructorEditForm(forms.ModelForm):
    class Meta:
        model = Instructor
        fields = ['department', 'expertise', 'phone', 'bio', 'profile_picture']
        widgets = {
            'expertise': forms.Textarea(attrs={'rows': 4}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add bootstrap classes except for file input (file input has its own class)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs.setdefault('class', 'form-control form-control-file')
            else:
                field.widget.attrs.setdefault('class', 'form-control')


class InstructorPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter current password"})
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter new password"})
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm new password"})
    )



# Course creation for instructors
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description', 'duration', 'credits', 'category', 'level', 'syllabus', 'price', 'is_active', 'language', 'image', 'video']

        widgets = {
            
           'name': forms.TextInput(attrs={
               'class': 'form-control rounded-2 px-3',
               'placeholder': 'Enter course name'
           }),
           'description': forms.Textarea(attrs={
               'class': 'form-control rounded-2 px-3',
               'placeholder': 'Enter course description',
               'style': 'height: 150px;'
           }),
           'duration': forms.TextInput(attrs={
               'class': 'form-control rounded-2 px-3',
               'placeholder': 'Enter course duration'
           }),
           'credits': forms.TextInput(attrs={
               'class': 'form-control rounded-2 px-3',
               'placeholder': 'Enter course credits'
           }),
           'category': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Choose course category'
            }),
            'level': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Choose course level'
            }),
            'price': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter course price'
            }),
            'language': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Choose Language'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'type' : 'file',
                'onchange': 'uploadPhoto()', 
                'accept' : 'image/*',
                'id' : 'fileInput',
            }),
            'video': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'type' : 'file',
                'onchange': 'uploadVideo()', 
                'accept' : 'video/*',
                'id' : 'fileInputv',
            }),
        }

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = [ 'title', 'description']
        widgets = {
            
           'title': forms.TextInput(attrs={
               'class': 'form-control rounded-2 px-3',
               'placeholder': 'Enter module name'
           }),
           'description': forms.Textarea(attrs={
               'class': 'form-control rounded-2 px-3',
               'placeholder': 'Enter course description',
               'style': 'height: 150px;'
           }),
        }

class InstructorContactForm(forms.Form):
    subject = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your message here...', 'rows': 5})
    )



class InstructorWithdrawalForm(forms.ModelForm):
    class Meta:
        model = InstructorWithdrawalRequest
        fields = ['amount', 'source_account']
        widgets = {
            'source_account': forms.RadioSelect
        }
