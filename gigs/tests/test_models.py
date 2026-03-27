from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
from gigs.models import Musician, Band, Listing, Review, Application, MediaLink, BandInterest

class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user1 = User.objects.create_superuser(username="thierrycnf", email="2850192F@student.gla.ac.uk", password="lol")
        cls.test_user2 = User.objects.create_user(username="notchface", email="cruzfru123@outlook.com", password="haha")
        
        for i in range(20):
            Review.objects.create(reviewer=cls.test_user1, reviewee=cls.test_user2, rating=5, comment="")

class MusicianTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_musician = Musician.objects.create(
            user=cls.test_user1, bio="Looking for a band that needs a guitar player",
            age=18, instruments="Guitar", location="Glasgow"
        )

    def test_username(self):
        self.assertEqual("thierrycnf", self.test_musician.user.username)

    def test_instrument(self):
        self.assertEqual("Guitar", self.test_musician.instruments)

    def test_community_badge(self):
        self.assertEqual(20, self.test_musician.user.reviews_written.count())

class BandTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_band = Band.objects.create(
            user=cls.test_user1, name="Gouging Fire", location="Glasgow", bio="Looking for a guitar player"
        )

    def test_band_name(self):
        self.assertEqual("Gouging Fire", self.test_band.name)

class ListingTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_band = Band.objects.create(user=cls.test_user1, name="Gouging Fire", location="Glasgow", bio="bio")
        cls.listing = Listing.objects.create(
            band=cls.test_band, title="Guitar player needed!", deadline=date(2026, 3, 24),
            is_urgent=True, description="Need drummer", location="Glasgow", req_instruments="Guitar"
        )

    def test_title(self):
        self.assertEqual("Guitar player needed!", self.listing.title)

    def test_is_urgent(self):
        self.assertTrue(self.listing.is_urgent)

class ReviewTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        

        cls.test_band = Band.objects.create(user=cls.test_user2, name="The Testtones", location="Glasgow", bio="Jazz")
        cls.test_listing = Listing.objects.create(
            band=cls.test_band, title="Jazz drummer needed", deadline=date(2026, 4, 1),
            is_urgent=False, 
            description="Need drummer", location="Glasgow", req_instruments="Drums"
        )
        
        cls.test_review = Review.objects.create(
            reviewer=cls.test_user1, 
            reviewee=cls.test_user2,
            listing=cls.test_listing, 
            rating=3, 
            comment="He's alright"
        )

    def test_reviewer_and_reviewee(self):
        self.assertEqual(self.test_user1, self.test_review.reviewer)
        self.assertEqual(self.test_user2, self.test_review.reviewee)
        
    def test_listing_attached(self):
        self.assertEqual(self.test_listing, self.test_review.listing)

    def test_validation_error(self):
        """EDGE CASE: Rating validation (max 5) must block invalid integers"""
        bad_review = Review(
            reviewer=self.test_user1, reviewee=self.test_user2, 
            listing=self.test_listing, rating=20, comment="Great!"
        )
        with self.assertRaises(ValidationError):
            bad_review.full_clean()

class ApplicationTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_band = Band.objects.create(user=cls.test_user1, name="Gouging Fire", location="Glasgow", bio="bio")
        cls.listing = Listing.objects.create(
            band=cls.test_band, title="Guitar player needed!", deadline=date(2026, 3, 24), 
            is_urgent=True, description="Need drummer", location="Glasgow", req_instruments="Guitar"
        )
        cls.time = timezone.now()
        cls.test_application = Application.objects.create(
            applicant=cls.test_user2, listing=cls.listing, date_applied=cls.time
        )

    def test_date(self):
        self.assertEqual(self.time.date(), self.test_application.date_applied.date())

    def test_status(self):
        self.assertEqual("Pending", self.test_application.status)

class MediaLinkTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.musician = Musician.objects.create(user=cls.test_user1, bio="Drummer", age=22, instruments="Drums", location="Glasgow")
        cls.media_link = MediaLink.objects.create(musician=cls.musician, url="https://youtube.com")

    def test_url(self):
        self.assertEqual("https://youtube.com", self.media_link.url)

class BandInterestTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.band = Band.objects.create(user=cls.test_user1, name="The Testtones", location="Glasgow", bio="Jazz")
        cls.musician = Musician.objects.create(user=cls.test_user2, bio="Bassist", age=25, instruments="Bass", location="Glasgow")
        cls.band_interest = BandInterest.objects.create(band=cls.band, musician=cls.musician, message="Audition?")

    def test_message(self):
        self.assertEqual("Audition?", self.band_interest.message)

class ModelMethodTests(BaseTestCase):
    """EDGE CASE: Verifying that custom model methods and string representations work correctly."""
    
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.band = Band.objects.create(user=cls.test_user1, name="The Beatles", location="Liverpool")
        cls.musician = Musician.objects.create(user=cls.test_user2, instruments="Drums", location="Liverpool")
        cls.listing = Listing.objects.create(
            band=cls.band, title="Need a drummer!", deadline=date(2026, 4, 1),
            is_urgent=False,
            description="Urgent", location="Liverpool", req_instruments="Drums"
        )
        cls.review = Review.objects.create(
            reviewer=cls.test_user2, reviewee=cls.test_user1, listing=cls.listing, rating=5, comment="Great!"
        )

    def test_band_str(self):
        """Verifies the __str__ method of the Band model."""
        self.assertEqual(str(self.band), "The Beatles")

    def test_musician_str(self):
        """Verifies the __str__ method of the Musician model."""
        self.assertEqual(str(self.musician), self.test_user2.username)

    def test_listing_str(self):
        """Verifies the __str__ method of the Listing model."""
        self.assertEqual(str(self.listing), "Need a drummer!")

    def test_review_str(self):
        """Verifies the __str__ method of the Review model formats the string correctly."""
        expected_str = f"Review by {self.test_user2.username} for {self.test_user1.username}"
        self.assertEqual(str(self.review), expected_str)

    def test_review_minimum_rating_validation(self):
        """EDGE CASE: Rating validation must block integers below 1."""
        bad_review = Review(
            reviewer=self.test_user1, reviewee=self.test_user2, 
            listing=self.listing, rating=0, comment="Terrible!"
        )
        with self.assertRaises(ValidationError):
            bad_review.full_clean()