from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from pytube import YouTube
from django.db.models import Sum  # Importing Sum explicitly
from django.db.models import Avg, Count, Sum

class Category(models.Model):
    name = models.CharField(max_length=50)
    icon = models.TextField(default="No")  # Assuming SVG icon will be stored as text
    num_courses = models.IntegerField(default=0)  # Number of courses for this category

    def __str__(self):
        return self.name

    def update_num_courses(self):
        """
        Update the number of courses associated with this category.
        This method should be called whenever a course is added to or removed from the category.
        """
        self.num_courses = self.course_set.count()  # Count the number of courses related to this category
        self.save()
    
class Course(models.Model):
    title = models.CharField(max_length=250)
    description =  RichTextField()
    image = models.ImageField(upload_to='course_images/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=2)  # Changed to ForeignKey
    tagline = models.CharField(max_length=250)
    level = models.CharField(max_length=51)
    language = models.CharField(max_length=51, default="English")
    orignal_price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration = models.FloatField(default=0)
    created_at = models.DateField(auto_now_add=True, null=True)
    updated_at = models.DateField(auto_now=True)
    total_lectures = models.IntegerField(default=0)
    course_review = models.IntegerField(default=0)
    student_enrolled = models.IntegerField(default=0)
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_course_details()


    def update_course_details(self):
        # Calculate total duration and total lectures for the course
        total_duration_minutes = Lecture.objects.filter(section__course=self).aggregate(total_duration=Sum('duration'))['total_duration'] or 0
        total_lectures = Lecture.objects.filter(section__course=self).count()

        # Convert total duration to hours and minutes format
        total_hours = int(total_duration_minutes // 60)
        total_minutes = int(total_duration_minutes % 60)

        # Update duration for the course
        self.duration = round(total_hours + total_minutes / 100, 2)  # Convert minutes to fraction of an hour

        self.total_lectures = total_lectures
        super().save(update_fields=['duration', 'total_lectures'])

class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    def __str__(self):
        return f'{self.title} of {self.course.title}'

class Lecture(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    video_url = models.URLField()
    description = RichTextField()
    duration = models.FloatField(default=0)  # Store duration in minutes as an integer
    is_preview = models.BooleanField(default=False)


    def __str__(self):
        return f"Lecture Title: {self.title}"  # Displaying lecture title
    
    def save(self, *args, **kwargs):
        # Get the duration of the video
        duration_minutes = self.get_video_duration(self.video_url)
        self.duration = round(duration_minutes, 2)  # Round to 2 decimal places
        super().save(*args, **kwargs)
        
        # Update the total duration and total lectures for the associated course
        self.section.course.update_course_details()

    def get_video_duration(self, url):
        yt = YouTube(url)
        duration_seconds = yt.length
        total_minutes = duration_seconds // 60
        total_seconds = duration_seconds % 60
        total_duration = total_minutes + (total_seconds / 100)  # Convert seconds to minutes fraction
        return total_duration
        
class Requirement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    description =  RichTextField()

class Goal(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    description =  RichTextField()

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    completion_status = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            # This is a new enrollment
            course = self.course
            # Increment the student_enrolled count for the associated course
            course.student_enrolled += 1
            course.save(update_fields=['student_enrolled'])
            # Get the associated profile of the student
            profile = self.student.profile
            # Set the enrolled status to True
            profile.enrolled_status = True
            # Save the profile instance
            profile.save()
        super().save(*args, **kwargs)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    courses = models.ManyToManyField('Course', related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cart for {self.user.username}'

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    stars = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # Rating from 1 to 5
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s review on {self.course.title}"
    

class Question(models.Model):
    question_text = models.TextField()
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.question_text
    
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()

    def __str__(self):
        return self.answer_text