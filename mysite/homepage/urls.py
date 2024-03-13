from django.contrib import admin
from django.urls import path, include

from . import views

"""path('admin/', admin.site.urls),
    path('', include('homepage.urls')),"""

"""path('', views.hello),"""

urlpatterns = [
    path('', views.catay)
]