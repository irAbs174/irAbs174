from django.contrib.sitemaps.views import sitemap as django_sitemap
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.generic import DetailView, ListView, TemplateView

from .models import AboutFocus, CareerEntry, Project, SiteProfile, SocialChannel, TechItem
from .seo import catalog_seo, default_seo, project_seo, public_url
from .sitemaps import HomeSitemap, ProjectSitemap


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
    sitemap_url = public_url("/sitemap.xml")
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
    response = django_sitemap(
        request,
        sitemaps={"home": HomeSitemap, "projects": ProjectSitemap},
    )
    response["Cache-Control"] = "public, max-age=300, must-revalidate"
    _agent_log(
        "portfolio/views.py:sitemap_xml",
        "sitemap served",
        {"path": request.path, "status": getattr(response, "status_code", None)},
        "C",
    )
    return response


class ProfileContextMixin:
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.setdefault("profile", SiteProfile.load())
        ctx["seo"] = self.build_seo(ctx)
        return ctx

    def build_seo(self, ctx):
        return default_seo(ctx["profile"], self.request.path)


class HomeView(ProfileContextMixin, TemplateView):
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
        ctx["about_focuses"] = AboutFocus.objects.published()
        ctx["tech_items"] = TechItem.objects.published()
        ctx["career_entries"] = CareerEntry.objects.published()
        ctx["projects"] = Project.objects.published().prefetch_related("links")
        ctx["socials"] = SocialChannel.objects.published()
        return ctx


class ProjectListView(ProfileContextMixin, ListView):
    template_name = "portfolio/project_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        qs = Project.objects.catalog()
        category = self.request.GET.get("category", "")
        self.selected_category = category if category in dict(Project.CATEGORIES) else ""
        if self.selected_category:
            qs = qs.filter(category=self.selected_category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        used = set(
            Project.objects.published().exclude(category="").values_list("category", flat=True)
        )
        ctx["category_filters"] = [
            (value, label) for value, label in Project.CATEGORIES if value in used
        ]
        ctx["selected_category"] = getattr(self, "selected_category", "")
        ctx["show_category_filters"] = len(ctx["category_filters"]) > 1
        return ctx

    def build_seo(self, ctx):
        return catalog_seo(ctx["profile"], self.request.path)


class ProjectDetailView(ProfileContextMixin, DetailView):
    template_name = "portfolio/project_detail.html"
    context_object_name = "project"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Project.objects.published().prefetch_related("technologies", "media", "links")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        project = ctx["project"]
        media = list(project.media.all())
        cover = project.cover_media()
        if cover and len(media) > 1:
            ctx["gallery"] = [item for item in media if item.pk != cover.pk]
        else:
            ctx["gallery"] = []
        ctx["primary_link"] = project.primary_link()
        ctx["tech_groups"] = project.technologies_grouped()
        ctx["related_projects"] = project.related_projects()
        return ctx

    def build_seo(self, ctx):
        project = ctx["project"]
        return project_seo(ctx["profile"], project, project.get_absolute_url())


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
