# from django.shortcuts import get_object_or_404, redirect, render
# from django.http import HttpResponse, JsonResponse
# from django.views import View
# from .models import BlogPost, User, Course
# from django.utils import timezone
# from datetime import timedelta
# from student.models import Student, Wallet, Transaction, WalletTransaction
# from .forms import EditBalanceForm
# from django.contrib.auth.decorators import login_required 
# from django.contrib.admin.views.decorators import staff_member_required 
# from django.contrib.auth.decorators import user_passes_test
# from django.contrib import messages
# from django.urls import reverse
# from instructors.models import Course
# from instructors.models import Instructor
# from student.models import Enrollment 
# from django.db.models.functions import TruncDate

# from django.db.models import Count
# from django.utils import timezone
# from django.utils.timezone import now, timedelta
# from instructors.models import Instructor
# from instructors.models import Course
# from django.contrib.auth.models import User
# from django.db.models.functions import TruncDate
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render, redirect
# from .forms import BlogPostForm
# from django.core.paginator import Paginator
# from django.db.models import Sum
# from decimal import Decimal
# from django.contrib.auth import logout


# # Create your views here.

# def admin_dashboard(request):
#     return render(request, 'admins/dashboard.html')


# @login_required
# def admin(request):
#     # ====== Overview Statistics ======
#     total_instructors = Instructor.objects.count()
#     active_instructors = Instructor.objects.filter(user__is_active=True).count()
#     pending_instructors = Instructor.objects.filter(user__is_active=False).count()
#     total_courses = Course.objects.count()
#     total_students = Student.objects.count()

#     # ====== Platform Revenue (already net earnings stored) ======
#     platform_revenue = WalletTransaction.objects.filter(
#     transaction_type='credit',
#     instructor__isnull=True  # exclude instructor payouts
#     ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

#     # ====== Weekly Trends ======
#     one_week_ago = now() - timedelta(days=7)

#     instructor_trend = (
#         User.objects.filter(instructor__isnull=False, date_joined__gte=one_week_ago)
#         .annotate(day=TruncDate('date_joined'))
#         .values('day')
#         .annotate(count=Count('id'))
#         .order_by('day')
#     )

#     course_trend = (
#         Course.objects.filter(created_at__gte=one_week_ago)
#         .annotate(day=TruncDate('created_at'))
#         .values('day')
#         .annotate(count=Count('id'))
#         .order_by('day')
#     )

#     student_trend = (
#         User.objects.filter(student__isnull=False, date_joined__gte=one_week_ago)
#         .annotate(day=TruncDate('date_joined'))
#         .values('day')
#         .annotate(count=Count('id'))
#         .order_by('day')
#     )

#     # ====== Recent Activity ======
#     latest_instructors = Instructor.objects.select_related('user').order_by('-user__date_joined')[:5]
#     recent_courses = Course.objects.select_related('instructor').order_by('-created_at')[:5]

#     # ====== Context for Template ======
#     context = {
#         'total_instructors': total_instructors,
#         'active_instructors': active_instructors,
#         'pending_instructors': pending_instructors,
#         'total_courses': total_courses,
#         'total_students': total_students,
#         'platform_revenue': platform_revenue,  # direct value
#         'instructor_trend': list(instructor_trend),
#         'course_trend': list(course_trend),
#         'student_trend': [
#             {'day': str(item['day']), 'count': item['count']} for item in student_trend
#         ],
#         'latest_instructors': latest_instructors,
#         'recent_courses': recent_courses,
#     }

#     return render(request, 'admins/index.html', context)

# @staff_member_required
# def admin_course_list(request):
#     courses = Course.objects.all().order_by('-created_at')
#     return render(request, 'admins/course_list.html', {'courses': courses})

# def dashboard_data(request):
#     # ----- Courses by Category -----
#     categories = dict(Course.COURSE_CATEGORIES)  # Convert choices to a dictionary
#     category_counts = {category: 0 for category in categories.keys()}

#     for course in Course.objects.all():
#         category_counts[course.category] += 1

#     labels = list(category_counts.keys())
#     counts = list(category_counts.values())

#     total_courses = Course.objects.count()
#     others_count = total_courses - sum(counts)
#     if others_count > 0:
#         labels.append('Others')
#         counts.append(others_count)

#     # ----- Instructor Stats -----
#     total_instructors = Instructor.objects.count()
#     active_instructors = Instructor.objects.filter(user__is_active=True).count()
#     pending_instructors = Instructor.objects.filter(user__is_active=False).count()

#     data = {
#         'labels': labels,
#         'counts': counts,
#         'instructor_stats': {
#             'total': total_instructors,
#             'active': active_instructors,
#             'pending': pending_instructors
#         }
#     }

#     return JsonResponse(data)


# @login_required
# def admin_students(request):
#     students = Student.objects.all()
#     student_data = []
#     for student in students:
#         wallet, created = Wallet.objects.get_or_create(student=student)
#         student_data.append({
#             'student': student,
#             'balance': wallet.balance
#         })
#     return render(request, 'admins/students.html', {'students': student_data})


# @login_required
# def edit_wallet_balance(request, student_id):
#     if request.method == 'POST':
#         new_balance = request.POST.get('new_balance')
#         try:
#             wallet = Wallet.objects.get(student__id=student_id)
#             old_balance = wallet.balance
#             new_balance = Decimal(new_balance)

#             # Calculate the difference
#             difference = new_balance - old_balance

#             if difference > 0:
#                 # Admin added funds → Credit
#                 WalletTransaction.objects.create(
#                     student=wallet.student.user,
#                     amount=difference,
#                     transaction_type='credit',
#                     description=f"Admin credited {difference} to wallet"
#                 )
#             elif difference < 0:
#                 # Admin removed funds → Debit
#                 WalletTransaction.objects.create(
#                     student=wallet.student.user,
#                     amount=abs(difference),
#                     transaction_type='debit',
#                     description=f"Admin debited {abs(difference)} from wallet"
#                 )

#             # Update balance
#             wallet.balance = new_balance
#             wallet.save()

#             return HttpResponse(f"Balance updated! New balance: ${wallet.balance}")

#         except Wallet.DoesNotExist:
#             return HttpResponse("Error: Wallet not found.", status=404)
#         except Exception as e:
#             return HttpResponse(f"Error: {str(e)}", status=500)

#     return HttpResponse("Error: Invalid request method.", status=400)

# @login_required
# def edit_student(request, student_id):
#     # Fetch the student object or return a 404 if it doesn't exist
#     student = get_object_or_404(Student, id=student_id)

#     if request.method == 'POST':
#         # Update student details from the submitted form data
#         student.first_name = request.POST.get('first_name')
#         student.last_name = request.POST.get('last_name')
#         student.email = request.POST.get('email')
#         student.save()  # Save the changes to the database

#         messages.success(request, "Student details updated successfully!")
#         return redirect(reverse('edit_student', kwargs={'student_id': student_id}))

#     return render(request, 'admins/student_edit.html', {'student': student})

# # pending courses
# @staff_member_required
# def pending_courses(request):
#     pending = Course.objects.filter(is_active=False).order_by('-created_at')
#     return render(request, 'admins/pending_courses.html', {'pending_courses': pending})


# @staff_member_required
# def approve_course(request, course_id):
#     course = get_object_or_404(Course, id=course_id)
#     course.is_active = True
#     course.is_published = True
#     course.save()
#     return redirect('pending_courses')  # after approval, redirect back

# # instructors list
# @staff_member_required
# def instructor_list(request):
#     instructors = Instructor.objects.all().select_related('user')  # or .filter(is_active=True)

#     active_instructors = instructors.filter(user__is_active=True).count()
#     pending_instructors = instructors.filter(user__is_active=False).count()
#     total_courses = Course.objects.count()

#     context = {
#         'active_instructors': active_instructors,
#         'pending_instructors': pending_instructors,
#         'total_courses': total_courses,
#         'instructors': instructors
#     }
#     return render(request, 'admins/instructor_list.html', context)


# @staff_member_required
# def instructor_detail(request, instructor_id):
#     instructor = get_object_or_404(Instructor, id=instructor_id)
#     courses = Course.objects.filter(instructor=instructor)

#     return render(request, 'admins/instructor_detail.html', {
#         'instructor': instructor,
#         'courses': courses
#     })

# @user_passes_test(lambda u: u.is_staff)
# def toggle_instructor_status(request, instructor_id):
#     instructor = get_object_or_404(Instructor, id=instructor_id)
#     user = instructor.user
#     user.is_active = not user.is_active
#     user.save()
#     return redirect('admin_instructor_list')

# def approve_instructor(request, instructor_id):
#     instructor = get_object_or_404(Instructor, id=instructor_id)
#     user = instructor.user
#     user.is_active = True
#     user.save()
#     return redirect('admin_instructor_list')


# def is_admin(user):
#     return user.is_staff

# @login_required
# @user_passes_test(is_admin)
# def create_blog_post(request):
#     if request.method == "POST":
#         form = BlogPostForm(request.POST, request.FILES)
#         if form.is_valid():
#             blog_post = form.save(commit=False)
#             blog_post.author = request.user  # if BlogPost has author field
#             blog_post.save()
#             return redirect("admin_dashboard")  # redirect back to dashboard
#     else:
#         form = BlogPostForm()

#     return render(request, "admins/create_blog.html", {"form": form})

# @login_required
# def blog_list(request):
#     blogs = BlogPost.objects.all().order_by('-created_at')  # latest first
#     return render(request, 'admins/blog_list.html', {'blogs': blogs})

# @login_required
# def blog_detail(request, pk):
#     blog = get_object_or_404(BlogPost, pk=pk)
#     return render(request, 'admins/blog_details.html', {'blog': blog})


# @login_required
# @user_passes_test(is_admin)
# def edit_blog_post(request, pk):
#     blog = get_object_or_404(BlogPost, pk=pk)
#     if request.method == "POST":
#         form = BlogPostForm(request.POST, request.FILES, instance=blog)
#         if form.is_valid():
#             form.save()
#             return redirect("blog_detail", pk=blog.pk)
#     else:
#         form = BlogPostForm(instance=blog)

#     return render(request, "admins/edit_blog.html", {"form": form, "blog": blog})


# @login_required
# @user_passes_test(is_admin)
# def delete_blog_post(request, pk):
#     blog = get_object_or_404(BlogPost, pk=pk)
#     blog.delete()
#     return redirect("blog_list")



# @login_required
# def transactions(request):
#     transactions = WalletTransaction.objects.select_related('student', 'instructor', 'course').order_by('-created_at')

#     # Filters (if any query params are passed)
#     transaction_type = request.GET.get('type')
#     if transaction_type in ['credit', 'debit']:
#         transactions = transactions.filter(transaction_type=transaction_type)

#     student = request.GET.get('student')
#     if student:
#         transactions = transactions.filter(student__username__icontains=student)

#     instructor = request.GET.get('instructor')
#     if instructor:
#         transactions = transactions.filter(instructor__user__username__icontains=instructor)

#     # Totals
#     total_credits = WalletTransaction.objects.filter(transaction_type='credit').aggregate(total=Sum('amount'))['total'] or 0
#     total_debits = WalletTransaction.objects.filter(transaction_type='debit').aggregate(total=Sum('amount'))['total'] or 0

#     context = {
#         "transactions": transactions,
#         "total_credits": total_credits,
#         "total_debits": total_debits,
#     }
#     return render(request, "admins/transcations.html", context)



# @login_required
# def admin_logout(request):
#     logout(request)
#     return redirect('login')











from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils.timezone import now, timedelta
from decimal import Decimal
from django.contrib.auth import logout

from .models import BlogPost
from .forms import BlogPostForm
from instructors.models import Instructor, Course
from student.models import Student, Wallet, WalletTransaction, Enrollment
from instructors.models import InstructorWithdrawalRequest


# Helper function to check if user is staff
def is_admin(user):
    return user.is_staff


# ------------------- Admin Dashboard -------------------
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'admins/dashboard.html')


@login_required
@user_passes_test(is_admin)
def admin(request):
    # Overview Statistics
    total_instructors = Instructor.objects.count()
    active_instructors = Instructor.objects.filter(user__is_active=True).count()
    pending_instructors = Instructor.objects.filter(user__is_active=False).count()
    total_courses = Course.objects.count()
    total_students = Student.objects.count()

    # Platform Revenue
    platform_revenue = WalletTransaction.objects.filter(
        transaction_type='credit',
        instructor__isnull=True
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    # Weekly Trends
    one_week_ago = now() - timedelta(days=7)
    instructor_trend = (
        Instructor.objects.filter(user__date_joined__gte=one_week_ago)
        .annotate(day=TruncDate('user__date_joined'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    course_trend = (
        Course.objects.filter(created_at__gte=one_week_ago)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    student_trend = (
        Student.objects.filter(user__date_joined__gte=one_week_ago)
        .annotate(day=TruncDate('user__date_joined'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    latest_instructors = Instructor.objects.select_related('user').order_by('-user__date_joined')[:5]
    recent_courses = Course.objects.select_related('instructor').order_by('-created_at')[:5]

    context = {
        'total_instructors': total_instructors,
        'active_instructors': active_instructors,
        'pending_instructors': pending_instructors,
        'total_courses': total_courses,
        'total_students': total_students,
        'platform_revenue': platform_revenue,
        'instructor_trend': list(instructor_trend),
        'course_trend': list(course_trend),
        'student_trend': [{'day': str(item['day']), 'count': item['count']} for item in student_trend],
        'latest_instructors': latest_instructors,
        'recent_courses': recent_courses,
    }

    return render(request, 'admins/index.html', context)


# ------------------- Courses -------------------
@login_required
@user_passes_test(is_admin)
def admin_course_list(request):
    courses = Course.objects.all().order_by('-created_at')
    return render(request, 'admins/course_list.html', {'courses': courses})


@login_required
@user_passes_test(is_admin)
def pending_courses(request):
    pending = Course.objects.filter(is_active=False).order_by('-created_at')
    return render(request, 'admins/pending_courses.html', {'pending_courses': pending})


@login_required
@user_passes_test(is_admin)
def approve_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.is_active = True
    course.is_published = True
    course.save()
    return redirect('pending_courses')


# ------------------- Instructors -------------------
@login_required
@user_passes_test(is_admin)
def instructor_list(request):
    instructors = Instructor.objects.all().select_related('user')
    active_instructors = instructors.filter(user__is_active=True).count()
    pending_instructors = instructors.filter(user__is_active=False).count()
    total_courses = Course.objects.count()

    context = {
        'active_instructors': active_instructors,
        'pending_instructors': pending_instructors,
        'total_courses': total_courses,
        'instructors': instructors
    }
    return render(request, 'admins/instructor_list.html', context)


@login_required
@user_passes_test(is_admin)
def instructor_detail(request, instructor_id):
    instructor = get_object_or_404(Instructor, id=instructor_id)
    courses = Course.objects.filter(instructor=instructor)
    return render(request, 'admins/instructor_detail.html', {'instructor': instructor, 'courses': courses})


@login_required
@user_passes_test(is_admin)
def toggle_instructor_status(request, instructor_id):
    instructor = get_object_or_404(Instructor, id=instructor_id)
    user = instructor.user
    user.is_active = not user.is_active
    user.save()
    return redirect('admin_instructor_list')


@login_required
@user_passes_test(is_admin)
def approve_instructor(request, instructor_id):
    instructor = get_object_or_404(Instructor, id=instructor_id)
    user = instructor.user
    user.is_active = True
    user.save()
    return redirect('admin_instructor_list')


# ------------------- Students & Wallet -------------------
@login_required
@user_passes_test(is_admin)
def admin_students(request):
    students = Student.objects.all()
    student_data = []
    for student in students:
        wallet, _ = Wallet.objects.get_or_create(student=student)
        student_data.append({'student': student, 'balance': wallet.balance})
    return render(request, 'admins/students.html', {'students': student_data})


@login_required
@user_passes_test(is_admin)
def edit_wallet_balance(request, student_id):
    if request.method == 'POST':
        new_balance = request.POST.get('new_balance')
        try:
            wallet = Wallet.objects.get(student__id=student_id)
            old_balance = wallet.balance
            new_balance = Decimal(new_balance)
            difference = new_balance - old_balance

            if difference > 0:
                WalletTransaction.objects.create(
                    student=wallet.student.user,
                    amount=difference,
                    transaction_type='credit',
                    description=f"Admin credited ${difference} to wallet"
                )
            elif difference < 0:
                WalletTransaction.objects.create(
                    student=wallet.student.user,
                    amount=abs(difference),
                    transaction_type='debit',
                    description=f"Admin debited ${abs(difference)} from wallet"
                )

            wallet.balance = new_balance
            wallet.save()
            return HttpResponse(f"Balance updated! New balance: ${wallet.balance}")

        except Wallet.DoesNotExist:
            return HttpResponse("Error: Wallet not found.", status=404)
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)

    return HttpResponse("Error: Invalid request method.", status=400)


@login_required
@user_passes_test(is_admin)
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        student.first_name = request.POST.get('first_name')
        student.last_name = request.POST.get('last_name')
        student.email = request.POST.get('email')
        student.save()
        messages.success(request, "Student details updated successfully!")
        return redirect(reverse('edit_student', kwargs={'student_id': student_id}))
    return render(request, 'admins/student_edit.html', {'student': student})


# ------------------- Blog -------------------
@login_required
@user_passes_test(is_admin)
def create_blog_post(request):
    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.author = request.user
            blog_post.save()
            return redirect("admin_dashboard")
    else:
        form = BlogPostForm()
    return render(request, "admins/create_blog.html", {"form": form})


@login_required
@user_passes_test(is_admin)
def edit_blog_post(request, pk):
    blog = get_object_or_404(BlogPost, pk=pk)
    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            return redirect("blog_detail", pk=blog.pk)
    else:
        form = BlogPostForm(instance=blog)
    return render(request, "admins/edit_blog.html", {"form": form, "blog": blog})


@login_required
@user_passes_test(is_admin)
def delete_blog_post(request, pk):
    blog = get_object_or_404(BlogPost, pk=pk)
    blog.delete()
    return redirect("blog_list")


@login_required
def blog_list(request):
    blogs = BlogPost.objects.all().order_by('-created_at')
    return render(request, 'admins/blog_list.html', {'blogs': blogs})


@login_required 
def blog_detail(request, pk):     
    blog = get_object_or_404(BlogPost, pk=pk)     
    return render(request, 'admins/blog_details.html', {'blog': blog})


# ------------------- Transactions -------------------

@login_required
@user_passes_test(is_admin)
def transactions(request):
    transactions = WalletTransaction.objects.select_related('student', 'instructor', 'course').order_by('-created_at')

    # Filters (if any query params are passed)
    transaction_type = request.GET.get('type')
    if transaction_type in ['credit', 'debit']:
        transactions = transactions.filter(transaction_type=transaction_type)

    student = request.GET.get('student')
    if student:
        transactions = transactions.filter(student__username__icontains=student)

    instructor = request.GET.get('instructor')
    if instructor:
        transactions = transactions.filter(instructor__user__username__icontains=instructor)

    # Totals
    total_credits = WalletTransaction.objects.filter(transaction_type='credit').aggregate(total=Sum('amount'))['total'] or 0
    total_debits = WalletTransaction.objects.filter(transaction_type='debit').aggregate(total=Sum('amount'))['total'] or 0

    context = {
        "transactions": transactions,
        "total_credits": total_credits,
        "total_debits": total_debits,
    }
    return render(request, "admins/transcations.html", context)

# ------------------- Dashboard data -------------------

@login_required
@user_passes_test(is_admin)
def dashboard_data(request):
    # Courses by Category
    categories = dict(Course.COURSE_CATEGORIES)
    category_counts = {category: 0 for category in categories.keys()}

    for course in Course.objects.all():
        category_counts[course.category] += 1

    labels = list(category_counts.keys())
    counts = list(category_counts.values())

    total_courses = Course.objects.count()
    others_count = total_courses - sum(counts)
    if others_count > 0:
        labels.append('Others')
        counts.append(others_count)

    # Instructor Stats
    total_instructors = Instructor.objects.count()
    active_instructors = Instructor.objects.filter(user__is_active=True).count()
    pending_instructors = Instructor.objects.filter(user__is_active=False).count()

    data = {
        'labels': labels,
        'counts': counts,
        'instructor_stats': {
            'total': total_instructors,
            'active': active_instructors,
            'pending': pending_instructors
        }
    }

    return JsonResponse(data)


@login_required
@user_passes_test(is_admin)
def withdrawal_requests_list(request):
    requests = InstructorWithdrawalRequest.objects.order_by('-requested_at')

    if request.method == 'POST':
        action = request.POST.get('action')
        req_id = request.POST.get('request_id')
        req = InstructorWithdrawalRequest.objects.get(id=req_id)

        if action == 'approve':
            if req.source_account == 'account_balance':
                req.instructor.account_balance -= req.amount
            else:  # from earnings
                req.instructor.earnings -= req.amount

            req.instructor.withdrawn += req.amount
            req.instructor.save()
            req.status = 'approved'
            messages.success(request, f"Withdrawal of ${req.amount} from {req.get_source_account_display()} approved.")
        elif action == 'decline':
            req.status = 'declined'
            messages.warning(request, f"Withdrawal of ${req.amount} declined.")

        req.save()
        return redirect('withdrawal_requests_list')

    return render(request, 'admins/withdrawal_requests_list.html', {'requests': requests})


# ------------------- logout -------------------

@login_required
@user_passes_test(is_admin)
def admin_logout(request):
    logout(request)
    return redirect('login')

