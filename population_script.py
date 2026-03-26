import os
import random
from datetime import timedelta
from django.utils import timezone

# Set up Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'find_my_gig.settings')
import django
django.setup()

import requests
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from gigs.models import Musician, Band, Listing

# ==========================================
# 1. HELPER DATA & FUNCTIONS
# ==========================================
INSTRUMENTS = ['Guitar', 'Bass', 'Drums', 'Vocals', 'Keys/Synth', 'Other']

UK_VENUES = [
    {"name": "King Tut's Wah Wah Hut", "city": "Glasgow", "lat": 55.8629, "lng": -4.2652},
    {"name": "Barrowland Ballroom", "city": "Glasgow", "lat": 55.8546, "lng": -4.2396},
    {"name": "SWG3", "city": "Glasgow", "lat": 55.8645, "lng": -4.2995},
    {"name": "Sneaky Pete's", "city": "Edinburgh", "lat": 55.9488, "lng": -3.1895},
    {"name": "The Liquid Room", "city": "Edinburgh", "lat": 55.9482, "lng": -3.1932},
    {"name": "Albert Hall", "city": "Manchester", "lat": 53.4785, "lng": -2.2492},
    {"name": "The Deaf Institute", "city": "Manchester", "lat": 53.4704, "lng": -2.2366},
    {"name": "YES", "city": "Manchester", "lat": 53.4716, "lng": -2.2372},
    {"name": "The Roundhouse", "city": "London", "lat": 51.5430, "lng": -0.1492},
    {"name": "O2 Academy Brixton", "city": "London", "lat": 51.4650, "lng": -0.1150},
    {"name": "KOKO", "city": "London", "lat": 51.5348, "lng": -0.1384},
    {"name": "The Underworld", "city": "London", "lat": 51.5388, "lng": -0.1424},
    {"name": "Brudenell Social Club", "city": "Leeds", "lat": 53.8116, "lng": -1.5721},
    {"name": "Thekla (Boat Venue)", "city": "Bristol", "lat": 51.4485, "lng": -2.5925},
    {"name": "The Fleece", "city": "Bristol", "lat": 51.4526, "lng": -2.5901},
    {"name": "The Sunflower Lounge", "city": "Birmingham", "lat": 52.4770, "lng": -1.8988},
    {"name": "The Cavern Club", "city": "Liverpool", "lat": 53.4065, "lng": -2.9876},
    {"name": "The Cluny", "city": "Newcastle", "lat": 54.9723, "lng": -1.5838},
    {"name": "The Leadmill", "city": "Sheffield", "lat": 53.3766, "lng": -1.4641},
    {"name": "Rock City", "city": "Nottingham", "lat": 52.9554, "lng": -1.1528},
    {"name": "The Limelight", "city": "Belfast", "lat": 54.5936, "lng": -5.9261},
    {"name": "Clwb Ifor Bach", "city": "Cardiff", "lat": 51.4807, "lng": -3.1812}
]

BAND_NAMES = [
    "The Midnight Howlers", "Crimson Riot", "Neon Syndicate", "The Jazz Cats", 
    "Glasgow Symphony", "Echoes of Eden", "Velvet Thunder", "Rusty Strings", 
    "The Underground", "Sonic Boom"
]

BAND_BIOS = [
    "We are a high-energy alt-rock outfit blending 90s grunge with modern indie sensibilities. Known for our chaotic live shows and tight rhythm section, we're currently recording our second EP.",
    "A 5-piece funk and soul collective playing exclusively vintage gear. We do mostly weddings and corporate gigs, meaning the pay is great but the standards are exceptionally high.",
    "Formed in a damp university basement last year, we play loud, fast punk rock. We don't care about perfect technique; we just want aggressive energy and people who can jump around on stage.",
    "An experimental synth-pop duo heavily influenced by Depeche Mode. We rely heavily on backing tracks and MIDI triggers, so timing to a click track is absolutely essential.",
    "We are a gigging blues-rock trio. Think Stevie Ray Vaughan meets The Black Keys. We gig 2-3 times a month locally and are looking to expand our sound for an upcoming summer festival run.",
    "Traditional folk and acoustic group. We feature fiddles, mandolins, and acoustic guitars. Our vibe is very laid back, focusing on rich vocal harmonies and storytelling.",
    "A working cover band playing all the hits from the 70s to today. We treat this like a business: show up on time, know your parts, get paid. We play every weekend without fail.",
    "Heavy metal/metalcore band with heavy breakdowns and melodic choruses. We practice twice a week and are booking a 10-day UK tour for next spring. Dedication is our number one requirement.",
    "An instrumental post-rock band focusing on atmospheric soundscapes and heavy crescendos. Our songs are 10 minutes long and require a lot of dynamic control and effects pedals.",
    "A modern country and Americana band. We write original music but throw in some Johnny Cash and Dolly Parton to keep the bar crowds happy. Looking for musicians who know how to serve the song."
]

MUSICIAN_BIOS = [
    "Classically trained but raised on classic rock. I've got 10 years of live gigging experience, pro gear, and my own transport. Looking for serious, paid projects only.",
    "Self-taught and strictly play by ear. I might not know the music theory behind it, but I can groove in the pocket better than anyone. Influences include Vulfpeck and RHCP.",
    "I'm a music student at the local conservatory looking to branch out from jazz and classical. My sight-reading is flawless and I can learn a 20-song setlist in a weekend.",
    "Total gear nerd here. I have a massive pedalboard and love creating weird, ambient soundscapes. I'm not looking to play 12-bar blues; I want to join an indie/shoegaze project.",
    "Frontman with 5 years of experience commanding a crowd. I can hit the high notes, but more importantly, I know how to hype up an audience. I come with my own in-ear monitors.",
    "Just moved to the area and looking to jam! I've been playing in bedroom projects for a few years and finally want to get on stage. Easy going, quick learner, and no ego.",
    "Session musician available for studio work and live fill-ins. I charge reasonable rates, show up perfectly prepared, and don't drink on the job. Let me know what you need.",
    "I play aggressive, fast, and loud. If your band plays doom metal, thrash, or hardcore, I'm your person. I hit hard and have the calluses to prove it.",
    "Acoustic player primarily, specializing in fingerstyle and folk. I have a great home recording setup so I'm very open to remote collaboration and writing sessions.",
    "Rhythm is my life. I play strictly to a click track and lock in perfectly with the bass. I have a full DW kit and my own transportation. Looking for an established gigging band."
]

GIG_TITLES = [
    "Looking for a shredder!", "Emergency fill-in needed", "Wedding band needs vocals",
    "Studio bassist wanted", "Drummer for Europe tour", "Acoustic guitarist for cafe",
    "Pianist for corporate event", "Seeking harsh vocalist", "Need a reliable bassist",
    "Synth player wanted for 80s cover band"
]

GIG_DESCRIPTIONS = [
    "URGENT: Our lead player broke their wrist and we have a headline show next Saturday. We play a mix of modern indie and classic rock. Paid gig (£150). Must learn 10 songs by Thursday.",
    "We are a working wedding band looking to replace a departing member. You must have pro gear, formal stage wear, and reliable transport. We gig 40+ weekends a year. Serious inquiries only.",
    "Looking for someone to complete our lineup for a 2-week UK tour supporting a major national act. All travel and accommodation paid for, plus a nightly per diem. Must have a valid passport.",
    "Starting a brand new original project in the vein of Paramore and Fall Out Boy. We have a rehearsal space locked down and 5 demos fully written. Just need the right person to bring them to life.",
    "Need a session player for a 2-day studio booking next month. We will send you the scratch tracks and sheet music in advance. Standard MU rates apply. Send links to previous studio work.",
    "Laid back acoustic duo looking to become a trio. We play quiet corner pubs on Sunday afternoons. The money isn't great but the beer is free and the vibes are excellent.",
    "Looking for a hired gun for a corporate function. It's a 3-hour set of standard Top 40 covers. £200 for the night. You must be able to dress sharply and act professionally.",
    "We are going into the studio next week and our current member just bailed. We need someone who can learn fast, write their own parts on the fly, and handle the pressure of tracking to a click.",
    "Looking for a permanent addition to our metal project. Must be capable of playing at 200 BPM and have stage presence. We practice every Tuesday and Thursday without fail.",
    "Experimental jazz/funk fusion band looking for a missing piece. You must be comfortable with odd time signatures, extended improvisation, and reading complex charts."
]

def download_image(seed_text, size=300):
    """Downloads a unique random image based on a text seed."""
    url = f"https://picsum.photos/seed/{seed_text}/{size}/{size}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return ContentFile(response.content, name=f"{seed_text}.jpg")
    except Exception as e:
        print(f"Warning: Could not download image for {seed_text}.")
    return None

def clear_data():
    """Clears existing users to prevent duplicates."""
    print("🗑️ Clearing old data...")
    User.objects.all().delete()
    print("✅ Database cleared.\n")


# ==========================================
# 2. POPULATION SCRIPT
# ==========================================
def populate():
    clear_data()
    
    bands_list = []
    
    # --- CREATE 10 BANDS ---
    print("🎸 Creating 10 Bands (Downloading unique images...)")
    for i in range(10):
        username = f"band_user_{i+1}"
        band_name = BAND_NAMES[i]
        
        # Pick a random "home base" from our real venues list to assign them a city
        home_base = random.choice(UK_VENUES)
        
        user = User.objects.create_user(username=username, email=f"{username}@test.com", password="Password123!")
        user.first_name = "Band"
        user.last_name = f"Manager {i+1}"
        user.save()
        
        band = Band.objects.create(
            user=user,
            name=band_name,
            bio=random.choice(BAND_BIOS),
            location=home_base['city'],
        )
        
        image_file = download_image(f"band_unique_seed_{i}")
        if image_file:
            band.profile_picture.save(f"band_{i}.jpg", image_file)
            
        bands_list.append(band)
        print(f"  - Created Band: {band.name} (from {band.location})")

    print("\n")


    # --- CREATE 30 MUSICIANS ---
    print("🥁 Creating 30 Musicians (Downloading unique images...)")
    for i in range(30):
        username = f"musician_{i+1}"
        
        user = User.objects.create_user(username=username, email=f"{username}@test.com", password="Password123!")
        user.first_name = f"Talent"
        user.last_name = f"Num{i+1}"
        user.save()
        
        musician = Musician.objects.create(
            user=user,
            bio=random.choice(MUSICIAN_BIOS),
            age=random.randint(18, 55),
            instruments=random.choice(INSTRUMENTS),
        )
        
        image_file = download_image(f"musician_unique_seed_{i}")
        if image_file:
            musician.profile_picture.save(f"musician_{i}.jpg", image_file)
            
        print(f"  - Created Musician: @{user.username} ({musician.instruments})")

    print("\n")


    # --- CREATE 30 GIG LISTINGS ---
    print("📅 Creating 30 Gig Listings (Assigning to Real UK Venues!)...")
    for i in range(30):
        owning_band = random.choice(bands_list)
        future_date = timezone.now() + timedelta(days=random.randint(1, 60))
        
        venue = random.choice(UK_VENUES)
        
        listing = Listing.objects.create(
            band=owning_band,
            title=random.choice(GIG_TITLES),
            req_instruments=random.choice(INSTRUMENTS),
            deadline=future_date,
            description=random.choice(GIG_DESCRIPTIONS),
            
            # Format: "King Tut's Wah Wah Hut, Glasgow"
            location=f"{venue['name']}, {venue['city']}",
            is_urgent=random.choice([True, False, False]),
            
            # Real-world Google Maps coordinates!
            latitude=venue['lat'],
            longitude=venue['lng']
        )
        print(f"  - Created Gig: '{listing.title}' at {venue['name']}")

    print("\n🎉 POPULATION COMPLETE! 🎉")
    print("Log in with any username (e.g., 'musician_1' or 'band_user_1') and password: Password123!")

if __name__ == '__main__':
    populate()