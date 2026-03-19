from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login
from django.db import transaction
from django.contrib.auth.decorators import login_required

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
    return render(request, 'gigs/band_review.html', context)

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
        'current_sort': sort_by
    }
    
    return render(request, 'gigs/gig_listings.html', context)

def gig_detail(request, gig_id):
    """Pulls a specific gig from the database using its ID."""
    gig = get_object_or_404(Listing, id=gig_id)
    return render(request, 'gigs/gig_detail.html', {'gig': gig})

def musicians_list(request):
    """Shows all musicians registered in the database."""
    musicians = Musician.objects.all()
    return render(request, 'gigs/musicians_list.html', {'musicians': musicians})

def musician_profile(request, id):
    """Pulls a specific musician's profile from the database."""
    musician = get_object_or_404(Musician, id=id)
    return render(request, 'gigs/musician_profile.html', {'musician': musician})

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
    return render(request, 'gigs/my_profile.html')


# ==========================================
# --- AUTHENTICATION & SIGNUP VIEWS ---
# ==========================================

def signup_choice(request):
    if request.user.is_authenticated:
        return redirect('gigs:home')
    
    if request.method == 'POST':
        user_type = request.POST.get('user_type')

        if user_type == 'musician':
            return redirect('gigs:musician_signup')
        elif user_type == 'band':
            return redirect('gigs:band_signup')
            
    return render(request, 'gigs/signup.html')

@transaction.atomic
def musician_signup(request):
    if request.user.is_authenticated:
        return redirect('gigs:home')
    
    if request.method == 'POST':
        user_form = UserSignUpForm(request.POST)
        profile_form = MusicianProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            musician = profile_form.save(commit=False)
            musician.user = user
            musician.save()

            login(request, user)
            return redirect('gigs:home')
    else: 
        user_form = UserSignUpForm()
        profile_form = MusicianProfileForm()
    
    return render(request, 'gigs/signup_musician.html', {'user_form': user_form,'profile_form': profile_form,})

@transaction.atomic
def band_signup(request):
    if request.user.is_authenticated:
        return redirect('gigs:home')

    if request.method == 'POST':
        user_form = UserSignUpForm(request.POST)
        profile_form = BandProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            band = profile_form.save(commit=False)
            band.user = user
            band.save()

            login(request, user)
            return redirect('gigs:home')
    else:
        user_form = UserSignUpForm()
        profile_form = BandProfileForm()

    return render(request, 'gigs/signup_band.html', {'user_form': user_form,'profile_form': profile_form,})
