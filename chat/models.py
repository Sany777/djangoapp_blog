from django.db import models
from blog.models import *



class Chat(models.Model):

    title = models.TextField(max_length=128)
    description = models.TextField(max_length=128)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title
    
  


class ChatEntry(models.Model):
    chat = models.ForeignKey(Chat,  on_delete=models.CASCADE)
    owner = models.ForeignKey(Bloger, blank=True, null=True, on_delete=models.SET_NULL)
    text = models.TextField(max_length=512)
    date_added = models.DateField(auto_now_add=True)
    scores = models.BigIntegerField(blank=True, null=True)
    score_num = models.IntegerField(blank=True, null=True)

    def __str__(self):
        if len(self.text)>50:
            return F"{self.text[:50]}..."
        return self.text
    
