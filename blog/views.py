from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import *
from .forms import *

def index(request):
    return render(request, 'blog/index.html')

@login_required
def topic(request):

    topics = Topic.objects.filter(owner=request.user) 
    return render(request, 'blog/topic.html', {
        'topics':topics
    })

@login_required
def new_topic(request):

    if request.method != 'POST':
        form = TopicForm()
    else:
        form = TopicForm(data=request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.owner = request.user
            topic.save()
            return redirect('blog:index')
        
    return render(request, 'blog/new_topic.html',{
        'form':form
    })

@login_required
def new_entry(request, topic_id):

    topic = Topic.objects.get(pk=topic_id)

    if topic.owner != request.user:
        raise Http404

    if topic and request.method == 'POST':
        form = EntryForm(data=request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.topic = topic
            entry.save()
            return redirect('blog:index')
    else:
        form = EntryForm()
        
    return render(request, 'blog/new_entry.html', {
        'form':form,
        'topic':topic
    })

@login_required
def edit_entry(request, entry_id):

    entry = Entry.objects.filter(owner=request.user).get(pk=entry_id)
    topic = entry.topic
    
    if request.method == 'POST':
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog:topic', topic_id=topic.id)

    form = EntryForm(instance=entry)
        
    return render(request, 'blog/edit_entry.html', {
        'form':form,
        'topic':topic,
        'entry':entry
    })

@login_required
def show_topic(request, topic_id):

    topic = Topic.objects.filter(owner=request.user).get(pk=topic_id)
    entries = topic.entry_set.order_by('-date_added')
    return render(request, 'blog/show_topic.html', {
        'topic':topic,
        'entries':entries
    })



