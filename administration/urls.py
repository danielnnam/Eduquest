from . import views
from django.urls import include, path


urlpatterns =[
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/', views.admin, name='admin'),
    path('admin-dashboard/data/', views.dashboard_data, name='dashboard_data'),
    path('students/', views.admin_students, name='admin_students'),
    path('edit-wallet/<int:student_id>/', views.edit_wallet_balance, name='edit_wallet_balance'),
    path('edit-student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('courses/', views.admin_course_list, name='admin_course_list'),
    path('courses/pending/', views.pending_courses, name='pending_courses'),
    path('courses/approve/<int:course_id>/', views.approve_course, name='approve_course'),
    path('instructors/', views.instructor_list, name='admin_instructor_list'),
    path('instructors/<int:instructor_id>/', views.instructor_detail, name='admin_instructor_detail'),
    path('instructors/<int:instructor_id>/toggle/', views.toggle_instructor_status, name='toggle_instructor_status'),
    path('instructors/<int:instructor_id>/approve/', views.approve_instructor, name='approve_instructor'),
    path("admin-dashboard/create-blog/", views.create_blog_post, name="create_blog_post"),
    path('admin-dashboard/blogs_lists/', views.blog_list, name='blog_list'),  
    path('admin-dashboard/blogs_lists/<int:pk>/', views.blog_detail, name='blog_detail'),
    path("admin-dashboard/blogs/<int:pk>/edit/", views.edit_blog_post, name="edit_blog_post"),
    path("admin-dashboard/blogs/<int:pk>/delete/", views.delete_blog_post, name="delete_blog_post"),
    path("transactions/", views.transactions, name="admin_transactions"),
    path('admin/logout/', views.admin_logout, name='admin_logout'),

]