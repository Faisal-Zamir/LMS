from django.db import models
from ckeditor.fields import RichTextField
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=255)
    content = RichTextField()
    SEO_description = models.CharField(blank=True, null=True,max_length=255)  # Added SEO description field
    categories = models.ManyToManyField(Category)
    thumbnail = models.ImageField(upload_to='post_thumbnails/', null=True, blank=True)

    # Published date defaults to the current date and time when the post is published
    published_date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"   
class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Reply by {self.name} on {self.comment.post}"

class Subscriber(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email