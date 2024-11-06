from . import views
from django.urls import include, path

urlpatterns =[
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
]