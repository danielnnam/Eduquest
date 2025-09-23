import os
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField 
from django.contrib.auth import get_user_model


# Create your models here.

class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='instructors/profile_pics/', blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    expertise = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    approved = models.BooleanField(default=False)

    account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    withdrawn = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.user.username


# creation of courses
class Course(models.Model):
	COURSE_CATEGORIES = [
		('Artificial Intelligence', 'Artificial Intelligence'),
		('Data Science', 'Data Science'),
		('Web Development', 'Web Development'),
		('Mobile App Development', 'Mobile App Development'),
		('Cloud Computing', 'Cloud Computing'),
		('Networking', 'Networking'),
		('Database Management', 'Database Management'),
		('Software Engineering', 'Software Engineering'),
		('IT Project Management', 'IT Project Management'),
		('Computer Science', 'Computer Science'),
	]

	COURSE_LEVELS = [
		('Beginner', 'Beginner'),
		('Intermediate', 'Intermediate'),
		('Advanced', 'Advanced'),
	]

	name = models.CharField(max_length=255)
	description = models.TextField()
	created_by = models.ForeignKey(User, on_delete=models.CASCADE)
	start_date = models.DateField(null=True)
	end_date = models.DateField(null=True)
	duration = models.CharField(max_length=50, null=True)
	credits = models.IntegerField(null=True)
	category = models.CharField(max_length=255, choices=COURSE_CATEGORIES, null=True)
	level = models.CharField(max_length=255, choices=COURSE_LEVELS, null=True)
	syllabus = RichTextField(null=True)
	price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	is_active = models.BooleanField(default=True)
	language = models.CharField(max_length=50, choices=[('English', 'English'), ('French', 'French'), ('Spanish', 'Spanish')], null=True)
	image = models.ImageField(upload_to='course_images/', blank=True, null=True)
	video = models.FileField(upload_to='course_videos/', blank=True, null=True)
	instructor = models.ForeignKey(Instructor, related_name='courses', on_delete=models.CASCADE)  # Add this line
	@property
	def alt_text(self):
		return os.path.basename(self.image.path)

	def __str__(self):
		return self.name


class Module(models.Model):
	course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
	title = models.CharField(max_length=200)
	description = models.TextField(blank=True)

	def __str__(self):
		return self.title

class Content(models.Model):
	CONTENT_TYPE_CHOICES = [
		('text', 'Text'),
		('video', 'Video'),
		('document', 'Document'),
	]

	module = models.ForeignKey(Module, related_name='contents', on_delete=models.CASCADE)
	topic = models.CharField(max_length=200)
	content_type = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES)
	content_data_text = RichTextField(null=True)
	content_data_video = models.FileField(upload_to='contents_videos/', blank=True, null=True)
	content_data_document = models.FileField(upload_to='documents/', blank=True, null=True)

	def save(self, *args, **kwargs):
		# Ensure only one content_data field is populated based on content_type
		if self.content_type == 'text':
			self.content_data_video = None
			self.content_data_document = None
		elif self.content_type == 'video':
			self.content_data_text = None
			self.content_data_document = None
		elif self.content_type == 'document':
			self.content_data_text = None
			self.content_data_video = None
		super().save(*args, **kwargs)

class StudentProgress(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	module = models.ForeignKey(Module, on_delete=models.CASCADE, null=True, blank=True)
	content = models.ForeignKey(Content, on_delete=models.CASCADE, null=True, blank=True)
	completed = models.BooleanField(default=False)  # Tracks completed content
	course_completed = models.BooleanField(default=False)  # Tracks full course completion

	class Meta:
		unique_together = ('user', 'course', 'module', 'content')

	def __str__(self):
		return f"{self.user.username} - {self.course} Progress"

	def update_completion(self):
		"""Check if all course contents are completed"""
		total_contents = Content.objects.filter(module__course=self.course).count()
		completed_contents = StudentProgress.objects.filter(
			user=self.user, course=self.course, completed=True
		).count()

		# Mark course as completed if all contents are done
		self.course_completed = completed_contents == total_contents
		self.save()


class WithdrawalRequest(models.Model):
	instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	is_processed = models.BooleanField(default=False)
	requested_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Withdrawal {self.amount} by {self.instructor.user.username}"
	

class WalletTransactions(models.Model):
	TRANSACTION_TYPE_CHOICES = [
		('credit', 'Credit'),
		('debit', 'Debit'),
	]

	instructor = models.ForeignKey(User, on_delete=models.CASCADE)  # Or a custom Instructor model
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
	description = models.CharField(max_length=255)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.instructor.username} - {self.transaction_type} - {self.amount}"

