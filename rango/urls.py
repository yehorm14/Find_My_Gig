from django.urls import path
from rango import views

app_name = 'rango'

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/musician/', views.musician_signup, name='musician_signup'),
    path('signup/band/', views.band_signup, name='band_signup'),
]