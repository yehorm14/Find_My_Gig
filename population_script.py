import os, django
from datetime import date


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'find_my_gig.settings')
django.setup()

import rango.models as models

from django.contrib.auth.models import User

def add_user(username, password, email, isAdmin = False):
    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    if created:
        user.set_password(password)
    if isAdmin:
        user.is_staff = True
        user.is_superuser = True
    user.save()
    return user

def add_musician(user, instruments, bio, media_link, location, profile_picture = ""):
    musician = models.Musician()
    musician.user = user
    musician.instruments = instruments
    musician.bio = bio
    musician.profile_picture = profile_picture
    musician.media_link = media_link
    musician.location = location

    musician.save()
    return musician

def add_band(user, band_name, location, bio, profile_picture = ""):
    band = models.Band()
    band.user = user
    band.name = band_name
    band.bio = bio
    band.profile_picture = profile_picture
    band.location = location

    band.save()
    return band

def add_review(reviwer, reviewee, rating, comment):
    review = models.Review()
    review.reviewer = reviwer
    review.reviewee = reviewee
    review.rating = rating
    review.comment = comment

    review.save()
    return review

def add_listing(band, title, req_instruments, deadline, is_urgent):
    listing = models.Listing()
    listing.band = band
    listing.title = title
    listing.req_instruments = req_instruments
    listing.deadline = deadline
    listing.is_urgent = is_urgent

    listing.save()
    return listing

def populate():
    users, musicians , bands , reviews , listings = [], [], [], [], []

    users.append(add_user("ButterMyBeefStick", "beepbop", "iLoveRedChairs@hotmail.com"))
    users.append(add_user("thierrycnf", "lolxd123", "sonicthegamer987@gmail.com", True))
    users.append(add_user("FuriousDestroyer", "AHHHHHHHH", "TheOneAboveAll@outlook.com"))


    musicians.append(add_musician(users[1], "Guitar", "Looking for a part-time position in a band", "", "Glasgow"))
    musicians.append(add_musician(users[2], "Drums", "Looking for a band that needs a drummer", "", "Glasgow"))

    bands.append(add_band(users[0], "Raging Demons", "Glasgow", "We're a hardcore heavy metal band based in Glasgow.  "
                                                                    "If you can handle some heat, we're your guys", ""))
    # bands.append(add_band(users[1], "Roaring Moon", "Glasgow", "This is a punk rock band that's loud, "
    #                                                                "proud and does everything at 200%", ""))

    reviews.append(add_review(users[0], users[1], 4, "Amazing guy. The best bassist you will ever meet."))

    listings.append(add_listing(bands[0], "Drummer needed! Glasgow.", "Drums", date(2026, 3, 9), True))



    # bands.append(add_band())

if __name__ == '__main__':
    print("Starting population script...")
    populate()