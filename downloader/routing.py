
from gdrive import consumers
from channels.routing import ProtocolTypeRouter,URLRouter
from django.urls import path
from channels.auth import AuthMiddlewareStack    
application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter([
          path("ws/downloads/",consumers.downloadClassConsumer.as_asgi())
    ])
    )
})
