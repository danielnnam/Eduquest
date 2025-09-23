from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Student, User, UserProfile

class StudentRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = Student
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'password_confirm']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")

    def save(self, commit=True):
        user = User(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
        )
        user.set_password(self.cleaned_data['password'])  # Hash the password
        if commit:
            user.save()
            student = super().save(commit=False)
            student.user = user
            if commit:
                student.save()
        return student
    

# Personal Information Edit Form
class PersonalInfoEditForm(forms.ModelForm):
    class Meta:
        model = User  
        fields = [
            'first_name',
            'last_name',
            'email',
            'username',
        ]
        widgets = {
            
           'first_name': forms.TextInput(attrs={
               'class': 'form-control rounded-2 px-3',
               'placeholder': 'Enter First name'
           }),
           'last_name': forms.TextInput(attrs={
               'class': 'form-control rounded-2 px-3',
               'placeholder': 'Last Name'
           }),
           'email': forms.EmailInput(attrs={
               'class': 'form-control rounded-2 px-3',
               'placeholder': 'Enter Last name'
           }),
           'username': forms.TextInput(attrs={
               'class': 'form-control rounded-2 px-3',
               'placeholder': 'Username'
           })
        }

# Password Change Form
class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput, label="Current Password")
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    confirm_new_password = forms.CharField(widget=forms.PasswordInput, label="Confirm New Password")


# UserProfileEditForm
class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone']  # Include 'phone' here
        widgets = {
            
           'phone': forms.TextInput(attrs={
               'class': 'form-control rounded-2 px-3',
               'placeholder': 'Enter phone number'
           })
        }

# StudentAdminForm for admin interface
class StudentAdminForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['user', 'first_name', 'last_name', 'email', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].label = "User  Account"  # Customize label if needed