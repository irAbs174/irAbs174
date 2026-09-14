from django.conf import settings
from django.contrib.sitemaps.views import sitemap as django_sitemap
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView

from .models import AboutFocus, CareerEntry, Project, SiteProfile, SocialChannel, TechItem
from .sitemaps import HomeSitemap


def _agent_log(location, message, data, hypothesis_id):
    # #region agent log
    try:
        import json
        import time

        payload = {
            "sessionId": "dce383",
            "runId": "cdn-check",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000),
        }
        with open("/tmp/debug-dce383.log", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload) + "\n")
    except Exception:
        pass
    # #endregion


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
    response = HttpResponse(body, content_type="text/plain; charset=utf-8")
    response["Cache-Control"] = "public, max-age=300, must-revalidate"
    _agent_log(
        "portfolio/views.py:robots_txt",
        "robots served",
        {"path": request.path, "status": response.status_code},
        "C",
    )
    return response


@require_GET
def sitemap_xml(request):
    response = django_sitemap(request, sitemaps={"home": HomeSitemap})
    response["Cache-Control"] = "public, max-age=300, must-revalidate"
    _agent_log(
        "portfolio/views.py:sitemap_xml",
        "sitemap served",
        {"path": request.path, "status": getattr(response, "status_code", None)},
        "C",
    )
    return response


class HomeView(TemplateView):
    template_name = "portfolio/home.html"

    def get(self, request, *args, **kwargs):
        # #region agent log
        try:
            import json
            import time

            payload = {
                "sessionId": "dce383",
                "runId": "post-fix",
                "hypothesisId": "A",
                "location": "portfolio/views.py:HomeView.get",
                "message": "portfolio home served",
                "data": {"path": request.path, "host": request.get_host()},
                "timestamp": int(time.time() * 1000),
            }
            with open("/tmp/debug-dce383.log", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(payload) + "\n")
        except Exception:
            pass
        # #endregion
        return super().get(request, *args, **kwargs)

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
    response = render(request, "errors/404.html", status=404)
    response["Cache-Control"] = "no-store"
    return response


def error_500(request):
    try:
        return render(request, "errors/500.html", status=500)
    except Exception:
        return HttpResponseServerError(
            "<!DOCTYPE html><title>500</title><h1>500</h1><p>Server error.</p>",
            content_type="text/html; charset=utf-8",
        )
