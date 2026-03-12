from django.urls import path
from rango import views

app_name = 'rango'

urlpatterns = [
    path("", views.home, name='home'),
]