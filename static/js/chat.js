document.addEventListener('DOMContentLoaded', () => {
    const messagesEl = document.getElementById('chat-messages');
    const form = document.getElementById('chat-form');
    const input = document.getElementById('chat-input');

    if (!messagesEl || !form || !input) return;

    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const socket = new WebSocket(`${protocol}://${window.location.host}/ws/chat/${CHAT_THREAD_ID}/`);

    socket.onmessage = function (e) {
        const data = JSON.parse(e.data);

        const wrapper = document.createElement('div');
        wrapper.style.marginBottom = '14px';

        if (String(data.sender_id) === String(CURRENT_USER_ID)) {
            wrapper.style.textAlign = 'right';
        }

        wrapper.innerHTML = `
            <div style="font-size:12px;color:#666;">${data.sender_email} · ${data.created_at}</div>
            <div style="
                display:inline-block;
                margin-top:4px;
                padding:10px 14px;
                border-radius:12px;
                background:${String(data.sender_id) === String(CURRENT_USER_ID) ? '#d66b52' : '#f1ece7'};
                color:${String(data.sender_id) === String(CURRENT_USER_ID) ? 'white' : '#222'};
            "></div>
        `;

        wrapper.querySelector('div:last-child').textContent = data.text;
        messagesEl.appendChild(wrapper);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    };

    socket.onopen = function () {
        console.log('WebSocket connected');
    };

    socket.onclose = function (e) {
        console.log('WebSocket closed', e);
    };

    socket.onerror = function (e) {
        console.error('WebSocket error', e);
    };

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const text = input.value.trim();
        if (!text) return;

        socket.send(JSON.stringify({ text }));
        input.value = '';
    });
});
