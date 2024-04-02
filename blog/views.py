from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden
from django.http import JsonResponse

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



def set_rate(request, publication_id):
    
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        rating_value = int(request.POST.get('rating'))
        entry = get_object_or_404(Entry, pk=publication_id)
        
        publication_rating = None
        
        if Rating.objects.filter(publication=entry, user=request.user).exists():
            publication_rating = Rating.objects.get(publication=entry, user=request.user)
            publication_rating.rating = rating_value;
        else:     
            publication_rating = Rating(publication=entry, rating=rating_value, user=request.user)
            
        publication_rating.save()
        publication_ratings = Rating.objects.filter(publication=entry)  
        total_ratings = publication_ratings.count()
        
        if total_ratings != 0:
            total_score = sum([rating.rating for rating in publication_ratings])
            rating_value = total_score / total_ratings if total_ratings > 0 else 0
            
        entry.avg_rating = rating_value
        entry.save()

        return JsonResponse({'success': rating_value})

    return JsonResponse({'error': ''})       
        
        
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
    
    (pub_topics, user_topics, friends_topics) = get_topics_data(request)

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
    
    (pub_topics, user_topics, friends_topics) = get_topics_data(request)

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
        'form':form,
        'user_aside_topics':user_topics[:7],
        'friends_aside_topics':friends_topics[:7],
        'pub_aside_topics': pub_topics[:7]
    })


@login_required
def edit_entry(request, entry_id):
    
    entry = get_object_or_404(Entry, pk=entry_id)
    
    (pub_topics, user_topics, friends_topics) = get_topics_data(request)

    topic = entry.topic
    
    if topic.user != request.user and topic.permision != topic.Permissions.FOR_ALL and topic.permision != topic.Permissions.GROUP and not topic in friends_topics:
        return Http404("It is forbidden")
    
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
        'user_aside_topics':user_topics[:7],
        'friends_aside_topics':friends_topics[:7],
        'pub_aside_topics': pub_topics[:7],
        'edit':topic.user == request.user
    })


@login_required
def new_entry(request, topic_id):

    topic = get_object_or_404(Topic, pk=topic_id, user=request.user)
    (pub_topics, user_topics, friends_topics) = get_topics_data(request)

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
        'message':'New entry',
        'user_aside_topics':user_topics[:7],
        'friends_aside_topics':friends_topics[:7],
        'pub_aside_topics': pub_topics[:7]
    })


@login_required
def remove_topic(request, topic_id):
    
    topic = get_object_or_404(Topic, pk=topic_id, user=request.user)
    
    topic_name = topic.text
    topic.delete()
    return render(request, 'blog/message.html', {
        'message_str': f'Topic "{topic_name}" removed'
    })
    

@login_required
def remove_entry(request, entry_id):
    
    entry = get_object_or_404(Entry, pk=entry_id)
    if entry.topic.user == request.user:
        text = entry.text[:40]
        entry.delete()
        return render(request, 'blog/message.html', {
            'message_str': f'Entry "{text}..." removed'
        })
        
    return Http404("It is forbidden")



def show_topic(request, topic_id, topic_start = 0, per_page=5):
    num_list = []
    topic = get_object_or_404(Topic, pk=topic_id)

    (pub_topics, user_topics, friends_topics) = get_topics_data(request)
    entries_num = topic.entries.count()
    if entries_num / per_page >= 2:
        num_list = [i+1 for i in range(0, entries_num-1, per_page)]
    else:
        per_page = entries_num
    entries = topic.entries.order_by('-date_added')[topic_start:topic_start+per_page]
    
    form = None
    if topic.user != request.user:
        form = RatingForm()
        
    
    
    return render(request, 'blog/show_topic.html', {
        'topic':topic,
        'entries':entries,
        'user_aside_topics':user_topics[:7],
        'friends_aside_topics':friends_topics[:7],
        'pub_aside_topics': pub_topics[:7],
        'num_list':num_list,
        'form':form
    })


def about(request):
    about = ServiceContent.objects.get(name='about')
    return render(request, 'blog/about.html', {
        'about':about
    })
