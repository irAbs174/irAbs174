from django.conf import settings
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView

from .models import AboutFocus, CareerEntry, Project, SiteProfile, SocialChannel, TechItem


@require_GET
def robots_txt(request):
    protocol = "http" if settings.DEBUG else "https"
    sitemap_url = f"{protocol}://{settings.SITE_DOMAIN}/sitemap.xml"
    body = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "Disallow: /unique/",
            "Disallow: /i18n/",
            f"Sitemap: {sitemap_url}",
            "",
        ]
    )
    return HttpResponse(body, content_type="text/plain; charset=utf-8")


class HomeView(TemplateView):
    template_name = "portfolio/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["profile"] = SiteProfile.load()
        ctx["about_focuses"] = AboutFocus.objects.published()
        ctx["tech_items"] = TechItem.objects.published()
        ctx["career_entries"] = CareerEntry.objects.published()
        ctx["projects"] = Project.objects.published().prefetch_related("links")
        ctx["socials"] = SocialChannel.objects.published()
        return ctx


def error_400(request, exception=None):
    return render(request, "errors/400.html", status=400)


def error_403(request, exception=None):
    return render(request, "errors/403.html", status=403)


def error_404(request, exception=None):
    return render(request, "errors/404.html", status=404)


def error_500(request):
    try:
        return render(request, "errors/500.html", status=500)
    except Exception:
        return HttpResponseServerError(
            "<!DOCTYPE html><title>500</title><h1>500</h1><p>Server error.</p>",
            content_type="text/html; charset=utf-8",
        )
