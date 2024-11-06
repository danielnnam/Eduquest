from django.shortcuts import render, redirect
from .forms import InstructorRegistrationForm
from django.contrib.auth import login
from .models import Instructor
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.

def register_instructor(request):
    if request.method == 'POST':
        form = InstructorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)  # Save the user and instructor
            messages.success(request, 'Registration successful! Your account will be approved by an admin.')
            return redirect('login')  # Redirect to the login page or another success page
    else:
        form = InstructorRegistrationForm()
    return render(request, 'mentors/register_instructor.html', {'form': form})

@login_required
def instructor_dashboard(request):
    return render(request, 'mentors/instructor_dashboard.html')

def not_approved(request):
    return render(request, 'mentors/not_approved.html')