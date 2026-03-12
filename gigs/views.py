from django.shortcuts import render, redirect
from django.urls import reverse
import difflib

# --- HELPER FUNCTIONS ---
def clean_search_query(query):
    """Strips whitespace and standardizes search text."""
    if query:
        return query.strip().lower()
    return ''

def fuzzy_match_instrument(user_typo):
    """Takes a misspelled word and tries to find the closest valid instrument."""
    # The official instruments
    valid_instruments = ['guitar', 'drums', 'vocals', 'piano', 'bass']
    
    # get_close_matches returns a list of the best guesses. 
    # n=1 means we only want the top 1 best guess. 
    # cutoff=0.5 means it must be at least a 50% match to count.
    best_guesses = difflib.get_close_matches(user_typo, valid_instruments, n=1, cutoff=0.5)
    
    if best_guesses:
        return best_guesses[0] # Return the corrected word (e.g., 'guitar')
    
    return user_typo # If it can't guess, just return what they typed


# --- CORE VIEWS ---
def index(request):
    """Handles the Home page (/)"""
    context = {'welcome_message': 'Welcome to Find My Gig!'}
    return render(request, 'gigs/index.html', context)

def gig_listings(request):
    """Handles the Gig Listings and Search engine (/gigs/)"""
    
    # 1. THE CATCHER: Grab everything the user put in the URL
    raw_instrument = request.GET.get('instrument', '')
    cleaned_instrument = clean_search_query(raw_instrument)
    
    location_query = clean_search_query(request.GET.get('location', ''))
    date_query = request.GET.get('date', '') 
    sort_by = request.GET.get('sort', '')

    # 2. THE SPELLCHECKER: Fix the instrument typo if they typed one
    search_term = fuzzy_match_instrument(cleaned_instrument) if cleaned_instrument else ''

    # 3. THE MOCK DATABASE
    mock_gigs = [
        {'id': 1, 'title': 'Drummer needed for a new band', 'band_name': 'Name TBC', 'instrument': 'drums', 'location': 'glasgow', 'deadline': '2026-03-15', 'description': 'Seeking a talented drummer...'},
        {'id': 2, 'title': 'Guitarist Needed Urgently!', 'band_name': 'Swim School', 'instrument': 'guitar', 'location': 'edinburgh', 'deadline': '2026-02-25', 'description': 'Current Guitarist injured...'}
    ]

    # 4. THE FILTERING FUNNEL
    if search_term:
        mock_gigs = [gig for gig in mock_gigs if search_term in gig['instrument']]
        
    if location_query:
        mock_gigs = [gig for gig in mock_gigs if location_query in gig['location']]
        
    if date_query:
        mock_gigs = [gig for gig in mock_gigs if gig['deadline'] == date_query]

    # 5. THE SORTER
    if sort_by == 'name':
        mock_gigs = sorted(mock_gigs, key=lambda k: k['title'])
    elif sort_by == 'date':
        mock_gigs = sorted(mock_gigs, key=lambda k: k['deadline'])

    # 6. Context
    context = {
        'gigs': mock_gigs,
        'selected_instrument': raw_instrument, 
        'corrected_instrument': search_term if search_term != cleaned_instrument else None,
        'selected_location': location_query, 
        'selected_date': date_query,
        'current_sort': sort_by
    }
    
    return render(request, 'gigs/gig_listings.html', context)

def gig_detail(request, gig_id):
    """Handles individual gig details (/gigs/<id>/)"""
    context = {
        'gig_id': gig_id,
        'title': 'Guitarist Needed Urgently!',
        'band_name': 'Swim School',
        'instrument': 'Guitar',
        'deadline': '25/02/2026',
        'location': 'King Tuts, Glasgow',
        'description': 'Current Guitarist is injured, need an urgent replacement.',
    }
    return render(request, 'gigs/gig_detail.html', context)

def musicians_list(request):
    """Handles the Musicians List directory (/musicians/)"""
    mock_musicians = [
        {'id': 1, 'name': 'Jack Daniel', 'instrument': 'Drums', 'location': 'Edinburgh'},
        {'id': 2, 'name': 'John William', 'instrument': 'Guitar', 'location': 'Glasgow, Scotland'}
    ]
    return render(request, 'gigs/musicians_list.html', {'musicians': mock_musicians})

def musician_profile(request, id):
    """Handles individual musician profiles (/musicians/<id>/)"""
    context = {
        'musician_id': id, 
        'name': 'Jack Daniel', 
        'age': 34,
        'location': 'Edinburgh',
        'instruments': 'Drums',
        'bio': 'I was in a band for 3 years before leaving to explore new options.',
        'media_link': 'youtube.com/@JackDoesDrums'
    }
    return render(request, 'gigs/musician_profile.html', context)

def band_profile(request, id):
    """Handles individual band profiles (/bands/<id>/)"""
    context = {
        'band_id': id, 
        'name': 'Soul Shatterers', 
        'location': 'Glasgow',
        'bio': 'The Soul Shatterers are a rock band based in Glasgow. They have been established for a year now.'
    }
    return render(request, 'gigs/band_profile.html', context)

def create_gig(request):
    """Handles the List A Gig page (/gigs/create/)"""
    if request.method == 'POST':
        return redirect(reverse('gigs:gig_listings'))
    
    return render(request, 'gigs/create_gig.html')