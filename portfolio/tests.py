from datetime import date

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
        self.assertContains(response, "/projects/")

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


TINY_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


class ProjectCatalogViewTests(TestCase):
    def setUp(self):
        SiteProfile.load()
        django = Technology.objects.create(name="Django", category="backend")
        self.platform = Project.objects.create(
            title_en="Otoino",
            short_description_en="Automotive services platform",
            description_en="Full case study copy",
            category="platform",
            status="shipped",
        )
        self.platform.technologies.add(django)
        ProjectMedia.objects.create(
            project=self.platform,
            image=SimpleUploadedFile("cover.png", TINY_PNG, content_type="image/png"),
            alt_text="Otoino cover",
            is_cover=True,
        )
        self.notes = Project.objects.create(
            title_en="System Notes",
            description_en="Engineering notes",
            category="content",
            status="in_progress",
        )
        Project.objects.create(
            title_en="Hidden Draft",
            description_en="Not ready",
            category="product",
            is_published=False,
        )

    def test_catalog_lists_published_projects(self):
        response = self.client.get(reverse("project_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Otoino")
        self.assertContains(response, "Automotive services platform")
        self.assertContains(response, "Django")
        self.assertContains(response, "Otoino cover")
        self.assertContains(response, reverse("project_detail", kwargs={"slug": self.platform.slug}))
        self.assertContains(response, "System Notes")
        self.assertNotContains(response, "Hidden Draft")
        self.assertContains(response, 'id="projGrid"')
        self.assertContains(response, "?category=platform")
        self.assertContains(response, "?category=content")

    def test_category_filter_is_server_side(self):
        response = self.client.get(reverse("project_list"), {"category": "platform"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Otoino")
        self.assertNotContains(response, "System Notes")

    def test_unknown_category_shows_all_published(self):
        response = self.client.get(reverse("project_list"), {"category": "not-a-category"})
        self.assertContains(response, "Otoino")
        self.assertContains(response, "System Notes")

    def test_home_links_to_catalog(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("project_list"))
        self.assertContains(response, 'id="projGrid"')

    def test_unpublished_detail_is_404(self):
        response = self.client.get("/projects/hidden-draft/")
        self.assertEqual(response.status_code, 404)

    def test_detail_renders_case_study_sections(self):
        self.platform.role_en = "Backend Engineer\nSystem Architect"
        self.platform.client = "Otoino"
        self.platform.started_at = date(2024, 1, 1)
        self.platform.save()
        ProjectLink.objects.create(
            project=self.platform,
            title="Live Website",
            url="https://otoino.example",
            type="live",
        )
        ProjectMedia.objects.create(
            project=self.platform,
            image=SimpleUploadedFile("shot.png", TINY_PNG, content_type="image/png"),
            caption="Dashboard",
            alt_text="Otoino dashboard",
            media_type="dashboard",
            order=1,
        )
        sibling = Project.objects.create(
            title_en="Fleet Ops",
            description_en="Related platform",
            category="platform",
            status="shipped",
        )
        response = self.client.get(self.platform.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Otoino")
        self.assertContains(response, "Automotive services platform")
        self.assertContains(response, "Full case study copy")
        self.assertContains(response, "Backend Engineer")
        self.assertContains(response, "System Architect")
        self.assertContains(response, "Django")
        self.assertContains(response, "Live Website")
        self.assertContains(response, "https://otoino.example")
        self.assertContains(response, "Otoino dashboard")
        self.assertContains(response, "Dashboard")
        self.assertContains(response, "data-gallery")
        self.assertContains(response, sibling.get_absolute_url())
        self.assertNotContains(response, "Hidden Draft")

    def test_detail_omits_empty_optional_sections(self):
        response = self.client.get(self.notes.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "System Notes")
        self.assertContains(response, "Engineering notes")
        self.assertNotContains(response, 'id="case-role-title"')
        self.assertNotContains(response, 'id="case-gallery-title"')
        self.assertNotContains(response, 'id="case-links-title"')
