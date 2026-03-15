from django.urls import path, reverse_lazy
from gigs import views
from django.contrib.auth import views as auth_views

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
    path('signup/band/', views.band_signup, name='band_signup'),

    # -- LOGIN/LOGOUT --
    path(
        'login/', 
         auth_views.LoginView.as_view(
             template_name='gigs/login.html',
             redirect_authenticated_user=True,), 
        name='login'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # -- PASSWORD RESETS --
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='gigs/password_reset_form.html',
            email_template_name='gigs/password_reset_email.html',
            subject_template_name='gigs/password_reset_subject.txt',
            success_url=reverse_lazy('gigs:password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='gigs/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='gigs/password_reset_confirm.html',
            success_url=reverse_lazy('gigs:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='gigs/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
]