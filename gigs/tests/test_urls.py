from django.test import SimpleTestCase
from django.urls import reverse, resolve
from gigs import views

class TestUrls(SimpleTestCase):
    """EDGE CASE: Verifying that URL routing resolves to the correct view functions."""
    
    def test_home_url_resolves(self):
        url = reverse('gigs:home')
        self.assertEqual(resolve(url).func, views.home)

    def test_gig_listings_url_resolves(self):
        url = reverse('gigs:gig_listings')
        self.assertEqual(resolve(url).func, views.gig_listings)

    def test_gig_detail_url_resolves(self):
        url = reverse('gigs:gig_detail', args=[1])
        self.assertEqual(resolve(url).func, views.gig_detail)

    def test_create_gig_url_resolves(self):
        url = reverse('gigs:create_gig')
        self.assertEqual(resolve(url).func, views.create_gig)

    def test_dashboard_url_resolves(self):
        url = reverse('gigs:dashboard')
        self.assertEqual(resolve(url).func, views.dashboard)

    def test_apply_gig_ajax_url_resolves(self):
        url = reverse('gigs:apply_gig', args=[5])
        self.assertEqual(resolve(url).func, views.apply_gig)
        
    def test_submit_review_url_resolves(self):
        url = reverse('gigs:submit_review', args=[10])
        self.assertEqual(resolve(url).func, views.submit_review)

    # --- Profile & Browsing URLs ---
    def test_musicians_list_url_resolves(self):
        url = reverse('gigs:musicians_list')
        self.assertEqual(resolve(url).func, views.musicians_list)

    def test_musician_detail_url_resolves(self):
        """EDGE CASE: Testing URL with an integer parameter for a musician profile"""
        url = reverse('gigs:musician_detail', args=[5])
        self.assertEqual(resolve(url).func, views.musician_detail)

    def test_bands_list_url_resolves(self):
        url = reverse('gigs:bands_list')
        self.assertEqual(resolve(url).func, views.bands_list)

    def test_band_detail_url_resolves(self):
        url = reverse('gigs:band_detail', args=[3])
        self.assertEqual(resolve(url).func, views.band_detail)

    # --- Dashboard Management URLs ---
    def test_my_applications_url_resolves(self):
        url = reverse('gigs:my_applications')
        self.assertEqual(resolve(url).func, views.my_applications)

    def test_my_bookmarks_url_resolves(self):
        url = reverse('gigs:my_bookmarks')
        self.assertEqual(resolve(url).func, views.my_bookmarks)

    def test_update_profile_url_resolves(self):
        url = reverse('gigs:update_profile')
        self.assertEqual(resolve(url).func, views.update_profile)

    def test_delete_listing_url_resolves(self):
        url = reverse('gigs:delete_listing', args=[10])
        self.assertEqual(resolve(url).func, views.delete_listing)

    # --- Authentication & Password Reset URLs ---
    def test_signup_url_resolves(self):
        url = reverse('gigs:signup')
        self.assertEqual(resolve(url).func, views.signup_choice)

    def test_login_url_resolves(self):
        url = reverse('gigs:login')
        self.assertEqual(resolve(url).func.view_class.__name__, 'LoginView')

    def test_password_reset_url_resolves(self):
        url = reverse('gigs:password_reset')
        self.assertEqual(resolve(url).func.view_class.__name__, 'PasswordResetView')