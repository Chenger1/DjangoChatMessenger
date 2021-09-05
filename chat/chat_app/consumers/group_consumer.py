import abc
import json
from channels.generic.websocket import AsyncWebsocketConsumer

from django.urls import reverse

from _db.models import Group, PersonalChat
from _db import async_crud


class BaseChatConsumer(abc.ABC, AsyncWebsocketConsumer):
    model = None

    async def connect(self):
        self.pk = self.scope['url_route']['kwargs']['pk']
        self.instance = await async_crud.get_instance_async(self.pk, self.model)
        if not self.instance:
            await self.close()

        self.group_name = self.get_group_name()

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        await self.action_after_accept()

        await self.restore_chat_history()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message_text = text_data_json['message']
        message = await self.save_message(message_text)

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message.text,
                'user': message.user.username,
                'user_id': message.user.pk,
                'created': message.created.isoformat()
            }
        )

        await self.send_notifications()

    async def chat_message(self, event):
        # method has the same name as 'type' in 'receive' method
        # to match the type key and
        # send message to WebSocket
        await self.send(text_data=json.dumps(event))

    async def restore_chat_history(self):
        # When user access to channel - restore all previous message from this channel
        messages = await async_crud.get_all_messages_async(self.instance)
        for message in messages:
            username, pk = await async_crud.get_message_user_async(message)
            data = {
                'type': 'chat_message',
                'message': message.text,
                'user': username,
                'user_id': pk,
                'created': message.created.isoformat()
            }

            await self.channel_layer.group_send(
                self.group_name,
                data
            )

    async def send_notifications(self):
        chat_source, chat_url = self.get_chat_source()

        await self.channel_layer.group_send(
            'main_socket',
            {
                'type': 'chat_message',
                'message': f'You have new message from {chat_source}',
                'chat_url': chat_url
            }
        )

    @abc.abstractmethod
    async def save_message(self, message_text):
        pass

    @abc.abstractmethod
    async def action_after_accept(self):
        """
        For example, add user to group after connection established
        """
        pass

    @abc.abstractmethod
    def get_group_name(self):
        pass

    @abc.abstractmethod
    def get_chat_source(self):
        pass


class ChatConsumer(BaseChatConsumer):
    model = Group

    def get_group_name(self):
        return self.instance.name

    async def action_after_accept(self):
        await async_crud.save_user_to_instance_async(self.instance, self.scope['user'])

    async def save_message(self, message_text):
        save_data = {
            'text': message_text,
            'user': self.scope['user'],
            'group': self.instance
        }
        return await async_crud.save_message_async(save_data)

    def get_chat_source(self):
        return f'Group: {self.instance.name}', reverse('chat_app:group_detail_view', args=[self.instance.pk])


class PersonalChatConsumer(BaseChatConsumer):
    model = PersonalChat

    def get_group_name(self):
        return f'chat_{self.instance.pk}'

    async def save_message(self, message_text):
        save_data = {
            'text': message_text,
            'user': self.scope['user'],
            'personal_chat': self.instance
        }
        return await async_crud.save_message_async(save_data)

    def get_chat_source(self):
        return 'Personal Chat', reverse('chat_app:personal_chat_view', args=[self.pk])

    async def action_after_accept(self):
        pass
