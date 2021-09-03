from django.urls import re_path

from .consumers import group_consumer


websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<pk>\d+)/$', group_consumer.ChatConsumer.as_asgi())
]
