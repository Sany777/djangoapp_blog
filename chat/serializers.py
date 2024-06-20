from rest_framework import serializers
from .models import Chat, Message

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['title']

class MessageSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()  

    class Meta:
        model = Message
        fields = ['id', 'chat', 'author', 'content', 'created_at']
