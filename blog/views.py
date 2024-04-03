from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden
from django.http import JsonResponse
from django.contrib.auth.models import User

from .models import *
from .forms import *


def get_friends(request):

    friends = []
    if request.user.is_authenticated:    
        
        try:
            user_group = Group.objects.get(owner=request.user)    
            friends = [user for user in user_group.membership.all()]
        except Group.DoesNotExist:
            Group.objects.create(owner=request.user)

    return friends


def get_user_data(request):
    
    friends = []
    not_friends = []
    
    if request.user.is_authenticated:
        users = User.objects.exclude(pk=request.user.id).filter(is_superuser=False)
        friends = get_friends(request)
        not_friends = [user for user in users if user not in friends]
        
    return (friends, not_friends)
    
    
def get_topics_data(request):
    
    user_topics = []
    friends_topics = []
    
    pub_topics = Topic.objects.filter(permision=Topic.Permissions.FOR_ALL)
            
    if request.user.is_authenticated:
        pub_topics = [topic for topic in pub_topics if topic.user != request.user]
        user_topics = request.user.topics.order_by('-pk')
        friends = get_friends(request)
        if friends:
            friends_topics = [topic for friend in friends for topic in friend.topics.order_by('-pk')]
            pub_topics = [topic for topic in pub_topics if topic not in friends_topics]

    return (pub_topics, user_topics, friends_topics)


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
        
        
@login_required
def add_friend(request, user_id):
    user_to_add = get_object_or_404(User, pk=user_id)
    
    friends = get_friends(request)
    if user_to_add not in friends and user_to_add.id != request.user.id:
        group = get_object_or_404(Group, owner=request.user)
        group.membership.add(user_to_add)


    return redirect('blog:social' )


@login_required
def remove_friend(request, user_id):

    user_to_remove = get_object_or_404(User, pk=user_id)
    
    friends = get_friends(request)
    if user_to_remove in friends:
        group = get_object_or_404(Group, owner=request.user)
        group.membership.remove(user_to_remove)

    return redirect('blog:social' )
    
    

    
@login_required   
def social(request):
    
    (friends, not_friends) = get_user_data(request)   
    (pub_topics, user_topics, friends_topics) = get_topics_data(request)
    
    return render(request, 'blog/social.html', {
        'friends':friends,
        'not_friends':not_friends,
        'user_aside_topics':user_topics[:7],
        'friends_aside_topics':friends_topics[:7],
        'pub_aside_topics': pub_topics[:7],
    })


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
        'pub_aside_topics': pub_topics[:7],
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
def edit_topic(request, topic_id = None):
    
    (pub_topics, user_topics, friends_topics) = get_topics_data(request)
    form = None
    topic = None
    if request.method != 'POST':
        if topic_id != None:
            topic = get_object_or_404(Topic, pk=topic_id)
            form = TopicForm(instance=topic)
        else:
            form = TopicForm()
    else:
        form = TopicForm(data=request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.user = request.user
            topic.save()
            return redirect('blog:show_topic', topic.id)
        
    return render(request, 'blog/edit_topic.html',{
        'form':form,
        'topic':topic,
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
    if topic.user != request.user and request.user.is_authenticated:
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
