from django.db import models
from django import forms
from django.contrib.auth.models import User




class Topic(models.Model):
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.text
    

class Entry(models.Model):
    """information about topic"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'enties'

    def __str__(self):
        if len(self.text) > 50:
            return f"{self.text[:50]}..." 
        
        return self.text
        

