from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404

from .models import *
from .forms import *



def index(request):

    pub_topics = Topic.objects.filter(permision=Topic.Permissions.FOR_ALL)
    slidecards = Entry.objects.all()
    # if pub_topics:
    #     slidecards = pub_topics.entries_set.all()

    if request.user.is_authenticated:
        friends = UserGroupPreference.objects.filter(user=request.user).values('user')
        # if friends:
            # friend_topics = friends.topic_set.order_by('-date_added')
            # friend_entry = friend_topics.entries_set.order_by('-date_added')

    return render(request, 'blog/index.html', {
        'slidecards':slidecards,
        # 'friend_topics':friend_topics,
        # 'friend_entry':friend_entry
    })


# @login_required
def show_topics(request):

    all_topics = Topic.objects.filter(permision=Topic.Permissions.FOR_ALL)
    own_topics = Topic.objects.filter(owner=request.user) 

    return render(request, 'blog/topic.html', {
        'own_topics':own_topics,
        'all_topics':all_topics
    })


# @login_required
def new_topic(request):

    if request.method != 'POST':
        form = TopicForm()
    else:
        form = TopicForm(data=request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.owner = request.user
            topic.permision = Topic.Permissions.PRIVATE;
            topic.save()
            return redirect('blog:index')
        
    return render(request, 'blog/new_topic.html',{
        'form':form
    })


# @login_required
def edit_entry(request, entry_id):

    own_topics = Topic.objects.filter(owner=request.user)
    entry = own_topics.entries_set.get(pk=entry_id)
    topic = entry.topic
    
    if request.method == 'POST':
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog:show_topics', topic_id=topic.id)

    form = EntryForm(instance=entry)
        
    return render(request, 'blog/edit_entry.html', {
        'form':form,
        'topic':topic,
        'entry':entry,
        'own_topics':own_topics
    })


# @login_required
def show_topic(request, topic_id):

    bloger = Bloger.objects.get(user=request.user)
    friends = UserGroupPreference.objects.filter(user=request.user).values('user')
    topic = Topic.objects.filter(user=request.user, permision=Topic.Permissions.FOR_ALL).get(pk=topic_id)
    entries = topic.entry_set.order_by('-date_added')

    return render(request, 'blog/show_topic.html', {
        'topic':topic,
        'entries':entries,
    })



