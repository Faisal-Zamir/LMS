from django.shortcuts import render
from django.contrib.auth import logout
from django.shortcuts import redirect
from .forms import UserForm, ProfileForm
from courses.models import Enrollment

# this is the comment
# def registration_view(request):
#     return render(request, 'users/register.html')

# def login_view(request):
#     return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('homepage')  # Redirect to home page or any other desired URL

def profile(request):
    return render(request, 'users/profile.html')

def setting(request):
    user = request.user
    profile = user.profile
    if request.method == 'POST':
            user_form = UserForm(request.POST, instance=user)
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
            
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                return redirect('profile')
            else:
                print(user_form.errors)
                print(profile_form.errors)

    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)
    context = {
        'user_form':user_form,
        'profile_form':profile_form,

    }
    return render(request, 'users/setting.html',context)

def my_courses(request):
    # Retrieve courses enrolled by the current user
    user_enrollments = Enrollment.objects.filter(student=request.user)
    courses = [enrollment.course for enrollment in user_enrollments]
    context = {
        'courses': courses
    }
    return render(request, 'users/my_courses.html', context)

def student_lessons(request):
    return render(request, 'users/student_lessons.html')
