from django.contrib import admin

from .models import (
    AboutFocus,
    CareerEntry,
    Project,
    ProjectLink,
    SiteProfile,
    SocialChannel,
    TechItem,
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


class ProjectLinkInline(admin.TabularInline):
    model = ProjectLink
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title_en", "order", "is_published")
    list_editable = ("order", "is_published")
    inlines = [ProjectLinkInline]


@admin.register(SocialChannel)
class SocialChannelAdmin(admin.ModelAdmin):
    list_display = ("name_en", "handle", "css_class", "order", "is_published", "show_in_footer")
    list_editable = ("order", "is_published", "show_in_footer")
