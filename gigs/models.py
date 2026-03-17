from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

# Create your models here.
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

    def __str__(self):
        return self.title


class Application(models.Model):
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications_sent")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="applications_received")
    date_applied = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending') # Can be Pending, Accepted, Rejected

    def __str__(self):
        return f"{self.applicant.username} applied to {self.listing.title}"

class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_written")
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews_received")
    rating = models.IntegerField()
    comment = models.CharField(max_length=200)

    def __str__(self):
        return self.comment