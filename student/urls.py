from . import views
from django.urls import include, path


urlpatterns =[
    # path('', include('my_app.urls')),
    path('register/', views.register_student, name='register_student'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('course_lists/', views.course_list, name='course_list'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('logout/', views.user_logout, name='user_logout'),
]