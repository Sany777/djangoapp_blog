from django.db import models
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy
import re



def is_phone_number(phone_num):
    if len(phone_num) != 0:
        pattern = r"^\+\d{1,3}\d{9}$"
        if re.match(pattern, phone_num) is not None:
            raise ValidationError(
                gettext_lazy("%(phone) is not phone number"),
                params = {'value':phone_num}
            )


class Banner(models.Model):
    link = models.URLField()
    image = models.ImageField(upload_to='blog/static/photos/')  
    description = models.CharField(max_length=32, default="")


class Bloger(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField(null=True)
    phone_number = models.CharField(max_length=12, validators=[is_phone_number,])

    def __str__(self):
        return self.user.username


class Group(models.Model): 
    """group by preferences"""
    name = models.CharField(max_length=32)
    date_created = models.DateField(auto_now_add=True)
    user = models.ManyToManyField(User)
    
    def __str__(self):
        return self.name


class Topic(models.Model):

    class Permissions(models.IntegerChoices):
        PRIVATE = 0
        GROUP = 1
        FOR_ALL = 2

    text = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topics')
    permision = models.IntegerField(choices=Permissions, default=Permissions.PRIVATE)

    def __str__(self):
        return self.text


class Entry(models.Model):

    text = models.TextField()
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE,related_name='entries')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if len(self.text) > 50:
            return f"{self.text[:50]}..." 

        return self.text
        

class ServiceContent(models.Model):
    name = models.CharField(max_length=200)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    
class Rating(models.Model):
    publication = models.ForeignKey(Entry, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
         
    class Meta:
        unique_together = ('publication', 'user')
        
    def __str__(self):
        return f"{self.publication} - {self.user.username}: {self.rating}"