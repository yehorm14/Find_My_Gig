"""
Main URL Configuration for the find_my_gig project.
Routes traffic to the primary 'gigs' application.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),
    
    # Delegate all primary routing and authentication to the 'gigs' app
    path('', include('gigs.urls')),
]