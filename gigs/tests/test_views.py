from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
import json

from gigs.models import Musician, Band, Listing, Application, Review

class ViewBaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        "Prepare shared objects for all the tests"
        cls.band_user = User.objects.create_user(
            username="banduser", email="band@test.com", password="pass123"
        )
        cls.musician_user = User.objects.create_user(
            username="musicianuser", email="musician@test.com", password="pass123"
        )

        cls.band = Band.objects.create(
            user=cls.band_user,
            name="Test Band",
            location="Glasgow",
            bio="Band bio"
        )

        cls.musician = Musician.objects.create(
            user=cls.musician_user,
            bio="Musician bio",
            age=21,
            instruments="Guitar",
            location="Glasgow"
        )

        cls.listing = Listing.objects.create(
            band=cls.band,
            title="Guitarist needed",
            deadline=date(2026, 4, 1),
            is_urgent=False,
            description="Need a guitarist",
            location="Glasgow",
            req_instruments="Guitar"
        )

class PublicViewTests(ViewBaseTestCase):
    "When There is data in the database, do the public views respond correctly?"
    def test_home_page_loads_for_anonymous_user(self):
        response = self.client.get(reverse('gigs:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gigs/home.html')
        self.assertContains(response, 'Connecting local talent')

    def test_gig_listings_page_loads(self):
        response = self.client.get(reverse('gigs:gig_listings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gigs/gig_listings.html')
        self.assertIn(self.listing, response.context['gigs'])

    def test_gig_detail_page_loads(self):
        response = self.client.get(reverse('gigs:gig_detail', args=[self.listing.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gigs/gig_detail.html')
        self.assertEqual(response.context['listing'], self.listing)

    def test_musicians_list_page_loads(self):
        response = self.client.get(reverse('gigs:musicians_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gigs/musicians_list.html')
        self.assertIn(self.musician, response.context['musicians'])

    def test_bands_list_page_loads(self):
        response = self.client.get(reverse('gigs:bands_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gigs/bands_list.html')
        self.assertIn(self.band, response.context['bands'])

    def test_gig_detail_invalid_id_returns_404(self):
        response = self.client.get(reverse('gigs:gig_detail', args=[999999]))
        self.assertEqual(response.status_code, 404)

class PublicViewEmptyStateTests(TestCase):
    "When There is no data in the database, do the public views respond correctly?"
    def test_gig_listings_empty(self):
        response = self.client.get(reverse('gigs:gig_listings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gigs/gig_listings.html')
        self.assertEqual(list(response.context['gigs']), [])

    def test_musicians_list_empty(self):
        response = self.client.get(reverse('gigs:musicians_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gigs/musicians_list.html')
        self.assertEqual(list(response.context['musicians']), [])

    def test_bands_list_empty(self):
        response = self.client.get(reverse('gigs:bands_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gigs/bands_list.html')
        self.assertEqual(list(response.context['bands']), [])

class CreateGigViewTests(ViewBaseTestCase):

    def test_create_gig_page_loads_for_band(self):
        self.client.login(username='banduser', password='pass123')
        response = self.client.get(reverse("gigs:create_gig"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gigs/create_gig.html')

    def test_band_can_create_gig(self):
        self.client.login(username='banduser', password='pass123')

        response = self.client.post(
            reverse('gigs:create_gig_listing'),
            data=json.dumps({
                'title': 'Drummer wanted',
                'req_instruments': 'Drums',
                'date': '2026-05-01',
                'description': 'Need drummer',
                'location': 'Glasgow',
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Listing.objects.filter(title='Drummer wanted').exists())


    def test_anonymous_user_cannot_create_gig(self):
        response = self.client.post(
            reverse('gigs:create_gig_listing'),
            data=json.dumps({
                'title': 'Drummer wanted',
                'req_instruments': 'Drums',
                'date': '2026-05-01',
                'description': 'Need drummer',
                'location': 'Glasgow',
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Listing.objects.filter(title='Drummer wanted').exists())

    def test_musician_cannot_create_gig(self):
        self.client.login(username='musicianuser', password='pass123')
        response = self.client.post(
            reverse('gigs:create_gig_listing'),
            data=json.dumps({
                'title': 'Drummer wanted',
                'req_instruments': 'Drums',
                'date': '2026-05-01',
                'description': 'Need drummer',
                'location': 'Glasgow',
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Listing.objects.filter(title='Drummer wanted').exists())

    def test_invalid_gig_data_does_not_create_listing(self):

        self.client.login(username='banduser', password='pass123')

        response = self.client.post(
                reverse('gigs:create_gig_listing'),
                data=json.dumps({
                    'title': 'Drummer wanted',
                }),
                content_type='application/json'
            )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Listing.objects.filter(title='Drummer wanted').exists())