from . import views
from django.urls import include, path

urlpatterns =[
    path('register/', views.register_instructor, name='register_instructor'),
    path('dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('not-approved/', views.not_approved, name='not_approved'),
]