document.addEventListener('DOMContentLoaded', () => {
    if (window.__chatInitialized) {
        console.log('CHAT ALREADY INITIALIZED');
        return;
    }
    window.__chatInitialized = true;

    const messagesEl = document.getElementById('chat-messages');
    const form = document.getElementById('chat-form');
    const input = document.getElementById('chat-input');

    if (!messagesEl || !form || !input) {
        console.log('CHAT INIT SKIPPED', {
            hasMessages: !!messagesEl,
            hasForm: !!form,
            hasInput: !!input,
        });
        return;
    }

    let socket = null;
    let reconnectTimer = null;
    let manuallyClosed = false;
    let isConnecting = false;

    function appendMessage(data) {
        const existing = document.querySelector(`[data-message-id="${data.id}"]`);
        if (existing) return;

        const wrapper = document.createElement('div');
        wrapper.style.marginBottom = '14px';
        wrapper.dataset.messageId = String(data.id);

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
    }

    function connectSocket() {
        if (manuallyClosed) {
            return;
        }

        if (isConnecting) {
            console.log('WS CONNECT SKIPPED: already connecting');
            return;
        }

        if (socket && (
            socket.readyState === WebSocket.OPEN ||
            socket.readyState === WebSocket.CONNECTING
        )) {
            console.log('WS CONNECT SKIPPED: socket already active', socket.readyState);
            return;
        }

        const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
        const url = `${protocol}://${window.location.host}/ws/chat/${CHAT_THREAD_ID}/`;

        isConnecting = true;
        console.log('WS CONNECTING', url);

        socket = new WebSocket(url);
        window.__chatSocket = socket;

        socket.onopen = function () {
            isConnecting = false;
            console.log('WS OPEN');
            messagesEl.scrollTop = messagesEl.scrollHeight;
        };

        socket.onmessage = function (e) {
            console.log('WS MESSAGE RAW', e.data);

            try {
                const data = JSON.parse(e.data);
                appendMessage(data);
            } catch (err) {
                console.error('WS MESSAGE PARSE ERROR', err, e.data);
            }
        };

        socket.onclose = function (e) {
            isConnecting = false;
            console.log('WS CLOSED', {
                code: e.code,
                reason: e.reason,
                wasClean: e.wasClean,
            });

            if (manuallyClosed) {
                return;
            }

            if (reconnectTimer) {
                clearTimeout(reconnectTimer);
            }

            reconnectTimer = setTimeout(() => {
                reconnectTimer = null;
                connectSocket();
            }, 1500);
        };

        socket.onerror = function (e) {
            console.error('WS ERROR', e);
        };
    }

    connectSocket();

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const text = input.value.trim();
        if (!text) return;

        if (!socket) {
            console.log('WS NOT INITIALIZED');
            return;
        }

        console.log('WS SEND ATTEMPT', {
            readyState: socket.readyState,
            text,
        });

        if (socket.readyState !== WebSocket.OPEN) {
            console.log('WS NOT OPEN, MESSAGE NOT SENT');
            return;
        }

        socket.send(JSON.stringify({ text }));
        input.value = '';
    });

    window.addEventListener('beforeunload', function () {
        manuallyClosed = true;

        if (reconnectTimer) {
            clearTimeout(reconnectTimer);
            reconnectTimer = null;
        }

        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.close(1000, 'page unload');
        }
    });

    messagesEl.scrollTop = messagesEl.scrollHeight;
});
