from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from portfolio.models import (
    AboutFocus,
    CareerEntry,
    Project,
    ProjectLink,
    SiteProfile,
    SocialChannel,
    TechItem,
)

IMG = Path(settings.BASE_DIR) / "static" / "img"

_LINK_TYPES = {
    "github": "github",
    "live": "live",
    "website": "live",
    "docs": "docs",
    "documentation": "docs",
    "demo": "demo",
    "youtube": "youtube",
    "medium": "article",
    "article": "article",
    "repository": "repository",
}


def _link_type(label):
    return _LINK_TYPES.get(label.strip().lower(), "other")


def attach(field, filename):
    path = IMG / filename
    if not path.exists():
        return
    if field.name:
        return
    with path.open("rb") as fh:
        field.save(filename, File(fh), save=False)


class Command(BaseCommand):
    help = "Seed portfolio CMS content from the original static site."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Replace existing content")

    def handle(self, *args, **options):
        force = options["force"]
        if SiteProfile.objects.filter(pk=1).exists() and TechItem.objects.exists() and not force:
            self.stdout.write(self.style.WARNING("Content already present. Use --force to replace."))
            return

        if force:
            ProjectLink.objects.all().delete()
            Project.objects.all().delete()
            AboutFocus.objects.all().delete()
            TechItem.objects.all().delete()
            CareerEntry.objects.all().delete()
            SocialChannel.objects.all().delete()

        profile = SiteProfile.load()
        profile.brand_name = "Abbas Damerchi"
        profile.page_title = "Abbas Damerchi | Personal Portfolio"
        profile.meta_description_en = "Abbas Damerchi | backend and product engineer building reliable systems and useful digital products."
        profile.meta_description_fa = "عباس دمرچی | مهندس بک‌اند و محصول، سازنده سیستم‌های قابل اعتماد و محصولات دیجیتال مفید."
        profile.greeting_en = "Hi. I'm"
        profile.greeting_fa = "سلام. من"
        profile.display_name_en = "Abbas;"
        profile.display_name_fa = "عباسم؛"
        profile.hero_title_en = "a technologist"
        profile.hero_title_fa = "یک تکنولوژیست"
        profile.hero_sub_en = "<strong>Distributed systems engineer</strong> working at the intersection of backend architecture, automation, FinTech, and product UX. I design reliable, Scalable systems and the interfaces people actually want to use."
        profile.hero_sub_fa = "<strong>مهندس سیستم‌های مغیاس پذیر و توزیع شده</strong> در مرز معماری بک‌اند، اتوماسیون، فین‌تک و تجربه کاربری محصول. سیستم‌هایی قابل اعتماد و مغیاس پذیر طراحی می‌کنم و رابط‌هایی که واقعاً استفاده از آن‌ها لذت‌بخش است."
        profile.cta_contact_en = "Get in Touch"
        profile.cta_contact_fa = "تماس با من"
        profile.badge_val_en = "Turning ideas into useful tools"
        profile.badge_val_fa = "تبدیل ایده‌ها به ابزارهای کاربردی"
        profile.about_title1_en = "Engineering with"
        profile.about_title1_fa = "مهندسی با"
        profile.about_title2_en = "product instincts."
        profile.about_title2_fa = "ذوق محصول."
        profile.about_p1_en = "I build <strong>reliable, automated systems that turn complex workflows into simple products</strong>. My work sits at the intersection of backend architecture, automation, product UX, and technical content | from distributed systems and financial technology to automated commerce platforms and SEO-driven products."
        profile.about_p1_fa = "من <strong>سیستم‌های قابل اعتماد و خودکاری می‌سازم که جریان‌های کاری پیچیده را به محصولاتی ساده تبدیل می‌کنند</strong>. کار من در تقاطع معماری بک‌اند، اتوماسیون، تجربه کاربری محصول و محتوای فنی قرار دارد | از سیستم‌های توزیع‌شده و فناوری مالی تا پلتفرم‌های تجارت الکترونیک خودکار و محصولات مبتنی بر سئو."
        profile.about_p2_en = "I care about more than making software <em>work</em>. I want it to be clear, dependable, and pleasant to use. That means thoughtful architecture, useful monitoring, and attention to the small details people notice."
        profile.about_p2_fa = "برایم فقط <em>کار کردن</em> نرم‌افزار مهم نیست؛ می‌خواهم واضح، قابل اعتماد و خوشایند باشد. این یعنی معماری سنجیده، پایش مفید و توجه به جزئیاتی که کاربر واقعاً حس می‌کند."
        profile.stack_title1_en = "Technologies I"
        profile.stack_title1_fa = "فناوری‌هایی که"
        profile.stack_title2_en = "build with."
        profile.stack_title2_fa = "با آن‌ها می‌سازم."
        profile.stack_sub_en = "A practical toolkit focused on backend depth, automation, and shipping products that hold up in production."
        profile.stack_sub_fa = "جعبه‌ابزاری عملیاتی با تمرکز بر عمق بک‌اند، اتوماسیون و عرضه محصولاتی که در تولید دوام می‌آورند."
        profile.career_title1_en = "A career"
        profile.career_title1_fa = "یک مسیر"
        profile.career_title2_en = "journey."
        profile.career_title2_fa = "حرفه‌ای."
        profile.career_sub_en = "A focused path through backend, automation, financial systems, and product engineering | built one production system at a time."
        profile.career_sub_fa = "مسیری متمرکز در بک‌اند، اتوماسیون، سیستم‌های مالی و مهندسی محصول | ساخته‌شده یک سیستم تولیدی در هر گام."
        profile.projects_title1_en = "Featured"
        profile.projects_title1_fa = "کارهای"
        profile.projects_title2_en = "work."
        profile.projects_title2_fa = "شاخص."
        profile.projects_sub_en = "A selection of systems, tools, and products I've built | focused on real reliability, automation, and user value."
        profile.projects_sub_fa = "گزیده‌ای از سیستم‌ها، ابزارها و محصولاتی که ساخته‌ام | با تمرکز بر قابلیت اطمینان واقعی، اتوماسیون و ارزش برای کاربر."
        profile.content_title1_en = "Where I"
        profile.content_title1_fa = "کجا"
        profile.content_title2_en = "share & connect."
        profile.content_title2_fa = "محتوا منتشر می‌کنم."
        profile.content_sub_en = "I create technical content and stay active across a few channels. Pick the one you prefer."
        profile.content_sub_fa = "محتوای فنی تولید می‌کنم و در چند کانال فعالم. هر کدام را ترجیح می‌دهید انتخاب کنید."
        profile.contact_title1_en = "Let's build"
        profile.contact_title1_fa = "بیایید چیز"
        profile.contact_title2_en = "something reliable."
        profile.contact_title2_fa = "قابل‌اعتمادی بسازیم."
        profile.contact_sub_en = "Open to collaboration on distributed systems, FinTech, automation tooling, and product engineering. Reach out | I'd love to hear what you're working on."
        profile.contact_sub_fa = "آماده همکاری در سیستم‌های توزیع‌شده، فین‌تک، ابزارهای اتوماسیون و مهندسی محصول. خوشحال می‌شوم درباره کار شما بشنوم."
        profile.contact_telegram_url = "https://t.me/unique174"
        profile.contact_email = "damerchiloa@gmail.com"
        profile.telegram_cta_en = "Message on Telegram"
        profile.telegram_cta_fa = "پیام در تلگرام"
        profile.email_cta_en = "Send an Email"
        profile.email_cta_fa = "ارسال ایمیل"
        profile.footer_copy_en = "All rights reserved for Abbas Damerchi"
        profile.footer_copy_fa = "تمامی حقوق برای عباس دمرچی محفوظ است"
        profile.github_url = "https://Github.com/irAbs174"
        profile.linkedin_url = "https://t.co/CMG342dwq6"
        profile.x_url = "https://x.com/abbasdamerchi"
        attach(profile.portrait, "abbas-portrait.jpg")
        attach(profile.brand_logo, "header-logo.webp")
        profile.save()

        focuses = [
            ("🏗️", "Distributed systems & backend architecture", "سیستم‌های توزیع‌شده و معماری بک‌اند"),
            ("💳", "FinTech · transactions · automation", "فین‌تک · تراکنش · اتوماسیون"),
            ("🛒", "End-to-end e-commerce systems", "سیستم‌های تجارت الکترونیک سرتاسری"),
            ("🎨", "Product UX · accessibility · SEO", "تجربه کاربری · دسترسی‌پذیری · سئو"),
        ]
        AboutFocus.objects.bulk_create(
            [
                AboutFocus(icon=icon, title_en=en, title_fa=fa, order=i)
                for i, (icon, en, fa) in enumerate(focuses)
            ]
        )

        tech = [
            ("Python", "backend", "https://cdn.simpleicons.org/python/3776AB"),
            ("Go", "backend", "https://cdn.simpleicons.org/go/00ADD8"),
            ("Node.js", "backend", "https://cdn.simpleicons.org/nodedotjs/339933"),
            ("TypeScript", "backend", "https://cdn.simpleicons.org/typescript/3178C6"),
            ("PostgreSQL", "data", "https://cdn.simpleicons.org/postgresql/4169E1"),
            ("Redis", "data", "https://cdn.simpleicons.org/redis/DC382D"),
            ("MongoDB", "data", "https://cdn.simpleicons.org/mongodb/47A248"),
            ("Docker", "devops", "https://cdn.simpleicons.org/docker/2496ED"),
            ("Linux", "devops", "https://cdn.simpleicons.org/linux/FCC624"),
            ("Nginx", "devops", "https://cdn.simpleicons.org/nginx/009639"),
            ("Git", "tools", "https://cdn.simpleicons.org/git/F05032"),
            ("React", "frontend", "https://cdn.simpleicons.org/react/61DAFB"),
            ("Next.js", "frontend", "https://cdn.simpleicons.org/nextdotjs/000000"),
            ("HTML / CSS", "frontend", "https://cdn.simpleicons.org/html5/E34F26"),
        ]
        TechItem.objects.bulk_create(
            [TechItem(name=n, category=c, logo_url=u, order=i) for i, (n, c, u) in enumerate(tech)]
        )

        careers = [
            dict(
                role_en="Backend / Distributed Systems Engineer",
                role_fa="مهندس بک‌اند / سیستم‌های توزیع‌شده",
                company_en="Independent · Production Systems",
                company_fa="مستقل · سیستم‌های تولیدی",
                period_en="2022 | Present",
                period_fa="۲۰۲۲ | اکنون",
                description_en="Designing and shipping distributed backends, FinTech transaction pipelines, and end-to-end e-commerce automations. Focused on reliability, observability, and clean product UX.",
                description_fa="طراحی و عرضه بک‌اندهای توزیع‌شده، خطوط تراکنش فین‌تک و اتوماسیون تجارت الکترونیک سرتاسری. تمرکز روی قابلیت اطمینان، مشاهده‌پذیری و تجربه کاربری تمیز محصول.",
                tags=["Python", "Go", "PostgreSQL", "Redis", "Docker", "Linux"],
            ),
            dict(
                role_en="Automation & E-Commerce Engineer",
                role_fa="مهندس اتوماسیون و تجارت الکترونیک",
                company_en="Commerce Platforms",
                company_fa="پلتفرم‌های تجارت",
                period_en="2020 | 2022",
                period_fa="۲۰۲۰ | ۲۰۲۲",
                description_en="Built automation tooling and integrations for online commerce operations | from catalog and order pipelines to financial reconciliation flows.",
                description_fa="ساخت ابزارهای اتوماسیون و یکپارچه‌سازی برای عملیات تجارت آنلاین | از کاتالوگ و خط سفارش تا جریان‌های تطبیق مالی.",
                tags=["Node.js", "APIs", "Workflow Automation", "Integrations"],
            ),
            dict(
                role_en="Product & Full-Stack Engineer",
                role_fa="مهندس محصول و فول‌استک",
                company_en="Web Products",
                company_fa="محصولات وب",
                period_en="2018 | 2020",
                period_fa="۲۰۱۸ | ۲۰۲۰",
                description_en="Shipped user-facing web products end-to-end. Backend services, frontend interfaces, SEO-driven content systems, and the connective tissue between them.",
                description_fa="عرضه محصولات وب کاربرمحور از ابتدا تا انتها. سرویس‌های بک‌اند، رابط‌های فرانت‌اند، سیستم‌های محتوای مبتنی بر سئو و اتصال میان آن‌ها.",
                tags=["JavaScript", "React", "SEO", "Product UX"],
            ),
            dict(
                role_en="Computer Science & Technical Content",
                role_fa="علوم کامپیوتر و محتوای فنی",
                company_en="YouTube · Medium · GitHub",
                company_fa="YouTube · Medium · GitHub",
                period_en="Ongoing",
                period_fa="ادامه دارد",
                description_en="Documenting computer science fundamentals, system design, and engineering practice through long-form content, tutorials, and open repositories.",
                description_fa="مستندسازی مبانی علوم کامپیوتر، طراحی سیستم و تمرین مهندسی از طریق محتوای بلند، آموزش و مخازن متن‌باز.",
                tags=["Writing", "Teaching", "Open Source"],
            ),
        ]
        CareerEntry.objects.bulk_create(
            [CareerEntry(order=i, **row) for i, row in enumerate(careers)]
        )

        projects = [
            dict(
                title_en="Distributed Transaction Pipeline",
                title_fa="خط لوله تراکنش توزیع‌شده",
                description_en="A fault-tolerant transaction processing pipeline for financial workflows | designed for reliability, observability, and operational simplicity.",
                description_fa="خط پردازش تراکنش تحمل‌پذیر خطا برای جریان‌های مالی | طراحی‌شده برای قابلیت اطمینان، مشاهده‌پذیری و سادگی عملیاتی.",
                tags=["Python", "PostgreSQL", "Redis", "Queues"],
                image="abbas-trip.jpg",
                links=[("GitHub", "https://Github.com/irAbs174")],
            ),
            dict(
                title_en="E-Commerce Automation Suite",
                title_fa="مجموعه اتوماسیون تجارت الکترونیک",
                description_en="End-to-end automation for online commerce: catalog sync, order orchestration, pricing, and reporting | replacing repetitive ops with reliable systems.",
                description_fa="اتوماسیون سرتاسری تجارت آنلاین: همگام‌سازی کاتالوگ، ارکستراسیون سفارش، قیمت‌گذاری و گزارش | جایگزینی کارهای تکراری با سیستم‌های قابل اعتماد.",
                tags=["Node.js", "APIs", "Workflows"],
                image="abbas-luggage.jpg",
                links=[("GitHub", "https://Github.com/irAbs174")],
            ),
            dict(
                title_en="System Design Notes & Resources",
                title_fa="یادداشت‌ها و منابع طراحی سیستم",
                description_en="A growing library of system design, distributed systems, and backend engineering notes | practical, opinionated, and built for engineers.",
                description_fa="کتابخانه‌ای در حال رشد از یادداشت‌های طراحی سیستم، سیستم‌های توزیع‌شده و مهندسی بک‌اند | عملی، نظرمند و ساخته‌شده برای مهندسان.",
                tags=["Markdown", "Education", "Open Source"],
                image="abbas-portrait.jpg",
                links=[
                    ("GitHub", "https://Github.com/irAbs174"),
                    ("Medium", "https://abbas-damerchi.Medium.com"),
                ],
            ),
            dict(
                title_en="SEO-Driven Product Framework",
                title_fa="چارچوب محصول مبتنی بر سئو",
                description_en="A framework for building discoverable, content-driven web products | combining SEO, performance, and a clean developer experience.",
                description_fa="چارچوبی برای ساخت محصولات وب قابل کشف و محتوا‌محور | ترکیبی از سئو، کارایی و تجربه توسعه‌دهنده تمیز.",
                tags=["Next.js", "TypeScript", "SEO"],
                image="abbas-trip.jpg",
                links=[("GitHub", "https://Github.com/irAbs174")],
            ),
        ]
        for i, row in enumerate(projects):
            links = row.pop("links")
            image_name = row.pop("image")
            project = Project.objects.create(order=i, **row)
            attach(project.image, image_name)
            project.save()
            ProjectLink.objects.bulk_create(
                [
                    ProjectLink(project=project, title=label, url=href, type=_link_type(label), order=j)
                    for j, (label, href) in enumerate(links)
                ]
            )

        socials = [
            ("YouTube", "یوتیوب", "@Unique_Sources", "yt", "https://cdn.simpleicons.org/youtube/FFFFFF", "https://YouTube.com/@Unique_Sources", False),
            ("Facebook", "فیسبوک", "/abbasDamerchilo", "fb", "https://cdn.simpleicons.org/facebook/FFFFFF", "https://www.facebook.com/abbasDamerchilo/", False),
            ("Instagram", "اینستاگرام", "@irAbs174", "ig", "https://cdn.simpleicons.org/instagram/FFFFFF", "https://www.instagram.com/irAbs174", False),
            ("GitHub", "گیت هاب", "@irAbs174", "gh", "https://cdn.simpleicons.org/github/FFFFFF", "https://Github.com/irAbs174", True),
            ("Reddit", "Reddit", "u/abbas-damerchi", "rd", "https://cdn.simpleicons.org/reddit/FFFFFF", "https://www.reddit.com/user/abbas-damerchi/", False),
            ("LinkedIn", "لینکدین", "in/abbas-damerchi", "li", "img/linkedin.svg", "https://t.co/CMG342dwq6", True),
            ("Medium", "Medium", "@abbas-damerchi", "med", "https://cdn.simpleicons.org/medium/FFFFFF", "https://abbas-damerchi.Medium.com", False),
            ("Blogsky", "وبلاگ بلاگ اسکای", "nahad1.blogsky.com", "bs", "https://cdn.simpleicons.org/blogger/FFFFFF", "https://nahad1.blogsky.com/", False),
            ("Discord", "Discord", "Unique Sources", "disc", "https://cdn.simpleicons.org/discord/FFFFFF", "https://discord.gg/DeHWVZRKS4", False),
            ("Telegram", "Telegram", "@Unique_Sources", "tg", "https://cdn.simpleicons.org/telegram/FFFFFF", "https://t.me/Unique_Sources", False),
            ("X", "X", "@abbasdamerchi", "x", "https://cdn.simpleicons.org/x/FFFFFF", "https://x.com/abbasdamerchi", True),
            ("Namasha", "نماشا", "unique.sources", "nm", "https://cdn.simpleicons.org/youtube/FFFFFF", "https://www.namasha.com/unique.sources", False),
            ("Aparat", "آپارات", "unique174", "ap", "https://cdn.simpleicons.org/youtube/FFFFFF", "https://www.aparat.com/unique174", False),
            ("Unique NFT", "NFT Market", "getgems.io/Unique-NFT", "nft", "https://cdn.simpleicons.org/opensea/FFFFFF", "https://getgems.io/Unique-NFT", False),
            ("DM Telegram", "DM Telegram", "@unique174", "tg", "https://cdn.simpleicons.org/telegram/FFFFFF", "https://t.me/unique174", False),
            ("Bale", "پیام رسان بله", "@unique174", "bale", "https://cdn.simpleicons.org/telegram/FFFFFF", "https://web.bale.ai/@unique174", False),
        ]
        SocialChannel.objects.bulk_create(
            [
                SocialChannel(
                    name_en=en,
                    name_fa=fa,
                    handle=handle,
                    css_class=cls,
                    icon_url=icon,
                    href=href,
                    show_in_footer=footer,
                    order=i,
                )
                for i, (en, fa, handle, cls, icon, href, footer) in enumerate(socials)
            ]
        )

        self.stdout.write(self.style.SUCCESS("Portfolio content seeded."))
