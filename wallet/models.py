from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from decimal import Decimal

class Wallet(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    instructor = models.ForeignKey('instructors.Instructor', on_delete=models.CASCADE, null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return f"{self.student.username}'s Wallet"


class WalletTransaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wallet_transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(
        max_length=10,
        choices=[("debit", "Debit"), ("credit", "Credit")]
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.transaction_type} {self.amount}"


class InstructorTransaction(models.Model):
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="instructor_transactions")
    course = models.ForeignKey("instructors.Course", on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.instructor.username} earned {self.amount} from {self.course.name}"