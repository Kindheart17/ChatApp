from django.urls import path
from . import consumers


websocket_urlpatterns = [
    path('chat/<int:convId>/', consumers.ChatConsumer.as_asgi()),
    path('chat/crop-image/<int:convId>/', consumers.ChatConsumer.as_asgi()),
]