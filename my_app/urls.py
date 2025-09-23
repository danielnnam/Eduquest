from django.urls import include, path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('student/', include('student.urls')),
    path('instructors/', include('instructors.urls')),
    path('administration/', include('administration.urls')),
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('instructor/pending/', views.instructor_pending_dashboard, name='instructor_pending_dashboard'),
    path('courses/', views.courses_list, name='courses_list'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('blog/', views.blog, name='blog'),
    path('blogs/<int:pk>/', views.blog_details, name='blog_details'),
    path('ckeditor/', include('ckeditor_uploader.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)