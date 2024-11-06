from django.contrib import admin
from .models import Instructor

# Register your models here.

class InstructorAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'is_approved')
    actions = ['approve_instructors']

    def approve_instructors(self, request, queryset):
        for instructor in queryset:
            instructor.is_approved = True
            instructor.user.is_active = True  # Activate the user account
            instructor.user.save()
            instructor.save()
        self.message_user(request, "Selected instructors have been approved.")

admin.site.register(Instructor)