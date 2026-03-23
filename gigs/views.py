from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login,logout
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.conf import settings



# IMPORT THE MODELS and FORMS
from gigs.models import Musician, Band, Listing, Application, Review
from gigs.forms import UserSignUpForm, MusicianProfileForm, BandProfileForm
import difflib

# ==========================================
# --- HELPER FUNCTIONS ---
# ==========================================

def clean_search_query(query):
    """Takes whatever the user typed in the search bar, removes extra spaces, and makes it lowercase."""
    if query:
        return query.strip().lower()
    return ''

def fuzzy_match_instrument(user_typo):
    """If the user spells 'gutar', this function guesses they meant 'guitar' and fixes it!"""
    valid_instruments = ['guitar', 'drums', 'vocals', 'piano', 'bass']
    best_guesses = difflib.get_close_matches(user_typo, valid_instruments, n=1, cutoff=0.5)

    if best_guesses:
        return best_guesses[0]
    return user_typo


# ==========================================
# --- CORE VIEWS ---
# ==========================================

def home(request):
    """Handles the main landing page (/)"""
    context = {'welcome_message': 'Welcome to Find My Gig!'}
    return render(request, 'gigs/home.html', context)

def gig_listings(request):
    """Handles the Gig Listings page using real database data."""

    # Start with all listings from the database
    gigs_queryset = Listing.objects.all()

    # GET parameters for filtering
    raw_instrument = request.GET.get('instrument', '')
    location_query = clean_search_query(request.GET.get('location', ''))
    date_query = request.GET.get('date', '')
    sort_by = request.GET.get('sort', '')

    # Filter by instrument (using fuzzy match)
    search_term = fuzzy_match_instrument(clean_search_query(raw_instrument)) if raw_instrument else ''
    if search_term:
        gigs_queryset = gigs_queryset.filter(req_instruments__icontains=search_term)

    # Filter by location
    if location_query:
        gigs_queryset = gigs_queryset.filter(location__icontains=location_query)

    # Filter by date
    if date_query:
        gigs_queryset = gigs_queryset.filter(deadline=date_query)

    # Sorting logic
    if sort_by == 'name':
        gigs_queryset = gigs_queryset.order_by('title')
    elif sort_by == 'date':
        gigs_queryset = gigs_queryset.order_by('deadline')

    context = {
        'gigs': gigs_queryset,
        'selected_instrument': raw_instrument,
        'corrected_instrument': search_term if search_term != clean_search_query(raw_instrument) else None,
        'selected_location': location_query,
        'selected_date': date_query,
        'current_sort': sort_by,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    }

    return render(request, 'gigs/gig_listings.html', context)

def gig_detail(request, gig_id):
    """Pulls a specific gig from the database using its ID."""
    gig = get_object_or_404(Listing, id=gig_id)
    has_applied = False
    is_bookmarked = False

    if request.user.is_authenticated:
        has_applied = Application.objects.filter(
            applicant=request.user, 
            listing=gig
        ).exists()

    return render(request, 'gigs/gig_detail.html', {
        'gig': gig,
        'has_applied': has_applied,
        'is_bookmarked': is_bookmarked,
    })

def musicians_list(request):
    """Shows all musicians registered in the database."""
    musicians = Musician.objects.all()
    return render(request, 'gigs/musicians_list.html', {'musicians': musicians})

def musician_detail(request, id):
    """Pulls a specific musician's profile from the database."""
    musician = get_object_or_404(Musician, id=id)
    return render(request, 'gigs/musician_detail.html', {'musician': musician})

def band_profile(request, id):
    """Pulls a specific band's profile from the database."""
    band = get_object_or_404(Band, id=id)
    return render(request, 'gigs/band_profile.html', {'band': band})

def create_gig(request):
    """Handles the form where bands can list a new gig."""
    if request.method == 'POST':
        return redirect(reverse('gigs:gig_listings'))
    return render(request, 'gigs/create_gig.html')


# ==========================================
# --- USER PORTAL VIEWS ---
# ==========================================

@login_required
def dashboard(request):
    """Handles the user dashboard navigation page."""
    return render(request, 'gigs/dashboard.html')

@login_required
def my_applications(request):
    """Shows only the applications created by the logged-in user."""
    user_applications = Application.objects.filter(applicant=request.user)
    return render(request, 'gigs/my_applications.html', {'applications': user_applications})

@login_required
def my_listings(request):
    """Shows only the gigs posted by the logged-in user's band."""
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
    except:
        profile = request.user.band
        profile_type = 'band'

    return render(request, 'gigs/my_profile.html', {
        'profile': profile,
        'profile_type': profile_type
    })


# ==========================================
# --- AUTHENTICATION & SIGNUP VIEWS ---
# ==========================================

@transaction.atomic
def signup_choice(request):
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
        else:
            data = json.loads(request.body)
            username = data.get('username')
            firstname = data.get('firstname')
            surname = data.get('surname')
            bio = data.get('about')
            age = data.get('age')
            instruments = data.get('instruments')
            picture = None

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
    if request.method == 'POST':
        user = request.user
        print(f"Deleting user: {user.username} (id: {user.id})")
        logout(request)
        user.delete()
        print("User deleted")
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def create_gig_listing(request):
    if request.method == 'POST':
        return JsonResponse({
            'success': True,
            'listing': {
                'id': 1,
                'title': 'Test',
                'req_instruments': 'Guitar',
                'deadline': '2026-04-01',
                'location': 'Glasgow'
            }
        })

@login_required
def delete_listing(request, listing_id):
    if request.method == 'POST':
        return JsonResponse({'success': True})

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
        return JsonResponse({'success': True})

def unsave_gig(request, gig_id):
    if request.method == 'POST':
        return JsonResponse({'success': True})

@login_required
def submit_review(request, gig_id):
    gig = get_object_or_404(Listing, id=gig_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('feedback')
        reviewee = gig.band.user

        if not rating:
            return render(request, 'gigs/gig_review.html', {
                'gig': gig,
                'error': 'Please select a rating'
            })

        Review.objects.create(
            reviewer=request.user,
            reviewee=reviewee,
            rating=int(rating),
            comment=comment
        )
        return redirect('gigs:gig_detail', gig_id=gig_id)

    return render(request, 'gigs/gig_review.html', {'gig': gig})

@login_required
def submit_musician_review(request, musician_id):
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
        return redirect('gigs:musician_profile', id=musician_id)

    return render(request, 'gigs/musician_review.html', {'musician': musician})
