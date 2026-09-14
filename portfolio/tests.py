from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from portfolio.models import Project, ProjectLink, ProjectMedia, SiteProfile, TechItem, Technology
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


class ProjectCatalogModelTests(TestCase):
    def test_project_generates_unique_slug(self):
        first = Project.objects.create(title_en="Otoino", description_en="Automotive platform")
        second = Project.objects.create(title_en="Otoino", description_en="Another one")
        self.assertEqual(first.slug, "otoino")
        self.assertEqual(second.slug, "otoino-2")

    def test_technology_slug_and_m2m(self):
        django = Technology.objects.create(name="Django", category="backend")
        postgres = Technology.objects.create(name="PostgreSQL", category="database")
        self.assertEqual(django.slug, "django")
        project = Project.objects.create(title_en="Catalog", description_en="Case study")
        project.technologies.set([django, postgres])
        self.assertQuerySetEqual(
            project.technologies.order_by("name"),
            [django, postgres],
            transform=lambda item: item,
        )

    def test_project_link_and_cover_media(self):
        project = Project.objects.create(title_en="Gallery", description_en="Images")
        ProjectLink.objects.create(
            project=project,
            title="GitHub",
            url="https://github.com/irAbs174",
            type="github",
        )
        png = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
            b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        cover = ProjectMedia.objects.create(
            project=project,
            image=SimpleUploadedFile("cover.png", png, content_type="image/png"),
            alt_text="Cover",
            is_cover=True,
            order=0,
        )
        extra = ProjectMedia.objects.create(
            project=project,
            image=SimpleUploadedFile("extra.png", png, content_type="image/png"),
            media_type="screenshot",
            order=1,
        )
        self.assertEqual(project.cover_media(), cover)
        self.assertEqual(project.links.first().href, "https://github.com/irAbs174")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProjectMedia.objects.create(
                    project=project,
                    image=SimpleUploadedFile("dup.png", png, content_type="image/png"),
                    is_cover=True,
                )
        extra.refresh_from_db()
        self.assertFalse(extra.is_cover)


class ProjectAdminTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser("admin", "admin@example.com", "pass")
        self.client.force_login(self.user)

    def test_project_admin_pages(self):
        for model in ("project", "technology", "projectlink", "projectmedia"):
            with self.subTest(model=model):
                changelist = self.client.get(reverse(f"admin:portfolio_{model}_changelist"))
                add_page = self.client.get(reverse(f"admin:portfolio_{model}_add"))
                self.assertEqual(changelist.status_code, 200)
                self.assertEqual(add_page.status_code, 200)

    def test_project_change_form_has_inlines_and_technologies(self):
        tech = Technology.objects.create(name="Django", category="backend")
        project = Project.objects.create(title_en="Otoino", description_en="Platform")
        project.technologies.add(tech)
        response = self.client.get(reverse("admin:portfolio_project_change", args=[project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Project media")
        self.assertContains(response, "Project links")
        self.assertContains(response, "Django")
        self.assertContains(response, 'name="technologies"')
