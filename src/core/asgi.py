import os
from django.urls import re_path, path

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from products.consumers import ServerSentEventsConsumer
from channels.http import AsgiHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')


application = ProtocolTypeRouter({
    'http': URLRouter([
        path("status/", ServerSentEventsConsumer.as_asgi()),
        re_path(r'', get_asgi_application()),
    ]),
})