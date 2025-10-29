
from import_export import resources
from .models import *

class CourseResource(resources.ModelResource):
    class Meta:
        model = Course

class SectionResource(resources.ModelResource):
    class Meta:
        model = Section

class LectureResource(resources.ModelResource):
    class Meta:
        model = Lecture

class RequirementResource(resources.ModelResource):
    class Meta:
        model = Requirement

class GoalResource(resources.ModelResource):
    class Meta:
        model = Goal