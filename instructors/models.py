from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField 


# Create your models here.

class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    expertise = models.TextField()
    phone = models.CharField(max_length=15, null=True, blank=True)

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

    def __str__(self):
        return self.name

