from django.shortcuts import render, redirect, get_object_or_404
from .forms import InstructorRegistrationForm, ModuleForm
from django.contrib.auth import login
from .models import Content, Instructor, Module
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
        form = CourseForm(request.POST, request.FILES)
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

@login_required
def instructor_course_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    modules = course.modules.all()
    # quizzes = course.quizzes.all()
    # modules = CourseModule.objects.filter(course=course)
    return render(request, 'mentors/course_detail.html', {'course': course, 'modules': modules})


@login_required
def add_module(request, course_id):
    course = get_object_or_404(Course, id=course_id)  # Get the course object
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)  # Don't save to the database yet
            module.course = course  # Set the course
            module.save()  # Now save it
            return redirect('instructor_course_detail', course_id=course.id)  # Redirect to course detail
    else:
        form = ModuleForm()
    return render(request, 'mentors/add_module.html', {'form': form, 'course': course})

@login_required
def edit_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)

    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            course_id = module.course.id  # Get the course ID associated with the module
            return redirect('instructor_course_detail', course_id=course_id)  # Redirect to the course detail page
    else:
        form = ModuleForm(instance=module)

    return render(request, 'mentors/edit_module.html', {'form': form, 'module': module})
@login_required
def delete_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)

    if request.method == 'POST':
        course_id = module.course.id  # Assuming the Module model has a foreign key to Course
        module.delete()
        messages.success(request, 'Module deleted successfully.')
        return redirect('instructor_course_detail', course_id=course_id)  # Redirect to the course detail page

    # If the request method is not POST, you can render a confirmation page if needed
    return render(request, 'mentors/delete_module.html', {'module': module})


@login_required
def create_content(request, module_id):
    module = get_object_or_404(Module, id=module_id)

    if request.method == 'POST':
        topic = request.POST.get('topic')
        content_type = request.POST.get('content_type')
        content_data_text = request.POST.get('content_data_text')
        content_data_video = request.FILES.get('content_data_video')
        content_data_document = request.FILES.get('content_data_document')

        # Create the content object based on the selected type
        content = Content(module=module, content_type=content_type, topic=topic)
        

        if content_type == 'text':
            content.content_data_text = content_data_text
        elif content_type == 'video':
            content.content_data_video = content_data_video
        elif content_type == 'document':
            content.content_data_document = content_data_document

        content.save()
        messages.success(request, 'Content submitted for approval.')
        return redirect('content_list', module_id=module.id)

    return render(request, 'mentors/add_content.html', {'module': module})


@login_required
def edit_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)

    if request.method == 'POST':
        topic = request.POST.get('topic')
        content_type = request.POST.get('content_type')
        content_data_text = request.POST.get('content_data_text')
        content_data_video = request.FILES.get('content_data_video')
        content_data_document = request.FILES.get('content_data_document')

        # Update the content object based on the selected type
        content.topic = topic
        content.content_type = content_type

        if content_type == 'text':
            content.content_data_text = content_data_text
            content.content_data_video = None  # Clear other fields if not used
            content.content_data_document = None
        elif content_type == 'video':
            content.content_data_video = content_data_video
            content.content_data_text = None
            content.content_data_document = None
        elif content_type == 'document':
            content.content_data_document = content_data_document
            content.content_data_text = None
            content.content_data_video = None

        content.save()
        messages.success(request, 'Content updated successfully.')
        return redirect('mentor_content_view')  # Redirect to the mentor content view or another appropriate page

    return render(request, 'mentors/edit_content.html', {'content': content})


@login_required
def delete_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)

    if request.method == 'POST':
        content.delete()
        return redirect('mentor_content_view')  # Redirect to the mentor content view or another appropriate page

    return render(request, 'mentors/delete_content.html', {'content': content})

@login_required
def content_list(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    # Fetch all contents related to the selected module
    contents = module.contents.all()  # Get all contents for the module
    return render(request, 'mentors/content_list.html', {'module': module, 'contents': contents})


@login_required
def content_detail(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    return render(request, 'mentors/content_detail.html', {'content': content})