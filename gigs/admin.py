from django.contrib import admin
from gigs.models import Musician, Band, Listing, Application, Review, MediaLink, BandInterest

# ==========================================
# --- USER PROFILES ---
# ==========================================

@admin.register(Musician)
class MusicianAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'age', 'instruments')
    search_fields = ('user__username', 'location', 'instruments')

@admin.register(Band)
class BandAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'location')
    search_fields = ('name', 'location')

# ==========================================
# --- GIGS & APPLICATIONS ---
# ==========================================

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'band', 'deadline', 'is_urgent', 'location')
    list_filter = ('is_urgent', 'deadline')
    search_fields = ('title', 'band__name', 'location')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'listing', 'status', 'date_applied')
    list_filter = ('status', 'date_applied')

# ==========================================
# --- INTERACTIONS & MEDIA ---
# ==========================================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'reviewee', 'rating')
    list_filter = ('rating',)

@admin.register(BandInterest)
class BandInterestAdmin(admin.ModelAdmin):
    list_display = ('band', 'musician', 'created_at')

@admin.register(MediaLink)
class MediaLinkAdmin(admin.ModelAdmin):
    list_display = ('musician', 'url')