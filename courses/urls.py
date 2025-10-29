from django.urls import path
from . import views

urlpatterns = [
    path('add_course/', views.add_course, name='add_course'),
    path('all_course/', views.all_course, name='all_course'),
    path('course_view/<int:course_id>/', views.course_view, name='course_view'),
    path('all_courses/', views.courses, name='courses'),
    path('category/<int:category_id>/', views.category_course, name='category_course'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('fetch_cart_items/', views.fetch_cart_items, name='fetch_cart_items'),
    path('course_lessons/<int:course_id>/', views.course_lessons, name='course_lessons'),
    path('get_lecture_description/', views.get_lecture_description, name='get_lecture_description'),

]