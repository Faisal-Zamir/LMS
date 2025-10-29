from django.core.management.base import BaseCommand
from courses.models import Lecture  # Replace 'yourapp' with the name of your Django app
from pytube import YouTube

class Command(BaseCommand):
    help = 'Update the durations for all video lectures'

    def handle(self, *args, **options):
        lectures = Lecture.objects.all()

        for lecture in lectures:
            duration_minutes = self.get_video_duration(lecture.video_url)
            lecture.duration = round(duration_minutes, 2)
            lecture.save()

    def get_video_duration(self, url):
        yt = YouTube(url)
        duration_seconds = yt.length
        total_minutes = duration_seconds // 60
        total_seconds = duration_seconds % 60
        total_duration = total_minutes + (total_seconds / 100)  # Convert seconds to minutes fraction
        return total_duration
