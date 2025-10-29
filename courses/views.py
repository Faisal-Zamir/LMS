from django.shortcuts import render,redirect, get_object_or_404, HttpResponseRedirect
from .models import Course,Lecture,Category,Cart,Review
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import *
from django.db.models import Avg,Sum, Count

# AIzaSyBKzUUSUkSzDfPiXFf6-XxKrfAAeDj-x7U
def get_cart_items(request):
    cart_items = None
    cart_courses = None
    total_courses = 0  # To store the total number of courses in the cart
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.courses.all()
            cart_courses = cart.courses.values_list('id', flat=True)
            total_courses = cart_items.count()  # Count total courses in the cart
        except Cart.DoesNotExist:
            pass
    return cart_items, cart_courses, total_courses

def add_course(request):
    return render(request, 'courses/add_course.html') 

def all_course(request):
    return render(request, 'courses/all_course.html') 

def course_view(request,course_id):
    categories = Category.objects.all()

    course = Course.objects.get(id=course_id)
    # Fetch all lectures for the course
    lectures = Lecture.objects.filter(section__course=course)

    # Get the first lecture, if it exists
    first_lecture = lectures.first()

    # Get the video URL from the first lecture, if it exists
    first_video_url_demo = first_lecture.video_url if first_lecture else None

    # Fetch goals and requirements related to the course
    goals = course.goal_set.all()
    requirements = course.requirement_set.all()
    sections = course.section_set.prefetch_related('lecture_set').all()
    # lectures = Lecture.objects.filter(section__course=course)  # Assuming Lecture model has a ForeignKey to Section
    # total_lectures = lectures.count()
    # # Update the total_lectures field in the Course object
    # course.total_lectures = total_lectures
    # course.save()

    # Calculate discount percentage
    original_price = course.orignal_price
    offer_price = course.offer_price
    discount_percentage = round(((original_price - offer_price) / original_price) * 100, 2) if original_price != 0 else 0

    recent_courses = Course.objects.order_by('-created_at')[:6]

    cart_items, cart_courses, total_courses = get_cart_items(request)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            stars = form.cleaned_data.get('stars')
            title = form.cleaned_data.get('title')
            content = form.cleaned_data.get('content')
            user = request.user
            review = Review.objects.create(user=user, course=course, title=title, content=content, stars=stars)
            review.save()
            
            # Calculate average stars for the course
            course_reviews = Review.objects.filter(course=course)
            # total_stars = sum(review.stars for review in course_reviews)
            # print("total star", total_stars)
            total_reviews = course_reviews.count()
            # print("total review", total_reviews)
            # average_stars = total_stars / total_reviews if total_reviews > 0 else 0
            # print(average_stars)
            # print("average stars")
            # Update course_review field in course model
            course.course_review = total_reviews
            course.save()
            
            return redirect('course_view', course_id=course_id)
        else:
            print(form.errors)
    else:
        form = ReviewForm()
    
    reviews = Review.objects.filter(course=course)
    context = {
        'course': course,
        'goals': goals,
        'requirements': requirements,
        'sections': sections,
        # 'total_lectures':total_lectures,
        'discount_percentage': discount_percentage,  # Add discount percentage to the context
        'categories':categories,
        'recent_courses': recent_courses,
        'first_video_url_demo':first_video_url_demo,
        'cart_courses': cart_courses,  # Pass the cart courses to the template context
        'cart_items': cart_items,
        'total_courses':total_courses,
        'form':form,
        'reviews':reviews,

    }
  
    return render(request, 'courses/course_view.html',context) 

@login_required
@require_POST
def add_to_cart(request):
    # print("Request Method:", request.method)
    # print("Request Headers:", request.headers)
    if request.method == 'POST':
        course_id = request.POST.get('course_id')

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Course not found.'}, status=404)

        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.courses.add(course)
        total_courses = Cart.objects.get(user=request.user).courses.count()
        return JsonResponse({'success': True, 'message': 'Course added to cart successfully.'})

    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method or not an AJAX request.'}, status=400)

@require_POST
def remove_from_cart(request):
    course_id = request.POST.get('course_id')
    course = get_object_or_404(Course, id=course_id)

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.courses.remove(course)

    # Check if the cart is empty
    if cart.courses.count() == 0:
        cart.delete()
        return JsonResponse({'success': True, 'message': 'Course removed from cart successfully. Cart is empty.'})
    
    return JsonResponse({'success': True, 'message': 'Course removed from cart successfully.'})

@login_required
def fetch_cart_items(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        user_cart_items = Cart.objects.filter(user=request.user)
        cart_items_data = []
        for cart_item in user_cart_items:
            for course in cart_item.courses.all():
                cart_items_data.append({
                    'id': course.id,
                    'title': course.title,
                    'image': course.image.url,
                    'price': course.offer_price
                })
        return JsonResponse({'cart_items': cart_items_data})
    else:
        return JsonResponse({'error': 'Invalid request method or not an AJAX request.'}, status=400)

def courses(request):
    courses = Course.objects.all()
    categories = Category.objects.all()
 
    # Get total number of courses
    total_courses_on_page = courses.count()

    cart_items, cart_courses, total_courses = get_cart_items(request)

    
    # Check if the 'free' parameter is present in the URL
    if 'free' in request.GET:
        # Filter courses where offer_price is zero or null
        courses = courses.filter(Q(offer_price=0) | Q(offer_price__isnull=True))
 
    elif 'paid' in request.GET:
        # Filter courses where offer_price is greater than 0
        courses = courses.filter(offer_price__gt=0)
    
    # Check if the 'level' parameter is present in the URL
    if 'level' in request.GET:
        # Filter courses based on the level provided in the URL
        level = request.GET.get('level')  # Assuming the parameter is 'level'
        courses = courses.filter(level__iexact=level)

    # Get total number of courses after filtering
    total_courses_on_page = courses.count()
    
    # Pagination
    paginator = Paginator(courses, 4)  # 10 courses per page
    page_number = request.GET.get('page')
    try:
        courses = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        courses = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results
        courses = paginator.page(paginator.num_pages)
    

    context = {
        'total_courses_on_page': total_courses_on_page,
        'courses': courses,
        'categories':categories,
        'cart_courses': cart_courses,  # Pass the cart courses to the template context
        'cart_items': cart_items,
        'total_courses':total_courses,

    }
    return render(request, 'courses/courses.html',context) 

def category_course(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    courses = category.course_set.all()
    categories = Category.objects.all()
    cart_items, cart_courses, total_courses = get_cart_items(request)
    
    # Get total number of courses before pagination
    total_courses_on_page = courses.count()
   
    # Pagination
    paginator = Paginator(courses, 4)  # 10 courses per page
    page_number = request.GET.get('page')
    try:
        courses = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        courses = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results
        courses = paginator.page(paginator.num_pages)
    
    context = {
        'total_courses_on_page':total_courses_on_page,
        'category': category, 
        'courses': courses,
        'categories':categories,
        'cart_courses': cart_courses,  # Pass the cart courses to the template context
        'cart_items': cart_items,
        'total_courses':total_courses,
        }
    return render(request, 'courses/category_courses.html', context)

def course_lessons(request, course_id):
    # Get the course object based on the course_id parameter
    course = get_object_or_404(Course, pk=course_id)
    # Fetch goals and requirements related to the course
    goals = course.goal_set.all()
    requirements = course.requirement_set.all()
    sections = course.section_set.prefetch_related('lecture_set').all()
    lectures = Lecture.objects.filter(section__course=course)  # Assuming Lecture model has a ForeignKey to Section
    question_form = QuestionForm()
    answer_form = AnswerForm()

    if request.method == 'POST':
        if 'questionForm' in request.POST:
            question_form = QuestionForm(request.POST)
            if question_form.is_valid():
                question = question_form.save(commit=False)
                lecture_id = request.POST.get('lecture_id')
                question.lecture = Lecture.objects.get(id=lecture_id)
                question.user = request.user
                question.save()
                return HttpResponseRedirect(request.path_info)
            else:
                print(question_form.errors)
        elif 'answerForm' in request.POST:
            answer_form = AnswerForm(request.POST)
            if answer_form.is_valid():
                answer = answer_form.save(commit=False)
                answer.question = Question.objects.get(id=request.POST['question_id'])
                answer.save()
                return HttpResponseRedirect(request.path_info)
            else:
                print(answer_form.errors)
        else:
            print("Not working")

    context = {
        'course': course,  # Pass the course object to the template
        'goals': goals,
        'requirements': requirements,
        'sections': sections,
        'lectures':lectures,
        'question_form':question_form,
        'answer_form':answer_form,

    }
    return render(request, 'courses/course_lessons.html', context)


def get_lecture_description(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        lecture_id = request.GET.get('lecture_id')
        try:
            lecture = Lecture.objects.get(id=lecture_id)
            questions = Question.objects.filter(lecture=lecture)
            question_data = []
            for question in questions:
                answers = question.answer_set.all().values_list('answer_text', flat=True)
                question_data.append({
                    'id': question.id,
                    'question_text': question.question_text,
                    'answers': list(answers)
                })
            return JsonResponse({'description': lecture.description, 'questions': question_data})
        except Lecture.DoesNotExist:
            return JsonResponse({'error': 'Lecture not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

