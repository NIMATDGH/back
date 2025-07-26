import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message, Channel
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.channel_id = self.scope['url_route']['kwargs']['channel_pk']
        self.room_group_name = f'chat_{self.channel_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        author_user = self.scope['user']

        # Save message to database
        new_message = await self.save_message(author_user, self.channel_id, message_content)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': new_message.content,
                'author': new_message.author.username
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        author = event['author']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'author': author
        }))

    @sync_to_async
    def save_message(self, author, channel_id, message):
        channel = Channel.objects.get(id=channel_id)
        return Message.objects.create(author=author, channel=channel, content=message)