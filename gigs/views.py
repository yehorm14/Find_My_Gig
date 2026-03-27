import json
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.conf import settings
from django.db import transaction
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# Local App Imports
from gigs.models import (
    Musician, 
    Band, 
    Listing, 
    Application, 
    Review, 
    MediaLink, 
    BandInterest
)
from gigs.forms import UserSignUpForm, MusicianProfileForm, BandProfileForm

# Set up a logger for tracking issues in production
logger = logging.getLogger(__name__)


# ==============================================================================
# --- 1. CORE PAGES (Browsing & Viewing) ---
# ==============================================================================

def home(request):
    """
    Handles the main landing page (/). 
    Redirects logged-in users directly to their dashboard.
    """
    if request.user.is_authenticated:
        return redirect('gigs:dashboard')
        
    context = {'welcome_message': 'Welcome to Find My Gig!'}
    return render(request, 'gigs/home.html', context)


def gig_listings(request):
    """
    Handles the main Gig list page with dropdown filtering and sorting.
    """
    gigs_queryset = Listing.objects.all()

    # Extract filter and sort parameters from URL
    instrument_filter = request.GET.get('instrument', '')
    date_query = request.GET.get('date', '')
    sort_by = request.GET.get('sort', '')

    # Apply filters
    if instrument_filter:
        gigs_queryset = gigs_queryset.filter(req_instruments__icontains=instrument_filter)
    if date_query:
        gigs_queryset = gigs_queryset.filter(deadline=date_query)

    # Apply sorting
    if sort_by == 'name':
        gigs_queryset = gigs_queryset.order_by('title')
    else:
        gigs_queryset = gigs_queryset.order_by('deadline') 
    
    # Track user interactions if logged in
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
    """
    Shows the full details of a single gig, including the Google Map.
    """
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
    """
    Shows the page for browsing all registered musicians with a dropdown filter.
    """
    musicians = Musician.objects.all()
    instrument_filter = request.GET.get('instrument', '')
    
    if instrument_filter:
        musicians = musicians.filter(instruments__icontains=instrument_filter)
        
    return render(request, 'gigs/musicians_list.html', {
        'musicians': musicians, 
        'selected_instrument': instrument_filter
    })


def musician_detail(request, id):
    """
    Shows a specific musician's public profile and reviews.
    """
    musician = get_object_or_404(Musician, id=id)
    reviews = Review.objects.filter(reviewee=musician.user).order_by('-id')
    
    context = {
        'musician': musician,
        'reviews': reviews,
        'google_maps_frontend_key': settings.GOOGLE_MAPS_FRONTEND_KEY,
    }
    return render(request, 'gigs/musician_detail.html', context)


def bands_list(request):
    """
    Shows the page for browsing all registered bands.
    """
    bands = Band.objects.all()
    return render(request, 'gigs/bands_list.html', {'bands': bands})


def band_detail(request, id):
    """
    Shows the public profile for a specific band.
    """
    band = get_object_or_404(Band, id=id)
    context = {
        'band': band, 
        'google_maps_frontend_key': settings.GOOGLE_MAPS_FRONTEND_KEY,
    }
    return render(request, 'gigs/band_detail.html', context)


# ==============================================================================
# --- 2. USER DASHBOARD & MANAGEMENT ---
# ==============================================================================

@login_required
def dashboard(request):
    """
    The main hub for a logged-in user. Routes to the appropriate 
    Musician or Band template based on their profile type.
    """
    if hasattr(request.user, 'musician'):
        return render(request, 'gigs/musician_dashboard.html', {
            'profile': request.user.musician,
            'profile_type': 'musician'
        })
    elif hasattr(request.user, 'band'):
        return render(request, 'gigs/band_dashboard.html', {
            'profile': request.user.band,
            'profile_type': 'band'
        })
        
    return redirect('gigs:home')

    
@login_required
def my_applications(request):
    """
    Shows a Musician all the gigs they have applied for.
    """
    if not hasattr(request.user, 'musician'):
        return redirect('gigs:dashboard')

    user_applications = Application.objects.filter(applicant=request.user)
    context = {
        'applications': user_applications,
        'google_maps_frontend_key': settings.GOOGLE_MAPS_FRONTEND_KEY,
    }
    return render(request, 'gigs/my_applications.html', context)


@login_required
def my_bookmarks(request):
    """
    Shows a Musician their saved gigs.
    """
    if not hasattr(request.user, 'musician'):
        return redirect('gigs:dashboard')
        
    context = {
        'profile_type': 'musician',
        'saved_gigs': request.user.saved_gigs.all()
    }
    return render(request, 'gigs/my_bookmarks.html', context)


@login_required
def my_listings(request):
    """
    Shows a Band all the gigs they have currently posted.
    """
    try:
        band = request.user.band
        listings = Listing.objects.filter(band=band)
    except Band.DoesNotExist:
        listings = []
        
    return render(request, 'gigs/my_listings.html', {'listings': listings})


@login_required
def my_profile(request):
    """
    Shows the user's editable profile settings.
    """
    if hasattr(request.user, 'musician'):
        context = {
            'profile': request.user.musician,
            'profile_type': 'musician',
            'media_links': request.user.musician.media_links.all()
        }
        return render(request, 'gigs/my_profile_musician.html', context)
        
    elif hasattr(request.user, 'band'):
        context = {
            'profile': request.user.band,
            'profile_type': 'band',
            'media_links': []
        }
        return render(request, 'gigs/my_profile_band.html', context)
        
    return redirect('gigs:home')

@login_required
def my_reach_outs(request):
    """View for a Band to see the musicians they have contacted."""
    
    # Security check: Ensure the user actually has a band profile
    if not hasattr(request.user, 'band'):
        return redirect('gigs:dashboard') 
        
    # Fetch all interests sent by this band, newest first
    reach_outs = BandInterest.objects.filter(band=request.user.band).order_by('-created_at')
    
    context = {
        'reach_outs': reach_outs
    }
    
    return render(request, 'gigs/my_reach_outs.html', context)


@login_required
def create_gig(request):
    """
    Renders the gig creation form for Bands.
    """
    if not hasattr(request.user, 'band'):
        return redirect('gigs:dashboard')

    return render(request, 'gigs/create_gig.html')


# ==============================================================================
# --- 3. AUTHENTICATION & SETTINGS ---
# ==============================================================================

@transaction.atomic
def signup_choice(request):
    """
    Handles the custom signup flow, separating users into Musicians 
    or Bands upon creation to enforce correct relational mapping.
    """
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
            
            # Create the associated profile object immediately
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
    """
    Handles saving profile edits (bio, picture, instruments, etc.) via AJAX.
    Supports both JSON payloads and Multipart form data (for image uploads).
    """
    if request.method == 'POST':
        user = request.user
        
        # Determine payload type to extract data safely
        if request.content_type and 'multipart' in request.content_type:
            data = request.POST
            picture = request.FILES.get('profile_picture')
        else:
            data = json.loads(request.body)
            picture = None

        username = data.get('username')
        firstname = data.get('firstname')
        surname = data.get('surname')
        bio = data.get('about')
        age = data.get('age')
        instruments = data.get('instruments')
        media_links_json = data.get('media_links')
        delete_media_json = data.get('delete_media')

        # Check for username conflicts
        if User.objects.exclude(pk=user.pk).filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'username_taken'})
            
        user.username = username
        user.first_name = firstname or ''
        user.last_name = surname or ''
        user.save()

        # Update Musician specific fields
        if hasattr(user, 'musician'):
            profile = user.musician
            profile.bio = bio
            if age: 
                profile.age = int(age)
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

        # Update Band specific fields
        elif hasattr(user, 'band'):
            profile = user.band
            profile.bio = bio
            band_name = data.get('band_name')
            if band_name:
                profile.name = band_name
            if picture:
                profile.profile_picture = picture
            profile.save()

        return JsonResponse({'success': True})
    
    return redirect('gigs:my_profile')


@login_required
def delete_account(request):
    """Permanently deletes the logged-in user and their cascaded profile."""
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# ==============================================================================
# --- 4. AJAX ACTIONS (Gigs, Apps, Bookmarks) ---
# ==============================================================================

@login_required
def create_gig_listing(request):
    """
    Allows a Band to post a new Gig via an AJAX payload.
    """
    if request.method == 'POST':
        if not hasattr(request.user, 'band'):
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
            band=request.user.band,
            title=title,
            req_instruments=req_instruments,
            deadline=deadline,
            description=description,
            location=location,
            is_urgent=False
        )

        return JsonResponse({
            'success': True,
            'listing': {
                'id': listing.id,
                'title': listing.title,
                'req_instruments': listing.req_instruments,
                'deadline': str(listing.deadline),
                'location': listing.location,
                'description': listing.description,
            }
        })
        
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

    
@login_required
def delete_listing(request, listing_id):
    """Allows a Band to delete their own listing."""
    if request.method == 'POST':
        try:
            listing = Listing.objects.get(id=listing_id, band=request.user.band)
            listing.delete()
            return JsonResponse({'success': True})
        except Listing.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'not_found'})
    return JsonResponse({'success': False, 'error': 'invalid_request'})


def apply_gig(request, gig_id):
    """Creates an Application linking a Musician to a Gig."""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'not_logged_in'})
        
        listing = get_object_or_404(Listing, id=gig_id)
        if Application.objects.filter(applicant=request.user, listing=listing).exists():
            return JsonResponse({'success': False, 'error': 'already_applied'})
        
        Application.objects.create(applicant=request.user, listing=listing)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def withdraw_gig(request, gig_id):
    """Deletes an Application linking a Musician to a Gig."""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'not_logged_in'})
            
        listing = get_object_or_404(Listing, id=gig_id)
        Application.objects.filter(applicant=request.user, listing=listing).delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def save_gig(request, gig_id):
    """Adds the Gig to the user's Bookmarked Gigs list."""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'not_logged_in'})
            
        listing = get_object_or_404(Listing, id=gig_id)
        listing.bookmarks.add(request.user) 
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def unsave_gig(request, gig_id):
    """Removes the Gig from the user's Bookmarked Gigs list."""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'not_logged_in'})
            
        listing = get_object_or_404(Listing, id=gig_id)
        listing.bookmarks.remove(request.user)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'})



# ==============================================================================
# --- 5. REVIEWS & FEEDBACK ---
# ==============================================================================

@login_required
def submit_review(request, gig_id):
    """Allows a Musician to submit a review for a Band after a gig."""
    gig = get_object_or_404(Listing, id=gig_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('feedback')

        if not rating:
            return render(request, 'gigs/gig_review.html', {
                'gig': gig,
                'error': 'Please select a rating'
            })

        Review.objects.create(
            reviewer=request.user,
            reviewee=gig.band.user,
            rating=int(rating),
            comment=comment
        )
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
            return render(request, 'gigs/musician_review.html', {
                'musician': musician,
                'error': 'Please select a rating'
            })

        Review.objects.create(
            reviewer=request.user,
            reviewee=musician.user,
            rating=int(rating),
            comment=comment
        )
        return redirect('gigs:musician_detail', id=musician_id)

    return render(request, 'gigs/musician_review.html', {'musician': musician})


@login_required
def send_interest(request, musician_id):
    """Allows a Band to send a simple interest message to a Musician via AJAX."""
    if request.method == 'POST':
        if not hasattr(request.user, 'band'):
            return JsonResponse({'success': False, 'error': 'Only bands can send interest.'})

        band = request.user.band
        musician = get_object_or_404(Musician, id=musician_id)
        data = json.loads(request.body)
        message = data.get('message', '').strip()

        if not message:
            return JsonResponse({'success': False, 'error': 'Message cannot be empty.'})

        if BandInterest.objects.filter(band=band, musician=musician).exists():
            return JsonResponse({'success': False, 'error': 'You have already reached out to this musician.'})

        BandInterest.objects.create(band=band, musician=musician, message=message)
        return JsonResponse({'success': True})
        
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
    

@login_required
def my_inbox(request):
    """Shows a Musician all the interest messages they have received."""
    if not hasattr(request.user, 'musician'):
        return redirect('gigs:dashboard')

    messages = request.user.musician.received_interests.all().order_by('-created_at')
    return render(request, 'gigs/my_inbox.html', {'messages': messages})


@login_required
def delete_interest(request, interest_id):
    """Allows a Musician to delete an interest message from their inbox via AJAX."""
    if request.method == 'POST':
        try:
            musician = request.user.musician
            interest = BandInterest.objects.get(id=interest_id, musician=musician)
            interest.delete()
            return JsonResponse({'success': True})
        except (Musician.DoesNotExist, BandInterest.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Not found.'})
            
    return JsonResponse({'success': False, 'error': 'Invalid request method'})