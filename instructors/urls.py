from . import views
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns =[
    path('register/', views.register_instructor, name='register_instructor'),
    path('dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('not-approved/', views.not_approved, name='not_approved'),
    path('courses/', views.instructor_course_list, name='instructor_course_list'),
    path('courses/create/', views.instructor_course_create, name='instructor_course_create'),
    path('courses/update/<int:course_id>/', views.instructor_course_update, name='instructor_course_update'),
    path('courses/delete/<int:course_id>/', views.instructor_course_delete, name='instructor_course_delete'),
    path('course/details/<int:course_id>/', views.instructor_course_detail, name='instructor_course_detail'),


    path('modules/add/<int:course_id>/', views.add_module, name='add_module'),  # Updated to include course_id
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)