import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from django.db.models import Q

from _db.models import Group, Message, User, PersonalChat


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


class PersonalChatConsumer(WebsocketConsumer):
    def connect(self):
        pk = self.scope['url_route']['kwargs']['pk']
        user = User.objects.filter(pk=pk).first()
        if not user:
            self.close()

        self.chat = PersonalChat.objects.filter(Q(sender=self.scope['user'])
                                                | Q(receiver=self.scope['user'])).\
            filter(Q(sender=user) | Q(receiver=user)).first()

        if not self.chat:
            self.chat = PersonalChat.objects.create(sender=self.scope['user'],
                                                    receiver=user)

        self.chat_name = f'chat_{self.chat.pk}'

        async_to_sync(self.channel_layer.group_add)(
            self.chat_name,
            self.channel_name
        )
        self.accept()

        self.restore_chat_history()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chat_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message_text = text_data_json['message']
        message = Message.objects.create(text=message_text,
                                         user=self.scope['user'],
                                         personal_chat=self.chat)

        async_to_sync(self.channel_layer.group_send)(
            self.chat_name,
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
        for message in self.chat.messages.all().order_by():
            data = {
                'type': 'chat_message',
                'message': message.text,
                'user': message.user.username,
                'user_id': message.user.pk,
                'created': message.created.isoformat()
            }
            async_to_sync(self.channel_layer.group_send)(
                self.chat_name,
                data
            )
