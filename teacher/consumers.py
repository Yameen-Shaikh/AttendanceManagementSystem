import json
from channels.generic.websocket import AsyncWebsocketConsumer

class AttendanceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lecture_id = self.scope['url_route']['kwargs']['lecture_id']
        self.lecture_group_name = f'attendance_{self.lecture_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.lecture_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.lecture_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        pass

    # Receive message from room group
    async def attendance_update(self, event):
        print(f"Received attendance_update event: {event}")
        # Send message to WebSocket
        data = json.dumps(event['data'])
        print(f"Sending data to WebSocket: {data}")
        await self.send(text_data=data)
