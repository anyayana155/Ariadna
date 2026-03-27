import json
import threading

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.notifications.services import send_email_notification, send_push_notification
from .models import ChatMessage, ChatThread


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        self.room_group_name = f'chat_{self.thread_id}'
        self.user = self.scope['user']

        if self.user.is_anonymous:
            await self.close()
            return

        allowed = await self.user_has_access()
        if not allowed:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        text = (data.get('text') or '').strip()

        if not text:
            return

        message = await self.save_message(text)

        # realtime
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
            }
        )

        # уведомления в фоне (НЕ блокируют сокет)
        threading.Thread(
            target=self.notify_other_side_sync,
            args=(message,),
            daemon=True
        ).start()

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    @database_sync_to_async
    def user_has_access(self):
        try:
            thread = ChatThread.objects.get(id=self.thread_id)
        except ChatThread.DoesNotExist:
            return False

        return self.user.is_staff or thread.user_id == self.user.id

    @database_sync_to_async
    def save_message(self, text):
        thread = ChatThread.objects.get(id=self.thread_id)

        if self.user.is_staff and thread.assigned_admin is None:
            thread.assigned_admin = self.user
            thread.save(update_fields=['assigned_admin'])

        message = ChatMessage.objects.create(
            thread=thread,
            sender=self.user,
            text=text
        )

        return {
            'id': message.id,
            'text': message.text,
            'sender_id': self.user.id,
            'sender_email': self.user.email,
            'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
        }

    def notify_other_side_sync(self, message):
        thread = ChatThread.objects.get(id=self.thread_id)

        if self.user.is_staff:
            recipient = thread.user
        else:
            recipient = thread.assigned_admin
            if recipient is None:
                recipient = (
                    type(self.user).objects
                    .filter(is_staff=True, is_active=True)
                    .order_by('id')
                    .first()
                )

        if not recipient:
            return

        try:
            send_email_notification(
                recipient,
                subject='Новое сообщение в чате — Ариадна',
                message=f'У вас новое сообщение:\n\n{message["text"]}',
                category='chat',
            )

            send_push_notification(
                recipient,
                title='Новое сообщение',
                body=message['text'][:120],
                url=f'/chat/{self.thread_id}/',
                category='chat',
            )
        except Exception as e:
            print('NOTIFICATION ERROR:', e)
