# chat/forms.py

from django import forms
from .models import Message, Chat

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']


class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['title']