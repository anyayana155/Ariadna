document.addEventListener('DOMContentLoaded', () => {
    const card = document.getElementById('swipe-card');
    if (!card) return;

    const titleEl = document.getElementById('card-title');
    const shortDescEl = document.getElementById('card-description-short');
    const fullDescEl = document.getElementById('card-description-full');
    const toggleDescBtn = document.getElementById('toggle-description-btn');
    const addressEl = document.getElementById('card-address');
    const metroEl = document.getElementById('card-metro');
    const checkEl = document.getElementById('card-check');
    const detailLink = document.getElementById('card-detail-link');

    const imageWrap = document.getElementById('swipe-image-wrap');
    const prevImageBtn = document.getElementById('prev-image');
    const nextImageBtn = document.getElementById('next-image');
    const expandImageBtn = document.getElementById('expand-image-btn');

    const imageModal = document.getElementById('image-modal');
    const modalImage = document.getElementById('modal-image');
    const closeImageModal = document.getElementById('close-image-modal');

    let galleryImages = [];
    let currentImageIndex = 0;

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function refreshGalleryElements() {
        galleryImages = Array.from(document.querySelectorAll('.card-gallery-image'));
        currentImageIndex = 0;
        renderGallery();
    }

    function renderGallery() {
        galleryImages.forEach((img, index) => {
            img.classList.toggle('hidden', index !== currentImageIndex);
        });
    }

    function buildGalleryHtml(images, title) {
        if (!images || !images.length) {
            return `<div class="no-image">Нет фото</div>`;
        }

        return images.map((img, index) => `
            <img
                class="card-gallery-image ${index !== 0 ? 'hidden' : ''}"
                src="${img}"
                alt="${title}"
            >
        `).join('');
    }

    function openModalWithCurrentImage() {
        if (!galleryImages.length || !imageModal || !modalImage) return;
        modalImage.src = galleryImages[currentImageIndex].src;
        imageModal.classList.remove('hidden');
    }

    function closeModal() {
        if (imageModal) {
            imageModal.classList.add('hidden');
        }
    }

    function setFullDescription(text) {
        if (!fullDescEl || !toggleDescBtn) return;

        if (text && text.trim()) {
            fullDescEl.textContent = text;
            fullDescEl.classList.add('hidden');
            toggleDescBtn.classList.remove('hidden');
            toggleDescBtn.textContent = 'Развернуть описание';
        } else {
            fullDescEl.textContent = '';
            fullDescEl.classList.add('hidden');
            toggleDescBtn.classList.add('hidden');
        }
    }

    async function sendAction(action) {
        const placeId = card.dataset.placeId;

        const response = await fetch(SWIPE_ACTION_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                place_id: placeId,
                action: action,
            }),
        });

        const data = await response.json();

        if (data.done) {
            const shell = document.querySelector('.swipe-card-shell');
            if (shell) {
                shell.innerHTML = `
                    <div class="empty-feed-static">
                        <h2>Карточки закончились</h2>
                        <p>Ты уже просмотрел(а) все доступные места.</p>
                        <a href="/places/" class="btn btn-primary">Открыть все места</a>
                    </div>
                `;
            }
            return;
        }

        const next = data.next_place;
        if (!next) return;

        card.dataset.placeId = next.id;
        titleEl.textContent = next.title || '';
        shortDescEl.textContent = next.short_description || '';
        addressEl.textContent = next.address || '';
        metroEl.textContent = next.metro || 'Не указано';
        checkEl.textContent = next.average_check ? `${next.average_check} ₽` : 'Не указан';
        detailLink.href = next.detail_url || '#';

        setFullDescription(next.full_description || '');

        imageWrap.innerHTML = buildGalleryHtml(next.images || [], next.title || '');
        refreshGalleryElements();

        card.classList.remove('swipe-left', 'swipe-right');
        card.style.transform = '';
    }

    // Кнопки действий
    document.querySelectorAll('[data-action]').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();

            const action = button.dataset.action;

            if (action === 'like') {
                card.classList.add('swipe-right');
            } else if (action === 'dislike') {
                card.classList.add('swipe-left');
            }

            setTimeout(() => sendAction(action), 180);
        });
    });

    // Галерея
    if (prevImageBtn) {
        prevImageBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            if (!galleryImages.length) return;
            currentImageIndex = (currentImageIndex - 1 + galleryImages.length) % galleryImages.length;
            renderGallery();
        });
    }

    if (nextImageBtn) {
        nextImageBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            if (!galleryImages.length) return;
            currentImageIndex = (currentImageIndex + 1) % galleryImages.length;
            renderGallery();
        });
    }

    if (expandImageBtn) {
        expandImageBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            openModalWithCurrentImage();
        });
    }

    if (toggleDescBtn) {
        toggleDescBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();

            const isHidden = fullDescEl.classList.contains('hidden');
            fullDescEl.classList.toggle('hidden');
            toggleDescBtn.textContent = isHidden ? 'Свернуть описание' : 'Развернуть описание';
        });
    }

    if (closeImageModal) {
        closeImageModal.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            closeModal();
        });
    }

    if (imageModal) {
        imageModal.addEventListener('click', (e) => {
            if (e.target === imageModal) {
                closeModal();
            }
        });
    }

    // Свайп всей карточки, но не при клике по интерактивным элементам
    let startX = 0;
    let currentX = 0;
    let isDragging = false;

    card.addEventListener('pointerdown', (e) => {
        if (e.target.closest('button, a, .gallery-arrow, #expand-image-btn, #toggle-description-btn, .modal-close')) {
            return;
        }

        isDragging = true;
        startX = e.clientX;
        card.setPointerCapture(e.pointerId);
    });

    card.addEventListener('pointermove', (e) => {
        if (!isDragging) return;
        currentX = e.clientX - startX;
        card.style.transform = `translateX(${currentX}px) rotate(${currentX / 20}deg)`;
    });

    card.addEventListener('pointerup', async () => {
        if (!isDragging) return;
        isDragging = false;

        if (currentX > 120) {
            card.classList.add('swipe-right');
            await sendAction('like');
        } else if (currentX < -120) {
            card.classList.add('swipe-left');
            await sendAction('dislike');
        }

        card.style.transform = '';
        currentX = 0;
    });

    card.addEventListener('pointercancel', () => {
        isDragging = false;
        currentX = 0;
        card.style.transform = '';
    });

    refreshGalleryElements();
    setFullDescription(fullDescEl ? fullDescEl.textContent : '');
});