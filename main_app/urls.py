from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('all_users/', views.all_users, name='all_users'), 
    path('all_students/', views.all_students, name='all_students'),
    path('enrollment/', views.enrollment, name='enrollment'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('blog/', views.blog, name='blog'),
    path('blog/category/<int:category_id>/', views.category_posts, name='category_posts'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('Terms & Conditions/', views.terms, name='terms'),
    path('Privacy Policy/', views.privacy, name='privacy'),
    path('JafriCode Intro/', views.jc_intro, name='jc_intro'),
    path('About Instructor/', views.about_inst, name='about_inst'),
    path('single_page_blog/<int:post_id>/', views.single_page_blog, name='single_page_blog'),

]  