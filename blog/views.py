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
def social(request, user_id=None):
    
    friends_group = FriendsGroup.objects.get(owner=request.user)
    my_friends = friends_group.membership.all()
    
    candidates_group = FriendCandidates.objects.get(owner=request.user)
    
    all_user = User.objects.filter(is_superuser=False).exclude(pk=request.user.id)
    requests_from_others = [candidate for candidate in all_user for u in get_obj_or_none(FriendCandidates,owner=candidate).membership.all() if u == request.user]
    
    my_requests = candidates_group.membership.all()
    if  user_id != None:
        
        candidate = get_object_or_404(User, pk=user_id)
        
        if candidate in my_friends:
            friends_group.membership.remove(candidate)
            my_friends = friends_group.membership.all()
        elif candidate in requests_from_others:
            friends_group.membership.add(candidate)
            my_friends = friends_group.membership.all()
        else:
            if candidate in my_requests:
                candidates_group.membership.remove(candidate)
            else:
                candidates_group.membership.add(candidate)        
            my_requests = candidates_group.membership.all()
                   
    
    not_friends = [user for user in all_user if user not in my_requests and user not in my_friends]
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





def index(request):

    slidecards_entry = []
    (pub_topics, user_topics, friends_topics) = get_topics_data(request.user)
    
    description = get_obj_or_none(ServiceContent, name='description')
    
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
        'description':description,
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
    
    form = None
    topic = None
    (pub_topics, user_topics, friends_topics) = get_topics_data(request)
    
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
    
    (pub_topics, user_topics, friends_topics) = get_topics_data(request)

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
    
    topic = get_object_or_404(Topic, pk=topic_id)
    if request.user.id == topic.id:
        topic_name = topic.text
        return render(request, 'blog/message.html', {
            'message_str': f'Topic "{topic_name}" removed'
        })
    return render(request, 'blog/message.html', {
            'message_str': f'You are not allowed to modify "{topic_name}" topic'
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
    
    about = get_obj_or_none(ServiceContent, name='about')
    if about:
        return render(request, 'blog/about.html', {
            'about':about
        })     

    return redirect('blog:index')
            
            
    
