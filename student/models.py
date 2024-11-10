from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username
    
# models.py
from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField  # Assuming you're using CKEditor for rich text fields

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

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = RichTextField()
    order = models.PositiveIntegerField(default=0)  # To order lessons

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title