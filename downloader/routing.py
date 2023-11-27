
from gdrive import consumers
from django.urls import path
  
websocket_urlpatterns = [
        path("ws/downloads/",consumers.downloadClassConsumer.as_asgi())
]
