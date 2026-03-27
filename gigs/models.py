import logging
import requests

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

logger = logging.getLogger(__name__)

# ==========================================
# MIXINS & ABSTRACT CLASSES
# ==========================================

class ReviewBadgeMixin:
    """
    Mixin to provide dynamic community badges based on review counts.
    Requires the model to have a OneToOneField to the User model.
    """
    @property
    def community_badge(self):
        """
        Dynamically calculates the user's community badge based on 
        the number of reviews they have submitted.
        """
        if not hasattr(self, 'user'):
            return None
            
        review_count = self.user.reviews_written.count()
        
        if review_count >= 20:
            return {'level': 'Gold', 'color': '#FFD700', 'text': 'Gold Reviewer 🌟'}
        elif review_count >= 10:
            return {'level': 'Silver', 'color': '#C0C0C0', 'text': 'Silver Reviewer 🥈'}
        elif review_count >= 5:
            return {'level': 'Bronze', 'color': '#CD7F32', 'text': 'Bronze Reviewer 🥉'}
        
        return None


# ==========================================
# USER PROFILE MODELS
# ==========================================

class Musician(ReviewBadgeMixin, models.Model):
    """
    Profile model for individual musicians.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    instruments = models.CharField(max_length=100)
    bio = models.CharField(max_length=500)
    age = models.IntegerField(null=True, blank=True)

    profile_picture = models.ImageField(
        upload_to='profile_images', 
        blank=True
    )
    media_link = models.URLField(blank=True)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


class Band(ReviewBadgeMixin, models.Model):
    """
    Profile model for bands seeking musicians or gigs.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    bio = models.CharField(max_length=500)
    profile_picture = models.ImageField(
        upload_to='profile_images', 
        blank=True
    )

    def __str__(self):
        return self.name


# ==========================================
# GIG & LISTING MODELS
# ==========================================

class Listing(models.Model):
    """
    Represents a specific gig or open position posted by a Band.
    """
    band = models.ForeignKey(Band, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    req_instruments = models.CharField(max_length=100)
    deadline = models.DateField()
    is_urgent = models.BooleanField()
    description = models.TextField(max_length=1000, default="No description provided.") 
    location = models.CharField(max_length=100, default="TBC") 
    bookmarks = models.ManyToManyField(User, related_name='saved_gigs', blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to automatically fetch 
        and save latitude and longitude using the Google Maps API.
        """
        if self.location and not self.latitude:
            try:
                api_key = settings.GOOGLE_MAPS_BACKEND_KEY
                url = (
                    f"https://maps.googleapis.com/maps/api/geocode/json"
                    f"?address={self.location}&key={api_key}"
                )
                
                response = requests.get(url, timeout=5).json()

                if response.get('status') == 'OK':
                    geometry = response['results'][0]['geometry']['location']
                    self.latitude = geometry['lat']
                    self.longitude = geometry['lng']
                else:
                    error_msg = response.get('error_message', 'No specific error message provided')
                    logger.error(f"Geocoding failed for '{self.location}': {response.get('status')} - {error_msg}")
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Network error during geocoding for '{self.location}': {e}")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# ==========================================
# INTERACTION & RELATIONSHIP MODELS
# ==========================================

class Application(models.Model):
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications_sent")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="applications_received")
    date_applied = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f"{self.applicant.username} applied to {self.listing.title}"


class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_written")
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_received")
    rating = models.IntegerField(validators=[
        MinValueValidator(0), 
        MaxValueValidator(5)
    ])
    comment = models.CharField(max_length=200)

    def __str__(self):
        return self.comment


class BandInterest(models.Model):
    band = models.ForeignKey(Band, on_delete=models.CASCADE)
    musician = models.ForeignKey(Musician, on_delete=models.CASCADE, related_name='received_interests')
    message = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.band.name} interested in {self.musician.user.username}"


# ==========================================
# MEDIA MODELS
# ==========================================

class MediaLink(models.Model):
    musician = models.ForeignKey(Musician, on_delete=models.CASCADE, related_name='media_links')
    url = models.URLField()

    def __str__(self):
        return self.url