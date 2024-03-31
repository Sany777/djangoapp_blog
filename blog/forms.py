from .models import *
from django import forms




class TopicForm(forms.ModelForm):

    class Meta:
        model = Topic
        permision = forms.ChoiceField(choices=Topic.Permissions)
        fields = ['text', 'permision']
        labels = {'text':'Topic', }


class EntryForm(forms.ModelForm):

    class Meta:
        model = Entry
        fields = ['text']
        labels = {'text':''}
        widgets = {'text':forms.Textarea(attrs={'cols':80,'id': 'auto-resize'})}