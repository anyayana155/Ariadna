document.addEventListener('DOMContentLoaded', () => {
    const nameInput = document.getElementById('guest-name');
    const startBtn = document.getElementById('start-btn');

    if (nameInput) {
        const savedName = localStorage.getItem('ariadna_guest_name');
        if (savedName) {
            nameInput.value = savedName;
        }

        nameInput.addEventListener('input', () => {
            localStorage.setItem('ariadna_guest_name', nameInput.value.trim());
        });
    }

    if (startBtn && nameInput) {
        startBtn.addEventListener('click', () => {
            localStorage.setItem('ariadna_guest_name', nameInput.value.trim());
        });
    }
});