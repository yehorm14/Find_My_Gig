from django.urls import path, reverse_lazy
from gigs import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

# This is our "namespace". If we ever add another app (like 'accounts'), 
# this stops Django from confusing 'gigs:home' with 'accounts:home'.
app_name = 'gigs'

urlpatterns = [
    # --- MAIN PAGES ---
    path('', views.home, name='home'),

    # --- GIGS ROUTING ---
    path('gigs/', views.gig_listings, name='gig_listings'),
    path('gigs/<int:gig_id>/', views.gig_detail, name='gig_detail'),
    path('gigs/<int:gig_id>/apply/', views.apply_gig, name='apply_gig'),
    path('gigs/<int:gig_id>/withdraw/', views.withdraw_gig, name='withdraw_gig'),
    path('gigs/<int:gig_id>/save/', views.save_gig, name='save_gig'),
    path('gigs/<int:gig_id>/unsave/', views.unsave_gig, name='unsave_gig'),
    path('gigs/create/', views.create_gig_listing, name='create_gig'),
    path('gigs/<int:gig_id>/gig_review/', views.submit_review, name='submit_review'),
    path('musicians/<int:musician_id>/review/', views.submit_musician_review, name='submit_musician_review'),
    path('bands/<int:band_id>/save/', views.save_band, name='save_band'),
    path('bands/<int:band_id>/unsave/', views.unsave_band, name='unsave_band'),

    # --- USER PROFILES ROUTING ---
    path('musicians/', views.musicians_list, name='musicians_list'),
    path('musicians/<int:id>/', views.musician_detail, name='musician_profile'),
    path('bands/', views.bands_list, name='bands_list'), 
    path('bands/<int:id>/', views.band_detail, name='band_profile'),
    
    # Scouting (Bookmarking Musicians)
    path('musicians/<int:musician_id>/save/', views.save_musician, name='save_musician'),
    path('musicians/<int:musician_id>/unsave/', views.unsave_musician, name='unsave_musician'),

    # Invitations
    path('musicians/<int:musician_id>/invite/', views.invite_musician, name='invite_musician'),
    path('invitations/<int:invite_id>/respond/', views.respond_invitation, name='respond_invitation'),

    # --- USER PORTAL ---
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/my-applications/', views.my_applications, name='my_applications'),
    path('dashboard/my-listings/', views.my_listings, name='my_listings'),
    path('dashboard/my-profile/', views.my_profile, name='my_profile'),
    path('dashboard/my-profile/update/', views.update_profile, name='update_profile'),
    path('dashboard/my-profile/delete-account/', views.delete_account, name='delete_account'),
    path('dashboard/my-listings/create/', views.create_gig_listing, name='create_gig_listing'),
    path('dashboard/my-bookmarks/', views.my_bookmarks, name='my_bookmarks'),
    path('dashboard/my-listings/<int:listing_id>/delete/', views.delete_listing, name='delete_listing'),


    # -- AUTHENTICATION AND SIGNUPS --
    path('signup/', views.signup_choice, name='signup'),

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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)