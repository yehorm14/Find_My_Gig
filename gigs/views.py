from django.shortcuts import render, redirect
from django.urls import reverse
import difflib

# ==========================================
# --- HELPER FUNCTIONS ---
# ==========================================

def clean_search_query(query):
    """Takes whatever the user typed in the search bar, removes extra spaces, and makes it lowercase so our search doesn't break."""
    if query:
        return query.strip().lower()
    return ''

def fuzzy_match_instrument(user_typo):
    """If the user spells 'gutar', this function guesses they meant 'guitar' and fixes it!"""
    valid_instruments = ['guitar', 'drums', 'vocals', 'piano', 'bass']
    
    # get_close_matches tries to find the closest valid word. 
    # n=1 means we only want the top guess. cutoff=0.5 means it must be at least a 50% match.
    best_guesses = difflib.get_close_matches(user_typo, valid_instruments, n=1, cutoff=0.5)
    
    if best_guesses:
        return best_guesses[0]
    return user_typo # If it can't figure it out, just return what they typed.


# ==========================================
# --- CORE VIEWS ---
# ==========================================

def home(request):
    """Handles the main landing page (/)"""
    # 'context' is the dictionary we use to pass Python data directly into our HTML file
    context = {'welcome_message': 'Welcome to Find My Gig!'}
    # Tell Django exactly which HTML file in the templates folder to show the user
    return render(request, 'gigs/home.html', context)

def gig_listings(request):
    """Handles the Gig Listings page and the Search/Filter logic (/gigs/)"""
    
    # 1. THE CATCHER: Look at the URL and grab the search terms the user typed in
    raw_instrument = request.GET.get('instrument', '')
    cleaned_instrument = clean_search_query(raw_instrument)
    
    location_query = clean_search_query(request.GET.get('location', ''))
    date_query = request.GET.get('date', '') 
    sort_by = request.GET.get('sort', '')

    # 2. THE SPELLCHECKER: Fix the instrument typo if they made one
    search_term = fuzzy_match_instrument(cleaned_instrument) if cleaned_instrument else ''

    # 3. THE MOCK DATABASE: Fake data until we hook up our real SQLite database
    mock_gigs = [
        {'id': 1, 'title': 'Drummer needed for a new band', 'band_name': 'Name TBC', 'instrument': 'drums', 'location': 'glasgow', 'deadline': '2026-03-15', 'description': 'Seeking a talented drummer...'},
        {'id': 2, 'title': 'Guitarist Needed Urgently!', 'band_name': 'Swim School', 'instrument': 'guitar', 'location': 'edinburgh', 'deadline': '2026-02-25', 'description': 'Current Guitarist injured...'}
    ]

    # 4. THE FILTERING FUNNEL: Throw away gigs that don't match the user's search
    if search_term:
        mock_gigs = [gig for gig in mock_gigs if search_term in gig['instrument']]
    if location_query:
        mock_gigs = [gig for gig in mock_gigs if location_query in gig['location']]
    if date_query:
        mock_gigs = [gig for gig in mock_gigs if gig['deadline'] == date_query]

    # 5. THE SORTER: Order the remaining gigs alphabetically or by date
    if sort_by == 'name':
        mock_gigs = sorted(mock_gigs, key=lambda k: k['title'])
    elif sort_by == 'date':
        mock_gigs = sorted(mock_gigs, key=lambda k: k['deadline'])

    # 6. PACKAGE AND SEND: Put all the finished data into the context dictionary and send it to the HTML file
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
    """Handles clicking on a single gig to see more details (/gigs/<id>/)"""
    # Note: gig_id was passed in automatically by the urls.py file!
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
    """Handles the directory showing all musicians on the site (/musicians/)"""
    mock_musicians = [
        {'id': 1, 'name': 'Jack Daniel', 'instrument': 'Drums', 'location': 'Edinburgh'},
        {'id': 2, 'name': 'John William', 'instrument': 'Guitar', 'location': 'Glasgow, Scotland'}
    ]
    return render(request, 'gigs/musicians_list.html', {'musicians': mock_musicians})

def musician_profile(request, id):
    """Handles clicking on a single musician to view their profile (/musicians/<id>/)"""
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
    """Handles clicking on a single band to view their profile (/bands/<id>/)"""
    context = {
        'band_id': id, 
        'name': 'Soul Shatterers', 
        'location': 'Glasgow',
        'bio': 'The Soul Shatterers are a rock band based in Glasgow. They have been established for a year now.'
    }
    return render(request, 'gigs/band_profile.html', context)

def create_gig(request):
    """Handles the form where bands can list a new gig (/gigs/create/)"""
    # If the user clicked "Submit" on the form, redirect them back to the gig listings page
    if request.method == 'POST':
        return redirect(reverse('gigs:gig_listings'))
    
    # If they just navigated to the page, show them the empty HTML form
    return render(request, 'gigs/create_gig.html')