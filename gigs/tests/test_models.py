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
        
        # Create 20 reviews to test the community badge logic
        for i in range(20):
            Review.objects.create(reviewer=cls.test_user1, reviewee=cls.test_user2, rating=5, comment="")

class MusicianTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_musician = Musician.objects.create(
            user=cls.test_user1,
            bio="Looking for a band that needs a guitar player",
            age=18,
            instruments="Guitar",
            location="Glasgow"
        )

    def test_username(self):
        self.assertEqual("thierrycnf", self.test_musician.user.username)

    def test_email(self):
        self.assertEqual("2850192F@student.gla.ac.uk", self.test_musician.user.email)

    def test_admin(self):
        self.assertTrue(self.test_musician.user.is_staff)
        self.assertTrue(self.test_musician.user.is_superuser)

    def test_instrument(self):
        self.assertEqual("Guitar", self.test_musician.instruments)

    def test_location(self):
        self.assertEqual("Glasgow", self.test_musician.location)

    def test_bio(self):
        self.assertEqual("Looking for a band that needs a guitar player", self.test_musician.bio)

    def test_age(self):
        self.assertEqual(18, self.test_musician.age)

    def test_community_badge(self):
        self.assertEqual(20, self.test_musician.user.reviews_written.count())

class BandTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_band = Band.objects.create(
            user=cls.test_user1,
            name="Gouging Fire",
            location="Glasgow",
            bio="Looking for a guitar player"
        )

    def test_band_name(self):
        self.assertEqual("Gouging Fire", self.test_band.name)

    def test_bio(self):
        self.assertEqual("Looking for a guitar player", self.test_band.bio)

    def test_location(self):
        self.assertEqual("Glasgow", self.test_band.location)

class ListingTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_band = Band.objects.create(
            user=cls.test_user1, name="Gouging Fire", location="Glasgow", bio="Looking for a guitar player"
        )
        cls.listing = Listing.objects.create(
            band=cls.test_band,
            title="Guitar player needed!",
            deadline=date(2026, 3, 24),
            is_urgent=True,
            description="Looking for a full-time drummer that has 3 years of experience",
            location="Glasgow",
            req_instruments="Guitar"
        )

    def test_title(self):
        self.assertEqual("Guitar player needed!", self.listing.title)

    def test_req_instruments(self):
        self.assertEqual("Guitar", self.listing.req_instruments)

    def test_deadline(self):
        self.assertEqual(date(2026, 3, 24), self.listing.deadline)

    def test_is_urgent(self):
        self.assertTrue(self.listing.is_urgent)

    def test_description(self):
        self.assertEqual("Looking for a full-time drummer that has 3 years of experience", self.listing.description)

    def test_location(self):
        self.assertEqual("Glasgow", self.listing.band.location)

class ReviewTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_review = Review.objects.create(
            reviewer=cls.test_user1, 
            reviewee=cls.test_user2, 
            rating=3, 
            comment="He's alright, what you get is what you see!"
        )

    def test_reviewer(self):
        self.assertEqual(self.test_user1, self.test_review.reviewer)

    def test_reviewee(self):
        self.assertEqual(self.test_user2, self.test_review.reviewee)

    def test_rating(self):
        self.assertEqual(3, self.test_review.rating)

    def test_comment(self):
        self.assertEqual("He's alright, what you get is what you see!", self.test_review.comment)

    def test_validation_error(self):
        """Tests that rating validation (max 5) works correctly using full_clean"""
        bad_review = Review(reviewer=self.test_user1, reviewee=self.test_user2, rating=20, comment="Great!")
        with self.assertRaises(ValidationError):
            bad_review.full_clean()

class ApplicationTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_band = Band.objects.create(
            user=cls.test_user1, name="Gouging Fire", location="Glasgow", bio="Looking for a guitar player"
        )
        cls.listing = Listing.objects.create(
            band=cls.test_band, title="Guitar player needed!", deadline=date(2026, 3, 24), 
            is_urgent=True, description="Need drummer", location="Glasgow", req_instruments="Guitar"
        )
        cls.time = timezone.now()
        cls.test_application = Application.objects.create(
            applicant=cls.test_user2,
            listing=cls.listing,
            date_applied=cls.time
        )

    def test_applicant(self):
        self.assertEqual(self.test_user2, self.test_application.applicant)

    def test_listing(self):
        self.assertEqual(self.listing, self.test_application.listing)

    def test_date(self):
        self.assertEqual(self.time.date(), self.test_application.date_applied.date())

    def test_status(self):
        self.assertEqual("Pending", self.test_application.status)


class MediaLinkTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Create a musician to attach the link to
        cls.musician = Musician.objects.create(
            user=cls.test_user1,
            bio="Drummer looking for a gig",
            age=22,
            instruments="Drums",
            location="Glasgow"
        )
        # Create the media link
        cls.media_link = MediaLink.objects.create(
            musician=cls.musician,
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )

    def test_musician(self):
        self.assertEqual(self.musician, self.media_link.musician)

    def test_url(self):
        self.assertEqual("https://www.youtube.com/watch?v=dQw4w9WgXcQ", self.media_link.url)


class BandInterestTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Create a band and a musician to interact
        cls.band = Band.objects.create(
            user=cls.test_user1, 
            name="The Testtones", 
            location="Glasgow", 
            bio="Jazz band"
        )
        cls.musician = Musician.objects.create(
            user=cls.test_user2,
            bio="Jazz bassist",
            age=25,
            instruments="Bass",
            location="Glasgow"
        )
        # Create the reach-out message
        cls.band_interest = BandInterest.objects.create(
            band=cls.band,
            musician=cls.musician,
            message="We loved your profile, do you want to audition?"
        )

    def test_band(self):
        self.assertEqual(self.band, self.band_interest.band)

    def test_musician(self):
        self.assertEqual(self.musician, self.band_interest.musician)

    def test_message(self):
        self.assertEqual("We loved your profile, do you want to audition?", self.band_interest.message)

    def test_created_at(self):
        self.assertIsNotNone(self.band_interest.created_at)