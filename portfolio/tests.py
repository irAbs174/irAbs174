from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from portfolio.models import SiteProfile, TechItem
from portfolio.views import error_400, error_403, error_404, error_500


class HomeViewTests(TestCase):
    def setUp(self):
        SiteProfile.load()
        TechItem.objects.create(
            name="Python",
            category="backend",
            logo_url="https://cdn.simpleicons.org/python/3776AB",
            order=0,
        )

    def test_home_renders(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python")
        self.assertContains(response, 'id="projGrid"')

    def test_robots_txt(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"].split(";")[0], "text/plain")
        self.assertContains(response, "User-agent: *")
        self.assertContains(response, "Disallow: /unique/")
        self.assertContains(response, "Sitemap:")
        self.assertContains(response, "/sitemap.xml")

    def test_sitemap_xml(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertIn("xml", response["Content-Type"])
        self.assertContains(response, "damerchi.ir")
        self.assertContains(response, "<loc>")

    def test_language_switch_sets_cookie(self):
        response = self.client.post(
            reverse("set_language"),
            {"language": "en", "next": "/"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.cookies.get("django_language").value, "en")


class ErrorPageTests(TestCase):
    @override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
    def test_404_page(self):
        response = self.client.get("/this-page-does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "404", status_code=404)
        self.assertContains(response, "error-page", status_code=404)

    def test_error_views_render(self):
        factory = RequestFactory()
        request = factory.get("/")
        self.assertEqual(error_400(request).status_code, 400)
        self.assertEqual(error_403(request).status_code, 403)
        self.assertEqual(error_404(request).status_code, 404)
        self.assertEqual(error_500(request).status_code, 500)
        self.assertContains(error_500(request), "500", status_code=500)
