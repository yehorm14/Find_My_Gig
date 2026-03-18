import os, django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'find_my_gig.settings')
django.setup()

import gigs.models as models
from django.contrib.auth.models import User

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

def add_review(reviewer, reviewee, rating, comment):
    review, created = models.Review.objects.get_or_create(reviewer=reviewer, reviewee=reviewee, defaults={
        'rating': rating,
        'comment': comment
    })
    return review


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


def populate():
    users, musicians, bands, reviews, listings = [], [], [], [], []


    users.append(add_user("ButterMyBeefStick", "beepbop", "iLoveRedChairs@hotmail.com"))
    users.append(add_user("thierrycnf", "lolxd123", "sonicthegamer987@gmail.com", True))
    users.append(add_user("FuriousDestroyer", "AHHHHHHHH", "TheOneAboveAll@outlook.com"))

    # 2. Create Musicians (Now includes Age)
    musicians.append(add_musician(users[1], "Guitar", "Looking for a part-time position in a band", 24, "", "Glasgow"))
    musicians.append(add_musician(users[2], "Drums", "Looking for a band that needs a drummer", 28, "", "Glasgow"))

    # 3. Create Bands
    bands.append(add_band(users[0], "Raging Demons", "Glasgow", "We're a hardcore heavy metal band based in Glasgow. If you can handle some heat, we're your guys", ""))

    # 4. Create Reviews
    reviews.append(add_review(users[0], users[1], 4, "Amazing guy. The best bassist you will ever meet."))

    # 5. Create Listings (Now includes Description and Location)
    listings.append(add_listing(
        band=bands[0], 
        title="Drummer needed! Glasgow.", 
        req_instruments="Drums", 
        deadline=date(2026, 3, 9), 
        is_urgent=True,
        description="Our previous drummer spontaneously combusted. We need a new one ASAP to play a gig at King Tuts.",
        location="King Tuts, Glasgow"
    ))

    # 6. Create an Application (So FuriousDestroyer has something on his dashboard!)
    add_application(applicant=users[2], listing=listings[0])

if __name__ == '__main__':
    print("Starting population script...")
    populate()
    print("Database successfully populated! 🎉")