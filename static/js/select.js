document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-select]').forEach((wrapper) => {
        const trigger = wrapper.querySelector('[data-select-trigger]');
        const optionsList = wrapper.querySelector('[data-select-options]');
        const label = wrapper.querySelector('[data-select-label]');
        const nativeSelect = wrapper.querySelector('select');
        const options = wrapper.querySelectorAll('[data-select-option], .c-select__option');

        function closeList() {
            optionsList.hidden = true;
            trigger.setAttribute('aria-expanded', 'false');
        }

        function openList() {
            optionsList.hidden = false;
            trigger.setAttribute('aria-expanded', 'true');
        }

        function selectOption(option) {
            const value = option.dataset.value;
            const text = option.textContent;
            nativeSelect.value = value;
            nativeSelect.dispatchEvent(new Event('change'));
            label.textContent = text;
            options.forEach(o => o.setAttribute('aria-selected', 'false'));
            option.setAttribute('aria-selected', 'true');
            closeList();
            trigger.focus();
        }

        trigger.addEventListener('click', () => {
            optionsList.hidden ? openList() : closeList();
        });

        options.forEach((option) => {
            option.addEventListener('click', () => selectOption(option));
            option.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    selectOption(option);
                }
            });
        });

        document.addEventListener('click', (e) => {
            if (!wrapper.contains(e.target)) closeList();
        });

        wrapper.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeList();
                trigger.focus();
            }
        });
    });
});
