from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden

from django.http import JsonResponse
from django.contrib.auth.models import User

from .models import *
from .forms import *
from .tools import *

def set_rate(request, publication_id):
    
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        
        entry = get_object_or_404(Entry, pk=publication_id)
        rating_value = int(request.POST.get('rating'))
        
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
    
    candidate = get_object_or_404(User, pk=user_id)
    all_user = User.objects.filter(is_superuser=False).exclude(pk=request.user.id)
    friends_group = get_obj_or_create(FriendsGroup, owner=request.user)
    friends = friends_group.membership.all()
    requests_from_others = get_requests(user=request.user, all_user=all_user, friends=friends)
    
    if candidate in requests_from_others:
        get_obj_or_create(FriendsGroup, owner=candidate).membership.add(request.user)
        get_obj_or_create(FriendCandidates, owner=candidate).membership.remove(request.user)
        friends_group.membership.add(candidate)
    return redirect('blog:social')




@login_required   
def remove_friend(request, user_id):
    
    candidate = get_object_or_404(User, pk=user_id)
    get_obj_or_create(FriendsGroup, owner=request.user).membership.remove(candidate)
    get_obj_or_create(FriendsGroup, owner=candidate).membership.remove(request.user)
    return redirect('blog:social')
    
    
@login_required   
def add_request(request, user_id):
    
    candidate = get_object_or_404(User, pk=user_id)
    my_requests = get_obj_or_create(FriendCandidates, owner=request.user)
    
    if candidate not in my_requests.membership.all():
        my_requests.membership.add(candidate)
    return redirect('blog:social')
    
    
@login_required   
def remove_request(request, user_id):
    
    candidate = get_object_or_404(User, pk=user_id)
    get_obj_or_create(FriendCandidates, owner=request.user).membership.remove(candidate)
    get_obj_or_create(FriendsGroup, owner=request.user).membership.remove(candidate)
    
    return redirect('blog:social')
    
    

@login_required   
def add_request(request, user_id):
    
    candidate = get_object_or_404(User, pk=user_id)
    friends_group = get_obj_or_create(FriendsGroup, owner=request.user) 
    my_requests = get_obj_or_create(FriendCandidates, owner=request.user)
    
    if candidate not in my_requests.membership.all() and candidate not in friends_group.membership.all():
        my_requests.membership.add(candidate)
        
    return redirect('blog:social')
        
        
@login_required   
def social(request):
    
    all_user = User.objects.filter(is_superuser=False).exclude(pk=request.user.id)
    
    my_friends = get_obj_or_create(FriendsGroup, owner=request.user).membership.all() 
    my_requests = get_obj_or_create(FriendCandidates, owner=request.user).membership.all()
    requests_from_others = get_requests(request.user, my_friends, all_user)
    not_friends = [user for user in all_user if user not in my_requests and user not in my_friends and user not in requests_from_others]
    
    (pub_topics, user_topics, friends_topics) = get_topics_data(user=request.user, friends_list=my_friends)

    return render(request, 'blog/social.html', {
        'friends':my_friends,
        'not_friends':not_friends,
        'my_requests':my_requests,
        'requests_from_others':requests_from_others,
        'user_aside_topics':user_topics[:7],
        'friends_aside_topics':friends_topics[:7],
        'pub_aside_topics': pub_topics[:7],
    })

def welcome_page(request):
    
    return render(request, 'blog/message.html', {
            'message_str': f"Вітаємо нового користувача! Тепер можна користуватися ресурсами сайта в повній мірі підписуватися і заводити підписників, вести блоги!"
        })


def index(request):

    slidecards_entry = []
    (pub_topics, user_topics, friends_topics) = get_topics_data(request.user)
    
    description = get_obj_or_create(ServiceContent, create=False,name='description')
    pub_entries = get_entry_from_topics(pub_topics)[:10]
    friends_entries = get_entry_from_topics(friends_topics)[:10]
    user_entries = get_entry_from_topics(user_topics)[:10]

    slidecards_entry = (friends_entries + pub_entries + user_entries)[:10]

    return render(request, 'blog/index.html', {
        'description':description,
        'slidecards':slidecards_entry,
        'user_aside_topics':user_topics[:7],
        'friends_aside_topics':friends_topics[:7],
        'pub_aside_topics': pub_topics[:7],
    })



def show_topic_list(request):
    
    (pub_topics, user_topics, friends_topics) = get_topics_data(request.user)

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
    
    form = None
    topic = None
    (pub_topics, user_topics, friends_topics) = get_topics_data(request.user)
    
    if request.method != 'POST':
        if topic_id != None:
            topic = get_object_or_404(Topic, pk=topic_id)
            if request.user.id != topic.user.id:    
                return render(request, 'blog/message.html', {
                        'message_str': f'You are not allowed to modify "{topic}" topic'
                    })
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


def edit_entry(request, entry_id):
    
    entry = get_object_or_404(Entry, pk=entry_id)
    topic = entry.topic
    
    (pub_topics, user_topics, friends_topics) = get_topics_data(request.user)

    if topic.user != request.user and topic.permision != topic.Permissions.FOR_ALL and topic.permision != topic.Permissions.GROUP and not topic in friends_topics:
        return Http404("It is forbidden")
    
    if request.method == 'POST':
        if request.user.id != topic.user.id:    
            return render(request, 'blog/message.html', {
                    'message_str': f'You are not allowed to modify "{topic}" topic'
                })
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
    (pub_topics, user_topics, friends_topics) = get_topics_data(request.user)

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
    
    topic = get_object_or_404(Topic, pk=topic_id)
    topic_name = topic.text
    if request.user.id == topic.user.id:
        topic.delete()
        return render(request, 'blog/message.html', {
            'message_str': f"Topic '{topic_name}' removed"
        })
    return render(request, 'blog/message.html', {
            'message_str': f"You are not allowed to modify '{topic_name}' topic"
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

    (pub_topics, user_topics, friends_topics) = get_topics_data(request.user)
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
    
    about = get_obj_or_create(ServiceContent, name='about')
    if about:
        return render(request, 'blog/about.html', {
            'about':about
        })     

    return redirect('blog:index')
            
            
    
