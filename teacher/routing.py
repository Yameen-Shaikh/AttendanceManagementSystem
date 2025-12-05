from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/attendance/<int:lecture_id>/', consumers.AttendanceConsumer.as_asgi()),
]
