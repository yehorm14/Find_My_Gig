from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
import json

from gigs.models import Musician, Band, Listing, Application, Review

class ViewBaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.band_user = User.objects.create_user(username="banduser", email="band@test.com", password="pass123")
        cls.musician_user = User.objects.create_user(username="musicianuser", email="musician@test.com", password="pass123")

        cls.band = Band.objects.create(user=cls.band_user, name="Test Band", location="Glasgow", bio="Band bio")
        cls.musician = Musician.objects.create(user=cls.musician_user, bio="Musician bio", age=21, instruments="Guitar", location="Glasgow")

        cls.listing = Listing.objects.create(
            band=cls.band, title="Guitarist needed", deadline=date(2026, 4, 1),
            is_urgent=False, description="Need a guitarist", location="Glasgow", req_instruments="Guitar"
        )

class PublicViewTests(ViewBaseTestCase):
    def test_home_page_loads_for_anonymous_user(self):
        response = self.client.get(reverse('gigs:home'))
        self.assertEqual(response.status_code, 200)

    def test_gig_detail_invalid_id_returns_404(self):
        """EDGE CASE: Looking up a gig that does not exist"""
        response = self.client.get(reverse('gigs:gig_detail', args=[999999]))
        self.assertEqual(response.status_code, 404)

class FilterTests(ViewBaseTestCase):
    def test_filter_gigs_by_instrument_match(self):
        """EDGE CASE: Using the search filter should return matching gigs"""
        response = self.client.get(reverse('gigs:gig_listings'), {'instrument': 'Guitar'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.listing, response.context['gigs'])

    def test_filter_gigs_by_instrument_no_match(self):
        """EDGE CASE: Using the search filter should exclude non-matching gigs"""
        response = self.client.get(reverse('gigs:gig_listings'), {'instrument': 'Drums'})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.listing, response.context['gigs'])

class AjaxActionTests(ViewBaseTestCase):
    def setUp(self):
        self.client.login(username='musicianuser', password='pass123')

    def test_apply_for_gig_success(self):
        response = self.client.post(reverse('gigs:apply_gig', args=[self.listing.id]))
        self.assertEqual(response.json()['success'], True)
        self.assertTrue(Application.objects.filter(applicant=self.musician_user, listing=self.listing).exists())

    def test_duplicate_application_blocked(self):
        """EDGE CASE: Spamming the apply button should return an error"""
        Application.objects.create(applicant=self.musician_user, listing=self.listing)
        response = self.client.post(reverse('gigs:apply_gig', args=[self.listing.id]))
        self.assertEqual(response.json()['success'], False)
        self.assertEqual(response.json()['error'], 'already_applied')

    def test_invalid_http_method_blocked(self):
        """EDGE CASE: Sending a GET request to an AJAX POST endpoint"""
        response = self.client.get(reverse('gigs:apply_gig', args=[self.listing.id]))
        self.assertEqual(response.json()['success'], False)
        self.assertEqual(response.json()['error'], 'Invalid request')

    def test_save_gig_bookmark(self):
        response = self.client.post(reverse('gigs:save_gig', args=[self.listing.id]))
        self.assertEqual(response.json()['success'], True)
        self.assertTrue(self.listing.bookmarks.filter(id=self.musician_user.id).exists())

class ReviewViewTests(ViewBaseTestCase):
    def setUp(self):
        self.client.login(username='musicianuser', password='pass123')

    def test_submit_valid_review(self):
        response = self.client.post(reverse('gigs:submit_review', args=[self.listing.id]), data={
            'rating': '5',
            'comment': 'Awesome band!'
        })
        self.assertEqual(response.status_code, 302) 
        self.assertTrue(Review.objects.filter(reviewer=self.musician_user, listing=self.listing).exists())

    def test_duplicate_review_blocked(self):
        """EDGE CASE: Submitting two reviews for the exact same gig is forbidden"""
        Review.objects.create(reviewer=self.musician_user, reviewee=self.band_user, listing=self.listing, rating=4, comment="Good")
        
        response = self.client.post(reverse('gigs:submit_review', args=[self.listing.id]), data={
            'rating': '5',
            'comment': 'I am trying to review them again!'
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.filter(reviewer=self.musician_user, listing=self.listing).count(), 1)


class SecurityViewTests(TestCase):
    """EDGE CASE: Verifying that unauthenticated users are blocked from protected views."""
    
    @classmethod
    def setUpTestData(cls):
        cls.band_user = User.objects.create_user(username="secureband", email="band@test.com", password="pass")
        cls.band = Band.objects.create(user=cls.band_user, name="Secure Band", location="Glasgow")
        cls.listing = Listing.objects.create(
            band=cls.band, title="Gig", deadline=date(2026, 4, 1),
            is_urgent=False,
            description="Desc", location="Glasgow", req_instruments="Guitar"
        )

    def test_dashboard_requires_login(self):
        """EDGE CASE: Anonymous user trying to access the dashboard"""
        response = self.client.get(reverse('gigs:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('gigs:login')))

    def test_create_gig_requires_login(self):
        """EDGE CASE: Anonymous user trying to load the create gig form"""
        response = self.client.get(reverse('gigs:create_gig'))
        self.assertEqual(response.status_code, 302)

    def test_submit_review_requires_login(self):
        """EDGE CASE: Anonymous user trying to submit a review directly via URL"""
        response = self.client.post(reverse('gigs:submit_review', args=[self.listing.id]), data={
            'rating': '5',
            'comment': 'Hacked review!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.exists())

    def test_ajax_apply_requires_login(self):
        """EDGE CASE: Anonymous user trying to hit the apply endpoint"""
        response = self.client.post(reverse('gigs:apply_gig', args=[self.listing.id]))
        self.assertEqual(response.json()['success'], False)
        self.assertEqual(response.json()['error'], 'not_logged_in')

class AccountManagementTests(TestCase):
    """EDGE CASE: Verifying that users can successfully register and update their profiles."""
    
    def test_signup_creates_musician_profile(self):
        """EDGE CASE: Submitting the signup form as a 'musician' should create both a User and a Musician."""
        data = {
            'username': 'new_drummer',
            'first_name': 'Test',       
            'last_name': 'Musician',    
            'email': 'drummer@test.com',
            'password1': 'SecurePassword123!',  
            'password2': 'SecurePassword123!',  
            'location': 'Glasgow',             
            'user_type': 'musician'
        }
        response = self.client.post(reverse('gigs:signup'), data=data)
        
        if response.status_code == 200:
            print("\nSIGNUP ERRORS (Musician):", response.context['user_form'].errors)

        self.assertEqual(response.status_code, 302) 
        self.assertTrue(User.objects.filter(username='new_drummer').exists())
        self.assertTrue(Musician.objects.filter(user__username='new_drummer').exists())

    def test_signup_creates_band_profile(self):
        """EDGE CASE: Submitting the signup form as a 'band' should create both a User and a Band."""
        data = {
            'username': 'new_manager',
            'first_name': 'Test',       
            'last_name': 'Manager',     
            'email': 'manager@test.com',
            'password1': 'SecurePassword123!',
            'password2': 'SecurePassword123!',
            'location': 'Glasgow',
            'user_type': 'band',
            'band_name': 'The Rockers'
        }
        response = self.client.post(reverse('gigs:signup'), data=data)

        if response.status_code == 200:
            print("\nSIGNUP ERRORS (Band):", response.context['user_form'].errors)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Band.objects.filter(name='The Rockers').exists())


class DataDeletionTests(ViewBaseTestCase):
    """EDGE CASE: Verifying that users can safely delete their data without server crashes."""
    
    def test_withdraw_application(self):
        """EDGE CASE: Withdrawing an application should remove the database record."""
        self.client.login(username='musicianuser', password='pass123')
        Application.objects.create(applicant=self.musician_user, listing=self.listing)
        
      
        response = self.client.post(reverse('gigs:withdraw_gig', args=[self.listing.id]))
        self.assertEqual(response.json()['success'], True)
        self.assertFalse(Application.objects.filter(applicant=self.musician_user, listing=self.listing).exists())

    def test_delete_listing(self):
        """EDGE CASE: A band deleting their own listing."""
        self.client.login(username='banduser', password='pass123')
        
        response = self.client.post(reverse('gigs:delete_listing', args=[self.listing.id]))
        self.assertEqual(response.json()['success'], True)
        self.assertFalse(Listing.objects.filter(id=self.listing.id).exists())