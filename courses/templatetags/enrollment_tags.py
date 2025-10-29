from django import template
from courses.models import Enrollment

register = template.Library()

@register.filter(name='has_enrollment')
def has_enrollment(lecture, user):
    return Enrollment.objects.filter(course=lecture.section.course, student=user).exists()
