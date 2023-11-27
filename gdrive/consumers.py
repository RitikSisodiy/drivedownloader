# consumers.py

from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer

class downloadClassConsumer(SyncConsumer):
    def websocket_connect(self,event):
        user = self.scope["user"]
        self.room_name = str(user.id)
        self.send({
            'type':'websocket.accept'
        })
        async_to_sync(self.channel_layer.group_add)(self.room_name,self.channel_name)
        print(f'[{self.channel_name}] you are connected')
    def websocket_receive(self,event):
        print(f'[{self.channel_name}] - received - {event.get("text")}')
        async_to_sync(self.channel_layer.group_send)(self.room_name,{
            "type":"websocket.message",
            "text":event.get('text')
        })
    def websocket_message(self,event):
        print(f'[{self.channel_name}] - message sent - {event.get("text")}')
        self.send({
            'type':'websocket.send',
            'text': event.get('text')
        })
    async def send_chat_message(self, room_name, message):
        # Send message to room group
        await self.channel_layer.group_send(
            room_name,
            {
                'type': 'websocket.message',
                'message': message
            }
        )
    def websocket_disconnect(self,event):
        print("event is disconnected")
        async_to_sync(self.channel_layer.group_discard)(self.room_name,self.channel_name)
        print(f'[{self.channel_name}] you are disconnected')
        print(event)
