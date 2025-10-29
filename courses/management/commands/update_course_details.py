from django.core.management.base import BaseCommand
from courses.models import Course, Lecture  # Replace 'yourapp' with the name of your Django app

class Command(BaseCommand):
    help = 'Update the durations and total lectures for all courses'

    def handle(self, *args, **options):
        courses = Course.objects.all()

        for course in courses:
            total_duration_minutes = 0
            total_lectures = 0

            # Iterate over lectures related to the course
            for section in course.section_set.all():
                for lecture in section.lecture_set.all():
                    # Split the duration into minutes and seconds
                    minutes, seconds = divmod(lecture.duration, 1)
                    total_duration_minutes += minutes + seconds / 100  # Convert seconds to fraction of a minute
                    total_lectures += 1

            # Convert total duration to hours and minutes
            total_hours = int(total_duration_minutes // 60)
            total_minutes = int(total_duration_minutes % 60)

            # Update duration for the course
            course.duration = round(total_hours + total_minutes / 100, 2)  # Convert minutes to fraction of an hour
            course.total_lectures = total_lectures
            course.save()
