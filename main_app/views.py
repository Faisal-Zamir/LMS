from django.shortcuts import render, redirect, get_object_or_404
from .models import Post,Category
from django.db.models import Count, Sum
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail
from .forms import ContactForm, SubscriberForm
from django.contrib import messages
from courses.models import Category as CourseCategory
from courses.models import Cart, Enrollment, Course
from django.contrib.auth.decorators import login_required
from main_app.models import Post, Category,Comment
import random
from courses.views import get_cart_items  # Import the function from the courses app
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from .models import Subscriber
from .forms import CommentForm, ReplyForm
from django.http import HttpResponseRedirect


def fetch_categories():
    return CourseCategory.objects.all()

def handle_login_registration(request):
    registration_form = UserCreationForm()
    login_form = AuthenticationForm()

    if request.method == 'POST':
        if 'register' in request.POST:
            registration_form = UserCreationForm(request.POST)
            if registration_form.is_valid():
                registration_form.save()
                username = registration_form.cleaned_data.get('username')
                password = registration_form.cleaned_data.get('password1')
                user = authenticate(username=username, password=password)
                login(request, user)
                return redirect('homepage')  # Redirect to home page after successful registration
        elif 'login' in request.POST:
            login_form = AuthenticationForm(data=request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('homepage')  # Redirect to home page after successful login

    return registration_form, login_form
    
def fetch_random_categories():
    # Fetch all categories
    all_categories = CourseCategory.objects.all()
    # Shuffle the categories randomly
    random_categories = random.sample(list(all_categories), min(len(all_categories), 8))
    return random_categories
def homepage(request):
    courses = Course.objects.all()
    blog_posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')[:3]
    blog_categories = Category.objects.all()  # Query all categories
    random_categories = fetch_random_categories()

    categories = fetch_categories()
    
    # Call handle_login_registration function to handle registration
    forms_or_redirect = handle_login_registration(request)
    
    try:
        # Unpack the returned forms
        registration_form, login_form = forms_or_redirect if len(forms_or_redirect) == 2 else (forms_or_redirect[0], None)
    except TypeError:  # Handle TypeError if redirect response is returned
        return forms_or_redirect
    cart_items, cart_courses, total_courses = get_cart_items(request)

    context = {
        'registration_form': registration_form,
        'login_form': login_form,
        'categories': categories,
        'courses': courses,
        'blog_posts':blog_posts,
        'blog_categories':blog_categories,
        'random_categories':random_categories,
        'cart_courses': cart_courses,  # Pass the cart courses to the template context
        'cart_items': cart_items,
        'total_courses':total_courses,
    }
    return render(request, 'main_app/homepage.html', context)

def dashboard(request):
    return render(request, 'main_app/dashboard.html')

def all_users(request):
    return render(request, 'main_app/all_users.html')

def all_students(request):
    # Retrieve all enrollments
    enrollments = Enrollment.objects.select_related('student', 'course').all()

    # Prepare data to pass to the template
    student_data = []
    for enrollment in enrollments:
        # Extract information for each enrollment
        student_name = f"{enrollment.student.first_name} {enrollment.student.last_name}"
        email = enrollment.student.email
        course_title = enrollment.course.title
        offer_price = enrollment.course.offer_price
        completion_status = "Completed" if enrollment.completion_status else "Incomplete"
        enrollment_date = enrollment.enrollment_date
        country = enrollment.student.profile.country

        # Append data to the list
        student_data.append({
            'student_name': student_name,
            'email': email,
            'course_title': course_title,
            'offer_price': offer_price,
            'completion_status': completion_status,
            'enrollment_date': enrollment_date,
            'country': country,
        })

    # Pass the data to the template for rendering
    context = {
        'student_data': student_data,
    }
    return render(request, 'main_app/all_students.html', context)

def enrollment(request):
    return render(request, 'main_app/enrollment.html')

@login_required
def cart(request):
    cart_items, cart_courses, total_courses = get_cart_items(request)
    # Fetch cart items for the logged-in user
    user_cart_items = Cart.objects.filter(user=request.user).prefetch_related('courses')

    # Calculate subtotal and total using Django aggregation
    subtotal = sum(course.offer_price for course in cart_items)  # Sum offer prices of all courses
    total = subtotal  # You can apply any discounts or taxes here if needed

    categories = fetch_categories()
    context = {
        'categories': categories,
        'subtotal': subtotal,
        'total': total,
        'user_cart_items': user_cart_items,
        'cart_courses': cart_courses,
        'total_courses': total_courses,
        'cart_items': cart_items,

    }
    return render(request, 'main_app/cart.html', context)

@login_required
def checkout(request):
    cart_items, cart_courses, total_courses = get_cart_items(request)
    # Fetch cart items for the logged-in user
    user_cart_items = Cart.objects.filter(user=request.user).prefetch_related('courses')

    # Calculate subtotal and total
    subtotal = sum(item.courses.aggregate(Sum('offer_price'))['offer_price__sum'] or 0 for item in user_cart_items)
    total = subtotal  # Add any additional charges or taxes here

    categories = fetch_categories()
    context = {
        'categories': categories,
        'user_cart_items': user_cart_items,
        'subtotal': subtotal,
        'total': total,
        'cart_courses': cart_courses,  # Pass the cart courses to the template context
        'cart_items': cart_items,
        'total_courses':total_courses,
    }
    return render(request, 'main_app/checkout.html', context)

def blog(request):
    cart_items, cart_courses, total_courses = get_cart_items(request)

    categories = fetch_categories()
    posts = Post.objects.all()
    # Fetch the first 4 recent posts ordered by published date
    recent_posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')[:4]

    blog_categories = Category.objects.all()  # Query all categories
    categories_with_posts = Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)
    # Call handle_login_registration function to handle registration
    forms_or_redirect = handle_login_registration(request)
    
    try:
        # Unpack the returned forms
        registration_form, login_form = forms_or_redirect if len(forms_or_redirect) == 2 else (forms_or_redirect[0], None)
    except TypeError:  # Handle TypeError if redirect response is returned
        return forms_or_redirect
    
    query = request.GET.get('q')
    if query:
        # Filter posts by title (exact match)
        posts = Post.objects.filter(title__icontains=query)
    else:
        posts = Post.objects.all()

   # Pagination
    paginator = Paginator(posts, 4)  # 10 courses per page
    page_number = request.GET.get('page')
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results
        posts = paginator.page(paginator.num_pages)   
    context = {
        'posts': posts, 
        'categories': blog_categories, 
        'recent_posts': recent_posts,
        'categories': categories, 
        'categories_with_posts':categories_with_posts,
        'registration_form': registration_form,
        'login_form': login_form,
        'cart_courses': cart_courses,  # Pass the cart courses to the template context
        'cart_items': cart_items,
        'query':query,
        'total_courses':total_courses,
        }  
    return render(request, 'main_app/blog.html', context)

def category_posts(request, category_id):
    cart_items, cart_courses, total_courses = get_cart_items(request)
    categories = fetch_categories()
    category = get_object_or_404(Category, id=category_id)
    posts = category.post_set.all()
    categories_with_posts = Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)
    # Fetch the first 4 recent posts ordered by published date
    recent_posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')[:4]
    # Call handle_login_registration function to handle registration
    forms_or_redirect = handle_login_registration(request)
    
    try:
        # Unpack the returned forms
        registration_form, login_form = forms_or_redirect if len(forms_or_redirect) == 2 else (forms_or_redirect[0], None)
    except TypeError:  # Handle TypeError if redirect response is returned
        return forms_or_redirect
   # Pagination
    paginator = Paginator(posts, 4)  # 10 courses per page
    page_number = request.GET.get('page')
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results
        posts = paginator.page(paginator.num_pages)   
    context = {
        'category': category, 
        'posts': posts,
        'categories':categories,
        'categories_with_posts':categories_with_posts,
        'recent_posts': recent_posts,
        'registration_form': registration_form,
        'login_form': login_form,
        'cart_courses': cart_courses,  # Pass the cart courses to the template context
        'cart_items': cart_items,
        'total_courses':total_courses,
        }
    return render(request, 'main_app/category_posts.html', context)

def single_page_blog(request,post_id):
    cart_items, cart_courses, total_courses = get_cart_items(request)
    categories = fetch_categories()
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post)
    # Fetch the first 3 recent posts ordered by published date
    recent_posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')[:3]
    # Call handle_login_registration function to handle registration
    forms_or_redirect = handle_login_registration(request)
    
    try:
        # Unpack the returned forms
        registration_form, login_form = forms_or_redirect if len(forms_or_redirect) == 2 else (forms_or_redirect[0], None)
    except TypeError:  # Handle TypeError if redirect response is returned
        return forms_or_redirect
    
    comment_form = CommentForm()
    reply_form = ReplyForm()

    if request.method == 'POST':
        if 'commentForm' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment_id = comment.id
                comment.save()
                return HttpResponseRedirect(request.path_info)
            else:
                print(comment_form.errors)
        elif 'replyForm' in request.POST:
            reply_form = ReplyForm(request.POST)
            if reply_form.is_valid():
                reply = reply_form.save(commit=False)
                reply.name="Faisal Zamir"
                reply.comment = Comment.objects.get(id=request.POST['comment_id'])
                reply.save()
                return HttpResponseRedirect(request.path_info)
            else:
                print(reply_form.errors)
        else:
            print("not wor")

    context = {
        'categories': categories,
        'post': post,
        'recent_posts': recent_posts,
        'registration_form': registration_form,
        'login_form': login_form,
        'cart_courses': cart_courses,  # Pass the cart courses to the template context
        'cart_items': cart_items,
        'total_courses':total_courses,
        'comment_form':comment_form,
        'comments':comments,
        'reply_form':reply_form,

    }
    return render(request, 'main_app/single.html',context)

def contact(request):
    categories = fetch_categories()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            # Send email
            send_mail(
                f'New Contact Form Submission from {name}',
                f'Email: {email}\nMessage: {message}',
                email,  # Use the sender's email address as the 'from_email'
                ['jafricodeLMS@hotmail.com'],  # Recipient email address
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully.')
            return redirect('contact')  

    else:
        form = ContactForm()

    # Handle registration/login
    registration_form, login_form = handle_login_registration(request)
    cart_items, cart_courses, total_courses = get_cart_items(request)
    context = {
        'form': form,
        'categories': categories,
        'registration_form': registration_form,
        'login_form': login_form,
        'cart_courses': cart_courses,  # Pass the cart courses to the template context
        'cart_items': cart_items,
        'total_courses':total_courses,
    }
    return render(request, 'main_app/contact.html', context)

def about(request):
    if request.method == 'POST':
        sub_form = SubscriberForm(request.POST)
        if sub_form.is_valid():
            sub_form.save()
            data = {'message': 'Successfully subscribed!'}
        else:
            data = sub_form.errors
            if 'email' in data:
                data['error'] = data['email'][0]
                del data['email']
        return JsonResponse(data)
    else:
        sub_form = SubscriberForm()

    cart_items, cart_courses, total_courses = get_cart_items(request)
    categories = fetch_categories()
    # Call handle_login_registration function to handle registration
    forms_or_redirect = handle_login_registration(request)
    
    try:
        # Unpack the returned forms
        registration_form, login_form = forms_or_redirect if len(forms_or_redirect) == 2 else (forms_or_redirect[0], None)
    except TypeError:  # Handle TypeError if redirect response is returned
        return forms_or_redirect
    
    context = {
        'categories': categories,
        'registration_form': registration_form,
        'login_form': login_form,
        'cart_courses': cart_courses,  # Pass the cart courses to the template context
        'cart_items': cart_items,
        'sub_form':sub_form,
        'total_courses':total_courses,
    }
    return render(request, 'main_app/about.html',context)

def terms(request):
    cart_items, cart_courses, total_courses = get_cart_items(request)
    categories = fetch_categories()
    # Call handle_login_registration function to handle registration
    forms_or_redirect = handle_login_registration(request)
    
    try:
        # Unpack the returned forms
        registration_form, login_form = forms_or_redirect if len(forms_or_redirect) == 2 else (forms_or_redirect[0], None)
    except TypeError:  # Handle TypeError if redirect response is returned
        return forms_or_redirect
    context = {
        'categories': categories,
        'registration_form': registration_form,
        'login_form': login_form,
        'cart_courses': cart_courses,  # Pass the cart courses to the template context
        'cart_items': cart_items,
        'total_courses':total_courses,
    }
    return render(request, 'main_app/Terms & Conditions.html',context)

def privacy(request):
    cart_items, cart_courses, total_courses = get_cart_items(request)
    categories = fetch_categories()
    # Call handle_login_registration function to handle registration
    forms_or_redirect = handle_login_registration(request)
    
    try:
        # Unpack the returned forms
        registration_form, login_form = forms_or_redirect if len(forms_or_redirect) == 2 else (forms_or_redirect[0], None)
    except TypeError:  # Handle TypeError if redirect response is returned
        return forms_or_redirect
    context = {
        'categories': categories,
        'registration_form': registration_form,
        'login_form': login_form,
        'cart_courses': cart_courses,  # Pass the cart courses to the template context
        'cart_items': cart_items,
        'total_courses':total_courses,
    }
    return render(request, 'main_app/Privacy Policy.html',context)

def jc_intro(request):
    cart_items, cart_courses, total_courses = get_cart_items(request)
    categories = fetch_categories()
    # Call handle_login_registration function to handle registration
    forms_or_redirect = handle_login_registration(request)
    
    try:
        # Unpack the returned forms
        registration_form, login_form = forms_or_redirect if len(forms_or_redirect) == 2 else (forms_or_redirect[0], None)
    except TypeError:  # Handle TypeError if redirect response is returned
        return forms_or_redirect
    context = {
        'categories': categories,
        'registration_form': registration_form,
        'login_form': login_form,
        'cart_courses': cart_courses,  # Pass the cart courses to the template context
        'cart_items': cart_items,
        'total_courses':total_courses,
    }
    return render(request, 'main_app/jc_intro.html',context)

def about_inst(request):
    cart_items, cart_courses, total_courses = get_cart_items(request)
    categories = fetch_categories()
    # Call handle_login_registration function to handle registration
    forms_or_redirect = handle_login_registration(request)
    
    try:
        # Unpack the returned forms
        registration_form, login_form = forms_or_redirect if len(forms_or_redirect) == 2 else (forms_or_redirect[0], None)
    except TypeError:  # Handle TypeError if redirect response is returned
        return forms_or_redirect
    context = {
        'categories': categories,
        'registration_form': registration_form,
        'login_form': login_form,
        'cart_courses': cart_courses,  # Pass the cart courses to the template context
        'cart_items': cart_items,
        'total_courses':total_courses,
    }
    return render(request, 'main_app/about_instructor.html',context)


