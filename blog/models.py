from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Banner(models.Model):
    link = models.URLField()
    image = models.ImageField(upload_to='photos/')  
    description = models.CharField(max_length=32, default="")

    def __str__(self):
        return self.description


class FriendCandidates(models.Model):
    membership = models.ManyToManyField(User, related_name='candidates_group')
    owner = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"requests from {self.owner.username}"


class FriendsGroup(models.Model):
    membership = models.ManyToManyField(User, related_name='friend_group')
    owner = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"friends {self.owner.username}"


class Topic(models.Model):

    class Permissions(models.IntegerChoices):
        PRIVATE = 0
        GROUP = 1
        FOR_ALL = 2

    text = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topics')
    permission = models.IntegerField(choices=Permissions.choices, default=Permissions.PRIVATE)

    def is_valid_topic(self):
        return len(self.text) != 0 and self.permission in self.Permissions.values

    def __str__(self):
        return self.text



class Entry(models.Model):
    DEFAULT_RATING = -1
    text = models.TextField()
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='entries')
    date_added = models.DateTimeField(auto_now_add=True)
    avg_rating = models.IntegerField(default=DEFAULT_RATING)

    def is_valid_entry(self):
        return len(self.text) != 0

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
    MAX_RATING = 10
    MIN_RATING = 0
    publication = models.ForeignKey(Entry, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=MIN_RATING, validators=[MinValueValidator(MIN_RATING),
                                                                 MaxValueValidator(MAX_RATING)])

    class Meta:
        unique_together = ('publication', 'user')

    def __str__(self):
        return f"{self.publication} - {self.user.username}: {self.rating}"
