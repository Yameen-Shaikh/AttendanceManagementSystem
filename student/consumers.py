import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GeneralConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            if self.user.role == 'Teacher':
                self.group_name = f"teacher_{self.user.id}"
            elif self.user.role == 'Student':
                self.group_name = f"student_{self.user.id}"
            else:
                await self.close()
                return

            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def attendance_update(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'attendance.update',
            'message': message
        }))

    async def attendance_status_update(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'attendance.status',
            'message': message
        }))

    async def notification(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': message
        }))
