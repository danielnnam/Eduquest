from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from .forms import InstructorContactForm
from django.core.mail import send_mail
from instructors.models import Course
from django.core.paginator import Paginator
from administration.models import BlogPost
from django.shortcuts import render, get_object_or_404



# Create your views here.

def index(request):
    # Get the latest 3 courses
    latest_courses = Course.objects.order_by('-created_at')[:3]  
    return render(request, 'my_app/index.html', {
        'latest_courses': latest_courses
    })



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

                elif hasattr(user, 'instructor'):
                    if user.is_active:
                        return redirect('instructor_dashboard')  # ✅ active instructor
                    else:
                        return redirect('instructor_pending_dashboard')  # ⛔️ still pending

                elif user.is_staff:
                    return redirect('admin')
                else:
                    messages.error(request, 'User type not recognized.')

            else:
                messages.error(request, 'Invalid credentials')
    else:
        form = LoginForm()

    return render(request, 'my_app/login.html', {'form': form})



def allow_any_logged_in_user(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:  # allows even inactive users
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return _wrapped_view

@allow_any_logged_in_user
def instructor_pending_dashboard(request):
    if request.method == 'POST':
        form = InstructorContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            sender_name = request.user.get_full_name() or request.user.username
            sender_email = request.user.email

            full_message = f"""
You have received a new message from a pending instructor.

From:
Name: {sender_name}
Email: {sender_email}

Subject: {subject}

Message:
{message}
            """

            try:
                send_mail(
                    subject=f"Message from Pending Instructor: {subject}",
                    message=full_message,
                    from_email={sender_email},
                    recipient_list=['cyrilnnamsi@gmail.com'],
                    fail_silently=False,
                    reply_to=[sender_email],  # So admin can reply directly
                )
                messages.success(request, 'Your message has been sent to the admin.')
                return redirect('instructor_pending_dashboard')
            except Exception as e:
                messages.error(request, f"Error sending message: {e}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = InstructorContactForm()

    return render(request, 'my_app/pending_dashboard.html', {'form': form})


def courses_list(request):
    category = request.GET.get('category', None)  # get category from query string
    page_number = request.GET.get('page', 1)      # current page from query string

    if category:
        courses = Course.objects.filter(category=category).order_by('-created_at')
    else:
        courses = Course.objects.all().order_by('-created_at')

    # Add pagination (6 per page, you can change the number)
    paginator = Paginator(courses, 6)
    page_obj = paginator.get_page(page_number)

    categories = [choice[0] for choice in Course.COURSE_CATEGORIES]  # list of categories

    return render(request, 'my_app/courses.html', {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category
    })


def about(request):
    return render(request, 'my_app/about.html')

def contact(request):
    return render(request, 'my_app/contact.html')


def blog(request):
    post_list = BlogPost.objects.all().order_by("-created_at")
    paginator = Paginator(post_list, 6)  # 6 posts per page
    page_number = request.GET.get("page")
    posts = paginator.get_page(page_number)
    return render(request, "my_app/blog.html", {"posts": posts})


def blog_details(request, pk):
    blog = get_object_or_404(BlogPost, pk=pk)
    return render(request, "my_app/blog_detail.html", {"blog": blog})