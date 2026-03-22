document.addEventListener('DOMContentLoaded', () => {
    const card = document.getElementById('swipe-card');
    if (!card) return;

    const titleEl = document.getElementById('card-title');
    const descEl = document.getElementById('card-description');
    const addressEl = document.getElementById('card-address');
    const checkEl = document.getElementById('card-check');
    const imageEl = document.getElementById('card-image');
    const detailLink = document.getElementById('card-detail-link');

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
            card.innerHTML = `
                <div class="empty-feed">
                    <p>Карточки закончились.</p>
                    <a href="/places/">Открыть все места</a>
                </div>
            `;
            return;
        }

        if (data.next_place) {
            const next = data.next_place;
            card.dataset.placeId = next.id;
            titleEl.textContent = next.title;
            descEl.textContent = next.short_description;
            addressEl.textContent = next.address;
            checkEl.textContent = next.average_check ? `${next.average_check} ₽` : 'Не указан';
            detailLink.href = next.detail_url;

            if (imageEl && next.image_url) {
                imageEl.src = next.image_url;
                imageEl.alt = next.title;
            }

            card.classList.remove('swipe-left', 'swipe-right');
        }
    }

    document.querySelectorAll('[data-action]').forEach(button => {
        button.addEventListener('click', async () => {
            const action = button.dataset.action;

            if (action === 'like') {
                card.classList.add('swipe-right');
            } else if (action === 'dislike') {
                card.classList.add('swipe-left');
            }

            setTimeout(() => sendAction(action), 180);
        });
    });

    let startX = 0;
    let currentX = 0;
    let isDragging = false;

    card.addEventListener('pointerdown', (e) => {
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
});
