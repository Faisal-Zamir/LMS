from django.contrib import admin
from .models import *
from .resources import *
from import_export.admin import ImportExportModelAdmin


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Course)
class CourseAdmin(ImportExportModelAdmin):
    list_display = ['title','student_enrolled','category','duration','total_lectures','course_review', 'level','language', 'orignal_price','offer_price', 'created_at', 'updated_at']
    resource_class = CourseResource

@admin.register(Section)
class SectionAdmin(ImportExportModelAdmin):
    list_display = ['title', 'course']
    list_filter = ['course']
    resource_class = SectionResource

@admin.register(Lecture)
class LectureAdmin(ImportExportModelAdmin):
    list_display = ['title', 'section','duration','is_preview']
    list_filter = ['section']
    resource_class = LectureResource

@admin.register(Requirement)
class RequirementAdmin(ImportExportModelAdmin):
    list_display = ['course','description']
    resource_class = RequirementResource

@admin.register(Goal)
class GoalAdmin(ImportExportModelAdmin):
    list_display = ['course','description']
    resource_class = GoalResource

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrollment_date', 'completion_status', 'completion_date')
    list_filter = ('course', 'completion_status')
    search_fields = ('student__username', 'course__name')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    list_filter = ('created_at',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'stars', 'created_at','title','content')
    list_filter = ('course', 'created_at')
    search_fields = ('user__username', 'course__title', 'title', 'content')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'lecture', 'user')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer_text')