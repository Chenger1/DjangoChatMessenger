import abc
import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

from django.db.models import Q

from _db.models import Group, Message, User, PersonalChat


class BaseChatConsumer(abc.ABC, WebsocketConsumer):
    def connect(self):
        self.pk = self.scope['url_route']['kwargs']['pk']
        self.instance = self.get_instance()
        if not self.instance:
            self.close()

        self.group_name = self.get_group_name()

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

        self.action_after_accept()

        self.restore_chat_history()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message_text = text_data_json['message']
        message = self.save_message(message_text)

        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
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
        for message in self.instance.messages.all().order_by():
            data = {
                'type': 'chat_message',
                'message': message.text,
                'user': message.user.username,
                'user_id': message.user.pk,
                'created': message.created.isoformat()
            }
            async_to_sync(self.channel_layer.group_send)(
                self.group_name,
                data
            )

    @abc.abstractmethod
    def save_message(self, message_text):
        pass

    @abc.abstractmethod
    def action_after_accept(self):
        """
        For example, add user to group after connection established
        """
        pass

    @abc.abstractmethod
    def get_group_name(self):
        pass

    @abc.abstractmethod
    def get_instance(self):
        """
        For public groups (Group) getting instance is just filter by pk.
        But for Personal Chat we have to filter by sender and receiver field.
        WebSocket doesnt not provide an ability to add headers, so we cant pass 'pk' to url and 'user' to headers -
        in the case to create a chat if there is no existing one.
        """
        pass


class ChatConsumer(BaseChatConsumer):
    def get_instance(self):
        instance = Group.objects.filter(pk=self.pk).first()
        return instance

    def get_group_name(self):
        return self.instance.name

    def action_after_accept(self):
        self.instance.users.add(self.scope['user'])

    def save_message(self, message_text):
        message = Message.objects.create(text=message_text,
                                         user=self.scope['user'],
                                         group=self.instance)
        return message


class PersonalChatConsumer(BaseChatConsumer):
    def get_instance(self):
        user = User.objects.filter(pk=self.pk).first()
        if not user:
            return

        instance = PersonalChat.objects.filter(Q(sender=self.scope['user'])
                                               | Q(receiver=self.scope['user'])).\
            filter(Q(sender=user) | Q(receiver=user)).first()
        if not instance:
            instance = PersonalChat.objects.create(sender=self.scope['user'],
                                                   receiver=user)
        return instance

    def get_group_name(self):
        return f'chat_{self.instance.pk}'

    def save_message(self, message_text):
        message = Message.objects.create(text=message_text,
                                         user=self.scope['user'],
                                         personal_chat=self.instance)
        return message

    def action_after_accept(self):
        pass
