from decimal import Decimal
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from student.models import Enrollment
from student.models import WalletTransaction
from django.db.models import Sum  # for aggregation (total earnings/withdrawn)
from .models import Instructor, Course, Module, Content
from .models import Instructor
from .forms import InstructorRegistrationForm, UserEditForm, InstructorEditForm, InstructorPasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db.models import Count
from .forms import InstructorWithdrawalForm
from .models import InstructorWithdrawalRequest



from .forms import (
    InstructorRegistrationForm,
    CourseForm,
    ModuleForm,
    InstructorContactForm,
)



# -----------------------------
# Authentication & Registration
# -----------------------------
def register_instructor(request):
    if request.method == 'POST':
        form = InstructorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Require admin approval
            user.save()

            Instructor.objects.create(user=user)
            form.save_m2m()

            messages.success(
                request,
                'Registration successful! Your account will be reviewed and approved by an admin.'
            )
            return redirect('login')
    else:
        form = InstructorRegistrationForm()

    return render(request, 'mentors/register_instructor.html', {'form': form})


@login_required
def tutor_edit_profile(request):
    instructor = get_object_or_404(Instructor, user=request.user)
    user = request.user

    if request.method == "POST":
        user_form = UserEditForm(request.POST, instance=user)
        instructor_form = InstructorEditForm(request.POST, request.FILES, instance=instructor)

        if user_form.is_valid() and instructor_form.is_valid():
            user_form.save()
            instructor_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('tutor_edit_profile')  # or another profile page
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserEditForm(instance=user)
        instructor_form = InstructorEditForm(instance=instructor)

    context = {
        'user_form': user_form,
        'instructor_form': instructor_form,
        'instructor': instructor,
    }
    return render(request, 'mentors/edit_profile.html', context)


@login_required
def tutor_change_password(request):
    if request.method == 'POST':
        form = InstructorPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps the user logged in after password change
            messages.success(request, "Your password was successfully updated!")
            return redirect('change_password')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = InstructorPasswordChangeForm(user=request.user)
    
    return render(request, 'mentors/change_password.html', {'form': form})

@login_required
def instructor_home(request):
    if not request.user.is_active:
        return redirect('instructor_pending_dashboard')
    return redirect('instructor_dashboard')


# -----------------------------
# Dashboard & Transactions
# -----------------------------
# @login_required
# def instructor_dashboard(request):
#     instructor = Instructor.objects.get(user=request.user)

#     # Count active courses
#     active_courses_count = Course.objects.filter(instructor=instructor, is_active=True).count()

#     # Count distinct students who purchased any course of this instructor
#     students_count = Enrollment.objects.filter(course__instructor=instructor).values('student').distinct().count()

#     context = {
#         'account_balance': instructor.account_balance,
#         'total_earnings': instructor.earnings,
#         'total_withdrawn': instructor.withdrawn,
#         'active_courses_count': active_courses_count,
#         'students_count': students_count,
#     }

#     return render(request, 'mentors/instructor_dashboard.html', context)


@login_required
def instructor_dashboard(request):
    instructor = Instructor.objects.get(user=request.user)

    active_courses_count = instructor.courses.filter(is_active=True).count()

    # Total unique students across all courses
    students_count = Enrollment.objects.filter(course__instructor=instructor).values('student').distinct().count()

    # Last 5 courses with student count
    recent_courses = instructor.courses.annotate(
        students_count=Count('enrollment')  # use the correct related_name
    ).order_by('-created_at')[:5]

    context = {
        'active_courses_count': active_courses_count,
        'students_count': students_count,          # total unique students
        'account_balance': instructor.account_balance,
        'total_earnings': instructor.earnings,
        'total_withdrawn': instructor.withdrawn,
        'recent_courses': recent_courses,          # each course has .students_count
    }

    return render(request, 'mentors/instructor_dashboard.html', context)




@login_required
def instructor_earnings(request):
    instructor = get_object_or_404(Instructor, user=request.user)

    # Fetch all transactions for this instructor
    transactions = WalletTransaction.objects.filter(
        instructor=instructor
    ).order_by('-created_at')

    context = {
        "instructor": instructor,
        "transactions": transactions,
        "account_balance": instructor.account_balance,   # from Instructor model
        "total_earnings": instructor.earnings,          # from Instructor model
        "total_withdrawn": instructor.withdrawn,        # from Instructor model
    }
    return render(request, "mentors/instructor_earnings.html", context)


# @login_required
# def instructor_earnings(request):
#     instructor = get_object_or_404(Instructor, user=request.user)

#     # Fetch transactions for this instructor
#     transactions = WalletTransaction.objects.filter(
#         instructor=instructor
#     ).order_by('-created_at')

#     # Total earnings from student payments
#     total_earnings = transactions.filter(
#         transaction_type="student_payment"
#     ).aggregate(total=Sum("amount"))["total"] or 0

#     # Total withdrawn (payouts)
#     total_withdrawn = transactions.filter(
#         transaction_type="instructor_payout"
#     ).aggregate(total=Sum("amount"))["total"] or 0

#     # Current account balance = earnings - withdrawn
#     account_balance = total_earnings - total_withdrawn

#     context = {
#         "instructor": instructor,
#         "transactions": transactions,
#         "account_balance": account_balance,
#         "total_earnings": total_earnings,
#         "total_withdrawn": total_withdrawn,
#     }
#     return render(request, "mentors/instructor_earnings.html", context)




@login_required
def instructor_transactions(request):
    instructor = request.user.instructor  # or however you get the instructor object

    # Get all transactions of students who belong to this instructor
    transactions = WalletTransaction.objects.filter(
        student__instructor=instructor
    ).order_by('-created_at')  # use the new field

    context = {
        'transactions': transactions
    }

    return render(request, 'mentors/instructor_transactions.html', context)


@login_required
def instructor_withdraw(request):
    instructor = Instructor.objects.get(user=request.user)

    if request.method == 'POST':
        form = InstructorWithdrawalForm(request.POST)
        if form.is_valid():
            withdrawal = form.save(commit=False)
            withdrawal.instructor = instructor

            if withdrawal.source_account == 'account_balance':
                if withdrawal.amount > instructor.account_balance:
                    messages.error(request, "You cannot withdraw more than your Account Balance.")
                    return redirect('instructor_withdraw')
            else:  # from earnings
                if withdrawal.amount > instructor.earnings:
                    messages.error(request, "You cannot withdraw more than your Earnings.")
                    return redirect('instructor_withdraw')

            withdrawal.save()
            messages.success(request, "Withdrawal request sent. Waiting for admin approval.")
            return redirect('instructor_withdraw')
    else:
        form = InstructorWithdrawalForm()

    past_requests = instructor.withdrawal_requests.order_by('-requested_at')[:5]

    return render(request, 'mentors/withdraw.html', {
        'form': form,
        'past_requests': past_requests,
        'account_balance': instructor.account_balance,
        'earnings': instructor.earnings,
    })




def allow_any_logged_in_user(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:  # even inactive users
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return _wrapped_view


def instructor_pending_dashboard(request):
    form = InstructorContactForm()

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
                email = EmailMessage(
                    subject=f"Message from Pending Instructor: {subject}",
                    body=full_message,
                    from_email=sender_email,
                    to=['cyrilnnamsi@gmail.com'],
                    reply_to=[sender_email],
                )
                email.send(fail_silently=False)
                messages.success(request, 'Your message has been sent to the admin.')
                return redirect('instructor_pending_dashboard')
            except Exception as e:
                messages.error(request, f"Error sending message: {e}")

    return render(request, 'my_app/pending_dashboard.html', {'form': form})


# -----------------------------
# Courses & Modules
# -----------------------------
@login_required
def instructor_course_list(request):
    courses = Course.objects.filter(created_by=request.user)
    paginator = Paginator(courses, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'mentors/course_list.html', {'page_obj': page_obj})


@login_required
def instructor_course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)

            try:
                instructor = Instructor.objects.get(user=request.user)
                course.instructor = instructor
            except Instructor.DoesNotExist:
                course.instructor = None

            course.created_by = request.user
            course.is_active = False
            course.is_published = False
            course.save()
            return redirect('instructor_course_list')
    else:
        form = CourseForm()
    return render(request, 'mentors/course_form.html', {'form': form})


@login_required
def instructor_course_update(request, course_id):
    course = get_object_or_404(Course, id=course_id, created_by=request.user)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            course = form.save(commit=False)
            course.is_active = False
            course.is_published = False
            course.save()
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
    return render(request, 'mentors/course_detail.html', {'course': course, 'modules': modules})


# -----------------------------
# Modules
# -----------------------------
@login_required
def add_module(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            return redirect('instructor_course_detail', course_id=course.id)
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
            return redirect('instructor_course_detail', course_id=module.course.id)
    else:
        form = ModuleForm(instance=module)
    return render(request, 'mentors/edit_module.html', {'form': form, 'module': module})


@login_required
def delete_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        course_id = module.course.id
        module.delete()
        messages.success(request, 'Module deleted successfully.')
        return redirect('instructor_course_detail', course_id=course_id)
    return render(request, 'mentors/delete_module.html', {'module': module})


# -----------------------------
# Content
# -----------------------------
@login_required
def create_content(request, module_id):
    module = get_object_or_404(Module, id=module_id)

    if request.method == 'POST':
        topic = request.POST.get('topic')
        content_type = request.POST.get('content_type')
        content_data_text = request.POST.get('content_data_text')
        content_data_video = request.FILES.get('content_data_video')
        content_data_document = request.FILES.get('content_data_document')

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

        content.topic = topic
        content.content_type = content_type

        if content_type == 'text':
            content.content_data_text = content_data_text
            content.content_data_video = None
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
        return redirect('mentor_content_view')

    return render(request, 'mentors/edit_content.html', {'content': content})


@login_required
def delete_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    if request.method == 'POST':
        content.delete()
        return redirect('mentor_content_view')
    return render(request, 'mentors/delete_content.html', {'content': content})


@login_required
def content_list(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    contents = module.contents.all()
    return render(request, 'mentors/content_list.html', {'module': module, 'contents': contents})


@login_required
def content_detail(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    return render(request, 'mentors/content_detail.html', {'content': content})


# -----------------------------
# Transactions & Withdrawals
# -----------------------------
def handle_course_purchase(student, course_id):
    """Called when a student buys a course"""
    course = Course.objects.get(id=course_id)
    instructor = course.instructor

    course_price = course.price
    platform_percentage = Decimal('20.00')
    instructor_earning = course_price * (Decimal('100.00') - platform_percentage) / Decimal('100.00')

    instructor.earnings += instructor_earning
    instructor.save()

    # Log instructor transaction
    WalletTransaction.objects.create(
        user=instructor.user,
        amount=instructor_earning,
        transaction_type='credit',
        description=f"Earnings from course purchase: {course.title}",
    )


@login_required
def request_withdrawal(request):
    instructor = request.user.instructor

    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))
        if amount > instructor.account_balance:
            messages.error(request, "Insufficient balance.")
        else:
            instructor.withdrawn += amount
            instructor.save()

            # Log withdrawal
            WalletTransaction.objects.create(
                user=request.user,
                amount=amount,
                transaction_type='debit',
                description="Instructor withdrawal",
            )

            messages.success(request, f"Withdrawal of ${amount} successful.")

    return redirect('instructor_dashboard')
