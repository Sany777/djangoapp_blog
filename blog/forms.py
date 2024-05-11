from .models import *
from django import forms





class TopicForm(forms.ModelForm):

    class Meta:
        model = Topic
        permission = forms.ChoiceField(choices=Topic.Permissions)
        fields = ['text', 'permission']
        labels = {'text':'Topic', }


class EntryForm(forms.ModelForm):

    class Meta:
        model = Entry
        fields = ['text']
        labels = {'text':''}
        widgets = {'text':forms.Textarea(attrs={'cols':80,'id':'auto-resize'})}
       
       


class RatingForm(forms.ModelForm):
    
    RATING_CHOICES = [(i, str(i)) for i in range(Rating.MIN_RATING, Rating.MAX_RATING+1)]
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
    )
    
    class Meta:
        model = Entry
        fields = ['rating']
        
         