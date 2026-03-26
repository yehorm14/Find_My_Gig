import django.core.exceptions
from django.test import TestCase
import population_script
from datetime import date
import gigs.models as models
from django.core.validators import MinValueValidator, MaxValueValidator
class MusicianTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = population_script.add_user("thierrycnf", "lol", "2850192F@student.gla.ac.uk", True)
        cls.test_musician = population_script.add_musician(cls.test_user, "Guitar",
                                                       "Looking for a band that needs a guitar player", 18,
                                                       "", "Glasgow")

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

class BandTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = population_script.add_user("thierrycnf",
                                                   "lol", "2850192F@student.gla.ac.uk", True)
        cls.test_band = population_script.add_band(cls.test_user, "Gouging Fire", "Glasgow",
                                              "Looking for a guitar player", "", )

    def test_band_name(self):
        self.assertEqual("Gouging Fire", self.test_band.name)

    def test_bio(self):
        self.assertEqual("Looking for a guitar player", self.test_band.bio)

    def test_location(self):
        self.assertEqual("Glasgow", self.test_band.location)

class ListingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = population_script.add_user("thierrycnf",
                                                   "lol", "2850192F@student.gla.ac.uk", True)
        cls.test_band = population_script.add_band(cls.test_user, "Gouging Fire", "Glasgow",
                                              "Looking for a guitar player", "", )
        cls.test_listing = population_script.add_listing(cls.test_band, "Guitar player needed!", "Guitar",
                                                         date(2026, 3, 24), True,
                                                         "Looking for a full-time drummer that has 3 years of experience",
                                                         "Glasgow")

    def test_title(self):
        self.assertEqual("Guitar player needed!", self.test_listing.title)

    def test_req_instruments(self):
        self.assertEquals("Guitar", self.test_listing.req_instruments)

    def test_deadline(self):
        self.assertEquals(date(2026, 3, 24), self.test_listing.deadline)

    def test_is_urgent(self):
        self.assertTrue(self.test_listing.is_urgent)

class ReviewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user1 = population_script.add_user("thierrycnf",
                                                   "lol", "2850192F@student.gla.ac.uk", True)
        cls.test_user2 = population_script.add_user("notchface",
                                                    "haha", "cruzfru123@outlook.com", False)
        cls.test_review = models.Review.objects.create(reviewer=cls.test_user1, reviewee=cls.test_user2, rating=3, comment="He's alright, what you get is what you see!")

    def test_reviewer(self):
        self.assertEqual(self.test_user1, self.test_review.reviewer)

    def test_reviewee(self):
        self.assertEqual(self.test_user2, self.test_review.reviewee)

    def test_rating(self):
        self.assertEqual(3, self.test_review.rating)

    def test_comment(self):
        self.assertEqual("He's alright, what you get is what you see!", self.test_review.comment)

    def validation_error(self):
        caught_error = False
        try:
            models.Review.objects.create(reviewer=self.test_user1, reviewee=self.test_user2, rating=20, comment="Great!")
        except django.core.exceptions.ValidationError:
            self.assertTrue(caught_error)