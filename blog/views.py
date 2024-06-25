from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.contrib.auth.models import User

from .models import Entry, Rating, Topic, FriendsGroup, FriendCandidates, ServiceContent
from .forms import EntryForm, TopicForm, RatingForm
from .tools import get_rating, get_obj_or_create, get_topics_data, get_requests, get_entry_from_topics


def set_rate(request, publication_id):
    entry = get_object_or_404(Entry, pk=publication_id)

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if entry.topic.user is not request.user:
            new_rating = int(request.POST.get('rating'))
            publication_rating, created = Rating.objects.get_or_create(publication=entry, user=request.user)
            publication_rating.rating = new_rating
            publication_rating.save()

            entry.avg_rating = get_rating(entry)
            entry.save()
            return JsonResponse({'r': entry.avg_rating})

    return JsonResponse({'r': ''})


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
    friends_group = get_obj_or_create(FriendsGroup, owner=request.user)
    my_requests = get_obj_or_create(FriendCandidates, owner=request.user)

    if candidate not in my_requests.membership.all() and candidate not in friends_group.membership.all():
        my_requests.membership.add(candidate)

    return redirect('blog:social')


@login_required
def remove_request(request, user_id):
    candidate = get_object_or_404(User, pk=user_id)
    get_obj_or_create(FriendCandidates, owner=request.user).membership.remove(candidate)
    get_obj_or_create(FriendsGroup, owner=request.user).membership.remove(candidate)

    return redirect('blog:social')


@login_required
def social(request):
    all_user = User.objects.filter(is_superuser=False).exclude(pk=request.user.id)
    my_friends = get_obj_or_create(FriendsGroup, owner=request.user).membership.all()
    my_requests = get_obj_or_create(FriendCandidates, owner=request.user).membership.all()
    requests_from_others = get_requests(request.user, my_friends, all_user)
    not_friends = [user for user in all_user if user not in my_requests and user not in my_friends and user not in requests_from_others]

    pub_topics, user_topics, friends_topics = get_topics_data(user=request.user, friends_list=my_friends)

    return render(request, 'blog/social.html', {
        'friends': my_friends,
        'not_friends': not_friends,
        'my_requests': my_requests,
        'requests_from_others': requests_from_others,
        'user_aside_topics': user_topics[:7],
        'friends_aside_topics': friends_topics[:7],
        'pub_aside_topics': pub_topics[:7],
    })


def welcome_page(request):
    return render(request, 'blog/message.html', {
        'message_str': "Congratulate!"
    })


def index(request):
    pub_topics, user_topics, friends_topics = get_topics_data(request.user)
    description = get_obj_or_create(ServiceContent, create=False, name='description')
    pub_entries = get_entry_from_topics(pub_topics)[:10]
    friends_entries = get_entry_from_topics(friends_topics)[:10]
    user_entries = get_entry_from_topics(user_topics)[:10]
    all_entries = list(pub_entries) + list(friends_entries) + list(user_entries)

    unique_entries = []
    seen = set()
    for entry in all_entries:
        if entry.pk not in seen:
            unique_entries.append(entry)
            seen.add(entry.pk)
        if len(unique_entries) == 10:
            break

    for entry in unique_entries:
        entry.text = entry.text[:200]

    return render(request, 'blog/index.html', {
        'description': description,
        'slidecards': unique_entries,
        'user_aside_topics': user_topics[:7],
        'friends_aside_topics': friends_topics[:7],
        'pub_aside_topics': pub_topics[:7],
    })


def show_topic_list(request):
    pub_topics, user_topics, friends_topics = get_topics_data(request.user)

    return render(request, 'blog/show_topic_list.html', {
        'user_topics': user_topics,
        'friends_topics': friends_topics,
        'pub_topics': pub_topics,
        'user_aside_topics': user_topics[:7],
        'friends_aside_topics': friends_topics[:7],
        'pub_aside_topics': pub_topics[:7]
    })


@login_required
def edit_topic(request, topic_id=None):
    form = None
    topic = None
    pub_topics, user_topics, friends_topics = get_topics_data(request.user)

    if request.method == 'POST':
        form = TopicForm(data=request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.user = request.user
            topic.save()
            return redirect('blog:show_topic', topic.id)
    else:
        if topic_id:
            topic = get_object_or_404(Topic, pk=topic_id)
            if request.user.id != topic.user.id:
                return render(request, 'blog/message.html', {
                    'message_str': f'You are not allowed to modify "{topic}" topic'
                })
            form = TopicForm(instance=topic)
        else:
            form = TopicForm()

    return render(request, 'blog/edit_topic.html', {
        'form': form,
        'topic': topic,
        'user_aside_topics': user_topics[:7],
        'friends_aside_topics': friends_topics[:7],
        'pub_aside_topics': pub_topics[:7]
    })


def edit_entry(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)
    topic = entry.topic

    pub_topics, user_topics, friends_topics = get_topics_data(request.user)

    if topic.user != request.user and topic.permission not in [Topic.Permissions.FOR_ALL, Topic.Permissions.GROUP] and topic not in friends_topics:
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
    else:
        form = EntryForm(instance=entry)

    return render(request, 'blog/edit_entry.html', {
        'form': form,
        'topic': topic,
        'entry': entry,
        'user_aside_topics': user_topics[:7],
        'friends_aside_topics': friends_topics[:7],
        'pub_aside_topics': pub_topics[:7],
    })


@login_required
def new_entry(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id, user=request.user)
    pub_topics, user_topics, friends_topics = get_topics_data(request.user)

    if request.method == 'POST':
        form = EntryForm(data=request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.topic = topic
            entry.save()
            return redirect('blog:show_topic', topic_id=topic.id)
    else:
        form = EntryForm()

    return render(request, 'blog/new_entry.html', {
        'form': form,
        'topic': topic,
        'message': 'New entry',
        'user_aside_topics': user_topics[:7],
        'friends_aside_topics': friends_topics[:7],
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

    raise Http404("It is forbidden")


def show_topic(request, topic_id, topic_start=0, per_page=5):
    topic = get_object_or_404(Topic, pk=topic_id)
    pub_topics, user_topics, friends_topics = get_topics_data(request.user)

    if topic not in pub_topics and topic not in user_topics and topic not in friends_topics:
        raise Http404("You do not have access to this topic")

    entries_num = topic.entries.count()
    num_list = [i + 1 for i in range(0, entries_num, per_page)] if entries_num / per_page >= 2 else []

    entries = topic.entries.order_by('-date_added')[topic_start:topic_start + per_page]

    form = RatingForm() if topic.user != request.user and request.user.is_authenticated else None

    return render(request, 'blog/show_topic.html', {
        'topic': topic,
        'entries': entries,
        'user_aside_topics': user_topics[:7],
        'friends_aside_topics': friends_topics[:7],
        'pub_aside_topics': pub_topics[:7],
        'num_list': num_list,
        'form': form
    })


def about(request):
    about = get_obj_or_create(ServiceContent, name='about')
    if about:
        return render(request, 'blog/about.html', {
            'about': about
        })

    return redirect('blog:index')
