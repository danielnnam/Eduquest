from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Instructor, Lesson, Module, Topic
from .models import Course


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

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['module', 'title', 'description']

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['topic', 'title', 'content']