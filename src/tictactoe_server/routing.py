from django.urls import path, re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from tictactoe_server import consumers

websocket_urlpatterns = [
    re_path(r'ws/server/$', consumers.GameConsumer.as_asgi()),
]