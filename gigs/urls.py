from django.urls import path
from gigs import views

# This is our "namespace". If we ever add another app (like 'accounts'), 
# this stops Django from confusing 'gigs:home' with 'accounts:home'.
app_name = 'gigs'

urlpatterns = [
    # --- MAIN PAGES ---
    # When the user goes to "127.0.0.1:8000/", send them to the 'home' view.
    path('', views.home, name='home'),

    # --- GIGS ROUTING ---
    # When the user goes to "/gigs/", show them the search engine and list of all gigs.
    path('gigs/', views.gig_listings, name='gig_listings'),
    
    # The <int:gig_id> part is a variable! If the user goes to "/gigs/5/", 
    # Django grabs the number 5 and passes it to the 'gig_detail' view.
    path('gigs/<int:gig_id>/', views.gig_detail, name='gig_detail'),
    
    # Form page for users to create a new gig
    path('gigs/create/', views.create_gig, name='create_gig'),

    # --- USER PROFILES ROUTING ---
    # Shows the list of all musicians
    path('musicians/', views.musicians_list, name='musicians_list'),
    
    # Grabs the specific ID from the URL to show a single musician's profile
    path('musicians/<int:id>/', views.musician_profile, name='musician_profile'),
    
    # Grabs the specific ID from the URL to show a single band's profile
    path('bands/<int:id>/', views.band_profile, name='band_profile'),

    # -- AUTHENTICATION AND SIGNUPS --
    path('signup/', views.signup_choice, name='signup'),
    path('signup/musician/', views.musician_signup, name='musician_signup'),
    path('signup/band/', views.band_signup, name='band_signup')
]