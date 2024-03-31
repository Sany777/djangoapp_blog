from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden

from django.contrib.auth.models import User



from .models import *
from .forms import *



def index(request):

    pub_topics = Topic.objects.filter(permision=Topic.Permissions.FOR_ALL)
    user_topic = None
    pub_entry = None
    friend_entries = None
    friends_topics = None

    if pub_topics:
        pub_entry = pub_topics[0].entries.all()[:10]

    if request.user.is_authenticated:
        user_groups = request.user.group_set.all()
        user_topic = request.user.topics.all()
        if user_groups:
            friends = [user for group in user_groups for user in group.user.all()]
            if friends:
                friends_topics = [topic for friend in friends for topic in friend.topics.all()]
                friend_entries = [entry for topic in friends_topics for entry in topic.entries.all() ]
    
    return render(request, 'blog/index.html', {
        'slidecards':friend_entries,
        'user_topic':user_topic,
        'friends_topics':friends_topics,
        'pub_topics':pub_topics
    })


# @login_required
def show_topic_list(request):

    all_topics = Topic.objects.filter(permision=Topic.Permissions.FOR_ALL)\

    own_topics = None
    if request.user and request.user.is_authenticated:
        own_topics = Topic.objects.filter(user=request.user) 

    return render(request, 'blog/show_topic_list.html', {
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
            topic.user = request.user
            topic.save()
            return redirect('blog:show_topic', topic.id)
        
    return render(request, 'blog/new_topic.html',{
        'form':form
    })


# @login_required
def edit_entry(request, entry_id):

    entry = Entry.objects.get(pk=entry_id)
    topic = entry.topic
    
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
        'message':'Edit entry'
    })

def new_entry(request, topic_id):

    topic = Topic.objects.get(pk=topic_id)

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

def remove_topic(request):
    pass

# @login_required
def show_topic(request, topic_id):

    # topic = Topic.objects.filter(user=request.user, permision=Topic.Permissions.FOR_ALL).get(pk=topic_id)
    topic = Topic.objects.get(pk=topic_id)
    entries = topic.entries.order_by('-date_added')

    return render(request, 'blog/show_topic.html', {
        'topic':topic,
        'entries':entries,
    })


def about(request):
    about = ServiceContent.objects.get(name='about')
    return render(request, 'blog/about.html', {
        'about':about
    })
