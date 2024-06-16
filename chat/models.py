# chat/models.py

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class Chat(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if Chat.objects.filter(title=self.title).exists():
            raise ValidationError({'title': 'Ця назва чату вже існує. Будь ласка, оберіть іншу назву.'})

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='replies')

    def __str__(self):
        return f'{self.author.username} - {self.timestamp}'

    def get_absolute_url(self):
        return reverse('chat:message_list', kwargs={'pk': self.chat.pk})
