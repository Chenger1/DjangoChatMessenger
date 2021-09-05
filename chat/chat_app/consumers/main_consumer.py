import json
from channels.generic.websocket import AsyncWebsocketConsumer


class MainNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'main_socket'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message.text
            }
        )

    async def chat_message(self, event):
        # method has the same name as 'type' in 'receive' method
        # to match the type key and
        # send message to WebSocket
        await self.send(text_data=json.dumps(event))
