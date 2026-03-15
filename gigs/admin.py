from django.contrib import admin
from gigs.models import Musician, Band, Listing, Review

# Register our models here, models will be visible on the admin panel

admin.site.register(Musician)
admin.site.register(Band)
admin.site.register(Listing)
admin.site.register(Review)
