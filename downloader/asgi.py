
import os

from django.core.asgi import get_asgi_application

# ******************** #
import downloader.routing
import django 
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

# ******************** #


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'downloader.settings')
django.setup()
# application = get_asgi_application() # This must be replaced

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            downloader.routing.websocket_urlpatterns
        )
    )
})
