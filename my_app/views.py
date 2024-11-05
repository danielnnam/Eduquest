from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from django.contrib import messages


# Create your views here.

def index(request):
    return render(request, 'my_app/index.html')




# Login View for Students and Teachers
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if hasattr(user, 'student'):
                    return redirect('student_dashboard')
                elif hasattr(user, 'teacher'):
                    return redirect('teacher_dashboard')
                elif user.is_staff:
                    return redirect('admin_dashboard')
            else:
                messages.error(request, 'Invalid credentials')
    else:
        form = LoginForm()
    return render(request, 'my_app/login.html', {'form': form})