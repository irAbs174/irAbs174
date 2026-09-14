from django.urls import path

from .views import HomeView, robots_txt, sitemap_xml

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap_xml, name="sitemap"),
]
