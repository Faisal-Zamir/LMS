from django.contrib import admin
from django.urls import path, include
import users, main_app
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('', include('main_app.urls')),
    path('courses/', include('courses.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

