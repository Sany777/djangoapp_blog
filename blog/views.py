from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden

from django.contrib.auth.models import User

from .models import *
from .forms import *


def get_topics_data(request):
    
    user_topics = []
    friends_topics = []
    
    pub_topics = Topic.objects.filter(permision=Topic.Permissions.FOR_ALL)
            
    if request.user.is_authenticated:
        user_topics = request.user.topics.order_by('-pk')
        user_groups = request.user.group_set.all()
        if user_groups:
            friends = [user for group in user_groups for user in group.user.exclude(username=request.user.username)]
            if friends:
                friends_topics = [topic for friend in friends for topic in friend.topics.order_by('-pk')]

    return (pub_topics or [], user_topics, friends_topics)


def get_entry_from_topics(topics):
    return [entry for topic in topics for entry in topic.entries.order_by('-pk')]

       
def index(request):
    
    slidecards_entry = []
    (pub_topics, user_topics, friends_topics) = get_topics_data(request)
    pub_entries = get_entry_from_topics(pub_topics)
    friends_entries = get_entry_from_topics(friends_topics)
    
    if len(pub_entries) == 0:
        pub_topics = []
    else:
        pub_entries = pub_entries[:10]
        
    if len(friends_entries) > 0:
        friends_entries = friends_entries[:10]
 

    if len(friends_entries) >0 or len(pub_entries) >0:
            slidecards_entry = (friends_entries + pub_entries)[:10]
            
    return render(request, 'blog/index.html', {
        'slidecards':slidecards_entry,
        'user_aside_topics':user_topics[:7],
        'friends_aside_topics':friends_topics[:7],
        'pub_aside_topics': pub_topics[:7]
    })



def show_topic_list(request):
    (pub_topics, user_topics, friends_topics ) = get_topics_data(request)

    return render(request, 'blog/show_topic_list.html', {
        'user_topics':user_topics,
        'friends_topics':friends_topics,
        'pub_topics':pub_topics,
        'user_aside_topics':user_topics[:7],
        'friends_aside_topics':friends_topics[:7],
        'pub_aside_topics': pub_topics[:7]
    })


@login_required
def new_topic(request):

    if request.method != 'POST':
        form = TopicForm()
    else:
        form = TopicForm(data=request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.user = request.user
            topic.save()
            return redirect('blog:show_topic', topic.id)
        
    return render(request, 'blog/new_topic.html',{
        'form':form
    })



@login_required
def edit_entry(request, entry_id):

    entry = get_object_or_404(Entry, pk=entry_id, user=request.user)
    topic = entry.topic
    if topic.user != request.user:
        return redirect('blog:index', topic.id)
    
    if request.method == 'POST':
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog:show_topic', topic_id=topic.id)

    form = EntryForm(instance=entry)
        
    return render(request, 'blog/edit_entry.html', {
        'form':form,
        'topic':topic,
        'entry':entry,
    })


@login_required
def new_entry(request, topic_id):

    topic = get_object_or_404(Topic, pk=topic_id, user=request.user)

    if request.method == 'POST':
        form = EntryForm(data=request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.topic = topic
            entry.save()
            return redirect('blog:show_topic', topic_id=topic.id)
     
    form = EntryForm()
    return render(request, 'blog/new_entry.html', {
        'form':form,
        'topic':topic,
        'message':'New entry'
    })


@login_required
def remove_topic(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id, user=request.user)
    topic_name = topic.text
    topic.delete()
    return render(request, 'blog/message.html', {
        'message_str': f"{topic_name} removed"
    })



@login_required
def remove_entry(request, entry_id):
    
    entry = get_object_or_404(Entry, pk=entry_id )
    entry_name = entry.name
    if entry.topic.user == request.user:
        entry.delete()     
        return render(request, 'blog/message.html', {
            'message_str': f"{entry_name} removed"
        })
        
    return Http404("Forbied")


def show_topic(request, topic_id):

    topic = get_object_or_404(Topic, pk=topic_id)
    entries = topic.entries.order_by('-date_added')

    return render(request, 'blog/show_topic.html', {
        'topic':topic,
        'entries':entries,
        'own_topic':topic.user == request.user
    })


def about(request):
    about = ServiceContent.objects.get(name='about')
    return render(request, 'blog/about.html', {
        'about':about
    })
