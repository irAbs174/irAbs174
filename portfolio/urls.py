from django.urls import path

from .views import HomeView, ProjectDetailView, ProjectListView, robots_txt, sitemap_xml

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("projects/", ProjectListView.as_view(), name="project_list"),
    path("projects/<slug:slug>/", ProjectDetailView.as_view(), name="project_detail"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap_xml, name="sitemap"),
]
