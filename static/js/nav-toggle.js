document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.querySelector('[data-nav-toggle]');
    const collapse = document.querySelector('[data-nav-collapse]');

    if (!toggle || !collapse) return;

    toggle.addEventListener('click', () => {
        const isOpen = collapse.classList.toggle('is-open');
        toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    document.addEventListener('click', (e) => {
        if (!toggle.contains(e.target) && !collapse.contains(e.target)) {
            collapse.classList.remove('is-open');
            toggle.setAttribute('aria-expanded', 'false');
        }
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth >= 768) {
            collapse.classList.remove('is-open');
            toggle.setAttribute('aria-expanded', 'false');
        }
    });
});
