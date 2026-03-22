import logging
import requests
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

logger = logging.getLogger(__name__)

class Musician(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    instruments = models.CharField(max_length=100)
    bio = models.CharField(max_length=500)
    age = models.IntegerField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_images', blank=True)
    media_link = models.URLField(blank=True)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class Band(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    bio = models.CharField(max_length=500)
    profile_picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        return self.name

class Listing(models.Model):
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
        # 1. Logic to check if geocoding is needed
        if self.location and not self.latitude:
            try:
                api_key = settings.GOOGLE_MAPS_API_KEY
                url = f"https://maps.googleapis.com/maps/api/geocode/json?address={self.location}&key={api_key}"
                
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

        # 2. Save the instance
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

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
    rating = models.IntegerField()
    comment = models.CharField(max_length=200)

    def __str__(self):
        return self.comment