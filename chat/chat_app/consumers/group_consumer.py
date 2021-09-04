import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from _db.models import Group, Message


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.pk = self.scope['url_route']['kwargs']['pk']
        self.group = Group.objects.filter(pk=self.pk).first()
        if not self.group:
            self.close()
        self.chat_group_name = self.group.name

        # join chat group
        async_to_sync(self.channel_layer.group_add)(
            self.chat_group_name,
            self.channel_name
        )
        self.accept()
        self.group.users.add(self.scope['user'])

        self.restore_chat_history()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chat_group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message_text = text_data_json['message']
        message = Message.objects.create(text=message_text,
                                         user=self.scope['user'],
                                         group=self.group)

        # broadcast messaging
        async_to_sync(self.channel_layer.group_send)(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'message': message.text,
                'user': message.user.username,
                'user_id': message.user.pk,
                'created': message.created.isoformat()
            }
        )

    def chat_message(self, event):
        # method has the same name as 'type' in 'receive' method
        # to match the type key and
        # send message to WebSocket
        self.send(text_data=json.dumps(event))

    def restore_chat_history(self):
        # When user access to channel - restore all previous message from this channel
        for message in self.group.messages.all().order_by():
            data = {
                'type': 'chat_message',
                'message': message.text,
                'user': message.user.username,
                'user_id': message.user.pk,
                'created': message.created.isoformat()
            }
            async_to_sync(self.channel_layer.group_send)(
                self.chat_group_name,
                data
            )

