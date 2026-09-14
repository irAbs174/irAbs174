from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Project


class DomainSitemap(Sitemap):
    def get_protocol(self, protocol=None):
        if self.protocol is not None:
            return self.protocol
        return "http" if settings.DEBUG else "https"

    def get_domain(self, site=None):
        return settings.SITE_DOMAIN


class HomeSitemap(DomainSitemap):
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        return ["home", "project_list"]

    def location(self, item):
        return reverse(item)


class ProjectSitemap(DomainSitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Project.objects.published()

    def lastmod(self, obj):
        return obj.updated_at
