from django.urls import path
from . import views

urlpatterns = [
    # path('register/', views.registration_view, name='register'),
    # path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('setting/', views.setting, name='setting'),
    path('my_courses/', views.my_courses, name='my_courses'),
    path('student_lessons/', views.student_lessons, name='student_lessons'),
]