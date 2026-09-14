from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class HomeSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        return ["home"]

    def location(self, item):
        return reverse(item)

    def get_protocol(self, protocol=None):
        if self.protocol is not None:
            return self.protocol
        return "http" if settings.DEBUG else "https"

    def get_domain(self, site=None):
        return settings.SITE_DOMAIN
