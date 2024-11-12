from django.shortcuts import render, redirect, get_object_or_404
from .forms import InstructorRegistrationForm
from django.contrib.auth import login
from .models import Instructor
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course
from .forms import CourseForm 
from django.core.paginator import Paginator

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

@login_required
def instructor_course_list(request):
    # Only show courses created by the logged-in instructor
    courses = Course.objects.filter(created_by=request.user)

    # Set up pagination
    paginator = Paginator(courses, 6)  # Show 6 courses per page
    page_number = request.GET.get('page')  # Get the page number from the query parameters
    page_obj = paginator.get_page(page_number)  # Get the courses for the current page

    return render(request, 'mentors/course_list.html', {'page_obj': page_obj})

@login_required
def instructor_course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.created_by = request.user  # Set the instructor as the creator
            course.save()
            return redirect('instructor_course_list')
    else:
        form = CourseForm()
    return render(request, 'mentors/course_form.html', {'form': form})

@login_required
def instructor_course_update(request, course_id):
    course = get_object_or_404(Course, id=course_id, created_by=request.user)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('instructor_course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'mentors/course_form.html', {'form': form})

@login_required
def instructor_course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id, created_by=request.user)
    if request.method == 'POST':
        course.delete()
        return redirect('instructor_course_list')
    return render(request, 'mentors/course_confirm_delete.html', {'course': course})