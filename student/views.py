from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from student.models import Cart, CartItem, Course, WalletTransaction
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from student.forms import StudentRegistrationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, update_session_auth_hash
from .forms import PersonalInfoEditForm, UserProfileEditForm
from .models import Enrollment, UserProfile
from .models import Wallet, Student 
from instructors.models import Content, StudentProgress
from decimal import Decimal
from django.db import transaction
import uuid
from django.db.models import Sum
from django.contrib.auth.decorators import login_required


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
	# Get the student profile
	student = Student.objects.get(user=request.user)

	# Get the wallet if it exists, else default to 0
	wallet_balance = 0.00
	try:
		wallet = Wallet.objects.get(student=student)
		wallet_balance = wallet.balance
	except Wallet.DoesNotExist:
		pass  # Keep wallet_balance as 0 if no wallet exists yet

	context = {
		'student': student,
		'wallet_balance': wallet_balance,
	}

	return render(request, 'students/dashboard.html', context)

@login_required
def edit_profile(request):
	user = request.user
	profile = UserProfile.objects.get_or_create(user=user)[0]

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
	courses = Course.objects.filter(is_active=True)

	if not Course.is_active and not request.user.is_staff:
		raise Http404("This course is not available.")

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
	cart = Cart.objects.get_or_create(user=request.user)[0]

	# Check if the course is already in the cart
	if not cart.items.filter(course=course).exists():
		CartItem.objects.create(cart=cart, course=course)
		messages.success(request, f"{course.name} has been added to your cart.")
	else:
		messages.info(request, f"You already have {course.name} in your cart.")

	return redirect('view_cart')


@login_required
def view_cart(request):
	cart = get_object_or_404(Cart, user=request.user)
	cart_items = cart.items.all()

	total_amount = sum(item.get_total_price() for item in cart_items)
	print(cart_items)
	context = {
		'cart_items': cart_items,
		'total_amount': total_amount,
	}
	return render(request, 'students/wishlist.html', context)

@login_required
def delete_cart_item(request, item_id):
	cart_item = get_object_or_404(CartItem, id=item_id)

	if cart_item.cart.user != request.user:
		messages.error(request, 'You do not have permission to delete this item.')
		return redirect('view_cart')  # Redirect to the cart view

	if request.method == 'POST':
		cart_item.delete()
		messages.success(request, 'Item Removed successfully.')
		return redirect('view_cart')  # Redirect to the cart view

	return redirect('view_cart')  # Redirect for any other method


from django.contrib import messages
from django.shortcuts import redirect, render

@login_required
def checkout(request):
    user = request.user
    cart = Cart.objects.get(user=user)
    cart_items = cart.items.all()

    # Filter only courses not already purchased
    courses_to_buy = [
        item.course for item in cart_items 
        if not Enrollment.objects.filter(course=item.course, student=user).exists()
    ]

    if request.method == 'POST':

        if not courses_to_buy:
            messages.error(request, "You have already purchased all courses in your cart.")
            return redirect('checkout')  # redirect to same checkout view

        total_amount = sum(item.course.price for item in cart_items if item.course in courses_to_buy)
        wallet = Wallet.objects.get(student__user=user)

        if wallet.balance < total_amount:
            messages.error(request, "Insufficient funds in wallet.")
            return redirect('checkout')  # stay on the same page

        # Generate unique group ID for this checkout session
        group_id = uuid.uuid4()

        with transaction.atomic():
            # Deduct wallet balance
            wallet.balance -= total_amount
            wallet.save()

            # Record student payment (debit)
            WalletTransaction.objects.create(
                student=user,
                amount=total_amount,
                transaction_type='debit',
                description=f'Purchased course(s): {", ".join([c.name for c in courses_to_buy])}',
                transaction_group_id=group_id
            )

            for course in courses_to_buy:
                # Enroll the student
                Enrollment.objects.create(course=course, student=user)

                if course.instructor:
                    instructor = course.instructor
                    instructor_cut = Decimal(course.price) * Decimal('0.70')
                    platform_cut = Decimal(course.price) * Decimal('0.30')

                    # Update instructor earnings
                    instructor.earnings += instructor_cut
                    instructor.save()

                    # Record instructor payout
                    WalletTransaction.objects.create(
                        student=user,
                        instructor=instructor,
                        course=course,
                        amount=instructor_cut,
                        transaction_type='credit',
                        description=f'{instructor.user.username} earned 70% from {course.name}',
                        transaction_group_id=group_id
                    )

                    # Record platform revenue
                    WalletTransaction.objects.create(
                        student=user,
                        course=course,
                        amount=platform_cut,
                        transaction_type='credit',
                        description=f'Platform earned 30% from {course.name}',
                        transaction_group_id=group_id
                    )

            # Remove purchased items from cart
            cart.items.filter(course__in=courses_to_buy).delete()

        messages.success(request, "Purchase successful!")
        return redirect('checkout')  # stay on checkout page

    # GET request: just render checkout page
    return render(request, 'students/wishlist.html', {'cart_items': cart_items})



def success_page(request):
	return render(request, 'students/success.html')


@login_required
def my_courses(request):
    user = request.user

    enrollments = Enrollment.objects.filter(student=user).select_related('course')

    active_courses = []
    completed_courses = []
    total_progress = 0
    course_count = enrollments.count()

    for enrollment in enrollments:
        course = enrollment.course
        total_contents = Content.objects.filter(module__course=course).count()
        completed_contents = StudentProgress.objects.filter(
            user=user, course=course, completed=True
        ).count()

        if total_contents > 0:
            progress_percent = int((completed_contents / total_contents) * 100)
        else:
            progress_percent = 0

        # Store per-course progress
        enrollment.progress = progress_percent
        enrollment.completed = progress_percent == 100

        total_progress += progress_percent

        if enrollment.completed:
            completed_courses.append(enrollment)
        else:
            active_courses.append(enrollment)

    # Calculate overall average progress across all enrolled courses
    if course_count > 0:
        average_progress = int(total_progress / course_count)
    else:
        average_progress = 0

    context = {
        'active_courses': active_courses,
        'completed_courses': completed_courses,
        'enrolled_courses': enrollments,
        'active_course_count': len(active_courses),
        'completed_course_count': len(completed_courses),
        'average_progress': average_progress,  
    }

    return render(request, 'students/my_courses.html', context)




@login_required
def content_view(request, course_id):
	course = get_object_or_404(Course, id=course_id)
	modules = course.modules.all()
	all_contents = list(Content.objects.filter(module__in=modules))

	selected_content = None
	if 'content_id' in request.GET:
		selected_content = get_object_or_404(Content, id=request.GET['content_id'])
	else:
		selected_content = all_contents[0] if all_contents else None

	current_index = all_contents.index(selected_content) if selected_content in all_contents else -1
	previous_content = all_contents[current_index - 1] if current_index > 0 else None
	next_content = all_contents[current_index + 1] if current_index < len(all_contents) - 1 else None

	# Track progress
	progress = StudentProgress.objects.get_or_create(
		user=request.user, course=course, content=selected_content
	)[0]

	if selected_content:
		progress.module = selected_content.module
		progress.content = selected_content  # ✅ Mark content as viewed
		progress.completed = True
		progress.save()

	# Get list of completed content IDs
	completed_content_ids = StudentProgress.objects.filter(
		user=request.user, course=course, completed=True
	).values_list('content_id', flat=True)

	# ✅ Check if all course contents are completed
	total_course_contents = Content.objects.filter(module__in=modules).count()
	completed_count = len(completed_content_ids)
	is_course_completed = completed_count == total_course_contents and total_course_contents > 0

	# ✅ Show completion page when user reaches the last topic
	show_completion_page = selected_content == all_contents[-1] if all_contents else False

	context = {
		'course': course,
		'modules': modules,
		'contents': all_contents,
		'selected_content': selected_content,
		'previous_content': previous_content,
		'next_content': next_content,
		'progress': progress,
		'completed_content_ids': list(completed_content_ids),
		'is_course_completed': is_course_completed,
		'show_completion_page': show_completion_page,  # ✅ Pass to template
	}
	return render(request, 'students/course_content.html', context)


@login_required
def transaction_history(request):
    student = Student.objects.get(user=request.user)
    transactions = WalletTransaction.objects.filter(
    student=request.user,
    instructor__isnull=True
	).exclude(description__icontains='Platform').order_by('-created_at')


    try:
        wallet = Wallet.objects.get(student=student)
    except Wallet.DoesNotExist:
        wallet = None

    # Calculate summary totals
    total_in = transactions.filter(transaction_type='credit').aggregate(total=Sum('amount'))['total'] or 0
    total_out = transactions.filter(transaction_type='debit').aggregate(total=Sum('amount'))['total'] or 0
    current_balance = wallet.balance if wallet else 0

    return render(request, 'students/transaction_history.html', {
        'transactions': transactions,
        'wallet': wallet,
        'total_in': total_in,
        'total_out': total_out,
        'current_balance': current_balance,
    })


@login_required
def user_logout(request):
	logout(request)
	return redirect('login')  # Redirect to user login after logout