from django.contrib.auth.models import User

from .models import *
from .forms import *



def get_obj_or_create(modelClass, user_add=None, create=True, **kwargs):

    try:
        return modelClass.objects.get(**kwargs)
    except modelClass.DoesNotExist:
        if create:
            model = modelClass.objects.create(**kwargs)
            if user_add and model:
                model.save()
                models.membership.add(user_add)
            return model
    except:
        pass
    return None
   
    
def get_topics_data(user, friends_list=None):
    
    user_topics = []
    friends_topics = []
    
    pub_topics = Topic.objects.filter(permission=Topic.Permissions.FOR_ALL)
            
    if user.is_authenticated:
        pub_topics = [topic for topic in pub_topics if topic.user != user]
        user_topics = user.topics.order_by('-pk')
        if friends_list == None:
            friends_group = get_obj_or_create(FriendsGroup, owner=user)
            if friends_group:
                friends_list = friends_group.membership.all()
            
        if friends_list:
            friends_topics = [topic for friend in friends_list for topic in friend.topics.order_by('-pk') if topic.permission != Topic.Permissions.PRIVATE]
            pub_topics = [topic for topic in pub_topics if topic not in friends_topics]

    return (pub_topics, user_topics, friends_topics)


def get_entry_from_topics(topics):
    return [entry for topic in topics for entry in topic.entries.order_by('-pk')]


def get_requests(user, friends, all_user):
    return [candidate for candidate in all_user if candidate not in friends for u in get_obj_or_create(FriendCandidates, owner=candidate).membership.all() if u == user]
        