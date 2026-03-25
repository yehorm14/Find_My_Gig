from django.contrib import admin
from gigs.models import Musician, Band, Listing, Application, Review

# Register our models here, models will be visible on the admin panel

admin.site.register(Musician)
admin.site.register(Band)
admin.site.register(Listing)
admin.site.register(Application)
admin.site.register(Review)
