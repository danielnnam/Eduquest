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
    path('add_to_cart/<int:course_id>/', views.add_to_cart, name='add_to_cart'),
    path('wishlist/', views.view_cart, name="view_cart"),
    path('cart/delete/<int:item_id>/', views.delete_cart_item, name='delete_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.success_page, name='success_page'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('my-course/<int:course_id>/content/', views.content_view, name='content_view'),
    path('my-course/<int:course_id>/content/<int:content_id>/', views.content_view, name='content_view_with_content'),
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('logout/', views.user_logout, name='user_logout'),
]