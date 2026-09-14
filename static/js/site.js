document.addEventListener('DOMContentLoaded', () => {
    const store = {
        get theme() { return localStorage.getItem('theme') || 'dark'; },
        set theme(v) { localStorage.setItem('theme', v); },
    };

    function applyTheme() {
        document.documentElement.setAttribute('data-theme', store.theme);
        const icon = document.getElementById('themeIcon');
        if (!icon) return;
        if (store.theme === 'light') {
            icon.innerHTML = '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>';
        } else {
            icon.innerHTML = '<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>';
        }
    }

    const themeBtn = document.getElementById('themeBtn');
    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            store.theme = store.theme === 'dark' ? 'light' : 'dark';
            applyTheme();
        });
    }

    const langBtn = document.getElementById('langBtn');
    const langForm = document.getElementById('langForm');
    if (langBtn && langForm) {
        langBtn.addEventListener('click', () => langForm.submit());
    }

    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => navLinks.classList.toggle('open'));
        navLinks.addEventListener('click', e => {
            if (e.target.tagName === 'A') navLinks.classList.remove('open');
        });
    }

    window.addEventListener('scroll', () => {
        const top = window.scrollY;
        const height = document.documentElement.scrollHeight - window.innerHeight;
        const pct = height > 0 ? (top / height) * 100 : 0;
        const bar = document.getElementById('progressBar');
        if (bar) bar.style.width = pct + '%';
    }, { passive: true });

    const io = new IntersectionObserver(entries => {
        entries.forEach(e => {
            if (e.isIntersecting) {
                e.target.classList.add('in');
                io.unobserve(e.target);
            }
        });
    }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });
    document.querySelectorAll('.reveal').forEach(el => io.observe(el));

    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener('click', e => {
            const id = a.getAttribute('href');
            if (id.length > 1 && document.querySelector(id)) {
                e.preventDefault();
                document.querySelector(id).scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    applyTheme();
});
