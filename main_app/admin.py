from django.contrib import admin
from .models import Category, Post, Subscriber,Comment,Reply
from django.db import models  # Import models module
from ckeditor.widgets import CKEditorWidget  # Import CKEditorWidget
from django.utils import timezone

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date','published_date')
    list_filter = ('published_date',)
    search_fields = ('title', 'content')
    filter_horizontal = ('categories',)

    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget}
    }

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display =  ['name', 'comment','post']

@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display =  ['name', 'reply','comment','created_at']