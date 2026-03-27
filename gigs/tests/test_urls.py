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