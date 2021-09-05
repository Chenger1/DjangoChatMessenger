from channels.db import database_sync_to_async

from .models import Message


async def get_instance_async(pk, model):
    return await get_instance(pk, model)


@database_sync_to_async
def get_instance(pk, model):
    return model.objects.filter(pk=pk).first()


async def get_all_messages_async(model):
    return await get_all_messages(model)


@database_sync_to_async
def get_all_messages(model):
    """
    Cant call sync django orm from async context. But QuerySet is laze
    So we have to transform it to list before return
    """
    return list(model.messages.all().order_by())


async def save_user_to_instance_async(instance, user):
    return await save_user_to_instance(instance, user)


@database_sync_to_async
def save_user_to_instance(instance, user):
    instance.users.add(user)


async def save_message_async(data):
    return await save_message(data)


@database_sync_to_async
def save_message(data):
    message = Message.objects.create(**data)
    return message


async def get_message_user_async(message):
    return await get_message_user(message)


@database_sync_to_async
def get_message_user(message):
    user = message.user
    return user.username, user.pk
