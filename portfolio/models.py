from django.db import models
from django.utils.translation import get_language, gettext_lazy as _


class LocalizedMixin:
    def loc(self, name):
        lang = (get_language() or "en").split("-")[0]
        for code in (lang, "en", "fa"):
            attr = f"{name}_{code}"
            if hasattr(self, attr):
                value = getattr(self, attr)
                if value:
                    return value
        return ""


class OrderedPublishedQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True).order_by("order", "pk")


class SiteProfile(LocalizedMixin, models.Model):
    brand_name = models.CharField(max_length=120, default="Abbas Damerchi")
    page_title = models.CharField(max_length=180, default="Abbas Damerchi | Personal Portfolio")
    meta_description_en = models.TextField(blank=True)
    meta_description_fa = models.TextField(blank=True)

    greeting_en = models.CharField(max_length=80, blank=True)
    greeting_fa = models.CharField(max_length=80, blank=True)
    display_name_en = models.CharField(max_length=80, blank=True)
    display_name_fa = models.CharField(max_length=80, blank=True)
    hero_title_en = models.CharField(max_length=120, blank=True)
    hero_title_fa = models.CharField(max_length=120, blank=True)
    hero_sub_en = models.TextField(blank=True)
    hero_sub_fa = models.TextField(blank=True)
    cta_contact_en = models.CharField(max_length=80, blank=True)
    cta_contact_fa = models.CharField(max_length=80, blank=True)
    badge_val_en = models.CharField(max_length=160, blank=True)
    badge_val_fa = models.CharField(max_length=160, blank=True)

    about_title1_en = models.CharField(max_length=120, blank=True)
    about_title1_fa = models.CharField(max_length=120, blank=True)
    about_title2_en = models.CharField(max_length=120, blank=True)
    about_title2_fa = models.CharField(max_length=120, blank=True)
    about_p1_en = models.TextField(blank=True)
    about_p1_fa = models.TextField(blank=True)
    about_p2_en = models.TextField(blank=True)
    about_p2_fa = models.TextField(blank=True)

    stack_title1_en = models.CharField(max_length=120, blank=True)
    stack_title1_fa = models.CharField(max_length=120, blank=True)
    stack_title2_en = models.CharField(max_length=120, blank=True)
    stack_title2_fa = models.CharField(max_length=120, blank=True)
    stack_sub_en = models.TextField(blank=True)
    stack_sub_fa = models.TextField(blank=True)

    career_title1_en = models.CharField(max_length=120, blank=True)
    career_title1_fa = models.CharField(max_length=120, blank=True)
    career_title2_en = models.CharField(max_length=120, blank=True)
    career_title2_fa = models.CharField(max_length=120, blank=True)
    career_sub_en = models.TextField(blank=True)
    career_sub_fa = models.TextField(blank=True)

    projects_title1_en = models.CharField(max_length=120, blank=True)
    projects_title1_fa = models.CharField(max_length=120, blank=True)
    projects_title2_en = models.CharField(max_length=120, blank=True)
    projects_title2_fa = models.CharField(max_length=120, blank=True)
    projects_sub_en = models.TextField(blank=True)
    projects_sub_fa = models.TextField(blank=True)

    content_title1_en = models.CharField(max_length=120, blank=True)
    content_title1_fa = models.CharField(max_length=120, blank=True)
    content_title2_en = models.CharField(max_length=120, blank=True)
    content_title2_fa = models.CharField(max_length=120, blank=True)
    content_sub_en = models.TextField(blank=True)
    content_sub_fa = models.TextField(blank=True)

    contact_title1_en = models.CharField(max_length=120, blank=True)
    contact_title1_fa = models.CharField(max_length=120, blank=True)
    contact_title2_en = models.CharField(max_length=120, blank=True)
    contact_title2_fa = models.CharField(max_length=120, blank=True)
    contact_sub_en = models.TextField(blank=True)
    contact_sub_fa = models.TextField(blank=True)
    contact_telegram_url = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    telegram_cta_en = models.CharField(max_length=80, blank=True)
    telegram_cta_fa = models.CharField(max_length=80, blank=True)
    email_cta_en = models.CharField(max_length=80, blank=True)
    email_cta_fa = models.CharField(max_length=80, blank=True)

    footer_copy_en = models.CharField(max_length=200, blank=True)
    footer_copy_fa = models.CharField(max_length=200, blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    x_url = models.URLField(blank=True)

    portrait = models.ImageField(upload_to="profile/", blank=True)
    brand_logo = models.ImageField(upload_to="profile/", blank=True)

    class Meta:
        verbose_name = "Site profile"
        verbose_name_plural = "Site profile"

    def __str__(self):
        return self.brand_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AboutFocus(LocalizedMixin, models.Model):
    icon = models.CharField(max_length=16, help_text="Emoji or short icon")
    title_en = models.CharField(max_length=160)
    title_fa = models.CharField(max_length=160, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    objects = OrderedPublishedQuerySet.as_manager()

    class Meta:
        ordering = ["order", "pk"]

    def __str__(self):
        return self.title_en


class TechItem(models.Model):
    CATEGORIES = [
        ("backend", "Backend"),
        ("frontend", "Frontend"),
        ("devops", "DevOps"),
        ("data", "Data"),
        ("tools", "Tools"),
    ]
    name = models.CharField(max_length=80)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    logo_url = models.URLField()
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    objects = OrderedPublishedQuerySet.as_manager()

    class Meta:
        ordering = ["order", "pk"]

    def __str__(self):
        return self.name

    def category_label(self):
        labels = {
            "backend": _("Backend"),
            "frontend": _("Frontend"),
            "devops": _("DevOps"),
            "data": _("Data"),
            "tools": _("Tools"),
        }
        return labels.get(self.category, self.category)


class CareerEntry(LocalizedMixin, models.Model):
    role_en = models.CharField(max_length=160)
    role_fa = models.CharField(max_length=160, blank=True)
    company_en = models.CharField(max_length=160)
    company_fa = models.CharField(max_length=160, blank=True)
    period_en = models.CharField(max_length=80)
    period_fa = models.CharField(max_length=80, blank=True)
    description_en = models.TextField()
    description_fa = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    objects = OrderedPublishedQuerySet.as_manager()

    class Meta:
        ordering = ["order", "pk"]
        verbose_name_plural = "Career entries"

    def __str__(self):
        return self.role_en


class Project(LocalizedMixin, models.Model):
    title_en = models.CharField(max_length=160)
    title_fa = models.CharField(max_length=160, blank=True)
    description_en = models.TextField()
    description_fa = models.TextField(blank=True)
    image = models.ImageField(upload_to="projects/", blank=True)
    tags = models.JSONField(default=list, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    objects = OrderedPublishedQuerySet.as_manager()

    class Meta:
        ordering = ["order", "pk"]

    def __str__(self):
        return self.title_en


class ProjectLink(models.Model):
    project = models.ForeignKey(Project, related_name="links", on_delete=models.CASCADE)
    label = models.CharField(max_length=80)
    href = models.URLField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "pk"]

    def __str__(self):
        return f"{self.project.title_en} · {self.label}"


class SocialChannel(LocalizedMixin, models.Model):
    name_en = models.CharField(max_length=80)
    name_fa = models.CharField(max_length=80, blank=True)
    handle = models.CharField(max_length=120)
    href = models.URLField()
    icon_url = models.CharField(max_length=300)
    css_class = models.CharField(max_length=20)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    show_in_footer = models.BooleanField(default=False)

    objects = OrderedPublishedQuerySet.as_manager()

    class Meta:
        ordering = ["order", "pk"]

    def __str__(self):
        return self.name_en
