import logging
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, logout
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings

# IMPORT THE MODELS and FORMS
from gigs.models import Musician, Band, Listing, Application, Review, MediaLink, Invitation
from gigs.forms import UserSignUpForm, MusicianProfileForm, BandProfileForm

# Set up a logger for tracking issues in production
logger = logging.getLogger(__name__)


# ==========================================
# --- CORE PAGES (Browsing & Viewing) ---
# ==========================================

def home(request):
    """Handles the main landing page (/). Redirects logged-in users to their dashboard."""
    if request.user.is_authenticated:
        return redirect('gigs:dashboard')
        
    context = {'welcome_message': 'Welcome to Find My Gig!'}
    return render(request, 'gigs/home.html', context)


def gig_listings(request):
    """Handles the main Gig list page with dropdown filtering and sorting."""
    gigs_queryset = Listing.objects.all()

    instrument_filter = request.GET.get('instrument', '')
    date_query = request.GET.get('date', '')
    sort_by = request.GET.get('sort', '')

    if instrument_filter:
        gigs_queryset = gigs_queryset.filter(req_instruments__icontains=instrument_filter)
    if date_query:
        gigs_queryset = gigs_queryset.filter(deadline=date_query)

    if sort_by == 'name':
        gigs_queryset = gigs_queryset.order_by('title')
    else:
        gigs_queryset = gigs_queryset.order_by('deadline')
    
    applied_gig_ids = []
    bookmarked_gig_ids = []
    if request.user.is_authenticated:
        applied_gig_ids = Application.objects.filter(applicant=request.user).values_list('listing_id', flat=True)
        bookmarked_gig_ids = request.user.saved_gigs.values_list('id', flat=True)

    context = {
        'gigs': gigs_queryset,
        'applied_gig_ids': applied_gig_ids,
        'selected_instrument': instrument_filter,
        'selected_date': date_query,
        'current_sort': sort_by,
        'bookmarked_gig_ids': bookmarked_gig_ids,
    }

    return render(request, 'gigs/gig_listings.html', context)

def gig_detail(request, gig_id):
    """Shows the full details of a single gig, including the Google Map."""
    listing = get_object_or_404(Listing, id=gig_id)
    
    has_applied = False
    is_bookmarked = False
    
    if request.user.is_authenticated:
        has_applied = listing.applications_received.filter(applicant=request.user).exists()
        is_bookmarked = listing.bookmarks.filter(id=request.user.id).exists()

    context = {
        'listing': listing, 
        'has_applied': has_applied,
        'is_bookmarked': is_bookmarked,
        'google_maps_frontend_key': settings.GOOGLE_MAPS_FRONTEND_KEY,
    }
    
    return render(request, 'gigs/gig_detail.html', context)

def musicians_list(request):
    """Shows the page for browsing all registered musicians with a dropdown filter."""
    musicians = Musician.objects.all()
    instrument_filter = request.GET.get('instrument', '')
    
    if instrument_filter:
        musicians = musicians.filter(instruments__icontains=instrument_filter)
        
    return render(request, 'gigs/musicians_list.html', {'musicians': musicians, 'selected_instrument': instrument_filter})

def musician_detail(request, id):
    """Shows the public profile for a specific musician and fetches band data for invitations."""
    musician = get_object_or_404(Musician, id=id)
    reviews = Review.objects.filter(reviewee=musician.user).order_by('-id')
    
    is_scouted = False
    band_listings = [] 
    
    if request.user.is_authenticated and hasattr(request.user, 'band'):
        is_scouted = request.user.band.scouted_musicians.filter(id=musician.id).exists()
        # Fetch only the active listings belonging to the logged-in band
        band_listings = Listing.objects.filter(band=request.user.band)
    
    context = {
        'musician': musician,
        'reviews': reviews,
        'is_scouted': is_scouted,
        'band_listings': band_listings,
        'google_maps_frontend_key': settings.GOOGLE_MAPS_FRONTEND_KEY,
    }
    return render(request, 'gigs/musician_detail.html', context)


def bands_list(request):
    """Shows the page for browsing all registered bands and venues."""
    bands = Band.objects.all()
    return render(request, 'gigs/bands_list.html', {'bands': bands})

def band_detail(request, id):
    """Shows the public profile for a specific band and checks if it is bookmarked."""
    band = get_object_or_404(Band, id=id)
    is_bookmarked = False
    
    if request.user.is_authenticated and hasattr(request.user, 'musician'):
        is_bookmarked = request.user.musician.bookmarked_bands.filter(id=band.id).exists()
        
    context = {
        'band': band, 
        'is_bookmarked': is_bookmarked,
        'google_maps_frontend_key': settings.GOOGLE_MAPS_FRONTEND_KEY,
    }
        
    return render(request, 'gigs/band_detail.html', context)

# ==========================================
# --- USER DASHBOARD & MANAGEMENT ---
# ==========================================

@login_required
def dashboard(request):
    """The main hub for a logged-in user. Routes to templates with profile context."""
    context = {}
    
    # Try to load a Musician profile
    try:
        context['profile'] = request.user.musician
        context['profile_type'] = 'musician'  
        return render(request, 'gigs/musician_dashboard.html', context)
    except Musician.DoesNotExist:
        pass

    # Try to load a Band profile
    try:
        context['profile'] = request.user.band
        context['profile_type'] = 'band'  
        return render(request, 'gigs/band_dashboard.html', context)
    except Band.DoesNotExist:
        pass
        
    return redirect('gigs:home')
    
@login_required
def my_applications(request):
    """Shows a Musician all the gigs they have applied for, and pending invites."""
    try:
        musician = request.user.musician
    except Musician.DoesNotExist:
        return redirect('gigs:dashboard')

    user_applications = Application.objects.filter(applicant=request.user)
    pending_invites = musician.received_invitations.filter(status='Pending').order_by('-created_at')
    
    context = {
        'applications': user_applications,
        'invitations': pending_invites,
        'google_maps_frontend_key': settings.GOOGLE_MAPS_FRONTEND_KEY,
    }
    return render(request, 'gigs/my_applications.html', context)

@login_required
def my_bookmarks(request):
    """Shows users their saved items. Musicians see Gigs/Bands. Bands see scouted Musicians."""
    context = {}
    
    # Logic for Musician
    try:
        profile = request.user.musician
        context['profile_type'] = 'musician'
        context['saved_gigs'] = request.user.saved_gigs.all()
        context['saved_bands'] = profile.bookmarked_bands.all()
        return render(request, 'gigs/my_bookmarks.html', context)
    except Musician.DoesNotExist:
        pass

    # Logic for Band
    try:
        profile = request.user.band
        context['profile_type'] = 'band'
        context['scouted_musicians'] = profile.scouted_musicians.all()
        return render(request, 'gigs/my_bookmarks.html', context)
    except Band.DoesNotExist:
        pass

    return redirect('gigs:dashboard')

@login_required
def my_listings(request):
    """Shows a Band all the gigs they have currently posted."""
    try:
        band = request.user.band
        listings = Listing.objects.filter(band=band)
    except Band.DoesNotExist:
        listings = []
    return render(request, 'gigs/my_listings.html', {'listings': listings})

@login_required
def my_profile(request):
    """Shows the user's editable profile settings."""
    try:
        profile = request.user.musician
        profile_type = 'musician'
        media_links = profile.media_links.all()
    except Musician.DoesNotExist:
        try:
            profile = request.user.band
            profile_type = 'band'
            media_links = []
        except Band.DoesNotExist:
            return redirect('gigs:home')

    context = {
        'profile': profile,
        'profile_type': profile_type,
        'media_links': media_links
    }

    if profile_type == 'musician':
        return render(request, 'gigs/my_profile_musician.html', context)
    else:
        return render(request, 'gigs/my_profile_band.html', context)

# ==========================================
# --- AUTHENTICATION & SETTINGS ---
# ==========================================

@transaction.atomic
def signup_choice(request):
    """Handles account creation for Musicians or Bands."""
    if request.user.is_authenticated:
        return redirect('gigs:home')

    user_form = UserSignUpForm()

    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        user_form = UserSignUpForm(request.POST)

        if user_type not in ('musician', 'band'):
            return render(request, 'gigs/signup.html', {
                'user_form': user_form,
                'error_message': 'Please select an account type.'
            })

        if user_form.is_valid():
            user = user_form.save()
            
            if user_type == 'musician':
                Musician.objects.create(user=user)
            elif user_type == 'band':
                band_name = request.POST.get('band_name', '').strip()
                Band.objects.create(user=user, name=band_name)

            login(request, user)
            return redirect('gigs:my_profile')

        return render(request, 'gigs/signup.html', {'user_form': user_form})

    return render(request, 'gigs/signup.html')


@login_required
def update_profile(request):
    """Handles saving profile edits via AJAX."""
    if request.method == 'POST':
        user = request.user
        
        if request.content_type and 'multipart' in request.content_type:
            username = request.POST.get('username')
            firstname = request.POST.get('firstname')
            surname = request.POST.get('surname')
            bio = request.POST.get('about')
            age = request.POST.get('age')
            instruments = request.POST.get('instruments')
            picture = request.FILES.get('profile_picture')
            media_links_json = request.POST.get('media_links')
            delete_media_json = request.POST.get('delete_media')
        else:
            data = json.loads(request.body)
            username = data.get('username')
            firstname = data.get('firstname')
            surname = data.get('surname')
            bio = data.get('about')
            age = data.get('age')
            instruments = data.get('instruments')
            picture = None
            media_links_json = data.get('media_links')
            delete_media_json = data.get('delete_media')

        if User.objects.exclude(pk=user.pk).filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'username_taken'})
            
        user.username = username
        user.first_name = firstname or ''
        user.last_name = surname or ''
        user.save()

        try:
            profile = user.musician
            profile.bio = bio
            profile.age = age
            profile.instruments = instruments
            if picture:
                profile.profile_picture = picture
            profile.save()

            if media_links_json:
                new_links = json.loads(media_links_json) if isinstance(media_links_json, str) else media_links_json
                for url in new_links:
                    MediaLink.objects.create(musician=profile, url=url)

            if delete_media_json:
                ids_to_delete = json.loads(delete_media_json) if isinstance(delete_media_json, str) else delete_media_json
                MediaLink.objects.filter(id__in=ids_to_delete).delete()

        except Musician.DoesNotExist:
            try:
                profile = user.band
                profile.bio = bio
                band_name = data.get('band_name') if not 'multipart' in request.content_type else request.POST.get('band_name')
                if band_name:
                    profile.name = band_name
                if picture:
                    profile.profile_picture = picture
                profile.save()
            except Band.DoesNotExist:
                pass

        return JsonResponse({'success': True})
    
    return redirect('gigs:my_profile')

@login_required
def delete_account(request):
    """Permanently deletes the logged-in user."""
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


# ==========================================
# --- AJAX ACTIONS (Gigs, Apps, Bookmarks) ---
# ==========================================

@login_required
def create_gig_listing(request):
    """Allows a Band to post a new Gig via AJAX."""
    if request.method == 'POST':
        try:
            band = request.user.band
        except Band.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'not_a_band'})

        data = json.loads(request.body)
        title = data.get('title', '').strip()
        req_instruments = data.get('req_instruments', '').strip()
        deadline = data.get('date', '')
        description = data.get('description', '').strip()
        location = data.get('location', '').strip()

        if not all([title, req_instruments, deadline, description, location]):
            return JsonResponse({'success': False, 'error': 'missing_fields'})

        listing = Listing.objects.create(
            band=band,
            title=title,
            req_instruments=req_instruments,
            deadline=deadline,
            description=description,
            location=location,
            is_urgent=False
        )

        return JsonResponse({'success': True})
        
    return render(request, 'gigs/create_gig.html')
    
@login_required
def delete_listing(request, listing_id):
    if request.method == 'POST':
        try:
            listing = Listing.objects.get(id=listing_id, band=request.user.band)
            listing.delete()
            return JsonResponse({'success': True})
        except Listing.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'not_found'})
    
    return JsonResponse({'success': False, 'error': 'invalid_request'})

def apply_gig(request, gig_id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'not_logged_in'})
        
        listing = get_object_or_404(Listing, id=gig_id)
        
        if Application.objects.filter(applicant=request.user, listing=listing).exists():
            return JsonResponse({'success': False, 'error': 'already_applied'})
        
        Application.objects.create(applicant=request.user, listing=listing)
        return JsonResponse({'success': True})

def withdraw_gig(request, gig_id):
    if request.method == 'POST':
        listing = get_object_or_404(Listing, id=gig_id)
        Application.objects.filter(applicant=request.user, listing=listing).delete()
        return JsonResponse({'success': True})

def save_gig(request, gig_id):
    if request.method == 'POST':
        listing = get_object_or_404(Listing, id=gig_id)
        listing.bookmarks.add(request.user)
        return JsonResponse({'success': True})

def unsave_gig(request, gig_id):
    if request.method == 'POST':
        listing = get_object_or_404(Listing, id=gig_id)
        listing.bookmarks.remove(request.user)
        return JsonResponse({'success': True})

def save_band(request, band_id):
    if request.method == 'POST':
        band = get_object_or_404(Band, id=band_id)
        request.user.musician.bookmarked_bands.add(band)
        return JsonResponse({'success': True})

def unsave_band(request, band_id):
    if request.method == 'POST':
        band = get_object_or_404(Band, id=band_id)
        request.user.musician.bookmarked_bands.remove(band)
        return JsonResponse({'success': True})


# ==========================================
# --- MUSICIAN SCOUTING & INVITES ---
# ==========================================

@login_required
def save_musician(request, musician_id):
    """Adds a Musician to a Band's Scouted roster via AJAX."""
    if request.method == 'POST':
        if not hasattr(request.user, 'band'):
            return JsonResponse({'success': False, 'error': 'Only bands can scout talent.'})
            
        musician = get_object_or_404(Musician, id=musician_id)
        request.user.band.scouted_musicians.add(musician)
        return JsonResponse({'success': True})

@login_required
def unsave_musician(request, musician_id):
    """Removes a Musician from a Band's Scouted roster via AJAX."""
    if request.method == 'POST':
        if not hasattr(request.user, 'band'):
            return JsonResponse({'success': False, 'error': 'Invalid request.'})
            
        musician = get_object_or_404(Musician, id=musician_id)
        request.user.band.scouted_musicians.remove(musician)
        return JsonResponse({'success': True})

@login_required
def invite_musician(request, musician_id):
    """Allows a Band to formally invite a Musician to one of their gigs."""
    if request.method == 'POST':
        try:
            band = request.user.band
            musician = get_object_or_404(Musician, id=musician_id)
            data = json.loads(request.body)
            listing = get_object_or_404(Listing, id=data.get('listing_id'), band=band)

            if Invitation.objects.filter(musician=musician, listing=listing, status='Pending').exists():
                return JsonResponse({'success': False, 'error': 'You have already invited them.'})

            Invitation.objects.create(band=band, musician=musician, listing=listing)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@login_required
def respond_invitation(request, invite_id):
    """Allows a Musician to Accept or Decline a band's invitation."""
    if request.method == 'POST':
        try:
            invitation = get_object_or_404(Invitation, id=invite_id, musician=request.user.musician)
            data = json.loads(request.body)
            action = data.get('action')
            
            if action in ['Accepted', 'Declined']:
                invitation.status = action
                invitation.save()
                
                if action == 'Accepted':
                    Application.objects.get_or_create(applicant=request.user, listing=invitation.listing)
                    
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'error': 'Invalid action.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


# ==========================================
# --- REVIEWS & FEEDBACK ---
# ==========================================

@login_required
def submit_review(request, gig_id):
    """Allows a Musician to submit a review for a Band after a gig."""
    gig = get_object_or_404(Listing, id=gig_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('feedback')
        reviewee = gig.band.user

        if not rating:
            return render(request, 'gigs/gig_review.html', {'gig': gig, 'error': 'Please select a rating'})

        Review.objects.create(reviewer=request.user, reviewee=reviewee, rating=int(rating), comment=comment)
        return redirect('gigs:gig_detail', gig_id=gig_id)

    return render(request, 'gigs/gig_review.html', {'gig': gig})

@login_required
def submit_musician_review(request, musician_id):
    """Allows a Band to submit a review for a Musician."""
    musician = get_object_or_404(Musician, id=musician_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('feedback')

        if not rating:
            return render(request, 'gigs/musician_review.html', {'musician': musician, 'error': 'Please select a rating'})

        Review.objects.create(reviewer=request.user, reviewee=musician.user, rating=int(rating), comment=comment)
        return redirect('gigs:musician_detail', id=musician_id)

    return render(request, 'gigs/musician_review.html', {'musician': musician})