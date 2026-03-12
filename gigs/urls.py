from django.urls import path
from gigs import views

app_name = 'gigs'

urlpatterns = [
    # Home
    path('', views.index, name='index'),

    # Gigs
    path('gigs/', views.gig_listings, name='gig_listings'),
    path('gigs/<int:gig_id>/', views.gig_detail, name='gig_detail'),
    path('gigs/create/', views.create_gig, name='create_gig'),

    #Musicians 
    path('musicians/', views.musicians_list, name='musicians_list'),
    path('musicians/<int:id>/', views.musician_profile, name='musician_profile'),
    
    #Bands
    path('bands/<int:id>/', views.band_profile, name='band_profile'),

]