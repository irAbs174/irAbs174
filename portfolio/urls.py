from django.contrib.sitemaps.views import sitemap
from django.urls import path

from .sitemaps import HomeSitemap
from .views import HomeView, robots_txt

sitemaps = {"home": HomeSitemap}

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]
