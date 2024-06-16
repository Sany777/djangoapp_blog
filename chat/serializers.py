# chat/serializers.py

from rest_framework import serializers
from .models import Chat, Message

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()  # Для відображення імені користувача

    class Meta:
        model = Message
        fields = ['id', 'chat', 'author', 'content', 'created_at']
