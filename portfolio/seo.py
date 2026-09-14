from django.conf import settings
from django.utils.translation import gettext as _


def public_url(path=""):
    protocol = "http" if settings.DEBUG else "https"
    if path.startswith(("http://", "https://")):
        return path
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{protocol}://{settings.SITE_DOMAIN}{path}"


def default_seo(profile, path="/"):
    image = ""
    if getattr(profile, "portrait", None):
        image = public_url(profile.portrait.url)
    elif getattr(profile, "brand_logo", None):
        image = public_url(profile.brand_logo.url)
    return {
        "title": profile.page_title,
        "description": profile.loc("meta_description"),
        "canonical": public_url(path),
        "image": image,
        "og_type": "website",
    }


def catalog_seo(profile, path="/projects/"):
    seo = default_seo(profile, path)
    seo["title"] = f"{_('Projects')} | {profile.brand_name}"
    seo["description"] = _("Systems I've built. Products I've shipped. Problems I've solved.")
    return seo


def project_seo(profile, project, path):
    seo = default_seo(profile, path)
    seo["title"] = project.seo_title(profile.brand_name)
    seo["description"] = project.seo_description()
    seo["og_type"] = "article"
    if project.cover_url:
        seo["image"] = public_url(project.cover_url)
    return seo
