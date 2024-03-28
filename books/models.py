from django.db import models
from blog.models import *



class Genre(models.Model):
    text = models.CharField(max_length=128)
    description = models.TextField(default="")

    def __str__(self):
        return self.text


class Book(models.Model):
    title = models.CharField(max_length=128)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    scores = models.BigIntegerField(null=True)
    score_num = models.IntegerField(null=True)

    def __str__(self):
        return self.title


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    owner = models.ForeignKey(Bloger, on_delete=models.CASCADE)
    text = models.TextField()
    pub_date = models.DateField(auto_now_add=True)
    scores = models.BigIntegerField(null=True)
    score_num = models.IntegerField(null=True)

    def __str__(self):
        return F'review {self.owner} "{self.book}"'
    

