document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.querySelector('[data-nav-toggle]');
    const collapse = document.querySelector('[data-nav-collapse]');
    const overlay = document.querySelector('[data-nav-overlay]');

    if (!toggle || !collapse) return;

    function closeMenu() {
        collapse.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
        if (overlay) overlay.hidden = true;
    }

    function openMenu() {
        collapse.classList.add('is-open');
        toggle.setAttribute('aria-expanded', 'true');
        if (overlay) overlay.hidden = false;
    }

    toggle.addEventListener('click', () => {
        collapse.classList.contains('is-open') ? closeMenu() : openMenu();
    });

    if (overlay) {
        overlay.addEventListener('click', closeMenu);
    }

    const closeBtn = document.querySelector('[data-nav-close]');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeMenu);
    }

    document.addEventListener('click', (e) => {
        if (!toggle.contains(e.target) && !collapse.contains(e.target)) {
            closeMenu();
        }
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth >= 768) {
            closeMenu();
        }
    });
});
