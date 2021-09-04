from django.urls import re_path

from .consumers import group_consumer


websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<pk>\d+)/$', group_consumer.ChatConsumer.as_asgi()),
    re_path(r'ws/chat/personal/(?P<pk>\d+)/$', group_consumer.PersonalChatConsumer.as_asgi())
]
