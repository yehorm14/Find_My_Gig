import os
import django
from datetime import date, timedelta  
from dotenv import load_dotenv       

load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'find_my_gig.settings')
django.setup()

import gigs.models as models
from django.contrib.auth.models import User

# ==========================================
# --- HELPER FUNCTIONS ---
# ==========================================

def add_user(username, password, email, isAdmin=False):
    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    if created:
        user.set_password(password)
    if isAdmin:
        user.is_staff = True
        user.is_superuser = True
    user.save()
    return user

def add_musician(user, instruments, bio, age, media_link, location, profile_picture=""):
    musician, created = models.Musician.objects.get_or_create(user=user, defaults={
        'instruments': instruments,
        'bio': bio,
        'age': age,
        'media_link': media_link,
        'location': location,
        'profile_picture': profile_picture
    })
    return musician

def add_band(user, band_name, location, bio, profile_picture=""):
    band, created = models.Band.objects.get_or_create(user=user, defaults={
        'name': band_name,
        'bio': bio,
        'location': location,
        'profile_picture': profile_picture
    })
    return band

def add_listing(band, title, req_instruments, deadline, is_urgent, description, location):
    listing, created = models.Listing.objects.get_or_create(band=band, title=title, defaults={
        'req_instruments': req_instruments,
        'deadline': deadline,
        'is_urgent': is_urgent,
        'description': description,
        'location': location
    })
    return listing

def add_application(applicant, listing, status='Pending'):
    application, created = models.Application.objects.get_or_create(applicant=applicant, listing=listing, defaults={
        'status': status
    })
    return application

# ==========================================
# --- MAIN POPULATION LOGIC ---
# ==========================================

def populate():
    print("1. Creating Users & Musicians...")
    musicians_data = [
        ("GuitarHero99", "Guitar", "20 years of shredding.", 35, "Glasgow"),
        ("BassBoss", "Bass", "Slappin da bass.", 28, "Edinburgh"),
        ("DrumMachine", "Drums", "I hit things hard and on beat.", 24, "London"),
        ("VocalQueen", "Vocals", "Classically trained soprano.", 30, "Manchester"),
        ("SynthWizard", "Other", "Keyboards and synthesizers.", 22, "Bristol"),
        ("JazzPaws", "Piano", "Smooth jazz specialist.", 45, "Glasgow"),
        ("MetalHead", "Guitar", "Looking for heavy riffs only.", 21, "Birmingham"),
        ("GrooveMaster", "Bass", "Funk and soul groove master.", 33, "Liverpool"),
        ("BeatKeeper", "Drums", "Reliable session drummer.", 29, "Leeds"),
        ("Screamer123", "Vocals", "Death metal vocals.", 26, "Sheffield"),
        ("AcousticSoul", "Guitar", "Chill acoustic vibes.", 23, "Edinburgh"),
        ("RhythmKing", "Guitar", "Rhythm guitar is the backbone.", 40, "London"),
        ("TheGoldenReviewer", "Piano", "I review everyone!", 31, "Glasgow"), # Our Gold Badge tester
        ("TheSilverReviewer", "Bass", "I review some people.", 28, "Edinburgh"), # Our Silver Badge tester
        ("TheBronzeReviewer", "Drums", "I rarely review.", 25, "London"), # Our Bronze Badge tester
    ]
    
    musician_users = []
    for username, inst, bio, age, loc in musicians_data:
        u = add_user(username, "password123", f"{username}@test.com")
        add_musician(u, inst, bio, age, "", loc)
        musician_users.append(u)

    print("2. Creating Users & Bands...")
    bands_data = [
        ("SonicBoom", "Sonic Boom", "Loudest band in the UK.", "Glasgow"),
        ("VelvetUnderground2", "Velvet Underground 2", "Indie rock covers.", "Edinburgh"),
        ("TheMidnightHowlers", "The Midnight Howlers", "Blues and rock.", "Manchester"),
        ("NeonKnights", "Neon Knights", "80s Synth Pop.", "Bristol"),
        ("SymphonyOfDestruction", "Symphony of Destruction", "Thrash metal.", "Birmingham"),
        ("ChillWave", "Chill Wave", "Lo-Fi beats and live instruments.", "Leeds"),
        ("TheLocalLads", "The Local Lads", "Pub rock band.", "Liverpool"),
        ("ElectricEchoes", "Electric Echoes", "Shoegaze and ambient.", "London"),
    ]

    band_users = []
    bands = []
    for username, name, bio, loc in bands_data:
        u = add_user(username, "password123", f"{username}@test.com")
        b = add_band(u, name, loc, bio)
        band_users.append(u)
        bands.append(b)

    print("3. Creating 20 Gig Listings (Geocoding via Google Maps API in background)...")
    gigs_data = [
        (bands[0], "Lead Guitarist Needed ASAP", "Guitar", 5, True, "Our lead broke his arm. Need a fill-in!", "King Tuts, Glasgow"),
        (bands[0], "Session Drummer", "Drums", 14, False, "Need tracks recorded for our EP.", "Barrowland Ballroom, Glasgow"),
        (bands[1], "Indie Bassist", "Bass", 30, False, "Looking for a permanent member.", "Sneaky Pete's, Edinburgh"),
        (bands[2], "Blues Vocalist", "Vocals", 7, True, "Frontman needed for upcoming pub tour.", "The Deaf Institute, Manchester"),
        (bands[3], "Keyboard/Synth Player", "Other", 45, False, "Must love the 80s.", "The Fleece, Bristol"),
        (bands[4], "Thrash Metal Drummer", "Drums", 3, True, "Double kick pedal experience required.", "O2 Academy, Birmingham"),
        (bands[5], "Acoustic Guitarist", "Guitar", 20, False, "Chill coffee shop vibes.", "Brudenell Social Club, Leeds"),
        (bands[6], "Pub Singer", "Vocals", 10, True, "Singing covers for drunk crowds.", "The Cavern Club, Liverpool"),
        (bands[7], "Ambient Bass Player", "Bass", 60, False, "Must have lots of effect pedals.", "Camden Assembly, London"),
        (bands[1], "Rhythm Guitar", "Guitar", 15, False, "Need someone to hold down the chords.", "The Liquid Room, Edinburgh"),
        (bands[2], "Harmonica Player", "Other", 25, False, "Blues band needs some harp.", "Band on the Wall, Manchester"),
        (bands[4], "Screaming Vocals", "Vocals", 8, True, "Can you scream for 45 minutes straight?", "The Asylum, Birmingham"),
        (bands[0], "Touring Bassist", "Bass", 40, False, "UK tour coming up next month.", "O2 Academy Glasgow"),
        (bands[3], "Electronic Drummer", "Drums", 35, False, "Looking for Roland SPD-SX experience.", "Exchange, Bristol"),
        (bands[6], "Lead Singer", "Vocals", 12, True, "Need a charismatic frontman.", "O2 Academy Liverpool"),
        (bands[7], "Second Guitar", "Guitar", 50, False, "Adding depth to our sound.", "The Underworld, London"),
        (bands[5], "Saxophone", "Other", 18, False, "Jazz up our lo-fi beats.", "Belgrave Music Hall, Leeds"),
        (bands[1], "Backup Vocals", "Vocals", 22, False, "Harmonies are key.", "La Belle Angele, Edinburgh"),
        (bands[2], "Blues Piano", "Piano", 28, False, "Jerry Lee Lewis style.", "Albert Hall, Manchester"),
        (bands[0], "Heavy Metal Bass", "Bass", 6, True, "Must play with a pick.", "Cathouse Rock Club, Glasgow"),
    ]

    all_listings = []
    for band, title, inst, days_out, urgent, desc, loc in gigs_data:
        listing = add_listing(
            band=band, title=title, req_instruments=inst,
            deadline=date.today() + timedelta(days=days_out),
            is_urgent=urgent, description=desc, location=loc
        )
        all_listings.append(listing)

    print("4. Generating Badge Test Data (Auto-writing Reviews)...")
    # Grab our specific testing users
    gold_user = User.objects.get(username="TheGoldenReviewer")
    silver_user = User.objects.get(username="TheSilverReviewer")
    bronze_user = User.objects.get(username="TheBronzeReviewer")
    
    # We will review all the band users to rack up the count quickly
    for i in range(21): # Needs 20+ for Gold
        models.Review.objects.create(reviewer=gold_user, reviewee=band_users[i % len(band_users)], rating=5, comment="Great!")
    
    for i in range(12): # Needs 10+ for Silver
        models.Review.objects.create(reviewer=silver_user, reviewee=band_users[i % len(band_users)], rating=4, comment="Good!")
        
    for i in range(6):  # Needs 5+ for Bronze
        models.Review.objects.create(reviewer=bronze_user, reviewee=band_users[i % len(band_users)], rating=3, comment="Okay.")

    print("5. Generating Random Applications & Bookmarks...")
    # Apply GuitarHero99 to the first gig
    add_application(applicant=musician_users[0], listing=all_listings[0])
    add_application(applicant=musician_users[0], listing=all_listings[9])
    
    # Bookmark a gig for the Gold Reviewer so they have something in their dashboard
    all_listings[2].bookmarks.add(gold_user)

if __name__ == '__main__':
    print("Starting Mega Population Script... (This might take a minute due to Google Maps API limits)")
    
    # Optional: Clear the database before running to prevent duplicate clutter
    models.Application.objects.all().delete()
    models.Listing.objects.all().delete()
    models.Review.objects.all().delete()
    models.Band.objects.all().delete()
    models.Musician.objects.all().delete()
    User.objects.exclude(is_superuser=True).delete()
    
    populate()
    print("\nDatabase successfully populated! 🎉")