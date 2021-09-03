import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from _db.models import Group


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.pk = self.scope['url_route']['kwargs']['pk']
        group = Group.objects.filter(pk=self.pk).first()
        if not group:
            self.disconnect()
        self.chat_group_name = group.name

        # join chat group
        async_to_sync(self.channel_layer.group_add)(
            self.chat_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chat_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # broadcast messaging
        async_to_sync(self.channel_layer.group_send)(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def chat_message(self, event):
        # method has the same name as 'type' in 'receive' method
        # to match the type key and
        # send message to WebSocket
        self.send(text_data=json.dumps(event))
