from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("unique/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include("portfolio.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = "portfolio.views.error_400"
handler403 = "portfolio.views.error_403"
handler404 = "portfolio.views.error_404"
handler500 = "portfolio.views.error_500"
