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
    image = models.ImageField(upload_to='photos/')  
    description = models.CharField(max_length=32, default="")


class Bloger(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(blank=True)
    birth_date = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=12, validators=[is_phone_number,],blank=True)

    def __str__(self):
        return self.user.username


class Group(models.Model):
    """group by preferences"""
    description = models.CharField(max_length=32)
    image = models.ImageField(blank=True)  
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.description


class UserGroupPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user} in {self.group}"
    


class Topic(models.Model):

    class Permissions(models.IntegerChoices):
        PRIVATE = 0
        GROUP = 1
        FOR_ALL = 2

    text = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    permision = models.IntegerField(choices=Permissions, default=Permissions.PRIVATE)

    def __str__(self):
        return self.text
 

class Entry(models.Model):

    text = models.TextField()
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    scores = models.BigIntegerField(null=True)
    score_num = models.IntegerField(null=True)

    class Meta:
        verbose_name_plural = 'entries'

    def __str__(self):
        if len(self.text) > 50:
            return f"{self.text[:50]}..." 
        
        return self.text
        

