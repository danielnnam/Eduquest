from django.db import models
from django.contrib.auth.models import User
from instructors.models import Course
from instructors.models import Instructor
import uuid

# Create your models here.


# Student
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# User Profile
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username


# Wallet
class Wallet(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.student.first_name}'s Wallet"


# Transactions
class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10)  # 'credit', 'debit', or 'edit'
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} on {self.date}"


# Enrollment
class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)  # Assuming User is the student
    date_enrolled = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"


# Cart 
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user.username}'s Cart"


# Cart Items 
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.course.name} in {self.cart.user.username}'s Cart"

    def get_total_price(self):
        return self.course.price  
    

# New model to track wallet transactions
class WalletTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('student_payment', 'Student Payment'),   
        ('instructor_payout', 'Instructor Payout'), 
        ('platform_revenue', 'Platform Revenue'), 
    )

    student = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True,
        related_name="student_transactions"
    )
    instructor = models.ForeignKey(
        'instructors.Instructor', on_delete=models.CASCADE, null=True, blank=True,
        related_name="instructor_transactions"
    )
    course = models.ForeignKey(
        'instructors.Course', on_delete=models.CASCADE, null=True, blank=True
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    # NEW FIELD
    transaction_group_id = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)

    def __str__(self):
        who = self.student.username if self.student else (
            self.instructor.user.username if self.instructor else "N/A"
        )
        return f"{who} - {self.transaction_type} - ${self.amount}"

