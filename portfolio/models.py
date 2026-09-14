from django.db import models
from django.urls import reverse
from django.utils.text import slugify
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


class Technology(models.Model):
    CATEGORIES = [
        ("language", "Language"),
        ("backend", "Backend"),
        ("frontend", "Frontend"),
        ("database", "Database"),
        ("infrastructure", "Infrastructure"),
        ("devops", "DevOps"),
        ("data", "Data"),
        ("tools", "Tools"),
    ]

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    icon = models.CharField(
        max_length=300,
        blank=True,
        help_text="Emoji, CSS class, or icon URL",
    )
    category = models.CharField(max_length=20, choices=CATEGORIES, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Technologies"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(Technology, self, slugify(self.name) or "technology")
        super().save(*args, **kwargs)


class ProjectQuerySet(OrderedPublishedQuerySet):
    def featured(self):
        return self.filter(featured=True)


class Project(LocalizedMixin, models.Model):
    CATEGORIES = [
        ("product", "Product"),
        ("platform", "Platform"),
        ("open_source", "Open Source"),
        ("infrastructure", "Infrastructure"),
        ("content", "Content"),
        ("other", "Other"),
    ]
    STATUSES = [
        ("in_progress", "In progress"),
        ("shipped", "Shipped"),
        ("maintained", "Maintained"),
        ("archived", "Archived"),
    ]

    title_en = models.CharField(max_length=160)
    title_fa = models.CharField(max_length=160, blank=True)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    short_description_en = models.CharField(max_length=280, blank=True)
    short_description_fa = models.CharField(max_length=280, blank=True)
    description_en = models.TextField()
    description_fa = models.TextField(blank=True)
    role_en = models.TextField(blank=True, help_text="One role per line, e.g. Backend Engineer")
    role_fa = models.TextField(blank=True)
    client = models.CharField(max_length=160, blank=True)
    category = models.CharField(max_length=32, choices=CATEGORIES, blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default="shipped")
    started_at = models.DateField(null=True, blank=True)
    completed_at = models.DateField(null=True, blank=True)
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    image = models.ImageField(upload_to="projects/", blank=True)
    tags = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=True)
    technologies = models.ManyToManyField(Technology, related_name="projects", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProjectQuerySet.as_manager()

    class Meta:
        ordering = ["order", "pk"]

    def __str__(self):
        return self.title_en

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(Project, self, slugify(self.title_en) or "project")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("project_detail", kwargs={"slug": self.slug})

    def cover_media(self):
        cover = self.media.filter(is_cover=True).first()
        if cover:
            return cover
        return self.media.order_by("order", "pk").first()

    def role_lines(self):
        text = self.loc("role")
        return [line.strip() for line in text.splitlines() if line.strip()]


class ProjectMedia(models.Model):
    MEDIA_TYPES = [
        ("image", "Image"),
        ("screenshot", "Screenshot"),
        ("architecture", "Architecture"),
        ("dashboard", "Dashboard"),
        ("mobile", "Mobile"),
        ("diagram", "Diagram"),
        ("video", "Video"),
    ]

    project = models.ForeignKey(Project, related_name="media", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="projects/gallery/")
    caption = models.CharField(max_length=240, blank=True)
    alt_text = models.CharField(max_length=160, blank=True)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES, default="image")
    is_cover = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "pk"]
        verbose_name_plural = "Project media"
        constraints = [
            models.UniqueConstraint(
                fields=["project"],
                condition=models.Q(is_cover=True),
                name="unique_project_cover_media",
            ),
        ]

    def __str__(self):
        label = self.caption or self.alt_text or self.image.name
        return f"{self.project.title_en} · {label}"


class ProjectLink(models.Model):
    LINK_TYPES = [
        ("live", "Live Website"),
        ("github", "GitHub"),
        ("docs", "Documentation"),
        ("demo", "Demo"),
        ("youtube", "YouTube"),
        ("article", "Article"),
        ("repository", "Repository"),
        ("other", "Other"),
    ]

    project = models.ForeignKey(Project, related_name="links", on_delete=models.CASCADE)
    title = models.CharField(max_length=80)
    url = models.URLField()
    type = models.CharField(max_length=32, choices=LINK_TYPES, default="other")
    icon = models.CharField(max_length=300, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "pk"]

    def __str__(self):
        return f"{self.project.title_en} · {self.title}"

    @property
    def label(self):
        return self.title

    @property
    def href(self):
        return self.url


def _unique_slug(model, instance, base):
    slug = base
    n = 2
    qs = model.objects.filter(slug=slug)
    if instance.pk:
        qs = qs.exclude(pk=instance.pk)
    while qs.exists():
        slug = f"{base}-{n}"
        n += 1
        qs = model.objects.filter(slug=slug)
        if instance.pk:
            qs = qs.exclude(pk=instance.pk)
    return slug


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
