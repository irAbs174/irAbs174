from django.contrib import admin

from .models import (
    AboutFocus,
    CareerEntry,
    Project,
    ProjectLink,
    ProjectMedia,
    SiteProfile,
    SocialChannel,
    TechItem,
    Technology,
)


@admin.register(SiteProfile)
class SiteProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Identity", {"fields": ("brand_name", "page_title", "meta_description_en", "meta_description_fa", "portrait", "brand_logo")}),
        ("Hero", {"fields": (
            "greeting_en", "greeting_fa", "display_name_en", "display_name_fa",
            "hero_title_en", "hero_title_fa", "hero_sub_en", "hero_sub_fa",
            "cta_contact_en", "cta_contact_fa", "badge_val_en", "badge_val_fa",
        )}),
        ("About", {"fields": (
            "about_title1_en", "about_title1_fa", "about_title2_en", "about_title2_fa",
            "about_p1_en", "about_p1_fa", "about_p2_en", "about_p2_fa",
        )}),
        ("Section titles", {"fields": (
            "stack_title1_en", "stack_title1_fa", "stack_title2_en", "stack_title2_fa", "stack_sub_en", "stack_sub_fa",
            "career_title1_en", "career_title1_fa", "career_title2_en", "career_title2_fa", "career_sub_en", "career_sub_fa",
            "projects_title1_en", "projects_title1_fa", "projects_title2_en", "projects_title2_fa", "projects_sub_en", "projects_sub_fa",
            "content_title1_en", "content_title1_fa", "content_title2_en", "content_title2_fa", "content_sub_en", "content_sub_fa",
        )}),
        ("Contact", {"fields": (
            "contact_title1_en", "contact_title1_fa", "contact_title2_en", "contact_title2_fa",
            "contact_sub_en", "contact_sub_fa", "contact_telegram_url", "contact_email",
            "telegram_cta_en", "telegram_cta_fa", "email_cta_en", "email_cta_fa",
        )}),
        ("Footer", {"fields": ("footer_copy_en", "footer_copy_fa", "github_url", "linkedin_url", "x_url")}),
    )

    def has_add_permission(self, request):
        return not SiteProfile.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AboutFocus)
class AboutFocusAdmin(admin.ModelAdmin):
    list_display = ("title_en", "icon", "order", "is_published")
    list_editable = ("order", "is_published")


@admin.register(TechItem)
class TechItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "order", "is_published")
    list_editable = ("order", "is_published")
    list_filter = ("category",)


@admin.register(CareerEntry)
class CareerEntryAdmin(admin.ModelAdmin):
    list_display = ("role_en", "company_en", "period_en", "order", "is_published")
    list_editable = ("order", "is_published")


class ProjectMediaInline(admin.TabularInline):
    model = ProjectMedia
    extra = 1
    fields = ("image", "caption", "alt_text", "media_type", "is_cover", "order")


class ProjectLinkInline(admin.TabularInline):
    model = ProjectLink
    extra = 1
    fields = ("title", "url", "type", "icon", "order")


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "category")
    list_filter = ("category",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title_en", "slug", "category", "status", "featured", "order", "is_published")
    list_editable = ("order", "is_published", "featured")
    list_filter = ("category", "status", "featured", "is_published")
    search_fields = ("title_en", "title_fa", "slug", "client", "short_description_en")
    prepopulated_fields = {"slug": ("title_en",)}
    filter_horizontal = ("technologies",)
    inlines = [ProjectMediaInline, ProjectLinkInline]
    ordering = ("order", "pk")
    readonly_fields = ("created_at", "updated_at")
    view_on_site = False
    fieldsets = (
        ("Identity", {"fields": ("title_en", "title_fa", "slug", "category", "status", "client")}),
        ("Copy", {"fields": (
            "short_description_en", "short_description_fa",
            "description_en", "description_fa",
            "role_en", "role_fa",
        )}),
        ("Dates & visibility", {"fields": (
            "started_at", "completed_at", "featured", "order", "is_published",
        )}),
        ("Links", {"fields": ("live_url", "github_url")}),
        ("Homepage card", {"fields": ("image", "tags")}),
        ("Technologies", {"fields": ("technologies",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(ProjectMedia)
class ProjectMediaAdmin(admin.ModelAdmin):
    list_display = ("project", "media_type", "is_cover", "order", "caption")
    list_filter = ("media_type", "is_cover")
    list_editable = ("order",)
    search_fields = ("caption", "alt_text", "project__title_en")
    autocomplete_fields = ("project",)
    ordering = ("project", "order", "pk")


@admin.register(ProjectLink)
class ProjectLinkAdmin(admin.ModelAdmin):
    list_display = ("project", "title", "type", "url", "order")
    list_filter = ("type",)
    list_editable = ("order",)
    search_fields = ("title", "url", "project__title_en")
    autocomplete_fields = ("project",)
    ordering = ("project", "order", "pk")


@admin.register(SocialChannel)
class SocialChannelAdmin(admin.ModelAdmin):
    list_display = ("name_en", "handle", "css_class", "order", "is_published", "show_in_footer")
    list_editable = ("order", "is_published", "show_in_footer")
