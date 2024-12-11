from django.shortcuts import get_object_or_404, render, redirect
from student.models import Cart, CartItem, Course
from django.http import JsonResponse
from student.forms import StudentRegistrationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, update_session_auth_hash
from .forms import PersonalInfoEditForm, UserProfileEditForm
from .models import UserProfile

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
def edit_profile(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        personal_info_form = PersonalInfoEditForm(request.POST, instance=user)
        profile_form = UserProfileEditForm(request.POST, instance=profile)

        if personal_info_form.is_valid() and profile_form.is_valid():
            personal_info_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully.')  # Success message
            return redirect('edit_profile')  # Redirect to the same page to show the message

        else:
            messages.error(request, 'Please correct the errors below.')  # Error message

    else:
        personal_info_form = PersonalInfoEditForm(instance=user)
        profile_form = UserProfileEditForm(instance=profile)

    return render(request, 'students/edit_profile.html', {
        'personal_info_form': personal_info_form,
        'profile_form': profile_form,
    })

@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        # Check if the current password is correct
        if request.user.check_password(current_password):
            if new_password == confirm_new_password:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, 'Your profile has been updated successfully.')  # Success message
                update_session_auth_hash(request, request.user)  # Important!
                return redirect('change_password')  # Redirect to a profile view or success page
            else:
                # error_message = "New passwords do not match."
                messages.success(request, 'New passwords do not match.')  # Success message
        else:
            # error_message = "Current password is incorrect."
            messages.success(request, 'Current password is incorrect.')  # Success message

        

    return render(request, 'students/change_password.html', {
        # 'error_message': error_message,
    })

@login_required
def course_list(request):
    courses = Course.objects.all()  # Get all courses initially


    # Get filter parameters from the request
    skill_level = request.GET.get('skillLevel')
    category = request.GET.get('category')

    # Filter courses based on selected skill level and category
    if category:
        courses = courses.filter(category=category)
    if skill_level:
        courses = courses.filter(level=skill_level)

    return render(request, 'students/course_list.html', {'courses': courses})

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    modules = course.modules.all()  # Get all modules for the course
    content_topics = []  # Initialize an empty list to store content topics
    for module in modules:
        content_topics.extend(module.contents.values_list('topic', flat=True))  # Get all content topics for each module
    return render(request, 'students/course_detail.html', {
        'course': course,
        'content_topics': content_topics,
        'instructor_name': course.instructor.user,
        'instructor_department': course.instructor.department
        })

@login_required
def add_to_cart(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Check if the course is already in the cart
    if not cart.items.filter(course=course).exists():
        CartItem.objects.create(cart=cart, course=course)
        messages.success(request, f"{course.name} has been added to your cart.")
    else:
        messages.info(request, f"You already have {course.name} in your cart.")

    return redirect('view_cart')


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')  # Redirect to user login after logout