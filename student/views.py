from django.shortcuts import render, redirect
from student.forms import StudentRegistrationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

# Create your views here.


def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')  # Redirect to the login page
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'students/register.html', {'form': form})


@login_required
def student_dashboard(request):
    return render(request, 'students/dashboard.html')

@login_required
def course_list(request):
    return render(request, 'students/course_list.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')  # Redirect to user login after logout