from . import views
from django.urls import include, path


urlpatterns =[
    # path('', include('my_app.urls')),
    path('register/', views.register_student, name='register_student'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
]